# Bundled lab pack schemas 1 and 2

The bundled packs are `learning_lab/packs/gateway-dns.json` and `subnet-boundary.json` (schema 1), plus `service-firewall.json` (schema 2). All are JSON data, loaded before the UI is created. There is no import or download feature.

| Field | Contract |
| --- | --- |
| `schema_version` | Integer 1 or 2; unknown versions rejected |
| `lab_id` | Stable lowercase identifier, at most 64 characters |
| `content_version` | Three-part numeric version string |
| `required_capabilities` | Schema 1 declares `ipv4-routing`, `dns`, `portal-reachability`; schema 2 adds `tcp-connect` and `ordered-firewall` |
| `metadata` | Title, topic, difficulty, minutes, plain-text brief |
| `topology` | Named segments and devices with interfaces, gateway, DNS, forwarding, records and endpoint names |
| `initial_state` | One editable, single-interface workstation; address, prefix, gateway, DNS |
| `editable_fields` | A unique subset (nonempty in schema 1; can be empty when the firewall is the editable state in schema 2) of the workstation's four fields; omitted fields remain fixed at initial values |
| `objectives` | Stable IDs, labels, positive points totaling 100, predicate IDs and validated parameters |
| `hints` | Exactly three progressive plain-text hints |

Predicates are implemented in Python: `address_equals(device,value)`, `prefix_equals(device,value)`, `reachable(source,target)`, and `dns_and_portal(source,hostname)`. No expression language, eval, embedded code, dynamic imports, or paths exist in the schema. Adding mechanics requires engine changes and tests.

Topology links are shared named segments: interfaces on the same segment can discover each other. The engine chooses the longest connected subnet match, then the configured default gateway; routers must explicitly forward. Replies must have a valid return route. DNS first requires a route to the configured simulated server. Portal checks require DNS, a reachable address and a declared endpoint name; they model no transport protocol.

Limits: 256 KiB pack, 32 devices, 64 segments, 8 interfaces per device, 64 DNS records per device, 32 endpoint names per device, 32 objectives, 16 KiB per text field. Prefixes /1–/30 are supported; /31 point-to-point and /32 host routes are outside schema 1. Input accepts numeric prefixes, slash prefixes and contiguous dotted subnet masks. Hostmask notation is rejected.

Validation rejects duplicate JSON keys, duplicate lab/device/interface/objective IDs, unknown fields, invalid references, malformed values, network/broadcast interface addresses, unsupported capabilities and unsatisfiable objectives. A finite search of declared gateways and DNS servers checks that the objective set can be satisfied within the declared editable fields. Fixed gateway/DNS values are retained in this check. Faulty gateway/DNS values are intentionally allowed as starting faults.

All three bundled labs are registered explicitly. `load_catalog` rejects duplicate IDs. The subnet lab uses the existing IPv4 engine and existing predicates; no new simulation mechanic was added. Apply and saved-record validation enforce fixed fields. The firewall capability is declared only by schema 2.

## Schema 2 firewall declarations

Schema 2 adds exactly two data fields:

- `firewall`: a forwarding router device ID, `initial_policy`, and `editable: ["rules", "default"]`.
- `tcp_services`: bounded entries with a known device ID and unique integer listening ports.

A policy has explicit `default: "allow" | "deny"` and an ordered `rules` array of at most 16 entries. Each rule contains a unique bounded `id`, `action: "allow" | "deny"`, `protocol: "tcp"`, source and destination IPv4 selectors, and a destination `port` (1–65535 or `"any"`). Selectors use canonical IPv4 CIDR or `"any"`; UI host input is normalized to /32 when applied. Invalid values, noncanonical pack values, host bits in a network selector, unknown fields, and duplicate IDs are rejected. There are no expressions, scripts or paths.

New allowlisted predicates are `tcp_allowed(source,target,port)`, `tcp_blocked(source,target,port)` and `tcp_isolated(source,target,port)`. Targets must be known interfaces with a declared listening port. A blocked objective requires an actual firewall denial; broken routing, DNS or a missing listener is not accepted as isolation. Firewall packs require one narrow permission objective, and feasibility uses an engine-built narrow candidate on the declared firewall's forwarding path.

TCP uses the same routing and return-path engine. The firewall evaluates new outbound TCP connects crossing its router. A permitted connection's replies are established in this bounded model; reply traffic does not require a second reverse allow. ICMP and modeled DNS are independent of the TCP rule list. Ping and the portal reachability helper do not validate TCP.

`tcp_isolated` checks the effective first-match allow set over the whole IPv4 selector and destination-port space. Selector boundaries form a finite partition on which every rule decision is constant. This rejects broad grants while accepting shadowed broad rules, unrelated denies, renamed rules and equivalent safe orderings. Default allow can pass only when earlier rules deny all other flow cells. Analysis is bounded by 16 rules; it creates no packets and performs no network I/O.
