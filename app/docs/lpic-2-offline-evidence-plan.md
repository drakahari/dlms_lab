# Offline evidence content checkpoint

Baseline: `1201aaa69d409f765d54e81cf8ce0b42e35560ca`, clean main and live origin/main verified. Recovery: `offline-evidence-20261011T034639363368Z`, 469 source files copied and hash verified; no personal profile copied.

## Capability and overlap

Existing simulator inventory: 5 collections, 30 appearances / 26 unique Linux packs plus 3 networking labs. Fundamentals, Files & Permissions, Organize and Find, Text/Filters/Reports, Resource Evidence. Existing networking repairs gateway/DNS, subnet and ordered service firewall faults; new content instead correlates saved evidence. VM inventory: 9 units / 76 self-reviewed lessons (processes, resources, services, Bash, users, scheduling, backup, discovery, storage). No current VM DNS/web/network administration unit. Resource Evidence remains separate; none of the twelve below repeats CPU/cache/capacity exercises.

Three four-lab additions reach **8 collections / 38 unique Linux packs / 41 simulator labs**, within the unchanged 8-collection and 32-items-per-collection bounds. VM limits stay 9/76. Contract 5, filesystem schema 3 and portable schema 1 suffice: read immutable UTF-8 evidence, extract records with bounded text filters, write declared reports and inspect them. No live ip/dig/curl/ss/openssl or configuration validation, DNS updates, TLS negotiation, mounting or real networking.

Each report contains context, timestamps and selected facts copied from supplied annotated records. Score: exact report bytes (80) plus final report `cat` (20), after the last write. No points for rote reading every source. Equivalent supported filters/paths work; arbitrary equivalent report formatting is **not** normalized by this checker. Required format is disclosed. Model reasoning and next checks are in HELP.txt; reading keywords does not assess those explanations. Learn shows one step at a time; Challenge hides commands/hints. Reset preserves history and restores immutable sources; separate-process Resume retains mode, outputs, draft and exact pack pins.

## Lesson matrix — written before implementation

All are **Simulator / Offline snapshots**, fictional `.test` hosts and documentation IPv4 addresses. Actions: inspect sources, extract stated records, save report, read report, submit, self-review model. No repair is performed.

| Collection / lab | Scenario and supplied evidence | Automatically checked facts | Self-review / objective ceiling |
|---|---|---|---|
| Network: Interface/address evidence | client interface operational state and IPv4 records, absent route/DNS data | time, vantage, interface state, address/prefix, missing evidence markers | UP alone is not internet connectivity; 205.3 evidence interpretation preparation |
| Network: Routes/reachability | two vantage points: missing default route vs successful remote HTTP 503 | local route/test failure and independent remote response | ping vs TCP/HTTP; separate local routing failure from service response, not root cause; 205.3 |
| Network: Names/connectivity | same client's numeric HTTP success, hostname resolution error and resolver setting | time, numeric result, hostname error, configured resolver | isolate layers, request DNS evidence next, not prove DNS server fault; 205.3 |
| Network: Incident handover | out-of-order time-stamped observations including later recovery | sorted incident facts with vantage and status | chronology/correlation does not prove cause; 205.3 |
| DNS: Resolver/authority | annotated dig headers, NXDOMAIN, NOERROR empty answer, SERVFAIL and timeout | question, server, status, AA/RA flags, answer count and timeout | authoritative vs recursive roles and negative categories; 207.1 preparation |
| DNS: Inspect a zone | realistic zone excerpt plus supplied named-checkzone finding | origin, SOA serial, NS/A/CNAME records and supplied finding | validity does not prove intended records or live reload; 207.2 preparation |
| DNS: Delegation/consistency | parent delegation and two authoritative SOA/A responses | server identities, delegation, differing serials/answers at one time | compare same owner/type, no assertion which is intended or cache convergence; 207.2 |
| DNS: Incident handover | cached response followed by direct authoritative results | ordered facts, remaining TTL, serials and answers | remaining TTL is not proof of stale server; distinguish cache from server state; 207.1/207.2 |
| Web: Listener/request evidence | local listener, numeric request success, application 503 and refusal on another port | binding address/port, request/status/exit and log correlation | listening is not remote reachability; HTTP status not unique cause; 208.1 preparation |
| Web: Virtual-host selection | ordered Apache vhosts and Host request responses | first/default host, named host, document roots and supplied request outcomes | DNS resolves address, Host selects HTTP vhost; no config change; 208.1 |
| Web: TLS evidence | supplied SAN/dates and hostname-verification handshake result | requested name, SAN, time validity interval, error and curl exit | hostname vs chain/time vs application checks; no key/cert provisioning; 208.2 preparation |
| Web: Reverse-proxy handover | nginx proxy_pass excerpt, connect-refused log, 502 and direct upstream probe | timestamp, upstream endpoint, observed failures/statuses | refused is supported, process crash/firewall/config cause unconfirmed; 208.4 preparation |

## Reference and claim review

Verified 2026-10-10 local date: [official LPIC-2 objectives](https://www.lpi.org/our-certifications/exam-201-202-objectives/) version **4.5.0**, exams 201-450/202-450. These exercises are limited interpretation reinforcement/preparation, **not** configuration, live troubleshooting, full objective coverage or endorsement. No 207.3 DNS-security claim.

Semantic references: [kernel operational states](https://docs.kernel.org/networking/operstates.html), [iproute2 manuals](https://github.com/iproute2/iproute2/tree/main/man/man8), [ISC BIND manual/dig/checkzone](https://bind9.readthedocs.io/en/stable/manpages.html), [DNS response codes RFC 1035](https://www.rfc-editor.org/rfc/rfc1035), [Apache name-based vhosts](https://httpd.apache.org/docs/2.4/vhosts/name-based.html), [curl manual](https://curl.se/docs/manpage.html), [OpenSSL s_client](https://docs.openssl.org/3.5/man1/openssl-s_client/), [nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html). GNU reference checks validate only text filtering/redirection, not these saved service outputs.

## Acceptance checkpoints

Finish each collection before the next: validate all four packs; both modes correct/incomplete/incorrect/retry/last-write evidence, Reset, separate-process Resume and isolation; independent technical/checker review. Preserve previous failed evidence. Final: exact baseline preservation except collection index; unchanged engine/QML/controller/VM resources; full regression and GNU fixtures; native/offscreen compact/wide at DPR 1/1.5/2; menu persistence beyond polling interval; installed wheel outside checkout; independent final review. Physical keyboard, wheel/trackpad and accessibility remain outstanding. No real guests or owner profiles are used.
