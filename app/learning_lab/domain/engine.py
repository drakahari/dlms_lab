"""Bounded IPv4 simulation. This module performs no external I/O."""
from copy import deepcopy
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network
import re

from .validation import ValidationError, require, settings, validate_pack, initial_applied


@dataclass(frozen=True)
class Evidence:
    ok: bool
    message: str
    hops: tuple = ()
    kind: str = ''


class Engine:
    def __init__(self, pack, applied=None):
        self.pack = pack
        self.source = next(iter(pack["initial_state"]))
        self.applied = deepcopy(applied if applied is not None else initial_applied(pack))
        self.devices = deepcopy(pack["topology"]["devices"])
        self.by_id = {d["id"]: d for d in self.devices}
        device = self.by_id[self.source]
        device["interfaces"][0].update({k: self.applied[k] for k in ("address", "prefix")})
        device.update({k: self.applied[k] for k in ("gateway", "dns")})
        self.policy = None
        if 'firewall' in pack:
            from .firewall import Policy
            self.policy = Policy(self.applied['firewall'])

    @staticmethod
    def network(iface):
        return IPv4Network((iface["address"], iface["prefix"]), strict=False)

    def owner(self, ip):
        return next((d for d in self.devices if any(i["address"] == ip for i in d["interfaces"])), None)

    def path(self, source, target):
        current = self.by_id[source]
        hops = [source]
        for _ in range(len(self.devices) + 1):
            if any(i["address"] == target for i in current["interfaces"]):
                return Evidence(True, " → ".join(hops), tuple(hops))
            if current["id"] != source and not current["forwarding"]:
                return Evidence(False, f"{current['id']} does not forward packets.", tuple(hops))
            direct = [i for i in current["interfaces"] if IPv4Address(target) in self.network(i)]
            if direct:
                iface = max(direct, key=lambda i: i["prefix"])
                next_ip = target
            else:
                next_ip = current["gateway"]
                if not next_ip:
                    return Evidence(False, f"{current['id']} has no route to {target}.", tuple(hops))
                choices = [i for i in current["interfaces"] if IPv4Address(next_ip) in self.network(i)]
                if not choices:
                    return Evidence(False, f"Gateway {next_ip} is outside {current['id']}'s local subnet.", tuple(hops))
                iface = max(choices, key=lambda i: i["prefix"])
            neighbor = next((d for d in self.devices if any(i["segment"] == iface["segment"] and i["address"] == next_ip for i in d["interfaces"])), None)
            if neighbor is None:
                return Evidence(False, f"No simulated neighbor answers at {next_ip} on {iface['segment']}.", tuple(hops))
            if neighbor["id"] in hops:
                return Evidence(False, "Routing loop detected.", tuple(hops))
            current = neighbor
            hops.append(current["id"])
        return Evidence(False, "Simulation hop limit reached.", tuple(hops))

    def reach(self, target, source=None):
        source = source or self.source
        try:
            IPv4Address(target)
        except ValueError:
            return Evidence(False, "Target is not a simulated IPv4 address.")
        destination = self.owner(target)
        if destination is None:
            return Evidence(False, f"No known simulated endpoint at {target}.")
        outbound = self.path(source, target)
        if not outbound.ok:
            return outbound
        reply_ip = self.by_id[source]["interfaces"][0]["address"]
        inbound = self.path(destination["id"], reply_ip)
        if not inbound.ok:
            return Evidence(False, f"Return path failed: {inbound.message}", outbound.hops)
        return Evidence(True, f"{target} reachable; {outbound.message}; return path works.", outbound.hops)

    def resolve(self, hostname):
        hostname = hostname.lower().rstrip(".")
        known = any(hostname in d["records"] for d in self.devices)
        if not known:
            return Evidence(False, f"Name '{hostname}' is outside this bounded simulation."), None
        server_ip = self.applied["dns"]
        reachable = self.reach(server_ip)
        if not reachable.ok:
            return Evidence(False, f"DNS server {server_ip} unavailable: {reachable.message}"), None
        server = self.owner(server_ip)
        ip = server["records"].get(hostname)
        if ip is None:
            return Evidence(False, f"DNS server {server_ip} has no record for {hostname}."), None
        return Evidence(True, f"{hostname} resolves to {ip} via {server_ip}."), ip

    def portal(self, hostname="portal.lab.test"):
        dns, ip = self.resolve(hostname)
        if not dns.ok:
            return Evidence(False, dns.message)
        route = self.reach(ip)
        if not route.ok:
            return route
        endpoint = self.owner(ip)
        if hostname.lower().rstrip(".") not in endpoint["endpoints"]:
            return Evidence(False, "No modeled portal endpoint for that name.")
        return Evidence(True, "Portal name resolves and its endpoint is reachable. DNS/reachability only; TCP, HTTPS and firewall behavior are not validated.")

    def connect(self, target, port):
        if self.policy is None:
            return Evidence(False, 'Bounded simulation: unsupported TCP/firewall operation; capability is not declared by this lab.', kind='unsupported')
        from .firewall import port_number
        try:
            port = port_number(port)
        except ValidationError as exc:
            return Evidence(False, str(exc), kind='invalid-port')
        original = target
        try:
            IPv4Address(target)
        except (ValueError, TypeError):
            if not isinstance(target, str):
                return Evidence(False, 'Target is outside this bounded simulation.', kind='unknown-target')
            dns, target = self.resolve(target)
            if not dns.ok:
                return Evidence(False, dns.message, kind='dns-failure')
        route = self.reach(target)
        if not route.ok:
            return Evidence(False, f'TCP connection cannot reach its destination: {route.message} No firewall decision was reached.', route.hops, 'routing-failure')
        fw = self.pack['firewall']['device']
        if fw in route.hops[1:-1]:
            allowed, decision = self.policy.decision(self.applied['address'], target, port)
            explanation = f'{fw}: {decision}'
            if not allowed:
                return Evidence(False, f'TCP {self.applied["address"]} → {target}:{port} BLOCKED by {explanation}.', route.hops, 'policy-deny')
        else:
            explanation = f'{fw} is not on this route; its policy was not evaluated'
        owner = self.owner(target)
        listening = any(s['device'] == owner['id'] and port in s['ports'] for s in self.pack['tcp_services'])
        if not listening:
            return Evidence(False, f'TCP {original}:{port}: {explanation}; no declared listening service on this port.', route.hops, 'no-listener')
        return Evidence(True, f'TCP {self.applied["address"]} → {target}:{port} CONNECTED; allowed by {explanation}; declared listener and return route work. Simulated TCP only; no TLS or HTTP validation.', route.hops, 'connected')

    def grade(self):
        results = []
        for objective in self.pack["objectives"]:
            pred, params = objective["predicate"], objective["params"]
            if pred == "address_equals":
                ok = self.applied["address"] == params["value"]
                evidence = f"Address {self.applied['address']}; required {params['value']}."
            elif pred == "prefix_equals":
                ok = self.applied["prefix"] == params["value"]
                evidence = f"Prefix /{self.applied['prefix']}; required /{params['value']}."
            elif pred == "reachable":
                result = self.reach(params["target"])
                ok, evidence = result.ok, result.message
            elif pred == 'dns_and_portal':
                result = self.portal(params["hostname"])
                ok, evidence = result.ok, result.message
            elif pred in ('tcp_allowed', 'tcp_blocked'):
                result = self.connect(params['target'], params['port'])
                ok = result.ok if pred == 'tcp_allowed' else result.kind == 'policy-deny'
                evidence = result.message
            elif pred == 'tcp_isolated':
                route = self.reach(params['target'])
                if not route.ok or self.pack['firewall']['device'] not in route.hops[1:-1]:
                    ok, evidence = False, 'The declared firewall is not on a working forward/return path for the required flow.'
                else:
                    required_source = self.pack['initial_state'][params['source']]['address']
                    ok, evidence = self.policy.isolation(required_source, params['target'], params['port'])
            results.append({"id": objective["id"], "label": objective["label"], "possible": objective["points"],
                            "earned": objective["points"] if ok else 0, "ok": ok, "evidence": evidence})
        return {"score": sum(r["earned"] for r in results), "complete": all(r["ok"] for r in results), "objectives": results}

    def command(self, command):
        if not isinstance(command, str) or len(command) > 512:
            return "Simulation input limit: 512 characters."
        if not re.fullmatch(r"[A-Za-z0-9 ._-]*", command):
            return "Bounded simulation: shell syntax and control characters are not supported."
        parts = command.strip().split()
        if not parts:
            return ""
        if parts == ["help"]:
            tcp_help = '\nconnect <IPv4-or-hostname> <port> (1–65535; simulated TCP)' if self.policy else '\nTCP/firewall capability is not declared by this lab.'
            return f"{self.source} simulated commands:\nhelp | clear | ipconfig | ip addr | ip route\nping <IPv4-or-hostname>\nnslookup <hostname>\ntraceroute <IPv4-or-hostname>" + tcp_help + '\nNo options, host shell or real traffic.'
        if parts == ["clear"]:
            return ""
        if parts in (["ipconfig"], ["ip", "addr"]):
            return f"{self.source} applied settings\nIPv4 {self.applied['address']}/{self.applied['prefix']}\nGateway {self.applied['gateway']}\nDNS {self.applied['dns']}"
        if parts == ["ip", "route"]:
            iface = self.by_id[self.source]["interfaces"][0]
            return f"{self.network(iface)} directly connected\ndefault via {self.applied['gateway']}"
        if len(parts) == 3 and parts[0] == 'connect':
            return self.connect(parts[1], parts[2]).message
        if len(parts) != 2 or parts[0] not in {"ping", "nslookup", "traceroute"}:
            return "Bounded simulation: unsupported command or options. Type help for supported syntax."
        operation, target = parts
        if operation == "nslookup":
            return self.resolve(target)[0].message
        try:
            IPv4Address(target)
        except ValueError:
            dns, target = self.resolve(target)
            if not dns.ok:
                return dns.message
        result = self.reach(target)
        if operation == "traceroute":
            return "Simulated route: " + (" → ".join(result.hops) or "no hops") + "\n" + result.message
        return ("Simulated reply: " if result.ok else "Simulated failure: ") + result.message


def _load_pack(raw, *, hint_limit=None, candidate_limit=None):
    from .validation import decode
    pack = validate_pack(decode(raw), hint_limit=hint_limit)
    source = next(iter(pack["initial_state"]))
    candidate = initial_applied(pack)
    for objective in pack["objectives"]:
        if objective["predicate"] == "address_equals":
            candidate["address"] = objective["params"]["value"]
        if objective["predicate"] == "prefix_equals":
            candidate["prefix"] = objective["params"]["value"]
    network = settings({k: candidate[k] for k in ('address','prefix','gateway','dns')})
    candidate.update(network)
    if 'firewall' in pack:
        isolated = [o['params'] for o in pack['objectives'] if o['predicate'] == 'tcp_isolated']
        require(len(isolated) == 1, 'Firewall packs require one explicit narrow TCP permission objective.')
        p = isolated[0]
        candidate['firewall'] = {'default':'deny', 'rules':[{'id':'feasibility', 'action':'allow', 'protocol':'tcp', 'source':candidate['address']+'/32', 'destination':p['target']+'/32', 'port':p['port']}]}
    # Finite search of declared interfaces/DNS servers, not arbitrary expressions.
    devices = pack["topology"]["devices"]
    gateways = [i["address"] for d in devices for i in d["interfaces"]]
    dns_servers = [i["address"] for d in devices if d["records"] for i in d["interfaces"]]
    editable = pack["editable_fields"][source]
    if "gateway" not in editable:
        gateways = [candidate["gateway"]]
    if "dns" not in editable:
        dns_servers = [candidate["dns"]]
    require(candidate_limit is None or len(gateways) * len(dns_servers) <= candidate_limit,
            'Pack feasibility validation limit exceeded; reduce candidate gateways/DNS servers.')
    require(all(candidate[k] == pack["initial_state"][source][k] for k in network if k not in editable),
            "Objectives would require changing a fixed setting.")
    require(any(Engine(pack, {**candidate, "gateway": gw, "dns": dns}).grade()["complete"]
                for gw in gateways for dns in dns_servers), "Pack objectives cannot be satisfied by the declared topology.")
    return pack


def load_pack(raw, *, hint_limit=None, candidate_limit=None):
    try:
        return _load_pack(raw, hint_limit=hint_limit, candidate_limit=candidate_limit)
    except (TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise ValidationError("Malformed pack value or structure.") from exc


def load_catalog(raw_packs):
    packs = [load_pack(raw) for raw in raw_packs]
    require(len({p["lab_id"] for p in packs}) == len(packs), "Duplicate lab IDs.")
    return packs
