# Curriculum coverage and release target — 11 October 2026

Audited against current official [LPIC-1 v5.0, 101-500/102-500](https://www.lpi.org/our-certifications/exam-101-102-objectives/) and [LPIC-2 v4.5 (4.5.0), 201-450/202-450](https://www.lpi.org/our-certifications/exam-201-202-objectives/), verified 2026-10-11. This is a repository/lesson/evidence audit, not LPI endorsement or an exam-readiness guarantee. Supersedes the historical pre-VM gap table in Unit 3; accepted scenario content is unchanged.

**Implemented** below means the stated subskills have exercises and evidence. **Partial** means significant objective skills still remain. **Reinforcement/preparation only** adds no complete-objective credit. **Missing** means there is no dedicated demonstrated exercise. **No complete official objective is claimed**. Simulated labs have objective grading within a bounded contract; VM completion is self-reviewed, not automatically assessed. Real guest execution evidence validates lesson feasibility, not every learner's mastery.

The core simulated app remains usable without VM images/QEMU. [Resource Evidence — Offline Snapshots](lpic-2-resource-simulator.md) adds four factual-report activities with self-reviewed interpretation; it adds no live measurement or diagnosis checker. [Network/DNS/Web offline evidence](lpic-2-offline-evidence.md) adds twelve factual-report activities; interpretation remains self-reviewed, with no live service operations. Eight simulator collections fit unchanged bounds. The 102 trusted VM lessons are twelve bounded units. Source availability is not a public guest-image release. Native physical-keyboard/accessibility acceptance and Qt/ICU redistribution blockers remain open.

## Comprehensive audit supersedes coarse coverage labels

The [11 October objective/subtopic audit](lpic-comprehensive-audit.md) independently
verifies **83 active objectives and 378 knowledge-area rows**, with official weights,
exact lesson IDs/content hashes, practice modality, assessment boundaries and
accepted validation references. The 84 rows below include removed 104.4 and are
a coarse roadmap overview, not a complete subtopic audit. Adjacent preparation
earns no operational credit. See the [staged completion program](lpic-completion-program.md)
for the revised per-exam counts, version-transition caveat and approval gates.
No existing lesson or runtime contract changes accompany these analysis reports.

## LPIC-1 — every published objective

| Objective | Status | Existing unit/evidence and essential gaps |
|---|---|---|
| 101.1 | Partial | [System Discovery & Packages](vm-preview/discovery-unit.md). Virtual CPU/PCI and /proc and /sys hardware observations. No USB tools, firmware/device configuration or physical-hardware control. |
| 101.2 | Partial | [System Discovery & Packages](vm-preview/discovery-unit.md). Current-boot kernel/log evidence and kernel arguments; boot stages explained. No loader interaction, boot options or recovery. |
| 101.3 | Partial | [Services & Recovery](vm-preview/admin-unit.md). Implemented clean reboot/service enabled-state observations; targets, runlevels and timed advance-notification practice still missing. [Accounts, Scheduling, Logging & Recovery](vm-preview/operations-unit.md). Bounded local wall delivery is related tool preparation; timed advance-notification before a major event remains missing, and sender success cannot establish comprehension. |
| 102.1 | Preparation only | [Linux Storage](vm-preview/storage-unit.md). Bounded regular-file GPT planning; no system root/var/home/boot/ESP, swap or LVM layout. |
| 102.2 | Missing | —. No dedicated demonstrated boot manager exercise. |
| 102.3 | Partial | [System Discovery & Packages](vm-preview/discovery-unit.md). Trusted executable dependencies, loader cache/configuration and canonical package ownership. No library installation or runtime loader changes. |
| 102.4 | Partial | [System Discovery & Packages](vm-preview/discovery-unit.md). Installed/archived ownership, versions, status and scoped verification; actual offline fixture installation, upgrade, dependency repair, reinstallation, remove/purge. No online repository administration or complete Debian workflow. |
| 102.5 | Missing | —. No dedicated demonstrated RPM ecosystem exercise. |
| 102.6 | Preparation only | [Processes & Jobs](vm-preview/processes-unit.md). Using an offline VM is not assessed image/cloud/container preparation. |
| 103.1 | Partial | [Bash & Safe Changes](vm-preview/bash-unit.md). Implemented quoting, lookup, temporary PATH/env and statuses; broader command/environment mastery remains partial. [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md). Isolated history insertion, inspection, entry deletion, explicit write and clean shell reopening; memory clear differs from disk history. Other command/tool breadth remains partial. |
| 103.2 | Partial | [Text & Reports](lpic-unit-3.md), [Bash & Safe Changes](vm-preview/bash-unit.md), [Backup & Recovery](vm-preview/backup-unit.md). Implemented bounded filters, anchored sed previews and hashes; broader utilities/options and binary/locale cases missing. [Text & Archive Tools](vm-preview/text-archive-unit.md). Real sorted join/comm reconciliation and order rejection; no CSV or duplicate-key policy invented. |
| 103.3 | Partial | [Organize & Find](lpic-unit-2.md), [Bash & Safe Changes](vm-preview/bash-unit.md), [Backup & Recovery](vm-preview/backup-unit.md). Implemented scoped file operations, quoted paths and tar/gzip recovery; recursive management and broader compression remain missing. [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md). Independent regular copies and bounded quoted type/name/byte-size/time find criteria. No recursive file-management or general archive breadth. [Text & Archive Tools](vm-preview/text-archive-unit.md). Grouped/pruned batched find and trusted regular-file newc cpio with separate restoration; xz and general archive breadth remain missing. |
| 103.4 | Partial | [Text & Reports](lpic-unit-3.md), [Bash & Safe Changes](vm-preview/bash-unit.md). Implemented pipes, stdout/stderr, truncation/append and pipeline status; wider composition remains incomplete. [Text & Archive Tools](vm-preview/text-archive-unit.md). Real descriptor ordering, tee partial bytes, immediate PIPESTATUS, owning-shell pipefail and literal NUL xargs with bounded batches. |
| 103.5 | Partial | [Processes & Jobs](vm-preview/processes-unit.md). Implemented actual process inspection, job control, scoped signals and logout survival; multiplexers and broader process workflows missing. |
| 103.6 | Partial | [Processes & Jobs](vm-preview/processes-unit.md). Implemented unprivileged nice/renice, refusal and actual values; the original unit is unprivileged; scoped guest-root recovery is added below. [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md). Actual existing-process niceness, denied unprivileged reversal and approved scoped guest-root reversal on one owned sleep. No scheduler/CPU-share guarantee. |
| 103.7 | Partial | [Bash & Safe Changes](vm-preview/bash-unit.md). Implemented BRE/ERE, anchors/classes, matches/nonmatches, sed replacement; broader filesystem/regex tasks missing. grep-F alone adds no regex coverage. |
| 103.8 | Partial | [Bash & Safe Changes](vm-preview/bash-unit.md). Implemented actual vi modes, navigation, edits, search and rollback; persistent editor configuration and broader editor awareness remain missing. [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md). Temporary VISUAL/EDITOR through sensible-editor with actual Vim Tiny editing and preserved before-copy. No global alternatives, persistent editor configuration or Emacs completeness. |
| 104.1 | Partial | [Linux Storage](vm-preview/storage-unit.md). Regular-file GPT partition and ext4 creation with dynamic loop identity. No MBR, swap or other filesystem creation. |
| 104.2 | Partial | [Linux Storage](vm-preview/storage-unit.md). Bounded ext4 offline check, copy-only controlled link-count repair, independent contents/metadata/access verification and reserve monitoring. No arbitrary corruption, XFS/Btrfs or exhaustion exercises. |
| 104.3 | Partial | [Linux Storage](vm-preview/storage-unit.md). Explicit ext4 mount/unmount, ro/access diagnosis, unique UUID handling and separate private-fstab validation/explicit mount. No live fstab/boot mounting, removable user mounts or systemd mount units. |
| 104.4 | Removed / not applicable | —. Removed in the current official objectives; not counted as a missing active skill. |
| 104.5 | Partial | [Files & Permissions](lpic-unit-1.md), [Users & Access](vm-preview/users-unit.md), [Backup & Recovery](vm-preview/backup-unit.md). Implemented file/directory permissions, actual identities, owner/group, setgid and umask; remaining special-bit workflows and broader cases missing. No ACL claim. [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md). Actual sticky write-versus-unlink restrictions and owner exceptions; read-only privileged-bit audit. No executable setuid helper, ACLs or comprehensive special-file handling. |
| 104.6 | Partial | Previously no dedicated links exercise; the new bounded practice is described below. [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md). Real hard-link device/inode/count/shared changes/unlink and relative/dangling symlink repair; independent copy and dereference distinction. Cross-filesystem/directory-link breadth remains. |
| 104.7 | Partial | [Organize & Find](lpic-unit-2.md). Implemented representative home/etc/var path reasoning and bounded locating; complete hierarchy and locating utilities missing. [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md). Bounded real find and FHS interpretation in a model tree. No actual relocation of system configuration, locate/updatedb or full FHS breadth. |
| 105.1 | Partial | [Bash & Safe Changes](vm-preview/bash-unit.md). Implemented temporary environment/functions; persistent startup-file customization and full scope missing. [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md). Isolated login, interactive non-login and clean child startup, actual flags/HOME/marker evidence. No persistent account skeleton or owner startup changes. |
| 105.2 | Partial | [Bash & Safe Changes](vm-preview/bash-unit.md), [Scheduling](vm-preview/scheduling-unit.md). Implemented short scripts, arguments, conditions, bounded loops, statuses, environment and repeatable jobs; broader workflows missing. [Text & Archive Tools](vm-preview/text-archive-unit.md). Status-aware pipeline retry preserving failed output; reinforcement, not general robust-shell coverage. |
| 106.1 | Missing | —. No dedicated demonstrated X11 exercise. |
| 106.2 | Missing | —. No dedicated demonstrated desktops exercise. |
| 106.3 | Missing | —. No dedicated demonstrated accessibility exercise. |
| 107.1 | Partial | [Users & Access](vm-preview/users-unit.md). Implemented disposable accounts, homes/shells, primary/supplementary groups, expiry/locking distinctions; complete account policy and credential administration omitted. [Accounts, Scheduling, Logging & Recovery](vm-preview/operations-unit.md). Fabricated alternate-file grpck consistency and separate-copy repair; installed identity and aging inspection remain read-only. |
| 107.2 | Partial | [Scheduling](vm-preview/scheduling-unit.md). Implemented real cron, system/user timers, identities, catch-up/overlap and cleanup; at, access policies, mail/DST and complete scheduling coverage omitted. [Accounts, Scheduling, Logging & Recovery](vm-preview/operations-unit.md). Read-only allow/deny interpretation and -u privilege distinction; exact initially absent table ownership, actual results and loaded oneshot timeout. No allow/deny administration; at remains absent. |
| 107.3 | Missing | —. No dedicated demonstrated locales exercise. |
| 108.1 | Reinforcement only | [Scheduling](vm-preview/scheduling-unit.md). Read-only clock/timezone observations; no time synchronization/configuration practice. |
| 108.2 | Partial | [Services & Recovery](vm-preview/admin-unit.md). Implemented journal/rsyslog correlation, local rules and rotation; remote logging and full facility/configuration workflows missing. [Accounts, Scheduling, Logging & Recovery](vm-preview/operations-unit.md). Real saved cursor/boot continuation, journal field logic/severity, and private rename/create rotation with writer descriptor evidence. |
| 108.3 | Missing | —. No dedicated demonstrated mail basics exercise. |
| 108.4 | Missing | —. No dedicated demonstrated printing exercise. |
| 109.1 | Preparation only | [Original networking](native-acceptance.md). Original networking simulations practice IPv4 subnets/routes/DNS/TCP, not complete protocol coverage or real Linux configuration. |
| 109.2 | Missing | —. No dedicated demonstrated persistent networking exercise. |
| 109.3 | Preparation only | [Original networking](native-acceptance.md). Bounded original network diagnostics; no real interface/routing troubleshooting. |
| 109.4 | Preparation only | [Original networking](native-acceptance.md). Simulated gateway/DNS repair; no real resolver configuration. |
| 110.1 | Partial | [Users & Access](vm-preview/users-unit.md). Least privilege/locked disposable identities; no security audit/sudo-policy administration claim. [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md). Read-only /usr/bin special-bit audit and careful interpretation. No comprehensive host security/port/login-history policy practice. |
| 110.2 | Reinforcement only | [Users & Access](vm-preview/users-unit.md). Authentication/expiry/shell distinctions; no host security hardening exercise. |
| 110.3 | Missing | —. No dedicated demonstrated encryption exercise. |

## LPIC-2 — every published objective

| Objective | Status | Existing unit/evidence and essential gaps |
|---|---|---|
| 200.1 | Partial | [Resource Evidence](vm-preview/resource-unit.md), [Processes & Jobs](vm-preview/processes-unit.md). Implemented actual CPU/memory/file-I/O observations plus supplied space/inode fault interpretation; [Simulator snapshots](lpic-2-resource-simulator.md) reinforce interpretation only; advanced/network throughput and missing monitoring tools omitted. |
| 200.2 | Partial | [Resource Evidence](vm-preview/resource-unit.md). Implemented synthetic trends, independently checked forecasts and insufficient-evidence decisions; [Simulator handover](lpic-2-resource-simulator.md) checks factual trend records, not reasoning or forecasts; production monitoring deployment missing. |
| 201.1 | Missing | —. No dedicated demonstrated kernel components exercise. |
| 201.2 | Missing | —. No dedicated demonstrated kernel builds exercise. |
| 201.3 | Partial | [System Discovery & Packages](vm-preview/discovery-unit.md). Running kernel, loaded/built-in module and parameter queries. No module load/unload, sysctl mutation, udev administration or boot/runtime repair. |
| 202.1 | Partial | [Services & Recovery](vm-preview/admin-unit.md), [Scheduling](vm-preview/scheduling-unit.md). Implemented systemd service enablement/overrides and boot evidence; targets, SysV/LSB and broader startup missing. |
| 202.2 | Preparation only | [Services & Recovery](vm-preview/admin-unit.md). Service/file rollback is not bootloader, rescue/emergency or whole-system recovery. |
| 202.3 | Missing | —. No dedicated demonstrated other bootloaders exercise. |
| 203.1 | Partial | [Linux Storage](vm-preview/storage-unit.md). Ext4 mount/unmount, private-fstab validation and explicit mount, UUID ambiguity refusal and actual access verification. Swap and systemd mount units omitted. |
| 203.2 | Partial | [Linux Storage](vm-preview/storage-unit.md). Ext4 creation/superblock inspection, offline check and controlled repair copy with retained original and content/metadata/access expectations. No SMART, XFS, Btrfs or ZFS administration. |
| 203.3 | Missing | —. No dedicated demonstrated filesystem options exercise. |
| 204.1 | Missing | —. No dedicated demonstrated RAID exercise. |
| 204.2 | Missing | —. No dedicated demonstrated storage access exercise. |
| 204.3 | Missing | —. No dedicated demonstrated LVM exercise. |
| 205.1 | Missing | —. No dedicated demonstrated network configuration exercise. |
| 205.2 | Missing | —. No dedicated demonstrated advanced networking exercise. |
| 205.3 | Reinforcement only | [Original networking](native-acceptance.md) exercises bounded simulated repairs; [Network evidence simulator](lpic-2-offline-evidence.md) reinforces interface/route/name evidence and cautious handover. Neither establishes advanced real Linux troubleshooting or live network correction. |
| 206.1 | Reinforcement only | [Backup & Recovery](vm-preview/backup-unit.md). Archive skills alone do not demonstrate configure/make/install or source-build management. |
| 206.2 | Partial | [Backup & Recovery](vm-preview/backup-unit.md). Implemented manual scoped archives, independent references, damage/completeness/version checks, separate restore and actual-user access; system directory selection, media/tape, rsync and backup suites omitted. |
| 206.3 | Missing | —. No dedicated demonstrated user notices exercise. |
| 207.1 | Reinforcement only | [DNS evidence simulator](lpic-2-offline-evidence.md): response roles/status/cache interpretation only; no BIND installation/configuration/reload. |
| 207.2 | Reinforcement only | [DNS evidence simulator](lpic-2-offline-evidence.md): supplied records, validator finding, delegation and consistency interpretation; no live zone maintenance. |
| 207.3 | Missing | —. No dedicated demonstrated DNS security exercise. |
| 208.1 | Reinforcement only | [Web evidence simulator](lpic-2-offline-evidence.md): listener/request, logs and Apache Host selection interpretation; no server configuration or operational assessment. |
| 208.2 | Reinforcement only | [Web evidence simulator](lpic-2-offline-evidence.md): supplied SAN/date/hostname-check interpretation; no certificate/key generation, installation or live verification. |
| 208.3 | Missing | —. No dedicated demonstrated Squid exercise. |
| 208.4 | Reinforcement only | [Web evidence simulator](lpic-2-offline-evidence.md): nginx upstream/config/log interpretation; no proxy deployment or repair. |
| 209.1 | Missing | —. No dedicated demonstrated Samba exercise. |
| 209.2 | Missing | —. No dedicated demonstrated NFS exercise. |
| 210.1 | Missing | —. No dedicated demonstrated DHCP exercise. |
| 210.2 | Preparation only | [Users & Access](vm-preview/users-unit.md). Observed expiry/password-lock/shell distinctions are not PAM module/configuration practice. |
| 210.3 | Missing | —. No dedicated demonstrated LDAP client exercise. |
| 210.4 | Missing | —. No dedicated demonstrated LDAP server exercise. |
| 211.1 | Missing | —. No dedicated demonstrated mail servers exercise. |
| 211.2 | Missing | —. No dedicated demonstrated mail delivery exercise. |
| 211.3 | Missing | —. No dedicated demonstrated mailboxes exercise. |
| 212.1 | Preparation only | [Original networking](native-acceptance.md). Original simulated ordered firewall rules are not real router/NAT/firewall administration. |
| 212.2 | Missing | —. No dedicated demonstrated FTP exercise. |
| 212.3 | Missing | —. No dedicated demonstrated SSH exercise. |
| 212.4 | Reinforcement only | [Users & Access](vm-preview/users-unit.md), [Services & Recovery](vm-preview/admin-unit.md). Least privilege and scoped service access; no network/system security-tool workflow. |
| 212.5 | Missing | —. No dedicated demonstrated VPN exercise. |

## Proposed coherent batches, in useful order (not implemented here)

| Batch / proposed lessons | Outcomes and mapping | Existing capability vs approval needed |
|---|---|---|
| System discovery/package fundamentals — implemented, 8 | Virtual hardware/kernel/current-boot observations, trusted library lookup, installed/archive ownership and integrity, and actual scoped offline fixture package transactions (partial 101.1/101.2/102.3/102.4/201.3). No new locale/time/FHS coverage. | Implemented using the independently prepared package-administrator image and two trusted offline fixture packages. Locale/time/FHS breadth, repository administration and RPM remain future work requiring any absent packages/images to be approved. |
| Advanced storage and separate boot recovery, future | Disposable partition/fs/swap, mount/fstab faults, inode/space repair, LVM/RAID snapshots and rescue/bootloader recovery (104.1–3, 201–204). Verify after restart with a preserved good disk. | Guest-only administration already exists, but additional guest disks/boot media/controller block graph or packages require explicit architecture approval. Never raw host devices. No automatic approval inferred from existing sudo. |
| Local operational completeness, 8 | Remaining priority/special-bit/link/shell/editor skills, user notices, at and scheduler policy, richer logging/backup plans (103/104/105/107/108, 206). | Content can use verified current tools; absent at, ACL, rsync or multiplexer tools require approved offline packages/image revision, exact pins and compatibility. No networking required. Avoid padding with chmod variations. |
| Isolated networking and security, 8–10 | IPv4/IPv6 addressing, resolver/client routing, diagnosis, firewall/NAT, SSH and TLS identity (109/110, 205, 212). Verify from another guest, not mode bits or configuration alone. | Separate approval for isolated guest-only networking and often two guests, NIC/launch-policy changes, packages and disposable test credentials. Never host LAN/Internet exposure or shared personal folders. |
| DNS/DHCP and secure web services, 10–12 | Zones/reverse/delegation/cache/security, lease diagnosis, Apache/Nginx/HTTPS, bounded proxy access (207/208/210.1). Positive and negative client tests with narrow cleanup. | Approved offline server/client images, packages, trust fixtures and isolated multi-guest network required; certificates/credentials require explicit scope. |
| Shared files and identity, 8–10 | NFS/Samba ownership/access/client behavior, PAM and LDAP diagnosis (209/210.2–4). Verify actual identities, mounts and denial. | Separate images/packages, isolated clients/network and narrowly approved guest authentication fixtures; no real accounts or directory services. |
| Mail, transfer and service-security recovery, 8–10 | Local mail queues/delivery/mailbox access, FTP policy, VPN/firewall recovery and auditing (108.3, 211/212). | Additional packages and isolated multi-guest network; test credentials/keys and guest privilege scopes explicitly approved, no public mail/FTP/VPN services. |
| Source builds and platform breadth, 8 | Trusted source configure/make/install/uninstall, kernel/module provenance, RPM packaging, graphics/printing/accessibility (102.5/106/108.4/201/206.1). | Approved offline inputs/build tooling and separate distro/GUI images; kernel/boot experiments need recoverable images. Accessibility requires actual assistive-technology/owner evidence, not metadata tests. |

Current registry capacity is full at ten units/86 lessons; retained lesson/default maps also have a86-entry bound. Image/key/release and per-image compatibility lists remain64; parser byte/depth/node bounds are unchanged. A further unit or retained revision requires an explicitly approved bounded capacity review, not removal of limits.

Each future batch needs bounded registry capacity, pinned exact image/lesson revisions, failure and rollback fixtures, both modes, native lifecycle and installed-wheel tests. Preserve current image versions/session access; neither task authorization nor full guest root authorizes new host/security capabilities.

## Practical release target

Recommend a clearly labelled **Linux operations foundations preview**, covering the existing simulated file/text practice and real process/resource/service/access/scheduling/recovery units, with explicit partial LPIC mapping. Meaningful LPIC-2 preparation now includes resource evidence and manual recovery; it is not full LPIC-2 preparation. If the release is advertised as comprehensive certification preparation, **all missing active objective areas above become essential**, not optional.

For a usable foundations release, essential gates are: accepted unchanged lesson pins; complete repeatable installation and all eight new recovery outcomes; lifecycle/failure and backup-exclusion disclosure; remaining native keyboard/accessibility checks; clean public image provenance, authenticated release admission, source/notices and license compliance (unfinished Qt review and ICU signing-key warning); independent fresh-user installation; and honest curriculum gaps. Production trust stays empty until separately approved release preparation. No publication is authorized.

For a broader administrator curriculum, system/package discovery now supplies prerequisites; prioritize storage/boot recovery before network service troubleshooting. Networking, multi-VM orchestration and new image packages are substantive approvals, not routine content edits. Later enhancements: UI polish/shorter explanations, additional reinforcement, monitoring dashboards, more tooling and cross-domain expansion. Do not confuse interface polish with missing assessed skills.

[Linux Storage](vm-preview/storage-unit.md) now supplies eight bounded regular-file GPT/ext4/mount/recovery exercises using the unchanged administrator image. Remaining storage scope includes swap, other filesystems, LVM/RAID and separate boot recovery. No extra controller disk or live-fstab change is implied. Objective mapping checked2026-10-07; no full-objective claims.
