# Bash, Regex & Safe File Changes — acceptance record

Verification date: 2026-10-05. Baseline:
`33111ff59f541917b62ccc6c1b0ffbfe94d395c8` (clean before the batch).
Local development evidence, not public-release clearance or owner UAT.

## Scope and preservation

The fourth bundled unit adds twelve display-only lessons, raises the aggregate
registry limit from 24 to 36, and explicitly maps every new lesson to the existing
unprivileged `debian13-jobs-local-v1` image. Bounds remain four units and sixteen
lessons per unit. Acceptance at 36 and rejection at 37/five units are tested.
See [unit guide](bash-unit.md) for instructional scope and partial LPIC mappings.

The owner separately approved a narrow `Manager.stop()` completion fix after a
reproduced lifecycle blocker. Only that controller method changes. Process
identity, launch-policy validation, ownership, QMP authority, descriptor containment,
shared exclusion, image descriptors and disk-generation policy remain unchanged.
Original 24 lesson bytes, order, identities, image routes and legacy session
location remain preserved. No QML, simulated engines, guest privileges, image,
profile/session/disk/backup schema or production trust change. No host setting,
working installation, real profile or user guest was changed or stopped.

Verified recovery root (outside Git and personal profiles), abbreviated **B**:

```text
/home/drak/.local/state/omarchy-learning-lab/recovery/bash-unit-20261005T123917849349Z
```

`B/source-manifest.json` covers 347 original tracked files. The original batch,
pre-fix source, interrupted evidence and retained disks have separate snapshots.
Current durable verification root, abbreviated **R**:

```text
B/lifecycle-review-20261005T155827Z
```

Disposable guests use `B/runtime`, an independent read-only base copy:

```text
image: debian13-jobs-local-v1
raw size: 17179869184 bytes
base SHA-256: a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d
image descriptor: 0a289a55b446de28e6e1ad0872a50cea82f19925212b247a850f01ade01a9548
```

## Stop failure: demonstrated cause and authorized fix

`R/prior-profile-after-diagnostic/trace-27952.json` captured the failure. The only
Start before it belonged to the Bash-script session. Selecting the background-job
lesson did not change Stop ownership:

- App PID 27952; QEMU PID 27995; boot
  `1ac12877-398f-4c01-bf31-200be0467b3e`; process start tick `395868`.
- Run `34171783-0c1a-4da8-b0aa-66c6cb8193e3`.
- Profile `add1f4714d1e1bbd5e470a15d2b8c4453a593d06ae6be65e2a57aaa18b6f143a`.
- Session `acea5ce0-2ca8-4d80-aa3c-65a0121b453a`;
  generation `0a6ca225-0244-4fd7-b9d8-a29366b25f76`.
- Lesson `real-linux-bash-script`, digest
  `5b412853d52593974d1318e6f12774e4d194b82b8cc8fe02c52d0ff1dccf4da9`;
  original unprivileged image above.

`Manager.stop()` returned **Cleanly stopped** and published stopped records.
About 1.24 ms later, the bridge's post-operation refresh called
`Sessions.view → Manager.reconcile → Manager.gate`; its nonblocking lifetime-lock
acquisition failed with **“A preview VM is already running, possibly in another
profile.”** Thus the reproduced message came from refresh after Stop, not a second
Start or misrouted shutdown. The lock was free by the later descriptor-holder scan.
The evidence does not identify a kernel-level reason for the short release window.
A separate trace captured real QMP `SHUTDOWN` (`guest: true`) and process exit with
the lock already released, explaining why repeats could pass without a fix.

The approved fix preserves the operation lock and existing verified shutdown/exit
checks, then waits **at most five seconds** to acquire the same descriptor-verified
lifetime lock. Both locks remain held while completion is published. Timeout
reports failure, retains records/disks, and never claims completion or bypasses the
lock. No signal escalation or new QMP operation was added.

Three regression tests exercise real `flock` boundaries: delayed release before
publication; five-second timeout with byte-identical records; separate competing
processes refused both locks during publication. Their guest shutdown is a fixture;
actual QMP/process shutdown is covered separately by native installed tests.

## Separate focus and test-harness findings

A deterministic UI fixture holds the existing asynchronous refresh worker, focuses
the Return control and yields as the old harness did. Busy state disables the
control and removes focus. After refresh completion, readiness and immediate focus
activation succeed. Six assertions cover this transition at every tested UI scale.
The native harness now waits for active window, idle/completed refresh and enabled
control, then focuses/activates without the old 100 ms event-loop gap. No app focus
policy or QML changed. Stop ownership remained correct in the failure trace.

Tight Qt-only polling initially starved/slowed the image-hash worker; stack and
file-offset evidence identified ongoing hashing before any guest launch. Readiness
polling now yields to worker threads while checking explicit conditions. Two later
raw-OCR acknowledgement failures occurred after guest commands had completed.
Lifecycle smoke uses contrast/upscaled exact marker recognition. The longer lesson
replay uses calibrated, exact whole-row framebuffer acknowledgements with unique
counters, rejecting stale markers and command echoes. Five tests exercise acknowledgements and exact editor readiness. It is developer-only, fixed to the verified console geometry/font; it adds
no agent, host share, runtime command execution or assessment capability.

## Actual installed-wheel and native lifecycle results

Built with declared setuptools 84.0.0 in an isolated build environment; installed
into a separate venv, using the existing official PySide6 environment read-only.
No global packages or working installation changed. `pip check` passed.
Runtime: Python 3.14.7, PySide6/Qt 6.11.2, QEMU 11.1.1.

```text
R/wheels/omarchy_learning_lab-0.1.0-py3-none-any.whl
SHA-256 8e0068832d342bc75562964450f9a6b1448357003a7da1ec7d575c5fadbe34ff
```

All 152 packaged application/resource members match reviewed source bytes.
Outside-checkout `python -I -B` installed smoke passes core startup without QEMU
or an image, packaged resources, four units/36 lessons and scenario start/resume.
Test trust, evidence, disks and profiles are excluded from the wheel.

The final installed native lifecycle uses three separate app processes and the
same disposable profile `R/evidence/installed-fixed-25cp05cp`:

| Phase | Result | Durable log |
|---|---|---|
| Start | 17 checks passed | `R/fixed-installed5-start.log` |
| Restart and same-disk Resume | 20 checks passed | `R/fixed-installed5-resume.log` |
| Retained Reset and fresh boot | 22 checks passed | `R/fixed-installed5-reset.log` |

Each phase verifies lesson switching while running, a controlled foreign-profile
Start refusal followed by the owning profile's clean Stop, and exact running →
stopped process identity. Resume preserves generation, files and image/lesson pins;
it does not restore RAM or jobs. Reset retains the old disk byte-for-byte, creates
a new generation with the same pins, and verifies the old marker absent. Records,
QMP evidence and screenshots remain in each `run-*` subdirectory;
`R/installed-lifecycle-identities.json` summarizes the exact identities. These
passes use the fixed controller; earlier diagnostic successes are not substitutes.

## Final lesson replay and regression gates

**All twelve lessons × Learn/Challenge passed: 24 distinct native workflows.**
`R/final-24-workflows.json` matches every case's exact running/stopped process
identity, lesson/image pin, generation and evidence. Detailed guest commands,
assertion results and raw screenshots remain in:

| Cases accepted | Directory beneath `R/evidence/` |
|---|---|
| Files, environment, quoting, streams, regex, transformation × both modes | `bash-unit-live-hu2lpyhg` |
| vi and mistaken-edit recovery × both modes | `bash-unit-live-qer89szv` |
| Script, guards, records, capstone × both modes | `bash-unit-live-w4ebv2jk` |

The first two runs later encountered independent editor-readiness failures; only
completed cases above count. All affected nano cases were rerun after the final
header fix, including the previously passing basic script. Each accepted case
verifies actual guest output/files/statuses, unprivileged UID/no sudo/loopback only,
real cross-profile refusal, mode behavior, self-reviewed completion, clean Stop,
exact same-profile metadata reopening and unchanged base hash.

Guest exercises include actual Vim Tiny edits and nano script entry, unsaved edit
discard, saved rollback, original bytes/modes, spaces/backslashes, empty and
unterminated records, BRE/ERE matches/nonmatches/errors, redirection side effects,
pipeline status, script argument/permission failures, finite-time loop termination,
record/byte bounds, rejected publication and retained good reports. Syntax checks
are distinguished from behavior assertions; no fixture executes lesson JSON.

Final post-replay gates passed:

- **546 regression tests** in 28.960 seconds (`R/final-all-regressions.log`).
  Includes delayed lock release, timeout, competing acquisition, legacy routing,
  registry/resource bounds, identities, profile/scenario/backup compatibility,
  hostile input and isolated failure fixtures.
- The pre-batch legacy session booted its original pinned image, verified retained
  guest files/tools, then cleanly stopped. Saved `current.json` bytes and base hash
  are unchanged (`R/final-legacy-native.log`,
  `R/evidence/bash-unit-live-zv6a1eom`).
- Final actual host inspection found no QEMU process, the last runtime record
  stopped, its exact process absent, and both descriptor-verified operation and
  lifetime locks available (`R/final-host-state.json`). No coordination record was
  removed or rewritten by this inspection.
- All 347 baseline snapshot files, 41 retained disk copies and 43 original owner
  session records match their recorded hashes (`R/reverified-recovery-and-owner.json`).
  Both complete 16-GiB original and test base hashes remain unchanged, mode 0444
  (`R/final-base-integrity.json`).

Existing GNU text reference comparisons: **44 passed** (`R/final-gnu-reference.log`).

UI checks: **365 assertions each** on offscreen Qt and native Wayland at effective
100%, 150%, 200%, with exact 800×600 and 1280×900 logical windows. Zero QML warnings.
`R/final-ui-summary.json` links all six evidence directories and screenshots.
Native rendering and synthesized input are distinguished from physical keyboard or
accessibility acceptance. Existing monitor scaling was accounted for, not changed.

## Interrupted and failed evidence, remaining limits

The host interruption was not reinvestigated. The owner reports finding the PC
powered off and manually powering it on, empty pstore and no actionable NVMe
health/error warning; the shutdown cause remains unknown. Pre-reboot summaries
survive, but their lost `/tmp` command logs are **not final evidence** for this batch.
The former acceptance document is retained at
`R/acceptance-before-consolidation.md`, along with all surviving recovery records.

`R/historical-failure-ledger.json` identifies the earlier two Stop-wait failures,
focus failure and invalid literal `..` path rejection. Exact old profile/session,
lesson/image/generation pins survive; their per-run PIDs/lock-owner records were
not captured and cannot be reconstructed honestly. New reproduction and final
runs retain those identities. `R/current-failure-ledger.json` hashes failed and
interrupted current runs, including polling/OCR failures and the initial failed
regression fixtures. The vi readiness expression incorrectly expected `3L`;
Vim Tiny actually reports `3 lines, 17 bytes`. Nano full-screen OCR confused
`GNU` with `GHU`; readiness now uses the existing exact cropped-header/title and
filename check. Both failures have raw screenshots, strict regression tests and
clean guest cleanup. `R/failed-lesson-identities.json` retains the exact process,
profile, session, generation, image and stopped lifecycle of all three failed
lesson replays. They are not relabeled as successes. All retained overlays,
failed candidates and recovery evidence remain outside Git. No lock removal,
force Resume or forced guest shutdown was used to make tests pass.

Known baseline shutdown warning remains unsuppressed:

```text
gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them
```

Physical keyboard, accessibility, exhaustive native compositor/focus combinations,
full LPIC coverage and public-release compliance remain outstanding. Completion is
still self-reviewed and unscored. Qt/ICU source/signing obligations remain open.
No staging, commit, push, installed-app update or production image admission.
