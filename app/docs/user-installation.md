# User-local installation and application-menu launch

This is an owner-run workflow. Agent development used only temporary staging
trees. The owner subsequently reports successful installation and Omarchy menu
launch, with the Learning Lab entry and icon visible. This commit review leaves
the working installation untouched. The approved UI, original packs, grading and data formats are
unchanged. The SVG is original project artwork, packaged in the wheel.

## Reviewed installation command

To install or update from a reviewed checkout in your existing Omarchy session:

```bash
python3 -B /home/drak/Documents/dlms_lab/app/tools/user_install.py install
```

This builds from the matching checkout, installs into a new dedicated venv,
checks dependencies and runs an offscreen installed-wheel smoke test. Only then
does it activate that release and publish a standard desktop entry. Open the
application menu and search **Learning Lab**. Source launch remains available.
No sudo, system Python installation or shell/plugin configuration is used.

The build uses the declared `setuptools` backend in a separate build venv; the
runtime venv installs the wheel and its declared PySide6 dependencies. Only binary
runtime dependencies are accepted. Internet access to the Python package index is
needed unless a complete trusted local wheelhouse is supplied. No downloaded
installer scripts, dependency mirrors or network-restriction bypasses are used.

## Stable paths

Defaults for `/home/drak`:

| Purpose | Path |
| --- | --- |
| Managed application root | `/home/drak/.local/opt/omarchy-learning-lab/` |
| Each independent installation | `releases/<UTC-time>-<unique-id>/venv/` under that root |
| Active release | `current` symlink under that root |
| Rollback target | `previous` symlink under that root |
| Stable executable | `/home/drak/.local/opt/omarchy-learning-lab/launch` |
| Desktop entry | `/home/drak/.local/share/applications/omarchy-learning-lab.desktop` |
| Project icon | `/home/drak/.local/opt/omarchy-learning-lab/current/icon.svg` |
| Existing personal progress | `/home/drak/.local/share/omarchy-learning-lab/` — retained |
| Existing personal configuration | `/home/drak/.config/omarchy-learning-lab/` — retained |

The desktop entry honors `XDG_DATA_HOME` if configured; Qt continues to honor its
established XDG data/config locations. The launcher does not override them. Keep
the same XDG environment across install/update/uninstall; the ownership marker
records the desktop destination and refuses to adopt a changed path silently.

The launcher resolves `current` to the actual release path before executing that
venv's Python with `-I -m learning_lab`. It works independently of cwd, ignores
`PYTHONPATH`, and keeps an already-running process tied to its original release.
Arguments are forwarded without shell interpretation. The desktop ID matches
the application's existing `omarchy-learning-lab` identity.

## Build a wheel separately or use a wheelhouse

Choose an empty output directory outside the checkout:

```bash
python3 -B /home/drak/Documents/dlms_lab/app/tools/user_install.py build \
  --output /tmp/learning-lab-owner-wheels
```

Then install the resulting trusted wheel:

```bash
python3 -B /home/drak/Documents/dlms_lab/app/tools/user_install.py install \
  --wheel /tmp/learning-lab-owner-wheels/omarchy_learning_lab-0.1.0-py3-none-any.whl
```

Use a wheel built from this revision or later: the installer requires its packaged
icon. The earlier owner-built collection wheel predates that icon. `--source`
can point to another reviewed `app/` source directory. Build and install do not
write generated artifacts into the source tree.

Add `--wheelhouse /absolute/path/to/trusted-wheels` to either command for
`--no-index` dependency resolution. It must contain all required build/runtime
wheels compatible with this Python/platform. Missing dependencies stop preparation;
they do not replace an active installation.

## Updates and rollback

Run the same install command from the reviewed updated checkout. Each update
creates a new release at its final path; venvs are never moved after creation.
Preparation must pass all of:

1. Wheel build (or read the supplied wheel), including the packaged icon.
2. Installation into a fresh venv without system site packages.
3. `pip check`.
4. Packaged QML/resources, all four collections (22 unique packs, including both six-lab LPIC units and the eight-lab text unit), and start/resume smoke checks in new
   disposable profiles and fresh Python processes.

An atomic `current` symlink replacement is the final activation step. Previous
releases remain on disk. Failure leaves the current release selected and preserves
the candidate's `install.log`. Successful candidates also retain their wheel,
SHA-256 in `ready.json`, smoke harness and log. Concurrent operations are blocked
by a lock; the installer does not remove someone else's lock. Existing unmanaged
application directories or edited desktop/launcher files are preserved with an
error rather than overwritten.

Close Learning Lab normally before starting the new version so the existing
single-writer protection and saves remain straightforward. Roll back with:

```bash
python3 -B /home/drak/Documents/dlms_lab/app/tools/user_install.py rollback
```

Rollback switches to the previously prepared release and retains the replaced
release as the next rollback target. It changes application selection only:
personal data is never rewound or migrated. If a future app version requires a
data migration, stop for a separate reviewed migration/backup plan. System Python
upgrades can invalidate old venvs; build a new release with the new interpreter
rather than assuming an older venv will always remain runnable.

There is no automatic release pruning. Multiple Qt environments can consume
significant disk space; unsuccessful candidates also remain for inspection.

## Uninstall application files, keep personal data

After closing the app:

```bash
python3 -B /home/drak/Documents/dlms_lab/app/tools/user_install.py uninstall
```

This explicitly removes this installer's application root (including its releases,
wheels and logs) and its matching desktop entry. It refuses an unmanaged root,
modified launcher/desktop file, unexpected root files or unsafe release links.
Progress, configuration, recovery snapshots and the source checkout are never
enumerated for deletion. There is no data-purge option.

## Staging and reproducible smoke test

To exercise the installer without using the real home/menu:

```bash
stage=$(mktemp -d /tmp/learning-lab-stage.XXXXXX)
python3 -B /home/drak/Documents/dlms_lab/app/tools/user_install.py install \
  --staging-root "$stage"
```

Application files go under `$stage/home/.local/opt/omarchy-learning-lab/` and the
desktop entry under `$stage/data/applications/`. Use the same `--staging-root`
for rollback/uninstall tests. Do not launch the staged entry against the real
profile: the installer itself runs only isolated smoke profiles. For a manual
staged window, pass `--data-dir "$stage/manual-data" --config-dir "$stage/manual-config"`
to its `launch` script.

After a successful install, the standalone harness is retained with each release:

```bash
~/.local/opt/omarchy-learning-lab/current/venv/bin/python -I -B \
  ~/.local/opt/omarchy-learning-lab/current/installed_smoke.py --require-icon
```

The harness can also be copied to any temporary directory and run by a dedicated
wheel-installed venv. It requires wheel metadata and package files inside that
venv, creates temporary data/config, loads packaged QML and all four collections
(22 unique packs), starts each lab, runs simulated `pwd`, and saves pending
commands. It completes both original LPIC pilots, all six file-management labs in both modes,
all eight text labs in both modes, and an authored Learn/Challenge pack,
then verifies all saved attempts and the selected draft in a fresh process. It uses
offscreen Qt; it does not require the source checkout or examples directory.

## Evidence and acceptance limits

Baseline was clean at `1baca2fdfdabff270db8791e3b9f67d60ce23b5b`.
The owner reports building/installing the committed collection wheel in separate
environments, passing `pip check`, and launching with all six Fundamentals entries
visible. This establishes that reported build/install/launch result, not complete
installed-lab or native-dialog acceptance. The owner additionally reports that
the user-local installation succeeded, the Omarchy application-menu launch works,
and the Learning Lab entry and icon are visible. Those checks are recorded as
**owner-reported success**, not independently repeated during this review.

This work:

- **197 tests passed**: the previous 183 plus 14 installer tests. Transaction
  tests use fixture runners to exercise preparation failures, activation,
  rollback, locks, path/ownership checks and uninstall retention; they do not
  substitute for an actual successful pip installation of this revision.
- Generated desktop entries pass the installed `desktop-file-validate`; the
  original SVG parses with QtSvg. Launch tests work from `/` with spaced paths.
- The standalone smoke harness was copied outside the checkout and passed both
  phases against the owner's existing wheel-installed environment. Its six packs
  loaded and all attempts resumed; `pip check` again reported no broken requirements.
  This older artifact lacks the new icon, so this run omitted `--require-icon`.
- An actual new installer run used only an explicit temporary staging root. It
  stopped fetching declared `setuptools` from `pypi.org` with DNS error
  `[Errno -2] Name or service not known`. No active link or desktop entry appeared.
  That agent run did not verify the new wheel installation or icon-inclusive smoke
  end to end. The later owner installation report is separate evidence; no
  restriction was bypassed or system package changed by the agent.
- Collection, Linux service and networking/framework Qt suites were rerun at
  100/150/200% offscreen. Native input/menu acceptance is separate.
- Existing recovery snapshots verified before work; a new combined source/data
  snapshot was not taken because Learning Lab was running. Real personal data was
  not used as a test profile or edited by installation tooling.

Ignored local evidence: `evidence/user-install-commit-regressions.txt`,
`evidence/user-install-regressions.txt`,
`evidence/user-install-ui-results.json`, `evidence/user-install-owner-wheel-smoke.txt`,
and `evidence/user-install-staging-attempt.txt`.

Owner checks still outstanding (menu launch and visible entry/icon are reported successful):

- Complete individual installed labs, including save/reopen, with a physical keyboard.
- Exercise native import/export file dialogs, accessibility, focus and display scaling.
- Confirm existing personal history and Learn/Challenge distinctions remain visible.

This review does not change the working user installation, desktop settings or
personal data. Local commit execution or a Git-write blocker is reported
separately. No push, publication or deployment is performed.
