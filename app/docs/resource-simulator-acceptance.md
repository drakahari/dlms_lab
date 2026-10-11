# Resource Evidence simulator acceptance

2026-10-10 (local date). Content-only batch based on clean, pushed main
`7638b284bd2f4cabb676f50d6da7d064ddae69c2`. Live origin/main matched before work.
The owner reported the navigation repair looked good; that approval is not
extended to these new activities, physical keyboard or accessibility.

## Delivered scope and inventory

Four new contract-5 packs, one collection manifest and one index entry.
No Python application logic, QML, engine, controller, contract, storage, backup,
VM image or old pack/lesson was edited. Test harnesses and guidance are updated.

| Inventory | Before | After |
| --- | ---: | ---: |
| Simulator Linux collections | 4 | 5 |
| Unique Linux simulator packs | 22 | 26 |
| Collection appearances | 26 | 30 |
| Network simulator packs | 3 | 3 |
| Unique simulator packs total | 25 | 29 |
| Real-VM units / lessons | 9 / 76 | 9 / 76 |

IDs (content version 1.0.0): `linux-resource-baseline`, `linux-memory-evidence`,
`linux-space-inodes`, `linux-trend-handover`. Existing eight-collection/32-item
limits remain; VM bounds/maps/serialized resources remain unchanged.
See [the unit guide and walkthrough](lpic-2-resource-simulator.md).

## Evidence and recovery

Verified 459-file source recovery snapshot, reverified after testing:
`/home/drak/.local/state/omarchy-learning-lab/recovery/resource-simulator-20261011T021120435046Z/source-before`.
Its sibling `source-before.sha256.json` records bytes; no real profile was copied.
Logs, screenshots, isolated wheel/venv and failure evidence are retained in that
same recovery root outside Git. `reviewed-files.sha256` provides final candidate
paths/hashes. `wheel-package-hashes.json` verifies all 204 application/resource
files in the actual wheel equal current candidates.

- **Full regression: 632 passed**, 41.271 seconds. Includes 11 focused new tests.
- **GNU: 44 existing fixtures + 5 new report fixtures passed.** Fixed developer
  argv only, C locale. New fixtures compare stdout, successful status, empty
  stderr and resulting virtual report bytes; existing fixtures cover error,
  truncation and partial-output semantics. No learner or imported command is sent
  to GNU. Physical resource measurements are not claimed by these fixtures.
- Four packs validate with the authoritative portable loader and feasible guided
  routes. Both modes reach 100 using actual simulator commands; alternative
  paths/pipelines pass. Challenge guidance/hints are hidden.
- Incorrect/incomplete reports, missing trend rows, wrong reading tool, retry,
  last-write evidence invalidation, unsupported/hostile commands, output path
  isolation, bounded content, collection overflow, reset/mode history, lab
  isolation, separate-process resume, exact pins/drafts/record bytes,
  scenario/history export, reimport, older pinned version, backup/restore and
  hidden visibility all passed using disposable profiles.
- A preservation test compares **every original application/resource file** with
  the baseline, allowing only the collection index to change. Existing packs,
  simulator implementations, navigation QML, 76 VM lessons/images/pins and
  controller bytes remain identical.
- Actual wheel built with existing declared build dependencies, no download;
  installed into a separate venv using existing system PySide6. `pip check`
  passed. Wheel hash:
  `b17117e52db1da6fa60518125e484155b7077ffc5d6bcc4e7f1d05fa4940da14`.
  Standalone `python -I -B` smoke outside checkout loaded five collections/26
  packs, completed four new packs in both modes and separately reopened exact
  saved records. Authoring, prior collections and optional-no-QEMU startup passed.
  No working installation was updated.

## UI and native evidence

Python 3.14.7; PySide6/Qt 6.11.2; Omarchy 4.0.4, Hyprland 0.56.2 Wayland;
software Qt Quick rendering. Native test monitor eDP-1, 2880×1920, scale 2.
Test-only per-process QT_SCALE_FACTOR .5/.75/1 gives verified Qt DPR 1/1.5/2;
no global desktop settings changed. Actual logical sizes were asserted.

| Suite | Scope | Result |
| --- | --- | --- |
| Source simulator UI | 800×600 / 1280×900, 100/150/200%, four labs and both modes | Native: 111 checks + 9 fresh-process resume checks per scale; passed |
| Simulator UI | Same layouts/scales | Offscreen: 110 + 8 resume checks per scale; passed |
| Repaired navigation | Compact/wide, current Omarchy and built-in fallback colors, all scales | Native: 375 checks per scale; offscreen: 374; passed |
| Installed-wheel simulator UI | Outside checkout, all four labs/both modes | Offscreen all scales: 110 + 8 each; native at 200%: 111 + 9; passed |

Checks exercise actual command entry, Help/model reference, independent scrolling,
non-modal details remaining open while commands run, final grades, per-mode
collection progress and separate-process reopen. Reused navigation tests cover
real popup lifetime, mouse/key selection, Escape/outside click, long lists,
selected/hover/focus/disabled contrast ≥4.5, stale choices and existing control
wiring. Its VM actions are guarded/UI fixtures, **not guest lifecycle proof**.
No real guest was started for this task.

Native screenshots (in recovery root):

- `native-ui/resource-native-reviewed-2-completed-collection.png`: new collection,
  four rows and separate Learn/Challenge progress.
- `native-ui/resource-native-reviewed-1-lab-1-800.png`: compact memory lab,
  non-modal details and visible console/input.
- `native-ui/resource-native-reviewed-2-assessment-Challenge.png`: final factual
  trend report including missing sample; its 100 score does not assess reasoning.
- Full source/installed-native lab/collection screenshots at tested sizes/scales
  are retained, not committed as generated evidence.

## Independent review and retained failures

Independent reviewer checked factual semantics, commands, Learn/Challenge,
checker truthfulness, content isolation, integration, guidance and final diff.
One finding: “read” sounded broader than the required `cat` evidence predicate.
Fixed briefs/constraints/action labels and added a negative test: identical full
output through `head` plus HELP reading earns only report/preservation points;
required `cat` actions earn remaining evidence. Equivalent report filters remain
accepted. No blocking finding remained.

Early failed runs are retained; not counted as passes:

1. New assertion expected literal “not scored”, then mismatched capitalization;
   corrected to test self-reviewed/model/common-mistake disclosures in every pack.
2. Old test counts assumed four collections/22 curated packs; updated only these
   inventory expectations, preserving old pack/pin assertions.
3. Two harness assertions looked for portable mission metadata on the domain
   adapter, where it does not exist; corrected to read the portable scenario.
4. Programmatic focus alone left a heading partly above the viewport after
   resize. Harness now uses the real scrollbar and keeps containment assertions.
   This does not claim complete focus-following behavior for all resize cases.
5. Native harness floated its window on each resize, toggling its state; corrected
   to float once and assert actual requested size. No application change.

Final regression/GNU, source native/navigation and actual installed-wheel checks
were rerun after relevant corrections. Final wheel/package hashes and retained
reports identify the candidate content. No assertion was replaced by an existence
check or hidden failure; no engine/controller policy was weakened.

## Limits and outstanding checks

Automatic scores check **report facts, specified cat actions and source invariant**.
No free-form reasoning entry/grading or numeric forecast assessment exists in this
contract. Models and arithmetic are openly supplied for self-review. Coverage is
limited reinforcement of official LPIC-2 v4.5.0 200.1/200.2, not live measurement,
monitoring, real mount/repair practice, complete preparation or LPI endorsement.

Native input here is QtTest-generated. Physical keyboard, actual wheel/trackpad,
screen reader, exhaustive native accessibility and other themes/scales remain
unverified. Known baseline warnings remain, not suppressed:

- `ResourceWarning: gc: 5 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`
- `Failed to register with host portal QDBusError("org.freedesktop.portal.Error.Failed", "Could not register app ID: Connection already associated with an application ID")`

Existing release-compliance/Qt/ICU and VM-distribution blockers remain unchanged.
Owner installation/profile and guest sessions were untouched. Task-owned test
windows/processes finished and locks were released; no guest lifecycle was used.
