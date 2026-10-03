# Restore access to your file

Pack: [`examples/linux-file-permissions.lab.json`](../examples/linux-file-permissions.lab.json).
This is an original five-minute beginner exercise. The approved terminal-first
interface, non-modal Lab details and service editor layout are unchanged.

## Launch/import

From the existing Omarchy graphical session:

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -B -m learning_lab
```

Choose **Library → Import scenario…**, select the pack above, then open **Restore
access to your file**. It starts its own pinned attempt without replacing other
labs. For review without using personal progress:

```bash
review_profile=$(mktemp -d /tmp/learning-lab-permissions-review.XXXXXX)
python3 -B -m learning_lab --data-dir "$review_profile/data" --config-dir "$review_profile/config"
```

Retain that path and reuse both arguments for restart/resume checks. Reopening
starts on Library; Current Lab opens the selected attempt.

## Learning and grading

Simulated `learner` owns `/home/learner/notes.txt`, initially mode **0200**. Its
parents are accessible. Its original short notes and ownership never change.
Learn presents inspection, a denied read, repair, and verification one step at a
time. It explains owner/group/other classes, read/write/execute, numeric bit values
and why `777` grants unnecessary access. Directory execute means traversal; the
existing VFS requires read and execute to list a directory.

| Objective | Checks | Points |
| --- | --- | ---: |
| Private access | Final mode **0600**: owner read/write, no execute and no group/other access | 70 |
| Verified repair | Successful simulated `cat` of notes after the most recent actual mode change | 30 |

Inspection and the initial failed read guide learning but are **not graded
prerequisites** in either mode. Challenge exposes the goal and constraints without
the guided commands or hints. Supported equivalent paths and approaches pass;
both `u+r` from 0200 and numeric `600` produce the same required result. `777`
followed by a read scores only 30. Correcting it to 600 requires a new read before
full credit. Reapplying an unchanged mode does not invalidate verification.
Diagnostics and viewing the reference never supply read-verification evidence.

Learn can skip already-satisfied steps: a learner who repairs immediately is
asked to verify. Three progressive hints explain reasoning with no score penalty.
Hints are not restricted to three by the shared framework.

## Exact supported syntax

```text
help
pwd
ls [-l] [PATH]
cd [PATH]
cat PATH
chmod u+r PATH
chmod NNN PATH
```

- `u+r` is the **only** symbolic form: add owner-read while preserving every other
  bit. It will not remove excessive permissions previously set with 777.
- `NNN` is exactly three octal digits (`000`–`777`), replacing all ordinary bits.
  Thus `600` is accepted; four-digit `0600` input is deliberately unsupported.
  Stored/displayed modes use four digits. Numeric 6 means read (4) plus write (2).
- Exactly one target, and only pack-enabled **learner-owned regular files**.
  No directory mode editing, recursive options, other symbolic forms, multiple
  targets, special bits, ACLs, supplementary groups or host chmod compatibility.
- Paths use letters, digits, `_`, `.`, `-`, `/`; whitespace separates arguments.
  Relative/absolute paths, `.` and valid `..` work. No quoting, `~`, expansion,
  wildcards, variables, pipelines, redirection, chaining or host commands.
- `cd` without an argument returns to the starting directory. Traversal above
  virtual `/` is rejected unchanged, preserving the existing simulation boundary
  rather than emulating a real shell's root clamping.
- Content editing, file execution, ownership changes and real filesystem actions
  are unavailable. Changes to enabled modes apply immediately; no Apply is needed.

Ownership is checked before mode mutation. A writable file owned by someone else
is still not eligible. Read access chooses **one** permission triplet: owner if
the user owns the node, otherwise its matching group, otherwise other. It never
unions these classes or falls back from denied owner/group bits to other bits.
The modeled user has its same-named group, as in the existing VFS. Search
permission is checked along every traversed directory, including before `..`.

## Architecture and compatibility

The existing `linux-navigation` engine now has an explicit **contract 2** extension
with behavior **`linux-permissions-1`**, domain schema **2**, and required
`mutable-permissions` capability. Pack content is **1.0.0**, outer pack format
schema remains **1**, and existing pinned attempt record schema **4** is reused.
These are distinct versions; there is no data migration.

Contract 1 and `linux-navigation-1` remain supported with their original immutable
tree and command semantics. Service/network engines, original packs and the shared
VFS/tokenizer are unchanged. The navigation base adds three small extension points
for help, evidence recording and validation. The permissions subclass reuses
ordinary navigation commands and adds only its bounded chmod branch and rubric.
Symbolic `u+r` is accepted through an exact syntax check scoped to contract 2;
the shared tokenizer is not broadened.

The pack declares `permission_targets`. Validation requires canonical, reachable,
learner-owned regular files, and refuses undeclared changes. State validation
permits only their mode bits to differ from the pinned tree; paths, node types,
ownership, contents and all other modes are fixed. At most 64 nodes, 16 enabled
files/objectives and 32 hints; existing pack/file/path/command limits still apply.
The four-step beginner lesson has a declared target and data-only explanations;
the engine derives commands from trusted actions, not scripts in a pack.

Bounded `inspected`, `denied` and `verified` path sets supply learning evidence.
Actual mode changes clear verified reads (across enabled files), while inspection
and denied-read facts remain for guidance. Mode/evidence/cwd changes increment the
applied revision. This is local simulated evidence, not a tamper-proof exam log.
Reset/mode changes archive the whole prior attempt and create fresh state.
The existing atomic writer, backup, pinned identity, duplicate submission handling,
bounded command recall and unpruned attempt history remain in use.

Scenario export/reimport preserves exact content and pin without personal state.
History export remains a separate personal-data operation. **History import does
not exist**; an exported attempt is rejected as a scenario pack. Imported packs
are validated JSON; unknown versions/capabilities/predicates/fields, executable
hooks, arbitrary assets, paths and archives fail cleanly. Code-like file content
is displayed as plain text and never executed.

## Verification

### Owner test and commit review — 3 October 2026

The owner reports that the permissions lab **worked well** and authorizes a local
commit. This records a successful owner test; no specific keyboard, full workflow,
display-scale, chooser or accessibility coverage was supplied. Unverified items
in the checklist below remain outstanding.

The commit review against `c7e3361` covers 11 source, pack, test and documentation
files. No secrets, real personal progress, temporary profiles or recovery copies
were found in these candidates. Generated evidence stays excluded and is not
deleted. A fresh isolated regression run passed **154 tests**. All six Qt UI
suites also passed their reruns at 100/150/200% offscreen scale, including
fresh-process resume checks. These runs do not add native acceptance evidence.

### Implementation evidence

Started from a clean tree at **c7e3361b526343c429054a3cbf7d1f593c162825**. Local
`origin/main` points to the same commit, indicating it was pushed. A read-only
live remote check failed (`Could not resolve host: github.com`), so current server
state could not be independently confirmed. No fetch, push or remote change.

Before edits, all 12 prior snapshots were verified and a new source/config/progress
snapshot was created and verified:

```text
/home/drak/.local/state/omarchy-learning-lab/recovery/linux-permissions-before-20261003T042440753806Z
```

Final checks verify all 13 copies, unchanged real personal progress/configuration,
and unchanged existing scenario packs, service/network engines and QML files.
The implementation was left uncommitted for owner review. The subsequent local
commit authorization is recorded above; no Git permission changes or deployment.

**154 regression tests pass**: all 140 prior tests plus 14 permissions tests.
Coverage includes class selection for reads/traversal, ownership, symbolic/numeric
equivalence, broad modes, invalid syntax, simulation escape prevention, stale
verification, mode/reset/history semantics, same-profile reopen, exact scenario
round-trip, separate history export, malformed/imported inert data, future pins
and corruption recovery. Every mutation uses isolated fixtures.

The focused Qt suite passes **62 checks plus 10 fresh-process restart checks per
scale** at 100/150/200%, with 800×600, 1024×768, 1180×860 and 1280×900 logical
windows. It covers direct input, Enter/Run, guide scrolling/readability, permissions
feedback, Challenge, non-modal details, splitter drag and output retention, focus
after tool closure, seven-lab switching, restart and transfers. All five existing
UI suites pass at each scale too. Evidence is **offscreen software rendering with
QtTest synthesized input**, not native or physical-keyboard acceptance.

Host: `omarchy`; Python **3.14.7**, Qt/PySide6 **6.11.2**. The native connection probe
still fails at `/run/user/1000/wayland-1` with errno 1, **Operation not permitted**.
No new agent-obtained native screenshots or physical-keyboard evidence. The owner
has since reported a successful test as recorded above; prior approval of the
interface and navigation lesson is also preserved.

Generated local evidence (ignored and reproducible):

- [Full regression log](../evidence/linux-permissions-regressions.txt)
- [100% Qt results](../evidence/permissions-check-linux_permissions-100.json),
  [150%](../evidence/permissions-check-linux_permissions-150.json),
  [200%](../evidence/permissions-check-linux_permissions-200.json)
- [Compact Learn screenshot](../evidence/permissions-check-linux_permissions-100-learn-800.png)
- [Learn completion, 150%](../evidence/permissions-check-linux_permissions-150-learn-complete.png)
- [Challenge completion, 200%](../evidence/permissions-check-linux_permissions-200-challenge-complete.png)
- [Recovery verification](../evidence/linux-permissions-recovery-verification.json)

From `app/`, reproduce with:

```bash
python3 -B -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 \
  python3 -B tests/linux_permissions_acceptance.py --label permissions-check-linux_permissions-100 --expected-dpr 1 --offscreen
```

Repeat with scale/DPR 1.5 and 2. No packages or system configuration were changed.

## Owner checklist — outstanding

- Import using the native chooser and complete Learn using the physical keyboard;
  check that permission-class and least-privilege explanations are clear.
- In Challenge, try 777 and read, then 600 and read again; inspect rubric feedback.
  Reset, switch labs/modes and reopen the same profile to check retained history.
- At native 100/150/200%, check text contrast, compact guide scrolling, typing with
  Lab details open, divider resizing, selection, Tab/Shift+Tab/F6 and dialog focus.
- Review native export/reimport choosers, assistive-technology reading order and
  mixed-monitor behavior. Offscreen checks do not close these items.
