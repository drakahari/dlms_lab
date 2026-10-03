# Unit 1: Finding files and controlling access

Five short teaching labs and one transfer assessment, approximately 30–40 minutes.
All six labs are built into **LPIC-1 Foundations: Files & Permissions** in Library.
Linux Fundamentals keeps its original six labs and order. Shared labs use the
same attempts and separate Learn/Challenge results in either collection.
See [collection delivery and disposable review](lpic-collection.md).
This is original introductory practice, not an
LPI product, endorsement, complete exam course or claim of full objective coverage.

LPI's current objectives are version **5.0**, exams **101-500 / 102-500**:
[official Exam 101/102 objectives](https://www.lpi.org/our-certifications/exam-101-102-objectives/).
The sequence develops part of **104.5 (file/directory permissions)** and prepares
for **103.1 (command-line work)** and **103.3 (file management)**. Navigation alone
does not establish shell processing or text-filter skills. There is no complete
Exam 102 objective coverage. No supplied LPIC curriculum guide was available.

## Suggested sequence

Prerequisites are recommendations, not locks. All paths below are relative to
`app/examples/` for optional export/import comparisons. No import is needed
to start these labs from the new built-in collection.

| # | Lab and availability | Outcome and relationship to earlier practice |
| --- | --- | --- |
| 1 | **Find your way around Linux** — built in; `linux-file-navigation.lab.json` | No prerequisite. Use pwd/ls/cd/cat; distinguish recorded actions from the final working directory. Introductory 103.1/103.3 preparation. |
| 2 | **Restore access to your file** — built in; `linux-file-permissions.lab.json` | After 1. Add missing owner-read access while retaining private owner read/write; verify with a read. Partial 104.5, ordinary file permissions. |
| 3 | **Why can’t I enter this directory?** — built in; `linux-directory-permissions.lab.json` | After 1–2. Distinguish names (directory read) from traversal (execute/search); restore 0400 to 0500. Partial 104.5, directories. |
| 4 | **Make an overexposed note private** — built in; `linux-private-note.lab.json` | After 2. Reading already works at 0777. Remove unnecessary execute and group/other access, require 0600, then verify reading. Partial 104.5: reducing excessive access. |
| 5 | **Read a known file without listing its folder** — built in; `linux-search-only-directory.lab.json` | After 3. Search-only 0100 permits entry and a known readable child, while name listing stays denied. Partial 104.5: search without listing; denied listing is demonstrated, not separately graded. |
| 6 | **Read the fieldwork handover** — built in; `linux-archive-access.lab.json` | After 1–3; useful again after 5. Transfer assessment in another directory tree. Reinforces directory access; it is not an additional objective or new coverage. |

The service labs remain in Linux Fundamentals. Collection membership is
organization, not another copy of a scenario or a separate progress record.

## Play lab 4 in a disposable profile (optional import comparison)

From a terminal in the existing graphical session:

```bash
cd /home/drak/Documents/dlms_lab/app
review_profile=$(mktemp -d /tmp/learning-lab-private-note.XXXXXX)
printf 'Disposable profile: %s\n' "$review_profile"
python3 -B -m learning_lab --data-dir "$review_profile/data" --config-dir "$review_profile/config"
```

Keep the printed path for reopening. In Library, expand **LPIC-1 Foundations:
Files & Permissions** and start **Make an overexposed note private**. Optionally
import `/home/drak/Documents/dlms_lab/app/examples/linux-private-note.lab.json`
to confirm that an exact existing pack does not create a second entry or reset progress.

1. In Learn, optionally run `cat notes.txt` immediately: it succeeds, but submission
   earns only the read-verification points. Reading is not proof of privacy.
2. Follow inspection, repair and verification guidance. Read the three permission
   triplets: owner, group, other. Ordinary text notes need no execute permission.
3. Try `chmod u+r notes.txt` before repairing: it cannot remove excessive bits.
   `chmod 644 notes.txt` still grants group/other read access. Neither earns full credit.
4. Use `chmod 600 notes.txt`, then `cat notes.txt`. Submit for 100. Final mode earns
   70 points; successful reading after the last actual mode change earns 30.
5. Reset or switch to Challenge: the previous attempt stays in history. Challenge
   shows goals and constraints without a repair command or hints. Complete it by
   any supported path/order. An initial read or mistake is not required.
6. Close and reopen with the **same** data/config arguments; check results and any
   pending command. Export scenario/reimport into another disposable profile to
   check content identity. Scenario export excludes personal progress. History
   export is separate; history import is not supported.

Changing permissions after verification clears that evidence, even if a later
change restores 0600. Read again. A no-op chmod does not clear evidence. Nothing
requires an exact transcript. Hints are recorded without a hidden score penalty.

## Play lab 5 in a disposable profile (optional import comparison)

Use the launch command above with a **new** temporary directory, or reuse that
disposable profile to check both pilots together. Start the fifth entry in
the LPIC collection. For an optional exact-pack import comparison, select:

`/home/drak/Documents/dlms_lab/app/examples/linux-search-only-directory.lab.json`

Library title: **Read a known file without listing its folder**. Identity:
`linux-search-only-directory`, content version `1.0.0`, permissions contract 3,
behavior `linux-permissions-2`. Bundled and imported copies share this exact identity.

1. Learn starts in `/home/learner`. Inspect with `ls -l .`: Lookup is `d---------`
   (0000). `ls Lookup`, `cd Lookup` and `cat Lookup/message.txt` initially fail.
2. Follow the repair suggestion `chmod u+x Lookup`, or use `chmod 100 Lookup`.
   Enter with `cd Lookup`. Directory x permits search/traversal; it does not run
   the directory as a program. The child already has file-read permission.
3. At the read step, try the suggested comparison `ls .`: it reports
   `Permission denied (list names)`. Then `cat message.txt` works because its
   name is known. No directory read permission is needed for this access.
4. Submit: 70 points for final directory mode 0100, 15 for successful entry and
   15 for reading the known child after the final actual permission change.
   Denied listing is demonstrated and regression-tested, **not a separately
   graded action**. The guide does not wait for a successful listing or require
   a failed command. There is no denial predicate or new lesson action.
5. Reset into Challenge. It states desired access and verification constraints
   without a repair command. Numeric/symbolic repairs, equivalent paths and
   reading-before-entry all count. `0400` cannot traverse; `0500` and `0777`
   permit unwanted listing and fail the exact-mode objective even if reading
   and entry work. Later permission changes clear entry/read evidence.
6. Close/reopen with the same profile arguments, export/reimport the scenario,
   or use Backup and explicitly restore into a **new empty disposable profile**.
   Existing attempts stay pinned; no history import is claimed.

No listing is **not a confidentiality guarantee**. Someone with search access
can resolve a known or guessed name, and can read it if that file's permissions
allow. Here only the owner has directory search, and the child is owner-readable
0600. Other-user sessions are not simulated. On real Linux, use only a disposable
directory to compare directory read/search and file read, never a personal folder.

## Simulation boundaries

These lessons operate on virtual files only. The permissions contract supports
`help`, `pwd`, `ls [-l] [PATH]`, `cd [PATH]`, `cat PATH`, `chmod u+r PATH`,
`chmod u+x PATH` and `chmod NNN PATH` (exactly three octal digits). Only declared,
learner-owned objects permit changes. The older file-permissions pack retains its
original contract and does not support `u+x`.

No shell expansion, quotes, pipelines, redirects, chaining, wildcard paths,
ownership changes, user switching, supplementary groups, ACLs, special bits or
umask are modeled. The mode check does not simulate another person's session.
Content writing and file execution are not exercised here. Directory read/search
is modeled, but `ls -l` without search reports an error rather than partial Linux
metadata. `cd` without a path returns to the scenario start; above-root traversal
is rejected. Use only syntax advertised in that lab's Command reference.

## Optional real-Linux follow-up (outside the application)

Run only in your own real Linux terminal. This creates a new private temporary
parent, changes one disposable text file, and leaves it for inspection. The
parent's 0700 mode prevents other users reaching the file even while its own mode
is broad; this demonstrates the difference between file bits and effective access.
Do not substitute a personal file path. No sudo, execution or deletion is needed.

```bash
practice_dir=$(mktemp -d /tmp/learning-lab-permissions.XXXXXX) || exit
chmod 700 "$practice_dir"
printf 'Disposable practice note\n' > "$practice_dir/notes.txt"
chmod 777 "$practice_dir/notes.txt"
ls -ld "$practice_dir"
ls -l "$practice_dir/notes.txt"
cat "$practice_dir/notes.txt"
chmod 600 "$practice_dir/notes.txt"
ls -l "$practice_dir/notes.txt"
cat "$practice_dir/notes.txt"
printf 'Practice files remain at: %s\n' "$practice_dir"
```

Explain why both reads succeed and why the final file mode better matches the
goal. This is not a multi-user access test and does not cover ownership changes,
special bits or creation masks needed for broader 104.5 preparation.

## Batch 1 verification — 3 October 2026

Starting HEAD: `0c20fb735e796208c000e60221a18e6617df6856`; working tree initially
clean. A source-only recovery snapshot was created and SHA-256 verified before
editing at:

`/home/drak/.local/state/omarchy-learning-lab/recovery/private-note-source-20261003T195806248589Z`

All **195 pre-existing tracked files** still match that snapshot byte-for-byte.
Only this guide, the new example pack and two new test files were added. No
application code, existing pack bytes, UI, collection, engine, storage or backup
contract changed. The installed app and personal profile were not opened or
modified. All profile mutations in verification used temporary directories.

- Authoritative validation accepts `linux-private-note`, content `1.0.0`, outer
  format 1, engine/domain contract 3, behavior `linux-permissions-2`.
- **257 regression tests pass**: the previous 249 plus 8 focused tests. Coverage
  includes inappropriate modes, insufficient symbolic additions, missing/stale
  evidence, Learn/Challenge, hints, reset, same-profile reopen, separate content
  and history exports, exact pack reimport, existing attempts and pinned versions.
  The run emitted a shutdown `ResourceWarning` about four uncollectable objects;
  it did not fail a test. No unrelated application changes were made to address it.
- New Qt offscreen workflow: **47 checks plus 8 fresh-process restart checks per
  scale**, at 100/150/200%. Tested 800×600, 1024×768 and 1280×900 logical windows,
  entry by Enter/Run, focus after Run/tool close, Challenge hiding, non-modal
  details with Command reference, readable/scroll-reachable guidance and reset.
  Compact guidance uses the existing mission scrolling; all instructions are not
  simultaneously visible. Representative screenshots were inspected for wrapping
  and contrast. No QML errors were reported.
- Existing directory workflow: **62 checks plus 9 restart checks**, offscreen
  at 100%, passed. Existing networking/service behavior is also covered by the
  complete regression suite.
- **Native checks remain outstanding:** connecting to
  `/run/user/1000/wayland-1` failed with errno 1, `Operation not permitted`.
  Offscreen QtTest events do not prove physical-keyboard, native file chooser,
  assistive-technology or exhaustive native scaling acceptance. The subsequent
  owner confirmation below is limited to the workflows explicitly reported.

Reproduce from `app/`:

```bash
python3 -B tools/validate_scenario.py examples/linux-private-note.lab.json
python3 -B -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 \
  python3 -B tests/private_note_acceptance.py --label private-note-100 --expected-dpr 1 --offscreen
```

Repeat with factor/DPR 1.5 and 2 and distinct labels. Generated logs, JSON reports
and screenshots are retained locally under ignored `app/evidence/private-note-*`.
For owner review, use the disposable walkthrough above, check physical keyboard
and native import/export, and resize at native 100/150/200% before recording those
checks as accepted.

## Owner confirmation and commit review — 3 October 2026

The owner confirms that the private-note walkthrough works, including Challenge
and reopening. The owner reports that the Learn screenshot explicitly shows
**100/100**, with mode **0600** and a successful read after the last permission
change. These specific functional checks are accepted. The screenshot was
described by the owner, not independently re-inspected during this review.
This does not establish physical-keyboard, accessibility, every native dialog,
every invalid-input case or exhaustive scaling acceptance.

The four commit candidates are this guide, `examples/linux-private-note.lab.json`,
`tests/test_private_note.py` and `tests/private_note_acceptance.py`. Review found
no credentials, personal progress, recovery copies, environments or generated
evidence in them. The code-like text in the regression fixture is intentional
inert safety-test data. Ignored local evidence and recovery files are preserved.
Application files and pre-existing packs remain byte-identical to the baseline.

### Shutdown warning investigation

Exact original and reproduced message:

```text
gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them
```

On Python **3.14.7** / PySide6 **6.11.2**:

- An untouched `git archive` of baseline
  `0c20fb735e796208c000e60221a18e6617df6856` ran **249 tests successfully** and emitted
  exactly the same warning. The candidate ran **257 tests successfully** and
  emitted the same four-object warning. The new pack is not needed to reproduce it.
- A baseline process that only imports `learning_lab.catalog`, with no app
  instance, profile, test suite or saved attempt, reproduces it too.
- `gc.DEBUG_UNCOLLECTABLE` identifies four **PySide6.QtCore.Property** objects.
  Comparing their addresses before shutdown with the diagnostic list identifies
  them exactly as `AuthoringBridge.view`, `Bridge.view`,
  `CatalogBridge.authoring` and `CatalogBridge.view`.
- Importing QtCore and constructing only a QCoreApplication did not reproduce it.
  This narrows the issue to existing bridge-property finalization in this runtime;
  it does not establish the precise underlying PySide/CPython defect or its fix.

This is an actual report of Python objects that the collector could not reclaim
at shutdown, not a warning about an open profile file or a failed save. Python
documents this distinction in [gc.garbage](https://docs.python.org/3.14/library/gc.html#gc.garbage).
The retained objects here are class-level Qt property descriptors. There is no
evidence from this probe of leaked file descriptors, pending writes or corrupted
saved state: reproduction needs no profile, and exact-state persistence tests,
fresh-process reopening and the owner's reopening check pass. This is not an
exhaustive proof against long-running memory growth or every shutdown failure.

No warning filters or garbage-collector workarounds were added. Fixing existing
bridge teardown or the Python/PySide runtime would be separate maintenance work,
outside this content-only batch. No application change is proposed as part of
this commit.

Reproduce on an isolated baseline checkout from its `app/` directory:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B -Walways -c 'import gc; gc.set_debug(gc.DEBUG_UNCOLLECTABLE); import learning_lab.catalog'
```

Local investigation evidence is retained under `/tmp/private-note-baseline-tests.log`,
`/tmp/private-note-baseline-gc.log`, `/tmp/private-note-import-gc.log` and
`/tmp/private-note-property-map.log`; these logs are excluded from the commit.
The complete candidate regression rerun is in ignored
`app/evidence/private-note-commit-tests.log`. The private-note offscreen workflow
was rerun at 100/150/200%, including same-profile fresh-process reopening; it does
not add native acceptance.

## Batch 2: search-only directory verification — 3 October 2026

Verified starting baseline: `2c32d6d9f51b9a3141c79b9067b240ec0c6b1639`, clean
working tree. Before editing, all 199 tracked files were copied and SHA-256
verified at:

`/home/drak/.local/state/omarchy-learning-lab/recovery/search-only-source-20261003T203606109431Z`

The recovery copy remains verified. All 198 tracked files other than this guide
remain byte-identical, including every existing pack, application module, QML,
template, collection and test. Added only `examples/linux-search-only-directory.lab.json`,
`tests/test_search_only.py` and `tests/search_only_acceptance.py`. No engine,
contract, collection loader, storage or backup-format change was required.
The installed application and real profile were not opened or changed.

- **266 regression tests pass** (257 baseline plus 9 new). Focused cases cover
  numeric/symbolic repairs, relative/absolute paths, either verification order,
  denied listing at 0100, incorrect 0400/0500/0777 modes, invalidated evidence,
  both modes, hints, reset, reopening, imports/conflicts, separate scenario/history
  exports, exact-byte backup/restore, pinned versions and earlier attempts.
  Host API tripwires and inert imported text tests pass.
- **67 Qt offscreen checks per scale** at 100/150/200%: 51 workflow checks,
  8 fresh-process source-profile checks and 8 fresh-process restored-profile
  checks. Each restored attempt retained its exact pin, mode, history, pending
  command and applied state, then completed successfully. Window sizes were
  800×600, 1024×768 and 1280×900 logical pixels. Tests exercise Enter/Run, focus,
  non-modal details alongside Command reference, guidance scroll reachability,
  Challenge hiding, the denied-listing comparison and reset. No QML errors.
  Representative offscreen screenshots were inspected for wrapping and contrast.
- The existing four-Property shutdown warning reproduced unchanged in the full
  suite; its baseline investigation above remains applicable. No suppression or
  unrelated fix was added.
- Native Wayland connection still fails at `/run/user/1000/wayland-1` with
  errno 1, `Operation not permitted`. Physical-keyboard, native chooser,
  accessibility and exhaustive native scaling checks remain outstanding.
  The subsequent owner review is recorded below without extending it to these
  unverified checks.

Reproduce from `app/` using disposable test fixtures:

```bash
python3 -B tools/validate_scenario.py examples/linux-search-only-directory.lab.json
python3 -B -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 \
  python3 -B tests/search_only_acceptance.py --label search-only-final-1 --expected-dpr 1 --offscreen
```

Repeat with scale/DPR 1.5 and 2 and distinct labels. Generated evidence remains
ignored under `app/evidence/search-only-*`. No push or installation was performed.

### Owner review and local commit preparation

The owner reports completing the search-only directory lab review and authorizes
the local commit. This records review completion, not specific additional native
keyboard, accessibility, chooser or exhaustive scaling results.

Commit review is limited to the new JSON pack, this guide and the two search-only
test files. Existing application and pack bytes remain unchanged. No personal
profile, credentials, recovery copy, environment or generated evidence is included;
excluded local files remain in place. The known baseline four-Property shutdown
warning remains documented above, with no suppression or application change.

## Collection batch — implemented for review

The previously proposed batch is now implemented; see [verification](lpic-collection.md).
The scope was **deliver Unit 1 as a discoverable Library collection**, using these six exact
scenario identities rather than creating more near-duplicate permissions labs.

| Scope | Work to deliver together |
| --- | --- |
| Content/resources | A six-entry unit manifest, short skill/prerequisite descriptions, partial-objective labels and the guide; bundle the two pilots without changing their content bytes. |
| Application shell, separately approved | Generalize the current single six-item Fundamentals collection assumption. Render both collections using existing card components, share availability/status for identical pack identities and preserve imported versions, pins, hidden states and Learn/Challenge distinctions. This is application work, not content-only work. |
| Engine capabilities | **None needed for this unit.** Existing contract 1/2/3 behavior remains unchanged. No profile migration or backup-format change is proposed; if implementation reveals such a requirement, stop for review. |
| Acceptance | Fresh/existing profiles, overlap with Fundamentals and imported pilots, version conflicts, hidden/restored labs, truthful per-mode progress, backup round trips, installed-wheel resource loading and native owner review. |

For the next *new-skills* unit after that, a coherent candidate is **create,
organize and locate files**. Content can supply a small project tree and three
missions (create a folder, copy/rename a file, find and read a specified file), but
that unit requires an explicitly scoped engine capability for filesystem mutation
and discovery/grading. Navigation is currently immutable, and the service engine's
mkdir must not be repurposed with unrelated service goals. Commands/options,
permission checks, error atomicity, size limits, pinned state and an opt-in
compatibility version need design and tests before authoring those packs. No such
extension or new unit is included in this batch.
