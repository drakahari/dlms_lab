# Checkpoint 1 — identity and legacy compatibility

Implemented 2 October 2026. Scope: in-memory identity and compatibility around
the existing gateway/DNS pack. No progress migration, import/export, workspace
redesign, new scenario, commit, push, packaging, or Git initialization was performed.

## Recovery snapshot

The owner closed the running application normally before copying. The writer
lock was absent and no `python -m learning_lab` process was running during the
snapshot checks.

Snapshot location, outside the source tree:

```text
/home/drak/.local/state/omarchy-learning-lab/recovery/checkpoint-1-before-20261002T213111Z/
  source/        complete pre-edit app tree, including existing evidence
  config/        application preferences and selection
  progress/      current records, backups, and retained attempts
  Omarchy-Learning-Lab-v0.1-Spec.docx
  manifest.json
  VERIFIED.json
```

Snapshot verification passed for 300 source/evidence files, seven progress files,
and two configuration files. Original inventories before and after copying and
the copies agree on path, size, SHA-256, permissions, and modification time.
The specification copy also matches by SHA-256. Snapshot access is restricted by
its private parent directory. Personal progress was not copied into the app tree.

Git status was rechecked in both the workspace and app before editing. Neither
was a usable repository; the visible `.git` directory was empty. Git metadata
was not initialized, repaired, replaced, or included in the snapshot.

For recovery, close the app and preserve the current tree before using this
snapshot. Restore source separately from progress/configuration. Restoring code
does not require rolling back personal progress for this checkpoint because
record formats and paths are unchanged. Never overwrite newer progress merely
to undo the source change. The manifest contains the original component roots
and exact file hashes; verify copies against it before restoration.

## Changed files

- `learning_lab/scenario_identity.py` — immutable identity/runtime values and versioned canonical content digest.
- `learning_lab/legacy_scenario.py` — gateway-only adapter using the existing validator and engine compatibility declaration.
- `learning_lab/__main__.py` — integrate the adapter at bundled loading; runtime metadata stays outside saved records.
- `tests/test_scenario_identity.py` — canonicalization, compatibility, behavior parity, isolated record preservation, and startup checks.
- `docs/scenario-identity.md` — exact digest rules, version meanings, and limits of legacy provenance.
- `docs/checkpoint-1.md` — recovery and checkpoint results.
- `README.md` — link to checkpoint documentation.
- `evidence/checkpoint-1-tests.txt` and `evidence/checkpoint-1-verification.json` — test output and final preservation checks.

The three original packs, domain engine/validator, session, storage, catalog,
theme adapter, QML, and existing tests are unchanged.

## Verification

Before editing, all 63 existing unit/controller tests passed. After implementation,
the full suite contains 79 passing tests: those 63 plus 16 checkpoint tests.

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -B -m unittest discover -s tests -v
```

New coverage includes a fixed canonical-byte/digest vector; object ordering and
escape equivalence; meaningful metadata/topology/state/rubric/hint changes; array
ordering and exact Unicode; size/depth/type rejection; distinct format/content/
engine versions; unsupported format/contract/behavior/capability rejection;
immutable adapter data; original engine/session behavior; all three bundled
packs; unchanged storage paths and legacy record bytes; and isolated startup.

All mutating tests use temporary fixtures generated from bundled packs, not
personal history. The startup test uses a separate process, temporary data,
configuration and cache directories, the offscreen Qt platform, and software
rendering. An inherited GTK platform theme initially tried to open a display;
the test now clears that theme setting in its own environment. No system setting
was changed.

This is a startup/loader check, not native visual or physical-keyboard acceptance.
The unchanged UI was not requalified. Physical-keyboard acceptance remains open.

Final preservation results and exact pack hashes are in
`evidence/checkpoint-1-verification.json`; full test output is in
`evidence/checkpoint-1-tests.txt`.

## Remaining limits and stop point

The adapter supports only the gateway pack's legacy format. Subnet/firewall retain
their existing paths and loaders. The shared identity layer imposes no hint-count
rule; the old format and UI still preserve their three hints.

Identity and runtime declarations are in memory only. Legacy records still lack
exact content/engine provenance, and this checkpoint cannot supply it retroactively.
No persisted attempt pinning, engine version registry, portable import format,
or migration has been introduced. See `scenario-identity.md` for the precise
boundary. Stop here for owner review before checkpoint 2.
