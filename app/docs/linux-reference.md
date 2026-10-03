# Non-modal Linux reference and editor spacing

## Behavior

**Lab details ▾** expands the existing mission area into a reference pane. It has
its own scroll view and collapse/Close controls. There is no popup, modal focus
scope, backdrop or automatic dismissal. Clicking/typing in the terminal, changing
tools, navigating or switching Linux labs leaves it open within the window.
Switching labs updates the reference and starts its scroll at the top.

On wide windows, the reference sits beside the terminal and editor. Drag the
existing vertical framing divider to resize its width. It uses the mission column
instead of adding a third narrow column: the compact mission has a 260-pixel
minimum width, and the expanded reference has a 320-pixel minimum. Existing
networking size rules are unchanged.

Below 1000 logical pixels, reference and workspace stack vertically. Drag the
horizontal framing divider to adjust the reference height. With both reference
and tools open, the duplicate top tool launcher row is hidden; all tools remain
available through the supporting pane's tabs. This leaves room for the reference,
terminal output and command entry, and independently scrolling editor at 800×600.
The terminal's existing colors, font, prompt, bounded transcript and entry remain.
The smaller compact terminal height is correctly saved after a divider drag.

The editor uses consistent 12-pixel content/group margins, 10-pixel code padding,
and separate draft/applied groups. The code font remains 14 pixels. The applied
version is collapsed initially and expands using **Applied version ▸**. Tab leaves
the draft for that disclosure; expanded applied text remains selectable. The
editing rule and Apply/restart explanation stay concise. Closing tools, switching
tabs, resizing or collapsing the applied version does not apply or discard drafts.

## Results

- Full suite: **126 tests passed** ([log](../evidence/linux-reference-tests.txt)).
- Qt/PySide6 6.11.2, software rendering, **offscreen only**:

| UI checks per run | 100% | 150% | 200% |
|---|---|---|---|
| Non-modal reference/editor combinations | [85](../evidence/linux-reference-panels-100.json) | [85](../evidence/linux-reference-panels-150.json) | [85](../evidence/linux-reference-panels-200.json) |
| Existing console/beginner/sizing/restart | [153](../evidence/linux-reference-100.json) | [153](../evidence/linux-reference-150.json) | [153](../evidence/linux-reference-200.json) |
| Linux repair/editor/lifecycle regression | [71](../evidence/linux-reference-regression-100.json) | [71](../evidence/linux-reference-regression-150.json) | [71](../evidence/linux-reference-regression-200.json) |
| Three networking labs | [190](../evidence/linux-reference-network-100.json) | [190](../evidence/linux-reference-network-150.json) | [190](../evidence/linux-reference-network-200.json) |

Checks cover 800×600, 1024×768, 1180×860 and 1280×900 logical windows;
direct pointer entry and keyboard Tab traversal with details open; Escape not
closing reference; simultaneous reference/editor/terminal; independent scrolling;
focus and draft preservation; applied disclosure navigation; pointer resizing in
both orientations; compact terminal drag retention; and mode/lab changes. Existing
regressions still exercise grading, hints, archives, reset, restart and exports.
Linux reports have no QML errors. Networking has the previously documented focused
item warning, with no reference/type/binding errors.

Offscreen screenshots:

- [Wide reference + terminal + editor](../evidence/linux-reference-panels-100-wide-details-editor.png)
- [Compact combined layout](../evidence/linux-reference-panels-100-combined-800.png)
- [Editor padding](../evidence/linux-reference-panels-100-editor-padding.png)
- [200% compact layout](../evidence/linux-reference-panels-200-combined-800.png)

The updated repair UI checks navigate the Applied disclosure and verify cursor
visibility in the independently scrolling editor; long-file start/end navigation
remains covered. No font-size reduction is used to fit text.

## Owner approval and outstanding native checks

On 2 October 2026, the owner approved the current visual layout and authorized a
local commit. No physical-keyboard, accessibility, native scale/monitor, picker or
complete native workflow verification was stated. Those checks remain outstanding;
the approval does not convert offscreen automation into native acceptance.

The existing Wayland socket `/run/user/1000/wayland-1` remains inaccessible:
**errno 1, Operation not permitted** ([probe](../evidence/linux-reference-native-probe.json)).
Offscreen QtTest events do not establish native visual or physical-input acceptance.

- [ ] Open Lab details, type commands and use Enter/Run without dismissing it.
- [ ] Use physical Tab/Shift+Tab/F6, independent scrolling and both resize handles;
  confirm details never traps focus, dims the app or covers command entry.
- [ ] Edit a virtual draft with details open, switch tool tabs, expand/collapse
  Applied, and confirm the draft is retained with readable spacing and rules.
- [ ] Check wide and compact native windows at 100/150/200%; confirm readable
  wrapping, visible input and useful pane sizes. Review file choosers/monitor moves
  and assistive technology as applicable.

## Launch

From the Omarchy graphical session, use an isolated review profile:

```bash
cd /home/drak/Documents/dlms_lab/app
review_profile=$(mktemp -d /tmp/learning-lab-review-XXXXXX)
python3 -B -m learning_lab --data-dir "$review_profile/data" --config-dir "$review_profile/config"
```

Import either Linux scenario from `examples/`. Keep the profile path to test
reopening. Normal launch without these flags uses personal progress.

To repeat the focused automated checks from `app/`:

```bash
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software python3 -B tests/linux_reference_acceptance.py --label linux-reference-panels-100 --offscreen
```

Use `QT_SCALE_FACTOR=1.5` / `2` and `--expected-dpr 1.5` / `2` for the other scales.

## Recovery and scope

Before edits, ten previous snapshots were verified and this new copy was verified:

`/home/drak/.local/state/omarchy-learning-lab/recovery/linux-reference-before-20261003T023409962311Z`

The final [preservation report](../evidence/linux-reference-preservation.json)
records snapshot verification, unchanged personal progress/configuration and exact
changed files. No engine, pack, schema, safety boundary or persistence implementation
changed. Prior uncommitted work is retained. No staging, commit, push or Git metadata
change was performed.

Changes are confined to Linux reference/editor/console QML, conditional shell/mission
layout, focused acceptance checks and documentation. `LinuxReferencePanel.qml` and
`tests/linux_reference_acceptance.py` are new. Existing Linux repair tests now operate
the Applied disclosure. Networking behavior and layouts passed their existing gates.
