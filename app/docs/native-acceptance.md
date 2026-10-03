# Three-lab native acceptance — 1 October 2026

## Target and runtime

Confirmed target: Framework Laptop 13 Pro, hostname `omarchy`; Omarchy OS 4.0.4 (`4.0.4-1`), kernel `7.2.5-3-omarchy`, Hyprland 0.56.2 (`0.56.2-2`, commit `efb50993780079460b0cbed1363e2166a2de1d9f`). Python 3.14.7; Qt, PySide6 and Shiboken6 6.11.2. [Runtime inventory](../evidence/runtime.json)

The native reports verify the Wayland platform, exposed QQuickWindow, OpenGL renderer and compositor `xwayland: false`. The installed Omarchy ethereal palette and readable built-in fallback are both exercised. No system theme, shell, keybinding or monitor configuration was changed.

## Automated results

**63 unit/controller tests pass**, including the previous 45 regressions and 18 firewall/state/validation tests. [Full output](../evidence/firewall-unit-results.txt)

| Scale | Display/runtime | Three-lab keyboard and restart | Layout and scrolling |
| --- | --- | --- | --- |
| 100% | DP-1, measured Qt DPR 1.0 | [PASS · 135 checks + restart](../evidence/firewall-native-100.json) | [PASS · 133 checks](../evidence/firewall-layout-100.json) |
| 150% | eDP-1, compositor scale 2 with process-local `QT_SCALE_FACTOR=0.75`, measured DPR 1.5 | [PASS · 135 checks + restart](../evidence/firewall-native-150.json) | [PASS · 133 checks](../evidence/firewall-layout-150.json) |
| 200% | eDP-1, measured Qt DPR 2.0 | [PASS · 135 checks + restart](../evidence/firewall-native-200.json) | [PASS · 133 checks](../evidence/firewall-layout-200.json) |

Each native walkthrough has **135 passed checks**, followed by a fresh native process that reopens all three labs with their independent applied state, drafts, Challenge modes, retained hint usage and assessments intact. Each layout run has **133 passed checks** at **1024 × 768**, **1180 × 860** and **1260 × 880 logical pixels**. All six final reports record PASS.

Native interaction uses QtTest key events delivered to actual Wayland QQuickWindows: Tab, Enter, Space, Escape, text keys, arrows, Home/End and Alt+1/2/3. No mouse events are used. The separate geometry probe uses direct page/focus selection; it verifies all four Applied values are inside the viewport and untruncated in every lab, firewall fields and buttons become visible when focused, complete selector text fits, and Page Down reaches the third hint. These geometry checks supplement the keyboard walkthrough; they are not independent physical-keyboard evidence.

Test windows use only their own PID in the installed Hyprland Lua dispatcher. Test progress/config is isolated in temporary directories and never replaces learner history. Tests run sequentially to avoid competing GUI focus. An offscreen startup was checked separately and is not counted as native UI acceptance. No Fedora or browser-prototype result is counted.

## Behaviors verified

- Gateway/DNS: baseline faults, draft exclusion, gateway-only score 70, full fix 100, hints, modal reset focus/cancellation, Challenge, archived assisted work, reset of incomplete work and restart.
- Subnet: /28 peer success with gateway/server failure, fixed gateway/DNS, /24 full connectivity and score 100, wider /16 score 70, three recorded hints, idempotent grading, reset, Challenge, history and restart.
- Firewall: DNS and ping succeed initially while TCP 443 is denied by `block-portal` and TCP 22 by the explicit deny default. `connect` parses only supported simulation syntax and names the deciding rule/default.
- Firewall editor: correct a rule or add and move a narrow allow before the deny; preserve drafts until atomic Apply; reject invalid ports without changing applied state; inspect applied rules in a modal dialog and restore focus on Escape.
- Policy outcomes: first-match ordering, source/destination/port matching, allow/deny defaults, narrow 443 success, continued policy denial of 22, loss of full credit for broad source/destination/port permissions, redundant/shadowed rules and equivalent safe final policies.
- History/session: duplicate submissions are idempotent; resets and mode changes preserve complete prior attempts; all three labs resume their exact pending attempts/drafts after switching and fresh-process restart. Records are never automatically pruned.
- Safety/recovery: malformed/oversized packs, unsupported versions/capabilities, invalid selectors/ports, hostile commands, engine import boundaries and guarded executors/sockets, corrupted snapshots with preserved backup recovery, newer progress preserved read-only, schema 1 legacy paths and schema 2 firewall records.

The native testing exposed and fixed repeated Tab navigation in the library, entry into lab content, editor focus order, and focus left in a hidden editor after page changes. Current explicit navigation preserves access to every library card and editable rule field.

## Native screenshots

QQuickWindow captures of actual Wayland rendering; compositor metadata is in the native JSON reports.

- [Initial firewall diagnostics](../evidence/firewall-native-100-firewall-baseline.png)
- [Draft rule editor](../evidence/firewall-native-100-firewall-drafts.png)
- [Applied policy inspection dialog](../evidence/firewall-native-100-firewall-applied-dialog.png)
- [Narrow 443 success and 22 denial with decision explanations](../evidence/firewall-native-100-firewall-corrected-connections.png)
- [100/100 with three recorded hints](../evidence/firewall-native-100-firewall-completed.png)
- [Broad source permission loses isolation credit](../evidence/firewall-native-100-firewall-broad-rejected.png)
- [Retained firewall history](../evidence/firewall-native-100-firewall-history.png)
- [100% minimum firewall layout](../evidence/firewall-layout-100-firewall-1024x768.png)
- [150% minimum firewall layout](../evidence/firewall-layout-150-firewall-1024x768.png)
- [200% minimum firewall layout](../evidence/firewall-layout-200-firewall-1024x768.png)

Debugging `*-failure.png` captures are retained separately and are not the final acceptance screenshots.

## Manual acceptance still open

**Physical-keyboard acceptance is unverified.** QtTest bypasses physical key delivery through Hyprland. Assistive-technology behavior, personal readability and continuous mixed-monitor movement are also not independently verified.

- [ ] Launch from your normal graphical terminal using the README command; keep at least 1024 × 768 logical pixels. Use the existing floating/maximize bindings if tiling allocates less.
- [ ] With a physical keyboard, use Tab/Shift+Tab and Alt+1/2/3 through all three library cards, task briefs, device inspection, settings, console, feedback and history. Verify focus remains visible.
- [ ] Gateway/DNS: repair gateway only, observe IP success/DNS failure and score 70; repair DNS, Apply and earn 100. Verify drafts do not change tests or grading.
- [ ] Subnet: verify peer .21 works at /28 while gateway .1/server fail. Preserve the address and apply /24 for 100; a working /16 must lose prefix credit.
- [ ] Firewall baseline: ping and nslookup work; connect 443 names the deny rule and connect 22 names default deny.
- [ ] Correct the existing rule to allow only source 192.168.50.20/32 → 10.20.0.10/32 port 443. Inspect Applied policy before Apply, then verify 443 works and 22 stays blocked.
- [ ] Add an allow below the deny and confirm it is blocked; move it above and confirm access. Test broad source/port/default permissions and confirm they cannot earn full credit.
- [ ] Try invalid rule input and Apply; confirm every applied value remains unchanged. Close/reopen with unfinished rule text and confirm the draft survives.
- [ ] Reveal three Learn hints without a score penalty; change to Challenge and verify a fresh attempt with hidden hints. Inspect the prior assisted attempt.
- [ ] Open Reset; Escape cancels and restores focus. Confirm Reset archives all prior settings, rules, drafts, console, hints and submissions and restores the initial scenario.
- [ ] Switch labs with pending drafts: cancel and confirm the dialog; return to the same attempt. Close/reopen and inspect all three histories, modes and drafts.
- [ ] Check text, focus, modal dialogs and scrolling at 100%, 150% and 200%; enable the built-in palette and move between monitors.

## Repeat tests and launch

From `/home/drak/Documents/dlms_lab/app`:

```bash
python3 -m unittest discover -s tests -v
python3 -m learning_lab
```

Target-specific GUI commands (run one at a time):

```bash
QT_QPA_PLATFORM=wayland python3 tests/native_acceptance.py --label firewall-native-100 --monitor external
QT_QPA_PLATFORM=wayland QT_SCALE_FACTOR=0.75 python3 tests/native_acceptance.py --label firewall-native-150 --monitor internal
QT_QPA_PLATFORM=wayland python3 tests/native_acceptance.py --label firewall-native-200 --monitor internal
QT_QPA_PLATFORM=wayland python3 tests/layout_probe.py --label firewall-layout-100 --workspace 2
QT_QPA_PLATFORM=wayland QT_SCALE_FACTOR=0.75 python3 tests/layout_probe.py --label firewall-layout-150 --workspace 1
QT_QPA_PLATFORM=wayland python3 tests/layout_probe.py --label firewall-layout-200 --workspace 1
```

This host's external monitor uses workspace 2 and internal monitor workspace 1. Adjust the test arguments if that existing layout changes.

## Model limits and stop point

The portal helper remains DNS plus reachability. `connect` models TCP policy permission, declared listeners and return routing; allowed replies are treated as established. There is no TCP stack, TLS handshake or HTTP response. Rules support only TCP, IPv4 selectors and one destination port or any; no packet capture or real traffic occurs in the engine.

All three original packs are bundled; imports, downloads, full host commands, packaging and desktop integration remain deferred. Filesystem failures use deterministic fixtures, not destructive power-loss experiments. No commits, pushes, packaging, deployment or unrelated settings changes were made.
