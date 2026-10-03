"""Pure, bounded first-match TCP policy evaluation and permission analysis."""
from copy import deepcopy
from ipaddress import IPv4Address, IPv4Network
import re
from .validation import ValidationError, keys, require

MAX_RULES = 16
RULE_FIELDS = {'id', 'action', 'protocol', 'source', 'destination', 'port'}


def network_selector(value):
    require(isinstance(value, str) and len(value) <= 64, 'Use an IPv4 host, CIDR network, or any.')
    if value == 'any':
        return value
    try:
        return str(IPv4Network(value, strict=True))
    except ValueError as exc:
        raise ValidationError('Use a valid IPv4 host or canonical CIDR network; host bits must be zero for a network.') from exc


def port_number(value):
    require(type(value) in (int, str), 'TCP port must be an integer from 1 through 65535.')
    if isinstance(value, str):
        require(bool(re.fullmatch(r'[0-9]{1,5}', value)), 'TCP port must be an integer from 1 through 65535.')
        value = int(value)
    require(1 <= value <= 65535, 'TCP port must be an integer from 1 through 65535.')
    return value


def policy(value):
    keys(value, {'default', 'rules'}, 'firewall policy')
    require(value['default'] in ('allow', 'deny'), 'Default TCP policy must be allow or deny.')
    require(isinstance(value['rules'], list) and len(value['rules']) <= MAX_RULES, 'At most 16 ordered firewall rules are supported.')
    rules, ids = [], set()
    for rule in value['rules']:
        keys(rule, RULE_FIELDS, 'firewall rule')
        require(isinstance(rule['id'], str) and re.fullmatch(r'[A-Za-z0-9_-]{1,32}', rule['id']) and rule['id'] not in ids, 'Rule IDs must be unique and contain 1–32 letters, digits, hyphens or underscores.')
        ids.add(rule['id'])
        require(rule['action'] in ('allow', 'deny'), 'Rule action must be allow or deny.')
        require(rule['protocol'] == 'tcp', 'Only simulated TCP rules are supported; DNS and ICMP are unaffected.')
        rules.append({**rule, 'source': network_selector(rule['source']), 'destination': network_selector(rule['destination']),
                      'port': 'any' if rule['port'] == 'any' else port_number(rule['port'])})
    return {'default': value['default'], 'rules': rules}


def draft_policy(value):
    """Validate shape/size only, so invalid unfinished edits can survive restart."""
    keys(value, {'default', 'rules'}, 'draft firewall policy')
    require(isinstance(value['default'], str) and len(value['default']) <= 128, 'Invalid draft default policy.')
    require(isinstance(value['rules'], list) and len(value['rules']) <= MAX_RULES, 'Invalid draft rule count.')
    for rule in value['rules']:
        keys(rule, RULE_FIELDS, 'draft firewall rule')
        require(all(isinstance(v, str) and len(v) <= 128 for v in rule.values()), 'Invalid draft rule value.')
    return deepcopy(value)


def editable_policy(value):
    return {'default': value['default'], 'rules': [{k: str(v) for k, v in rule.items()} for rule in value['rules']]}


def interval(selector):
    net = IPv4Network('0.0.0.0/0' if selector == 'any' else selector)
    return int(net.network_address), int(net.broadcast_address)


class Policy:
    def __init__(self, value):
        self.value = policy(value)
        self.rules = [(interval(r['source']), interval(r['destination']),
                       (1, 65535) if r['port'] == 'any' else (r['port'], r['port']), r) for r in self.value['rules']]

    def decision(self, source, destination, port):
        """No I/O, and no inferred transport permission from reachability."""
        return self.decide_int(int(IPv4Address(source)), int(IPv4Address(destination)), port)

    def decide_int(self, source, destination, port):
        for index, (src, dst, ports, rule) in enumerate(self.rules):
            if src[0] <= source <= src[1] and dst[0] <= destination <= dst[1] and ports[0] <= port <= ports[1]:
                return rule['action'] == 'allow', f"rule {index + 1} [{rule['id']}] {rule['action']} tcp {rule['source']} → {rule['destination']} port {rule['port']}"
        return self.value['default'] == 'allow', f"default policy {self.value['default']} (no rule matched)"

    def isolation(self, source, destination, port):
        """Exact finite partition of selectors; no sampling of arbitrary hosts.

        A rule's decision is constant between every source/destination/port
        boundary. One representative per cell proves the effective allow set.
        At 16 rules this has at most 35×35×35 cells and bounded rule scans.
        Shadowed/redundant rules are accepted when their effective policy is safe.
        """
        src, dst = int(IPv4Address(source)), int(IPv4Address(destination))
        allowed, reason = self.decide_int(src, dst, port)
        if not allowed:
            return False, 'Required TCP flow is still blocked by ' + reason + '.'
        axes = [{0, 2**32, src, src + 1}, {0, 2**32, dst, dst + 1}, {1, 65536, port, port + 1}]
        for s, d, p, _ in self.rules:
            for axis, bounds in zip(axes, (s, d, p)):
                axis.update((bounds[0], bounds[1] + 1))
        cells = [sorted(axis)[:-1] for axis in axes]
        for s in cells[0]:
            for d in cells[1]:
                for p in cells[2]:
                    if (s, d, p) != (src, dst, port):
                        ok, why = self.decide_int(s, d, p)
                        if ok:
                            return False, f"Overly broad effective permission: {IPv4Address(s)} → {IPv4Address(d)} TCP {p} is allowed by {why}. Only {source} → {destination} TCP {port} may be allowed."
        return True, f"Effective TCP permission is limited to {source} → {destination} port {port}; every other selector flow is denied."
