# Resource Diagnosis & Capacity Evidence: implementation evidence

Baseline: `e3987126b4382d1888f8ca252be4578a9f57acae`, verified clean before edits.
This authorized batch is unstaged/uncommitted. No working installation, real
profile, original image/session, host configuration or production trust changed.

## Recovery and isolation

Verified source snapshot (311 tracked files):
`/home/drak/.local/state/omarchy-learning-lab/recovery/capacity-unit-source-20261004T220004291152Z`.
All copied files were SHA-256 verified before editing. No personal profile copied.

Disposable native VM home:
`/home/drak/.local/state/omarchy-learning-lab/recovery/capacity-unit-runtime-20261004T221659764135Z`.
The prepared read-only image was reflink-copied and independently hashed; normal
shared user-wide VM exclusion applies. No coordination records were cleared to
make a test launch succeed. Test overlays and failed evidence remain retained.

Pinned raw base SHA-256:
`a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d`.

## Scope and compatibility

- Trusted multi-unit index, bounded registry and unit selector; no external index.
  Limits remain four units, sixteen per unit, **sixteen total**. Original unit is
  the default API result; flattened lookup discovers running lessons in either.
- Eight new display-only lessons/support entries, new exact compatibility pairs
  with the existing image; all original lesson bytes, canonical pins, order,
  special background-job binding and original catalog descriptors are preserved.
- Unit selection derives from the existing selected lesson ID. No profile, session,
  image, engine, pack or backup-format migration. No launch-policy/QMP/security
  controller change. Profile backup still excludes VM records/disks/guest reports.
- Completion remains self-reviewed, unscored and explicitly not guest assessment.
  Resume boots an existing disk, not RAM or jobs. No live-threshold requirement.
- Lesson commands are read-only text. Fixed developer console fixtures are
  independent trusted literals, parity-checked against instructions; application
  runtime does not read them or execute JSON. Developer QMP input/screenshots are
  separate from the application's private operation allowlist.

## Evidence boundaries and retained failures

The first disposable test directory had an overly permissive newly created
`images/` parent; the unchanged controller rejected it before launch. Only that
new test directory was corrected to its required private mode. The original
image/directory and security guards were not changed.

Early evidence capture rejected genuine passing console output because OCR
misread a long marker at VGA resolution. Screenshots and clean-stop failure
records remain retained. The harness now uses a short word with exact-line
recognition and fails closed on unreadable output. No instruction/controller
change or fabricated success was used to address this test issue.

Concurrent native Lab fixtures initially encountered unit-selector width and
unchanged Main.qml dialog warnings. Sequential repeats use the same runtime,
per-process scale factors and requested sizes. No global display/window rules
were changed. Final successful evidence and remaining gaps are recorded below.

## Final results

| Check | Verified result / evidence |
|---|---|
| Full regression suite | **502 passed**, including 14 new registry/arithmetic/session tests; `/tmp/capacity-delivery-final-regressions.log` |
| GNU reference regressions | **44 passed**; `/tmp/capacity-final-gnu.log` |
| Original VM UI | **22 checks passed**; `/tmp/capacity-final-original-ui.log` |
| Final offscreen UI | **163 checks per scale**, 100/150/200%, actual 800×600 and 1280×900; `/tmp/capacity-frozen-ui-{100,150,200}.log` |
| Final native Wayland UI | **163 checks per scale**, same actual sizes/scales, zero QML warnings; `/tmp/capacity-frozen-native-ui-{100,150,200}.log` |
| All eight guest lessons | **16 distinct lesson/mode passes**, 96 controller checks; `/tmp/capacity-native-aggregate.json` |
| Final I/O payload/interruption | Passed, including actual 16777216-byte payload, kernel file-limit failure, foreground interruption and repeated cleanup; `/tmp/capacity-unit-live-8aqedd75/report.json` |
| Wheel/sdist build, install, pip check | Passed with declared build dependencies and an isolated venv; no dependency downloads or system-Python changes |
| Final wheel/source parity | **129 packaged application files** match source; `resource-parity.json` in the package evidence directory |
| Installed-wheel offscreen start/reopen | Passed outside checkout; 22 simulated collection packs, four simulation collections, both VM units/all 16 lesson resources; metadata fixture, not VM boot |
| Installed-wheel native lifecycle | **17 Start + 20 fresh-process Resume checks**; `/tmp/capacity-installed-native-final-pu6wpz3a/{start,resume}-report.json` |

Native lesson results are split across retained fixture reports:
`/tmp/capacity-unit-live-qefipzhp/report.json` (baseline/CPU/memory in both modes),
`/tmp/capacity-unit-live-dcl3luiq/report.json` (I/O and space/inodes in both modes),
and `/tmp/capacity-unit-live-8fm7z_et/report.json` (final trends/forecast/report in
both modes). Failed entries in those reports are excluded from pass totals.
The separate final I/O run adds payload-size assertions before scratch cleanup.

Confirmed inside the actual guest: CPU expiry status 124, actual supervisor/child
identities, refusal of a second worker, matching-start-tick repeated cleanup;
16 MiB payload/read/write, kernel refusal of a 17 MiB attempt under the file limit,
and interruption cleanup. Low-space admission was checked with a deliberately
small supplied counter, **not by exhausting a filesystem**. Synthetic rows/chart
counts and forecast output were checked in the guest and independently with
Python rational arithmetic. The final report was edited through actual nano;
this proves tool/data behavior, not human understanding or assessed mastery.

The installed native proof loaded the wheel outside the checkout, launched the
baseline lesson, selected the original unit while it ran, used Return/Stop,
refused a real cross-profile second launch, exited the application, and reopened
in a fresh process. Resume kept the same disk generation, exact lesson/image pins,
self-review and guest-local baseline/marker; no old shell jobs survived. Both
phases cleanly stopped with zero QML warnings. Source/restart fixtures also protect
old accepted session bytes; this is not native replay of all eight older lessons.

Final package evidence:
`/home/drak/.local/state/omarchy-learning-lab/recovery/capacity-unit-package-reviewed-20261004T224713Z`.
Wheel SHA-256:
`eb0c0afe1e3e618ddefa8eac99909992303816ff1db22fc4084769714d43adb3`.
The installed dependency environment reuses existing dependency files read-only;
`learning_lab` itself is installed from this candidate wheel and its location is
asserted inside the new venv. Test-only synthetic metadata/resources and developer
fixtures are not runtime guest assessment.

The final source distribution was rebuilt separately after documentation/test
review. Matching license/notices and unit/lesson JSON resources are verified; the
existing manifest intentionally prunes tests and does not ship these source-only
unit/acceptance guides. Installed guidance is contained in the bundled JSON and
does not depend on those files or the checkout.

Runtime: Python 3.14.7, PySide6/Qt 6.11.2, QEMU 11.1.1. The unchanged Debian 13.7
image contains Bash 5.2.37, coreutils 9.7 and procps 4.0.4. Native UI tests used
per-process scale factors 0.5/0.75/1 on the scale-2 display to assert actual DPR
1/1.5/2. No global desktop scaling was changed.

One unreleased trend review sentence was corrected from “checksummed by
inspection” to “checked by inspection.” An already-running disposable fixture
correctly rejected its changed resource digest; its cleanly stopped disk/evidence
were retained and both modes rerun from frozen content. No accepted lesson,
owner session or provenance was changed/migrated.

An initial installed native fixture clicked after GTK activation and failed its
Stop step. Cleanup cleanly stopped its guest and retained its disk. The passing
fixture waits for native window activation, asserts the exact focused button and
uses Space; it does not retry a failed operation or weaken the controller. This
is synthesized-input evidence, with physical-input acceptance still outstanding.

## Outstanding acceptance and roadmap

Physical keyboard, screen reader/accessibility, exhaustive focus/contrast,
multi-monitor/window-manager arrangements remain unverified. Synthesized QtTest
and developer guest input are not those checks. Installed native smoke is a
representative lifecycle, not exhaustive installed playtesting of all lessons.

Live timing/cache observations are guest-specific, not physical hardware
benchmarks. Guest timers are not hard deadlines for suspension/uninterruptible
I/O; file limits are per-file, admission is not a free-space reservation or
aggregate quota. Retained overlays consume storage and are never pruned here.

Known unchanged baseline warning is retained, not suppressed:
`gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.

Partial LPIC-2 v4.5 200.1/200.2 only; real administration/troubleshooting is next.
Guest privileges, additional packages/disks, networking and multi-guest practice
need separate approval. Public release remains deferred, including the existing
ICU signing-key warning and unfinished Qt redistribution review.

## Optional disposable owner check

Use the [setup command](setup.md#disposable-app-review-does-not-update-the-installed-app)
with a new `/tmp` data/config profile and the existing verified VM home. Open
Library → Real Linux VM preview → Resource Diagnosis & Capacity Evidence. Start
baseline, collect guest-local notes, select the Processes unit while running and
use Return/Stop. Reopen the same disposable profile and Resume; notes survive,
jobs do not. Choose forecast to compare the reserve-aware arithmetic with the
irregular example. No owner walkthrough is a routine acceptance gate.

## Final state and reviewed paths

Both the original prepared image and the isolated read-only copy were fully hashed
after the last native test; SHA-256, 16 GiB size and read-only modes match. Normal
coordination ends `stopped`, host process inventory finds no QEMU guest, and no
force stop was used. `/tmp/capacity-final-runtime.json` records these checks.
Retained test runtime uses about **1.21 GiB allocated** (sparse/reflink accounting,
not a portable download-size estimate), with about **819.67 GiB available**.
No evidence/generation was pruned.

All 311 recovery snapshot hashes were reverified; 300 existing files outside the
11 intended edits remain byte-identical. Source packaging, simulation engines,
accepted scenario resources, persistence/backup and security controller files are
preserved. Candidate review found only the following 26 text source/resource/test/
documentation files. Profiles, disks, environments, evidence and trust material
remain outside this list. `/tmp/resource-unit-reviewed.sha256` records final hashes.
The index remains empty; HEAD stays at the requested baseline.

- `app/docs/vm-preview/processes-unit.md`
- `app/docs/vm-preview/resource-acceptance.md`
- `app/docs/vm-preview/resource-unit.md`
- `app/docs/vm-preview/setup.md`
- `app/learning_lab/qml/VmPreview.qml`
- `app/learning_lab/vm_preview/bridge.py`
- `app/learning_lab/vm_preview/image-catalog.json`
- `app/learning_lab/vm_preview/real-linux-capacity-baseline.json`
- `app/learning_lab/vm_preview/real-linux-capacity-cpu.json`
- `app/learning_lab/vm_preview/real-linux-capacity-forecast.json`
- `app/learning_lab/vm_preview/real-linux-capacity-io.json`
- `app/learning_lab/vm_preview/real-linux-capacity-memory.json`
- `app/learning_lab/vm_preview/real-linux-capacity-recommendation.json`
- `app/learning_lab/vm_preview/real-linux-capacity-space-inodes.json`
- `app/learning_lab/vm_preview/real-linux-capacity-trends.json`
- `app/learning_lab/vm_preview/registry.py`
- `app/learning_lab/vm_preview/resource-unit.json`
- `app/learning_lab/vm_preview/sessions.py`
- `app/learning_lab/vm_preview/units.json`
- `app/tests/capacity_guest_fixtures.py`
- `app/tests/capacity_unit_live.py`
- `app/tests/test_capacity_unit.py`
- `app/tests/test_image_catalog.py`
- `app/tests/vm_lessons_acceptance.py`
- `app/tests/vm_lessons_switch_live.py`
- `app/tools/installed_smoke.py`
