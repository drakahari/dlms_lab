# Platform and curriculum expansion: approval bundle

Planning checkpoint: **2026-10-11 America/Chicago /2026-10-12 UTC**, clean main
`90035155ffcd704ec1d5bc5e9171a01beb7bb99d`, live origin/main matched.
This proposal does not authorize its implementation. Existing **12 units/102 VM
lessons**, all old resources and exact pins remain unchanged.

## Recommendation

Approve one coherent block of **two units, 16–18 substantive lessons**:

1. **Locale, Encoding, Time & Offline Jobs** — ten proposed outcomes.
2. **RPM & Offline Package Administration** — eight proposed outcomes.

The implementation ceiling for this exact matrix is **14 units/120 lessons**.
Use fewer lessons if future native feasibility disproves an outcome; do not fill
missing skills with variations. Both environments remain offline, console-only,
2 vCPUs/2 GiB RAM/16 GiB raw base, with existing controller isolation and
self-reviewed, unscored completion. The [detailed lesson matrix](lpic-platform-expansion-plan.json)
contains every proposed ID, goal, prerequisite, Learn/Challenge task, negative
case, observable evidence and cleanup. It is planning data, not runtime content.

No new host package, engine, controller operation, network, authentication
credential, virtual disk, GUI session, profile migration or backup format is
needed for the proposed core. Fresh image preparation, packaged guest services,
guest-only policy exercises and bounded catalog expansion **do need approval**.
Do not update the working installation or silently route old lessons to new images.

## Curriculum reconciliation

The [comprehensive audit](lpic-comprehensive-audit.md) remains the shipped-coverage
record. Delivered lessons are not complete objectives. There are 83 active
objectives, plus removed 104.4 preserved separately. No whole objective has
comprehensive coverage. Current rollups:101 **0 complete/19 partial/4 missing**;
102 **0/10/9**;201 **0/9/11**;202 **0/6/15**. Eight simulator collections contain
41 distinct activities (38 Linux packs plus three networking labs), distinct
from the 102 real-guest lessons. No shipped live Exam202 service unit exists.

| Family | Delivered evidence | Useful remaining breadth |
|---|---|---|
| Local Shell: ten | Actual isolated Bash/history/editor, links/inodes, find/FHS model, sticky access and bounded priority; [guide](vm-preview/local-shell-unit.md) / [acceptance](vm-preview/local-shell-acceptance.md) | locate/updatedb, wider FHS, cross-filesystem links, global/skel customization, editor breadth and special-file/security breadth. Do not repeat link repairs just to add lessons. |
| Text & Archive: eight | Real descriptor routing, tee/PIPESTATUS, NUL xargs, join/comm, find grouping, cpio and partial archives; [guide](vm-preview/text-archive-unit.md) / [acceptance](vm-preview/text-operations-acceptance.md) | Actual xz/xzcat; wider filters/globs/recursive lifecycle and independent composition depth. Existing cpio does not prove arbitrary archives safe. |
| Accounts/Operations: eight | Alternate database consistency, actual cron ownership/results, timer failure/timeout, journal cursor/fields, private rotation, wall delivery and verified recovery; [guide](vm-preview/operations-unit.md) / [acceptance](vm-preview/text-operations-acceptance.md) | at and scheduler access changes; persistent/size-limited/offline journals; deliberate maintenance/login notices; authentication changes remain separate. |
| Next platform families | Read-only Debian/kernel/library/package work, current local shell and offline isolation | locale/encoding/timezone, RPM lifecycle, guest/cloud concepts; GUI/accessibility/printing/mail; boot/kernel/storage/network administration separately. |

These units add **limited new107.3 practice, at breadth within108.2,
xz breadth within103.2/103.3 and RPM/DNF breadth within102.5**. Timezone
configuration can add the timezone subskill of108.1; it does not establish clock,
RTC or NTP administration. LPIC-2 206.2 appears only as reinforcement; this block
adds **no new comprehensive LPIC-2 objective coverage**. Source builds206.1,
maintenance notices206.3, kernel/boot and real network services remain genuine
later gaps. The owner’s LPIC-2 goal is preserved; rushing those into this
platform block would require additional tools or infrastructure decisions.

Official sources checked: [LPIC-1 active5.0 /101-500,102-500](https://www.lpi.org/our-certifications/exam-101-102-objectives/),
[LPIC-2 active4.5.0 /201-450,202-450](https://www.lpi.org/our-certifications/exam-201-202-objectives/).
LPI’s [2025 annual review](https://www.lpi.org/wp-content/uploads/2026/03/2025_LPI-AnnualReview.pdf)
mentions2026 LPIC-2 updates, but [LPIC-2 v5](https://wiki.lpi.org/wiki/LPIC-2_Objectives_V5.0)
is still labeled draft in the checked sources. Those sources did not supply a
dated launch/retirement transition. Recheck before implementation; retain active
mappings, do not silently reinterpret existing objective numbers. This is
original preparation content, not exam questions, full coverage or endorsement.

## Demonstrated existing capabilities versus proposals

See [sanitized feasibility evidence](vm-preview/platform-feasibility.md).
Existing guests already contain `locales`, `locale`, `localedef`, `iconv`,
`en_US.utf8`, C/C.utf8 and locale source data. Strict UTF-8/ISO-8859-1 round-trip,
unrepresentable ASCII and invalid UTF-8 failures were exercised with temporary
files. Fixed winter/summer UTC instants display the expected New York/Berlin
DST offsets; inspecting timedatectl does not change clocks or NTP.

`xz`, `at`, `mesg`, `write`, compilers/make/patch, RPM and DNF are not available
in these tested guests. Debian13 **removed mesg/write**, not merely an optional
package split: [Debian maintainer record1088011](https://bugs.debian.org/1088011)
and [Trixie changes](https://wiki.debian.org/NewInTrixie). Do not downgrade
util-linux, copy old binaries or re-enable setgid helpers to claim these skills.
Defer those platform-specific tools. Existing wall practice remains valid.

Non-English locale generation, persistent locale/timezone edits, new at jobs,
RPM transactions and the new image boot are **future acceptance requirements**,
not established by these read-only probes. No package/service/policy/clock change
was made during planning. Package-page versions and ISO contents are metadata
observations, not demonstrated RPM guest behavior or authenticated build pins.

## Proposed lessons at a glance

Every row is **proposed**, not an implemented lesson. Detailed independent
Challenge, negative case, evidence and exact cleanup requirements are in the
[machine-readable matrix](lpic-platform-expansion-plan.json). Learner completion
remains self-reviewed; developer acceptance must verify actual outcomes.

| Unit / sequence | Lesson | Skill and active subtopic | Evidence required |
|---|---|---|---|
| 1.1 | Choose the locale scope deliberately | 107.3 locale environment; 103.1 variables: reinforcement | Before/child/parent locale output, statuses, byte-exact system-default snapshot, explanation of category precedence. |
| 1.2 | Compare localized formats without corrupting data | 107.3 non-English localization and LC_*; 103.2 sorting: reinforcement | Actual locale availability, category output, retained byte-level input/output and tested sorting interpretation. |
| 1.3 | Convert text strictly and preserve a recovery path | 107.3 iconv/encoding terms | Input hashes, byte counts/od, status/error, independent expected bytes and successful round-trip where representable. |
| 1.4 | Make a guest locale default reversible | 107.3 locale configuration; 105.1 environment: reinforcement | Protected before copy, exact changed fields, real fresh-session locale and successful byte/mode/owner rollback. |
| 1.5 | Interpret timezones without changing the clock | 107.3 timezone configuration/TZ; 108.1 timezone subskill only | Fixed-instant offsets, original/final localtime link or bytes, monotonic/epoch observations, timedatectl fields, rollback. |
| 1.6 | Inspect an xz stream and recover exact bytes | 103.2 xzcat; 103.3 xz/unxz; 206.2 reinforcement | Source hash, compressed/list/check status, bounded resource options, rejected-copy evidence, restored-byte comparison. |
| 1.7 | Inspect and cancel the exact one-off job | 108.2 at/atq/atrm | Queue ID/owner/time/body hash before/after, absence of cancelled output after its deadline, foreign job preserved. |
| 1.8 | Prove a one-off job’s environment and result | 108.2 at execution; 105.2 status: reinforcement | Actual job UID/cwd/umask, exact bytes/status, failed job retained, 6s child timeout and <=150s observation deadline. |
| 1.9 | Test scheduler access as the intended identity | 108.2 at access controls | Exact policy bytes/modes/owner, queue/run denial and successful UID evidence, unaffected learner/auth/sudo fingerprints. |
| 1.10 | Deliver a localized offline job handover | 107.3 and108.2 independent transfer; no new objective credit | Facts, units/zone/encoding, job identity/status, original preservation, rejected hypothesis and self-review answers. |
| 2.1 | Identify RPM package state and file providers | 102.5 installed metadata/file-provider; DNF awareness | Actual tool versions, NEVRA, file ownership/provider and metadata; unrelated package list unchanged. |
| 2.2 | Inspect an offline RPM before admitting it | Partial102.5 uninstalled metadata, contents and dependencies | Inspected payload paths/modes/owners, absence of scripts/triggers, exact external hashes and internal digest results. The project fixtures are unsigned; no signer/authenticity or rpm2cpio practice is claimed. |
| 2.3 | Observe a dependency failure without forcing installation | 102.5 RPM install/dependencies | Solver/transaction errors, unchanged full unrelated RPM inventory and fixture state, exact required version. |
| 2.4 | Resolve the offline fixture dependency explicitly | 102.5 DNF awareness/dependency frontend; modern YUM compatibility limitation | Exact versions/actions, plan refusal, execution status, expected files and before/after all nonfixture packages and policy. |
| 2.5 | Retain edited configuration during an RPM upgrade | 102.5 upgrade/reinstall lifecycle | Versions, original/config/new candidate hashes, owners/modes and expected package-owned contents. |
| 2.6 | Repair package-owned contents with independent verification | 102.5 integrity/reinstall | Actual rpm verification before/after, reference comparison, intended unprivileged-user read/result, unchanged other packages. |
| 2.7 | Remove only intended packages and explain retained files | 102.5 RPM removal | Dependency refusal, exact erased identities, retained configuration/content and byte-identical nonfixture inventory. |
| 2.8 | Repair an offline package incident and hand it over | 102.5 transfer; no claim of full objective or Zypper/YUM mastery | All intended fixture outcomes, negative-plan refusal, exact versions/file bytes/access and unchanged unrelated package/guest policy. |

No row claims a full objective. Timezone display/configuration does not teach
clock synchronization; DNF is not legacy YUM or Zypper. Recovery/handover rows
transfer prior skills and receive no additional objective credit.

## Fresh foundational Debian image

Proposed new ID: `debian13-foundation-admin-local-v1`; version/recipe1. Build
independently from the existing verified Debian13.7 DVD input, using the
**corrected package-image recipe’s separate finalization**, not a used overlay
or the older administrator late-command inventory. Base policy: finalized204
packages from `tools/vm_image/packages/expected-packages.tsv`, omit Discovery
fixtures, preserve old images and their supplemental provenance. The older administrator
base has a separately documented finalized 216-row inventory; its original
204-row descriptor history is not rewritten by this proposal. Use the corrected
204-row recipe as the new-build starting point, not that older late inventory.

| Proposed package/version | Purpose and direct dependencies | Service/policy effect |
|---|---|---|
| `xz-utils=5.8.1-1+deb13u2` and `liblzma5=5.8.1-1+deb13u2` | xz/xzcat; libc6>=2.34, liblzma>=5.6.2. Deliberate new-image security-library revision from retained u1, not an old-image upgrade | No daemon; inspect exact archive modes/notices |
| `at=3.2.5-2.2` | Queue/execution. libc6>=2.38, libpam-runtime>=1.0.1-11, libpam0g>=0.99.7.1, libselinux1>=3.1 and lsb-base>=3.2-14 | New guest atd service/spool, packaged helper permissions and `/etc/pam.d/atd`; inspect all scripts/account/group effects before build |
| Retain `sysvinit-utils=3.14-4` | Exact retained .deb control provides `lsb-base (=11.1.0)`, satisfying at's versioned dependency; no new `lsb-base` binary required | Existing base policy retained |
| Retain `locales/libc-l10n/libc-bin/libc6=2.41-12+deb13u4`, `tzdata=2026c-0+deb13u1` | Already available; generate only en_US.UTF-8 and de_DE.UTF-8 at build time | Reversible guest default-locale/timezone exercises; no clock/NTP changes |

Existing direct at dependencies are already in the204-row inventory:
libpam-runtime/libpam0g1.7.0-5, libselinux1 3.8.1-1,
sysvinit-utils3.14-4, libc6 2.41-12+deb13u4. Read-only inspection of the retained
DVD binary, matched to its package-metadata hash, resolved the lsb-base provider:
`sysvinit-utils` provides version11.1.0. Proposed final policy is **206 rows**:
204 retained rows plus xz-utils and at, with the approved liblzma5 row updated.
**Authenticate and freeze the exact closure before building**, including
Recommends disabled. Stop for any other added/replaced package or substitute
version. No default-MTA recommendation, mail delivery promise or automatic upgrade.

[Official xz package](https://packages.debian.org/trixie/xz-utils),
[liblzma](https://packages.debian.org/trixie/liblzma5),
[at](https://packages.debian.org/trixie/at),
[locales](https://packages.debian.org/trixie/locales),
[lsb-base](https://packages.debian.org/trixie/lsb-base),
[tzdata](https://packages.debian.org/trixie/tzdata).
These proposed version pins still require authenticated InRelease→Packages/Sources
hash validation in a non-overwriting acquisition directory after approval.
Retain exact .deb/control/copyright, .dsc/upstream/Debian patches, signatures,
Built-Using/Static-Built-Using closure and all existing base notices. Official
at notices include GPL2+/GPL3+/ISC; xz contains 0BSD and additional component
licenses. Do not relabel everything MIT or equate a generic source link with closure.

Atd may be enabled **inside this new disposable guest only**. No cron/systemd
changes on the host. Initial queue empty; named test identities have locked
passwords/non-login shells and only declared scheduler permissions. Existing
console-only learner autologin, locked root/learner passwords and
`learner ALL=(root) NOPASSWD: ALL` remain the guest model. Approval must explicitly
cover new packaged at helper/spool/PAM definitions and reversible at.allow/deny
exercises, not general password/PAM/sudo editing. Root can override guest limits.
All jobs use `at -M`, bounded explicit output and exact owned IDs; no MTA,
network or load-sensitive `batch` workload is needed.

Acquire inputs on the host in a dedicated preparation directory, authenticate
without executing downloads, and deliver to a **build-only** guest via existing
approved preparation tooling. No runtime guest NIC/download, shared HOME or
app-controlled lesson execution. Finalizer must complete installer/hardware
steps, verify exact package/service/account policy, clear fresh build state,
shutdown fully and only then hash/register immutable base and exact descriptor.
Repeat a normal-boot inventory comparison before lesson acceptance. This is a
repeatable recipe; byte-for-byte image reproducibility is not claimed.

Size estimate, **unmeasured**: incremental guest files about5–25MiB (xz/at plus
two compiled locales); full occupied raw disk about1.5–3GiB, compressed bundle
0.6–1.2GiB. Current enforced logical base16GiB,2GiB RAM/2vCPU unchanged. Reserve
>=1GiB guest free space and>=80GiB host admission during preparation; retained
overlays can grow and neither observation guarantees a reserve/quota.

## Separate RPM environment

Recommend **AlmaLinux9.8 x86_64 minimal ISO**, proposed
`almalinux9-rpm-admin-local-v1`, rather than a cloud-image adaptation or network
installer. Its official [release notes](https://wiki.almalinux.org/release-notes/9.8)
and [installation guide](https://wiki.almalinux.org/documentation/installation-guide)
support self-contained offline installation and BIOS. Documented minima1.5GiB
RAM/10GB disk plausibly fit the approved2GiB/16GiB configuration, but actual
VGA/tty1 boot, memory, storage and poweroff remain future gates. Do not enlarge
launch resources or switch firmware silently if it fails.

Official directory metadata observed the exact ISO filename
`AlmaLinux-9.8-x86_64-minimal.iso`, **2,838,495,232 bytes**. The55,455-byte
ISO contents manifest lists:

- rpm/rpm-libs/rpm-build-libs/python3-rpm **4.16.1.3-40.el9**;
- dnf/dnf-data/python3-dnf/yum **4.14.0-34.el9_8.alma.1**;
- libdnf/python3-libdnf **0.69.0-18.el9.alma.1**;
- sudo **1.9.17p2-3.el9_8**; util-linux **2.37.4-25.el9**.

These are proposed frozen-media selections, **not a finalized image inventory**.
Do not follow mutable9-latest URLs or take newer repository sudo versions as the
ISO version. Download only after approval; authenticate CHECKSUM against the
independently cross-checked official Alma9 fingerprint
`BF18AC2876178908D6E71267D36CB86CB86B3716`, then exact ISO hash; inspect signed
RPMs and repository metadata. Record selected NEVRA and complete solver closure
before installing a minimal raw guest. Keep SELinux enforcing and contexts;
exclude/disable SSH, cloud-init, remote login, networking, guest agent and kdump
according to a reviewed package/service selection. Do not disable SELinux to
fix an autologin or fixture failure. Locked passwords, tty1-only learner
autologin and guest-only sudo policy need native acceptance on this new distro.

Fedora44 ordinary Cloud or Server DVD were considered: current RPM6/DNF5 add
unnecessary version-specific solver/console preparation for this first unit.
Cloud can be smaller but needs provisioning cleanup and truthful source-image
provenance; UKI is not a legacy-BIOS substitute. This is a choice of a bounded
teaching environment, not a promise that Alma is the smallest possible disk.

Use **two project-owned noarch identities/three archives**:
`ll-rpm-data`1.0-1 and2.0-1, `ll-rpm-report`1.0-1 requiring exact data2.0-1.
Data payload under `/usr/share/learning-lab-rpm/`, one
`/etc/learning-lab-rpm/report.conf` as `%config(noreplace)`;
report is a small ordinary executable script under `/usr/bin/ll-rpm-report`.
No maintainer scripts, triggers, services, accounts, links, capabilities or
privileged bits. Retain full spec/source/notices/expected-byte manifest protected
from ordinary learner writes, not guest root. Fixtures start uninstalled.

Noarch RPM building still requires rpmbuild and its exact dependency closure.
Use a separately approved disposable **build-only** environment with matching
rpm-build4.16.1.3-40.el9 (listed in the official9.8 AppStream metadata) and
frozen-media/source inputs; do not install tools on
the host or sneak build dependencies into the learner base. Inspect build
postprocessing/requires generation and prove archive reproducibility by two
independent builds before claiming it. Acquire missing builder dependencies
only from authenticated exact metadata, stop for unlisted versions.

Fixture archives can stay **unsigned**, with independently reviewed/hash-pinned
local payloads. Approve only a per-command localpkg_gpgcheck exception for these
exact project archives, not broad `--nogpgcheck`, disabled official-repo checks
or generated keys. A retained official signed package may be inspected against
the existing vendor public key without installing it. No project signing
credentials or production image admission in this block.

Preview and execution must share root identity, fixed config, C locale, local
paths, disabled repositories/weak dependencies/autoremoval. A fixed trusted
**guest fixture helper**, visibly invoked by the learner, resolves and validates
all package actions/version/architecture against the two identities using the
pinned DNF4 API, then runs the same resolved transaction. Stop if exact solver
changes cannot be inspected/bounded; CLI `--assumeno` text alone is insufficient
when ambiguous. No arbitrary lesson JSON execution, host API or controller change.
Retain before/after all nonfixture packages, learner/groups/sudo policy and
configuration; reject extra/removal/downgrade/replacement actions. No force,
`--nodeps`, autoremove, network repositories or generic repair/undo command.

The eight-lesson unit teaches **RPM and modern DNF**. Alma’s yum frontend must be
probed, and is not evidence of original YUM implementation. **Zypper requires a
separate SUSE environment**; DNF5 also needs version-specific treatment.102.5
remains partial. RPM erase/config retention has no generic Debian-style purge.

Retain exact source RPMs, specs/patches, license files and redistributable source
for every installed package plus builder inputs, with signature/hash inventory.
[Alma EULA](https://git.almalinux.org/rpms/almalinux-release/src/branch/a9/EULA)
does not replace individual package licenses or branding requirements. Describe
the modified guest truthfully as Learning Lab prepared from AlmaLinux, not an
unmodified official image. Qt/ICU and existing image obligations remain separate
release blockers. No public publication is approved.

**Unmeasured estimates**: prepared occupied base1.5–3.5GiB, compressed0.7–1.5GiB,
source closure several GiB; logical16GiB and2GiB RAM unchanged. ISO size above
is observed metadata, not a download measurement. Retain >=80GiB host free at
admission and >=1GiB guest free; assess source/builder/overlay use before build.

## Capacity and compatibility design

Proposed exact maxima: units**12→14**, total**102→120**, retained lesson
revisions**102→120**, both default lesson/image maps**102→120**. Keep16 per unit,
64 compatible revisions per image,64 catalog images/keys/releases,64 KiB JSON,
8,192 nodes/depth 32, 4 KiB text and existing step/hint/resource limits. Existing
compatibility counts44 unprivileged/50 administrator/8 each package revision
remain unchanged; new Debian/RPM images get10/8 exact pairs, not wildcard access.

The current catalog is62,885 bytes/1,113 nodes/depth5. Deterministic compact JSON
is52,087 bytes with unchanged parsed descriptors/canonical digests. The proposed
18-lesson/two-image projection is recorded in the machine plan; pretty JSON
exceeds64KiB but compact fits with about3.5KiB headroom. **Do not raise parser
limits**. Final serializer output must be <=64KiB, retain at least2KiB headroom,
and verify parsed-value equality and all old digests. If descriptors/provenance
or retained revisions exhaust that budget, stop for a catalog-specific design
decision rather than extending untrusted manifest/session limits.

Test120 accepted/121 rejected,14units/15 rejected,16 per unit/17 rejected;
retained/default maps120/121, per-image64/65; byte boundary65536/65537,
nodes8192/8193,depth32/33. Synthetic maximum fixtures must test each independent
bound, not let a different early refusal masquerade as coverage. The catalog
has the generic node/depth walker. Registry resources share the
64KiB byte ceiling and duplicate-key rejection, with separate typed field,
text, step and hint bounds; they do not currently use that generic walker.
Ensure every final unit/lesson resource fits its actual validator. Catalog
compaction changes whitespace only and does not migrate storage.

Old lessons keep exact resource bytes, canonical revisions and per-lesson
image mappings; old sessions resolve pins through retained descriptors, never
new defaults. Missing/mismatched/resume-only/withdrawn semantics and verified
Stop remain unchanged. Update default maps only for new IDs. Application
rollback can load old pins but cannot promise to understand newly introduced
IDs/descriptors absent from its packaged registry; retain the new app build and
images to access new sessions, do not silently migrate disks to old images.
VM sessions/disks remain excluded from profile backup; application progress
backup format unchanged. Core simulations remain usable without any VM image/QEMU.

## Reviewable implementation order and acceptance

1. **Freeze exact inputs/closures and capacity fixtures.** Authenticate metadata,
   inspect package effects/source obligations and image policy before builds.
   No newer-version substitution. Preserve102 old resource/descriptor hashes.
2. **Independently prepare images and fixture archives.** Finish installer and
   dedicated finalizer before inventory/hash. Normal-boot compare finalized
   inventory; verify no NIC/shares/listeners/SSH, locked accounts, sudo, SELinux,
   guest services and readonly bases. Inspect each RPM payload and reproducibility.
3. **Native tool/permission/solver feasibility.** Actual non-English locale,
   timezone rollback, xz limits/corruption, at cancel/environment/identities/PAM
   distinctions and exact RPM dependency/config/verification/recovery outcomes.
   Use existing controller and shared exclusion; failure stops dependent lessons.
4. **Register two units and implement reviewed display-only content.** Every
   lesson in Learn and independent Challenge, positive/negative/incomplete cases,
   repeated/interrupted cleanup and original preservation. No automatic-score claim.
5. **Consolidated gates on final hashes.** Full regressions/GNU comparisons;
   old pins/session loading, missing images, default maps, boundaries;
   native Start/verified clean Stop/separate-process reopen/same-disk Resume/
   retained Reset/cross-profile refusal and owning Stop. Actual installed wheel
   outside checkout. Compact/wide100/150/200% navigation/instructions; independent
   coverage/safety review. Physical-input/accessibility gaps remain explicit.
6. **Coherent reviewed commits/push only if separately authorized for that
   implementation.** No working-installation update or release by implication.

Common practice bounds: unique guarded private workspace, small manually
enterable fixtures, source<=64KiB, aggregate private output<=1MiB,1GiB free-space
admission, child jobs<=6s and output<=64KiB, observation<=150s, exact IDs/paths
and preflighted cleanup. Build/at daemon/root policy limits are distinct from
cooperative exercise guards; guest root can override guest-side restrictions.
No tests against owner guests or host files; preserve every failed candidate.

## Single approval checklist

- [ ] Independent Debian foundation image using corrected finalized recipe and
  exact package changes above; generate two locales; atd/service/spool/helper/PAM
  package effects inspected; no MTA/network/automatic upgrade.
- [ ] Reversible **guest-only** locale/default/timezone changes and at.allow/deny
  fixtures; locked named practice identities, unchanged learner/sudo/PAM login
  policy. No clock/RTC/NTP writes, passwords or credentials.
- [ ] Independent Alma9.8 minimal-ISO guest under unchanged BIOS/VGA/resources,
  console autologin/locked passwords/guest sudo, SELinux enforcing; freeze exact
  selected package/service/dependency inventory before build. No SSH/kdump/NIC.
- [ ] Separate bounded RPM fixture builder, exact dependencies inspected before
  use; two identities/three inspected archives and trusted fixed guest transaction
  helper, narrow unsigned-local-fixture exception, no production signing keys.
- [ ] Two units/up to18 distinct lessons; exact14/120/16 registry, retained/default
  bounds120, deterministic compact catalog under unchanged parser limits.
- [ ] Disposable native tests and retained evidence under existing shared
  coordination; preserve all old resources/pins/images/attempts. Stop for a new
  controller/QMP/launch/storage/backup/network requirement.

Unresolved inputs requiring a checkpoint, not blanket discretion: authenticated
Debian closure matching the verified provider; selected minimal Alma package/
fixture-builder closure; actual at PAM/service behavior and RPM solver API;
final serialized resource size.
Approve the named policy/version set, then freeze these derived closures before
building; escalate any additional capability or version substitution.

## Fallback and later decisions

If image expansion is declined, recommend **four existing-image lessons** only:
locale scope/C versus UTF-8, strict byte conversion, fixed-instant TZ/DST evidence,
and an independent encoding/time handover. Four new lessons still need a bounded
13-unit/106 retained/default expansion and serialized-size check; no persistent
locale/timezone or scheduler changes are implicitly authorized. This is useful
107.3 preparation/partial practice, not the larger platform unit.

GUI/X11/Wayland/accessibility/remote desktop need a separate environment and
native assistive-technology testing. Time synchronization/RTC/clock mutation,
printing/MTA, mesg alternatives, original YUM/Zypper, source builds/compiler,
clone identities/cloud-init, boot/storage/disks, network/client-server service
units and any automatic assessment are separate approvals. No new credential,
production image key, network listener or multiple-guest controller is needed
now. Source builds206.1 and deliberate notices206.3 are sensible next offline
LPIC-2 candidates after this foundation, with their own package/fixture approval;
boot recovery remains separate. Public release and UI polish remain deferred.

## Implementation mapping correction

On2026-10-12 the official active5.0 objectives were rechecked: one-off
scheduling is108.2, not107.2 (X11). The new runtime lessons use108.2. This
corrects planning tags only; no accepted existing lesson bytes or pins changed.
