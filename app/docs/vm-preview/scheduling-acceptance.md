# Scheduling unit acceptance

## Scope and recovery

Baseline: `a3119804656fb23f511afe47da71874b5f9ca835`; initially clean main,
one commit ahead of local origin/main tracking. That commit remains unpushed.
No changes to the working installation, real profiles, host settings or images.

Verified source recovery snapshot and persistent evidence:

`/home/drak/.local/state/omarchy-learning-lab/recovery/scheduling-unit-20261005T202426657951Z`

The snapshot's 382 tracked files verify against its recorded hashes. Final
comparison protects 158 original package files, all 44 original lessons and
unit content, exact image routes and pins. Removing only the eight additions
from the catalog reproduces the baseline catalog exactly. Controller, launch
policy, QMP authority, accepted Stop-completion wait, images, session/disk/backup
formats and empty production keys/release allowlists remain unchanged.

The only production Python change is the explicit registry expansion:
**six units, sixteen lessons per unit, fifty-two total**. Tests accept 52/16 and
reject 53, a seventh unit and a seventeenth per-unit entry before extra reads.
Resource/text/step bounds and the bundled-only registry remain enforced.

## Final verification

| Check | Actual result and evidence under the recovery directory |
|---|---|
| Complete regressions | 573 passed, 30.333 seconds; commit-review `regression-final.log` |
| GNU developer references | 44 comparisons passed, including output/status/file state; commit-review `gnu-final.log` |
| Real lessons | All eight in Learn and Challenge; final 16 records match current canonical lesson pins and executed static commands: commit-review `final-current-pin-matrix.json` |
| Native supplemental assertions | Output ownership, final inactive service results, loaded limits and actual timeout/cgroup tasks; `evidence/final-affected-native-evidence.json` |
| Legacy real sessions | Original unprivileged and administrator sessions resumed; privately unavailable/withdrawn content refused boot while owning verified Stop worked: `evidence/legacy-live.log` |
| Qt layout/input | Current full offscreen: 553 × 3 checks; focused native: 223 × 3 (new eight plus legacy/long-text checks); 2328 checks at compact 800×600 and wide 1280×900, effective 100/150/200%, zero warnings in these layout runs. Prior full native runs remain retained. Commit-review `focused-native-ui-summary.json` and `ui-guard-fixed-offscreen-*.log` |
| Actual installed wheel | Built with declared setuptools 84.0.0 in an isolated environment, installed separately, pip check/resource/reopen passed outside checkout with Python isolated mode: commit-review `wheel-guard-fixed.log` |
| Installed source parity | All 170 application files match source bytes: commit-review `installed-source-parity.json` |
| Installed native lifecycle | Three separate processes: Start/Stop (17 checks), restart/same-disk Resume (20), retained Reset/fresh disk/unchanged retained disk (22): commit-review `installed-final-{start,resume,reset}.log`; baseline diagnostics classified explicitly, see below |
| Image integrity | Full SHA-256 of both approved sources and both private test copies; read-only, unchanged: commit-review `final-base-integrity.json` |
| Final guest state | All task guests cleanly stopped; reliable host process enumeration found no QEMU, last verified runtime record stopped and identity absent: commit-review `final-process-state.json` |

Runtime: Python 3.14.7, PySide6/Qt 6.11.2, QEMU 11.1.1; unchanged guest
systemd 257.13-1~deb13u1 and cron 3.0pl1-197. At is absent and not practiced.
Final wheel SHA-256:
`0f644d2681724f183218cd84375bb28bcb783abe6e626d064785e7c73fc1f331`.

Final commit review evidence is retained in:

`/home/drak/.local/state/omarchy-learning-lab/recovery/scheduling-unit-20261005T202426657951Z/commit-review-20261006T001334033393Z`

The original reviewed manifest and all 26 candidate bytes were copied and verified
before review edits; they remain in `original-reviewed.sha256` and
`candidate-snapshot/`. The final manifest records the in-scope corrections below.

The main real-guest matrix is retained at `evidence/scheduling-unit-live-aqjn3_i3`.
Affected lessons were repeated after corrections. The final matrix chooses the
latest matching lesson/command evidence rather than counting older candidate
pins as current. Executed harness/fixture copies, commands, screenshots, exact
acknowledgements, process identity and lifecycle events are retained per run.
Tests execute static developer fixtures only, never lesson JSON.

### What the guest checks established

- Actual disposable user identities, private report contents/owners/modes,
  bounded overwrite behavior, root-identity refusal without report damage.
- Real minute-boundary cron execution, status 127 lookup failure, status 126
  executable denial, repaired cron status 0, exact crontab removal. Collision
  refusal, conditional repeated cleanup and bounded Ctrl-C interruption were
  exercised; protected learner/root/service metadata and sudo policy remained
  unchanged.
- Loaded Type=exec/RuntimeMax/MemoryMax/TasksMax properties. A real two-second
  runtime timeout produced Result=timeout, MainPID=0 and no remaining cgroup
  tasks. Memory/task limits were inspected while loaded, **not pressure-tested**.
  Guest root can override guest-side limits.
- Real elapsed-time Persistent=true catch-up once after multiple missed slots;
  Persistent=false did not catch up immediately. No clock changes. The active
  associated service retained the same MainPID/count and ordered BEGIN/END
  evidence; its timeout wrapper PID differs legitimately from the Bash child.
- Assessment identity failure (2), then output-access failure (1), followed by
  successful calendar and cron output/status, narrow repair and handover.
- Learn hints/self-review versus Challenge guidance refusal, mode-specific
  records, reset/reopen, unchanged bases, normal cross-profile launch refusal,
  running controls after selection changes and owning verified clean Stop.

UI fixtures use mocked disks/process metadata for layout and backup checks;
those checks are not guest-lifecycle evidence. Real native guest evidence is
separate. Profile backup round trips retain supported versions and exclude VM
sessions/disks; no backup migration. Core optional startup remains covered by
regressions and installed resource smoke without needing a registered image.

## Failures and corrections retained

1. The initial overlap pilot (`scheduling-unit-live-7w66rjs2`) redirected a private
   file before sudo in a test assertion. Replaced that assertion with sudo cat
   piped to wc. Expected actual PID/count/events were retained, but the failed
   run is not counted as passing. Its disk/screens/report and clean Stop remain.
2. The initial full run (`scheduling-unit-live-gpawgzji`) entered a list-timers
   pager and timed out awaiting acknowledgement. Added explicit --no-pager to
   new commands. Failed disk/screens/report remain; verified clean Stop.
3. Initial offscreen candidate-digest mismatch (`vm-lessons-ui-ebdn05ks`) was
   correctly rejected after unpublished content changed while cached. Stable
   final-content repeats passed. The aggregate runner reused its log path;
   original failure text is separately recorded from tool output, not claimed
   as an intact original aggregate log. Screens/checks remain retained.
4. Initial wheel preparation used the wrong notices path. Traceback retained;
   corrected isolated build/install/smoke passed. Packaging configuration did
   not need modification.
5. Initial sandbox GPG fixture IPC was blocked. Approved isolated repeats
   passed; no production trust was created.
6. Instruction review found --no-pager inside command -v and an inaccurate claim
   that systemd-run defaults to Type=exec. Removed the flag, explicitly selected
   Type=exec and corrected the hint against Debian systemd-run(1). Both affected
   lessons were repeated in both modes, then installed/native/UI gates repeated.
7. Challenge fault setup had over-escaped quotes. It now matches the exact static
   initial-fault commands already tested on guests; parity is regression-tested.
   It supplies starting conditions, not repairs. Final wheel/UI checks used it.

8. Final adversarial review found that Debian's mode 1730 root:crontab spool is
   not traversable by learner. Unprivileged `test ! -e` falsely reported absence
   for an existing file. Three unpublished lessons now use guest `sudo test`.
   Their catalog digests and static fixtures match. Both modes of all three were
   repeated with the exact installation pipeline refusing a root-owned collision
   and preserving its bytes, then real execution, cleanup and clean Stop.
   Original 44 lessons/pins and controller remain unchanged.
9. A separate backup-tool probe initially supplied an actual newline to the
   key-input helper. Its KeyError and clean cleanup are retained; not a pass.
   Corrected input passed bounded creation, listing, separate restoration,
   corruption checks, cleanup and unchanged-base/clean-Stop assertions.
10. The temporary focused native layout harness initially omitted an older
    metadata fixture required later. Its TypeError/74 checks are retained, not
    counted as passing. Restoring that fixture yielded 223 checks at every scale.
    The full offscreen sequencing wrapper was intentionally stopped; its current
    200% child completed normally. No app or guest was signalled.
11. Two isolated installed runs passed guest assertions and clean Stop, then
    failed an unconditional zero-warning guard. The first harness did not retain
    the exact message, so its precise warning is unknown. Durable logging in the
    repeat captured existing Main.qml Dialog implicitHeight binding loops at
    lines 485/521. Both reproduce on the unchanged baseline, as do cleanup-time
    null-binding diagnostics at Main.qml:10/481, AuthoringDialog.qml:9 and
    VmPreview.qml:8. No application/QML fix is included. The native harness now
    retains every diagnostic with phase/context, visibly reports only those two
    exact baseline live messages and fails on any additional live message.
    Final three-process Start/Resume/Reset passed using the frozen harness;
    existing saved pins/progress and retained disks verified. Baseline diagnostics
    are an outstanding UI issue, not repaired or suppressed. Evidence includes
    `baseline-close-probe/`, failed `installed-native-start.log`, failed
    `installed-warning-probe-resume.log`, and final `installed-final-*.log`.

Pre-correction candidates and all failed native generations remain outside Git.
No force stop, owner guest termination, lock bypass or controller change was
needed. The final diff/hash manifest excludes all profiles, disks, environments,
trust material and generated evidence.

## Outstanding acceptance and release limits

- Baseline dialog binding loops and cleanup null-binding warnings remain
  unresolved. Layout runs had no warnings; native lifecycle acceptance is
  relative to the explicitly reproduced baseline, not a claim of warning-free
  application teardown.
- Native QtTest and QMP input are synthesized. Physical keyboard, accessibility,
  screen reader and exhaustive manual scaling/usability remain unverified.
- Completion is visibly **self-reviewed and unscored**, not guest assessment.
  Resume boots disk state, not RAM or shell jobs. Isolation is not protection
  against hostile malware. VM sessions/disks/reports are excluded from profile
  backup/export.
- No at, mail delivery, cron access-policy, DST-edge, aggregate quota or guaranteed
  host-reserve coverage. These exercises provide partial LPIC-1 107.2 practice;
  earlier scripting/service/logging skills are reinforcement/context only.
- Known baseline warning remains unsuppressed:

```text
gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them
```

No unrelated shutdown change. Public release remains deferred; the unfinished
Qt review and ICU signing-key warning remain explicit release blockers.

## Optional disposable owner check

Use the source launch in [setup.md](setup.md) with new data/config directories
and the verified private runtime above; do not use a real learning profile.
Library → **Real Linux VM preview…** → select **Scheduling & Operational
Automation: Cron and systemd Timers** → a lesson → Learn/Challenge → Start.
Practice in GTK, Stop cleanly, reopen the same profile and Resume. Reset only
after retaining observations; it preserves the old generation. No owner replay
is required for completion of this batch. See [unit guide](scheduling-unit.md).
