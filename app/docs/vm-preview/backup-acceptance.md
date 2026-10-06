# Backup & Safe File Recovery — acceptance

Baseline: `7bd907e6946a51d164a0112c840d312dcd423246`, inspected clean on 2026-10-06. Existing two local commits remain unpushed. New work is unstaged/uncommitted. This report covers the eight display-only recovery lessons and the approved bounded registry extension; it does not authorize publication.

## Scope and compatibility

Seven units, **60 total / 16 per unit**; accepts 60 and rejects 61, an eighth unit and 17 in one unit. Every new lesson maps exactly to the existing administrator image, without fallback. Original 52 lesson resources, original six unit resources, controller, launch/process/QMP policy, both image descriptors, simulated engines/QML, profile/backup formats and production trust are unchanged. The baseline catalog projection is identical after removing only the eight additions. Production keys and releases remain empty.

A 396-file source recovery copy was created and byte-verified before edits, then verified again at final review. 167 protected application files remain byte-identical. Personal profiles, working installation and original proof VM are untouched. Mutating tests use disposable profiles and overlays; runtime evidence/disks stay outside Git.

## Automated gates

- Full regression: **587 passed**, 26.882 seconds (`regression-final-candidate.log`). Includes prior scenario/persistence/import/export/backup tests and new bounds, exact routing, retained records and developer archive-reference tests.
- GNU reference suite: **44 passed**, including expected stdout/status/error categories and resulting virtual-file bytes (`gnu-reviewed-final.log`). Real GNU execution is confined to static developer fixtures.
- Actual wheel built offline using existing declared build tools, installed in an isolated environment; `pip check` passes. Installed smoke runs with `python -I -B` outside the checkout. All 179 packaged application/resource files match the candidate. Wheel SHA-256: `167057b098a41827478387caa599e25dc492dbcedcd46159da0aeffe8ab11466`.
- Core startup without a VM image/QEMU requirement, seven units/60 lessons, packaged authoring guide/template/scenarios, simulated start/resume and authoring resources pass the installed smoke. This is separate from native guest lifecycle evidence below.

## Real guest evidence

**16/16 real guest lesson/mode runs passed**. `guest-matrix.json` combines completed runs only; `guest-command-parity.json` verifies all 16 exact final lesson pins and static command lists. Partial/interrupted rows remain retained and excluded.

Copied legacy unprivileged and administrator sessions both booted on their original image pins. Verified Stop succeeded with missing pinned lesson content/withdrawn image state; subsequent withdrawn boot was refused without changing the saved record. Original source session directories were not edited.

The wheel-installed native lifecycle ran outside the checkout in **three separate app processes**: Start (17 checks), Resume (20), retained Reset (22). It exercised archive/compression/checksum/separate restore, actual preserved report contents, same disk/generation on Resume, new generation after Reset, unchanged retained disk bytes, shared cross-profile refusal, and verified owner Stop. All phases passed (`installed-final-{start,resume,reset}.log`); no additional live Qt warnings beyond the recorded baseline classifications.

The current focused offscreen suite passed **253 checks at each DPR 1/1.5/2**, at 800×600 and 1280×900, with zero QML warnings. Earlier full UI runs passed 647 checks/scale before the final private-backup/collision text corrections; current focused runs cover all eight final new lessons and representative original/long-instruction cases. These are offscreen fixtures, not native guest lifecycle or physical input proof. Final isolated **native Wayland** runs also passed **253 checks at each DPR 1/1.5/2**, with zero QML warnings. Actual logical sizes were 800×600 and 1280×900 at every scale; command/material wrapping, focus, control access, both modes, unit selection, profile-backup exclusions and preserved records are covered. `native-ui-summary.json` records screenshot directories. UI metadata/image operations use isolated fixtures; actual guest behavior is established by the separate guest/lifecycle tests, not those mocks.

All 22 retained real-guest lifecycle records are `stopped`; the final host check verifies no QEMU process and no live process matching the stopped shared record. Source/test base hashes remain unchanged. No current guest or unclean-disk Resume remains.

Runtime: host Python 3.14.7, PySide6/Qt 6.11.2, QEMU 11.1.1; unchanged Debian administrator guest with actual GNU tar 1.35, gzip 1.13 and coreutils 9.7. Task-owned guests use verified process/QMP identity and normal cross-profile exclusion; no forced shutdown or lock bypass.

The lesson tests distinguish valid member listings/gzip streams from correct payloads, detect a truncated stream, altered payload, incomplete member set and wrong version, compare contents/modes/timestamps, and read/deny access as actual disposable identities. Backup originals are retained during these tests. Interruption tests cancel a bounded tar input-list operation, retain the candidate and retry under a different name; they do **not** establish power-loss recovery or arbitrary hostile-archive extraction safety.

## Failures and review corrections

All failed and partial runs are retained. Initial test-root/image directories were rejected for unsafe 0755 permissions; only newly created isolated test directories were corrected to private 0700. No host security settings were changed.

Review found that private archives in ownership exercises could inherit permissive modes when their workspace was traversable. Lessons 6/8 now save/use/restore a shell-local 077 umask, explicitly protect the root-created archive with 0600, and test archive/reference privacy. Collision checks precede archive creation/source changes in lessons 6–8; real repetitions must refuse and preserve backup/source hashes. These changes affected only new lesson content/pins and static fixtures.

Two runs were deliberately interrupted at new-lesson boundaries while those corrections were made. Completed rows are accepted only if their exact canonical pin and executed commands match the final content. Partial rows are not passes. One early-boot normal Stop request timed out, retaining the disk/runtime record; after verifying ownership and boot completion, normal Stop succeeded even though the edited draft lesson revision was unavailable. No force Stop, Resume of an unclean disk or coordination-file removal was used.

UI harness corrections compare current Challenge materials rather than old wording, test self-review labels case-insensitively, and wait for actual refresh/activation/focus readiness. Disposable failure profiles are retained; teardown waits for pending work. An earlier overlapping native test failed focus/scroll visibility and is not accepted as a pass. Final native runs must be isolated from guest testing.

## Limits and outstanding acceptance

Completion remains **self-reviewed/unscored**, not verified guest assessment. Native synthesized QtTest/QMP input is not physical-keyboard, screen-reader or exhaustive manual scaling acceptance. These remain outstanding. Cooperative guest guards are not a hostile-archive sandbox; guest root can override guest-side limits. The free-space check is admission observation, not a hard reserve. Checksums detect change against a retained reference, not authenticity.

Known baseline `gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them` remains recorded, not suppressed or fixed in this batch. Existing lifecycle Dialog `implicitHeight` binding-loop/teardown messages are retained and classified separately; layout fixtures require zero QML warnings. No warning-free general startup claim is made.

Public release is deferred: unresolved Qt redistribution review and ICU signing-key warning remain blockers. No ACL/xattr, rsync, cpio, tape, remote-backup or complete LPIC-objective coverage is claimed. VM disks/reports are excluded from profile backups; Resume boots disk state, not RAM/jobs. See [guide](backup-unit.md) and the [objective inventory](../curriculum-coverage.md).

## Recovery, exact files and reproducibility

Persistent private evidence/recovery root:
`/home/drak/.local/state/omarchy-learning-lab/recovery/backup-unit-20261006T115848179580Z`.
`source-manifest.json` verifies the original 396-file snapshot;
`guest-matrix.json`, `guest-command-parity.json`, `protected-final.json`,
`installed-source-parity.json`, `base-final.json`, `bases-after-all-native.json`,
`final-host-process-check.json`, `final-lifecycle-inventory.json`,
`offscreen-current-summary.json` and `native-ui-summary.json` describe the checks.
All failed logs, partial overlays, copied legacy sessions and build environments
remain outside Git. The final 29-file hash list is `reviewed.sha256` in that root
and `/tmp/backup-unit-reviewed.sha256`.

Routine review uses `python3 -B -m unittest discover -s tests -v` and
`PYTHONPATH=. python3 -B tests/text_gnu_reference.py` from `app/`.
The real guest harness is `tests/backup_unit_live.py --vm-home <private verified test root>`;
use persistent `TMPDIR`, reliable host-process visibility, no other running VM
and normal shared exclusion. Never overlap native UI and guest harnesses.
Installed smoke/lifecycle scripts are copied outside the checkout and run with
the wheel-installed venv's `python -I -B`. No system-wide or working-app installation/update was
performed; the isolated environment reused existing PySide6 and declared build tools.

Optional source review (new application profile, existing private test images;
no installed-app update or personal-profile use):

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -B -m learning_lab \
  --data-dir /home/drak/.local/state/omarchy-learning-lab/recovery/backup-unit-20261006T115848179580Z/owner-review/data \
  --config-dir /home/drak/.local/state/omarchy-learning-lab/recovery/backup-unit-20261006T115848179580Z/owner-review/config \
  --vm-home /home/drak/.local/state/omarchy-learning-lab/recovery/backup-unit-20261006T115848179580Z/runtime
```

Select **Real Linux VM preview → Backup & Safe File Recovery → Define recovery
requirements and expected metadata**. Start only when shared exclusion permits;
use normal Stop before closing or switching guests. Owner replay is optional,
not a completion gate. All existing simulated labs remain available without QEMU.

### Changed paths (29)

- `app/docs/curriculum-coverage.json`
- `app/docs/curriculum-coverage.md`
- `app/docs/vm-preview/backup-acceptance.md`
- `app/docs/vm-preview/backup-unit.md`
- `app/docs/vm-preview/setup.md`
- `app/learning_lab/vm_preview/backup-unit.json`
- `app/learning_lab/vm_preview/image-catalog.json`
- `app/learning_lab/vm_preview/real-linux-backup-access.json`
- `app/learning_lab/vm_preview/real-linux-backup-archive.json`
- `app/learning_lab/vm_preview/real-linux-backup-assessment.json`
- `app/learning_lab/vm_preview/real-linux-backup-checksum.json`
- `app/learning_lab/vm_preview/real-linux-backup-damage.json`
- `app/learning_lab/vm_preview/real-linux-backup-requirements.json`
- `app/learning_lab/vm_preview/real-linux-backup-restore.json`
- `app/learning_lab/vm_preview/real-linux-backup-versions.json`
- `app/learning_lab/vm_preview/registry.py`
- `app/learning_lab/vm_preview/units.json`
- `app/tests/backup_guest_fixtures.py`
- `app/tests/backup_unit_live.py`
- `app/tests/test_admin_unit.py`
- `app/tests/test_backup_unit.py`
- `app/tests/test_bash_unit.py`
- `app/tests/test_capacity_unit.py`
- `app/tests/test_image_catalog.py`
- `app/tests/test_scheduling_unit.py`
- `app/tests/test_users_unit.py`
- `app/tests/vm_lessons_acceptance.py`
- `app/tests/vm_lessons_switch_live.py`
- `app/tools/installed_smoke.py`
