# Directory permissions: implementation and acceptance

New scenario: **Why can’t I enter this directory?**
[`examples/linux-directory-permissions.lab.json`](../examples/linux-directory-permissions.lab.json).
Authoring resources: [guide](permissions-authoring.md) and
[template](../templates/linux-permissions.lab.json). Use Library → Import scenario
from the existing `python3 -B -m learning_lab` native application. No UI changes.

## Contract assessment and scope

**This was not possible with content-only changes on the starting baseline.**
Contract 2 restricted mutable targets to regular files, fixed the guided repair
to 0600, recorded reads but not entry, and required read plus search for all
directory listing. The gap and extension scope were explained before editing.

The same trusted `PermissionsEngine` now supports contract **3**, domain schema
**3**, behavior **linux-permissions-2**, with three additional required capabilities.
No duplicate engine, arbitrary plugin or UI component was added. Shared VFS and
the older command tokenizer remain unchanged. New names-only listing lives in
the opt-in permissions path, using the existing VFS's permission selection and
resolution. Contract-2 entry points still use their old branches and runtime pin.

New behavior permits declared learner-owned directory modes, exact `u+x`,
declarative Learn actions and traversal evidence. Mutable directories can lose
search while they are cwd without breaking save/resume; absolute recovery paths
remain available. Evidence for `cd` and `cat` is cleared by actual mode changes.
This extends reusable mechanics rather than encoding the Research scenario in
application code. Template customization and the directory pack are then ordinary
validated JSON data. The template demonstrates regular-file use of contract 3 too.

The example starts Research at 0400 and its welcome note at 0600, with searchable
ancestors. `ls Research` lists the note; `cd Research` and reading it fail.
`chmod u+x Research` or `chmod 500 Research` enables the stated goal. Rubric:
exact mode 0500 **70**, successful entry **15**, successful read **15**. Both
verification actions must follow the last mode change; order/valid paths vary.
No initial mistake is required. 0700/0777 permit access but lose the mode points;
0100 also loses the required listing access. Partial `ls -l` metadata output and
full Linux path semantics are explicitly outside the simulation; see the guide.

## Baseline and recovery

Verified clean HEAD **6276c552eb87a1d9790f42d1b627f2f19f2db272**
(`Add beginner Linux file-permissions lab`). Local `origin/main` matched exactly.
Live `git ls-remote` failed because `github.com` could not resolve; no claim of
current live remote verification is made. No push or Git metadata modification.

All 13 earlier recovery snapshots verified, then a new copy was created and
verified before edits:

```text
/home/drak/.local/state/omarchy-learning-lab/recovery/permissions-authoring-before-20261003T141830860338Z
```

Final verification passed for all **14 snapshots**, and the real progress/config
inventories (bytes and metadata) still match the pre-edit copy. All **43 protected
existing source files** checked match their snapshot hashes. See the local
[recovery verification](../evidence/permissions-authoring-recovery-verification.json). Real
personal progress/configuration, original packs, networking/service engines, VFS
and QML remain unchanged. The old permissions AST guard now also recognizes the
new trusted pure lesson helper; its host-execution checks remain intact.

## Results and remaining acceptance

Regression suite: **168 passing tests**, all 154 earlier tests plus 14 new tests.
They exercise the template and a renamed content-only variant, both modes,
read-versus-search behavior, class selection, narrow/broad fixes, permission
loss while inside, ownership, unsupported commands, inert imported text,
malformed packs/states, CLI validation, imports, reset, same-profile restart,
all eight lab records, scenario round-trip and separate history export.

All **seven Qt acceptance suites passed at 100%, 150% and 200% scaling** (21 runs).
The new directory suite passed 62 checks plus nine fresh-process restart checks
per scale, including 800×600, 1024×768, 1180×860 and 1280×900 windows.
Qt tests use temporary profiles and synthesized pointer/key events. Current
screenshots are offscreen software rendering; native acceptance and physical
keyboard/accessibility coverage remain separate. The owner subsequently reported
reviewing the new directory lab and said it looks good. That records visual
approval; it does not establish physical-keyboard or accessibility acceptance.

Native access was blocked: connecting to `/run/user/1000/wayland-1` returned
errno 1, `Operation not permitted`. No permission or desktop changes were made.
Test runtime: Omarchy host, Python 3.14.7, Qt/PySide6 6.11.2.

Local ignored evidence is reproducible and may be absent from a fresh checkout:

- [Regression results](../evidence/permissions-authoring-regressions.txt)
- [UI suite summary](../evidence/permissions-authoring-ui-results.json)
- Directory UI: [100%](../evidence/authoring-directory_permissions-100.json),
  [150%](../evidence/authoring-directory_permissions-150.json),
  [200%](../evidence/authoring-directory_permissions-200.json)
- [Compact Learn view](../evidence/authoring-directory_permissions-100-learn-800.png)
- [Completed Learn view](../evidence/authoring-directory_permissions-150-learn-complete.png)

Owner checklist:

- Import the new pack; check that name listing versus directory entry makes sense.
- Complete Learn and Challenge with a physical keyboard; try both narrow fixes
  and reject unnecessary access. Check reset/history and same-profile reopen.
- At native 100/150/200%, check heading wrapping, guide scrolling, terminal focus,
  Lab details beside Help, file choosers, accessibility and mixed-monitor behavior.

The owner has now authorized a local commit after regression and file review;
see the [commit review](permissions-contract-review.md#local-commit-review).
No push, deployment or packaging is authorized.
