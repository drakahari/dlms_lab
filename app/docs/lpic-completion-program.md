# Toward comprehensive LPIC-1 and LPIC-2 preparation support

Original planning checkpoint, 2026-10-11. Read with the [complete objective/subtopic matrix](lpic-comprehensive-audit.md)
and [machine evidence inventory](lpic-comprehensive-audit.json). No new lessons,
contracts, images, guest launches or runtime fixes are part of this assessment.
Original exercises only; no exam dumps or reproduced protected exam questions.

## Four exam summaries — historical assessment checkpoint

This table preserves the pre-family assessment. After the delivered Local Shell family, exam 101 is **0 complete /19 partial /4 missing**; the other three rollups are unchanged. Use the updated comprehensive matrix for current subtopic evidence.

All four active exams have official weight 60. Counts refer to **whole objective
breadth**, not lesson counts or a readiness percentage. “Partial” includes a
substantive narrow factual/knowledge exercise; no whole objective is complete.
Adjacent preparation without the required skill is counted missing.

| Active exam / version | Covered / partial / missing | What actually exists | Principal remaining breadth |
|---|---|---|---|
|101-500 /5.0|0 /18 /5|Real Bash/vi/process practice, scoped Debian transactions/libraries, virtual file/text/permission exercises, GPT/ext4 maintenance.|Boot manager/layout, RPM, guest/template concepts; history, richer filters/find/archives, links/FHS, special bits, privileged priority and editor configuration.|
|102-500 /5.0|0 /10 /9|Small scripts, actual disposable identities, cron/timers, local journal/rsyslog/rotation; bounded networking simulations.|Persistent shell startup, scheduler policies/at, locale/time, GUI/accessibility, mail/printing, real persistent networking/resolver settings, security audit/SSH/GPG.|
|201-450 /4.5.0|0 /9 /11|Real bounded resource observations/synthetic capacity reasoning, systemd/service recovery, read-only kernel queries, ext4 copy recovery, manual archives; static network facts.|Kernel compilation/runtime changes, boot/rescue breadth, swap/automount/encryption, other filesystems/RAID/LVM/storage protocols, live networking/throughput, source builds/notices and production backup scope.|
|202-450 /4.5.0|0 /6 /15|Factual zone/delegation, Apache/vhost/TLS/proxy excerpts and bounded simulated filtering; credential-database preparation.|Operational DNS/security, web/TLS/Squid/nginx, Samba/NFS, DHCP/PAM/LDAP, mail/delivery/mailboxes, routing/FTP/SSH/auditing/VPN. **No shipped live Exam 202 service unit.**|

[Active LPIC-1 objectives](https://www.lpi.org/our-certifications/exam-101-102-objectives/),
[active LPIC-2 objectives](https://www.lpi.org/our-certifications/exam-201-202-objectives/),
accessed 2026-10-11. LPI's [annual review](https://www.lpi.org/wp-content/uploads/2026/03/2025_LPI-AnnualReview.pdf)
announces planned 2026 LPIC-2 updates, while [version 5.0.0](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V5.0)
remains draft. Confirm the final transition before committing to large
version-specific service/kernel batches. Durable Linux skills remain valuable;
old objective numbers must not be silently repurposed.

## What complete would mean

For every active objective and substantive subtopic:

1. Explain its purpose, prerequisites, tool/platform variants and common mistakes.
2. Supply appropriate independent practice: real administration where behavior
   depends on identities, devices, traffic, authentication or services; supplied
   evidence for interpretation; knowledge exercises for awareness topics.
3. Provide clear positive/negative outcomes, expected evidence and recovery.
   Challenge must require transfer rather than only copying a model transcript.
4. State what is automatically checked versus externally/learner reviewed.
   A byte-exact report or a self-reviewed completion button is not a diagnosis
   assessor. Use original knowledge checks/rubrics where real practice is
   inappropriate; do not pretend the current engine already implements quizzes.
5. Verify supported images/versions and installed resources, safe lifecycle,
   progress/pins/backup exclusions, readable native delivery and prerequisites.
6. Independently review coverage and teaching accuracy. Reconcile changes to
   official objectives and explicitly retain legacy lesson/image revisions.

This would support comprehensive preparation, not promise a pass, certify
live-system competence or imply LPI affiliation. “Fully automatically assessed”
is a separate ambition, not a prerequisite to honest self-reviewed reasoning.
Publication also needs independent platform and redistribution readiness.

## Five kinds of remaining work

| Work type | Useful next contributions | Boundary |
|---|---|---|
|Existing-engine content|Text transformations, careful extraction and report comparison for distinct operational incidents; actual local-shell/file lessons on existing guests.|More snapshots alone cannot close operational gaps. Simulator collection capacity8 and VM9/76 are full. New collection/lesson/default/retained capacity needs explicit bounded approval.|
|Assessment within current contracts|Add wrong/incomplete/stale-work cases, demonstrate equivalent supported command constructions, make score requirements and model/self-review rubrics explicit.|Exact file predicates remain exact; free-form equivalent prose, forecasts or causes cannot be semantically assessed. Copying a reference still satisfies current factual-report checks.|
|New simulator capabilities|Only consider a separately designed semantic factual-field/rubric or original knowledge-check mechanism if it adds value across many lessons.|Requires engine/contract/grading/identity/version review. No generalized shell, live networking or fake service effects. Prefer real VM work over stretching simulations.|
|Real environments|Boot/kernel/advanced storage, RPM/GUI, operational client/server networking, TLS/identity/mail, richer monitoring/source builds.|Approved versioned images/packages; some need additional virtual disks, guest privileges, credentials and isolated multiple guests/NICs. Existing host isolation is not authorization for those extensions.|
|Explanation/external practice|Firmware/storage hardware differences, cloud/container concepts, storage/media tradeoffs, platform variants, remote-desktop/accessibility and obsolete-command awareness.|Some hardware/platform skills are best practiced externally or with suitable GUI environments. Accessible user testing cannot be replaced by offscreen metadata assertions.|

## Estimated coherent backlog, not a promise

The following ranges are planning estimates based on distinct skill outcomes,
not hours. They assume current live lesson material can be reused for
prerequisites, all variants need not duplicate each exercise, and the active
objective versions remain the target. Thirteen families likely split into
**about16–22 reviewable units and122–166 new substantive exercises**. In addition,
**24–40 existing exercises** may need depth/negative/independent-transfer review,
and **16–24 short conceptual checks** could cover awareness topics, contingent on
an approved knowledge-check design or explicit external/self-review delivery.
These categories overlap in objectives, not in counted new exercises. A single
capstone can validate several already taught skills; it is not new objective
coverage. Re-estimate after each family's tool/capability probe and the LPIC-2
transition. These ranges are not evidence that every gap fits content-only work.

| Family / estimated new exercises | Outcomes and objective areas | Dependencies, effort and acceptance |
|---|---|---|
|1. Local shell, links and access10–12|History/startup/default editor; hard/soft links and safe copy; richer find/FHS; sticky/privileged-bit audit; scoped privileged priority; independent transfer.103.1/3/6/8,104.5–7,105.1,110.1.|Existing guest capabilities where actual probes pass; bounded registry expansion. Moderate content/verification. Check real inode/access/process evidence, mistakes, restart and exact cleanup.|
|2. Text and archive breadth8–10|stdin/stderr/tee/xargs, richer filters/regex/find, alternate archives/compression and robust script composition.103.2–4/7,105.2.|Tool probes; missing cpio/xz/etc requires separately approved image revision. Moderate; compare outputs/status/side effects including failures, spaces and empty input.|
|3. Account, scheduler, logging and recovery completeness8–12|Credential/aging policy, at/access rules, persistent/size-limited journals and rescue queries, user notices, complete backup planning/restoration.107.1–2,108.2,110.1–2,206.2–3.|at/other absent tools need image approval; credential exercises need explicit guest-only policy. Moderate; actual identities, denial, missed runs, meaningful retained recovery evidence, no unrelated units/crontabs.|
|4. Locale/time and desktop essentials10–14|Locale/encoding/timezone, controlled time-sync understanding, GUI/remote-desktop/accessibility, local mail aliases/printing.106.1–3,107.3,108.1/3/4.|Split conceptual and GUI/service units. New packages/GUI image; time/network and assistive-tech practice separate approvals. High platform breadth; verify actual configuration, queues/time interpretation and human accessibility practice.|
|5. RPM and image/cloud fundamentals8–12|Scoped RPM/DNF/Zypper metadata/lifecycle; clone identities, guest integration/cloud-init/container distinctions.102.5–6; disk-layout prerequisites102.1.|Separate offline distro/tool fixture image, no arbitrary repositories. High preparation; positive/negative dependency transactions, unchanged unrelated package state and exact pins; concept checks without assuming VM use teaches cloning.|
|6. Kernel, startup and separate boot recovery10–14|Source/build/module/config provenance, runtime controls, targets/SysV/LSB awareness, GRUB/rescue/alternate boot paths.101.1–3,102.2,201.1–3,202.1–3.|New versioned image/offline build inputs, boot media/controller graph review if required. High safety cost; recover from wrong configuration on expendable disks, preserve known-good boot and retained generations. Firmware/PXE/hardware limits explicit.|
|7. Advanced storage10–14|System layout/swap, broader filesystems, mount/automount/LUKS, RAID/LVM/snapshots, device-access/SAN awareness.102.1,104.1–3,203.1–3,204.1–3.|Separate package/disk/block-graph approval; storage protocols may need clients/network. High; verified disposable targets, mounted-repair refusals, redundancy failures and actual content/access restoration. No raw host devices.|
|8. Networking and security foundations10–14|IPv4/IPv6 persistent settings/resolver/NSS, route/traffic diagnosis, firewall/NAT, SSH/GPG trust, monitoring/audit concepts.109.1–4,110.1–3,200.1,205.1–3,212.1/3/4.|Isolated guest-only NICs/multiple peers, tools and test keys/credentials separately approved. High architecture cost; actual positive/negative client flows, persistent reboot state, verified identity, no host LAN/Internet listeners.|
|9. DNS and DHCP operations10–12|Authoritative/reverse/cache/delegation/consistency, TSIG/DNSSEC awareness/practice, narrow leases and failure diagnosis.207.1–3,210.1.|Offline server/client packages and isolated network; guest trust fixtures. High integration; query actual servers, validation/reload/expiry/negative cases, preserve unrelated configuration. Existing snapshots become prework, not operational credit.|
|10. Web/TLS/proxy operations8–12|Apache vhost/auth/log/capacity/redirect, CSR/key/chain/SNI/cipher policy, nginx reverse proxy and Squid ACLs.208.1–4.|Packages, isolated clients and test credentials/certificates. High; real requests and denials, trust/name/date distinctions, no private owner keys or public services.|
|11. Sharing and identity10–14|NFS/Samba actual client access, mappings and mount restrictions; PAM/SSSD/LDAP schemas/queries/access.209.1–2,210.2–4.|Multiple guest images, isolated networking and explicitly approved authentication fixtures. High; actual identities/denials, startup recovery and client/server evidence, avoid locking out guest recovery.|
|12. Mail, remote transfer and VPN12–16|SMTP queues/TLS, aliases/Sieve/IMAP, bounded FTP policy, OpenSSH recovery and VPN trust/routes.108.3,211.1–3,212.2–3/5.|Additional packages, guest-only credentials/keys and isolated clients/network. High; message/delivery/mailbox evidence, auth/relay restrictions and real tunnel flows, no public mail/FTP/VPN endpoints.|
|13. Source builds, monitoring and operational synthesis8–10|Verified configure/make/install/uninstall, monitoring deployment/forecast limits, backup media/suites and advisories/security tests.200.1–2,206.1–3,212.4.|Approved offline source/build/monitoring inputs; selected networking/tooling. High evidence cost; installed files/removal/dependencies, real series and inconclusive outcomes, safe advisory-driven decisions.|

These families cover the missing rows and widen partial rows in the audit; the
JSON is the authoritative per-objective gap list. Obsolete tools in active
objectives need historical/conceptual coverage with honest modern-platform
limitations, not unsafe recreation. Source builds are not covered merely by
unpacking an archive; configuration excerpts are not operational services.

## Staged completion program

1. **Foundations and evidence:** families1–3, preserve existing contracts and
   improve independent Challenge evidence. Confirm current LPIC-2 finalization
   status. Produce reviewed per-subskill rubrics, exact pins and gap updates.
2. **Platform/offline administration:** families4–7, with separately approved
   image/package/boot/disk scopes. Split awareness-only/platform-specific work
   from real administration. Each environment must have provenance, rollback,
   isolation and fresh installed-app lifecycle acceptance.
3. **Network architecture approval first:** authorize the smallest internal-only
   client/server topology and credential/trust fixtures, with a focused security
   review; then families8–11. No existing offline preview authority implies NIC
   or multi-VM authority. Keep core simulated app independent of virtualization.
4. **Services and synthesis:** families12–13, reuse earlier environments and
   introduce only separately approved capabilities. Test independent incidents,
   incomplete evidence and recovery, not only guided happy paths.
5. **Course/release acceptance:** independent objective/subtopic audit, original
   knowledge checks and cross-unit transfer; install on a fresh supported desktop,
   native keyboard/accessibility checks, all pinned-image and backup exclusions;
   reviewed image licensing/source closure, release authenticity and acquisition.
   Unfinished Qt review/ICU signing-key obligations remain release blockers.

A large autonomous **content** batch is realistic once environment/tool probes
and bounds pass. The whole program is not one content-only autonomous run:
network/VM/controller changes, package/image revisions, guest credentials,
assessment contracts, capacity and licensing/platform decisions each need
explicit authorization. Parallel review can speed independent units; it cannot
replace safety/coverage evidence or manufacture live behavior.

## Recommended next implementation approval

Largest sensible first batch: **10–12 lessons, “Local Shell & Filesystem
Administration: Completing the Foundations.”** Proposed sequence:

1. Distinguish login/non-login/child-shell startup using disposable HOME/account.
2. Inspect and edit isolated command history; explain persistence boundaries.
3. Choose an editor and verify default-editor behavior on a test file.
4. Create/identify hard links and explain inode/deletion semantics.
5. Repair relative/dangling symbolic links without changing originals.
6. Compare copy/link behavior and verify contents/metadata after independent changes.
7. Locate files by type/size/time and explain FHS placement; include only tools
   actually available, not invented locate/updatedb support.
8. Verify a sticky shared directory as two disposable identities; contrast access
   and deletion. Preserve unrelated users/groups.
9. Audit privileged bits and use scoped guest-root priority changes on an owned,
   bounded practice task; do not create a dangerous executable setuid helper.
10. Independent shell/link/file handover with mistakes and original preservation.
11–12, if substantive/probed: a second access-repair transfer and locating/editor
   application case; omit redundant filler and keep the batch at10 if appropriate.

Use existing unprivileged/admin images only where their capabilities are proven.
Required new probes (in the later authorized implementation) include actual
`ln`, history/startup/editor behavior, relevant find forms and privilege cases.
Package inventories do not prove those tools/workflows. Missing man/locate/editor
or other commands must stop that dependent scope; no silent install/image change.
The simulator cannot teach these missing real-shell/link/multiuser features
without an unapproved extension.

**Capacity decision needed:** authorize a narrowly bounded tenth VM unit and
86–88total lessons after the final10–12 scope is agreed; keep16 per unit. Audit
retained revisions, both default maps, image compatibility lists and serialized
parser sizes before changing them. Preserve all 76 lesson bytes/pins and verify
87/89 overflow as appropriate,11 units,17 per unit, old sessions and missing-image
refusal. No unbounded registry or fallback to privileged images.

### Suggested first-batch prompt (not authorization)

> Implement the agreed10–12 Local Shell & Filesystem Administration lessons after
> disposable-guest tool feasibility passes. Approve only the exact bounded
> registry/default/retained-map capacity increase agreed above. Preserve all
> current lesson/image/session pins and the controller. Use existing images;
> do not install packages, change privileges/authentication policy, networking,
> host configuration or assessment contracts. Scope startup/history/editor files
> to disposable guest accounts/HOME. Verify real link/inode/access/process
> outcomes, incorrect cases, originals, bounded tasks and repeatable cleanup in
> both modes. Keep completion self-reviewed. Stop dependent work if missing tools
> require an image revision. Use persistent evidence, shared VM exclusion,
> installed-wheel lifecycle/compatibility and native/offscreen gates. Leave the
> batch for independent review; no working-installation update/public release.

Owner decisions: approve the final first-batch scope/capacity; choose the active
versus finalized future LPIC-2 target when LPI announces it; separately authorize
any new environment, guest credentials/network/controller/assessment capability.
Public distribution/signing/hosting and runtime-warning remediation remain
separate decisions. No routine owner walkthrough is a completion gate.

## First authorized family delivered

[Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md) implements ten of the proposed 10–12 exercises using the unchanged guests. The exact approved capacity is ten units /86 total/16 per unit, with retained/default maps86 and unchanged parser/image limits. It widens partial history, startup/editor, find/FHS, special-bit/priority coverage and adds partial link coverage; no full objective is claimed. The original family estimate and historical 9/76 constraint above describe the pre-approval plan. No later family is authorized by this delivery. [Acceptance](vm-preview/local-shell-acceptance.md) records the frozen-content evidence and remaining platform/release gaps.

## Second completion-family evidence update

[Text & Archive Tools](vm-preview/text-archive-unit.md) adds eight lessons, for eleven units / 94 lessons. See [acceptance](vm-preview/text-operations-acceptance.md) for exact evidence. Active objective versions and whole-objective rollups remain unchanged: new practice widens partial 103.2/103.3/103.4; 105.2 and recovery are reinforcement. No automatic guest assessment, full coverage, xz or at claim. Earlier counts above are retained historical context.

## Third completion-family evidence update

[Accounts, Scheduling, Logging & Recovery](vm-preview/operations-unit.md) adds eight lessons for twelve units / 102 lessons. Active objective versions and whole-objective rollups remain unchanged: bounded additions widen partial107.1/108.2 practice;101.3 gains related wall-tool preparation, not advance-event notification; scheduler/access/recovery are reinforcement. No authentication-policy change, at, automatic guest assessment or public-release readiness claim. Earlier counts remain historical context.

## Next platform expansion — proposal only

The [reviewed platform approval bundle](lpic-platform-expansion-plan.md) and
[detailed lesson matrix](lpic-platform-expansion-plan.json) propose a fresh
Debian locale/encoding/time/at/xz unit and an independent AlmaLinux RPM/DNF
unit: 16–18 distinct outcomes, at most14 units/120 lessons with unchanged
per-unit and parser bounds. [Actual disposable probes](vm-preview/platform-feasibility.md)
confirmed existing locale/encoding/time inspection support and missing xz/at/RPM
tools. Debian13 deliberately removed mesg/write; those are not silently restored.

This is not authorization or delivered coverage. The shipped baseline remains
12 units/102 lessons and the comprehensive audit's active-version rollups stay
unchanged. Image/package/service/guest-policy and bounded capacity decisions
require owner approval before implementation. No controller, profile, backup,
network or automatic assessment change is proposed. LPIC-2 source builds,
maintenance notifications, boot/kernel and authentic network administration
remain separate later work.
