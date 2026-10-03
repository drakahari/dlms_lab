# LPIC Foundations collection — delivery and acceptance

## Scope and identity

Baseline: `9e7403eb2ea5e2e33853febdaf5b34ce49729e7b`, initially clean.
Recovery snapshot (202 tracked files, SHA-256 reverified after implementation):

`/home/drak/.local/state/omarchy-learning-lab/recovery/lpic-collection-source-20261003T210733462068Z`

Two collapsible Library sections reuse the existing cards, spacing and actions.
Linux Fundamentals retains its original six items and order. **LPIC-1 Foundations:
Files & Permissions** presents the six accepted labs in the requested order.
Both sections start expanded; collapse a heading to scan another collection.
Expansion is session-local and is not a profile setting. No forced unlocks.

The manifests describe organization, not scenario identity. Eight unique exact
packs appear in twelve collection positions. Four shared labs use one content
key, one pinned store, and the same distinct Learn/Challenge summaries in both
places. An existing exact import is reused without replacing its bytes. Different
content versions remain separate. A same-ID/version different-content import
remains accessible under other scenarios and blocks the conflicting bundled start.

Each section reports per-mode completion out of all six labs, including hidden
ones. Hiding never awards completion or removes existing completion. If progress
cannot be read reliably, totals are withheld. Inactive counts point to the existing
Show hidden / removed list, which lists each exact scenario once. Hiding/restoring
a shared lab applies across both appearances. Existing Restore to Library and
Restore and resume behavior, including explicit attempt choice, remains in place.

### Previously removed imports becoming bundled

Library settings schema 1 already stores exact keys and `hidden` / `removed`.
The reader now accepts a removed bundled key **only when its exact installed pack
is also present**. Startup does not rewrite the file or reactivate the lab. Reimport
also preserves removal. Once explicitly restored, it follows normal built-in Hide
behavior. New removal of built-in resources is rejected; no bytes are deleted.

No storage migration, identity change, engine/grading change or backup-format
change was needed. Backup versions 1 and 2 remain supported; the existing validator
now obtains known built-in keys from both collections. Round trips preserve exact
pack bytes, attempts, drafts and visibility. Older applications lacking these new
built-in keys may reject backups containing a newly hidden pilot as an unknown
Library choice; use this version or later to restore such backups. This is a
resource-compatibility limit, not a claim that an older reader can understand new
bundled resources. No backward-reader bypass was introduced.

## Pack and coverage review

The existing Fundamentals manifest, all pre-existing pack/example bytes, domain
engine files and packaging declaration match the baseline. Both pilots are exact
resource copies. All six current content versions remain `1.0.0`.

| Scenario file | Canonical content digest (without `pack:` prefix) |
| --- | --- |
| `linux-file-navigation.lab.json` | `b1af1ddafd1d243011df3c062859516f14f5181dc5d545ea56d920df6141884e` |
| `linux-file-permissions.lab.json` | `8ebc6077bf6d11c8b83cdd60eccb0461e9b086a8b8be8e82e454a37ba74db4ce` |
| `linux-directory-permissions.lab.json` | `12d4eb5782e32afdad904e4be84335c2a6719005f132303f8c89fe129c8dbc85` |
| `linux-private-note.lab.json` | `03b7c4d8f06106be669ac77e8c060580058ffcee60215ed876e90d5623a559c3` |
| `linux-search-only-directory.lab.json` | `3b2e108eb4cf2ed531039d274b39d2516c07d93512d92a7a0e11d7579e0701a2` |
| `linux-archive-access.lab.json` | `e2a7a19a83b38ad4cb2e77edf06909fbc1580ef8c7c66bd325b6f9693f9fc9d6` |

The [unit guide](lpic-unit-1.md) explains sequence, prerequisites and limits.
Descriptions were reviewed against the accepted lab behavior: navigation is
introductory 103.1/103.3 preparation, ordinary permissions are partial 104.5
practice, and handover reinforces directory access rather than adding objective
coverage. The unit does not teach shell processing, ownership changes, special
bits, umask, or full LPIC-1 preparation. No LPI affiliation is implied.

## Verification — 3 October 2026

- **275 regression tests pass**, including nine new multi-collection cases.
  Disposable fixtures cover shared progress in both directions, separate modes,
  hidden/removed overlaps, exact reimport, old pinned versions, conflicts, reset,
  reopen, backup round trips, truthful counts, and malformed manifests.
- Offscreen Qt at **800×600, 1024×768 and 1280×900 logical pixels**, DPR **1 / 1.5 / 2**:
  LPIC collection 73 checks plus 7 fresh-process restart checks per scale;
  Fundamentals 65 plus 8 restart; Library cleanup 71; backup/restore 90;
  authoring 78; terminal/reference/editor 85. Synthesized focus, activation,
  menus, scrolling, section expansion and card bounds were exercised.
- Screenshots inspected for wrapping, readable padding and reachable controls;
  no QML errors in these runs. Scroll boundaries can partially reveal the next
  card, while focusing its action scrolls the complete card into view.
- Actual wheel built with the declared isolated setuptools backend. Network
  access initially failed in the sandbox; the normal approved retry succeeded.
  Installed into a separate `/tmp` venv; `pip check` passes. A copied smoke script
  ran from `/tmp` with `python -I`, using site-packages and no checkout/example
  lookup. Packaged QML/icon/authoring resources, both collections, all eight unique
  packs and all six unit entries load. All eight start; both pilots complete;
  authored Learn/Challenge and exact fresh-process resume pass. A separate byte
  comparison confirms all six installed unit packs equal accepted sources.
- Wheel: `/tmp/lpic-collection-wheel-approved/omarchy_learning_lab-0.1.0-py3-none-any.whl`.
  Isolated runtime: Python 3.14.7, PySide6/Shiboken6 6.11.2.
- Previous v1 backup-reader compatibility probe still rejects v2 before restoring
  anything and restores its v1 positive control. Current v1/v2 coverage passes.
- Known baseline warning remains unsuppressed:

```text
gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them
```

See the existing [warning investigation](lpic-unit-1.md#shutdown-warning-investigation).
It predates this batch; no engine or bridge-finalization workaround was added.

Evidence (ignored local artifacts): `app/evidence/lpic-regressions.log`,
`lpic-ui-matrix.json`, `lpic-installed-wheel.json`, `lpic-resource-hashes.json`,
and `lpic-matrix-*.json/.png`. No generated evidence belongs in a future commit.

Commit review reran all 275 regressions, the 73-check LPIC UI suite and its
7-check fresh-process probe at 100/150/200%, and the installed-wheel smoke.
All passed. The wheel package bytes and copied smoke harness match the final
application candidate. The exact 18-file candidate list excludes personal
profiles, secrets, recovery copies, environments, wheel/build outputs and
generated evidence; excluded local files remain in place.

## Owner acceptance (one short disposable check)

**Owner-reported checks passed:** finding the new collection, continuing the
same saved attempt between collections, and launching the bundled private-note
lab without importing. This does not establish exhaustive native, keyboard,
accessibility, file-dialog or scaling acceptance. The recipe below remains
available for a disposable repeat check.

Launch the candidate source, not the working installed app:

```bash
cd /home/drak/Documents/dlms_lab/app
review_profile=$(mktemp -d /tmp/learning-lab-lpic.XXXXXX)
printf 'Keep this disposable profile path for reopening: %s\n' "$review_profile"
python3 -B -m learning_lab --data-dir "$review_profile/data" --config-dir "$review_profile/config"
```

1. Find **LPIC-1 Foundations: Files & Permissions** in Library; collapse
   Fundamentals if helpful. Check the six titles and honest coverage note.
2. Start **Restore access to your file** from either section, type `pwd`, return
   to Library, and Continue it from the other section. Confirm the same transcript,
   mode and progress. A previously completed disposable attempt can be used instead.
3. Start **Make an overexposed note private** from the LPIC section without importing.
   No need to replay all six accepted labs. Close/reopen with the printed profile
   paths if checking persistence manually.

Native Wayland socket access is blocked here: `PermissionError`, errno 1,
`Operation not permitted`. Native compositor rendering, physical keyboard,
screen-reader accessibility, native file dialogs, and exhaustive scaling remain
outstanding. Offscreen Qt tests and the three owner reports do not establish
these broader checks. The installed app and real profile were not launched,
updated, backed up or changed during development and commit review.

## Changed files

Application: `learning_lab/collections.py`, `catalog.py`, `library_state.py`,
`profile_backup.py`, and the Library portion of `qml/Main.qml`.
Resources: `collections/index.json`, `collections/lpic-foundations.json`, and
byte-identical copies of the two pilot packs in `collections/packs/`.
Tests: new `test_lpic_collection.py` and `lpic_collection_acceptance.py`; updated
`test_linux_collection.py` and `test_private_note.py` for multiple collections and
accepted pilot bundling. Installed verification: `tools/installed_smoke.py`.
Documentation: this report, `lpic-unit-1.md`, `user-installation.md`, and
`framework-acceptance.md`. No terminal workspace, engine, grading, pack contract,
installer activation behavior or personal records were changed.
