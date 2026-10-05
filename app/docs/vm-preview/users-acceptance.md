# Users unit acceptance

## Scope and baseline

Baseline `e72dc7297c8e21cc9452af34b75594cb39a3f7ee` was clean on main,
pushed without force, and live origin/main verified at that exact hash. This source
push did not publish an image. The new unit is unstaged and uncommitted.

Recovery/evidence root:
`/home/drak/.local/state/omarchy-learning-lab/recovery/users-unit-20261005T181156411096Z`.
All 368 tracked baseline files were copied and reverified. No real profile,
working installation, original image, owner guest or host settings were changed.

The only production Python change is the authorized registry bound: five units,
sixteen lessons per unit, forty-four total. Six units, seventeen per unit and
forty-five total are rejected. The eight new routes use only the exact administrator
image. Original 36 lesson resources, units, image descriptors and controller files
match baseline bytes. Removing the new catalog entries reproduces the complete
baseline catalog digest `4c4a107cc57f49b20108c7a4ef13598353ff28686683655eded2d28062b5bab7`.
The Stop-completion fix, launch arguments, identity/QMP/exclusion rules, disk and
session formats and backup exclusions are unchanged. Production keys/releases are empty.

## Automated results

- Full regressions: **558 tests passed**, `final-regressions.log` and final post-native repeat
  `final-regressions-post-native.log`.
- GNU text reference: **44 comparisons passed**, `gnu-reference.log`; expected
  stdout, errors and virtual-file outcomes. An additional static GNU directory
  fixture proves short numeric chmod preserves directory setgid and explicit g-s
  clears it. Developer reference fixtures cannot execute learner input.
- Static Bash syntax: **41 displayed commands passed**,
  `evidence/static-syntax.json`; syntax alone does not establish correct behavior.
- UI: **459 assertions per run**, compact 800×600 and wide 1280×900 logical sizes,
  DPR 1/1.5/2, both offscreen and native Wayland (six final runs), zero QML warnings.
  Logs `ui-final-{offscreen,native}-{1,1.5,2}.log`. These check all 44 lessons,
  modes, pin routing, hints/self-review, wrapping/focus, selection, missing sessions,
  old-session reopening and unchanged backup exclusions. UI metadata fixtures
  do not prove real guest behavior. Screenshots/reports are linked from each log.
- Actual wheel built with declared setuptools dependency in a separate environment;
  installed into a second environment and `pip check` passed. Copied smoke script
  ran with installed Python `-I -B` outside checkout. All five units/44 exact pins,
  QML, icon, notices, simulated scenarios, authoring and restart were present.
  Package files match `wheel-source-hashes.json`; retained wheel is in `wheels/`. See
  `wheel-install.log`, `wheel-pip-check.log`, `wheel-smoke.log`.

## Real guest lesson results

All **16 cases passed**: eight lessons × Learn/Challenge. Exact current canonical
lesson/image pins were checked against each report. The first eight cases are in
`evidence/users-unit-live-uqvii16w/report.json`; the last eight in
`evidence/users-unit-live-jj3n6kp6/report.json`. The sole source difference between
these drivers is the explicit g-s fault in the later shared branch, which the first
eight cases do not execute. `evidence/completed-lesson-cases.json` indexes them.

Cases exercise displayed Learn commands, independent Challenge constraints,
identity-based access, wrong repairs, ownership-class selection, preservation of
unrelated groups, old-vs-fresh process groups, setgid inheritance, restrictive masks,
expiry/nologin contrasts, broad modes, setup collisions, exact/repeated cleanup,
partial-setup recovery, unchanged protected metadata, both-mode records and clean
Stop. Inspection cases also exercise real SIGINT of one bounded, exact child PID.
Each case checks foreign-profile Start refusal, running controls across units,
self-reviewed unscored completion, reopening records and unchanged full base hash.
Persistent commands, exact acknowledgements, screenshots, process identities and
session/generation pins are retained. These are static developer fixtures, never
lesson JSON execution or product assessment.

Older unprivileged background-job and pre-edit administrator sessions both booted
existing disks with their original exact pins and privilege policy. The legacy
retained file remained readable. Their current.json bytes stayed exact. Actual
verified Stop succeeded with the pinned lesson missing and image withdrawn; a new
boot after Stop was refused. No catalog/trust production resource was edited.
See `native-compatibility-repeat.log` and
`evidence/users-unit-live-hk9uobi9/report.json`. Failed first probe is retained.

Installed-wheel native Start, clean Stop, separate-process restart, same-disk Resume
and confirmed retained Reset all passed outside checkout: 17/20/22 assertions,
zero QML warnings. Profile: `evidence/installed-users-lifecycle`. Each phase's
`run-*/events.jsonl` records owning process, profile, exact session/generation/pins
and QMP-verified clean shutdown; screenshots and phase-report.json are retained.
Start creates a locked disposable account and marker as that real identity. Resume
retains account/marker and self-review; Reset retains the old overlay hash and
creates a fresh disk without that account. Each phase switches units while running,
refuses a foreign-profile Start and then permits the owning app's clean Stop.
Logs `installed-native-{start,resume,reset}.log`; serialized driver
`remaining-native-repeat.log`. Final host visibility found no QEMU and both existing
shared locks available; no record/lock bypass or force-stop was used.

Both full 16-GiB source bases and their private copies match approved hashes and
mode 0444 (`evidence/final-base-hashes.json`). Original older test profile/disk
source bytes remain intact (`evidence/legacy-source-preserved.json`). All new lesson
pins in executed cases match current resources; installed package resources match
current source. No VM image, trust, backup/storage format or controller change was
needed. Runtime: Python 3.14.7, PySide6/Qt 6.11.2, QEMU 11.1.1.

## Real guest policy

Required account/group tools actually execute in the approved unchanged guest.
Learner retains existing guest-only passwordless sudo; root/learner password
entries stay locked. No credentials are set/unlocked, no learner/PAM/sudoers changes,
no SSH, guest NIC, host shares, clipboard or remote console. Only loopback is present.
Privileged explicit runuser is contrasted with expired-account and nologin su
failures. A locked password is not represented as a universal process/account ban.
Guest root can override guest-side safeguards. Completion remains self-reviewed,
unscored; these test assertions are not application assessment.

## Retained failures and corrections

- Initial private image registration attempts were sandbox-blocked at the shared
  operations lock. Failed staged candidates remain retained. Normal elevated runs
  acquired the existing publication lock; no coordination record was removed.
- Preflight cleanup used rmdir on a skeleton-populated home. The failed disposable
  guest was cleanly stopped; exact userdel -r cleanup passed on a fresh guest.
- A faster native key-injection experiment lost a backslash. Exact command
  acknowledgement refused a false pass; that guest cleanly stopped. The established
  25 ms key rate was restored. Failed run `users-unit-live-9bqlxvxm` is retained.
- The shared-directory fault fixture used chmod 0770, which GNU preserves setgid
  on directories. Actual assertion caught it; no lesson or controller defect was
  hidden. The developer fault now uses explicit g-s; its later cases were repeated.
  Failed run `users-unit-live-uqvii16w` and static GNU comparison are retained.
- A tool-server restart interrupted access to the test session, not the guest
  harness. Reliable host process visibility, matching process/launch identity and
  shared locks verified its ownership; it continued and cleanly stopped. No host
  shutdown cause is inferred or investigated by this batch.
- The first older-session native probe requested a second Start while its own
  guest was running. The controller correctly refused at the shared lifetime lock;
  the test incorrectly expected an availability-specific message. Failed evidence
  `users-unit-live-jjkgp54m` was cleanly stopped. The probe now tests withdrawal after
  Stop, and tests missing lesson + withdrawn image Stop while the guest is running.
- Earlier UI test resets escaped the fake-image admission patch; another reset
  directly raced an asynchronous refresh. The test uses serialized vm.reset with
  both busy and pending readiness now. Six final UI runs passed; old failures remain.

## Outstanding limitations

Physical-keyboard, accessibility and exhaustive native compositor checks are
outstanding. Native QtTest/synthesized console input is not physical input approval.
This unit covers partial LPIC-1 107.1/104.5, not full objectives; LPIC-2 PAM/SSSD
configuration, real password authentication and remote login are not tested.
VM disks/session records remain excluded from profile backups/exports.

The known baseline shutdown warning remains unsuppressed:
`gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.
No application change addresses it in this batch. Public distribution/signing and
Qt/ICU compliance remain open, including the ICU signing-key warning; no production
image admission or publication is enabled.
