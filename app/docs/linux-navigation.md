# Find your way around Linux

New importable pack: [`examples/linux-file-navigation.lab.json`](../examples/linux-file-navigation.lab.json).
The approved terminal-first layout, non-modal Lab details, tool sizing and service
editor spacing are retained. This navigation exercise has no service state, file
editing, filesystem writes or Apply requirement.

## Launch and import

From the existing Omarchy graphical session:

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -B -m learning_lab
```

In Library choose **Import scenario…**, select the new JSON file, and open **Find
your way around Linux**. Import starts its own pinned attempt and does not replace
an existing scenario. No real personal profile was opened or changed during
implementation or testing.

For an isolated owner review without using personal progress:

```bash
review_profile=$(mktemp -d /tmp/learning-lab-navigation-review.XXXXXX)
python3 -B -m learning_lab --data-dir "$review_profile/data" --config-dir "$review_profile/config"
```

Keep that path and use the same arguments to verify reopening. The application
starts on Library; Current Lab opens the selected resumed attempt.

## Lesson and grading

Start as simulated `learner` in `/home/learner`. The small tree contains Documents,
Downloads, Projects, a welcome note, `/etc/motd`, and a private simulated `/root`.
Original virtual content contains no host data.

| Objective | Evidence checked | Points |
| --- | --- | ---: |
| Identify the starting directory | Successful `pwd` while in `/home/learner` | 15 |
| Explore its contents | Successful `ls` of `/home/learner` | 15 |
| Visit Documents | Successful `cd` into `/home/learner/Documents` | 20 |
| Read the welcome note | Successful `cat` of `/home/learner/Documents/welcome.txt` | 25 |
| Finish in Projects | Current directory equals `/home/learner/Projects` at submission | 25 |

The first four are **action** objectives. The last is **final state**. Visiting
Projects earlier is insufficient if you leave before submitting. The rubric and
diagnostics explain each kind in Lab details and review. Help, diagnostics,
reading instructions and unsuccessful commands do not supply activity evidence.

Learn suggests `pwd`, `ls`, `cd Documents`, `cat welcome.txt`, then
`cd /home/learner/Projects`, with an explanation and expected result for the current
step only. Guidance adapts the path to the current directory and returns to the
start if identification was skipped. Earlier successful actions can satisfy later
steps. Challenge hides guidance and hints, while retaining explicit goals and
necessary grading rules. Hints explain orientation and path reasoning without a
score penalty. Reset and mode changes archive the prior attempt and clear its
activity in the new attempt.

Equivalent absolute/relative paths, repeated separators, `.` and valid `..`
segments count by their resolved virtual targets. No fixed transcript or command
order is required. Relative and absolute paths are taught, not mandated as an
exact sequence of spellings.

## Bounded simulated commands

```text
help
pwd
ls [-l] [PATH]
cd [PATH]
cat PATH
```

`cd` without a path returns to the pack's starting directory. `ls` defaults to the
current directory and may also name a single file. `-l` reports virtual ordinary
permission bits and ownership. `cat` reads one regular virtual text file. Paths
and commands are case sensitive; quotes, spaces inside paths, `~`, globbing,
variables, shell metacharacters, redirection, pipes and chained commands are not
supported. Unsupported input returns a bounded-simulation explanation.

Missing paths, non-directory traversal, reading a directory and permission
failures leave directory/activity state unchanged. Search permission is checked
at every traversed directory, including before `..`; an inaccessible ancestor
cannot be bypassed by lexical normalization. `/` is the virtual boundary:
`cd /` and `cd .` there succeed, but `cd ..` there is rejected unchanged. This
preserves the existing VFS boundary behavior; a real Linux shell normally stays
at `/` instead. The difference is disclosed in Help and Lab details.

All operations query immutable dictionary-backed virtual nodes. Learner commands
never call a host shell, filesystem, process or network API. Imported code-like
file text remains plain text; pack fields cannot register handlers or executable
expressions. Unsupported versions, predicates, capabilities, arbitrary fields,
archives, assets/URLs and invalid paths fail validation before installation.

## Small backward-compatible architecture extension

- Added trusted `linux-navigation` engine/adapter, reusing the existing VFS and
  allowlisted tokenizer in `linux_service`. Those existing implementations and
  the service engine are unchanged. Navigation has its own initial state and two
  allowlisted predicates: `activity_observed` and `cwd_equals`.
- Reused the shared session lifecycle, registry, portable envelope/digest,
  repository, pinned store and Linux terminal UI. The historical presentation
  identifier `workspace='linux-service'` and field `serviceCwd` select the existing
  Linux UI; they impose no service mechanics on this domain.
- Shared UI changes are limited to an optional domain diagnostic message and
  guide completion text; old service text remains the fallback. No layout change.
- Navigation state contains the pinned immutable `filesystem`, `cwd`, and
  `activity`: four sorted, unique sets of resolved paths for successful `pwd`,
  `ls`, `cd` and `cat`. Evidence is bounded by the pack's maximum 64 nodes and
  survives the existing 100-command/500-line transcript limits. New facts or a
  changed cwd increment the applied revision; duplicate facts do not. Submission
  remains idempotent for an attempt/revision.
- Each activity fact is validated against the pinned tree and operation's path
  type/permissions. This is simulated learning evidence, not a tamper-proof audit
  log. Older attempts are never given evidence they did not record.
- Pack format schema **1**, content version **1.0.0**, domain data schema **1**,
  engine contract **1**, behavior **`linux-navigation-1`** are distinct. Capability
  requirements are `virtual-filesystem`, `file-navigation`, `activity-evidence`.
  Existing canonical digest covers the entire pack, including tree, text,
  objectives, hints and lesson steps. Existing pin and record schema **4** are
  reused without migration or changed storage paths.
- Up to 16 objectives, 32 hints, 64 virtual nodes; the existing 256 KiB pack,
  8 KiB per file, 64 KiB total file text, 256-character paths, and 512-character
  command limits apply. Guided suggestions come from allowlisted predicates and
  validated paths; packs do not contain executable command handlers.
- Scenario export/reimport preserves exact scenario bytes and identity, without
  personal progress. Personal attempt export separately contains activity,
  transcript, hints and assessments. **Importing personal attempt history is not
  supported by the existing contract**; these files are cleanly rejected as
  scenario packs. History reimport was not added.

## Verification — 2 October 2026 (America/Chicago)

### Owner review and local commit preparation

The owner reports that the navigation lab **looks good** and authorizes its local
commit. This records positive visual review only. It does not establish physical
keyboard, screen-reader, native chooser, mixed-monitor or specific native-scale
coverage; those checks below remain outstanding. The commit-preparation review
against `cb8e951` found no secrets, personal progress, temporary profiles or recovery
copies in the 14 selected source/pack/test/documentation files. Generated evidence
stays excluded and is not deleted. The full regression suite was rerun: **140 tests
passed**, using isolated fixtures. All five Qt UI suites were also rerun at
100/150/200% offscreen scale and passed, including fresh-process resume checks.
These reruns do not add native or physical-input acceptance.

### Implementation verification

Baseline `cb8e9518ca1ec308671efa438a6328e8ee05a670` existed; the working tree was
clean before edits. All prior recovery snapshots were verified before creating:

```text
/home/drak/.local/state/omarchy-learning-lab/recovery/linux-navigation-before-20261003T030332568113Z
```

The copy was verified before edits. Final verification covers all 12 snapshots
and byte/metadata equality of real personal progress and configuration against
the new snapshot. Existing pack examples and original networking/service engine
files remain unchanged. The implementation was left uncommitted for owner review;
the subsequent local commit authorization is recorded above.

**Automated:** 140 regression tests pass (126 existing plus 14 navigation tests).
They cover guided progression, Challenge, equivalent paths/order, retained facts,
wrong targets, permissions/root/errors, hostile commands, poisoned host APIs,
imported inert code-like text, malformed/future packs and records, corruption
recovery, pinning, idempotent submission, reset/modes, catalog switching,
same-profile reopen, exact scenario round-trip and separate personal export.
All mutations use temporary fixtures.

**Offscreen Qt:** navigation passes 89 checks plus 10 fresh-process restart checks
per scale at 100/150/200%. Sizes: 800×600, 1024×768, 1180×860, 1280×900 logical
pixels. Checks include direct command-entry clicks, Enter and Run, current-step
guidance, Challenge hiding, no unrelated editor/Apply, non-modal reference with
command reference, splitter drag/retention through output/resizing/lab switching
and restart, prompt/input bounds, readable font sizes, and all six lab records
resuming exactly. In compact windows the mission pane scrolls: focus it and use
PageDown to expose the complete current step; command input remains available.
Screenshots were inspected for contrast and clipping. Existing
offscreen suites also pass at each scale: 85 reference/editor, 153 usability,
71 service lifecycle, 190 networking checks. No new QML errors.

Host `omarchy`, Python 3.14.7, Qt/PySide6 6.11.2. **Native acceptance remains open:**
connecting to `/run/user/1000/wayland-1` fails with errno 1, `Operation not permitted`.
No current native screenshots or physical-input evidence were obtained. The
owner's positive review of the new lesson is recorded above; it does not establish
physical-keyboard/accessibility acceptance or the other native checks listed below.

Generated local evidence (ignored, reproducible):

- [Full regression log](../evidence/linux-navigation-regressions.txt)
- Offscreen results: [100%](../evidence/linux-navigation-100.json),
  [150%](../evidence/linux-navigation-150.json), [200%](../evidence/linux-navigation-200.json)
- [Initial Learn view, 100%](../evidence/linux-navigation-100-initial.png)
- [Compact Learn view, 150%](../evidence/linux-navigation-150-initial-compact.png)
- [Compact reference and terminal, 200%](../evidence/linux-navigation-200-reference-800.png)
- [Native connection probe](../evidence/linux-navigation-native-probe.json)
- [Recovery and personal-data verification](../evidence/linux-navigation-recovery-verification.json)

Reproduce from `app/`:

```bash
python3 -B -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 \
  python3 -B tests/linux_navigation_acceptance.py --label linux-navigation-100 --expected-dpr 1 --offscreen
```

Repeat with scale/DPR 1.5 and 2. Offscreen software rendering and QtTest synthesized
events cannot establish native or physical-keyboard acceptance.

## Short owner checklist — outstanding

- Import through the native chooser; complete Learn with the physical keyboard.
  Confirm explanations and expectations are approachable without outside help.
- Try Challenge with different valid paths; inspect action versus final-state
  feedback. Leave Projects after completing actions and confirm only that final
  objective becomes unmet. Reset, switch modes/labs, and reopen the same profile.
- At 100/150/200% native scale, resize between compact and wide windows, read/scroll
  details, type with details open, resize/close Command reference, and verify
  readable contrast, prompt, text selection and command focus. Recheck the existing
  service editor and its drafts when switching labs.
- Verify physical Tab/Shift+Tab/F6, dialogs, native export/reimport choosers,
  assistive-technology labels/reading order and mixed-monitor behavior. These
  checks remain unverified until there is owner evidence.
