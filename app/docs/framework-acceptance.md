# Framework acceptance — checkpoints 2 onward

## Linux Fundamentals collection — current

Six existing approved packs are available directly from the Library, with no
file-picker import required. Terminal workspace and grading are unchanged.
**183 regression tests pass** (172 prior plus 11 collection tests). All eight
offscreen UI suites passed at 100/150/200%, including collection Start/Continue,
draft confirmation, reset/modes and fresh-process restart.

[Collection verification](linux-fundamentals.md) distinguishes source/resource
and staged-package checks from the actual isolated wheel-build attempt. Fetching
the declared `setuptools` dependency failed because `pypi.org` could not resolve;
no wheel was produced or installed, so that verification gap remains open.
The owner reports that the Library collection works great. This records successful
functional review, not exhaustive native acceptance. Physical keyboard,
accessibility, native scaling and mixed-monitor checks remain outstanding.

## Permissions authoring and directory scenario — current

[Authoring guide](permissions-authoring.md), reusable template and directory
scenario are delivered with an opt-in contract-3 extension of the existing
permissions engine. This required application changes; it is not evidence that
the prior contract supported directory labs through data alone. QML is unchanged.
See [scope, tests and owner checklist](directory-permissions.md).

**172 regression tests pass**, including both directory scenarios and all prior
regressions. The owner reports reviewing the new directory lab and says it looks
good. This is owner-reported visual approval, not a claim that every native check
passed. Native physical keyboard, accessibility, choosers and display-scale checks
remain outstanding. See the [commit review](permissions-contract-review.md#local-commit-review)
for the current automated checks.

## Beginner Linux permissions — current

See [permissions architecture and acceptance](linux-permissions.md). **Restore
access to your file** opts into navigation contract 2 and mutable virtual file
modes. Existing packs retain their original runtimes and behavior; no QML layout
changes or personal-data migration were made.

**154 regression tests pass**. Offscreen permissions checks pass at 100/150/200%
(62 workflow checks and 10 fresh-process checks per scale), along with the five
existing UI suites. The owner reports on **3 October 2026** that the permissions
lab **worked well**. This records a successful owner test without specifying the
complete workflow, input device, display scale or assistive technology used.
The agent's recorded native Wayland probe was blocked with errno 1. Unverified
physical-keyboard, accessibility, native-scale, chooser and compositor checks
remain **outstanding**. Previous positive reviews below apply to the existing
interface and navigation lesson.

## Linux navigation extension — current

See [navigation architecture and acceptance](linux-navigation.md). The new
**Find your way around Linux** pack uses a separate trusted navigation engine,
the unchanged existing virtual filesystem/parser, and the approved Linux layout.
It has action evidence and a final-directory objective without service mechanics.

Fresh regression result: **140 tests passed**. New offscreen Qt runs pass **89
checks plus 10 fresh-process checks per scale** at 100/150/200%; all four existing
UI suites also pass at those scales. Native Wayland access is still blocked with
errno 1 (`Operation not permitted`) in the recorded probe. The owner now reports
that the navigation lab **looks good**. This is a positive visual review of the
new lesson; no monitor, scale or input-device coverage was specified. Unverified
native scaling/workflows, physical-keyboard input, native choosers and accessibility
remain **outstanding**. Prior visual approval below applies to the existing layout.

## Owner visual approval — 2 October 2026

The owner explicitly approved the **current visual layout** and authorized the
local Linux simulation/usability commit in this session. This records owner
visual approval only; it does not establish which monitor, scale, input device
or assistive technology was used.

Physical-keyboard end-to-end acceptance, accessibility/screen-reader behavior,
native file choosers and dialogs, compositor/mixed-monitor interactions, and
unverified native scaling and pointer workflows remain outstanding. Current Linux
QtTest evidence is offscreen; historical native networking evidence does not
validate these Linux changes.

The commit-readiness rerun passes **126 regression tests** and all four UI suites
at 100/150/200% offscreen scaling: **85 reference/editor**, **153 console/beginner**,
**71 Linux lifecycle**, and **190 networking** checks per scale. Mutating tests use
isolated temporary profiles. Generated logs/screenshots remain excluded local
artifacts under `app/evidence/linux-commit-*`; the test scripts and useful reports
are included in source control. Local evidence links in the Linux reports are
reproducible artifacts and may be absent from a fresh checkout.

## Non-modal Linux reference revision — current

See [the current reference/editor report](linux-reference.md) for combined-pane,
focus, scrolling, draft preservation and scaling checks. The current visual layout
has owner approval as recorded above. Unverified native and physical-input checks
remain outstanding; automated evidence is offscreen only.

## Linux visual clarity revision — historical

See [the current report](linux-clarity.md) for the bounded console, supporting tools,
Lab details, focused UI checks and recovery verification. Current acceptance is
**offscreen only**; native visual and physical-keyboard checks remain outstanding.

## Linux usability follow-up — historical

The terminal-first Linux view and separate beginner scenario are covered by
[the usability report](linux-usability.md). The full suite now passes **126 tests**.
Current UI evidence remains **offscreen only**. The new usability runs cover real
QtTest pointer dragging with output updates, release/refresh/resize retention,
cross-lab and fresh-process sizing, disclosures, and the beginner walkthrough.
Historical native results below do not validate these changes. Physical input,
native visual/scale checks and file-picker acceptance remain outstanding.

## Initial Linux-service extension — historical

The application now includes a separate trusted Linux service domain and an
importable missing-document-root scenario. See [its model, commands, results and
hands-on checklist](linux-service.md). The fresh full suite passes **118 tests**.
Linux Qt UI runs pass **71 checks each at 100/150/200% offscreen scale**, including
both fixes, editor focus/size limits, drafts, modes, grading, switching, reset and
fresh-process resume. Original networking UI regressions pass **190 checks each**
at those three offscreen scales. These are software-rendered offscreen tests.

**Current native acceptance is outstanding.** This execution environment cannot
connect to `/run/user/1000/wayland-1`: `Operation not permitted` (errno 1).
Wayland initialization failed; no current native screenshots were obtained.
Physical keyboard, native file pickers, compositor scaling/movement and subjective
visual/accessibility review remain owner checks. Historical native evidence below
does not establish acceptance of the changed application.

All eight recovery snapshots reverified. Original personal progress/configuration
match the fresh pre-change snapshot. Networking engine and original pack bytes
still match the historical freeze. The full-application frozen-code assertion was
replaced with that preservation check because a new trusted domain changes the
application; the historical manifest itself was not rewritten. The registry test
now expects the two explicitly shipped engines. Other existing regressions remain.

Current reports and screenshots are linked in [Linux service results](linux-service.md#delivery-results).
They are generated local artifacts ignored by the existing `.gitignore`.

## Target and test isolation

Target: `omarchy`, Framework Laptop 13 Pro, Omarchy 4.0.4-1,
kernel 7.2.5-3-omarchy. Python 3.14.7; Qt/PySide6/Shiboken6 6.11.2.
Native runs use the installed Wayland session and OpenGL renderer. DP-1 provides
100%; eDP-1 provides 200%; `QT_SCALE_FACTOR=0.75` on eDP-1 tests measured DPR 1.5.
No monitor configuration, theme, shell settings, packages or credentials changed.

Every mutating test uses a fresh temporary profile. Native windows belong only
to the test process, and captures use `QQuickWindow.grabWindow()`. QtTest events
are sent to the real native window; they **do not verify physical keyboard input
through the compositor**. No browser or Fedora evidence is counted as native.

## Acceptance status audit — 2 October 2026

The development-baseline audit reran the full suite: **102 tests passed**.
[Fresh regression log](../evidence/baseline-regression-tests.txt).
All seven recovery snapshots, including the completed framework and new
development baseline, were verified against their manifests, including source,
configuration, progress and specification. [Recovery verification](../evidence/baseline-recovery-verification.json).
All 31 application files still match the completed source snapshot and code freeze.

The native results below are **recorded evidence from the completed framework
work**, reviewed during this audit. Native GUI tests were not rerun in this audit.
No unchecked owner item has been promoted based on those automated results.

| Check | Verified evidence | Still requires owner input |
| --- | --- | --- |
| Regression and compatibility | Fresh 102-test suite; original labs, packs, pins, lifecycle and persistence fixtures | No owner action needed for the automated result |
| Native rendering and geometry | Recorded Wayland/OpenGL runs at measured 100/150/200%; four logical sizes; screenshots and focused Applied-label bounds | Personal readability, compositor interactions, continuous mixed-monitor movement |
| Navigation and dialogs | QtTest key events in native windows; F6 regions, original lab flows, reset cancellation and mode confirmation | Physical keyboard delivery, complete physical dialog/focus workflow; pending-draft submission dialog interaction |
| Instructions and pane access | QML rendering and geometry; field scrolling; imported Library-card focus visibility; layout persistence tests | Pointer split-handle interaction, physical scrolling/resizing, subjective access to long briefs |
| Modes, reset, history and reopen | Unit/controller checks plus native fresh-process restart; hints and archives preserved | Owner end-to-end reopening workflow remains unchecked |
| Pack and personal export | Transfer API tests, invalid input rejection, idempotence, exact scenario bytes, separate personal export | Native file choosers, overwrite/cancel dialogs, UI clarity of personal-data export |
| Assistive technology | No end-to-end screen-reader evidence | Screen reader, accessible reading order and labels |
| Second domain | Networking-only frozen-code proof | A separate trusted domain engine and scenario are needed to establish broader reuse |

The live profile now contains newer progress and an imported proof pack. Those
files were preserved in a new development-baseline snapshot; an imported file
on disk is **not** evidence of physical-keyboard or native-picker acceptance.

## Recorded automated evidence

- [Full unit and regression log](../evidence/framework-unit-tests.txt): engine,
  firewall, legacy storage, identity, networking adapter, portable validation,
  repository, pins, workspace state and frozen-code proof.
- Framework runs: [100%](../evidence/framework-native-100.json),
  [150%](../evidence/framework-native-150.json),
  [200%](../evidence/framework-native-200.json).
  Each passed 191 checks: original gateway/subnet/firewall keyboard workflows,
  hint and mode archives, grade/reset/dialog focus, broad-rule rejection,
  geometry at 800×600, 1024×768, 1180×860 and 1280×900 logical pixels,
  every focused settings field and Applied value, firewall scrolling,
  fallback palette, scoped headings, pending drafts and fresh-process restart.
- Portable native proof: [100%](../evidence/proof-native-100.json),
  [150%](../evidence/proof-native-150.json),
  [200%](../evidence/proof-native-200.json).
  These use the final frozen code, including Library/History focus scrolling.
- Separate offscreen evidence: [workspace](../evidence/framework-offscreen.json)
  and [portable proof](../evidence/proof-offscreen.json). These are not native acceptance.
- [Historical application freeze](../evidence/proof-code-freeze.json): hashes of every file
  under `learning_lab/` except bytecode caches, captured **before** authoring
  `examples/resolver-misdirection.lab.json`. At that checkpoint, tests verified
  the same complete file inventory/hashes afterward. The Linux extension's
  preservation regression is scoped as described above.

The new scenario uses CLIENT-7, EDGE, INVENTORY and ORDERS on different networks.
Both server IPs and DNS replies work initially; DNS answers swap the endpoints.
Only DNS is editable. The baseline scores 40/100; selecting the correct resolver
scores 100/100 in both modes. Gateway portable conversion and this scenario were
imported, graded, saved/reopened and exported/reimported without changing any
application source. Existing bundled files and saved-record bytes remain intact.

### Screenshots

- [Original lab workspace, 100%](../evidence/framework-native-100-gateway-dns-1280.png)
- [800×600 Settings and Applied values](../evidence/framework-native-100-gateway-dns-800.png)
- [Firewall editor at 150%](../evidence/framework-native-150-firewall-editor-800.png)
- [Gateway submission review](../evidence/framework-native-100-gateway-review.png)
- [Imported Library card at 800×600](../evidence/proof-native-100-imported-library-800.png)
- [Different topology and baseline DNS diagnostics](../evidence/proof-native-200-misdirection-diagnostics.png)
- [Portable Learn review](../evidence/proof-native-100-misdirection-learn-review.png)
- [Portable Challenge review](../evidence/proof-native-200-misdirection-challenge-review.png)
- [Pinned portable history](../evidence/proof-native-200-portable-history.png)

Some panes are intentionally scrollable; screenshots show their current scroll
positions, not every instruction at once. Settings tests separately verify all
focused fields and their Applied labels. Library navigation scrolls focused
cards into view.

### Reported runtime warnings

Qt's desktop portal reports `Connection already associated with an application
ID` during native startup. The application still renders and the native flows
pass; native chooser interaction is outstanding, so this is not evidence that
portal-backed dialogs work. Framework geometry probes also report a Qt warning
when a focused field changes from editable to fixed during lab switching.
The tested focus paths remain usable. No QML reference, type or binding-loop
errors remain in passing reports.

## Manual acceptance checklist — outstanding until owner confirms

Every box below remains **outstanding**. Overlap with automated checks is
intentional: these boxes represent the owner's physical-input and visual review,
not a denial of the automated evidence above. No owner confirmation has been
recorded. The portal warning remains unresolved for native file pickers.

Use a temporary profile to avoid changing personal history during review:

```bash
cd /home/drak/Documents/dlms_lab/app
acceptance_root=$(mktemp -d /tmp/learning-lab-owner-XXXXXX)
python3 -B -m learning_lab --data-dir "$acceptance_root/data" --config-dir "$acceptance_root/config"
```

Keep that path to reopen the same test profile. Do not delete personal data to
reset a test. No system-wide install or packaging is needed.

- [ ] **Physical keyboard:** complete investigate → edit → Apply → diagnostics →
  Submit → Review for each original lab using only physical keys. Verify
  Tab/Shift+Tab, Enter/Space, arrow selectors, Alt+1/2/3 and F6/Shift+F6.
- [ ] **Dialogs and focus:** Escape cancels reset, mode and pending-draft
  submission; focus returns visibly. Confirming archives drafts and hint usage.
  Switching labs with invalid edits preserves them when returning.
- [ ] **Mission and panes:** full brief/objectives/constraints remain accessible
  while working. Resize panes with keyboard +/− and pointer split handles;
  restore defaults. Scroll instructions and diagnostics with PageUp/PageDown.
- [ ] **Native visual review:** inspect 800×600, 1024×768, 1180×860 and 1280×900
  at 100/150/200% where the display permits them. Check focus rings, readability,
  complete Applied values, all firewall controls, review and history.
- [ ] **Continuous mixed-monitor movement:** move the real window between
  differently scaled displays and verify focus, geometry and text remain usable.
- [ ] **Native file pickers:** import `examples/gateway-dns.lab.json` and
  `examples/resolver-misdirection.lab.json`; cancel/reopen a chooser; export
  scenario to a new local filename and reimport. Test an invalid JSON file and
  confirm a clear error. Verify overwrite/cancel behavior on a disposable file.
- [ ] **Privacy distinction:** scenario export contains no attempt information;
  History's individual attempt export clearly represents personal evidence.
- [ ] **Reopen:** close normally and reopen the same temporary profile; verify
  selected version, modes, hints, scores, invalid drafts, pending command and
  both current/prior attempts. Test built-in colors and theme readability.
- [ ] **Assistive technology and subjective UX:** check accessible labels,
  reading order, screen reader behavior if used, and comfort of the responsive
  layout. Automated geometry does not replace this review.

## Reproduction commands

```bash
python3 -B -m unittest discover -s tests -v
QT_QPA_PLATFORM=wayland python3 -B tests/framework_acceptance.py --label framework-native-100 --monitor external --expected-dpr 1
QT_QPA_PLATFORM=wayland QT_SCALE_FACTOR=0.75 python3 -B tests/framework_acceptance.py --label framework-native-150 --monitor internal --expected-dpr 1.5
QT_QPA_PLATFORM=wayland python3 -B tests/framework_acceptance.py --label framework-native-200 --monitor internal --expected-dpr 2
QT_QPA_PLATFORM=wayland python3 -B tests/pack_proof_acceptance.py --label proof-native-100 --monitor external --expected-dpr 1
QT_QPA_PLATFORM=wayland QT_SCALE_FACTOR=0.75 python3 -B tests/pack_proof_acceptance.py --label proof-native-150 --monitor internal --expected-dpr 1.5
QT_QPA_PLATFORM=wayland python3 -B tests/pack_proof_acceptance.py --label proof-native-200 --monitor internal --expected-dpr 2
```

Run native tests sequentially; they briefly focus their own window. Each chooses
an existing active workspace on the selected monitor. The scripts do not alter
monitor settings and clean up only their own temporary profiles.
