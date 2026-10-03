# Restorable profile backups (formats 1 and 2)

Use **Library → Backup profile…** or **Restore profile…**. These actions preserve
the current interface and simulations. A backup contains personal work; keep it
private. A scenario export shares one data-only lesson. A history export shares
one attempt for review and cannot be imported as a profile. Neither substitutes
for a profile backup.

## Authoritative inventory

The existing XDG data/config roots stay unchanged. Explicit `--data-dir` and
`--config-dir` launch arguments still select a disposable or restored profile.

| Profile-relative location | Restores |
| --- | --- |
| Data `current.json`, `current.backup.json`, `attempts/<UUID>.json` | Gateway/DNS current attempt, last-known-good copy, retained history |
| Data `labs/{subnet-boundary,service-firewall}/` with the same record names | Other bundled networking attempts/history |
| Data `portable/packs/<content-digest>.json` | Exact installed/imported scenario bytes, including installed collection packs |
| Data `portable/attempts/<content-digest>/` with the same record names | Pinned attempts, drafts, applied simulation state, mode, hints, logs, assessments and history |
| Each attempt store's `workspace/<UUID>.json` | Pending command and diagnostic results/revision, including archived workspace sidecars |
| Config `selection.json` | Selected lab |
| Config `library-state.json` (optional, backup v2) | Hidden built-ins and removed imports, by exact identity |
| Config `preferences.json` | Built-in theme preference |
| Config `workspace-layout.json`, `linux-workspace-layout.json` | Persisted networking/Linux splitter sizes |

Record bytes are copied unchanged. File modification times are retained for the
existing history sort. No progress schema migration or provenance invention occurs.
Missing optional sidecars/settings remain missing. Packs not yet started from the
built-in collection remain available through application resources.

Excluded: writer locks, credentials, arbitrary config files, caches, exports,
corruption/recovery copies, recovery snapshots, installation environments, source,
Git metadata and unrelated files. Only the paths above can appear in an archive.
An unresolved invalid authoritative record, unsupported settings schema, missing
pinned pack or dangling workspace reference blocks a restorable backup. This is
not a forensic recovery tool; preserve damaged originals separately.

## Consistency and scope

Backup runs synchronously on the Qt GUI thread: app actions and save timers are
paused briefly until it finishes. The application holds both the data writer lock
and a settings writer lock for its lifetime. Backup requires both locks, checks the
existing files first, flushes every loaded lab (including pending drafts/commands),
and refuses to continue after any save failure. No event processing occurs while
the snapshot is collected, validated and published. The app resumes normally
after success or failure; it need not close for this workflow.

The settings lock also prevents two current-version instances from sharing a
config root even with separate data roots. Older application versions do not
honor this additional lock: close older instances sharing these settings first.
External programs must not edit profile files while the app is running. The locks
coordinate Learning Lab writers; they are not a filesystem freeze or protection
against a malicious local process. No background or automatic backups occur.

The live installed application is not updated by these source changes.

## Format and validation

Extension: `.llbackup`; ZIP containing `manifest.json` and allowlisted files under
`data/` and `config/`. Writer uses uncompressed ZIP; reader also supports deflate.
No directory, symlink, device, FIFO, encrypted or executable archive entries are
accepted. Absolute paths, traversal, backslashes, duplicate names, unknown paths
and inconsistent inventories are rejected. Entries are never blindly extracted.

Manifest:

```json
{
  "format": "learning-lab.profile-backup",
  "schema_version": 1,
  "created_utc": "2026-10-03T12:00:00+00:00",
  "legacy_resources": {"gateway-dns": "<sha256>", "subnet-boundary": "<sha256>", "service-firewall": "<sha256>"},
  "files": {
    "data/current.json": {"size": 1234, "sha256": "<sha256 of exact bytes>", "mtime_ns": 1791028800000000000}
  }
}
```

This abbreviated example omits the remaining required bundled profile records.
SHA-256 covers each complete file; the manifest binds each path to its size/hash.
**Hashes detect corruption, not authenticity.** Anyone can rewrite a backup and
recompute its hashes. Restore only backups you trust. This format is not encrypted.

Limits: 10,000 payload files, 128 MiB total payload, 136 MiB archive, 2 MiB manifest;
10 MiB per attempt record, 256 KiB per pack/workspace sidecar, 4 KiB per settings
file (64 KiB for Library settings), and at most 256 installed packs. Sizes are checked before decompression and
against decoded bytes. Excessive or unsupported profiles fail without pruning.

Existing strict JSON, scenario, attempt, domain-state, grading and workspace
validators are reused. Validation checks record filenames/IDs, scenario identity,
engine contract/behavior pins, pack ID/version conflicts, selected lab references,
workspace attempt/revision references and saved assessments. Imported content
remains data passed to installed trusted engines; it cannot install/run code.

Legacy bundled records never recorded exact original engine/content provenance.
The manifest's bundled-resource hashes describe resources at **backup time**, not
historical provenance. A restore requires those same bundled resources, supported
record/settings schemas and every pinned engine version. A newer incompatible
backup or unavailable engine is rejected; there is no automatic migration.

## Library settings compatibility

The reader accepts backup versions 1 and 2. Profiles without `library-state.json`
still write version 1. Profiles with that optional file write version 2, including
its integrity hash and reference validation. Version-1 backups restore with all
Library entries active; version 1 cannot carry Library choices. Version 2 requires
the choices file and an app supporting it. Older readers reject version 2 rather
than dropping the choices. No existing record migration is required. See
[reversible Library cleanup](library-cleanup.md).

## Restore preview and publication

Choose a backup and a parent folder. Validation finishes before the preview shows
creation time, file/pack/profile/history counts, separate Learn/Challenge record
counts, payload size and the exact destination. No destination is created yet.
Cancel releases the pending validated snapshot. **Restore new profile** is the
explicit confirmation; merely choosing a file/folder never restores anything.

Restore always creates a new generated `Learning-Lab-restored-<time>-<id>` folder
containing `data/` and `config/`. Even a pre-existing empty folder is refused.
The open profile stays selected and unchanged. Restore does not merge, overwrite,
replace default XDG roots, modify a launcher or automatically restart the app.
Use the displayed `--data-dir`/`--config-dir` arguments to open the restored copy.

Validated bytes are held for the preview, so changing the archive afterward does
not change the confirmed content. Writes go into a private hidden staging folder
beside the destination, with private profile/file permissions. Only after complete
writes does Linux `renameat2(RENAME_NOREPLACE)` publish the directory atomically.
A destination created during the operation is never replaced. Systems lacking
that primitive fail closed. Normal failures remove temporary staging; a killed
process may leave a hidden staging directory, never an activated partial profile.
Backup publication similarly refuses an existing filename (including symlinks).

## Disposable owner test

Run the reviewed source without changing the working installed app:

```bash
trial=$(mktemp -d /tmp/learning-lab-profile-review.XXXXXX)
cd /home/drak/Documents/dlms_lab/app
python3 -B -m learning_lab --data-dir "$trial/data" --config-dir "$trial/config"
```

1. Complete or partly complete a lab, use a hint in Learn, start Challenge, and
   leave a pending command/draft. Import a reviewed custom scenario if desired.
2. In Library, back up to a new filename **outside** the trial's data/config
   folders (e.g. directly under `$trial`). Notice success and continued usability.
3. Restore that file into `$trial`. Read the preview and cancel once; repeat and
   explicitly confirm. The active profile should not switch or reset.
4. Close normally; launch `python3 -B -m learning_lab` with the two restored paths
   shown in the success message. Compare progress, hints, modes, imported packs,
   pending edits/commands, selected lab and saved splitter sizes.
5. Check native file/folder choosers, Tab/Shift+Tab/Enter/Escape, cancel focus,
   readable scrolling at 800×600/1024×768/1280×900 and 100/150/200% scaling.
   Assistive-technology acceptance remains a separate hands-on check.

Automated tests use only temporary profiles. Offscreen Qt rendering/synthesized
input are reported separately from native and physical-keyboard acceptance.

## Verification in this change

- Baseline: `e76016071260731b02824a893c016b4150b97cf8`, clean before editing.
- **219 unit/regression tests pass**: 197 prior plus 22 profile tests.
- **90 new offscreen UI checks per scale** at 100/150/200%, across all three
  supported logical window sizes. Preview screenshots were inspected for wrapping
  and clipping. The picker test simulates reactivation before checking focus.
- Existing collection, Linux reference/editor and networking framework UI suites
  pass at each scale (nine runs), including their fresh-process restart checks.
- Qt/PySide6 6.11.2. Native Wayland connection is blocked with errno 1, Operation
  not permitted. Native chooser/compositor focus, physical keyboard, accessibility
  and exhaustive native-scale acceptance remain outstanding. Owner-reported
  checks **passed**: backup/restore into a separate disposable profile, verification of
  the updated Library and backup/restore spacing, and reopening the restored
  profile with original service-lab progress intact. Those specific owner checks
  do not establish exhaustive keyboard, assistive-technology or scale coverage.
- No real profile was inventoried, backed up, restored or migrated during these
  tests. The installed application, desktop entry and icon were not changed.

### Spacing and long-path revision

Library and profile dialogs share `InsetScrollView.qml`: 20 logical pixels of
content inset, a separate always-visible scrollbar lane, and inset-aware keyboard
scrolling. Card interiors use the same spacing. Fonts retain their previous sizes.
`ProfileTransferView.qml` groups summary, counts, included labs, paths and warnings
into separate sections. Prose wraps at word boundaries. `CopyablePath.qml` presents
exact paths/launch arguments in read-only selectable fields with horizontal
scrolling and a Copy action. Confirmation buttons remain outside the scrolling
body. Enter in a path field does not confirm restore.

The new checks use long nested destination paths at all supported sizes/scales,
verify exact keyboard/button clipboard copies, focus visibility, insets and font
sizes. Clipboard checks run on the isolated offscreen platform. Storage validators,
archive format and restore publication semantics are unchanged by this revision.


### Previous-reader compatibility evidence

The actual source at `673e4f0c2e435920188da629744a52196f589e41` was run in a
separate temporary directory. Its v1 reader rejects a valid v2 archive with
“Backup contains an unsupported path; only profile files are allowed.” This is
its original path allowlist rejecting `config/library-state.json`, before any
restore staging. Both low-level restore and UI preview/confirmation fail safely:
no destination or partial restore, and the open disposable profile stays byte
identical. A v1 archive restored successfully with the same previous reader.
Reproduce with `python3 -B tests/backup_compatibility_acceptance.py` from `app/`.

Current tests also restore v1 and round-trip v2 with exact file bytes, inactive
choices, archived attempts, pinned current content, mode and drafts; a new process
reopens the restored profile and explicitly restores/resumes its current attempt.
The version bump is necessary because choices are authoritative profile data,
while v1 allows no such file. Omitting it would silently lose choices; pretending
it were a v1 extension would violate the previous strict file allowlist.

No further format change was made for Restore and resume. Compatibility was tested
against that previous commit, not every historical release. Downgrading an in-use
profile is not supported or tested; use v1 backups only with the older app, or
restore v2 with the current compatible app. Hashes do not authenticate a backup.
