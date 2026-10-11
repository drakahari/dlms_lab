# Network, DNS and Web Evidence — Simulator collections

Twelve original **Simulator / Offline snapshots** activities, grouped into three
four-lab collections. These are saved fictional observations, not live diagnostics
of your computer or guest. No QEMU is needed or started. Recommended order is
Network → DNS → Web, but every lab is available independently.

Preparation: Text, Filters & Reports; virtual paths, `cat`, `head`/`tail`, `grep -F`,
`sort` and `>` redirection. Read `reference.txt` for realistic tool/configuration
excerpts and `HELP.txt` for the model interpretation and common mistakes.
Reading those files does **not** run ip, dig, curl, ss, openssl or a server.

## What the score means

Each lab checks **80 points of factual report contents** and **20 points for
displaying that final report with `cat` after the last write**. There are no
additional points for rote reading every source or an already enforced invariant.
Empty, incomplete or incorrect facts fail their report objective. Construct the
specified records in `report.txt`; preserve record spelling, order and final LF.
Equivalent supported filters and paths work. The existing checker does **not**
normalize arbitrary equivalent report formatting or assess free-form prose.

**Self-reviewed:** interpretation, possible causes, uncertainty, proposed next
checks and operational decisions. A 100/100 score does not certify diagnosis,
repair or mastery. Compare your explanation with the model in `HELP.txt` outside
the exact factual report. Challenge hides guided commands and hints; conceptual
reference material remains available, and no reasoning score is invented.

Only the declared virtual report is writable. Sources are read-only; no host
file/process/network access is available. `>` truncates before reading; errors
do not undo writes. Any actual write invalidates previous reading evidence, so
finish all report writes before `cat report.txt`. See [grammar and limits](text-stream-contract.md).

## Lesson matrix and owner walkthrough

Library collection → **Start/Continue** → Learn or Challenge → terminal. Read
the brief and non-modal Lab details, `cat reference.txt`, then `cat HELP.txt`.
In Learn, follow the two steps; in Challenge, choose supported filters yourself.
Inspect the final report and Submit. Self-review the question below afterward.
Mode changes start fresh attempts while preserving history. Reset confirms,
restores initial virtual data/removes reports and preserves completed history.
Reopening the same profile resumes its exact pack, mode, outputs and pending input.

| Collection / title | Learner action and automatically checked report | Self-review boundary / limited objective |
|---|---|---|
| Network: Read interface and address evidence | Retain interface administrative/operational state, address/prefix and missing route/DNS/test markers with host/time | UP and global scope do not establish remote connectivity; 205.3 preparation |
| Compare routes and reachability evidence | Retain two clients' route and test evidence, distinguishing unattempted connection after lookup failure from HTTP 503 | A working remote HTTP path is not application health; cause remains unknown; 205.3 |
| Separate name resolution from connectivity | Retain numeric HTTP success, named curl exit 6 and configured resolver | Configured resolver is not proof of its fault; numeric/Host requests need not select the same site; 205.3 |
| Write a timestamped network incident handover | Select NET-7 observations and sort UTC timestamps, preserving vantage points and absent change audit | Later success is not proof of a particular repair or lasting recovery; 205.3 |
| DNS: Distinguish resolver and authoritative responses | Retain question/type/server, AA/RA/RD, answers, negative response categories and timeout without RCODE | Non-AA is not proof of cache; empty NOERROR needs authority/context; 207.1 preparation |
| Inspect a zone and a supplied validation finding | Retain origin, TTL seconds, SOA serial, NS and conflicting ordinary CNAME/A plus supplied validator finding | Identify intended design before proposing repair; no validation/reload performed; 207.2 preparation |
| Compare delegation and authoritative versions | Retain parent delegation/glue and each authoritative SOA/A answer | Different versions establish inconsistency here, not deployment intent or cause; 207.2 |
| Prepare a DNS incident handover | Select DNS-9 records, sort UTC times and preserve separately supplied cache-origin trace/remaining TTL | Unexpired cache may differ; future convergence and intended deployment unproved; 207.1/207.2 |
| Web: Compare listener and request evidence | Retain IPv4 loopback binding, local HTTP 503, remote refusal/exit 7 and local log with time | LISTEN is not remote availability; status alone is not cause; 208.1 preparation |
| Correlate virtual hosts and request names | Retain loaded address/port order, ServerName/DocumentRoot and supplied Host/body results | Same status can serve different sites; this is plain HTTP, not DNS or SNI testing; 208.1 |
| Separate TLS name and validity evidence | Retain requested name, SAN, dates, explicit hostname error/abort and curl result | Separate hostname, chain, dates and untested revocation; no cryptographic check or key provisioning; 208.2 preparation |
| Write a reverse-proxy incident handover | Select WEB-4 records, sort timestamp/bytewise tie order, retain upstream and refused connection/502 observations | Equal-time order is not causality; crash/firewall/deployment explanations remain hypotheses; 208.4 preparation |

Try one incorrect/incomplete extraction and Submit, then repair the report and
retry; nothing requires an exact transcript. Read after the last write to earn the
inspection objective. Test Reset, then close and reopen the same **disposable**
profile. Export scenario content separately from personal history or profile backup.
Existing hidden/removed choices and pinned imported versions are preserved.

## References and coverage

Official objectives verified **2026-10-10**: LPIC-2 **4.5.0**, exams 201-450/202-450.
[Official LPI objectives](https://www.lpi.org/our-certifications/exam-201-202-objectives/).
These collections provide **limited interpretation reinforcement**, not complete
205.3 troubleshooting, 207.1/207.2 DNS administration, 208.1 Apache, 208.2 HTTPS or
208.4 nginx coverage. No LPI affiliation or endorsement. No DNSSEC/security claim.

Primary semantic references: [kernel interface states](https://docs.kernel.org/networking/operstates.html),
[iproute2 manuals](https://github.com/iproute2/iproute2/tree/main/man/man8),
[ISC BIND dig/checkzone manual](https://bind9.readthedocs.io/en/stable/manpages.html),
[RFC 1035 response semantics](https://www.rfc-editor.org/rfc/rfc1035),
[Apache name-based vhosts](https://httpd.apache.org/docs/2.4/vhosts/name-based.html),
[curl exits/options](https://curl.se/docs/manpage.html),
[OpenSSL verification options](https://docs.openssl.org/3.5/man1/openssl-s_client/),
[nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html).
Excerpts and normalized records are original synthetic teaching data, not captures
from services executed in this task. GNU comparisons validate text filtering only.

These complement [Resource Evidence simulator](lpic-2-resource-simulator.md),
[real-VM resource/capacity practice](vm-preview/resource-unit.md) and
[real-VM storage practice](vm-preview/storage-unit.md). Those VM activities require
their approved optional guest and are separately self-reviewed. Actual live
network/DNS/web configuration needs a separately approved environment and curriculum;
none is introduced here.

Eight simulator collections now fit the unchanged maximum of eight; 42 appearances,
38 unique Linux packs plus three networking labs. VM inventory remains nine units/
76 lessons. All prior application/pack bytes are unchanged except the trusted
collection index that appends these descriptors. No engine/schema/UI/controller,
storage, image, backup format or registry-limit change.

## Disposable screenshots and acceptance

See [retained checks, screenshots and exact launch command](offline-evidence-acceptance.md).
Offscreen and native QtTest automation are distinct from physical-keyboard,
wheel/trackpad and screen-reader acceptance, which remain outstanding.
