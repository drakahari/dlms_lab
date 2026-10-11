# Later update of the menu-installed app

**Procedure only; not performed by this assessment.** Source commits/pushes do not
update the application menu. Follow the existing [user-local installer](user-installation.md)
after owner approval. No sudo or system Python changes are needed.

## Identify the build accurately

Read-only inspection on 2026-10-11 found `current` selecting release
`20261003T162404Z-044bf565`. Its metadata says `0.1.0`; current source also says
`0.1.0`. That semantic version does **not** distinguish these builds. Installed
Main.qml, collection index and VM unit index hashes differ from accepted checkout
`67337af47561d6bccbb49cbba708bd1e1a4bb59e`. Do not attribute an old installed
window's behavior to current source.

The installer records a wheel SHA-256 and smoke result in each release's
`ready.json`, not the Git commit. A wheel hash identifies bytes, not authenticity
or an automatic Git provenance assertion. Retain the reviewed checkout hash,
wheel hash and selected release together; do not invent a commit identity for the
older installation.

Before an approved update:

```bash
git -C /home/drak/Documents/dlms_lab status --short --branch
git -C /home/drak/Documents/dlms_lab rev-parse HEAD
readlink -f /home/drak/.local/opt/omarchy-learning-lab/current
cat /home/drak/.local/opt/omarchy-learning-lab/current/ready.json
```

Review any checkout changes before building. Close the app normally and resolve
any save error with Retry save. If a guest is running, decide deliberately how to
stop/preserve it through its owning profile; an application update does not grant
permission to terminate it. Do not use a menu launch to inspect a disposable
profile unless you explicitly supply its isolated paths.

## Preserve data, prepare, then activate

Use the app's existing **Backup profile** workflow before a future update, storing
it separately; never copy a changing profile. VM disks, sessions and guest reports
are **excluded** and need separate retention. No data migration is part of this
accepted build. Retain the previous release; do not prune it automatically.

The reviewed owner-run command, **only after update approval**, is:

```bash
python3 -B /home/drak/Documents/dlms_lab/app/tools/user_install.py install
```

A complete trusted local wheelhouse can be supplied with
`--wheelhouse /absolute/path/to/wheelhouse`; otherwise declared build/runtime
wheel resolution needs package-index access. This does not fetch arbitrary
installer scripts. Failure must be reported, not bypassed.

The installer prepares a new release at its final user-local path, builds the
wheel, installs a fresh venv, runs `pip check`, and tests installed packaged
resources and simulator start/reopen in disposable profiles. Only successful
preparation activates `current` atomically and updates its managed launcher/entry.
It refuses unsafe/unmanaged collisions. Failed preparation retains the active
release and candidate log. It does not alter established progress/config paths.
The smoke is offscreen; it is not exhaustive native VM/dialog acceptance.

Then record the new `current` target and `ready.json` wheel digest, launch from the
menu, and inspect the expected eight simulator collections and nine/76VM lesson
metadata. Compare existing saved progress; do not Reset merely to check an update.
The generic `0.1.0` display alone cannot verify this content revision.

## Rollback and limits

After normal closure:

```bash
python3 -B /home/drak/Documents/dlms_lab/app/tools/user_install.py rollback
```

Rollback switches application releases; it does not rewind personal records or
migrate them. Keep the same XDG environment. If a future version changes data
formats, review compatibility before activation/rollback. Python ABI upgrades can
invalidate older venvs even when their files remain intact. Retain profile backup
and original VM images/generations independently; do not replace their pins.

The installed app, launcher, desktop entry, settings and owner profile were not
written during this task. See [diagnosis](shutdown-warning-diagnosis.md) for the
known warning; update is not claimed to fix it.
