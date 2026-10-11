# LPIC-1 / LPIC-2 comprehensive evidence audit

Verified **2026-10-11**, clean baseline `67337af47561d6bccbb49cbba708bd1e1a4bb59e`. Original analysis checkpoint; the approved first-family implementation update is recorded below.

Sources: [active LPIC-1 objectives](https://www.lpi.org/our-certifications/exam-101-102-objectives/), [LPIC-1 overview](https://www.lpi.org/our-certifications/lpic-1-overview/), [active LPIC-2 objectives](https://www.lpi.org/our-certifications/exam-201-202-objectives/), [LPIC-2 overview](https://www.lpi.org/our-certifications/lpic-2-overview/). LPIC-1 is 5.0 (101-500/102-500); LPIC-2 is 4.5.0 (201-450/202-450). Access dates, source-copy hashes, every KKA mapping and 127 concrete lesson records are in [machine-readable audit](lpic-comprehensive-audit.json).

**Transition:** [LPI annual review 2025](https://www.lpi.org/wp-content/uploads/2026/03/2025_LPI-AnnualReview.pdf) plans LPIC-2 changes for 2026. The [published 5.0.0 objectives](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V5.0) remain explicitly draft. No confirmed launch/retirement date was found. Do not merge draft IDs into the active inventory; recheck before a large curriculum build.

## Reading this matrix

**G** = explanation only; **S** = virtual commands or supplied offline snapshots; **V** = accepted real disposable-guest practice; **A** = bounded automated subskill/report checks, with positive/negative fixtures. **R** = reasoning self-review, not automatically graded. A V row is not an assessment agent: the app records self-reviewed completion, unscored. S+A on DNS/web/network output means checking extracted facts and final report display, never verified causal reasoning or live service repair.

**Partial** includes bounded substantive exposure. Adjacent preparation alone is counted **Missing**, with its related evidence retained. **Missing** means no substantive mapped exercise/explanation; merely encountering a VM or seeing an objective tag earns nothing. **Covered** would require the full substantive breadth, independent application and adequate success/failure evidence. No objective is claimed covered. Each row below corresponds to one official KKA in order; supplementary description/tool breadth is retained explicitly. Original paraphrases are used, not exam questions.

There are 83 active objectives (23/19/20/21), not 84. Historical 104.4 is a removed tombstone. All four exams have official weight 60. No weighted coverage percentage is calculated: touching one subskill cannot earn an entire objective weight. Counts below overlap across evidence types and are not mastery percentages.

| Exam / identifier / version | Covered | Partial | Missing | Any S | Any V | Any A |
|---|---:|---:|---:|---:|---:|---:|
| 101 / 101-500 / 5.0 | 0 | 19 | 4 | 6 | 19 | 6 |
| 102 / 102-500 / 5.0 | 0 | 10 | 9 | 3 | 6 | 3 |
| 201 / 201-450 / 4.5.0 | 0 | 9 | 11 | 4 | 7 | 4 |
| 202 / 202-450 / 4.5.0 | 0 | 6 | 15 | 5 | 0 | 5 |

Any A means **some checked subskill only**; fully assessed objectives: 0 in every exam. Guidance-only context is explicit in the rows, not equivalent to hands-on practice.

## Current inventory and evidence quality

Eight simulator collections have 42 appearances representing 38 unique Linux packs plus 3 original networking labs: 41 distinct simulator activities. Ten real-VM units have 86 lessons. Sharing a pack across collections does not add another skill or progress record. Collection limits are full (8 simulator collections; 10 VM units/86 lessons, 16 per unit); capacity/default/retained-map changes need separate authorization.

Positive/negative simulator evidence: permissions test wrong/broad modes and stale verification; navigation checks activity and final location; file-management/text cases check wrong files/content/order, errors and final state; snapshot cases reject missing/wrong reports and require post-write display. Exact record spelling/order/LF is part of current report grading. That is narrower than semantic reasoning. HELP models remain readable in Challenge; hiding steps/hints is not proof of independent mastery. Resource snapshots award 10 points for an engine-enforced immutable-source invariant: this is preservation, not another demonstrated learner skill.

VM acceptance reports retain both-mode runs, actual identities, expected outputs/status/files, deliberate failures and cleanup. They validate feasibility and preservation on the pinned images; they do not assess each learner automatically. Long manually typed safety guards and absent clipboard sharing are real workload barriers. Learners need prerequisites and independent transfer cases, not more copied transcripts.

## Every active objective and substantive subtopic

### 101.1 — Determine and configure hardware settings (exam 101, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Firmware peripheral controls | **Missing**: no demonstrated dedicated subskill. |
| 2 | Storage device categories | **Missing**: no demonstrated dedicated subskill. |
| 3 | Device resource allocation | V+R: [real-linux-discovery-identity](../learning_lab/vm_preview/real-linux-discovery-identity.json), [real-linux-discovery-kernel](../learning_lab/vm_preview/real-linux-discovery-kernel.json). Virtual CPU/PCI resources and read-only /proc/sysfs observations; no physical control, USB operations or udev/D-Bus administration. |
| 4 | Hardware enumeration | V+R: [real-linux-discovery-identity](../learning_lab/vm_preview/real-linux-discovery-identity.json), [real-linux-discovery-kernel](../learning_lab/vm_preview/real-linux-discovery-kernel.json). Virtual CPU/PCI resources and read-only /proc/sysfs observations; no physical control, USB operations or udev/D-Bus administration. |
| 5 | USB device operations | **Missing**: no demonstrated dedicated subskill. |
| 6 | sysfs/udev/D-Bus roles | V+R: [real-linux-discovery-identity](../learning_lab/vm_preview/real-linux-discovery-identity.json), [real-linux-discovery-kernel](../learning_lab/vm_preview/real-linux-discovery-kernel.json). Virtual CPU/PCI resources and read-only /proc/sysfs observations; no physical control, USB operations or udev/D-Bus administration. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/sys/`, `/proc/`, `/dev/`, `modprobe`, `lsmod`, `lspci`, `lsusb`.

Explicit bounded-practice terms: `/sys/`, `/proc/`, `lsmod`, `lspci`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 101.2 — Boot the system (exam 101, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Loader input and boot-time kernel arguments | **Missing**: no demonstrated dedicated subskill. |
| 2 | Firmware-to-userspace sequence | G+R: [real-linux-discovery-boot](../learning_lab/vm_preview/real-linux-discovery-boot.json), [real-linux-admin-boot](../learning_lab/vm_preview/real-linux-admin-boot.json). Boot sequence/systemd context only; no SysV implementation or recovery. |
| 3 | SysV/systemd startup concepts | G+R: [real-linux-discovery-boot](../learning_lab/vm_preview/real-linux-discovery-boot.json), [real-linux-admin-boot](../learning_lab/vm_preview/real-linux-admin-boot.json). Boot sequence/systemd context only; no SysV implementation or recovery. |
| 4 | Upstart awareness | **Missing**: no demonstrated dedicated subskill. |
| 5 | Boot-log investigation | V+R: [real-linux-discovery-boot](../learning_lab/vm_preview/real-linux-discovery-boot.json), [real-linux-admin-boot](../learning_lab/vm_preview/real-linux-admin-boot.json). Current boot journal/kernel observations. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `dmesg`, `journalctl`, `BIOS`, `UEFI`, `bootloader`, `kernel`, `initramfs`, `init`, `SysVinit`, `systemd`.

Explicit bounded-practice terms: `dmesg`, `journalctl`, `systemd`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 101.3 — Change runlevels / boot targets and shutdown or reboot system (exam 101, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Default runlevel/target selection | **Missing**: no demonstrated dedicated subskill. |
| 2 | Changing targets including single-user operation | **Missing**: no demonstrated dedicated subskill. |
| 3 | Orderly command-line shutdown/reboot | V+R: [real-linux-admin-lifecycle](../learning_lab/vm_preview/real-linux-admin-lifecycle.json), [real-linux-admin-boot](../learning_lab/vm_preview/real-linux-admin-boot.json). Clean guest reboot/shutdown, not target transitions. |
| 4 | Advance user notification | **Missing**: no demonstrated dedicated subskill. |
| 5 | Orderly process termination | V+R: [real-linux-targeted-signals](../learning_lab/vm_preview/real-linux-targeted-signals.json). Owned practice tasks only; no shutdown coordination exercise. |
| 6 | ACPI daemon role | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/inittab`, `shutdown`, `init`, `/etc/init.d/`, `telinit`, `systemd`, `systemctl`, `/etc/systemd/`, `/usr/lib/systemd/`, `wall`.

Explicit bounded-practice terms: `systemctl`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 102.1 — Design hard disk layout (exam 101, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Filesystem/swap separation | **Missing**: no demonstrated dedicated subskill. |
| 2 | Workload-specific disk layout | **Missing**: no demonstrated dedicated subskill. |
| 3 | Architecture-dependent boot partition needs | **Missing**: no demonstrated dedicated subskill. |
| 4 | LVM fundamentals | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/ (root) filesystem`, `/var filesystem`, `/home filesystem`, `/boot filesystem`, `EFI System Partition (ESP)`, `swap space`, `mount points`, `partitions`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 102.2 — Install a boot manager (exam 101, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Alternate and backup boot paths | **Missing**: no demonstrated dedicated subskill. |
| 2 | Legacy GRUB deployment/configuration | **Missing**: no demonstrated dedicated subskill. |
| 3 | GRUB2 configuration | **Missing**: no demonstrated dedicated subskill. |
| 4 | Interactive loader operation | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `menu.lst, grub.cfg and grub.conf`, `grub-install`, `grub-mkconfig`, `MBR`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 102.3 — Manage shared libraries (exam 101, weight 1; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Executable/library dependency identification | V+R: [real-linux-discovery-libraries](../learning_lab/vm_preview/real-linux-discovery-libraries.json). Known trusted executable, libc/loader cache and package owner; no cache/library mutation. |
| 2 | Library search locations | V+R: [real-linux-discovery-libraries](../learning_lab/vm_preview/real-linux-discovery-libraries.json). Known trusted executable, libc/loader cache and package owner; no cache/library mutation. |
| 3 | Loader configuration and loading | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `ldd`, `ldconfig`, `/etc/ld.so.conf`, `LD_LIBRARY_PATH`.

Explicit bounded-practice terms: `ldd`, `ldconfig`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 102.4 — Use Debian package management (exam 101, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Debian install/upgrade/removal | V+R: [real-linux-discovery-ownership](../learning_lab/vm_preview/real-linux-discovery-ownership.json), [real-linux-discovery-integrity](../learning_lab/vm_preview/real-linux-discovery-integrity.json), [real-linux-discovery-lifecycle](../learning_lab/vm_preview/real-linux-discovery-lifecycle.json), [real-linux-discovery-repair](../learning_lab/vm_preview/real-linux-discovery-repair.json). Two trusted offline package identities; actual ownership/metadata/dependency and content repair, not repository administration or arbitrary packages. |
| 2 | Installed and uninstalled file-provider lookup | V+R: [real-linux-discovery-ownership](../learning_lab/vm_preview/real-linux-discovery-ownership.json), [real-linux-discovery-integrity](../learning_lab/vm_preview/real-linux-discovery-integrity.json), [real-linux-discovery-lifecycle](../learning_lab/vm_preview/real-linux-discovery-lifecycle.json), [real-linux-discovery-repair](../learning_lab/vm_preview/real-linux-discovery-repair.json). Two trusted offline package identities; actual ownership/metadata/dependency and content repair, not repository administration or arbitrary packages. |
| 3 | Version/content/dependency/integrity/status queries | V+R: [real-linux-discovery-ownership](../learning_lab/vm_preview/real-linux-discovery-ownership.json), [real-linux-discovery-integrity](../learning_lab/vm_preview/real-linux-discovery-integrity.json), [real-linux-discovery-lifecycle](../learning_lab/vm_preview/real-linux-discovery-lifecycle.json), [real-linux-discovery-repair](../learning_lab/vm_preview/real-linux-discovery-repair.json). Two trusted offline package identities; actual ownership/metadata/dependency and content repair, not repository administration or arbitrary packages. |
| 4 | APT role | V+R: [real-linux-discovery-ownership](../learning_lab/vm_preview/real-linux-discovery-ownership.json), [real-linux-discovery-integrity](../learning_lab/vm_preview/real-linux-discovery-integrity.json), [real-linux-discovery-lifecycle](../learning_lab/vm_preview/real-linux-discovery-lifecycle.json), [real-linux-discovery-repair](../learning_lab/vm_preview/real-linux-discovery-repair.json). Two trusted offline package identities; actual ownership/metadata/dependency and content repair, not repository administration or arbitrary packages. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/apt/sources.list`, `dpkg`, `dpkg-reconfigure`, `apt-get`, `apt-cache`.

Explicit bounded-practice terms: `dpkg`, `apt-get`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 102.5 — Use RPM and YUM package management (exam 101, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | RPM/YUM/Zypper lifecycle | **Missing**: no demonstrated dedicated subskill. |
| 2 | RPM metadata/integrity/signature queries | **Missing**: no demonstrated dedicated subskill. |
| 3 | RPM file-provider lookup | **Missing**: no demonstrated dedicated subskill. |
| 4 | DNF role | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `rpm`, `rpm2cpio`, `/etc/yum.conf`, `/etc/yum.repos.d/`, `yum`, `zypper`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 102.6 — Linux as a virtualization guest (exam 101, weight 1; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | VM/container concepts | **Missing**: no demonstrated dedicated subskill. |
| 2 | Cloud instance/storage/network model | **Missing**: no demonstrated dedicated subskill. |
| 3 | Clone-specific identity changes | **Missing**: no demonstrated dedicated subskill. |
| 4 | Deployment from images | **Missing**: no demonstrated dedicated subskill. |
| 5 | Guest integration extensions | **Missing**: no demonstrated dedicated subskill. |
| 6 | cloud-init awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Using the app VM does not teach image cloning, cloud-init, containers, guest integration or identity regeneration.

Official non-exhaustive tools/files/terms: `Virtual machine`, `Linux container`, `Application container`, `Guest drivers`, `SSH host keys`, `D-Bus machine id`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 103.1 — Work on the command line (exam 101, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Individual commands and command sequences | V+R: [real-linux-bash-environment](../learning_lab/vm_preview/real-linux-bash-environment.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json), [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json). Partial subset; see remaining breadth.<br>S+A: [linux-file-navigation](../learning_lab/collections/packs/linux-file-navigation.lab.json). Recorded pwd/list/entry/read evidence and final directory; no real shell semantics. |
| 2 | Local/exported shell variables | V+R: [real-linux-bash-environment](../learning_lab/vm_preview/real-linux-bash-environment.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json), [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json). Partial subset; see remaining breadth. |
| 3 | History retrieval/editing | V+R: [real-linux-local-history](../learning_lab/vm_preview/real-linux-local-history.json). Isolated history insertion/edit/write/reopen, not credential or parent-history changes. |
| 4 | PATH and explicit executable lookup | V+R: [real-linux-bash-environment](../learning_lab/vm_preview/real-linux-bash-environment.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json), [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json). Partial subset; see remaining breadth. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `bash`, `echo`, `env`, `export`, `pwd`, `set`, `unset`, `type`, `which`, `man`, `uname`, `history`, `.bash_history`, `Quoting`.

Explicit bounded-practice terms: `Quoting`, `bash`, `export`, `history`, `pwd`, `type`, `unset`. Tool presence or a title is not executed practice. Exact resources/guide/acceptance references remain in the JSON evidence inventory.


### 103.2 — Process text streams using filters (exam 101, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Text filtering across the named utility breadth | V+R: [real-linux-bash-transform](../learning_lab/vm_preview/real-linux-bash-transform.json), [real-linux-bash-streams](../learning_lab/vm_preview/real-linux-bash-streams.json), [real-linux-backup-checksum](../learning_lab/vm_preview/real-linux-backup-checksum.json). sed previews, streams and independent hashes; not every named filter. S+A+R: [linux-log-slices](../learning_lab/collections/packs/linux-log-slices.lab.json), [linux-text-counts](../learning_lab/collections/packs/linux-text-counts.lab.json), [linux-text-deduplicate](../learning_lab/collections/packs/linux-text-deduplicate.lab.json), [linux-text-events](../learning_lab/collections/packs/linux-text-events.lab.json), [linux-text-fields](../learning_lab/collections/packs/linux-text-fields.lab.json), [linux-text-pipeline](../learning_lab/collections/packs/linux-text-pipeline.lab.json), [linux-text-report](../learning_lab/collections/packs/linux-text-report.lab.json), [linux-text-handover](../learning_lab/collections/packs/linux-text-handover.lab.json). Bounded head/tail/grep-F/wc/sort/uniq/cut, final files and action evidence; no regex or general shell. |

**Breadth still to verify/teach:** Not all listed filters/options are taught; binary representations, paste/nl/tr/split and xz/bzip stream breadth remain.

Official non-exhaustive tools/files/terms: `bzcat`, `cat`, `cut`, `head`, `less`, `md5sum`, `nl`, `od`, `paste`, `sed`, `sha256sum`, `sha512sum`, `sort`, `split`, `tail`, `tr`, `uniq`, `wc`, `xzcat`, `zcat`.

Explicit bounded-practice terms: `cat`, `cut`, `head`, `sed`, `sha256sum`, `sort`, `tail`, `uniq`, `wc`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 103.3 — Perform basic file management (exam 101, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Individual file/directory lifecycle | V+R: [real-linux-bash-files](../learning_lab/vm_preview/real-linux-bash-files.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json). Small quoted names/globs and constrained find; no advanced size/time/action breadth.<br>S+A: [linux-prepare-workspace](../learning_lab/collections/packs/linux-prepare-workspace.lab.json), [linux-copy-reference](../learning_lab/collections/packs/linux-copy-reference.lab.json), [linux-organize-report](../learning_lab/collections/packs/linux-organize-report.lab.json), [linux-find-handover](../learning_lab/collections/packs/linux-find-handover.lab.json), [linux-deliver-workspace](../learning_lab/collections/packs/linux-deliver-workspace.lab.json). Declared regular-file lifecycle and limited find; no recursive management.<br>V+R: [real-linux-local-copies](../learning_lab/vm_preview/real-linux-local-copies.json). Independent regular copy and protected before-copy; no recursive management. |
| 2 | Recursive copying | **Missing**: no demonstrated dedicated subskill. |
| 3 | Recursive deletion | **Missing**: no demonstrated dedicated subskill. |
| 4 | Shell glob patterns | V+R: [real-linux-bash-files](../learning_lab/vm_preview/real-linux-bash-files.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json). Small quoted names/globs and constrained find; no advanced size/time/action breadth. |
| 5 | find criteria and actions | V+R: [real-linux-bash-files](../learning_lab/vm_preview/real-linux-bash-files.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json). Small quoted names/globs and constrained find; no advanced size/time/action breadth.<br>S+A: [linux-prepare-workspace](../learning_lab/collections/packs/linux-prepare-workspace.lab.json), [linux-copy-reference](../learning_lab/collections/packs/linux-copy-reference.lab.json), [linux-organize-report](../learning_lab/collections/packs/linux-organize-report.lab.json), [linux-find-handover](../learning_lab/collections/packs/linux-find-handover.lab.json), [linux-deliver-workspace](../learning_lab/collections/packs/linux-deliver-workspace.lab.json). Declared regular-file lifecycle and limited find; no recursive management.<br>V+R: [real-linux-local-search](../learning_lab/vm_preview/real-linux-local-search.json). Quoted name/type/byte-size and completed-day/minute find criteria; no destructive find actions. |
| 6 | Archive/cpio/dd workflows | V+R: [real-linux-backup-archive](../learning_lab/vm_preview/real-linux-backup-archive.json), [real-linux-backup-checksum](../learning_lab/vm_preview/real-linux-backup-checksum.json), [real-linux-backup-restore](../learning_lab/vm_preview/real-linux-backup-restore.json). tar/gzip only; no cpio or general dd file management. |

**Breadth still to verify/teach:** No recursive simulator operations or links. Live tar/gzip is scoped; no cpio, full dd transfer or alternate-compression workflow.

Official non-exhaustive tools/files/terms: `cp`, `find`, `mkdir`, `mv`, `ls`, `rm`, `rmdir`, `touch`, `tar`, `cpio`, `dd`, `file`, `gzip`, `gunzip`, `bzip2`, `bunzip2`, `xz`, `unxz`, `file globbing`.

Explicit bounded-practice terms: `cp`, `find`, `mkdir`, `mv`, `ls`, `rm`, `rmdir`, `touch`, `tar`, `gzip`, `file globbing`. Tool presence or a title is not executed practice. Exact resources/guide/acceptance references remain in the JSON evidence inventory.


### 103.4 — Use streams, pipes and redirects (exam 101, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | stdin/stdout/stderr redirection | V+R: [real-linux-bash-streams](../learning_lab/vm_preview/real-linux-bash-streams.json), [real-linux-bash-handover](../learning_lab/vm_preview/real-linux-bash-handover.json). Partial subset; see remaining breadth. S+A+R: [linux-text-report](../learning_lab/collections/packs/linux-text-report.lab.json), [linux-text-pipeline](../learning_lab/collections/packs/linux-text-pipeline.lab.json), [linux-text-handover](../learning_lab/collections/packs/linux-text-handover.lab.json). Only stdout pipes and final > / >>; no stdin/stderr redirection. |
| 2 | Pipeline composition | V+R: [real-linux-bash-streams](../learning_lab/vm_preview/real-linux-bash-streams.json), [real-linux-bash-handover](../learning_lab/vm_preview/real-linux-bash-handover.json). Partial subset; see remaining breadth. S+A+R: [linux-text-report](../learning_lab/collections/packs/linux-text-report.lab.json), [linux-text-pipeline](../learning_lab/collections/packs/linux-text-pipeline.lab.json), [linux-text-handover](../learning_lab/collections/packs/linux-text-handover.lab.json). Only stdout pipes and final > / >>; no stdin/stderr redirection. |
| 3 | Output-to-arguments composition | **Missing**: no demonstrated dedicated subskill. |
| 4 | tee output duplication | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `tee`, `xargs`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 103.5 — Create, monitor and kill processes (exam 101, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Foreground/background job control | V+R: [real-linux-foreground-jobs](../learning_lab/vm_preview/real-linux-foreground-jobs.json), [real-linux-background-job](../learning_lab/vm_preview/lesson.json), [real-linux-logout-persistence](../learning_lab/vm_preview/real-linux-logout-persistence.json), [real-linux-process-inspection](../learning_lab/vm_preview/real-linux-process-inspection.json), [real-linux-live-monitoring](../learning_lab/vm_preview/real-linux-live-monitoring.json), [real-linux-targeted-signals](../learning_lab/vm_preview/real-linux-targeted-signals.json), [real-linux-process-handover](../learning_lab/vm_preview/real-linux-process-handover.json). Bounded owned tasks; no screen/tmux; learner completion is not automatically verified. |
| 2 | Logout survival | V+R: [real-linux-foreground-jobs](../learning_lab/vm_preview/real-linux-foreground-jobs.json), [real-linux-background-job](../learning_lab/vm_preview/lesson.json), [real-linux-logout-persistence](../learning_lab/vm_preview/real-linux-logout-persistence.json), [real-linux-process-inspection](../learning_lab/vm_preview/real-linux-process-inspection.json), [real-linux-live-monitoring](../learning_lab/vm_preview/real-linux-live-monitoring.json), [real-linux-targeted-signals](../learning_lab/vm_preview/real-linux-targeted-signals.json), [real-linux-process-handover](../learning_lab/vm_preview/real-linux-process-handover.json). Bounded owned tasks; no screen/tmux; learner completion is not automatically verified. |
| 3 | Process monitoring | V+R: [real-linux-foreground-jobs](../learning_lab/vm_preview/real-linux-foreground-jobs.json), [real-linux-background-job](../learning_lab/vm_preview/lesson.json), [real-linux-logout-persistence](../learning_lab/vm_preview/real-linux-logout-persistence.json), [real-linux-process-inspection](../learning_lab/vm_preview/real-linux-process-inspection.json), [real-linux-live-monitoring](../learning_lab/vm_preview/real-linux-live-monitoring.json), [real-linux-targeted-signals](../learning_lab/vm_preview/real-linux-targeted-signals.json), [real-linux-process-handover](../learning_lab/vm_preview/real-linux-process-handover.json). Bounded owned tasks; no screen/tmux; learner completion is not automatically verified. |
| 4 | Process display selection/order | V+R: [real-linux-foreground-jobs](../learning_lab/vm_preview/real-linux-foreground-jobs.json), [real-linux-background-job](../learning_lab/vm_preview/lesson.json), [real-linux-logout-persistence](../learning_lab/vm_preview/real-linux-logout-persistence.json), [real-linux-process-inspection](../learning_lab/vm_preview/real-linux-process-inspection.json), [real-linux-live-monitoring](../learning_lab/vm_preview/real-linux-live-monitoring.json), [real-linux-targeted-signals](../learning_lab/vm_preview/real-linux-targeted-signals.json), [real-linux-process-handover](../learning_lab/vm_preview/real-linux-process-handover.json). Bounded owned tasks; no screen/tmux; learner completion is not automatically verified. |
| 5 | Targeted signals | V+R: [real-linux-foreground-jobs](../learning_lab/vm_preview/real-linux-foreground-jobs.json), [real-linux-background-job](../learning_lab/vm_preview/lesson.json), [real-linux-logout-persistence](../learning_lab/vm_preview/real-linux-logout-persistence.json), [real-linux-process-inspection](../learning_lab/vm_preview/real-linux-process-inspection.json), [real-linux-live-monitoring](../learning_lab/vm_preview/real-linux-live-monitoring.json), [real-linux-targeted-signals](../learning_lab/vm_preview/real-linux-targeted-signals.json), [real-linux-process-handover](../learning_lab/vm_preview/real-linux-process-handover.json). Bounded owned tasks; no screen/tmux; learner completion is not automatically verified. |

**Breadth still to verify/teach:** screen/tmux, pgrep/pkill/killall breadth is unpracticed; broad termination is not an appropriate shortcut.

Official non-exhaustive tools/files/terms: `&`, `bg`, `fg`, `jobs`, `kill`, `nohup`, `ps`, `top`, `free`, `uptime`, `pgrep`, `pkill`, `killall`, `watch`, `screen`, `tmux`.

Explicit bounded-practice terms: `&`, `bg`, `fg`, `jobs`, `kill`, `nohup`, `ps`, `top`, `free`, `uptime`, `watch`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 103.6 — Modify process execution priorities (exam 101, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Default niceness | V+R: [real-linux-process-priorities](../learning_lab/vm_preview/real-linux-process-priorities.json). Unprivileged positive niceness and denied increases with actual-value checks; privileged priority recovery omitted. |
| 2 | Increasing and decreasing new-job priority | V+R: [real-linux-process-priorities](../learning_lab/vm_preview/real-linux-process-priorities.json). Unprivileged positive niceness and denied increases with actual-value checks; privileged priority recovery omitted. |
| 3 | Changing an existing process priority | V+R: [real-linux-process-priorities](../learning_lab/vm_preview/real-linux-process-priorities.json). Unprivileged positive niceness and denied increases with actual-value checks; privileged priority recovery omitted.<br>V+R: [real-linux-local-priority](../learning_lab/vm_preview/real-linux-local-priority.json). Actual owned task niceness 5, denied reversal and scoped approved guest-root return to0; no CPU-share guarantee. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `nice`, `ps`, `renice`, `top`.

Explicit bounded-practice terms: `nice`, `ps`, `renice`. Tool presence or a title is not executed practice. Exact resources/guide/acceptance references remain in the JSON evidence inventory.


### 103.7 — Search text files using regular expressions (exam 101, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Multi-element patterns | V+R: [real-linux-bash-regex](../learning_lab/vm_preview/real-linux-bash-regex.json). BRE/ERE, bounded matches/nonmatches and invalid patterns; wider search composition omitted. |
| 2 | BRE versus ERE | V+R: [real-linux-bash-regex](../learning_lab/vm_preview/real-linux-bash-regex.json). BRE/ERE, bounded matches/nonmatches and invalid patterns; wider search composition omitted. |
| 3 | Metacharacters/classes/repetition/anchors | V+R: [real-linux-bash-regex](../learning_lab/vm_preview/real-linux-bash-regex.json). BRE/ERE, bounded matches/nonmatches and invalid patterns; wider search composition omitted. |
| 4 | Pattern-based file/content search | V+R: [real-linux-bash-regex](../learning_lab/vm_preview/real-linux-bash-regex.json). BRE/ERE, bounded matches/nonmatches and invalid patterns; wider search composition omitted. |
| 5 | Regex-based text editing | V+R: [real-linux-bash-transform](../learning_lab/vm_preview/real-linux-bash-transform.json). Anchored sed substitution preview, not arbitrary regex editing. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `grep`, `egrep`, `fgrep`, `sed`, `regex(7)`.

Explicit bounded-practice terms: `grep`, `sed`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 103.8 — Basic file editing (exam 101, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | vi movement | V+R: [real-linux-bash-vi](../learning_lab/vm_preview/real-linux-bash-vi.json), [real-linux-bash-rollback](../learning_lab/vm_preview/real-linux-bash-rollback.json). Vim Tiny vi exercises and preserved-file rollback; editor/swap/power-loss breadth omitted. |
| 2 | vi modes | V+R: [real-linux-bash-vi](../learning_lab/vm_preview/real-linux-bash-vi.json), [real-linux-bash-rollback](../learning_lab/vm_preview/real-linux-bash-rollback.json). Vim Tiny vi exercises and preserved-file rollback; editor/swap/power-loss breadth omitted. |
| 3 | vi insertion/change/deletion/copy/search | V+R: [real-linux-bash-vi](../learning_lab/vm_preview/real-linux-bash-vi.json), [real-linux-bash-rollback](../learning_lab/vm_preview/real-linux-bash-rollback.json). Vim Tiny vi exercises and preserved-file rollback; editor/swap/power-loss breadth omitted. |
| 4 | Alternative editor awareness | G+R: [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json). nano used for short scripts; no Emacs/comparative editor lesson. |
| 5 | Default editor configuration | V+R: [real-linux-local-editor](../learning_lab/vm_preview/real-linux-local-editor.json). Temporary VISUAL/EDITOR consumed by sensible-editor and actual Vim Tiny save. No global/persistent alternatives change. |

**Breadth still to verify/teach:** Temporary consuming-editor selection added; persistent/editor-platform configuration, Emacs and swap/power-loss breadth remain.

Official non-exhaustive tools/files/terms: `vi`, `/, ?`, `h,j,k,l`, `i, o, a`, `d, p, y, dd, yy`, `ZZ, :w!, :q!`, `EDITOR`.

Explicit bounded-practice terms: `vi`, `h,j,k,l`. Tool presence or a title is not executed practice. Exact resources/guide/acceptance references remain in the JSON evidence inventory.


### 104.1 — Create partitions and filesystems (exam 101, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | MBR and GPT tables | V+R: [real-linux-storage-partition](../learning_lab/vm_preview/real-linux-storage-partition.json), [real-linux-storage-filesystem](../learning_lab/vm_preview/real-linux-storage-filesystem.json). Regular-file GPT/ext4 only; no MBR/ext2/ext3/swap or real system disk. |
| 2 | ext-family creation | V+R: [real-linux-storage-partition](../learning_lab/vm_preview/real-linux-storage-partition.json), [real-linux-storage-filesystem](../learning_lab/vm_preview/real-linux-storage-filesystem.json). Regular-file GPT/ext4 only; no MBR/ext2/ext3/swap or real system disk. |
| 3 | XFS creation | **Missing**: no demonstrated dedicated subskill. |
| 4 | VFAT creation | **Missing**: no demonstrated dedicated subskill. |
| 5 | exFAT creation | **Missing**: no demonstrated dedicated subskill. |
| 6 | Btrfs multidevice/compression/subvolume awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `fdisk`, `gdisk`, `parted`, `mkfs`, `mkswap`.

Explicit bounded-practice terms: `mkfs`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 104.2 — Maintain the integrity of filesystems (exam 101, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Filesystem consistency checking | V+R: [real-linux-storage-identify](../learning_lab/vm_preview/real-linux-storage-identify.json), [real-linux-storage-repair](../learning_lab/vm_preview/real-linux-storage-repair.json), [real-linux-storage-incident](../learning_lab/vm_preview/real-linux-storage-incident.json), [real-linux-capacity-space-inodes](../learning_lab/vm_preview/real-linux-capacity-space-inodes.json). Bounded ext4 offline copy repair and reserve; supplied shortages, not exhaustion. |
| 2 | Free blocks and inode monitoring | V+R: [real-linux-storage-identify](../learning_lab/vm_preview/real-linux-storage-identify.json), [real-linux-storage-repair](../learning_lab/vm_preview/real-linux-storage-repair.json), [real-linux-storage-incident](../learning_lab/vm_preview/real-linux-storage-incident.json), [real-linux-capacity-space-inodes](../learning_lab/vm_preview/real-linux-capacity-space-inodes.json). Bounded ext4 offline copy repair and reserve; supplied shortages, not exhaustion. |
| 3 | Simple filesystem repair | V+R: [real-linux-storage-identify](../learning_lab/vm_preview/real-linux-storage-identify.json), [real-linux-storage-repair](../learning_lab/vm_preview/real-linux-storage-repair.json), [real-linux-storage-incident](../learning_lab/vm_preview/real-linux-storage-incident.json), [real-linux-capacity-space-inodes](../learning_lab/vm_preview/real-linux-capacity-space-inodes.json). Bounded ext4 offline copy repair and reserve; supplied shortages, not exhaustion. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `du`, `df`, `fsck`, `e2fsck`, `mke2fs`, `tune2fs`, `xfs_repair`, `xfs_fsr`, `xfs_db`.

Explicit bounded-practice terms: `du`, `df`, `fsck`, `e2fsck`, `mke2fs`, `tune2fs`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 104.3 — Control mounting and unmounting of filesystems (exam 101, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Explicit mount/unmount | V+R: [real-linux-storage-mount](../learning_lab/vm_preview/real-linux-storage-mount.json), [real-linux-storage-faults](../learning_lab/vm_preview/real-linux-storage-faults.json), [real-linux-storage-fstab](../learning_lab/vm_preview/real-linux-storage-fstab.json). Explicit mounting/private fstab and UUID uniqueness; no live boot fstab or removable-user mounts. |
| 2 | Boot-time mounting | **Missing**: no demonstrated dedicated subskill. |
| 3 | User-mountable removable media | **Missing**: no demonstrated dedicated subskill. |
| 4 | Label/UUID selection | V+R: [real-linux-storage-mount](../learning_lab/vm_preview/real-linux-storage-mount.json), [real-linux-storage-faults](../learning_lab/vm_preview/real-linux-storage-faults.json), [real-linux-storage-fstab](../learning_lab/vm_preview/real-linux-storage-fstab.json). Explicit mounting/private fstab and UUID uniqueness; no live boot fstab or removable-user mounts. |
| 5 | systemd mount awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/fstab`, `/media/`, `mount`, `umount`, `blkid`, `lsblk`.

Explicit bounded-practice terms: `mount`, `umount`, `blkid`, `lsblk`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 104.5 — Manage file permissions and ownership (exam 101, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | File/special-file/directory access | V+R: [real-linux-users-ownership](../learning_lab/vm_preview/real-linux-users-ownership.json), [real-linux-users-shared](../learning_lab/vm_preview/real-linux-users-shared.json), [real-linux-users-umask](../learning_lab/vm_preview/real-linux-users-umask.json), [real-linux-users-repair](../learning_lab/vm_preview/real-linux-users-repair.json), [real-linux-backup-access](../learning_lab/vm_preview/real-linux-backup-access.json). Actual disposable identities, group ownership/setgid directories and umask; special files/setuid/sticky breadth omitted.<br>S+A: [linux-file-permissions](../learning_lab/collections/packs/linux-file-permissions.lab.json), [linux-directory-permissions](../learning_lab/collections/packs/linux-directory-permissions.lab.json), [linux-private-note](../learning_lab/collections/packs/linux-private-note.lab.json), [linux-search-only-directory](../learning_lab/collections/packs/linux-search-only-directory.lab.json), [linux-archive-access](../learning_lab/collections/packs/linux-archive-access.lab.json). Ordinary owner bits, directory read/search and post-change evidence; no real multiuser/group mutation/special bits. |
| 2 | setuid/setgid/sticky semantics | V+R: [real-linux-users-ownership](../learning_lab/vm_preview/real-linux-users-ownership.json), [real-linux-users-shared](../learning_lab/vm_preview/real-linux-users-shared.json), [real-linux-users-umask](../learning_lab/vm_preview/real-linux-users-umask.json), [real-linux-users-repair](../learning_lab/vm_preview/real-linux-users-repair.json), [real-linux-backup-access](../learning_lab/vm_preview/real-linux-backup-access.json). Actual disposable identities, group ownership/setgid directories and umask; special files/setuid/sticky breadth omitted.<br>V+R: [real-linux-local-sticky](../learning_lab/vm_preview/real-linux-local-sticky.json), [real-linux-local-priority](../learning_lab/vm_preview/real-linux-local-priority.json). Actual two existing identities separate writable content from sticky unlink refusal and owner exceptions; privileged bits audited read-only, no setuid helper execution. |
| 3 | Creation masks | V+R: [real-linux-users-ownership](../learning_lab/vm_preview/real-linux-users-ownership.json), [real-linux-users-shared](../learning_lab/vm_preview/real-linux-users-shared.json), [real-linux-users-umask](../learning_lab/vm_preview/real-linux-users-umask.json), [real-linux-users-repair](../learning_lab/vm_preview/real-linux-users-repair.json), [real-linux-backup-access](../learning_lab/vm_preview/real-linux-backup-access.json). Actual disposable identities, group ownership/setgid directories and umask; special files/setuid/sticky breadth omitted. |
| 4 | Group-based access | V+R: [real-linux-users-ownership](../learning_lab/vm_preview/real-linux-users-ownership.json), [real-linux-users-shared](../learning_lab/vm_preview/real-linux-users-shared.json), [real-linux-users-umask](../learning_lab/vm_preview/real-linux-users-umask.json), [real-linux-users-repair](../learning_lab/vm_preview/real-linux-users-repair.json), [real-linux-backup-access](../learning_lab/vm_preview/real-linux-backup-access.json). Actual disposable identities, group ownership/setgid directories and umask; special files/setuid/sticky breadth omitted. |

**Breadth still to verify/teach:** setgid directories are practiced, not full setuid/sticky/security semantics or special-file access. ACLs are not claimed.

Official non-exhaustive tools/files/terms: `chmod`, `umask`, `chown`, `chgrp`.

Explicit bounded-practice terms: `chmod`, `umask`, `chown`, `chgrp`. Tool presence or a title is not executed practice. Exact resources/guide/acceptance references remain in the JSON evidence inventory.


### 104.6 — Create and change hard and symbolic links (exam 101, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Hard and symbolic link creation | V+R: [real-linux-local-hardlinks](../learning_lab/vm_preview/real-linux-local-hardlinks.json), [real-linux-local-symlinks](../learning_lab/vm_preview/real-linux-local-symlinks.json). Real regular hard links and relative/dangling symlink repair, originals/before-copies preserved. |
| 2 | Link identification | V+R: [real-linux-local-hardlinks](../learning_lab/vm_preview/real-linux-local-hardlinks.json), [real-linux-local-symlinks](../learning_lab/vm_preview/real-linux-local-symlinks.json). Device/inode/link count plus lstat-style identity and dereferenced reading. |
| 3 | Copy versus link semantics | V+R: [real-linux-local-copies](../learning_lab/vm_preview/real-linux-local-copies.json). Independent cp-p versus shared hard link, cp-P versus dereference; no ACL/xattr completeness. |
| 4 | Administration through links | V+R: [real-linux-local-handover](../learning_lab/vm_preview/real-linux-local-handover.json). Scoped independent link/copy handover repair and preserved source metadata; broader administrative use missing. |

**Breadth still to verify/teach:** Scoped regular-file links/copies and independent handover now practiced. Cross-filesystem limitations, broader administrative link use, directory semantics and full transfer remain partial.

Official non-exhaustive tools/files/terms: `ln`, `ls`.

Explicit bounded-practice terms: `ln`. Tool presence or a title is not executed practice. Exact resources/guide/acceptance references remain in the JSON evidence inventory.


### 104.7 — Find system files and place files in the correct location (exam 101, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | FHS placement rules | S+A: [linux-file-locations](../learning_lab/collections/packs/linux-file-locations.lab.json), [linux-find-handover](../learning_lab/collections/packs/linux-find-handover.lab.json). Representative locations/find and declared reports; not complete FHS or locating-tool breadth.<br>G+R: [real-linux-local-search](../learning_lab/vm_preview/real-linux-local-search.json). Model-tree placement explanation, not system relocation. |
| 2 | Locate files and commands | S+A: [linux-file-locations](../learning_lab/collections/packs/linux-file-locations.lab.json), [linux-find-handover](../learning_lab/collections/packs/linux-find-handover.lab.json). Representative locations/find and declared reports; not complete FHS or locating-tool breadth.<br>V+R: [real-linux-bash-files](../learning_lab/vm_preview/real-linux-bash-files.json), [real-linux-bash-environment](../learning_lab/vm_preview/real-linux-bash-environment.json). Bounded find/command lookup only.<br>V+R: [real-linux-local-search](../learning_lab/vm_preview/real-linux-local-search.json). Scoped real find only; locate/updatedb/whereis breadth missing. |
| 3 | Purpose of key hierarchy locations | S+A: [linux-file-locations](../learning_lab/collections/packs/linux-file-locations.lab.json), [linux-find-handover](../learning_lab/collections/packs/linux-find-handover.lab.json). Representative locations/find and declared reports; not complete FHS or locating-tool breadth.<br>G+R: [real-linux-local-search](../learning_lab/vm_preview/real-linux-local-search.json). Model etc,var/log,usr/local/share purpose; full hierarchy breadth missing. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `find`, `locate`, `updatedb`, `whereis`, `which`, `type`, `/etc/updatedb.conf`.

Explicit bounded-practice terms: `find`, `type`. Tool presence or a title is not executed practice. Exact resources/guide/acceptance references remain in the JSON evidence inventory.


### 105.1 — Customize and use the shell environment (exam 102, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Login/child-shell environment configuration | V+R: [real-linux-bash-environment](../learning_lab/vm_preview/real-linux-bash-environment.json). Temporary environment/search path; no login profile persistence or skeleton maintenance.<br>V+R: [real-linux-local-startup](../learning_lab/vm_preview/real-linux-local-startup.json). Isolated HOME login/non-login/child startup, flags and profile/rc selection; no real-account persistent settings. |
| 2 | Reusable Bash functions | V+R: [real-linux-bash-records](../learning_lab/vm_preview/real-linux-bash-records.json). Partial subset; see remaining breadth. |
| 3 | Account skeleton maintenance | **Missing**: no demonstrated dedicated subskill. |
| 4 | Safe command search paths | V+R: [real-linux-bash-environment](../learning_lab/vm_preview/real-linux-bash-environment.json). Temporary environment/search path; no login profile persistence or skeleton maintenance. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `.`, `source`, `/etc/bash.bashrc`, `/etc/profile`, `env`, `export`, `set`, `unset`, `~/.bash_profile`, `~/.bash_login`, `~/.profile`, `~/.bashrc`, `~/.bash_logout`, `function`, `alias`.

Explicit bounded-practice terms: `env`, `export`, `unset`, `function`. Tool presence or a title is not executed practice. Exact resources/guide/acceptance references remain in the JSON evidence inventory.


### 105.2 — Customize or write simple scripts (exam 102, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | sh loops/tests | V+R: [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json), [real-linux-bash-guards](../learning_lab/vm_preview/real-linux-bash-guards.json), [real-linux-bash-records](../learning_lab/vm_preview/real-linux-bash-records.json), [real-linux-bash-handover](../learning_lab/vm_preview/real-linux-bash-handover.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json), [real-linux-schedule-report](../learning_lab/vm_preview/real-linux-schedule-report.json). Small bounded Bash scripts; portability to sh, administrator mail and script suid semantics not fully taught. |
| 2 | Command substitution | V+R: [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json), [real-linux-bash-guards](../learning_lab/vm_preview/real-linux-bash-guards.json), [real-linux-bash-records](../learning_lab/vm_preview/real-linux-bash-records.json), [real-linux-bash-handover](../learning_lab/vm_preview/real-linux-bash-handover.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json), [real-linux-schedule-report](../learning_lab/vm_preview/real-linux-schedule-report.json). Small bounded Bash scripts; portability to sh, administrator mail and script suid semantics not fully taught. |
| 3 | Status-aware behavior | V+R: [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json), [real-linux-bash-guards](../learning_lab/vm_preview/real-linux-bash-guards.json), [real-linux-bash-records](../learning_lab/vm_preview/real-linux-bash-records.json), [real-linux-bash-handover](../learning_lab/vm_preview/real-linux-bash-handover.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json), [real-linux-schedule-report](../learning_lab/vm_preview/real-linux-schedule-report.json). Small bounded Bash scripts; portability to sh, administrator mail and script suid semantics not fully taught. |
| 4 | Command chaining | V+R: [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json), [real-linux-bash-guards](../learning_lab/vm_preview/real-linux-bash-guards.json), [real-linux-bash-records](../learning_lab/vm_preview/real-linux-bash-records.json), [real-linux-bash-handover](../learning_lab/vm_preview/real-linux-bash-handover.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json), [real-linux-schedule-report](../learning_lab/vm_preview/real-linux-schedule-report.json). Small bounded Bash scripts; portability to sh, administrator mail and script suid semantics not fully taught. |
| 5 | Conditional administrator mail | **Missing**: no demonstrated dedicated subskill. |
| 6 | Interpreter selection | V+R: [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json), [real-linux-bash-guards](../learning_lab/vm_preview/real-linux-bash-guards.json), [real-linux-bash-records](../learning_lab/vm_preview/real-linux-bash-records.json), [real-linux-bash-handover](../learning_lab/vm_preview/real-linux-bash-handover.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json), [real-linux-schedule-report](../learning_lab/vm_preview/real-linux-schedule-report.json). Small bounded Bash scripts; portability to sh, administrator mail and script suid semantics not fully taught. |
| 7 | Script placement/ownership/execution/suid implications | V+R: [real-linux-bash-script](../learning_lab/vm_preview/real-linux-bash-script.json), [real-linux-bash-guards](../learning_lab/vm_preview/real-linux-bash-guards.json), [real-linux-bash-records](../learning_lab/vm_preview/real-linux-bash-records.json), [real-linux-bash-handover](../learning_lab/vm_preview/real-linux-bash-handover.json), [real-linux-bash-quoting](../learning_lab/vm_preview/real-linux-bash-quoting.json), [real-linux-schedule-report](../learning_lab/vm_preview/real-linux-schedule-report.json). Small bounded Bash scripts; portability to sh, administrator mail and script suid semantics not fully taught. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `for`, `while`, `test`, `if`, `read`, `seq`, `exec`, `||`, `&&`.

Explicit bounded-practice terms: `for`, `while`, `test`, `if`, `read`, `||`, `&&`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 106.1 — Install and configure X11 (exam 102, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | X11 roles | **Missing**: no demonstrated dedicated subskill. |
| 2 | Xorg configuration | **Missing**: no demonstrated dedicated subskill. |
| 3 | Keyboard/configuration overrides | **Missing**: no demonstrated dedicated subskill. |
| 4 | Display/window manager roles | **Missing**: no demonstrated dedicated subskill. |
| 5 | X access and remote display | **Missing**: no demonstrated dedicated subskill. |
| 6 | Wayland awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/X11/xorg.conf`, `/etc/X11/xorg.conf.d/`, `~/.xsession-errors`, `xhost`, `xauth`, `DISPLAY`, `X`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 106.2 — Graphical Desktops (exam 102, weight 1; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Desktop environment choices | **Missing**: no demonstrated dedicated subskill. |
| 2 | Remote desktop protocols | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `KDE`, `Gnome`, `Xfce`, `X11`, `XDMCP`, `VNC`, `Spice`, `RDP`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 106.3 — Accessibility (exam 102, weight 1; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Visual accessibility settings | **Missing**: no demonstrated dedicated subskill. |
| 2 | Assistive technology | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `High Contrast/Large Print Desktop Themes.`, `Screen Reader.`, `Braille Display.`, `Screen Magnifier.`, `On-Screen Keyboard.`, `Sticky/Repeat keys.`, `Slow/Bounce/Toggle keys.`, `Mouse keys.`, `Gestures.`, `Voice recognition.`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 107.1 — Manage user and group accounts and related system files (exam 102, weight 5; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Account/group lifecycle | V+R: [real-linux-users-inspect](../learning_lab/vm_preview/real-linux-users-inspect.json), [real-linux-users-create](../learning_lab/vm_preview/real-linux-users-create.json), [real-linux-users-membership](../learning_lab/vm_preview/real-linux-users-membership.json), [real-linux-users-restrictions](../learning_lab/vm_preview/real-linux-users-restrictions.json), [real-linux-users-repair](../learning_lab/vm_preview/real-linux-users-repair.json). Disposable identities and locked/expiry/shell distinctions; no real credential creation/full policy administration. |
| 2 | Account/group databases | V+R: [real-linux-users-inspect](../learning_lab/vm_preview/real-linux-users-inspect.json), [real-linux-users-create](../learning_lab/vm_preview/real-linux-users-create.json), [real-linux-users-membership](../learning_lab/vm_preview/real-linux-users-membership.json), [real-linux-users-restrictions](../learning_lab/vm_preview/real-linux-users-restrictions.json), [real-linux-users-repair](../learning_lab/vm_preview/real-linux-users-repair.json). Disposable identities and locked/expiry/shell distinctions; no real credential creation/full policy administration. |
| 3 | Restricted/service identities | V+R: [real-linux-users-inspect](../learning_lab/vm_preview/real-linux-users-inspect.json), [real-linux-users-create](../learning_lab/vm_preview/real-linux-users-create.json), [real-linux-users-membership](../learning_lab/vm_preview/real-linux-users-membership.json), [real-linux-users-restrictions](../learning_lab/vm_preview/real-linux-users-restrictions.json), [real-linux-users-repair](../learning_lab/vm_preview/real-linux-users-repair.json). Disposable identities and locked/expiry/shell distinctions; no real credential creation/full policy administration. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/passwd`, `/etc/shadow`, `/etc/group`, `/etc/skel/`, `chage`, `getent`, `groupadd`, `groupdel`, `groupmod`, `passwd`, `useradd`, `userdel`, `usermod`.

Explicit bounded-practice terms: `/etc/passwd`, `/etc/shadow`, `/etc/group`, `chage`, `getent`, `groupadd`, `groupdel`, `passwd`, `useradd`, `userdel`, `usermod`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 107.2 — Automate system administration tasks by scheduling jobs (exam 102, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | cron and at scheduling | V+R: [real-linux-schedule-cron](../learning_lab/vm_preview/real-linux-schedule-cron.json), [real-linux-schedule-diagnose](../learning_lab/vm_preview/real-linux-schedule-diagnose.json), [real-linux-schedule-monotonic](../learning_lab/vm_preview/real-linux-schedule-monotonic.json), [real-linux-schedule-calendar](../learning_lab/vm_preview/real-linux-schedule-calendar.json), [real-linux-schedule-persistence](../learning_lab/vm_preview/real-linux-schedule-persistence.json), [real-linux-schedule-assessment](../learning_lab/vm_preview/real-linux-schedule-assessment.json). cron/system/user timers with identities, catch-up/overlap and cleanup; at absent and policy breadth omitted. |
| 2 | Scheduler access control | **Missing**: no demonstrated dedicated subskill. |
| 3 | systemd timer operation | V+R: [real-linux-schedule-cron](../learning_lab/vm_preview/real-linux-schedule-cron.json), [real-linux-schedule-diagnose](../learning_lab/vm_preview/real-linux-schedule-diagnose.json), [real-linux-schedule-monotonic](../learning_lab/vm_preview/real-linux-schedule-monotonic.json), [real-linux-schedule-calendar](../learning_lab/vm_preview/real-linux-schedule-calendar.json), [real-linux-schedule-persistence](../learning_lab/vm_preview/real-linux-schedule-persistence.json), [real-linux-schedule-assessment](../learning_lab/vm_preview/real-linux-schedule-assessment.json). cron/system/user timers with identities, catch-up/overlap and cleanup; at absent and policy breadth omitted. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/cron.{d,daily,hourly,monthly,weekly}/`, `/etc/at.deny`, `/etc/at.allow`, `/etc/crontab`, `/etc/cron.allow`, `/etc/cron.deny`, `/var/spool/cron/`, `crontab`, `at`, `atq`, `atrm`, `systemctl`, `systemd-run`.

Explicit bounded-practice terms: `crontab`, `systemctl`, `systemd-run`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 107.3 — Localisation and internationalisation (exam 102, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Locale configuration | **Missing**: no demonstrated dedicated subskill. |
| 2 | Timezone configuration | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/timezone`, `/etc/localtime`, `/usr/share/zoneinfo/`, `LC_*`, `LC_ALL`, `LANG`, `TZ`, `/usr/bin/locale`, `tzselect`, `timedatectl`, `date`, `iconv`, `UTF-8`, `ISO-8859`, `ASCII`, `Unicode`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 108.1 — Maintain system time (exam 102, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | System-clock adjustment | **Missing**: no demonstrated dedicated subskill. |
| 2 | UTC hardware-clock configuration | **Missing**: no demonstrated dedicated subskill. |
| 3 | Timezone setup | Preparation only; no objective credit. G+R: [real-linux-schedule-inspect](../learning_lab/vm_preview/real-linux-schedule-inspect.json). Clock/timezone observation only; no setting or synchronization. Preparatory, not credited as objective practice. |
| 4 | ntpd/chrony configuration | **Missing**: no demonstrated dedicated subskill. |
| 5 | NTP pool operation | **Missing**: no demonstrated dedicated subskill. |
| 6 | ntpq awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/usr/share/zoneinfo/`, `/etc/timezone`, `/etc/localtime`, `/etc/ntp.conf`, `/etc/chrony.conf`, `date`, `hwclock`, `timedatectl`, `ntpd`, `ntpdate`, `chronyc`, `pool.ntp.org`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 108.2 — System logging (exam 102, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | rsyslog rules | V+R: [real-linux-admin-logs](../learning_lab/vm_preview/real-linux-admin-logs.json), [real-linux-admin-rotation](../learning_lab/vm_preview/real-linux-admin-rotation.json), [real-linux-admin-incident](../learning_lab/vm_preview/real-linux-admin-incident.json). Dedicated local rsyslog/journal/rotation; no general persistence/retention/rescue/remote logging. |
| 2 | Facilities/severity/actions | V+R: [real-linux-admin-logs](../learning_lab/vm_preview/real-linux-admin-logs.json), [real-linux-admin-rotation](../learning_lab/vm_preview/real-linux-admin-rotation.json), [real-linux-admin-incident](../learning_lab/vm_preview/real-linux-admin-incident.json). Dedicated local rsyslog/journal/rotation; no general persistence/retention/rescue/remote logging. |
| 3 | Journal queries | V+R: [real-linux-admin-logs](../learning_lab/vm_preview/real-linux-admin-logs.json), [real-linux-admin-rotation](../learning_lab/vm_preview/real-linux-admin-rotation.json), [real-linux-admin-incident](../learning_lab/vm_preview/real-linux-admin-incident.json). Dedicated local rsyslog/journal/rotation; no general persistence/retention/rescue/remote logging. |
| 4 | Journal time/unit/priority filters | V+R: [real-linux-admin-logs](../learning_lab/vm_preview/real-linux-admin-logs.json), [real-linux-admin-rotation](../learning_lab/vm_preview/real-linux-admin-rotation.json), [real-linux-admin-incident](../learning_lab/vm_preview/real-linux-admin-incident.json). Dedicated local rsyslog/journal/rotation; no general persistence/retention/rescue/remote logging. |
| 5 | Persistent journal and size control | **Missing**: no demonstrated dedicated subskill. |
| 6 | Journal retention deletion | **Missing**: no demonstrated dedicated subskill. |
| 7 | Offline/rescue journal access | **Missing**: no demonstrated dedicated subskill. |
| 8 | journald/rsyslog interaction | V+R: [real-linux-admin-logs](../learning_lab/vm_preview/real-linux-admin-logs.json), [real-linux-admin-rotation](../learning_lab/vm_preview/real-linux-admin-rotation.json), [real-linux-admin-incident](../learning_lab/vm_preview/real-linux-admin-incident.json). Dedicated local rsyslog/journal/rotation; no general persistence/retention/rescue/remote logging. |
| 9 | Log rotation | V+R: [real-linux-admin-logs](../learning_lab/vm_preview/real-linux-admin-logs.json), [real-linux-admin-rotation](../learning_lab/vm_preview/real-linux-admin-rotation.json), [real-linux-admin-incident](../learning_lab/vm_preview/real-linux-admin-incident.json). Dedicated local rsyslog/journal/rotation; no general persistence/retention/rescue/remote logging. |
| 10 | Other syslog implementations | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/rsyslog.conf`, `/var/log/`, `logger`, `logrotate`, `/etc/logrotate.conf`, `/etc/logrotate.d/`, `journalctl`, `systemd-cat`, `/etc/systemd/journald.conf`, `/var/log/journal/`.

Explicit bounded-practice terms: `logger`, `logrotate`, `journalctl`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 108.3 — Mail Transfer Agent (MTA) basics (exam 102, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Mail aliases | **Missing**: no demonstrated dedicated subskill. |
| 2 | Forwarding | **Missing**: no demonstrated dedicated subskill. |
| 3 | MTA implementation awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `~/.forward`, `sendmail emulation layer commands`, `newaliases`, `mail`, `mailq`, `postfix`, `sendmail`, `exim`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 108.4 — Manage printers and printing (exam 102, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Local/remote CUPS setup | **Missing**: no demonstrated dedicated subskill. |
| 2 | Queue administration | **Missing**: no demonstrated dedicated subskill. |
| 3 | Print fault diagnosis | **Missing**: no demonstrated dedicated subskill. |
| 4 | Job insertion/removal | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `CUPS configuration files, tools and utilities`, `/etc/cups/`, `lpd legacy interface (lpr, lprm, lpq)`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 109.1 — Fundamentals of internet protocols (exam 102, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | IPv4 masks/CIDR | S+A+R: [gateway-dns](../learning_lab/packs/gateway-dns.json), [subnet-boundary](../learning_lab/packs/subnet-boundary.json), [service-firewall](../learning_lab/packs/service-firewall.json). Small IPv4/ICMP/TCP/DNS model; only declared endpoints/ports and no UDP transport/full port list/IPv6. |
| 2 | Private/public IPv4 | **Missing**: no demonstrated dedicated subskill. |
| 3 | Common service ports | S+A+R: [gateway-dns](../learning_lab/packs/gateway-dns.json), [subnet-boundary](../learning_lab/packs/subnet-boundary.json), [service-firewall](../learning_lab/packs/service-firewall.json). Small IPv4/ICMP/TCP/DNS model; only declared endpoints/ports and no UDP transport/full port list/IPv6. |
| 4 | TCP/UDP/ICMP distinctions | S+A+R: [gateway-dns](../learning_lab/packs/gateway-dns.json), [subnet-boundary](../learning_lab/packs/subnet-boundary.json), [service-firewall](../learning_lab/packs/service-firewall.json). Small IPv4/ICMP/TCP/DNS model; only declared endpoints/ports and no UDP transport/full port list/IPv6. |
| 5 | IPv4/IPv6 differences | **Missing**: no demonstrated dedicated subskill. |
| 6 | IPv6 essentials | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/services`, `IPv4, IPv6`, `Subnetting`, `TCP, UDP, ICMP`.

Explicit bounded-practice terms: `Subnetting`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 109.2 — Persistent network configuration (exam 102, weight 4; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Persistent host IP settings | **Missing**: no demonstrated dedicated subskill. |
| 2 | NetworkManager wired/wireless configuration | **Missing**: no demonstrated dedicated subskill. |
| 3 | systemd-networkd awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/hostname`, `/etc/hosts`, `/etc/nsswitch.conf`, `/etc/resolv.conf`, `nmcli`, `hostnamectl`, `ifup`, `ifdown`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 109.3 — Basic network troubleshooting (exam 102, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | iproute2 interface mutation | **Missing**: no demonstrated dedicated subskill. |
| 2 | iproute2 route/default-gateway mutation | **Missing**: no demonstrated dedicated subskill. |
| 3 | Network fault investigation | S+A+R: [gateway-dns](../learning_lab/packs/gateway-dns.json), [subnet-boundary](../learning_lab/packs/subnet-boundary.json), [service-firewall](../learning_lab/packs/service-firewall.json). Simulated addressing/routing and ordered TCP firewall outcomes, not iproute2 administration. S+A+R: [linux-network-interface-evidence](../learning_lab/collections/packs/linux-network-interface-evidence.lab.json), [linux-network-route-evidence](../learning_lab/collections/packs/linux-network-route-evidence.lab.json), [linux-network-name-evidence](../learning_lab/collections/packs/linux-network-name-evidence.lab.json), [linux-network-incident-evidence](../learning_lab/collections/packs/linux-network-incident-evidence.lab.json). Factual extraction only; live diagnosis and causal reasoning are not checked. |
| 4 | Legacy network utility awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `ip`, `hostname`, `ss`, `ping`, `ping6`, `traceroute`, `traceroute6`, `tracepath`, `tracepath6`, `netcat`, `ifconfig`, `netstat`, `route`.

Explicit bounded-practice terms: `ping`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 109.4 — Configure client side DNS (exam 102, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Remote DNS queries | S+A+R: [linux-dns-response-evidence](../learning_lab/collections/packs/linux-dns-response-evidence.lab.json), [linux-network-name-evidence](../learning_lab/collections/packs/linux-network-name-evidence.lab.json). Read supplied lookup/connectivity results; does not perform a DNS query. |
| 2 | Local/remote resolver configuration | S+A+R: [gateway-dns](../learning_lab/packs/gateway-dns.json). Declared virtual DNS resolver/gateway repair, not NSS/systemd-resolved. |
| 3 | Name-service ordering | **Missing**: no demonstrated dedicated subskill. |
| 4 | Resolution diagnosis | S+A+R: [gateway-dns](../learning_lab/packs/gateway-dns.json). Declared virtual DNS resolver/gateway repair, not NSS/systemd-resolved. S+A+R: [linux-dns-response-evidence](../learning_lab/collections/packs/linux-dns-response-evidence.lab.json), [linux-network-name-evidence](../learning_lab/collections/packs/linux-network-name-evidence.lab.json). Read supplied lookup/connectivity results; does not perform a DNS query. |
| 5 | systemd-resolved awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/hosts`, `/etc/resolv.conf`, `/etc/nsswitch.conf`, `host`, `dig`, `getent`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 110.1 — Perform security administration tasks (exam 102, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Privileged-bit audit | V+R: [real-linux-local-priority](../learning_lab/vm_preview/real-linux-local-priority.json). Read-only bounded /usr/bin privileged-bit audit; permission bits alone do not prove effective privilege. |
| 2 | Passwords and aging | V+R: [real-linux-users-restrictions](../learning_lab/vm_preview/real-linux-users-restrictions.json), [real-linux-admin-change](../learning_lab/vm_preview/real-linux-admin-change.json). Aging/locking observation and approved guest sudo use only; no password creation or sudo-policy repair. |
| 3 | Port discovery | **Missing**: no demonstrated dedicated subskill. |
| 4 | Login/process/memory constraints | **Missing**: no demonstrated dedicated subskill. |
| 5 | Login-history inspection | **Missing**: no demonstrated dedicated subskill. |
| 6 | sudo use and policy | V+R: [real-linux-users-restrictions](../learning_lab/vm_preview/real-linux-users-restrictions.json), [real-linux-admin-change](../learning_lab/vm_preview/real-linux-admin-change.json). Aging/locking observation and approved guest sudo use only; no password creation or sudo-policy repair. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `find`, `passwd`, `fuser`, `lsof`, `nmap`, `chage`, `netstat`, `sudo`, `/etc/sudoers`, `su`, `usermod`, `ulimit`, `who, w, last`.

Explicit bounded-practice terms: `chage`, `find`, `su`, `sudo`, `usermod`. Tool presence or a title is not executed practice. Exact resources/guide/acceptance references remain in the JSON evidence inventory.


### 110.2 — Setup host security (exam 102, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Shadow credential concepts | G+R: [real-linux-users-restrictions](../learning_lab/vm_preview/real-linux-users-restrictions.json). Password lock versus expiry/nologin; not comprehensive shadow/security hardening. |
| 2 | Disabling unnecessary network services | **Missing**: no demonstrated dedicated subskill. |
| 3 | TCP-wrapper concepts | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/nologin`, `/etc/passwd`, `/etc/shadow`, `/etc/xinetd.d/`, `/etc/xinetd.conf`, `systemd.socket`, `/etc/inittab`, `/etc/init.d/`, `/etc/hosts.allow`, `/etc/hosts.deny`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 110.3 — Securing data with encryption (exam 102, weight 4; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | SSH client operation | **Missing**: no demonstrated dedicated subskill. |
| 2 | SSH host-key trust | **Missing**: no demonstrated dedicated subskill. |
| 3 | GnuPG setup/revocation | **Missing**: no demonstrated dedicated subskill. |
| 4 | Encryption/signature workflows | **Missing**: no demonstrated dedicated subskill. |
| 5 | SSH forwarding | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `ssh`, `ssh-keygen`, `ssh-agent`, `ssh-add`, `~/.ssh/id_rsa and id_rsa.pub`, `~/.ssh/id_dsa and id_dsa.pub`, `~/.ssh/id_ecdsa and id_ecdsa.pub`, `~/.ssh/id_ed25519 and id_ed25519.pub`, `/etc/ssh/ssh_host_rsa_key and ssh_host_rsa_key.pub`, `/etc/ssh/ssh_host_dsa_key and ssh_host_dsa_key.pub`, `/etc/ssh/ssh_host_ecdsa_key and ssh_host_ecdsa_key.pub`, `/etc/ssh/ssh_host_ed25519_key and ssh_host_ed25519_key.pub`, `~/.ssh/authorized_keys`, `ssh_known_hosts`, `gpg`, `gpg-agent`, `~/.gnupg/`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 200.1 — Measure and Troubleshoot Resource Usage (exam 201, weight 6; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | CPU observation | V+R: [real-linux-capacity-baseline](../learning_lab/vm_preview/real-linux-capacity-baseline.json), [real-linux-capacity-cpu](../learning_lab/vm_preview/real-linux-capacity-cpu.json), [real-linux-capacity-memory](../learning_lab/vm_preview/real-linux-capacity-memory.json), [real-linux-capacity-io](../learning_lab/vm_preview/real-linux-capacity-io.json), [real-linux-live-monitoring](../learning_lab/vm_preview/real-linux-live-monitoring.json). Available vmstat/free/ps/top and bounded workloads; no iostat/iotop/sar or network throughput. S+A+R: [linux-resource-baseline](../learning_lab/collections/packs/linux-resource-baseline.lab.json), [linux-memory-evidence](../learning_lab/collections/packs/linux-memory-evidence.lab.json), [linux-space-inodes](../learning_lab/collections/packs/linux-space-inodes.lab.json). Fixed fictional facts/report bytes, not live counters, bottleneck identification or causal reasoning assessment. |
| 2 | Memory observation | V+R: [real-linux-capacity-baseline](../learning_lab/vm_preview/real-linux-capacity-baseline.json), [real-linux-capacity-cpu](../learning_lab/vm_preview/real-linux-capacity-cpu.json), [real-linux-capacity-memory](../learning_lab/vm_preview/real-linux-capacity-memory.json), [real-linux-capacity-io](../learning_lab/vm_preview/real-linux-capacity-io.json), [real-linux-live-monitoring](../learning_lab/vm_preview/real-linux-live-monitoring.json). Available vmstat/free/ps/top and bounded workloads; no iostat/iotop/sar or network throughput. S+A+R: [linux-resource-baseline](../learning_lab/collections/packs/linux-resource-baseline.lab.json), [linux-memory-evidence](../learning_lab/collections/packs/linux-memory-evidence.lab.json), [linux-space-inodes](../learning_lab/collections/packs/linux-space-inodes.lab.json). Fixed fictional facts/report bytes, not live counters, bottleneck identification or causal reasoning assessment. |
| 3 | Disk I/O observation | V+R: [real-linux-capacity-baseline](../learning_lab/vm_preview/real-linux-capacity-baseline.json), [real-linux-capacity-cpu](../learning_lab/vm_preview/real-linux-capacity-cpu.json), [real-linux-capacity-memory](../learning_lab/vm_preview/real-linux-capacity-memory.json), [real-linux-capacity-io](../learning_lab/vm_preview/real-linux-capacity-io.json), [real-linux-live-monitoring](../learning_lab/vm_preview/real-linux-live-monitoring.json). Available vmstat/free/ps/top and bounded workloads; no iostat/iotop/sar or network throughput. S+A+R: [linux-resource-baseline](../learning_lab/collections/packs/linux-resource-baseline.lab.json), [linux-memory-evidence](../learning_lab/collections/packs/linux-memory-evidence.lab.json), [linux-space-inodes](../learning_lab/collections/packs/linux-space-inodes.lab.json). Fixed fictional facts/report bytes, not live counters, bottleneck identification or causal reasoning assessment. |
| 4 | Network I/O observation | **Missing**: no demonstrated dedicated subskill. |
| 5 | Router/firewall throughput | **Missing**: no demonstrated dedicated subskill. |
| 6 | Per-client bandwidth | **Missing**: no demonstrated dedicated subskill. |
| 7 | Symptom correlation | V+R: [real-linux-capacity-space-inodes](../learning_lab/vm_preview/real-linux-capacity-space-inodes.json), [real-linux-capacity-recommendation](../learning_lab/vm_preview/real-linux-capacity-recommendation.json). Supplied faults and cautious interpretation; not live manufactured shortage or network bottleneck. S+A+R: [linux-resource-baseline](../learning_lab/collections/packs/linux-resource-baseline.lab.json), [linux-memory-evidence](../learning_lab/collections/packs/linux-memory-evidence.lab.json), [linux-space-inodes](../learning_lab/collections/packs/linux-space-inodes.lab.json). Fixed fictional facts/report bytes, not live counters, bottleneck identification or causal reasoning assessment. |
| 8 | Bottleneck/throughput diagnosis | V+R: [real-linux-capacity-space-inodes](../learning_lab/vm_preview/real-linux-capacity-space-inodes.json), [real-linux-capacity-recommendation](../learning_lab/vm_preview/real-linux-capacity-recommendation.json). Supplied faults and cautious interpretation; not live manufactured shortage or network bottleneck. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `iostat`, `iotop`, `vmstat`, `netstat`, `ss`, `iptraf`, `pstree, ps`, `w`, `lsof`, `top`, `htop`, `uptime`, `sar`, `swap`, `processes blocked on I/O`, `blocks in`, `blocks out`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 200.2 — Predict Future Resource Needs (exam 201, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Sustained infrastructure monitoring | **Missing**: no demonstrated dedicated subskill. |
| 2 | Capacity breakpoint prediction | V+R: [real-linux-capacity-trends](../learning_lab/vm_preview/real-linux-capacity-trends.json), [real-linux-capacity-forecast](../learning_lab/vm_preview/real-linux-capacity-forecast.json), [real-linux-capacity-recommendation](../learning_lab/vm_preview/real-linux-capacity-recommendation.json). Small synthetic series/plain-text trend and independently checked arithmetic; incomplete evidence may prevent a forecast. |
| 3 | Growth-rate estimation | V+R: [real-linux-capacity-trends](../learning_lab/vm_preview/real-linux-capacity-trends.json), [real-linux-capacity-forecast](../learning_lab/vm_preview/real-linux-capacity-forecast.json), [real-linux-capacity-recommendation](../learning_lab/vm_preview/real-linux-capacity-recommendation.json). Small synthetic series/plain-text trend and independently checked arithmetic; incomplete evidence may prevent a forecast. S+A+R: [linux-trend-handover](../learning_lab/collections/packs/linux-trend-handover.lab.json). Checked dated records; growth reasoning/forecast remains self-review. |
| 4 | Trend plotting | V+R: [real-linux-capacity-trends](../learning_lab/vm_preview/real-linux-capacity-trends.json), [real-linux-capacity-forecast](../learning_lab/vm_preview/real-linux-capacity-forecast.json), [real-linux-capacity-recommendation](../learning_lab/vm_preview/real-linux-capacity-recommendation.json). Small synthetic series/plain-text trend and independently checked arithmetic; incomplete evidence may prevent a forecast. |
| 5 | Monitoring stack awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `diagnose`, `predict growth`, `resource exhaustion`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 201.1 — Kernel components (exam 201, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Kernel generation documentation | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** The objective description also requires kernel image types, stable/LTS policy, patches and module concepts; read-only version queries do not establish these.

Official non-exhaustive tools/files/terms: `/usr/src/linux/`, `/usr/src/linux/Documentation/`, `zImage`, `bzImage`, `xz compression`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 201.2 — Compiling a Linux kernel (exam 201, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Kernel source tree | **Missing**: no demonstrated dedicated subskill. |
| 2 | Kernel Makefile structure | **Missing**: no demonstrated dedicated subskill. |
| 3 | Kernel build targets | **Missing**: no demonstrated dedicated subskill. |
| 4 | Kernel feature configuration | **Missing**: no demonstrated dedicated subskill. |
| 5 | Kernel/module compilation | **Missing**: no demonstrated dedicated subskill. |
| 6 | Kernel/module installation | **Missing**: no demonstrated dedicated subskill. |
| 7 | Bootloader handoff to new kernel | **Missing**: no demonstrated dedicated subskill. |
| 8 | Module configuration | **Missing**: no demonstrated dedicated subskill. |
| 9 | DKMS workflow | **Missing**: no demonstrated dedicated subskill. |
| 10 | dracut awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** No build-tool/kernel/source installation environment has been approved; every listed compile/install/reboot outcome remains missing.

Official non-exhaustive tools/files/terms: `mkinitrd`, `mkinitramfs`, `make`, `make targets (all, config, xconfig, menuconfig, gconfig, oldconfig, mrproper, zImage, bzImage, modules, modules_install, rpm-pkg, binrpm-pkg, deb-pkg)`, `gzip`, `bzip2`, `module tools`, `/usr/src/linux/.config`, `/lib/modules/kernel-version/`, `depmod`, `dkms`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 201.3 — Kernel runtime management and troubleshooting (exam 201, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Running kernel/module queries | V+R: [real-linux-discovery-identity](../learning_lab/vm_preview/real-linux-discovery-identity.json), [real-linux-discovery-kernel](../learning_lab/vm_preview/real-linux-discovery-kernel.json), [real-linux-discovery-boot](../learning_lab/vm_preview/real-linux-discovery-boot.json). Read-only running/built-in/module/parameter/hardware evidence; no load/unload/alias/sysctl/udev operations. |
| 2 | Module insertion/removal | **Missing**: no demonstrated dedicated subskill. |
| 3 | Unload preconditions | **Missing**: no demonstrated dedicated subskill. |
| 4 | Module parameter discovery | V+R: [real-linux-discovery-identity](../learning_lab/vm_preview/real-linux-discovery-identity.json), [real-linux-discovery-kernel](../learning_lab/vm_preview/real-linux-discovery-kernel.json), [real-linux-discovery-boot](../learning_lab/vm_preview/real-linux-discovery-boot.json). Read-only running/built-in/module/parameter/hardware evidence; no load/unload/alias/sysctl/udev operations. |
| 5 | Module aliases | **Missing**: no demonstrated dedicated subskill. |
| 6 | /proc investigation | V+R: [real-linux-discovery-identity](../learning_lab/vm_preview/real-linux-discovery-identity.json), [real-linux-discovery-kernel](../learning_lab/vm_preview/real-linux-discovery-kernel.json), [real-linux-discovery-boot](../learning_lab/vm_preview/real-linux-discovery-boot.json). Read-only running/built-in/module/parameter/hardware evidence; no load/unload/alias/sysctl/udev operations. |
| 7 | Kernel/module/boot filesystem locations | V+R: [real-linux-discovery-identity](../learning_lab/vm_preview/real-linux-discovery-identity.json), [real-linux-discovery-kernel](../learning_lab/vm_preview/real-linux-discovery-kernel.json), [real-linux-discovery-boot](../learning_lab/vm_preview/real-linux-discovery-boot.json). Read-only running/built-in/module/parameter/hardware evidence; no load/unload/alias/sysctl/udev operations. |
| 8 | Hardware investigation | V+R: [real-linux-discovery-identity](../learning_lab/vm_preview/real-linux-discovery-identity.json), [real-linux-discovery-kernel](../learning_lab/vm_preview/real-linux-discovery-kernel.json), [real-linux-discovery-boot](../learning_lab/vm_preview/real-linux-discovery-boot.json). Read-only running/built-in/module/parameter/hardware evidence; no load/unload/alias/sysctl/udev operations. |
| 9 | udev rules | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/lib/modules/kernel-version/modules.dep`, `module configuration files in /etc/`, `/proc/sys/kernel/`, `/sbin/depmod`, `/sbin/rmmod`, `/sbin/modinfo`, `/bin/dmesg`, `/sbin/lspci`, `/usr/bin/lsdev`, `/sbin/lsmod`, `/sbin/modprobe`, `/sbin/insmod`, `/bin/uname`, `/usr/bin/lsusb`, `/etc/sysctl.conf, /etc/sysctl.d/`, `/sbin/sysctl`, `udevmonitor`, `udevadm monitor`, `/etc/udev/`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 202.1 — Customizing system startup (exam 201, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | systemd startup customization | V+R: [real-linux-admin-lifecycle](../learning_lab/vm_preview/real-linux-admin-lifecycle.json), [real-linux-admin-boot](../learning_lab/vm_preview/real-linux-admin-boot.json), [real-linux-admin-override](../learning_lab/vm_preview/real-linux-admin-override.json), [real-linux-schedule-calendar](../learning_lab/vm_preview/real-linux-schedule-calendar.json). Dedicated systemd enablement/override/timer fixtures, not target/SysV/LSB breadth. |
| 2 | SysV startup customization | **Missing**: no demonstrated dedicated subskill. |
| 3 | LSB conventions | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/usr/lib/systemd/`, `/etc/systemd/`, `/run/systemd/`, `systemctl`, `systemd-delta`, `/etc/inittab`, `/etc/init.d/`, `/etc/rc.d/`, `chkconfig`, `update-rc.d`, `init and telinit`.

Explicit bounded-practice terms: `systemctl`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 202.2 — System recovery (exam 201, weight 4; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Firmware boot paths | **Missing**: no demonstrated dedicated subskill. |
| 2 | NVMe boot | **Missing**: no demonstrated dedicated subskill. |
| 3 | GRUB variants | **Missing**: no demonstrated dedicated subskill. |
| 4 | GRUB interactive shell | **Missing**: no demonstrated dedicated subskill. |
| 5 | Loader handoff | **Missing**: no demonstrated dedicated subskill. |
| 6 | Kernel loading | **Missing**: no demonstrated dedicated subskill. |
| 7 | Hardware initialization | **Missing**: no demonstrated dedicated subskill. |
| 8 | Service initialization | Preparation only; no objective credit. G+R: [real-linux-admin-boot](../learning_lab/vm_preview/real-linux-admin-boot.json), [real-linux-admin-incident](../learning_lab/vm_preview/real-linux-admin-incident.json). Service initialization context only; no boot/rescue recovery practice credit. |
| 9 | Bootloader placement | **Missing**: no demonstrated dedicated subskill. |
| 10 | Temporary loader overrides | **Missing**: no demonstrated dedicated subskill. |
| 11 | Rescue/emergency modes | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Ordinary service rollback/guest reboot is not bootloader, root-filesystem, firmware or rescue recovery.

Official non-exhaustive tools/files/terms: `mount`, `fsck`, `inittab, telinit and init with SysV init`, `The contents of /boot/, /boot/grub/ and /boot/efi/`, `EFI System Partition (ESP)`, `GRUB`, `grub-install`, `efibootmgr`, `UEFI shell`, `initrd, initramfs`, `Master boot record`, `systemctl`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 202.3 — Alternate Bootloaders (exam 201, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | SYSLINUX family | **Missing**: no demonstrated dedicated subskill. |
| 2 | BIOS/UEFI PXE | **Missing**: no demonstrated dedicated subskill. |
| 3 | systemd-boot/U-Boot awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `syslinux`, `extlinux`, `isolinux.bin`, `isolinux.cfg`, `isohdpfx.bin`, `efiboot.img`, `pxelinux.0`, `pxelinux.cfg/`, `uefi/shim.efi`, `uefi/grubx64.efi`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 203.1 — Operating the Linux filesystem (exam 201, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | fstab operation | V+R: [real-linux-storage-fstab](../learning_lab/vm_preview/real-linux-storage-fstab.json), [real-linux-storage-mount](../learning_lab/vm_preview/real-linux-storage-mount.json), [real-linux-storage-faults](../learning_lab/vm_preview/real-linux-storage-faults.json). Separate practice fstab explicit mount; no live boot mounts/swap/systemd mount units. |
| 2 | Swap partitions/files | **Missing**: no demonstrated dedicated subskill. |
| 3 | UUID-based mounting | V+R: [real-linux-storage-fstab](../learning_lab/vm_preview/real-linux-storage-fstab.json), [real-linux-storage-mount](../learning_lab/vm_preview/real-linux-storage-mount.json), [real-linux-storage-faults](../learning_lab/vm_preview/real-linux-storage-faults.json). Separate practice fstab explicit mount; no live boot mounts/swap/systemd mount units. |
| 4 | systemd mounts | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/fstab`, `/etc/mtab`, `/proc/mounts`, `mount and umount`, `blkid`, `sync`, `swapon`, `swapoff`.

Explicit bounded-practice terms: `blkid`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 203.2 — Maintaining a Linux filesystem (exam 201, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | ext-family maintenance | V+R: [real-linux-storage-filesystem](../learning_lab/vm_preview/real-linux-storage-filesystem.json), [real-linux-storage-repair](../learning_lab/vm_preview/real-linux-storage-repair.json), [real-linux-storage-incident](../learning_lab/vm_preview/real-linux-storage-incident.json). Ext4 and controlled copy-only defect; no ext2/3 breadth/Btrfs/XFS/SMART. |
| 2 | Btrfs subvolumes/snapshots | **Missing**: no demonstrated dedicated subskill. |
| 3 | XFS maintenance | **Missing**: no demonstrated dedicated subskill. |
| 4 | ZFS awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** No SMART/Btrfs/XFS/ZFS operation; a controlled ext4 link-count fault does not generalize to arbitrary damage.

Official non-exhaustive tools/files/terms: `mkfs (mkfs.*)`, `mkswap`, `fsck (fsck.*)`, `tune2fs, dumpe2fs and debugfs`, `btrfs, btrfs-convert`, `xfs_info, xfs_check, xfs_repair, xfsdump and xfsrestore`, `smartd, smartctl`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 203.3 — Creating and configuring filesystem options (exam 201, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | autofs configuration | **Missing**: no demonstrated dedicated subskill. |
| 2 | systemd automounts | **Missing**: no demonstrated dedicated subskill. |
| 3 | UDF/ISO9660 tooling | **Missing**: no demonstrated dedicated subskill. |
| 4 | HFS optical awareness | **Missing**: no demonstrated dedicated subskill. |
| 5 | Optical filesystem extensions | **Missing**: no demonstrated dedicated subskill. |
| 6 | dm-crypt/LUKS concepts | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/auto.master`, `/etc/auto.[dir]`, `mkisofs`, `cryptsetup`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 204.1 — Configuring RAID (exam 201, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Software RAID operation | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `mdadm.conf`, `mdadm`, `/proc/mdstat`, `partition type 0xFD`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 204.2 — Adjusting Storage Device Access (exam 201, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | IDE/ATAPI/SATA DMA | **Missing**: no demonstrated dedicated subskill. |
| 2 | AHCI/NVMe storage access | **Missing**: no demonstrated dedicated subskill. |
| 3 | Interrupt/resource analysis | **Missing**: no demonstrated dedicated subskill. |
| 4 | sdparm awareness | **Missing**: no demonstrated dedicated subskill. |
| 5 | iSCSI operations | **Missing**: no demonstrated dedicated subskill. |
| 6 | SAN protocol awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `hdparm, sdparm`, `nvme`, `tune2fs`, `fstrim`, `sysctl`, `/dev/hd*, /dev/sd*, /dev/nvme*`, `iscsiadm, scsi_id, iscsid and iscsid.conf`, `WWID, WWN, LUN numbers`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 204.3 — Logical Volume Manager (exam 201, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | LVM toolset | **Missing**: no demonstrated dedicated subskill. |
| 2 | PV/VG/LV lifecycle and resizing | **Missing**: no demonstrated dedicated subskill. |
| 3 | LVM snapshots | **Missing**: no demonstrated dedicated subskill. |
| 4 | VG activation | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/sbin/pv*`, `/sbin/lv*`, `/sbin/vg*`, `mount`, `/dev/mapper/`, `lvm.conf`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 205.1 — Basic networking configuration (exam 201, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Ethernet configuration | **Missing**: no demonstrated dedicated subskill. |
| 2 | Wireless access configuration | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `ip`, `ifconfig`, `route`, `arp`, `iw`, `iwconfig`, `iwlist`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 205.2 — Advanced Network Configuration (exam 201, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Route administration | **Missing**: no demonstrated dedicated subskill. |
| 2 | Ethernet administration | **Missing**: no demonstrated dedicated subskill. |
| 3 | Interface status analysis | S+A+R: [linux-network-interface-evidence](../learning_lab/collections/packs/linux-network-interface-evidence.lab.json). Supplied interface facts only, no device command or live administration. |
| 4 | Traffic observation | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `ip`, `ifconfig`, `route`, `arp`, `ss`, `netstat`, `lsof`, `ping, ping6`, `nc`, `tcpdump`, `nmap`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 205.3 — Troubleshooting network issues (exam 201, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Network access policy files | **Missing**: no demonstrated dedicated subskill. |
| 2 | Interface troubleshooting | S+A+R: [linux-network-interface-evidence](../learning_lab/collections/packs/linux-network-interface-evidence.lab.json), [linux-network-route-evidence](../learning_lab/collections/packs/linux-network-route-evidence.lab.json), [linux-network-name-evidence](../learning_lab/collections/packs/linux-network-name-evidence.lab.json), [linux-network-incident-evidence](../learning_lab/collections/packs/linux-network-incident-evidence.lab.json). Static interface/route/test/context extraction; no hardware/startup repair or verified cause. S+A+R: [gateway-dns](../learning_lab/packs/gateway-dns.json), [subnet-boundary](../learning_lab/packs/subnet-boundary.json), [service-firewall](../learning_lab/packs/service-firewall.json). Original bounded connectivity troubleshooting; not real Linux tooling. |
| 3 | Route troubleshooting | S+A+R: [linux-network-interface-evidence](../learning_lab/collections/packs/linux-network-interface-evidence.lab.json), [linux-network-route-evidence](../learning_lab/collections/packs/linux-network-route-evidence.lab.json), [linux-network-name-evidence](../learning_lab/collections/packs/linux-network-name-evidence.lab.json), [linux-network-incident-evidence](../learning_lab/collections/packs/linux-network-incident-evidence.lab.json). Static interface/route/test/context extraction; no hardware/startup repair or verified cause. S+A+R: [gateway-dns](../learning_lab/packs/gateway-dns.json), [subnet-boundary](../learning_lab/packs/subnet-boundary.json), [service-firewall](../learning_lab/packs/service-firewall.json). Original bounded connectivity troubleshooting; not real Linux tooling. |
| 4 | Connection states | **Missing**: no demonstrated dedicated subskill. |
| 5 | Configuration evidence | S+A+R: [linux-network-interface-evidence](../learning_lab/collections/packs/linux-network-interface-evidence.lab.json), [linux-network-route-evidence](../learning_lab/collections/packs/linux-network-route-evidence.lab.json), [linux-network-name-evidence](../learning_lab/collections/packs/linux-network-name-evidence.lab.json), [linux-network-incident-evidence](../learning_lab/collections/packs/linux-network-incident-evidence.lab.json). Static interface/route/test/context extraction; no hardware/startup repair or verified cause. S+A+R: [gateway-dns](../learning_lab/packs/gateway-dns.json), [subnet-boundary](../learning_lab/packs/subnet-boundary.json), [service-firewall](../learning_lab/packs/service-firewall.json). Original bounded connectivity troubleshooting; not real Linux tooling. |
| 6 | Recognized/used devices | **Missing**: no demonstrated dedicated subskill. |
| 7 | Startup networking | **Missing**: no demonstrated dedicated subskill. |
| 8 | NetworkManager interactions | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Offline records check extraction, not running ip/ss/dig/curl or identifying a root cause.

Official non-exhaustive tools/files/terms: `ip`, `ifconfig`, `route`, `ss`, `netstat`, `/etc/network/, /etc/sysconfig/network-scripts/`, `ping, ping6`, `traceroute, traceroute6`, `mtr`, `hostname`, `System log files such as /var/log/syslog, /var/log/messages and the systemd journal`, `dmesg`, `/etc/resolv.conf`, `/etc/hosts`, `/etc/hostname, /etc/HOSTNAME`, `/etc/hosts.allow, /etc/hosts.deny`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 206.1 — Make and install programs from source (exam 201, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Source unpacking | Preparation only; no objective credit. G+R: [real-linux-backup-archive](../learning_lab/vm_preview/real-linux-backup-archive.json), [real-linux-backup-checksum](../learning_lab/vm_preview/real-linux-backup-checksum.json). Generic archive preparation only; not a source-code build exercise. Reinforcement, not objective-practice credit. |
| 2 | make builds | **Missing**: no demonstrated dedicated subskill. |
| 3 | configure options | **Missing**: no demonstrated dedicated subskill. |
| 4 | Source placement | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/usr/src/`, `gunzip`, `gzip`, `bzip2`, `xz`, `tar`, `configure`, `make`, `uname`, `install`, `patch`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 206.2 — Backup operations (exam 201, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | System backup scope | G+R: [real-linux-backup-requirements](../learning_lab/vm_preview/real-linux-backup-requirements.json). Recovery requirements for the tiny fixture; no complete system scope. |
| 2 | Network backup suites | **Missing**: no demonstrated dedicated subskill. |
| 3 | Backup-media tradeoffs | **Missing**: no demonstrated dedicated subskill. |
| 4 | Scoped/manual backup | V+R: [real-linux-backup-archive](../learning_lab/vm_preview/real-linux-backup-archive.json), [real-linux-backup-checksum](../learning_lab/vm_preview/real-linux-backup-checksum.json), [real-linux-backup-damage](../learning_lab/vm_preview/real-linux-backup-damage.json), [real-linux-backup-restore](../learning_lab/vm_preview/real-linux-backup-restore.json), [real-linux-backup-access](../learning_lab/vm_preview/real-linux-backup-access.json), [real-linux-backup-versions](../learning_lab/vm_preview/real-linux-backup-versions.json), [real-linux-backup-assessment](../learning_lab/vm_preview/real-linux-backup-assessment.json). Scoped tar/gzip, independent expectations, corruption/incompleteness/version checks and actual-user restore; no automated/full-system/network/media breadth. |
| 5 | Backup validation | V+R: [real-linux-backup-archive](../learning_lab/vm_preview/real-linux-backup-archive.json), [real-linux-backup-checksum](../learning_lab/vm_preview/real-linux-backup-checksum.json), [real-linux-backup-damage](../learning_lab/vm_preview/real-linux-backup-damage.json), [real-linux-backup-restore](../learning_lab/vm_preview/real-linux-backup-restore.json), [real-linux-backup-access](../learning_lab/vm_preview/real-linux-backup-access.json), [real-linux-backup-versions](../learning_lab/vm_preview/real-linux-backup-versions.json), [real-linux-backup-assessment](../learning_lab/vm_preview/real-linux-backup-assessment.json). Scoped tar/gzip, independent expectations, corruption/incompleteness/version checks and actual-user restore; no automated/full-system/network/media breadth. |
| 6 | Recovery | V+R: [real-linux-backup-archive](../learning_lab/vm_preview/real-linux-backup-archive.json), [real-linux-backup-checksum](../learning_lab/vm_preview/real-linux-backup-checksum.json), [real-linux-backup-damage](../learning_lab/vm_preview/real-linux-backup-damage.json), [real-linux-backup-restore](../learning_lab/vm_preview/real-linux-backup-restore.json), [real-linux-backup-access](../learning_lab/vm_preview/real-linux-backup-access.json), [real-linux-backup-versions](../learning_lab/vm_preview/real-linux-backup-versions.json), [real-linux-backup-assessment](../learning_lab/vm_preview/real-linux-backup-assessment.json). Scoped tar/gzip, independent expectations, corruption/incompleteness/version checks and actual-user restore; no automated/full-system/network/media breadth. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/bin/sh`, `dd`, `tar`, `/dev/st* and /dev/nst*`, `mt`, `rsync`.

Explicit bounded-practice terms: `tar`. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 206.3 — Notify users on system-related issues (exam 201, weight 1; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Login notices | **Missing**: no demonstrated dedicated subskill. |
| 2 | Maintenance notices to active users | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/issue`, `/etc/issue.net`, `/etc/motd`, `wall`, `shutdown`, `systemctl`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 207.1 — Basic DNS server configuration (exam 202, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | BIND server configuration | **Missing**: no demonstrated dedicated subskill. |
| 2 | Zone-path configuration | **Missing**: no demonstrated dedicated subskill. |
| 3 | Safe server/zone reload | **Missing**: no demonstrated dedicated subskill. |
| 4 | Alternate DNS implementations | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** AA/RA/cache/rcode interpretation is contextual reinforcement; no operational BIND server exists in the present lesson environment. Adjacent preparation only (no objective credit): linux-dns-response-evidence, linux-dns-handover-evidence.

Official non-exhaustive tools/files/terms: `/etc/named.conf`, `/var/named/`, `rndc`, `named-checkconf`, `kill`, `host`, `dig`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 207.2 — Create and maintain DNS zones (exam 202, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | BIND zone configuration | S+A+R: [linux-dns-zone-evidence](../learning_lab/collections/packs/linux-dns-zone-evidence.lab.json), [linux-dns-consistency-evidence](../learning_lab/collections/packs/linux-dns-consistency-evidence.lab.json), [linux-dns-handover-evidence](../learning_lab/collections/packs/linux-dns-handover-evidence.lab.json). Record/delegation/serial/validator-response facts only; no executed validation, edit/reload or authoritative operation. |
| 2 | DNS query tools | S+A+R: [linux-dns-zone-evidence](../learning_lab/collections/packs/linux-dns-zone-evidence.lab.json), [linux-dns-consistency-evidence](../learning_lab/collections/packs/linux-dns-consistency-evidence.lab.json), [linux-dns-handover-evidence](../learning_lab/collections/packs/linux-dns-handover-evidence.lab.json). Record/delegation/serial/validator-response facts only; no executed validation, edit/reload or authoritative operation. |
| 3 | Zone records/files | S+A+R: [linux-dns-zone-evidence](../learning_lab/collections/packs/linux-dns-zone-evidence.lab.json), [linux-dns-consistency-evidence](../learning_lab/collections/packs/linux-dns-consistency-evidence.lab.json), [linux-dns-handover-evidence](../learning_lab/collections/packs/linux-dns-handover-evidence.lab.json). Record/delegation/serial/validator-response facts only; no executed validation, edit/reload or authoritative operation. |
| 4 | Forward/reverse host changes | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** CNAME/serial/delegation facts do not establish editing, successful checkzone/reload, reverse-zone maintenance or real query competence.

Official non-exhaustive tools/files/terms: `/var/named/`, `zone file syntax`, `resource record formats`, `named-checkzone`, `named-compilezone`, `masterfile-format`, `dig`, `nslookup`, `host`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 207.3 — Securing a DNS server (exam 202, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | BIND security settings | **Missing**: no demonstrated dedicated subskill. |
| 2 | DNS chroot | **Missing**: no demonstrated dedicated subskill. |
| 3 | Split/forwarder policy | **Missing**: no demonstrated dedicated subskill. |
| 4 | TSIG | **Missing**: no demonstrated dedicated subskill. |
| 5 | DNSSEC tools | **Missing**: no demonstrated dedicated subskill. |
| 6 | DANE records | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/named.conf`, `/etc/passwd`, `DNSSEC`, `dnssec-keygen`, `dnssec-signzone`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 208.1 — Basic Apache configuration (exam 202, weight 4; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Apache server configuration | S+A+R: [linux-web-listener-evidence](../learning_lab/collections/packs/linux-web-listener-evidence.lab.json), [linux-web-vhost-evidence](../learning_lab/collections/packs/linux-web-vhost-evidence.lab.json). Saved listener/request/log/vhost facts; no configured server, access policy or real client. |
| 2 | Apache logs | S+A+R: [linux-web-listener-evidence](../learning_lab/collections/packs/linux-web-listener-evidence.lab.json), [linux-web-vhost-evidence](../learning_lab/collections/packs/linux-web-vhost-evidence.lab.json). Saved listener/request/log/vhost facts; no configured server, access policy or real client. |
| 3 | Access restrictions | **Missing**: no demonstrated dedicated subskill. |
| 4 | PHP/mod_perl integration | **Missing**: no demonstrated dedicated subskill. |
| 5 | HTTP user authentication | **Missing**: no demonstrated dedicated subskill. |
| 6 | Worker/client/request limits | **Missing**: no demonstrated dedicated subskill. |
| 7 | Virtual-host configuration | S+A+R: [linux-web-listener-evidence](../learning_lab/collections/packs/linux-web-listener-evidence.lab.json), [linux-web-vhost-evidence](../learning_lab/collections/packs/linux-web-vhost-evidence.lab.json). Saved listener/request/log/vhost facts; no configured server, access policy or real client. |
| 8 | Redirect rules | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** No deployed Apache, authentication, PHP, worker limits or live virtual-host repair.

Official non-exhaustive tools/files/terms: `access logs and error logs`, `.htaccess`, `httpd.conf`, `mod_auth_basic, mod_authz_host and mod_access_compat`, `htpasswd`, `AuthUserFile, AuthGroupFile`, `apachectl, apache2ctl`, `httpd, apache2`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 208.2 — Apache configuration for HTTPS (exam 202, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | TLS server configuration | S+A+R: [linux-web-tls-evidence](../learning_lab/collections/packs/linux-web-tls-evidence.lab.json). Supplied SAN/name/date/handshake results only; no crypto verification, key/certificate provisioning or SNI exercise. |
| 2 | Private-key/CSR creation | **Missing**: no demonstrated dedicated subskill. |
| 3 | Self-signed certificates | **Missing**: no demonstrated dedicated subskill. |
| 4 | Chain/key installation | **Missing**: no demonstrated dedicated subskill. |
| 5 | SNI virtual hosts | **Missing**: no demonstrated dedicated subskill. |
| 6 | TLS virtual-host pitfalls | S+A+R: [linux-web-tls-evidence](../learning_lab/collections/packs/linux-web-tls-evidence.lab.json). Supplied SAN/name/date/handshake results only; no crypto verification, key/certificate provisioning or SNI exercise. |
| 7 | Protocol/cipher hardening | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** SAN/date/hostname excerpts do not validate a certificate cryptographically; no keys, CSR, chain/SNI/protocol policy operations.

Official non-exhaustive tools/files/terms: `Apache2 configuration files`, `/etc/ssl/, /etc/pki/`, `openssl, CA.pl`, `SSLEngine, SSLCertificateKeyFile, SSLCertificateFile`, `SSLCACertificateFile, SSLCACertificatePath`, `SSLProtocol, SSLCipherSuite, ServerTokens, ServerSignature, TraceEnable`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 208.3 — Implementing Squid as a caching proxy (exam 202, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Squid operation | **Missing**: no demonstrated dedicated subskill. |
| 2 | Proxy access restrictions | **Missing**: no demonstrated dedicated subskill. |
| 3 | Proxy authentication | **Missing**: no demonstrated dedicated subskill. |
| 4 | Squid ACL evaluation | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `squid.conf`, `acl`, `http_access`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 208.4 — Implementing Nginx as a web server and a reverse proxy (exam 202, weight 2; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | nginx configuration | S+A+R: [linux-web-proxy-evidence](../learning_lab/collections/packs/linux-web-proxy-evidence.lab.json). Saved upstream/config/log records, not proxy deployment or causal assessment. |
| 2 | Reverse-proxy operation | S+A+R: [linux-web-proxy-evidence](../learning_lab/collections/packs/linux-web-proxy-evidence.lab.json). Saved upstream/config/log records, not proxy deployment or causal assessment. |
| 3 | nginx serving | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Saved nginx upstream evidence does not establish deployment, cache/proxy semantics or a causal incident diagnosis.

Official non-exhaustive tools/files/terms: `/etc/nginx/`, `nginx`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 209.1 — Samba Server Configuration (exam 202, weight 5; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Samba documentation | **Missing**: no demonstrated dedicated subskill. |
| 2 | Samba configuration | **Missing**: no demonstrated dedicated subskill. |
| 3 | Samba tools/daemons | **Missing**: no demonstrated dedicated subskill. |
| 4 | Linux CIFS mounting | **Missing**: no demonstrated dedicated subskill. |
| 5 | Windows/Linux identity mapping | **Missing**: no demonstrated dedicated subskill. |
| 6 | Samba/AD security models | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `smbd, nmbd, winbindd`, `smbcontrol, smbstatus, testparm, smbpasswd, nmblookup`, `samba-tool`, `net`, `smbclient`, `mount.cifs`, `/etc/samba/`, `/var/log/samba/`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 209.2 — NFS Server Configuration (exam 202, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | NFSv3 exports | **Missing**: no demonstrated dedicated subskill. |
| 2 | NFS tools | **Missing**: no demonstrated dedicated subskill. |
| 3 | Host/subnet restrictions | **Missing**: no demonstrated dedicated subskill. |
| 4 | Server/client mount options | **Missing**: no demonstrated dedicated subskill. |
| 5 | TCP wrappers | **Missing**: no demonstrated dedicated subskill. |
| 6 | NFSv4 awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/exports`, `exportfs`, `showmount`, `nfsstat`, `/proc/mounts`, `/etc/fstab`, `rpcinfo`, `mountd`, `portmapper`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 210.1 — DHCP configuration (exam 202, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | DHCP service configuration | **Missing**: no demonstrated dedicated subskill. |
| 2 | Subnet/range allocation | **Missing**: no demonstrated dedicated subskill. |
| 3 | DHCPv6/router advertisements | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `dhcpd.conf`, `dhcpd.leases`, `DHCP Log messages in syslog or systemd journal`, `arp`, `dhcpd`, `radvd`, `radvd.conf`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 210.2 — PAM authentication (exam 202, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | PAM configuration | **Missing**: no demonstrated dedicated subskill. |
| 2 | Credential databases | G+R: [real-linux-users-restrictions](../learning_lab/vm_preview/real-linux-users-restrictions.json). Credential-state preparation only; no PAM/SSSD exercise credit. |
| 3 | SSSD/LDAP authentication | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** The user-lock lesson prepares credential concepts; it does not exercise PAM or SSSD/LDAP authentication.

Official non-exhaustive tools/files/terms: `/etc/pam.d/`, `pam.conf`, `nsswitch.conf`, `pam_unix, pam_cracklib, pam_limits, pam_listfile, pam_sss`, `sssd.conf`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 210.3 — LDAP client usage (exam 202, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | LDAP management/query tools | **Missing**: no demonstrated dedicated subskill. |
| 2 | Directory password changes | **Missing**: no demonstrated dedicated subskill. |
| 3 | Directory searches | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `ldapsearch`, `ldappasswd`, `ldapadd`, `ldapdelete`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 210.4 — Configuring an OpenLDAP server (exam 202, weight 4; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | OpenLDAP operation | **Missing**: no demonstrated dedicated subskill. |
| 2 | Directory-backed configuration | **Missing**: no demonstrated dedicated subskill. |
| 3 | LDAP access controls | **Missing**: no demonstrated dedicated subskill. |
| 4 | Distinguished names | **Missing**: no demonstrated dedicated subskill. |
| 5 | LDIF changes | **Missing**: no demonstrated dedicated subskill. |
| 6 | Schemas/whitepages | **Missing**: no demonstrated dedicated subskill. |
| 7 | Directory hierarchy | **Missing**: no demonstrated dedicated subskill. |
| 8 | OIDs/attributes/classes | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `slapd`, `slapd-config`, `LDIF`, `slapadd`, `slapcat`, `slapindex`, `/var/lib/ldap/`, `loglevel`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 211.1 — Using e-mail servers (exam 202, weight 4; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Postfix service | **Missing**: no demonstrated dedicated subskill. |
| 2 | Postfix TLS | **Missing**: no demonstrated dedicated subskill. |
| 3 | SMTP behavior | **Missing**: no demonstrated dedicated subskill. |
| 4 | Other MTAs | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `Configuration files and commands for postfix`, `/etc/postfix/`, `/var/spool/postfix/`, `sendmail emulation layer commands`, `/etc/aliases`, `mail-related logs in /var/log/`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 211.2 — Managing E-Mail Delivery (exam 202, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Sieve grammar | **Missing**: no demonstrated dedicated subskill. |
| 2 | Sieve mail selection/sorting | **Missing**: no demonstrated dedicated subskill. |
| 3 | procmail awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `Conditions and comparison operators`, `keep, fileinto, redirect, reject, discard, stop`, `Dovecot vacation extension`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 211.3 — Managing Mailbox Access (exam 202, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Dovecot IMAP/POP3 | **Missing**: no demonstrated dedicated subskill. |
| 2 | Dovecot TLS | **Missing**: no demonstrated dedicated subskill. |
| 3 | Courier awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/dovecot/`, `dovecot.conf`, `doveconf`, `doveadm`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 212.1 — Configuring a router (exam 202, weight 3; partial)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | iptables/ip6tables | **Missing**: no demonstrated dedicated subskill. |
| 2 | Routing | **Missing**: no demonstrated dedicated subskill. |
| 3 | IPv4 private and IPv6 local/link-local ranges | **Missing**: no demonstrated dedicated subskill. |
| 4 | Forwarding/NAT | **Missing**: no demonstrated dedicated subskill. |
| 5 | Packet filtering | S+A+R: [service-firewall](../learning_lab/packs/service-firewall.json). Only IPv4 known endpoints and ordered TCP rules; no host packet forwarding/iptables/IPv6/NAT/persistence. |
| 6 | Firewall persistence | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Declared TCP firewall model does not implement iptables, forwarding, IPv6, NAT or persistence.

Official non-exhaustive tools/files/terms: `/proc/sys/net/ipv4/`, `/proc/sys/net/ipv6/`, `/etc/services`, `iptables`, `ip6tables`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 212.2 — Managing FTP servers (exam 202, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Pure-FTPd/vsftpd administration | **Missing**: no demonstrated dedicated subskill. |
| 2 | ProFTPd awareness | **Missing**: no demonstrated dedicated subskill. |
| 3 | Active/passive FTP | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `vsftpd.conf`, `important Pure-FTPd command line options`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 212.3 — Secure shell (SSH) (exam 202, weight 4; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | OpenSSH service configuration | **Missing**: no demonstrated dedicated subskill. |
| 2 | Login restrictions | **Missing**: no demonstrated dedicated subskill. |
| 3 | Client/server keys | **Missing**: no demonstrated dedicated subskill. |
| 4 | Safe parallel-session repair | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `ssh`, `sshd`, `/etc/ssh/sshd_config`, `/etc/ssh/`, `Private and public key files`, `PermitRootLogin, PubKeyAuthentication, AllowUsers, PasswordAuthentication, Protocol`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 212.4 — Security tasks (exam 202, weight 3; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | Port/security testing | **Missing**: no demonstrated dedicated subskill. |
| 2 | Security advisory sources | **Missing**: no demonstrated dedicated subskill. |
| 3 | IDS deployment | **Missing**: no demonstrated dedicated subskill. |
| 4 | OpenVAS/Snort awareness | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `telnet`, `nmap`, `fail2ban`, `nc`, `iptables`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

### 212.5 — OpenVPN (exam 202, weight 2; missing)

| KKA | Skill | Evidence / scope |
|---|---|---|
| 1 | OpenVPN operation | **Missing**: no demonstrated dedicated subskill. |

**Breadth still to verify/teach:** Missing rows and the unpracticed official tool/file breadth remain; evidence rows are partial, never a complete-objective claim.

Official non-exhaustive tools/files/terms: `/etc/openvpn/`, `openvpn`.

Explicit bounded-practice terms: none individually credited. Tool presence, a filename mention or reading saved command output is not executed practice. The JSON links each mapped lesson to its guide, acceptance report, tests and exact SHA-256.

## Fidelity, prerequisites and applicability

- Simulator contract5 supports bounded literal text filters and declared reports, not a shell. No regex grep, sed, variables, expansions, subprocesses or live ip/dig/curl/systemctl. Its bytewise locale, record/newline, pipe and truncation subset is documented in [text contract](text-stream-contract.md).
- Contract3 virtual permissions teaches limited owner-bit repairs and entry/read evidence. It does not model user switching, chown, umask, ACLs or special-bit administration. [Permissions guide](lpic-unit-1.md) documents ls/cd differences and supported chmod forms.
- Contract4 regular-file navigation/find/cp/mv/rm is bounded; no recursion, links or arbitrary destinations. See [file-management contract](file-management-contract.md).
- VM process/Bash units require path/quoting/status basics. Admin/access/scheduling/recovery units assume deliberate guest-only sudo, exact identity/target checks and retained originals. Storage requires those safeguards; it is not a boot recovery environment.
- Offline networking/DNS/web snapshots complement live units but cannot replace real traffic, service deployment, credentials, TLS checks, mounted recovery or multi-host diagnosis. Better reasoning assessment would require an explicitly reviewed contract or a separately designed rubric; never pretend current keyword/byte checks supply it.
- GUI/desktop/accessibility topics require a suitable guest/platform and human assistive-technology practice. Native Qt automation is not certification of these skills.

## Evidence ledger

The JSON contains117distinct IDs with exact candidate content hashes and local content/guide/test/acceptance references. It records all378 official KKA rows. Existing acceptance is reused; no guests or full application suite were run for this audit. New focused document checks verify ID/path/hash/count/weight/subtopic parity. External runtime evidence remains in recovery directories, outside Git; availability of an acceptance report is not a claim that a new execution occurred.

See [completion program and exam summaries](lpic-completion-program.md), [warning diagnosis](shutdown-warning-diagnosis.md), and [later installed-app update](accepted-build-update.md).

## Review and verification of this assessment

Independent review confirmed the active exam IDs/counts/weights and transition,
378 KKA rows and117 content hashes. It corrected an omitted Btrfs-awareness row,
removed address-classification credit, BIND configuration credit from dig output,
SNI configuration credit from TLS excerpts and unsubstantiated connection-state
listing credit. Generic archive preparation is not source-build practice;
unsupported utility credits were removed. Guidance-any and guidance-only summary
fields are now distinct. This changed documentation mappings, not lesson bytes.

Focused verification: 20 workspace/storage/writer/retry/backup-failure tests and 5
existing documentation/content-preservation tests pass. 1,466 initial document,
ID/hash/path/weight/KKA/link checks pass; final checks and exact candidate hashes
are retained in the diagnosis recovery root. No unrelated full regression suite,
GNU comparison rerun, guest launch or native lesson rerun was performed. Existing
accepted native/installed lesson evidence is referenced at its original scope.
Physical keyboard, assistive technology and exhaustive native acceptance remain
outstanding. No warning suppression or claim of runtime repair is made.

## First completion-family evidence update

Ten Local Shell & Filesystem Administration lessons add partial link coverage and widen history, temporary editor/startup, find/FHS, sticky and scoped priority/audit skills. Exam101 remains **0 complete /19 partial /4 missing**; the other exams remain0/10/9,0/9/11 and0/6/15. No full objective or automatic guest assessment is claimed. [Unit guide](vm-preview/local-shell-unit.md) and [acceptance](vm-preview/local-shell-acceptance.md) separate new evidence from the original assessment-only checkpoint.

## Second completion-family evidence update

[Text & Archive Tools](vm-preview/text-archive-unit.md) adds eight lessons, for eleven units / 94 lessons. See [acceptance](vm-preview/text-operations-acceptance.md) for exact evidence. Active objective versions and whole-objective rollups remain unchanged: new practice widens partial 103.2/103.3/103.4; 105.2 and recovery are reinforcement. No automatic guest assessment, full coverage, xz or at claim. Earlier counts above are retained historical context.
