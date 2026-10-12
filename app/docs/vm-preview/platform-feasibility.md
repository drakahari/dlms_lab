# Platform feasibility: disposable guest evidence

Planning-only inspection on **2026-10-11 America/Chicago /2026-10-12 UTC**,
baseline `90035155ffcd704ec1d5bc5e9171a01beb7bb99d`. No existing lesson, runtime code,
image, installed application or owner profile was changed. Disposable runtime
records and overlay disks were created and retained separately.

## Results and boundaries

Two sequential disposable guests passed **18 checks**: six tool/version/locale/
encoding/time/read-only-policy checks, exact temporary cleanup, normal Stop and
unchanged base hash for each. These are capability probes, not acceptance of
the proposed new lessons or package environments.

| Existing image | Exact raw SHA-256 | Representative unchanged lesson binding | Result |
|---|---|---|---|
| debian13-jobs-local-v1 | `a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d` | real-linux-textarchive-streams | PASS, 398.91s |
| debian13-admin-local-v1 | `f956d5c98848296f6887235c742ee4cc44ed5981acd0d2efd0a593b16d8a578f` | real-linux-operations-journalcursor | PASS, 398.74s |

The existing native harness/controller checked the exact task-owned process,
session and generation before console input. Each guest used a new disposable
profile and an overlay over a verified read-only copy under the recovery root.
Shared exclusion was acquired normally; no owner guest was active beforehand.
Final reliable `/proc` inspection found no QEMU-system executable processes,
and normal shared coordination reported `stopped`. No lock/record was removed,
force Stop used, or failed operation treated as permission to bypass exclusion.

## What actually ran

- `command -v` checked 33 named tools. Both guests have locale/localedef/iconv,
  date/zdump/timedatectl, wall/script/cpio. xz/xzcat, at/atq/atrm, mesg/write,
  hwclock/chronyc/ntpq, compiler/build tools, RPM/DNF/YUM/Zypper, locate/updatedb,
  mail and printing commands were unavailable in the learner's environment.
  Lookup absence is not a claim about every possible root search path.
- Locale enumeration showed C, C.utf8, en_US.utf8 and POSIX; en_US locale source
  and the compiled archive were inspected. UTF-8, C's ASCII charmap and category
  overrides were queried. Generating de_DE.UTF-8 was **not** attempted.
- Tiny UTF-8 `café` bytes converted to independently specified ISO-8859-1 bytes
  and back exactly. Strict ASCII conversion rejected the unrepresentable
  character; invalid UTF-8 `0xff` was rejected. Error/status and partial outputs
  were retained until inspected. No transliteration or ignored errors.
- Fixed UTC instants were displayed without setting time: New York Jan15 noon
  UTC →07:00−0500 EST, Jul15 →08:00−0400 EDT; Berlin →13:00+0100 CET and
  14:00+0200 CEST. `timedatectl` reported Etc/UTC, LocalRTC=no, NTP=no and
  NTPSynchronized=no. These facts do not prove synchronization or clock accuracy.
- Installed package queries agreed with retained inventories for glibc
  2.41-12+deb13u4, tzdata2026c-0+deb13u1 and util-linux2.41.5-0+deb13u1.
  Source-only residual dpkg rows were not classified as installed tools.
- Read-only control inspection of retained, hash-verified
  `sysvinit-utils_3.14-4_amd64.deb` showed `Provides: lsb-base (=11.1.0)`,
  satisfying at's declared >=3.2-14 dependency without a new lsb-base package.
  This reuses authenticated DVD evidence; fresh package acquisition remains a
  future verification gate.
- `/etc/localtime`, `/etc/passwd` and `/etc/group` hashes stayed unchanged;
  `/sys/class/net` contained only lo. Probe code performed no package, service,
  policy, timezone, clock or authentication writes.
- A learner-owned mode0700 temporary directory contained exactly15 known
  regular files. Enumerated members/types/ownership and private path shape were
  checked before exact file deletion/rmdir. No recursive deletion, host share,
  network or learner-command execution on the host was used.

Persistent locale/timezone changes, at/PAM access and execution, RPM behavior,
the proposed images and their resource estimates remain future acceptance gates.
Console automation is not physical-keyboard, wheel/trackpad or accessibility
acceptance. No UI alteration was made; accepted native/UI evidence was reused
only for unchanged behavior. The diagnosed shutdown warning remains unchanged.

## Retained failures and recovery

The first copy attempt used incompatible GNU cp reflink/sparse options and
refused before copying; it was corrected to reflink=always/sparse=auto. The
first controller preflight then correctly refused a newly created private root
with mode0755; no guest started. Only the new disposable roots were corrected
to0700. Both failures and the rejected run remain retained; neither is counted
as a passing probe. A post-run read-only diagnostic imported a nonexistent
registry symbol and was corrected to direct `/proc`/coordination inspection;
it made no controller or guest change.

Recovery and raw evidence are outside Git:

`/home/drak/.local/state/omarchy-learning-lab/recovery/platform-plan-20261012T011629036827Z`

The recovery snapshot contains549 byte-verified tracked source files, initial
Git metadata reports, verified base copies, failed candidates and both actual
guest logs/screenshots. Personal profiles were not copied. The successful run
is `foundation-live-94publcz`; [sanitized evidence and exact hashes](platform-feasibility.json)
identify its report, events, static developer probes and captured console
outputs. Raw process inventories, disks, profiles, frames and runtime records
are excluded from source commits and preserved locally.

Official bounded metadata downloads (not executable packages or new images)
are retained separately with hashes. Alma9.8 ISO manifest entries and Debian
package pages are proposed input evidence, not locally authenticated build
inputs. Image acquisition, full source closure and native acceptance require
approval and subsequent verification.

## Final planning checks and independent review

- **25 focused existing catalog/foundation tests passed**, 4.043s: current
  boundaries, legacy resource/pin preservation and exact default routing.
- All549 recovery source copies reverified;548 existing tracked files unchanged.
  The only changed existing file is the approved completion-program appendix.
  All102 lesson pins resolve against unchanged resources; production keys and
  releases remain empty. Original and private-copy raw base hashes all match.
- Proposed18 IDs/lesson fields, active-objective references, local links,
  capacity arithmetic and retained evidence/metadata hashes passed consistency
  checks. Catalog-size estimates are synthetic, not admission of new images.
- Independent review found no substantive blocker. Corrections clarified the
  actual33 tools, metadata hash root, disposable-state distinction and advancing
  clock semantics. Exact retained lsb provider inspection narrowed the proposed
  package closure. Package builds, new services/policies, RPM solver behavior and
  proposed lesson acceptance remain explicit future gates.

No repeated full application/GNU/native/wheel suite was used as a substitute for
planning evidence; unchanged accepted results were not relabeled as new runs.
The working installation, owner profiles and accepted lesson/controller/image
resources are preserved.
