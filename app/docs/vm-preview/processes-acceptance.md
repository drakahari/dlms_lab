# Processes, Jobs & Priorities: batch evidence

Reviewed baseline: `8377f55fa2c4261e75be5119b20b8a3a40add459`.
Prepared for the authorized local source commit after final review. No working
installation update, profile migration, host configuration change, image
publication or push occurred.

## Preservation and scope

Recovery source snapshot:
`/home/drak/.local/state/omarchy-learning-lab/recovery/vm-process-unit-source-20261004T123624Z`.
Its 265 manifest hashes were reverified. All 260 tracked files outside the five
intentional existing-file edits match the snapshot, including accepted packs,
simulation engines, persistence and backup code. No personal profile was copied.
Original `vm_preview/lesson.json` bytes, canonical lesson pin and profile binding
are protected by regression tests. Older session records reopen unchanged.

Application changes: trusted bundled registry; lesson-scoped selection/session
adapter; Qt adapter; VM panel; optional trusted lesson ID in Manager construction.
Manager lifecycle method bodies, path/process/security helpers, runner/QMP policy
and image descriptor are unchanged and fingerprint-tested. A confirmed action
racing a status refresh is handed off once in the Qt adapter; operations are still
serialized and duplicate mutations are refused. No guest input automation was
added to the application.

Content: seven new lessons plus a unit descriptor/support notes; the accepted
background-job lesson is reused exactly. Tests: registry/selection, refresh race,
UI fixtures, static developer guest fixtures and native lifecycle integration.
Packaging verification: installed smoke script extended for all eight resources.
Documentation: unit guide, curriculum coverage update and this report.

## Automated and native results

| Check | Result / evidence |
|---|---|
| Complete regression suite | **399 passed** again at commit review, `/tmp/process-unit-commit-regression.log` |
| Original VM preview UI fixture | **22 passed**, `/tmp/process-unit-original-ui.log` |
| New offscreen UI | **59 checks per scale**, 100/150/200%, requested/actual 800×600 and 1280×900; `/tmp/process-unit-ui-{1,1.5,2}-reviewed.log` |
| Native Wayland UI | **59 checks per scale**, same sizes/scales, zero QML warnings; `/tmp/process-unit-native-{1,1.5,2}-reviewed.log` |
| Real pinned guest exercises | All eight passed on distinct disposable overlays; **56 controller checks**; `/tmp/vm-process-lessons-live-noow9tyo/report.json` |
| Native app + GTK lifecycle | **23 checks**, `/tmp/vm-lessons-switch-live-um1ojt35/report.json` |
| Wheel build/install/pip check | Passed using declared dependencies and isolated build/install environments |
| Outside-checkout wheel smoke | Start/reopen passed, 22 simulated collection packs and all eight VM resources/session metadata; `/tmp/process-unit-installed-final-smoke.log` |
| Wheel/source parity | **113 packaged files** match final source; `/tmp/process-unit-wheel-final-parity.json` |
| Installed-wheel native guest smoke | **12 launch/practice/Stop + 15 restart/Resume checks**, `/tmp/process-unit-installed-native-profile-2/{start,resume}-report.json` |

Final wheel: `/tmp/process-unit-wheel-reviewed-final/omarchy_learning_lab-0.1.0-py3-none-any.whl`.
SHA-256: `a1132a9abe8a1936af04fe6463e91ed049dcb8ada3b0a2d247e1b15c27b9de90`.
It was installed only in `/tmp/process-unit-installed-env`; smoke ran from `/tmp`
using `python -I`. The original installed smoke verifies resources and metadata
only. The subsequent **native installed-wheel** smoke launched the GTK guest,
practiced the accepted background-job lesson, cleanly stopped, exited the app,
then reopened in a separate process and Resumed the same disk. Original lesson
bytes, canonical pin, profile binding, guidance/self-review record and generation
were preserved. A guest-local marker survived; the old practice process did not.
Both phases cleanly stopped with zero QML warnings. This used the isolated wheel
environment, not the owner's working installation, from `/tmp` outside the checkout.

The first installed native input fixture failed at its Stop button step after
returning from GTK (a second Start was refused). Its disk was cleanly stopped in
fixture cleanup and retained. The successful rerun uses explicit synthesized
mouse targeting for app buttons; this does not close the physical-keyboard gap.
The failed run remains under `/tmp/process-unit-installed-native-profile` and is
not accepted smoke evidence. No application/security code was changed for it.

Reproduce outside the checkout using the isolated wheel-installed Python (copy
the developer fixture first; select a **new** disposable profile for a new run):

```bash
cp app/tests/vm_lessons_switch_live.py /tmp/process-unit-installed-native.py
cd /tmp
QT_QPA_PLATFORM=wayland QT_QPA_PLATFORMTHEME='' QT_QUICK_BACKEND=software \
  /tmp/process-unit-installed-env/bin/python -I -B /tmp/process-unit-installed-native.py \
  --installed --smoke-phase start --profile /tmp/new-process-wheel-profile \
  --vm-home /home/drak/.local/share/learning-lab-vm/preview-v1
QT_QPA_PLATFORM=wayland QT_QPA_PLATFORMTHEME='' QT_QUICK_BACKEND=software \
  /tmp/process-unit-installed-env/bin/python -I -B /tmp/process-unit-installed-native.py \
  --installed --smoke-phase resume --profile /tmp/new-process-wheel-profile \
  --vm-home /home/drak/.local/share/learning-lab-vm/preview-v1
```

The fixture uses existing developer OCR tooling and fixed guest commands; neither
is a runtime dependency or a learner-command endpoint. All disks remain retained.

Native lifecycle evidence includes selection while running, accessible Stop and
Return controls, disabled/refused second Start, Stop of the verified owner, same
generation Resume, missing running record with control-only Stop, progress
preservation, and Reset retaining the exact prior disk with fresh Challenge state.
Other-profile exclusion was also tested for every guest lesson. All disposable
guests were cleanly stopped; final process/base verification is recorded in
`/tmp/process-unit-final-runtime.json`.

## Guest observations and test boundary

Runtime: Python 3.14.7, PySide6/Qt 6.11.2, QEMU 11.1.1. The existing offline
Debian 13.7 guest has Bash 5.2.37, coreutils 9.7, procps 4.0.4 and util-linux 2.41.5.
No packages or guest privileges were changed.

Reviewed console screenshots show process/job control, targeted TERM/KILL with
the companion unaffected, top/watch, controlled logout survival, niceness after
denial and handover cleanup. All eight final screenshots show a standalone
`GUESTCHECKPASS`, generated by fixed developer assertions inside each guest.
Developer OCR checked that marker and the screenshots were visually reviewed.
These fixtures use explicit developer QMP input/screenshot operations outside the
application's private allowlist; they do not execute lesson JSON and do not add a
runtime assessment interface. Early incomplete input-fixture runs are retained
but **are not accepted exercise evidence**.

Verified: huponexit off is the default; the controlled practice shell turns it on;
ordinary tasks end while nohup/disown-h tasks survive logout; the new shell has no
jobs and its setting returns to off. Priority observations show NI 0/12, renice to
15, denial leaving 15, and denied `nice -n -1` still starting sleep at NI 0.
No fixed PID/job number is assumed. Logout survival is not reboot survival.

Pinned base SHA-256 remains
`a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d`.
VM home remains `/home/drak/.local/share/learning-lab-vm/preview-v1`; runtime gates
remain `/run/user/1000/oll-vm-preview`. Disposable disks/generations remain under
the VM home's `profiles/` tree for recovery. The original proof directory, image,
working installed app and real learning profile were untouched. Retained disks
consume storage; none were automatically pruned.

VM disks, selection and self-review records remain excluded from simulation
profile backups/exports. Supported backup versions remain unchanged. Core startup
and simulations without QEMU/image, lesson/mode pinning, unknown/missing/newer
records, symlink refusal and cross-profile concurrency have regression coverage.

## Outstanding acceptance and limitations

- Native input was synthesized QtTest/developer console input. **Physical keyboard,
  screen reader/accessibility, exhaustive focus/contrast and multi-monitor checks
  remain outstanding.** No new owner UAT evidence is claimed.
- Installed-wheel native proof covers one representative accepted lesson and disk
  Resume; it is not exhaustive installed playtesting of every lesson or dialog.
- Completion is self-reviewed, with no verification score. Guided progression is
  not proof that commands ran. VM Resume boots disk files, not RAM/processes/jobs.
- Partial LPI objectives 103.5/103.6 only; multiplexers and successful privileged
  priority increases are absent. No imported VM lessons or automatic assessment.
- Existing shutdown warning remains unchanged and unsuppressed:
  `gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.
- Per-file growth limit and best-effort monitoring are inherited; no aggregate
  quota, guaranteed free-space reserve or protection against hostile malware.

Use the [unit guide](processes-unit.md) for the disposable source launch. Optional
hands-on check: Start an inspection lesson, choose another lesson and use Return/
Stop; Resume the original disk, then confirm Reset creates fresh Challenge state.
Practice priority denial or controlled logout inside GTK and compare observations.
This is optional review, not a standing delivery gate.

## Reviewed changed files

- `app/docs/lpic-unit-3.md`
- `app/docs/vm-preview/processes-acceptance.md`
- `app/docs/vm-preview/processes-unit.md`
- `app/learning_lab/qml/VmPreview.qml`
- `app/learning_lab/vm_preview/bridge.py`
- `app/learning_lab/vm_preview/manager.py`
- `app/learning_lab/vm_preview/real-linux-foreground-jobs.json`
- `app/learning_lab/vm_preview/real-linux-live-monitoring.json`
- `app/learning_lab/vm_preview/real-linux-logout-persistence.json`
- `app/learning_lab/vm_preview/real-linux-process-handover.json`
- `app/learning_lab/vm_preview/real-linux-process-inspection.json`
- `app/learning_lab/vm_preview/real-linux-process-priorities.json`
- `app/learning_lab/vm_preview/real-linux-targeted-signals.json`
- `app/learning_lab/vm_preview/registry.py`
- `app/learning_lab/vm_preview/sessions.py`
- `app/learning_lab/vm_preview/unit.json`
- `app/tests/test_vm_bridge.py`
- `app/tests/test_vm_lessons.py`
- `app/tests/vm_lessons_acceptance.py`
- `app/tests/vm_lessons_live.py`
- `app/tests/vm_lessons_switch_live.py`
- `app/tools/installed_smoke.py`
