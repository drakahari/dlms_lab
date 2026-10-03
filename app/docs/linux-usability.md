# Linux usability pass

Historical implementation report. The later [visual clarity revision](linux-clarity.md)
supersedes the control labels, sidebar and UI screenshots below.

## Changes

- The **Simulated Linux terminal** fills the Linux workspace by default. There is
  one output buffer and one command input. **Help** and **File editor** open an
  optional lower pane; **Close** returns its space to the terminal. The introductory
  lab has no file editor because its correct configuration is fixed.
- With the lower pane open, drag the visible divider or use the size buttons.
  The chosen logical-pixel height survives command/output refreshes, lab changes
  and restart. Narrow windows clamp the actual height to keep controls reachable;
  the stored preference stays intact and is restored when enough space returns.
- Linux has its own `linux-workspace-layout.json` in the app-owned config directory.
  Existing networking layout values and tools remain separate. Unknown layout
  versions stay untouched. A failed preference write preserves the previous file,
  keeps the selected size in memory, and shows that the setting is temporary.
- The sidebar opens with a short goal, concise objectives and accessible hints.
  Detailed instructions, constraints and limitations expand independently. A compact
  **Simulated environment** indicator stays in the lab header while the sidebar scrolls.

### Reproduced divider defect

The pre-fix QtTest pointer trace grows the terminal from **220 to 320 pixels**
during a drag, then records **220** immediately after release. The layout save
reports `Invalid workspace layout sizes`. QML's JavaScript numbers cross the
`QVariantMap` boundary as doubles, even after `Math.round`; strict Python integer
validation rejected them, emitted a view refresh, and restored the old size.

The fix converts bounded integral doubles at the UI boundary. File validation
still requires integers; fractions, booleans, NaN, infinity and out-of-range values
remain invalid. The same reproduction then retains **320** after release/output,
clamps temporarily in an 800×600 window, and returns to **320** at 1280×900.
The terminal-first workspace is independently tested with repeated output during
actual QtTest handle drags. No claim of native pointer acceptance is made.

- [Before trace](../evidence/linux-divider-before.txt)
- [Boundary-fix trace](../evidence/linux-divider-boundary-fix.txt)

## Two separate Linux scenarios

**Recover a failed web service** remains the original missing-document-root lab.
Its file bytes, content identity, initial fault, rubric, alternatives, and runtime
pin are unchanged. Creating the directory or changing the virtual config still
works; drafts require Apply and the service must load the applied configuration.

**Start your first service** is `examples/linux-service-basics.lab.json`.
It starts **inactive**, with a healthy configuration and accessible document root.
There is no hidden configuration fault. Learn shows only the current step:

1. `systemctl status lab-web` — inspect without changing state; expect inactive/stopped.
2. `systemctl start lab-web` — start with the existing correct configuration; expect active.
3. `systemctl status lab-web` — verify the result; expect active with the intended root/port.

The guide advances from the simulated state and retained command history. It does
not execute commands for the learner or alter the rubric. Starting/restarting
directly can still earn full credit: grading evaluates the final service and loaded
configuration, not an exact command order. The post-start status check drives the
instructional “verified” message, not a hidden grade condition. Challenge hides
the guide and hints. Reset/mode changes preserve prior attempts and restore the
stopped state; reopening restores the current step from the saved attempt.

### Compatibility and safety

The beginner pack explicitly selects Linux engine **contract 2**, behavior
**`linux-service-2`**, domain schema **2**, and capability `service-basics`.
Contract 1 / `linux-service-1` remains available for the original scenario and its
existing pinned attempts. The static resolver accepts those two reviewed versions;
it cannot load a module, execute a pack script or silently upgrade an attempt.

Domain schema 2 adds `initial_service: "inactive"` and `lesson` with a short goal
and three bounded inspect/start/verify explanations and expected results. It requires
an empty `editable_files` list and validates that configuration/root access is healthy
before installation. Actions are allowlisted service operations, not executable text.
Pack identity still covers the entire envelope. New beginner attempts use the existing
pinned record schema 4; no record migration is performed.

The interpreter and virtual filesystem remain dictionary-only simulation. Learner
commands cannot reach a host shell, process launcher, file path or network API.
Networking engines and original packs remain unchanged. Personal progress and
configuration are not used by mutating tests. Scenario/history exports stay separate.

## Launch and import

From the existing Omarchy graphical session, use a disposable profile for review:

```bash
cd /home/drak/Documents/dlms_lab/app
linux_review_profile=$(mktemp -d /tmp/learning-lab-review-XXXXXX)
python3 -B -m learning_lab --data-dir "$linux_review_profile/data" --config-dir "$linux_review_profile/config"
```

Use **Library → Import scenario…** for either:

- `examples/linux-service-basics.lab.json`
- `examples/linux-web-document-root.lab.json`

Keep that profile path to reopen it. Normal launch without those arguments uses
personal XDG data. No dependency installation, packaging or desktop integration.

## Automated evidence

- **126 tests pass:** [full regression log](../evidence/linux-usability-tests.txt).
  New tests cover initial stopped/healthy state, guided steps, modes, final-state
  grading, invalid contracts, original pin preservation, reset/history/reopen and
  exports; layout tests cover QML numeric conversion, independent preferences,
  restart, rejected values, unknown versions and write failure preservation.
- New usability UI: **94 checks per scale** at
  [100%](../evidence/linux-usability-100.json),
  [150%](../evidence/linux-usability-150.json),
  [200%](../evidence/linux-usability-200.json).
  These include dragging with output updates, release retention, 20 subsequent
  refreshes with visible input, four window sizes, restoration after expanding,
  lab switching and a fresh process; terminal-first defaults, disclosures and
  the beginner flow are also exercised.
- Existing repair UI: **71 checks per scale** at
  [100%](../evidence/linux-usability-regression-100.json),
  [150%](../evidence/linux-usability-regression-150.json),
  [200%](../evidence/linux-usability-regression-200.json).
- Networking UI: **190 checks per scale** at
  [100%](../evidence/linux-usability-network-100.json),
  [150%](../evidence/linux-usability-network-150.json),
  [200%](../evidence/linux-usability-network-200.json).
  The existing focused-field Qt warning remains; no QML reference/type/binding errors
  occur in passing reports. These are all offscreen software-rendered runs.

Screenshots (**offscreen**, not native acceptance):

- [Terminal-first troubleshooting view](../evidence/linux-usability-100-terminal-first.png)
- [Small window with a draggable divider](../evidence/linux-usability-100-small-divider.png)
- [Beginner: explained inspection command](../evidence/linux-usability-100-beginner-inspect.png)
- [Beginner: explained start command](../evidence/linux-usability-100-beginner-start.png)
- [Beginner: verified running state](../evidence/linux-usability-100-beginner-verified.png)

Reproduce:

```bash
python3 -B -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software python3 -B tests/linux_usability_acceptance.py --label linux-usability-100 --offscreen --expected-dpr 1
```

For offscreen 150/200%, add `QT_SCALE_FACTOR=1.5` / `2`, change the label and
`--expected-dpr`. Existing repair and networking scripts remain regression gates.
The native form omits `--offscreen`, uses Wayland, and checks the actual display DPR.
Tests create and remove only their own temporary profiles. Generated evidence remains
local under the existing `.gitignore`.

## Native and owner acceptance — outstanding

Native testing is blocked in this environment: connecting to
`/run/user/1000/wayland-1` returns **errno 1, Operation not permitted**.
No native visual or physical-input pass is claimed from these offscreen checks.

- [ ] Drag the divider with a physical pointer; run repeated commands before,
  during and after dragging. Resize the native window and verify restored sizing
  and visible input, including 800×600 and 100/150/200% scaling.
- [ ] Inspect the terminal-first default, readable output, optional tools and
  the persistent simulation indicator; expand/collapse each mission section.
- [ ] Complete both labs with physical keyboard input, including hints,
  disclosures, editor navigation, Learn/Challenge, reset and submission dialogs.
- [ ] Check the beginner explanations and expected results for teaching clarity;
  confirm that “stopped” is not presented as a configuration failure.
- [ ] Reopen the same profile; inspect both labs and their archived attempts.
- [ ] Exercise native import/export choosers, mixed-monitor movement, theme
  readability and assistive technology as applicable.

## Recovery and file scope

Before editing, all eight prior snapshots verified and a new snapshot was created:

`/home/drak/.local/state/omarchy-learning-lab/recovery/linux-usability-before-20261003T011323078562Z`

This preserves the already-uncommitted Linux implementation. Existing snapshots
were not overwritten, and Git metadata was untouched. The final preservation report
is [here](../evidence/linux-usability-preservation.json).

This pass changes the catalog layout boundary/preferences, static runtime resolution,
Linux engine/adapter, Linux-specific QML and conditional shell integration. It adds
`LinuxTerminalWorkspace.qml`, `LinuxMissionBody.qml`, the beginner example,
`test_linux_basics.py`, `linux_usability_acceptance.py` and its restart probe.
The existing Linux acceptance script now opens tools on demand. README and framework/
Linux documentation link to this report. No commit, push, deployment or real-data migration.
