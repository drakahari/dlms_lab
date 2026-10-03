# Create a lab from Library

**Library → Create a lab…** opens a bundled plain-text quick guide, a complete
worked JSON example, an optional copyable AI prompt and a Validation tab. There
is no connected AI service or visual JSON editor. Edit saved packs in your own
text editor.

## Supported authoring scope

One proven starter: **Linux file/directory permissions**, using the existing
`linux-navigation` engine, contract 3, behavior `linux-permissions-2`, domain
schema 3 and outer portable schema 1. It supports learner-owned mutable modes,
exclusive owner/group/other access, exact final modes, read/traversal evidence,
progressive Learn steps and Challenge goals. The guide includes the precise
`pwd`, `ls [-l]`, `cd`, `cat`, `chmod u+r`, `chmod u+x`, three-digit numeric chmod
and `help` syntax and limits. It does not imply full shell compatibility or a
template for every playable domain.

JSON supplies content and initial conditions to trusted shipped code. It cannot
add commands, execute files/scripts, install plugins, provision VMs or extend an
engine. Goals are allowlisted predicates, never evaluated expressions.

## Files, identity and validation

- **Save starter…** generates `my-permissions-<UUID>` with content version 1.0.0.
  It does not reuse the example ID. Every save previews its destination; replacing
  an existing regular file needs explicit confirmation. Cancellation writes
  nothing. New files are published without clobbering a file created meanwhile;
  replacements reject detectable changes since preview. Temporary writes are
  cleaned up. This is a single-user authoring operation, not a transaction lock
  against a hostile concurrent file writer.
- Save outside the active profile and application resources. Existing replacement
  targets must be regular, non-symlink files no larger than 256 KiB. The folder
  must exist and the name must end in `.lab.json`.
- Keep a stable scenario ID and increment content version for meaningful edits to
  an imported/published pack. Same ID/version with different content fails. Reimport
  of identical content remains idempotent and does not restore removed labs.
- **Validate lab…** reads at most 256 KiB and calls `PackRepository.check`, the
  same nonmutating preflight now used by `install`. It uses `load_portable` and
  the existing trusted domain validators, including the permissions contract's
  final-goal feasibility checks. No profile or repository writes occur. Imported
  text remains plain data. JSON syntax errors retain line/column; contract errors
  retain the validator's field/path labels where supplied. Some errors identify
  a section, not an exact field index. Validation does not assess teaching quality.
- The read-only summary shows title, exact identity, engine/contract/behavior,
  content version and goals. It explicitly is **not a gameplay test**.
- **Import validated lab** is enabled only on the Validation tab and requires
  explicit activation. Changed source bytes require revalidation. The reviewed
  bytes pass through the catalog's existing repository installation path, with
  conflicts checked again. Import does not launch or silently restore a lab.
  A new starter invalidates an older validation preview.

There is no storage migration, backup-format change, engine-contract change or
new profile file. Guide/save/validation state is memory-only. Existing pinned
attempts, Library choices, scenario export and personal history export retain
their contracts. History import does not exist.

## Bundled resources and module changes

- `learning_lab/authoring.py`: resource access, bounded reads, save preview and
  confirmation, read-only validation summary and explicit reviewed-byte import.
- `learning_lab/authoring_resources/guide.txt`, `permissions.lab.json`, `prompt.txt`:
  shipped guide, complete existing-template copy and optional drafting prompt.
  The AI prompt includes the full example and requires validation/playtesting.
- `qml/AuthoringDialog.qml` and two Library integration lines in `qml/Main.qml`:
  reference tabs, save/validate dialogs and explicit actions using shared insets
  and copyable paths. The terminal and existing Library menus are unchanged.
- `catalog.py`, `portable.py`: a separate authoring controller and shared
  read-only repository preflight. No duplicated validator or new engine logic.
- `pyproject.toml`: includes the three resources as package data. Access uses
  `importlib.resources`, never cwd or `app/examples`.
- `tools/installed_smoke.py`: verifies authoring resources and a newly authored
  scenario's Learn/Challenge completion and fresh-process resume in addition to
  the existing six collection packs. Run only with a matching test wheel.
- Tests: `test_authoring.py`, `authoring_acceptance.py`, and the explicitly
  non-wheel fallback `authoring_resource_acceptance.py`.

## Disposable beginner review

Use the current source, leaving the working installation alone:

```bash
trial=$(mktemp -d /tmp/learning-lab-author-review.XXXXXX)
printf 'Save your starter here: %s/my-notes.lab.json\n' "$trial"
cd /home/drak/Documents/dlms_lab/app
python3 -B -m learning_lab --data-dir "$trial/data" --config-dir "$trial/config"
```

1. Open **Create a lab…**. Read Quick guide and Worked example. Try the copyable
   AI prompt if useful; no AI connection is made.
2. Save `my-notes.lab.json` at the printed path. Cancel once, then save. Use an
   ordinary text editor to change `metadata.title` and the virtual notes content;
   preserve the generated identity and compatibility fields. Adjust the last
   Learn step's expected result to match your new note. Save valid UTF-8 JSON.
3. Choose **Validate lab…**. Read the title/engine/version/goals; the Library must
   remain unchanged. Then explicitly **Import validated lab**. Close the guide
   and open the new Library card.
4. In Learn, follow inspection → denied read → repair → verification. Submit for
   100. In Challenge, use `chmod 600 notes.txt`, then `cat notes.txt`, and submit.
   Hints/guidance are hidden and the Learn attempt is preserved. `chmod 777`
   must not earn full credit; the exact-mode goal matters.
5. Leave a pending command, close normally, and reopen using the same `$trial`
   data/config arguments. Check mode/progress/draft and History. Reset and verify
   the initial fault returns without erasing history.
6. Export the scenario to another file under `$trial`, validate it and import in
   another disposable profile. Also test a missing comma, unsupported engine,
   changed content under an imported ID/version, and cancellation/replacement of
   a disposable starter file. Do not use personal profiles or valuable files.
7. Check native save/open file pickers, long-path Copy, Tab/Shift+Tab, Enter/Escape,
   screen-reader labels and readability at compact/wide sizes and 100/150/200%.

The bundled guide describes the installed launcher for a future installed version
containing this workflow; the currently installed app was not updated.

## Recovery and verification

Verified clean baseline: `0277a15d033dd99d979688b1d8867cda4e5affae`.
Before edits, all 186 tracked files were copied and SHA-256 verified at:

`/home/drak/.local/state/omarchy-learning-lab/recovery/authoring-source-20261003T183113825732Z`

This source-only snapshot excludes personal profile files and Git metadata.
Tests use temporary profiles; no installed application or real profile is changed.
Results: **249 regression tests**, **78 authoring UI checks per scale** and
**18 UI suite/scale combinations** passed offscreen at 100/150/200%. Existing
Library cleanup, backup/restore, collection and terminal/network UI tests pass.
The v1/v2 compatibility probe passes; no format changed. Native file dialogs,
physical keyboard, accessibility and exhaustive native scaling remain unverified
(Wayland socket access denied, errno 1). See the
[acceptance report](framework-acceptance.md) for evidence scope and gaps.

Actual wheel preparation was attempted in `/tmp/authoring-wheel-26jn_vpb`, in a
new build venv. Pip could not obtain the declared `setuptools` build dependency:
“No matching distribution found for setuptools”. Package-source settings were
not changed. Therefore a newly built/installed wheel remains **unverified**.
The passing fallback copies only Python modules and declared package resources
to a temporary location, loads the real QML, saves/validates/imports, and completes
both modes without source examples. It proves resource-path independence, not
that setuptools built or installed a wheel.

When dependencies are available, use the existing build tool with a fresh output
folder, install the resulting wheel in a separate test venv, and run this revision's
`tools/installed_smoke.py --require-icon` with that venv's `python -I -B` from outside
the checkout. Do not run the installer against the owner's working installation
as part of review.


## Owner review and commit verification

The owner reports successful starter saving, JSON editing, validation, explicit
import, custom-text display, Learn and Challenge completion, and reopening the
same profile with results retained. These specific checks pass; accessibility,
comprehensive keyboard navigation, file-dialog edge cases and exhaustive native
scaling are not implied.

The commit review retried an actual wheel build through the existing PEP 517
workflow in `/tmp/authoring-commit-wheel-gbchx6fw`. The declared `setuptools`
build dependency remained unavailable (“No matching distribution found for
setuptools”). No candidate wheel was built or installed. The fallback isolated
resource-copy test remains explicitly separate from wheel acceptance.

A reviewed one-shot host verification helper is supplied locally:

```bash
python3 -B /tmp/dlms-lab-authoring-wheel-verify.py
```

It checks the baseline (or a direct child commit) and all reviewed build-input
hashes, copies only those files into a new temporary source directory, builds with
the declared backend, installs the wheel and declared dependencies in a separate
new venv, runs `pip check`, and executes the copied installed smoke harness with
`-I` from outside the checkout. That harness checks bundled authoring resources,
starter save/validation/import, both modes and a fresh-process resume. The helper
never invokes installation activation or desktop integration and leaves the
working installation alone. It stops on dependency/build/test failure; only an
actual passing result closes the installed-wheel gap. `/tmp` helper files are
local review aids, not shipped application resources or commit candidates.
