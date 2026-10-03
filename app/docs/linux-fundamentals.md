# Linux Fundamentals collection

The Library reuses its scroll view, cards, text and button components. Six compact
cards give a suggested order, a short skill description, separate Learn/Challenge
status and Start/Continue. Any lab can be chosen immediately. The terminal and
networking workspaces, simulation engines, pack content and grading are unchanged.

## Curated content

Titles come from the validated packs. Runtime copies below are under
`learning_lab/collections/packs/`; matching authoring examples remain in
`examples/`. Tests require their bytes, and therefore identities, to match.

| Order | Actual title | Resource filename |
| --- | --- | --- |
| 1 | Find your way around Linux | `linux-file-navigation.lab.json` |
| 2 | Start your first service | `linux-service-basics.lab.json` |
| 3 | Restore access to your file | `linux-file-permissions.lab.json` |
| 4 | Why can’t I enter this directory? | `linux-directory-permissions.lab.json` |
| 5 | Read the fieldwork handover | `linux-archive-access.lab.json` |
| 6 | Recover a failed web service | `linux-web-document-root.lab.json` |

The trusted `collections/linux-fundamentals.json` supplies ordering and short
skill text. `collections.py` reads resources through `importlib.resources` and
validates scenario bytes through the existing portable loader. Collection entries
do not define new commands, predicates, modes or executable extensions.

## Installation, identity and progress

Opening Library validates resources in memory; it does not install these packs
or create their attempts. Start passes the exact approved bytes to the existing
`PackRepository.install`, then opens the ordinary pinned session. It uses the
existing draft confirmation before installing/switching. There is no prerequisite
locking or new attempt-storage format.

- Exact imported content reuses the existing key, attempt, history and mode. The
  collection replaces its presentation in the generic list, so it is not shown
  twice. Start/Continue never resets an attempt.
- Same ID/version with different content blocks the curated entry with an error;
  the installed custom content remains available below. No replacement or merge.
- Different versions and custom IDs remain distinct in the generic list. No
  automatic upgrade, history migration or score transfer occurs.
- Reimport of identical content remains idempotent. A missing installed pack with
  an existing pinned attempt offers Continue but omits status until validated and
  resumed. Invalid resources leave the original Library accessible with a notice.
- Start means no known pinned attempt. Continue means an existing attempt can be
  opened; it does not promise that it is incomplete or usable without recovery.

Progress is derived separately for Learn and Challenge from the current validated
attempt plus all archived pages, using the existing final-grade `complete` flag.
Recorded activity/drafts/diagnostics count as in progress; a newly created idle
attempt can correctly show Not started alongside Continue. A completed prior
attempt remains completed after reset, but only in its original mode. The new
Library code never changes hints, assessments, scoring or mode semantics.

Unknown, recovered or unreadable records suppress collection status instead of
inventing a result. Existing generic Library/history displays retain their prior
behavior. Pack-loading or write errors preserve existing files and report failure.

## Source and distribution resources

Normal launch:

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -B -m learning_lab
```

No manual import is required. The runtime does not read `examples/` or resolve
these packs relative to the working directory. `pyproject.toml` declares QML,
networking packs and collection resources as package data, with explicit package
discovery and setuptools build backend.

Verified independently of the source working directory:

1. Resource loading from the source package while cwd is a temporary directory.
2. A staged installed-package layout containing only package Python and declared
   resource files, with no external examples: Qt renders and starts a Linux lab.
3. The resource loader reads all six packs from a ZIP-imported Python package.

**Actual wheel build attempted; blocked before backend execution.** For the local
commit review, source and package resources were copied into a temporary directory
outside the checkout. A new venv without system site packages used its bundled
pip to run `pip --isolated wheel --use-pep517 --no-deps` against that copy. The
project's declared build dependency is `setuptools`. Fetching it from
`https://pypi.org/simple/setuptools/` failed with name-resolution error
`[Errno -2] Name or service not known`; the build exited 1 during installation of
build dependencies. No wheel was produced, so installation into a second test
environment and testing resources from that installed wheel were not possible.
No restrictions were bypassed, and no system Python packages were changed.

Subsequent owner verification: the owner successfully built and installed the
committed wheel in separate environments, passed `pip check`, and launched with
all six entries visible. The later [installation-workflow smoke](user-installation.md)
also verified basic installed-pack start/resume in that environment. Individual
installed-lab completion and native file dialogs are still not fully verified.

The earlier staged-layout test verifies declared resource inclusion and runtime
lookup, not execution of the wheel build backend or an actual wheel installation.
The complete Qt application still expects ordinary unpacked QML resources; ZIP
testing covers the collection loader, not a zipapp distribution.

## Baseline, recovery and results

Started with a clean working tree at
`9b12d85024f934f1f985fab2e33b135d19c0b224`
(`Add directory-permissions labs and reusable authoring workflow`). Local
`origin/main` matched. Live `git ls-remote` failed with DNS resolution for GitHub;
local tracking state is not a claim of live remote verification.

Before editing, all 14 earlier recovery snapshots verified, followed by a verified
new snapshot:

```text
/home/drak/.local/state/omarchy-learning-lab/recovery/linux-fundamentals-before-20261003T151126933114Z
```

At feature completion, verification passed for all 15 snapshots and real personal
data/config inventories matched the pre-edit copy. This is historical evidence,
not an assertion that subsequent owner usage left the profile unchanged. Tests
use temporary profiles only.

- **183 regression tests passed**: all previous 172 plus 11 collection tests.
- Coverage includes unchanged pack bytes/titles/order, fresh profiles, lazy
  installation, exact imports/progress, repeated launches, Start/Continue, reset,
  mode separation beyond one history page, custom versions, conflicts, drafts,
  unavailable resources, write failures, newer records and missing installed packs.
- All seven existing Qt suites passed at 100/150/200% scaling. One existing
  service test now activates its collection button instead of the removed
  duplicate generic card; its simulation assertions remain intact.
- The new collection Qt suite passed **65 checks plus eight fresh-process checks
  per scale**, including 800×600, 1024×768 and 1280×900, scroll/focus access to all
  six buttons, arbitrary entry order, draft confirmation and Learn/Challenge status.
- Runtime: Omarchy host, Python 3.14.7, Qt/PySide6 6.11.2. These are offscreen
  software-rendered checks with synthesized Qt input, not physical-keyboard proof.

Local ignored evidence (not required in a checkout):

- [Regression log](../evidence/fundamentals-regressions.txt)
- [Existing UI matrix](../evidence/fundamentals-ui-regressions.json)
- [Collection 100%](../evidence/fundamentals-100.json),
  [150%](../evidence/fundamentals-150.json), [200%](../evidence/fundamentals-200.json)
- [Compact Library](../evidence/fundamentals-100-library-top-800.png)
- [Larger Library](../evidence/fundamentals-200-library-top-1280.png)
- [Preservation](../evidence/fundamentals-preservation.json)

The local-commit review reran all **183 tests** and the eight offscreen UI suites
at 100/150/200%. Current ignored evidence is
`evidence/fundamentals-commit-regressions.txt`,
`evidence/fundamentals-commit-ui-results.json`, and
`evidence/fundamentals-commit-wheel.json`. Build environments, temporary source
copies, logs and generated screenshots are excluded from commit candidates and
preserved locally. No actual-wheel success is inferred from the source/UI tests.

## Owner checks still outstanding

The native Wayland socket `/run/user/1000/wayland-1` returned errno 1,
`Operation not permitted`. The owner now reports that the Library collection
works great. This is successful owner-reported functional review; it does not
establish that every keyboard, accessibility, scaling or platform check passed.

- In the normal graphical session, start any lab directly, then use Continue on
  an existing import and confirm its mode, hints and history remain correct.
- Use Tab/Shift+Tab, Enter and scrolling to reach every card at native
  100/150/200%; check readability, focus, accessibility and mixed-monitor behavior.
- Reset or change mode, return to Library, and verify that Learn completion is
  never shown as Challenge completion. Restart and confirm the same attempt resumes.

The owner authorizes the local commit **Add built-in Linux Fundamentals
collection** after review and available tests. Commit execution or a Git-write
blocker is reported separately; this document does not assert commit success.
No push, deployment, real-history migration or system-setting change was performed.

The owner also reports successful user-local installation and Omarchy menu launch,
with the Learning Lab entry and icon visible. See [installation acceptance](user-installation.md#evidence-and-acceptance-limits).
This does not close the remaining installed-lab, keyboard or accessibility checks.
