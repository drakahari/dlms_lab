# LPIC-1 Foundations: Organize and Find Files

Six original beginner labs, approximately 30–35 minutes. Recommended preparation:
[Files & Permissions](lpic-unit-1.md), or confidence with paths, pwd/ls/cd/cat and
directory access. Sequence is guidance; every entry can be started independently.
The existing Library and terminal layout are unchanged.

This provides introductory **104.7** location practice and partial **103.3** file
management/discovery coverage, using LPIC-1 objective version **5.0**, exams
101-500/102-500. It does not cover full FHS knowledge, wildcard specifications,
recursive operations, archives, links, size/time find expressions, shell streams,
pipes, redirects, or full LPIC-1 preparation. Original content; no LPI affiliation.
[Official LPI objectives](https://www.lpi.org/our-certifications/exam-101-102-objectives/).

## Lessons, outcomes and assessed evidence

All files below are bundled under `learning_lab/collections/packs/`; no manual
import is needed. Each has a fresh identity and content version 1.0.0. Exporting
a scenario preserves its exact content; personal history export remains separate.

| # | Title / filename | Task, grading and incorrect approaches |
| --- | --- | --- |
| 1 | **What lives where?** / `linux-file-locations.lab.json` | Locate and read `/etc/web.conf` (25), list `/var/log` (15), read `/var/log/web.log` (25), read the home todo note (25), finish in home (10). Read-only contract 1. Wrong-file reads or merely viewing lesson text do not satisfy actions. Location roles are explained; their verbal understanding is not assessed. Introductory 104.7 preparation. |
| 2 | **Prepare a workspace** / `linux-prepare-workspace.lab.json` | Workshop directory (40), drafts subdirectory (40), final cwd Workshop (20). Final-state predicates accept separate mkdir calls or mkdir -p in one action. A similarly named wrong folder or an earlier visit alone fails. Selected 103.3 creation practice. |
| 3 | **Copy without losing the original** / `linux-copy-reference.lab.json` | Working copy content matches reference (60), source unchanged (20), final copy successfully read after changes (20). Reading only the reference or leaving an incorrect skipped target fails. Source preservation already earns its 20 points initially; it must still hold at submission. Selected 103.3 copy practice. |
| 4 | **Rename and organize** / `linux-organize-report.lab.json` | Final Reports/report.txt content (45), old inbox draft absent (35), final report read (20). A direct mv or equivalent cp plus rm can pass. Leaving both names is incomplete. Selected 103.3 rename/move practice. |
| 5 | **Find the handover** / `linux-find-handover.lab.json` | Successful supported find discovers the required path (50), successful cat reads it (50). Equivalent starts and filter order count. Reading alone does not demonstrate the explicitly assessed find skill; finding unrelated paths does not count. Partial 103.3 discovery practice. |
| 6 | **Tidy and deliver** / `linux-deliver-workspace.lab.json` | Final assessment: Delivery directory (10), matching delivered brief (15), unchanged incoming source (10), temporary file absent (10), scratch directory absent (10), final discovery (15), final read (20), cwd Delivery (10). Read/discover after all mutations. rmdir on a nonempty folder fails; recursive deletion is unsupported. Reinforces the new skills rather than adding objective coverage. |

Learn offers one step at a time with command, explanation and expected result;
hints develop diagnostic reasoning without a score penalty. Challenge hides
guidance/hints and states outcomes and rules. Both modes grade the same criteria.
Action evidence survives transcript trimming, but contract-4 filesystem mutations
clear prior read/discovery evidence. No-op/skipped commands do not clear it. Final
state is checked afresh; earlier completion does not excuse undoing a requirement.
No initial failed command or one exact transcript is mandatory.

## Simulation and command boundaries

See the [contract and syntax reference](file-management-contract.md), written before
the engine extension. Contract 4 uses `linux-navigation` behavior
`linux-file-management-1`. It permits bounded dictionary-only mkdir, regular-file
cp/mv, exact-name/type find, regular-file rm and empty-directory rmdir. It reuses
the existing filesystem, tokenizer, navigation, session and terminal infrastructure.
The first lesson remains on immutable navigation contract 1.

Only descendants of declared mutable roots may change. Parent write/search governs
creation/removal/move; cp additionally needs source read. The default creation mask
is fixed at 0022; no umask command or ownership alteration is added. `cp -n` / `mv -n`
are required; existing targets are skipped, never overwritten. Every failed action
leaves applied state unchanged. All content remains data, including script-like text.

No learner command accesses host files, processes or networks. No recursive
deletion/copy, arbitrary options, shell expansion, pipes, links or archives. `find`
reports permission failure without partial matches/evidence, a disclosed difference
from real Linux. Old contracts retain their prior command syntax and runtime pins.
Real Linux practice is still needed for broader command/options, permissions under
multiple users, full filesystem layout, exit statuses and shell behavior.

## Optional disposable owner check

Launch the candidate from the source in your graphical session. Keep the printed
directory for reopening; these arguments isolate all practice data/configuration.

```bash
cd /home/drak/Documents/dlms_lab/app
review_profile=$(mktemp -d /tmp/learning-lab-organize.XXXXXX)
printf 'Disposable profile: %s\n' "$review_profile"
python3 -B -m learning_lab --data-dir "$review_profile/data" --config-dir "$review_profile/config"
```

Find **LPIC-1 Foundations: Organize and Find Files**; collapse earlier collections
if useful. Start **Tidy and deliver** in Learn or Challenge. The commands below are
for the **Simulated Linux terminal inside Learning Lab**, not your real terminal:

```text
rmdir scratch
mkdir Delivery
cp -n incoming/brief.txt Delivery
cp -n incoming/brief.txt Delivery
rm scratch/temporary.txt
rmdir scratch
find Delivery -type f -name brief.txt
cat Delivery/brief.txt
cd Delivery
```

The first rmdir should clearly reject the nonempty directory; the repeated copy
should skip the existing target. Submit should earn 100. For an optional evidence
check, create another virtual folder after submission: read/discovery credit clears
until you repeat find/cat. Reset/mode changes preserve the previous attempt.
Close/reopen with the same printed data/config arguments and check the saved result.
No need to replay every accepted lab or alter the working installed app.

## Consolidated verification — 3 October 2026

Reviewed collection commit `c46ad12f36d554ab79d8f45b0077ef0c638d43cb` was pushed
without force to the existing origin. A live query confirmed that exact remote
main hash and clean local status before edits. Source recovery:

`/home/drak/.local/state/omarchy-learning-lab/recovery/organize-unit-source-20261003T213855315153Z`

All 209 snapshot files were SHA-256 reverified. The 44 protected baseline pack,
engine, UI, storage and build files are unchanged. No profile was migrated.

- Engine checkpoint passed **288 tests** before creating unit packs, including
  13 new isolated engine cases. Final suite: **302 tests pass** (275 baseline,
  16 engine cases and 11 unit/lifecycle cases).
- Coverage includes permission-class selection, nonowner removal via writable
  parent, inaccessible/missing ancestor traversal, wrong-kind and same-file
  collisions, no-clobber skips, node/text bounds, complete failure atomicity,
  hostile syntax, allowlisted goals and feasibility, verification invalidation,
  reset, hints/modes, same-profile reopening, exact import/export and history export.
- Actual baseline code created contract-1/2/3 pinned attempts in a disposable
  profile. The candidate reopened them with all record bytes unchanged. Baseline
  backup code rejects a new-contract backup before creating any destination;
  this is engine compatibility rejection, not a backup-format migration.
- Current backup round trips preserve all six labs' applied state, histories,
  exact pins, command drafts and visibility. Earlier v1/v2 compatibility probe
  still passes. An older app cannot resume/restore an unknown contract-4 pack;
  use this candidate or newer. Existing backups remain supported by this version.
- **24 offscreen suite/scale runs pass** at DPR 1/1.5/2. New unit: **192 checks +
  8 restart checks** at each scale, across 800×600, 1024×768 and 1280×900 logical
  windows. Existing collections, Library cleanup, authoring, profile transfer,
  Linux reference/editor and networking framework UI regressions also pass.
  The new-unit suite was rerun at all three scales after final validator review;
  all 192 checks and the 8-check reopening probe passed again.
- Actual wheel build succeeded using declared isolated setuptools dependencies
  after a normal approved network retry. A separate `/tmp` venv installed the wheel;
  pip check passes. Copied smoke harness ran with `python -I` from `/tmp`, without
  the checkout or examples on its import path. All three collections / 14 unique
  packs load; all six new labs complete in both modes and survive fresh-process
  reopen. All wheel application bytes and six new pack identities equal the source
  candidate. Authoring resources and authored Learn/Challenge/resume also pass.
- Runtime: Omarchy 4.0.4, Python 3.14.7, PySide6/Shiboken6 6.11.2; local reference
  tools GNU coreutils 9.11 and findutils 4.11.0-modified. Static developer-chosen GNU
  command checks ran only in a disposable directory, never from learner/pack input.

Wheel: `/tmp/organize-unit-wheel-final/omarchy_learning_lab-0.1.0-py3-none-any.whl`.
SHA-256: `afecb07e8edc0d587c1e47057142d358daa6a1ddacb3c0ef040f156419968900`.

Ignored evidence remains local: `app/evidence/organize-regressions.log`,
`organize-engine-gate.log`, `organize-ui-matrix.json`, `organize-installed-wheel.json`,
`organize-installed-resource-hashes.json`, `organize-gnu-reference.json`, and
`organize-matrix-*.json/.png`. The known baseline shutdown warning is retained:

```text
gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them
```

No suppression or unrelated teardown fix. Wayland socket access is denied with
`PermissionError`, errno 1 (`Operation not permitted`). Native visual, physical
keyboard, accessibility, native file dialogs and exhaustive native scaling remain
outstanding. Screenshots and QtTest input are offscreen evidence. The owner reports
that the Unit 2 final assessment works; that specific check passed. This does not
establish the other native checks above. Installed app and real profile are untouched.

## Changes for review

Trusted application: new `linux_navigation/file_management.py` and adapter;
`domains.py` runtime resolution and `portable.py` contract-specific validation.
Resources: third collection index entry, `lpic-file-management.json` and six packs.
Tests: new `test_file_management.py`, `test_organize_unit.py`,
`organize_unit_acceptance.py`; existing LPIC collection expectations now account
for the third independent collection. Installed smoke covers all 14 unique packs.
Documentation: contract, this guide/report, framework acceptance and installation
smoke counts. No QML/layout, old engine/pack, storage, backup-format, authoring
template or installer activation change.
Final candidate review covers 22 files; no personal profiles, secrets, recovery
copies, environments, build artifacts or generated evidence are included. Those
excluded local files are preserved. The authorized local commit includes only these
reviewed candidates, after exact staged-content verification and whitespace checks.
No push or installed-app update is authorized. Routine automated and instructional
review is agent-owned; this optional owner recipe is not a standing commit gate.
