# Safe Library cleanup

## What the actions mean

Each Library card has a keyboard-focusable **Actions ▾** menu. The approved
terminal workspace and shared 20-pixel content insets are unchanged.

- **Hide from Library** applies to built-in networking labs and the six exact
  Fundamentals resources. It hides a card, not progress or bundled content.
- **Show hidden / removed (N)** switches to a compact inactive list. Uncheck it to
  return to the active Library. It does not change any persisted choice.
- **Restore visibility** shows all hidden built-ins again without launching. A
  hidden card's menu also offers **Restore to Library** for that single exact lab.
  Removed imports stay removed.
- **Remove from Library…** applies to an imported pack that is not an exact
  built-in resource. Confirmation explains that its exact pack, drafts, current
  attempt, completed results and retained history stay on disk. Cancel changes
  nothing. There is no permanent-delete operation.
- Inactive entries with a resumable attempt offer **Restore and resume**. A preview
  identifies its mode, content version, start time and attempt ID before opening it.
  Cancel leaves the entry inactive. Confirmation restores Library availability and
  opens that exact attempt, retaining progress, drafts, mode and pinned content.
- **Actions → Restore to Library** restores without launching. This is the primary
  action when there is no resumable attempt. **Actions → View saved history** works
  without restoring and never opens an interactive workspace.

Both hidden built-ins and removed imports require restoration before practice.
Hiding/removing an already-open lab returns to Library without discarding edits.
Current Lab navigation, history's Open this lab, and backend edit/command/test/
submit/reset/mode actions cannot bypass this requirement. On restart a saved
inactive selection keeps its exact record but cannot enter practice. Restoring
returns normal control availability (subject to ordinary storage recovery rules).

The existing storage has **one current resumable attempt per exact pack version**.
The preview never substitutes an arbitrary archived record. Its chooser requires
an explicit selection if there are multiple resumable candidates; today each exact
version supplies at most one. Different pack versions have separate cards/stores.
Multiple ended records remain reviewable/exportable History, not resumable
candidates. This does not add archived-attempt resurrection or migrate the lifecycle.
The backend rechecks the chosen current ID; stale/reset/ended IDs fail without
restoring anything. Repeating the action for the same already-open attempt is safe.

If an inactive pack has no recoverable current record, merely viewing it, importing
it again or restarting must not manufacture an attempt. Restore to Library does
not create or launch an attempt; an explicit Open/Start after restoration can do so.
Damaged records retain existing recovery/read-only behavior; cleanup is not repair.

## Identity and truthful progress

Choices are keyed by the exact catalog identity: the three existing bundled
legacy keys or `pack:<content-digest>` for portable packs. They never use title,
filename, or scenario ID alone. Removing version A does not touch version B.

An exact import of a built-in collection pack is the same entry, with one pinned
attempt store. Built-in classification takes precedence, so it offers Hide rather
than Remove; restoring or reimporting does not create a duplicate. An imported
portable conversion of a legacy networking lab is a distinct pinned entry from
the original legacy store, even when its scenario ID matches.

Reimporting an exact removed or hidden pack reports that it is already installed
and stays inactive until an explicit Restore. A conflicting same-ID/version pack
still cannot replace retained content, even when the original entry is removed.
The same rule keeps a conflicting collection item unavailable; use a genuinely
new content version instead of silently replacing pinned material.

Learn and Challenge status still come from attempts and assessments. Visibility
is not completion. The inactive list shows the same status, and unknown/unreadable
progress is not presented as completed. No scores or histories are migrated.

## Persistence and backup compatibility

The only new profile file is config **`library-state.json`**:

```json
{
  "schema_version": 1,
  "entries": {
    "gateway-dns": "hidden",
    "pack:<exact 64-character content digest>": "removed"
  }
}
```

This illustrative placeholder is not a valid key. Real keys must reference known
built-ins or exact installed packs. Built-ins permit `hidden`; other installed
packs permit `removed`; absence means active. The file is limited to 64 KiB and
512 entries. Writes are atomic. Failed writes leave the displayed/persisted
choice unchanged. Unsupported, malformed or orphaned settings are preserved
read-only, with a recovery notice. Practice actions and backup are blocked
until that settings problem is resolved; original records are not rewritten.

No settings file is created just by opening an existing profile. Existing progress
schemas, paths, engine contracts and pinned identities are unchanged. Pack files,
current records, archives and workspace sidecars are never moved or deleted by
Hide, Remove or Restore.

The backup compatibility change was explained before implementation:

- The current reader accepts existing **version-1** backups unchanged. They have
  no Library settings, so restored profiles default to all entries active.
- A backup containing `config/library-state.json` uses **version 2**. Its manifest
  and SHA-256 file checks include that file. Reference validation checks every
  hidden/removed identity against the included packs or installed built-in set.
- A profile with no Library settings still writes version 1. Version 1 cannot
  carry the new file; version 2 must carry it. This avoids ambiguous old-format
  archives and silent loss of choices in an older app.
- The actual previous committed reader (`673e4f0`) was executed from isolated
  Git source against a new v2 backup. It rejects the new file as an unsupported
  path before staging, rejects the UI preview/confirmation, and leaves its open
  disposable profile and destination unchanged. The same old reader successfully
  restored a v1 positive control. Older app versions cannot restore version 2. Restore with this version or a
  compatible newer version. No migration, merge, overwrite or automatic activation
  was added. Hashes detect corruption, not authenticity.

## Recovery and scope

Starting baseline: `673e4f0c2e435920188da629744a52196f589e41`; working tree clean.
Before edits, 180 tracked source/docs/test/resource files were copied to:

`/home/drak/.local/state/omarchy-learning-lab/recovery/library-cleanup-source-20261003T172538886118Z`

Every source and copied file was checked against its SHA-256 manifest. The snapshot
uses `source-manifest.json` plus `VERIFIED.json` and does not overwrite previous
recovery snapshots. It intentionally excludes the real profile and Git metadata.
No real-profile or installed-application changes are part of this work.

Before the restore-action revision, the original 180-file snapshot was reverified.
A second snapshot preserves all 185 then-current source files, including the
uncommitted cleanup implementation, with verified SHA-256 copies:

`/home/drak/.local/state/omarchy-learning-lab/recovery/library-restore-actions-source-20261003T180258390093Z`

Neither snapshot includes personal profile files. The revision introduces no
further backup-format, record-schema or engine-contract change.

## Disposable owner test

```bash
trial=$(mktemp -d /tmp/learning-lab-cleanup-review.XXXXXX)
cd /home/drak/Documents/dlms_lab/app
python3 - "$trial" <<'PYTEST'
import json, sys
from pathlib import Path
value = json.loads(Path('examples/linux-service-basics.lab.json').read_text())
value['identity']['id'] = 'my-cleanup-practice'
value['metadata']['title'] = 'My cleanup practice'
Path(sys.argv[1], 'my-cleanup-practice.lab.json').write_text(json.dumps(value))
print('Disposable import:', Path(sys.argv[1], 'my-cleanup-practice.lab.json'))
PYTEST
python3 -B -m learning_lab --data-dir "$trial/data" --config-dir "$trial/config"
```

1. Start a built-in, make progress and leave a command draft. Hide it from Library.
   Current Lab must not reopen practice. Check Show hidden / removed, then choose
   **Restore and resume**. Cancel once, then confirm: same attempt, mode and draft.
2. Hide it again and use **Actions → Restore to Library**. Stay in Library; opening
   it later must retain progress. The primary action for an unstarted hidden lab is
   Restore to Library. Global Restore visibility also does not launch anything.
3. Import the disposable custom pack printed above. Start its service and submit.
   Reset once, switch mode if desired, and leave new progress/a draft. Remove it;
   verify **View saved history** works while inactive, including ended records.
4. Reimport the same file: it stays removed without duplicates. Restore and resume
   identifies the current attempt, not one ended by Reset/mode change. After
   confirmation, normal Reset/Change mode controls work again.
5. Remove it again and hide a built-in. Close normally, reopen using the same two
   temporary directories, and verify inactive selections cannot practice until
   restored. Restore without launching, close/reopen again, then Continue.
6. Back up outside those two directories, restore into a fresh folder under
   `$trial`, and reopen using the displayed arguments. Check choices, drafts,
   histories and pinned attempts. A previous v1 disposable backup defaults to
   active entries. Do not try downgrading the live installed profile.
7. Check menus, Cancel/confirmation focus, Tab/Shift+Tab, Enter/Escape, scrolling
   and readable spacing at 800×600, 1024×768 and 1280×900, 100/150/200% scaling.
   Physical keyboard and accessibility remain owner checks.

## Verification results

- **238 regression tests passed**, including all previous 219 and 19 cleanup tests.
- **71 rendered cleanup UI checks per scale** at 100/150/200%, covering compact/wide
  layouts, keyboard-triggered Actions, hide/restore, removal cancel/confirmation,
  retained completed progress, history without restoration, exact restore/resume,
  cancellation, restore without launch and normal restored controls.
- Profile backup/restore, collection, Linux reference/editor and networking
  framework UI regressions passed at all three scales: **15 successful UI runs**
  including the new cleanup suite.
- Qt/PySide6 6.11.2; checks use offscreen rendering and synthesized Qt input.
  Native Wayland socket access is blocked with errno 1, Operation not permitted.
  Native menus/focus, physical keyboard, accessibility and exhaustive display-scale
  checks remain outstanding. No native acceptance is inferred from offscreen runs.
- All mutating tests use temporary profiles. Bundled resources, trusted domain
  engines, installed application and personal profile were not changed.

Reproduce the previous-reader check (requires local baseline Git objects):

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -B tests/backup_compatibility_acceptance.py
```

This copies only committed application source into `/tmp`, uses disposable
profiles, checks v2 rejection/no partial activation, and restores a v1 control.
It neither runs nor modifies the owner's installed application.
