# Services, Logs & Safe Recovery: implementation evidence

## Inventory erratum (2026-10-06)

Independent review found **216 actual installed packages**, not the early recorded 204. Twelve were added by a later Debian Installer hook; ten additional source versions are absent from the retained closure. Historical statements of complete package/source inventory below are superseded. Behavioral test results do not establish that closure. The existing administrator disk, descriptor, policy and pins are unchanged. See [provenance erratum](admin-image-provenance.json) and [finalization analysis](package-image-provenance.json). Separate remediation must preserve existing sessions; this task does not replace their image.

Baseline `bbb19d7eb94d49bd70c49e117ec2ffd2b46b5972` was clean before editing.
The 32-file batch was reviewed for the authorized local commit. Existing local
commits are preserved; there was no push, working-installation update or
real-profile migration.

## Recovery and retained artifacts

Verified source snapshot, 326 tracked files:
`/home/drak/.local/state/omarchy-learning-lab/recovery/admin-unit-source-20261005T004759047304Z`.
All snapshot hashes were rechecked. No personal profile was copied.

Build, source/notices inventories, failed tests and disposable runtime:
`/home/drak/.local/state/omarchy-learning-lab/recovery/admin-unit-build-20261005T004827Z`.
The runtime is its `runtime/` directory. No original proof disk/practice overlay
was used to build the new image. Existing images and sessions remain separate.
All native fixtures use ordinary shared exclusion and verified process identity;
no coordination record was removed to permit a launch.

## Fresh administrator image

- Debian 13.7.0 amd64 DVD-1, independently rehashed and its signed checksum
  reverified. ISO SHA-256:
  `347b6c67a3cc0b7ddb60b178f683470c4e2b7ac426c996d9337a2ff36c1a32d2`.
  Debian CD signer: `DF9B9C49EAA9298432589D76DA87E80D6294BE9B`.
- Source build: `guest-build/prepared.raw`; registered copy:
  `runtime/images/f956d5c98848296f6887235c742ee4cc44ed5981acd0d2efd0a593b16d8a578f/base.raw`.
  Both are read-only 16 GiB raw files. Raw SHA-256:
  `f956d5c98848296f6887235c742ee4cc44ed5981acd0d2efd0a593b16d8a578f`.
- Exact descriptor SHA-256:
  `dcbdec81fc5aab2b775168cde1a350364ec8e017e67d1c25e1035f74cc8fb25d`.
  The original unprivileged descriptor/base remains unchanged.
- 204 exact installed binaries, compared with 199 in the original image. Added:
  sudo `1.9.16p2-3+deb13u2`, rsyslog `8.2504.0-1+deb13u2`, libestr0 `0.1.11-2`,
  libfastjson4 `1.2304.0-2`, liblognorm5 `2.0.6-5`.
- All binary hashes and copyright notices checked against the authenticated DVD;
  194 corresponding source versions, including incorporated-source requirements,
  verified against signed Debian main/security source metadata. Exact archives
  and notices are retained outside Git, including previously retained matching
  artifacts referenced read-only. No downloaded source/build script was executed.
  See [versions](admin-packages.tsv), [provenance](admin-image-provenance.json),
  `guest-package-inventory.json` and `source-inventory.json` in the evidence root.
- Build payloads `preseed.cfg` and `finish-image.sh` match their executed hashes.
  `guest-build/build.json` records the actual QEMU invocation. After that successful
  build, the developer builder explicitly retained its lifetime lease with QEMU
  `-add-fd`, matching the established runner mechanism, and closed a directory-fsync
  descriptor. These host-envelope edits do not change the executed guest payload;
  interrupted developer-builder recovery is not claimed as a new acceptance result.
- This is a local development build, not a production release or a demonstrated
  byte-for-byte reproducible image. Production keys and release allowlists remain
  empty. Source retention is not blanket redistribution clearance.

## Scope and compatibility

The only runtime Python changes are the explicit trusted per-lesson default-image
map and aggregate registry bound (16 → 24). Limits remain four units and sixteen
lessons per unit; currently three units each contain eight lessons. Mapping must
be complete and refer to exact compatible descriptor/lesson digests. Legacy
catalogs retain their previous behavior. Missing or incompatible images fail
without substitution, including substitution of the privileged image.

All sixteen original lesson files, original unit files, image descriptor, order,
canonical pins and special background-job session binding are preserved. The
controller, runner, launch policy, process/QMP checks, filesystem/publication
checks, session/generation formats, backup formats, simulated engines, scenario
packs, collection resources and QML are byte-identical to baseline.

Each new lesson remains display-only. Learn/Challenge records stay separate;
completion is explicitly self-reviewed and has no verification score. Guest
reports/files/VM sessions and disks remain excluded from profile backup/export.
Resume boots the disk; it does not restore RAM, shell variables or jobs.

The learner is unprivileged at console login and has the approved exact rule
`learner ALL=(root) NOPASSWD: ALL`. Root/learner passwords and the non-login
`ll-service` account are locked. Dedicated lab workers use that service user,
120-second runtime, 64 MiB memory, eight tasks, 20% CPU, 1 MiB file limit and
five-second stop timeout. Guest root can override all guest-side limits. Standard
guest services retain Debian's normal privileges; those worker limits are not
claimed for journald/rsyslog. No NIC, SSH, host shares or clipboard integration.
This is not isolation against hostile malware.

## Verification

Runtime: Python 3.14.7, PySide/Qt 6.11.2, existing QEMU 11.1.1. No host package,
service, group, security setting or desktop setting changed.

| Check | Result / retained evidence |
|---|---|
| Full regression suite | **521 passed**, `/tmp/admin-final-review-regressions-approved.log` |
| Static GNU references | **44 passed**, `/tmp/admin-final-review-gnu.log`; developer fixtures only |
| Final native Wayland UI | **227 checks per scale**, 100/150/200%, actual 800×600 and 1280×900 logical windows, zero QML warnings; `/tmp/admin-unit-native-ui-{1,1.5,2}.log` |
| Offscreen UI | **227 checks per scale**, final 100/150/200% matrix at both sizes; `/tmp/admin-unit-ui-final-{1,1.5,2}.log`; distinct from native acceptance |
| All eight guest lessons | **16 lesson/mode passes**, 96 controller checks; `native-lessons-aggregate.json` verifies each retained origin against final exact pins |
| Wheel build/install | Actual wheel in `package-reviewed/`, separate venv, `pip check`; 139 source/wheel/installed application/resource files match, including all 24 lessons and current notices; no checkout/examples import |
| Installed offscreen smoke | Pass, `package-reviewed/installed-smoke.log`; resources, simulated scenarios, authoring and all VM metadata modes/reopen, with no VM boot claim |
| Additional guest safety/lifecycle | **10 checks passed** plus actual guest assertions, `/tmp/admin-unit-live-qjkz1eig/report.json`; 120-second observation, incorrect repairs, kernel limits, dependency audit, no listeners, clean Stop/Resume/retained Reset |
| Copied pre-batch session | Native Resume and clean Stop pass; old image/no sudo entitlement, previous marker, exact session bytes and unchanged base; `native-legacy-resume.log` / `legacy-clone.json`; original copied-from profile rehashed unchanged |
| Installed native lifecycle | **17 Start + 20 fresh-process Resume checks passed**, `/tmp/admin-installed-native-pibte3zf/{start,resume}-report.json`; exact image/lesson pins, persisted marker/report, cross-unit controls and cross-profile exclusion, clean Stop, zero QML warnings |
| Final native availability/Stop review | **24 checks passed**, `/tmp/admin-unit-live-dr868let/report.json`; original and administrator images, withdrawn boot/Reset refusal, missing retained descriptor, real process identity/QMP clean Stop, durable clean lifecycle, unchanged session bytes and bases |

### Final security and compatibility review

The incoming 32 candidates matched `/tmp/admin-unit-reviewed.sha256`. Review added
three regression tests and a native availability fixture, without changing runtime
code, guest payloads, lesson pins or image content. All 24 explicit routes now have
image/lesson resume-only and withdrawn authorization checks, missing/mismatched
pin refusal, saved-byte preservation, and a real file lookup showing that an
installed administrator base cannot replace a missing unprivileged base. Existing
forged-process tests retain real process-identity checks. Synthetic routing fixtures
are distinct from the added native QMP/process-exit checks.

Availability means a retained revision is withdrawn/resume-only, its base is
missing, or a saved pin cannot resolve while valid default resources remain.
Malformed/missing application catalog or default lesson resources are a damaged
installation: catalog construction fails closed, with no substituted image. The
in-app Stop routing is not claimed to survive arbitrary deletion of installed
application resources. Preserve a compatible installation while a guest runs.

The actual runtime test observed the bounded worker ending around 120 seconds;
rotation tests exercised three rotations and retention of exactly two archives.
Oversized worker configuration was rejected and actual output remained small.
Memory/task/CPU limits were read from the running cgroup and the file limit from
the actual process. They were not tested by inducing OOM, task exhaustion or a
log flood. Journal size settings remain management targets. Guest root can override
all these guest-side limits; host isolation is unchanged.

Review rehashed all 204 retained binary packages/notices and 603 source files for
194 source versions, reverified signed Debian main/security metadata, and checked
the executed recipe payloads and all four original/new source/registered base
hashes. The exact administrator base is still
`f956d5c98848296f6887235c742ee4cc44ed5981acd0d2efd0a593b16d8a578f`.
Production keys/releases are empty. All 139 application/resource files still match
the tested wheel and installed package. Final installed smoke and offscreen UI
reruns are `/tmp/admin-final-review-installed.log` and
`/tmp/admin-final-review-ui-{1,1.5,2}.log` (227 checks per scale, both sizes).

The first sandboxed full-suite rerun could not start its isolated GPG fixtures;
the approved normal-user rerun passed all 521 tests. Test trust remains temporary
and excluded from package resources. The existing shutdown warning remains open.
Final commit-candidate hashes are in `/tmp/admin-unit-final-reviewed.sha256`;
the earlier manifest/evidence is retained separately rather than overwritten.

Per-lesson evidence combines unchanged lifecycle/boot/override passes from
`/tmp/admin-unit-live-qvlcxs51`, access/logging/rotation passes from
`/tmp/admin-unit-live-21tno5yr`, final incident passes from
`/tmp/admin-unit-live-juece3q2`, and final controlled-change passes from
`/tmp/admin-unit-live-q4cwsm93`. Both modes use fresh generations. Each run checks
cross-unit Stop routing, second-launch refusal, self-review-only records, clean
Stop, same-profile reopening and unchanged base hash. Guest assertions verify
actual sudo/account/network policy and the lesson-specific result. This does not
turn self-review into application assessment.

### Findings and retained failed evidence

- The original combined access restart/journal/Stop command could stop the new
  invocation before its readiness event. It is now a separate startup observation
  and Stop step, with a brief startup interval and explicit missing-event guidance.
  Both final modes pass. First-lesson setup now chains creation/cd/pwd with `&&`.
- An initial accelerated console-input experiment dropped characters; the paced
  developer input fixture was restored. Its failed disk/evidence is retained at
  `/tmp/admin-unit-live-9tx9_abd` and `native-first.log`.
- One incident fixture sent handover lines to the shell rather than an active
  nano editor. Copies of its retained disk established that no report existed;
  a separate native reproduction opened nano and saved successfully. The exact
  trigger of that initial editor loss was not established. The fixture now checks
  the native nano screen before sending text, captures it, and runs sequentially
  without other native UI fixtures. Both final incident modes pass. Failed evidence
  and diagnostic copies remain retained; no app/image-policy change masked it.

- The initial runtime fixture read `ExecMainStartTimestampMonotonic` and
  `ExecMainExitTimestampMonotonic` after successful deactivation, when this systemd
  returned zero for both. Its retained journal showed a 120.033-second run; a
  separate native reproduction confirmed active timestamps followed by zeroed
  inactive fields. The fixture now captures elapsed seconds when polling observes
  exit and retains the journal, keeping the same 119–126-second test window. No
  guest limit or controller behavior was changed. Evidence:
  `/tmp/admin-unit-live-f1t2l14d` and `/tmp/admin-unit-live-_a7l15g_`.

Known baseline warning remains visible, not suppressed:
`gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.

Native rendering and synthesized QtTest/QMP input are not physical-keyboard or
accessibility acceptance. Physical keyboard, assistive technology and untested
native workflows remain outstanding. Owner UAT is optional, not a completion gate.
Public distribution remains deferred, including unfinished Qt redistribution
review and the unresolved ICU signing-key warning. No personal credentials or production
signing material were created. Signature regressions use isolated test trust,
which is excluded from the package and production admission.

## Reproduction and review

See [admin-unit.md](admin-unit.md) for source launch, image registration and the
scope of each lesson. Native test tools contain static developer commands; the
application never loads them or executes lesson JSON. Native fixtures require
reliable host process visibility and normal shared VM exclusion; an unrelated
active guest is a blocker, never permission to stop it.

The final candidate list is below. `/tmp/admin-unit-reviewed.sha256` records exact
candidate hashes. All sequential native checks completed; test guests are cleanly
stopped and the normal shared coordination record is stopped.
`final-image-and-process-check.json` verifies original/new source/registered base
hashes, 16 GiB sizes and read-only modes after the final native run. The original
pre-batch disposable profile copied for compatibility testing was rehashed unchanged.

The evidence root's `evidence/` directory contains verified durable copies of the
referenced temporary reports, screenshots, fixture scripts and disposable app
profile. `evidence-manifest.json` lists their hashes. These are evidence copies,
not a profile migration or an alternate VM session location. No disks, profiles, source archives, screenshots,
runtime records or test trust material belong in the source commit.

## Complete changed-file list (32)

```text
app/THIRD_PARTY_NOTICES.md
app/docs/vm-preview/admin-acceptance.md
app/docs/vm-preview/admin-image-provenance.json
app/docs/vm-preview/admin-packages.tsv
app/docs/vm-preview/admin-unit.md
app/docs/vm-preview/setup.md
app/learning_lab/vm_preview/admin-image.json
app/learning_lab/vm_preview/admin-unit.json
app/learning_lab/vm_preview/image-catalog.json
app/learning_lab/vm_preview/image_catalog.py
app/learning_lab/vm_preview/real-linux-admin-access.json
app/learning_lab/vm_preview/real-linux-admin-boot.json
app/learning_lab/vm_preview/real-linux-admin-change.json
app/learning_lab/vm_preview/real-linux-admin-incident.json
app/learning_lab/vm_preview/real-linux-admin-lifecycle.json
app/learning_lab/vm_preview/real-linux-admin-logs.json
app/learning_lab/vm_preview/real-linux-admin-override.json
app/learning_lab/vm_preview/real-linux-admin-rotation.json
app/learning_lab/vm_preview/registry.py
app/learning_lab/vm_preview/units.json
app/tests/admin_guest_fixtures.py
app/tests/admin_unit_live.py
app/tests/test_admin_unit.py
app/tests/test_capacity_unit.py
app/tests/test_image_catalog.py
app/tests/vm_lessons_acceptance.py
app/tests/vm_lessons_switch_live.py
app/tools/installed_smoke.py
app/tools/vm_image/admin/finish-image.sh
app/tools/vm_image/admin/prepare.py
app/tools/vm_image/admin/preseed.cfg
app/tools/vm_image/admin/register.py
```
