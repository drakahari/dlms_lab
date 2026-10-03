# Linux visual clarity revision

Historical report. The [non-modal reference revision](linux-reference.md) replaces
the Lab details dialog and updates editor spacing; the console design is retained.

## What changed

- A Linux-only console contains the **Terminal** heading, **Simulated Linux** badge,
  selectable monospace transcript, current-directory prompt and command entry.
  The console has a stable dark background, visible border and readable text.
  A fresh attempt says **Type help and press Enter.** Input says **Type a command…**;
  Enter and Run invoke the same existing simulation controller.
- **Command reference**, **Virtual file editor** and **Diagnostics** open a distinct
  supporting pane. The terminal stays visible. Closing the pane restores terminal
  space and input focus without discarding drafts. Opening the editor focuses its
  text; ordinary output/theme updates do not take focus from the editor or reference.
- The divider appears only with supporting tools. Drag it, or Tab to it and use
  Up/Down. The existing saved-height mechanism remains; commands, refreshes,
  window resizing, lab changes and process restart retain the preference. Compact
  windows clamp the visible height, restoring it when space returns.
- The sidebar starts with goal, submission progress, current Learn step and one
  Hint control. Only the latest revealed hint appears there. **Lab details** holds
  instructions, objectives, constraints, limitations and all previously revealed
  hints. Challenge hides the guide and hints. The editor surfaces the pack's first
  configuration rule alongside the draft/apply explanation. The simulation
  indicator stays in the header.

Both Linux pack files, both domain engines, saved-record formats, pinning and
storage paths are unchanged. Networking QML behavior is unchanged: the shared
shell adjustments are conditional on Linux. No learner command reaches a host
process, shell, filesystem or network. The supported command set is unchanged.

## Verification

The full regression suite passes **126 tests**, including simulation safety,
malformed commands, valid/invalid repairs, both Linux scenarios, modes, grading,
history, reset, pinning, restart and exports. Mutating tests use isolated profiles.
See [the full log](../evidence/linux-clarity-tests.txt).

Offscreen Qt Quick software rendering with Qt/PySide6 **6.11.2**:

| Checks | 100% | 150% | 200% |
|---|---|---|---|
| Linux clarity, entry/focus, modes, splitter and beginner flow | [153](../evidence/linux-clarity-100.json) | [153](../evidence/linux-clarity-150.json) | [153](../evidence/linux-clarity-200.json) |
| Existing Linux repair, editor, lifecycle and restart | [71](../evidence/linux-clarity-regression-100.json) | [71](../evidence/linux-clarity-regression-150.json) | [71](../evidence/linux-clarity-regression-200.json) |
| Three networking labs | [190](../evidence/linux-clarity-network-100.json) | [190](../evidence/linux-clarity-network-150.json) | [190](../evidence/linux-clarity-network-200.json) |

Each run checks 800×600, 1024×768, 1180×860 and 1280×900 logical-pixel windows.
The focused checks exercise pointer clicks directly into initial input, Enter/Run,
`cd` prompt updates, transcript selection through refresh, tool focus/no focus
stealing, preserved editor drafts, details/hint access, hidden Challenge guidance,
actual QtTest divider drags with repeated output, keyboard resizing, footer/input
bounds, transcript redraw into expanded space, and restoration after resize/switch/restart. Console foreground/background
pairs exceed 4.5:1 contrast; its border exceeds 3:1. This establishes automated
behavior and offscreen geometry, not native or physical-input acceptance.

The compact tests caught and corrected tool padding that obscured the editor and
minimum pane sizes that could overlap the footer. Screenshot review also caught
stale transcript clipping after closing a supporting pane; a plain read-only TextEdit
with explicit scroll bounds fixes it, with rendered-pixel coverage at all four sizes.
Passing Linux runs have no QML
errors. Networking retains its pre-existing focused-item Qt warning, with no
reference, type or binding errors.

Screenshots are **offscreen**, not native evidence:

- [Fresh terminal](../evidence/linux-clarity-100-terminal-first.png)
- [Beginner Learn view](../evidence/linux-clarity-100-beginner-inspect.png)
- [Compact tools and divider](../evidence/linux-clarity-100-small-divider.png)
- [Lab details](../evidence/linux-clarity-100-lab-details.png)
- [200% compact console](../evidence/linux-clarity-200-console-800.png)

Reproduce from `app/`:

```bash
python3 -B -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software python3 -B tests/linux_usability_acceptance.py --label linux-clarity-100 --offscreen
```

For 150/200%, add `QT_SCALE_FACTOR=1.5` / `2`, change the evidence label and add
`--expected-dpr 1.5` / `2`. Existing `linux_service_acceptance.py` and
`framework_acceptance.py` remain regression gates.

## Launch and owner acceptance

Use an isolated profile from the existing Omarchy graphical session:

```bash
cd /home/drak/Documents/dlms_lab/app
linux_review_profile=$(mktemp -d /tmp/learning-lab-review-XXXXXX)
python3 -B -m learning_lab --data-dir "$linux_review_profile/data" --config-dir "$linux_review_profile/config"
```

Import `examples/linux-service-basics.lab.json` and/or
`examples/linux-web-document-root.lab.json` through Library. Retain the profile
path to test restart. Normal launch without the arguments uses personal progress.

Native access remains blocked: connecting to `/run/user/1000/wayland-1` returns
**errno 1: Operation not permitted** ([probe](../evidence/linux-clarity-native-probe.json)).
These checks remain **outstanding**:

- [ ] In a fresh lab, click command entry immediately; type `help`, use Enter and
  Run, and confirm that `cd /` changes the prompt. Select and scroll output.
- [ ] With a physical keyboard, navigate using Tab/Shift+Tab/F6; open both tools,
  edit a draft, close them and confirm appropriate focus without losing edits.
  Verify Lab details/Escape, hints, Learn/Challenge, submit and reset dialogs.
- [ ] Drag the divider with a physical pointer while running repeated commands.
  Resize, switch labs and reopen the same profile; confirm retained sizing.
- [ ] At native 100/150/200% scales, inspect compact and larger windows for contrast,
  wrapping, clipping and readable output; scroll the compact sidebar/editor.
  Check mixed-monitor movement and native file choosers where applicable.
- [ ] Confirm the goal/current-step/reference arrangement is clear to a new learner.

## Recovery and changed files

Verified before edits (including nine older snapshots), and reverified afterward:

`/home/drak/.local/state/omarchy-learning-lab/recovery/linux-clarity-before-20261003T020005511800Z`

Personal progress/configuration remain byte-for-byte unchanged. Original networking
packs, both Linux packs and all Python runtime files remain unchanged from this
snapshot. See [the preservation report](../evidence/linux-clarity-preservation.json).
No migration, Git metadata changes, staging, commit or push was performed.

This revision adds `learning_lab/qml/LinuxConsole.qml` and this report; updates
`LinuxTerminalWorkspace.qml`, `LinuxServiceWorkspace.qml`, `LinuxMissionBody.qml`,
Linux-only layout settings in `Main.qml`/`MissionPanel.qml`, and the focused
`tests/linux_usability_acceptance.py` script. README, framework acceptance and the
historical usability report link to the current evidence. Earlier uncommitted work
is retained. Generated evidence remains local under the existing ignore rules.
