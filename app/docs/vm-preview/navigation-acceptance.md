# VM lesson navigation review

## Baseline and installed-build comparison

Reviewed repository: `/home/drak/Documents/dlms_lab`, branch `main`, HEAD
`dbcc237dd37af7e4b341781225d58e7525ff8324`. The checkout and index were clean
before this task. The source has nine VM units and 76 lessons.

The app-menu launcher resolves to the older installation
`20261003T162404Z-044bf565`. Its package reports 0.1.0, as does the checkout, but
it has no `vm_preview` module or `VmPreview.qml`. Thus the version number alone
does not establish parity. No Lab was running at initial inspection; the owner's
last launch cannot be attributed to this installed build. Reproduction used the
frozen baseline checkout, not the older installed app. The installation was not
updated.

Read the previous [storage acceptance report](storage-acceptance.md). Its layout
checks do not establish dropdown lifetime or highlighted-row contrast.

## Reproduction and owner-issue checklist

Native environment: Omarchy 4.0.4, Linux 7.2.5-3-omarchy, Hyprland 0.56.2,
Python 3.14.7, PySide6/Qt 6.11.2, Wayland, GTK3 platform theme, Qt Quick Basic
controls and software rendering. Monitors: DP-1 1920×1080 at scale 1;
eDP-1 2880×1920 at scale 2. No global settings changed.

| Reported issue | Demonstrated cause / limit | Repair | Evidence |
| --- | --- | --- | --- |
| Menu closes while navigating | Open lesson popup; use Down without activating; leave it open through the five-second poll. At 10.380 s, the baseline trace records popup hidden, selector disabled and busy=true. Polling used the same disabled state as a mutation. Rebuilt models also introduced unnecessary model notifications. | Expose the existing read-only refresh flag; keep selectors enabled during polling, with stable ID/title models. Actual mutations still disable selectors and VM actions. | `before-trace-final.json`; held real asynchronous refresh and production timer tests at all scales. |
| Highlighted text unreadable | Baseline actual delegate text #060b1e on #1a1a1a. Basic ItemDelegate uses palette.light for its highlight background, whereas this app paired highlightedText with its accent elsewhere. | Explicit paired highlight/text colors in a local ComboBox component; normal, hover, selected, focused and disabled states tested. | Native before/after captures; actual delegate color contrast, not widget-existence assertions. Minimum tested enabled contrast 5.647:1. |
| Collection and lesson relationship unclear | Previous selectors were labelled independently; no fixed selected-lesson summary beside Start. This is a design observation, not a measured learning-outcome claim. | Numbered Collection → Lesson → Mode → Start labels, scoped lesson count, VM/simulator explanation and fixed summary. Keyboard focus brings selectors into view. | Exact-ID collection/lesson/mode tests; summary/action geometry at 800×600 and 1280×900. |

Baseline native screenshot geometry was 800×914 logical pixels at DPR 2 after
compositor configuration; it is not a size-matched comparison. Final tests assert
actual 800×600 and 1280×900 logical dimensions at every effective scale.

## Changes and compatibility boundary

The existing ComboBox navigation and activation machinery remains in use.
`LabChoice.qml` provides explicit readable delegates, wrapping, scrollbar space,
bounded popups and visible focus. Escape, outside click and intended activation
close the popup. Selection never boots a guest. Stale/empty selections cannot
enable Start or Reset. Activation during polling queues the exact intended ID.

The sole Python application change is the read-only `refreshing` field in
`VmBridge.view`. An inverse-hash test proves that removing this field restores
the exact baseline bridge bytes. Six existing protected-file tests update only
that bridge digest. Controller, runner, manager, sessions, registry, image
descriptors, lesson JSON, simulation engines, collection resources, persistence
and backup code remain byte-identical. No lesson, pin, bounds or safety-policy
changes are included.

## Final validation

| Check | Result and evidence |
| --- | --- |
| Full non-browser regression suite | **621 passed**, `regression-final-candidates.log`. |
| GNU developer fixtures | **44 passed**, `gnu.log`; engines unchanged afterward. |
| Native Wayland navigation | **379 checks per scale**, effective DPR 1 / 1.5 / 2; both sizes and current Omarchy + built-in fallback palettes. `native-nav-{100,150,200}-header-focus-final.log`. |
| Offscreen navigation | **378 checks per scale**, both sizes and palettes. `offscreen-navigation-{100,150,200}-header-focus-final.log`. Separate from native rendering. |
| Existing VM lesson/session UI suite | **207 checks at each offscreen scale**; final-layout repeat at 100% also passed, `lifecycle-wiring-footer-final.log`. Selection, modes, session reopening, missing-disk messaging and backup exclusions covered. |
| Action routing | Actual QML buttons against an isolated QObject fixture: Start exact lesson/mode, Resume pinned session mode, Stop running owner rather than selected lesson, Reset cancellation and explicit confirmation. This is UI wiring evidence, not native guest lifecycle evidence. |
| Isolated installed wheel | Built without network/new dependencies; pip check and installed smoke passed. Outside-checkout parity for **199 packaged resource files**, nine units/76 lessons and icon; copied navigation script under `python -I` passed **374 checks**. Wheel SHA256 `a688f4b08565af5da7686e6b5ccfe5f073ad97ef39aa15ae919df8bdc8a3f6bb`. |
| Independent review | Separate read-only reviewer inspected event handling, stable models, exact-ID routing, styles, focus/scroll handling, lifecycle fixture boundary and simulator proposal. No blocking finding; limitations below retained. |

Tests cover mouse and key selection, hover, selected/normal/disabled contrast,
focus borders, popup persistence/highlight through polling, activation queued
during polling, mutations disabling menus, Escape/outside click, repeated
opening/closing, 12-lesson lists, single/long/unbroken/empty/stale fixtures and actual
scrollbar dragging. No test guest was launched for this UI task. Native input
was QtTest-generated, not a physical-keyboard or screen-reader certification.

## Retained failures and limitations

- Earlier synthetic mouse-hover/keyboard interleaving produced an unexpected
  highlight change in one native run. Independent keyboard cases now wait for
  pointer delivery and for the pointer to leave delegates. The original event
  sink/timing is not established; physical mixed-input acceptance remains open.
  A later native repeat closed the popup with window activation and selector focus
  both false, rather than a polling-induced disable. Final tests move the pointer
  to the dialog header and retain detailed periodic focus/busy transitions; no
  claim is made that a source change fixes external focus loss.
- Synthetic wheel input after mode activation sometimes emitted no scroll
  changes despite enabled scrolling and a closed mode popup. Later gestures
  moved it. Right-lane, left-inset and focus diagnostics are retained; no source
  wheel fix is claimed. Final mouse scrolling uses an actual scrollbar-thumb
  drag and asserts visible target, settled scrolling and actual popup opening.
  It does not retry failed wheel input until a desired result appears. Physical
  wheel/trackpad behavior remains unverified.
- The long-unbroken-title fixture initially failed actual width/clip assertions;
  `Text.Wrap` now preserves word boundaries where possible and splits oversized
  tokens when needed, without shrinking fonts. Matching native/offscreen/wheel
  reruns pass. The failed pre-fix result remains in `unbroken-title-before.log`.
- Early harness setup errors, incorrect teardown/profile-directory assumptions,
  old Hyprland dispatch syntax, a wrong relative path in an installed-script copy,
  and all failed runs remain in recovery evidence. No failure is counted as a pass.
- A sandboxed full run failed 48 signing-fixture tests at setup because isolated
  gpg-agent could not start (573 tests ran, two setup errors). Normal approved
  host execution passed all 621; production trust was not changed.
- Qt/GTK portal warning reproduced on the unchanged baseline and remains visible:
  `Failed to register with host portal QDBusError("org.freedesktop.portal.Error.Failed", "Could not register app ID: Connection already associated with an application ID")`.
- Full-suite shutdown warning remains: `gc:0: ResourceWarning: gc: 5 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.
  Earlier baseline runs recorded the same warning family with a different count.
  This task does not claim the warning resolved or infer data loss from it.
- Only the current sanitized Omarchy palette and built-in fallback are accepted
  here; arbitrary custom palettes, physical keyboard, screen-reader use and
  broader native accessibility remain outstanding. No new VM lifecycle claim
  is made; accepted unchanged controller evidence is retained.

## Evidence, recovery and handoff

Local evidence root:
`~/.local/state/omarchy-learning-lab/recovery/menu-navigation-20261011T010814339862Z`.
`source-before/` and `source-before.json` preserve and verify all 454 tracked
baseline files. `protected-source-check.json` records unchanged protected source.
No personal profile was backed up or changed. All test profiles and screenshots
are outside source; excluded evidence and wheel environments are retained.

Before: `before-lesson-final.png`, `before-unit-final.png`,
`before-trace-final.json`. After: `navigation-kcu47c12/omarchy-1280-vmLessonChoice.png`
(100%); corresponding final 150/200% captures are in the native reports.
`menu-navigation-final.sha256` is the complete candidate path/hash manifest.

For a disposable review, launch the checkout with `python3 -B -m learning_lab`
and its documented `--data-dir`, `--config-dir`, `--vm-home` overrides. Use fresh
directories, open **Real Linux VM**, and navigate the numbered selectors without
pressing Start. No real guest is needed to review menus. See the separate
[LPIC-2 simulator proposal](../lpic-2-simulator-proposal.md); it adds no scenarios.

Changes remain unstaged and uncommitted. The installed application, real profiles,
owner sessions, guest images and host settings are untouched. Test windows close
normally; final process inspection confirms task-process cleanup separately.
