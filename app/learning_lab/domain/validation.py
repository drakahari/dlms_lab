"""Strict versioned pack validation. No executable predicates or expressions."""
import ipaddress
import json
import re
from copy import deepcopy

BASE_CAPABILITIES = {"ipv4-routing", "dns", "portal-reachability"}
CAPABILITIES = BASE_CAPABILITIES | {"tcp-connect", "ordered-firewall"}
FIELDS = {"address", "prefix", "gateway", "dns"}
PREDICATES = {
    "address_equals": {"device", "value"},
    "prefix_equals": {"device", "value"},
    "reachable": {"source", "target"},
    "dns_and_portal": {"source", "hostname"},
    "tcp_allowed": {"source", "target", "port"},
    "tcp_blocked": {"source", "target", "port"},
    "tcp_isolated": {"source", "target", "port"},
}


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def keys(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected), f"Invalid fields in {label}.")


def text(value, label, limit=16384):
    require(isinstance(value, str) and 0 < len(value) <= limit, f"Invalid {label}.")
    require(not any(ord(c) < 32 and c not in "\n\t" for c in value), f"Control characters in {label}.")


def address(value):
    require(isinstance(value, str), "IPv4 address must be text.")
    try:
        result = ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError as exc:
        raise ValidationError("Enter a valid IPv4 address.") from exc
    require(not result.is_multicast and not result.is_unspecified and not result.is_loopback,
            "Use a unicast simulation address.")
    return result


def prefix(value):
    if isinstance(value, str):
        if re.fullmatch(r"/?[0-9]{1,2}", value):
            value = int(value.lstrip("/"))
        elif re.fullmatch(r"[0-9.]+", value):
            try:
                bits = f"{int(ipaddress.IPv4Address(value)):032b}"
            except ipaddress.AddressValueError as exc:
                raise ValidationError("Invalid subnet mask.") from exc
            require(bool(re.fullmatch(r"1+0+", bits)), "Subnet masks must contain contiguous leading ones.")
            value = bits.count("1")
    require(type(value) is int and 1 <= value <= 30, "This lab supports host prefixes /1 through /30.")
    return value


def host(ip, length):
    parsed = address(ip)
    network = ipaddress.IPv4Network((parsed, prefix(length)), strict=False)
    require(parsed not in (network.network_address, network.broadcast_address),
            "Network and broadcast addresses cannot be assigned to a device.")


def settings(value):
    keys(value, FIELDS, "device settings")
    result = {k: str(v).strip() for k, v in value.items()}
    result["prefix"] = prefix(value["prefix"] if type(value["prefix"]) is int else result["prefix"])
    host(result["address"], result["prefix"])
    address(result["gateway"])
    address(result["dns"])
    return result


def initial_applied(pack):
    result = deepcopy(next(iter(pack['initial_state'].values())))
    if 'firewall' in pack:
        result['firewall'] = deepcopy(pack['firewall']['initial_policy'])
    return result


def applied_state(pack, value):
    keys(value, FIELDS | ({'firewall'} if 'firewall' in pack else set()), 'applied state')
    result = settings({k: value[k] for k in FIELDS})
    if 'firewall' in pack:
        from .firewall import policy
        result['firewall'] = policy(value['firewall'])
    return result


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def decode(raw, limit=262144):
    require(isinstance(raw, (str, bytes)) and len(raw) <= limit, "JSON exceeds the allowed size.")
    try:
        return json.loads(raw, object_pairs_hook=unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValidationError("Non-finite number.")))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ValidationError(f"Invalid JSON: {exc}") from exc


def validate_pack(pack, *, hint_limit=None):
    require(isinstance(pack, dict), "Invalid pack object.")
    version = pack.get('schema_version')
    require(type(version) is int and version in (1, 2), "Unsupported pack schema.")
    keys(pack, {"schema_version", "lab_id", "content_version", "required_capabilities", "metadata",
                "topology", "initial_state", "editable_fields", "objectives", "hints"} | ({'firewall', 'tcp_services'} if version == 2 else set()), "pack")
    require(isinstance(pack["lab_id"], str) and re.fullmatch(r"[a-z][a-z0-9-]{0,63}", pack["lab_id"]), "Invalid lab ID.")
    require(isinstance(pack["content_version"], str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", pack["content_version"]), "Invalid content version.")
    caps = pack["required_capabilities"]
    require(isinstance(caps, list) and all(isinstance(x, str) for x in caps), "Invalid capabilities.")
    require(len(caps) == len(set(caps)) and set(caps) == (CAPABILITIES if version == 2 else BASE_CAPABILITIES), "Unsupported or missing engine capabilities.")
    meta = pack["metadata"]
    keys(meta, {"title", "topic", "difficulty", "minutes", "brief"}, "metadata")
    for key in ("title", "topic", "difficulty", "brief"):
        text(meta[key], key)
    require(type(meta["minutes"]) is int and 1 <= meta["minutes"] <= 240, "Invalid duration.")
    topology = pack["topology"]
    keys(topology, {"devices", "segments"}, "topology")
    segments = topology["segments"]
    require(isinstance(segments, list) and 1 <= len(segments) <= 64 and all(isinstance(x, str) for x in segments), "Invalid segments.")
    require(len(segments) == len(set(segments)), "Duplicate segments.")
    for segment in segments:
        require(bool(re.fullmatch(r"[A-Za-z0-9_-]{1,32}", segment)), "Invalid segment ID.")
    devices = topology["devices"]
    require(isinstance(devices, list) and 1 <= len(devices) <= 32, "Invalid device count.")
    ids, ips = set(), set()
    for device in devices:
        keys(device, {"id", "role", "interfaces", "gateway", "dns", "forwarding", "records", "endpoints"}, "device")
        name = device["id"]
        require(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,32}", name) and name not in ids, "Invalid or duplicate device ID.")
        ids.add(name)
        require(device["role"] in ("workstation", "router", "server"), "Invalid device role.")
        require(type(device["forwarding"]) is bool, "Invalid forwarding value.")
        require(not device["forwarding"] or device["role"] == "router", "Only routers forward packets.")
        for key in ("gateway", "dns"):
            require(device[key] is None or isinstance(device[key], str), f"Invalid {key}.")
            if device[key] is not None:
                address(device[key])
        interfaces = device["interfaces"]
        require(isinstance(interfaces, list) and 1 <= len(interfaces) <= 8, "Invalid interfaces.")
        interface_ids = set()
        for iface in interfaces:
            keys(iface, {"id", "segment", "address", "prefix"}, "interface")
            require(isinstance(iface["id"], str) and re.fullmatch(r"[A-Za-z0-9_-]{1,32}", iface["id"]) and iface["id"] not in interface_ids, "Invalid interface ID.")
            interface_ids.add(iface["id"])
            require(iface["segment"] in segments, "Dangling segment reference.")
            require(type(iface["prefix"]) is int, "Pack prefixes must be integers.")
            host(iface["address"], iface["prefix"])
            require(iface["address"] not in ips, "Duplicate interface address.")
            ips.add(iface["address"])
        require(isinstance(device["records"], dict) and len(device["records"]) <= 64, "Invalid DNS records.")
        require(isinstance(device["endpoints"], list) and len(device["endpoints"]) <= 32, "Invalid endpoints.")
        for hostname, ip in device["records"].items():
            require(isinstance(hostname, str) and re.fullmatch(r"[a-z0-9.-]{1,253}", hostname), "Invalid DNS name.")
            address(ip)
        require(all(isinstance(x, str) and re.fullmatch(r"[a-z0-9.-]{1,253}", x) for x in device["endpoints"]), "Invalid endpoint name.")
    initial = pack["initial_state"]
    require(isinstance(initial, dict) and len(initial) == 1, "Schema 1 requires one editable workstation.")
    source = next(iter(initial))
    require(source in ids, "Unknown editable device.")
    editable_device = next(d for d in devices if d["id"] == source)
    require(editable_device["role"] == "workstation" and len(editable_device["interfaces"]) == 1, "Editable device must be a single-interface workstation.")
    normalized = settings(initial[source])
    require(normalized == initial[source], "Initial settings must use canonical values.")
    require(initial[source]["address"] == editable_device["interfaces"][0]["address"] and initial[source]["prefix"] == editable_device["interfaces"][0]["prefix"], "Initial interface mismatch.")
    keys(pack["editable_fields"], {source}, "editable fields")
    fields = pack["editable_fields"][source]
    require(isinstance(fields, list) and all(isinstance(x, str) for x in fields) and len(fields) == len(set(fields)) and (len(fields) > 0 or version == 2) and set(fields) <= FIELDS, "Invalid editable fields.")
    if version == 2:
        from .firewall import policy, port_number
        fw = pack['firewall']
        keys(fw, {'device', 'initial_policy', 'editable'}, 'firewall declaration')
        require(isinstance(fw['device'], str) and any(d['id'] == fw['device'] and d['role'] == 'router' and d['forwarding'] for d in devices), 'Firewall must belong to a forwarding router.')
        require(fw['editable'] == ['rules', 'default'], 'Unsupported firewall editable fields.')
        require(policy(fw['initial_policy']) == fw['initial_policy'], 'Pack firewall values must be canonical.')
        services = pack['tcp_services']
        require(isinstance(services, list) and 1 <= len(services) <= 32, 'Invalid TCP services.')
        service_ids = set()
        for service in services:
            keys(service, {'device', 'ports'}, 'TCP service')
            require(isinstance(service['device'], str) and service['device'] in ids and service['device'] not in service_ids, 'Invalid or duplicate service device.')
            service_ids.add(service['device'])
            require(isinstance(service['ports'], list) and 1 <= len(service['ports']) <= 32 and all(type(p) is int for p in service['ports']) and len(service['ports']) == len(set(service['ports'])), 'Invalid service ports.')
            for p in service['ports']: port_number(p)
    for device in devices:
        require(all(ip in ips for ip in device["records"].values()), "DNS record points outside topology.")
        require(all(any(d["records"].get(name) in {i["address"] for i in device["interfaces"]} for d in devices) for name in device["endpoints"]), "Endpoint has no matching DNS record.")
    objectives = pack["objectives"]
    require(isinstance(objectives, list) and 1 <= len(objectives) <= 32, "Invalid objectives.")
    objective_ids = set()
    for objective in objectives:
        keys(objective, {"id", "label", "points", "predicate", "params"}, "objective")
        text(objective["id"], "objective ID", 64)
        require(objective["id"] not in objective_ids, "Duplicate objective ID.")
        objective_ids.add(objective["id"])
        text(objective["label"], "objective label")
        require(type(objective["points"]) is int and 1 <= objective["points"] <= 100, "Invalid objective weight.")
        pred = objective["predicate"]
        require(isinstance(pred, str) and pred in PREDICATES, "Unsupported predicate.")
        params = objective["params"]
        keys(params, PREDICATES[pred], "predicate parameters")
        require(params.get("device", params.get("source")) == source, "Predicate must reference the editable workstation.")
        if pred == "address_equals":
            host(params["value"], initial[source]["prefix"])
        elif pred == "prefix_equals":
            require(type(params["value"]) is int, "Invalid required prefix.")
            host(initial[source]["address"], params["value"])
        elif pred == "reachable":
            require(params["target"] in ips, "Objective has an unknown target.")
        elif pred == 'dns_and_portal':
            require(any(params["hostname"] in d["endpoints"] for d in devices), "Objective has an unknown endpoint.")
        else:
            require(version == 2, 'TCP predicate requires schema 2 capabilities.')
            require(isinstance(params['target'], str) and params['target'] in ips, 'TCP objective has an unknown target.')
            require(type(params['port']) is int, 'Objective TCP port must be an integer.')
            port_number(params['port'])
            owner = next(d for d in devices if any(i['address'] == params['target'] for i in d['interfaces']))
            require(any(s['device'] == owner['id'] and params['port'] in s['ports'] for s in services), 'TCP objective requires a declared listening service.')
    require(sum(o["points"] for o in objectives) == 100, "Rubric must total 100 points.")
    # Prevent contradictory exact-value objectives; functional feasibility is also
    # checked by routing a candidate state in validate_feasibility().
    for pred in ("address_equals", "prefix_equals"):
        values = [o["params"]["value"] for o in objectives if o["predicate"] == pred]
        require(len(set(values)) <= 1, "Contradictory constraints.")
    require(isinstance(pack["hints"], list) and (len(pack['hints']) == 3 if hint_limit is None else len(pack['hints']) <= hint_limit),
            'Exactly three hints are required.' if hint_limit is None else 'Too many hints.')
    for hint in pack["hints"]:
        text(hint, "hint")
    return pack
