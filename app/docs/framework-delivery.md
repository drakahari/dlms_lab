# Framework delivery — checkpoints 2–6

Implemented 2 October 2026 after the owner authorized continuation beyond
checkpoint 1. No personal data migration, Git metadata repair, commit, push,
packaging, deployment, system-wide installation or unrelated project edit.

## Delivered

- A trusted networking adapter with pack-driven source devices, diagnostics,
  endpoints and workspace presentation; original engine behavior retained.
- Versioned, self-contained data-only JSON packs; bounded validation, explicit
  compatibility errors, immutable digest-keyed installation and content export.
- Separate portable attempts pinned to exact content and the declared engine
  contract/behavior; no invented provenance for old records.
- Persistent mission/objectives/constraints; connected topology; editable
  settings and ordered firewall rules; resizable console/diagnostics; distinct
  submission review; scoped Library/Current Lab/History headings.
- Saved pending commands/diagnostics and layout preferences; explicit draft,
  mode/reset and failed-save behavior. No automatic attempt-history pruning.
- A different four-device, two-endpoint DNS-misdirection scenario authored only
  as pack data after freezing all 31 application files. It was imported,
  completed in both modes, reopened and exported/reimported without source edits.
- Portable versions of all three original labs. Original bundles, legacy paths
  and history remain available; importing a portable example creates independent
  pinned attempts. Separate individual personal-attempt export is available.

Architecture, exact format/limits and rollback: [framework.md](framework.md).
Evidence and manual checks: [framework-acceptance.md](framework-acceptance.md).

## Verification

**102 unit/controller tests pass**, including all pre-refactor tests. Mutating
tests use isolated temporary profiles. [Full log](../evidence/framework-unit-tests.txt).

Each original-lab native framework run passes **191 checks** at measured DPR
1, 1.5 and 2, with four logical window sizes from 800×600 to 1280×900. The final
portable proof passes **38 / 38 / 39 checks** at the same scales (the last run
includes an additional expanded diagnostic screenshot). Fresh native processes
restore all original and portable attempts, modes, grades, history and pending
input. Offscreen results are separately labeled.

The original three pack files and the owner's seven progress/two configuration
files remain byte-for-byte unchanged. Final inventories also check permissions,
modification times and directory membership. No real history was copied into
the source tree. [Preservation report](../evidence/framework-preservation.json).

## Recovery

Private snapshots are under:

```text
/home/drak/.local/state/omarchy-learning-lab/recovery/
```

The original `checkpoint-1-before-20261002T213111Z` was verified and never
modified. Additional independently verified snapshots:

- `checkpoint-2-before-20261002T214538Z`
- `checkpoint-3-before-20261002T215407889180Z`
- `checkpoint-4-before-20261002T220129459992Z`
- `checkpoint-5-before-20261002T232448562472Z`

Each contains source, config, progress, specification, manifest and verification
record. `tools/recovery_snapshot.py` verifies every prior snapshot before
creating a new timestamped copy and checks originals before/after copying.
A final `framework-complete-*` snapshot additionally captures the completed
implementation; its exact path is in the preservation report. Snapshots are
never overwritten. Follow [rollback guidance](framework.md#storage-and-rollback)
and preserve the newest profile before any restore.

## Changed files

Changes are compared against the verified checkpoint-2 source copy. Git status
was checked; this workspace exposes an empty read-only `.git` mount and is not
a usable repository. Git metadata was left untouched. No source files removed.
Full path inventory: [framework-changed-files.json](../evidence/framework-changed-files.json).

| Area | Added | Modified |
| --- | --- | --- |
| Domain boundary and portable content | `learning_lab/networking.py`, `portable.py`, `pinned_storage.py`, `workspace_state.py` | `domain/engine.py`, `domain/validation.py`, `session.py`, `storage.py` |
| Native presentation | `qml/MissionPanel.qml`, `TopologyPanel.qml`, `SettingsPanel.qml`, `NetworkWorkspace.qml`, `DiagnosticsDock.qml` | `bridge.py`, `catalog.py`, `qml/Main.qml`, `FirewallPanel.qml`, `LabButton.qml`, `LabTabButton.qml`, `LabScrollView.qml` |
| Content | Four `examples/*.lab.json` files | No original bundled pack edits |
| Tests | `test_networking_adapter.py`, `test_portable.py`, `test_workspace.py`, `test_pack_proof.py`, `framework_acceptance.py`, `framework_restart_probe.py`, `pack_proof_acceptance.py`, `proof_restart_probe.py` | No original test edits |
| Recovery and docs | `tools/recovery_snapshot.py`, `docs/framework.md`, `framework-acceptance.md`, `framework-delivery.md`, evidence logs/JSON/screenshots | `README.md`, `docs/recovery.md`, `docs/scenario-identity.md` historical context |

## Launch

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -B -m learning_lab
```

Use Library → **Import scenario…** for files under `examples/`. There is no
server or extra package to install. Target runtime is Python 3.14.7 and
Qt/PySide6/Shiboken6 6.11.2 on Omarchy 4.0.4-1.

## Remaining limitations

- Physical keyboard/compositor delivery, native file-picker interaction,
  assistive technology, subjective readability and continuous mixed-monitor
  movement require the [owner checklist](framework-acceptance.md#manual-acceptance-checklist--outstanding-until-owner-confirms).
- Qt reports a desktop-portal app-ID registration warning. Rendering and tested
  native flows pass; native file choosers have not been validated. A focused-field
  warning also occurs during geometry probes when a field becomes fixed.
- This validates reusable **networking** packs, not arbitrary domain engines.
  Archives/assets, downloads, accounts, marketplaces, arbitrary plugins,
  history import/merge and visual authoring remain deferred.
- The installed engine behavior is declared and pinned, but old engine binaries
  are not automatically retained. Future incompatible attempts remain read-only;
  keep the matching source snapshots.
- Attempt records and workspace sidecars are separately atomic, not a multi-file
  transaction. A crash can leave older pending input/diagnostics; revision labels
  and explicit sidecar recovery avoid silently treating them as current state.
- Legacy records still lack exact historical content/engine provenance. Their
  records were not migrated or backfilled, and no real migration is authorized.
