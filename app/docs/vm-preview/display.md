# Native GTK console readability

## Default and controls

New graphical launches advertise an **800×600 VGA mode** and enable **View →
Zoom To Fit**, with the guest aspect ratio preserved. At the reviewed Omarchy
200% display, the Lab and guest each had about 701 logical pixels of width; guest
text is larger and has normal proportions. Letterboxing is intentional. Increase
the window's size for more readable text; fit scales the whole guest uniformly.
The VGA `xres`/`yres` properties supply its EDID preferred resolution; they do
not fix the host window at 800×600 or force every guest-selected mode. The pinned
Debian guest selected an 800×600 framebuffer in the native test. Neither desktop
scaling nor the guest image/font configuration is changed.

**Zoom In / Zoom Out disable fit.** In QEMU 11.1.1, leaving fit resets the manual
scale to the preferred scale before adding/subtracting a 25% step. Thus the first
Zoom In can even shrink a window whose fit scale was already above 125%. Manual
zoom survives ordinary redraws/resizing when the window can honor its minimum
size. It is not saved by QEMU across processes. Start/Resume intentionally opens
at the readable, aspect-preserving fit default; it does not restore a custom
manual percentage or window placement.

On this Hyprland version, **manual zoom in a tiled window narrower than QEMU's
minimum size can still distort the drawing and displace menu hit targets**.
Keep fit enabled for tiling beside the Lab. For manual zoom, float/enlarge only
that console using the desktop's existing window controls and leave sufficient
space for its requested size. No application window rule or desktop setting is
installed. Fixing arbitrary manual zoom in undersized tiles would require a
separate QEMU/compositor investigation; it is not claimed fixed here.

## What existing QEMU controls can do

Keep **Zoom To Fit** enabled to avoid the oversized manual minimum in a tile.
QEMU still publishes geometry hints, but the reviewed Hyprland tile can force a
smaller size. **Best Fit** returns to the preferred manual scale, so it is not a
guard. **Fullscreen** removes the side-by-side Lab layout and is not a replacement
for this workflow. The installed 11.1.1 [GTK options](https://github.com/qemu/qemu/blob/v11.1.1/qapi/ui.json)
offer no lock-fit, disable-zoom or minimum-window enforcement option. Changing
`scale` only changes the preferred manual percentage; subsequent Zoom In can again
exceed the tile. The patch does not add a compositor rule, process watcher, custom
QEMU build or window interception. The undersized manual-state limitation remains
explicit in the shared in-app VM guidance, in both Learn and Challenge.

## Reproduction and cause

Native inspection: Omarchy, Hyprland 0.56.2, QEMU/GTK package 11.1.1-1,
GTK 3.24.52-1. Active eDP-1: 2880×1920, scale 2, logical 1440×960. GTK uses native
Wayland. QEMU inherits `GDK_SCALE=2`; Qt-specific variables do not select its
backend. No global environment or monitor configuration was edited.

The old launch used bare VGA and GTK with fit disabled. In a 701×910 logical tile,
View's visible text occupied physical x=92–129 relative to the window, while its
accessible/hit rectangle began at logical x=76 (physical x=152). A native pointer
click at the visible label selected Machine; clicking further right opened View.
Changing geometry/activating fit corrected the drawing. Fresh process tests with
GDK_SCALE unset and with GDK_SCALE=1 reproduced the same initial offset. The
scale override was therefore not the fix. The observed fault correlates with
QEMU's framebuffer-sized minimum and Hyprland's smaller forced tile; this is an
observed interaction, not a fully diagnosed upstream compositor defect.

Baseline manual zoom stayed applied through redraws; an ordinary QEMU reopen
lost the selected zoom/fit state. With fit enabled, resizing changes the visible
scale by design. The installed version's [GTK implementation](https://github.com/qemu/qemu/blob/v11.1.1/ui/gtk.c)
confirms these minimum-size and zoom-mode behaviors.

## Narrow launch-policy revision

Only graphical display options changed:

- `-device VGA` → `-device VGA,xres=800,yres=600`.
- Append `zoom-to-fit=on,keep-aspect-ratio=on` to the fixed GTK display string.

Process verification accepts exactly the full old GTK form or the full new form,
not mixtures, extra options or arbitrary resolutions. This allows the current
controller to safely recognize an older running console. Headless argv is
unchanged. Descriptor containment, permitted block graph, process identity,
private allowlisted QMP, concurrency/lifecycle operations, disk limits, network
absence and sharing/clipboard restrictions remain unchanged. The backend,
image, lesson pins and storage/backup formats are unchanged. An older app rejects
a new graphical process policy; use the current app to Stop that console first.
The argv allowlist is intentionally extended by exactly one display-only form,
not claimed byte-for-byte unchanged. UID/executable inode, boot/PID start time,
full argv digest, before/after identity verification, QMP peer UID/PID and UUID
checks are unchanged. The installed app has not been updated. Running owner consoles are not stopped
automatically; the new default applies on their next user-authorized launch.

## Compatibility review (2026-10-04)

Direct comparison with the verified 23dd87 baseline launcher found exactly two
graphical argv-value differences (VGA properties and GTK fit/aspect flags), and
zero headless differences. Protected manager/process/files/runner/session/registry
code, image metadata and all lesson resources match the baseline bytes. The
policy fingerprint guard was updated only after this review; lifecycle method
fingerprints remain unchanged.

A new disposable fixture used the unchanged baseline source to create Learn and
Challenge sessions and start an old-policy GTK process. The current controller
recognized that real process and stopped it cleanly. Both baseline-created
sessions then booted with the new GTK policy and stopped cleanly. Session and
origin JSON bytes, session/generation IDs, mode, pins and guidance/hint state stayed
unchanged, and the pinned base hash matched. No real learning profile was used.

The requested shared user-facing display paragraph adds `VmPreview.qml` to the
original five candidates, and its UI assertions add `vm_lessons_acceptance.py`: the
reviewed patch now has seven files, with no lesson-content edits. Updated UI suites
passed 75 assertions each at offscreen 100/150/200%, and at native Wayland 200%,
including the display guidance in Challenge, wrapping and horizontal containment,
plus accessible footer controls at the reported Qt sizes 800×600 and 1280×900.
Native QtTest input is not physical-keyboard or accessibility acceptance. Full
regression after the guidance change: 408 passed.

The original recovery snapshot was reverified before this review. An additional
verified source snapshot preserves the five-file candidate before guidance edits:
`vm-display-review-source-20261004T173824Z` (284 tracked/candidate files). Neither
snapshot contains VM disks, profiles, installed environments or Git metadata.

## Initial display verification (2026-10-04)

Recovery snapshot: `vm-display-source-20261004T150912Z` beneath the app's recovery
state directory, verified hashes of all 282 baseline tracked files, no profiles
or disks. Source baseline: `23dd87bf68cc7110d8838c4465a8c3a6269da563`.

- Full regression: **408 passed** (399 existing + 9 display-policy checks).
- Offscreen VM lesson UI: 100/150/200%, 800×600 and 1280×900; passed, no QML
  warnings. These checks do not validate GTK/native rendering.
- Actual native Wayland console at the monitor's 200% scale: first-frame View
  label clicks aligned; default fit at 701×910 beside Lab; fit remained selected
  at 640×480, 800×600 and 1100×800; View popup remained reachable.
- Native manual zoom in a floating console: selected scale survived 1100×800 →
  1200×850 resize and subsequent redraw. OCR bounds for the same guest word
  remained 119×27 physical pixels before/after; menus stayed aligned. Returning
  to fit restored the tiled layout.
- Clean Stop, app close/reopen and disk Resume: same session/generation/pin,
  mode, guidance/hints and self-review state; fit default enabled and visible-label
  View click passed. Direct developer framebuffer capture confirmed 800×600.
  Pinned base hash remained
  `a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d`.
- Tests used a disposable profile/overlay and synthesized pointer/accessibility
  actions. No owner practice VM was running at initial inspection or stopped.
  Developer guest-key synthesis was unreliable in this run and is not claimed as
  successful typing acceptance. Physical keyboard, accessibility, another monitor
  and native 100/150% sessions remain unverified. Arbitrary undersized tiled manual
  zoom remains the limitation above.

The known baseline shutdown warning remains documented, not suppressed:
`gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.
Runtime screenshots/logs and disposable disks remain outside source; no personal
profile, working installation, original proof VM or image was altered.
