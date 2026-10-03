# Linux service troubleshooting — bounded second domain

The [usability follow-up](linux-usability.md) makes the terminal the primary view,
fixes divider persistence, collapses mission detail, and adds a separate beginner
pack. The original troubleshooting pack and its `linux-service-1` pin are unchanged.
Delivery results near the end of this document describe the initial implementation;
the follow-up report contains the current regression and UI results.

## Launch without touching personal progress

```bash
cd /home/drak/Documents/dlms_lab/app
linux_lab_profile=$(mktemp -d /tmp/learning-lab-linux-XXXXXX)
python3 -B -m learning_lab --data-dir "$linux_lab_profile/data" --config-dir "$linux_lab_profile/config"
```

Run from the existing graphical session. In **Library → Import scenario…** choose
`examples/linux-web-document-root.lab.json`, then open **Recover a failed web
service**. Keep the temporary profile path and use it again to test reopening.
Normal `python3 -B -m learning_lab` uses personal XDG progress; development tests
have not imported anything into that profile. No additional dependencies required.

## Supported terminal and editor

The dock is labeled **Simulated Linux terminal**. Commands are case sensitive.

```text
help
pwd
ls [-l] [PATH]
cd [PATH]
cat PATH
mkdir [-p] PATH
systemctl status|start|restart UNIT
journalctl [-u UNIT] [-n N]
```

`UNIT` is `lab-web` or `lab-web.service` in this scenario. Omitted `cd` path returns
to its initial `/srv`; `ls` defaults to the virtual working directory. `journalctl`
defaults to the only service and the latest 20 events; `-n` accepts 1–100.
Paths use ASCII letters, digits, slash, dot, underscore and hyphen, at most 256
characters. Relative paths, `.` and `..` are resolved inside the virtual tree;
traversal above `/` fails. Permissions are checked during each traversal step,
including before `..`, so an inaccessible ancestor cannot be bypassed lexically.

There is no shell grammar: no pipes, redirection, chaining, substitution, quoting,
globbing or environment expansion. Unknown commands/options/services fail with
an explicit bounded-simulation message. No `sudo`, `chmod`, `rm`, `vim`, `nano`,
real systemd, real journal, real process, socket or HTTP exchange is implemented.
The displayed port is a configuration constraint, not a real listening socket.

**Virtual file editor** edits only `/etc/lab-web.conf`. Draft and Applied text are
shown separately. Tab/Shift+Tab leave the editor; Enter inserts a newline. Apply
atomically commits structurally valid bounded text. Semantically broken service
configuration is allowed so it can be diagnosed. Apply does not restart a service.
Terminal commands use applied files and warn about drafts. `mkdir` and service
actions change simulated applied state immediately; failed commands commit no
partial filesystem changes. File drafts survive tool/lab changes and reopening.

Config syntax is intentionally small: unique `DocumentRoot=...` and `Port=...`
assignments, blank lines and full-line `#` comments. It does not emulate Apache,
nginx or a distribution-specific daemon configuration language.

## Scenario and grade

Startup tries the configured service once and records failure because `/srv/site`
does not exist. Use status and journal to identify the failure; compare config
with directory contents and owner/group/other permissions.

Two example solutions:

1. `mkdir /srv/site`, then `systemctl start lab-web`.
2. Edit `DocumentRoot=/srv/www`, preserve `Port=8080`, Apply, then
   `systemctl restart lab-web`.

Other accessible directories within `/srv` also work. The rubric gives 30 points
for valid configuration/constraints, 30 for a directory the service user can read
and traverse, and 40 for an active service with the current applied configuration.
An empty directory is sufficient; no index file or HTTP response is required.
An active service retains loaded configuration when the file changes. `start`
on an active service does not reload it; `restart` must load the new configuration.
A failed restart leaves the service failed. Grading uses state, not command order.

The learner and service user (`www-data`) have distinct permissions. Existing
ownership and rwx bits are fixed; new directories are learner:learner 0755.
Only the declared config is writable in the editor. Parent traversal and
directory creation permissions are enforced. Service control is an explicit
simulation permission, not implicit root access. ACLs, supplemental groups,
symlinks, devices, setuid bits and full systemd behavior are outside this model.

Learn provides three diagnostic-reasoning hints without a score penalty;
Challenge hides them. Shared portable contracts allow 0–32 hints. Reset or mode
change archives the entire previous attempt and sidecar, then restores initial
virtual files, cwd, service/logs, drafts, commands and hints. History is not pruned.
Repeated submission at the same revision is idempotent.

## Trusted engine, packs and persistence

`linux_service/engine.py` and `vfs.py` use copied Python dictionaries. They import
no host execution, filesystem or network APIs. The terminal tokenizes a narrow
character allowlist and dispatches explicit actions; it never forwards text to
a shell, evaluator, dynamic import or host path resolver. Application persistence
separately saves that state into its app-owned profile, under the existing writer
lock. The networking engine, firewall engine and original three pack bytes are
unchanged. Shared layout, theme, hints, review, transfer and history are reused.

The complete example is a data-only `learning-lab.scenario` schema 1 envelope:

| Version or content | Value / contract |
| --- | --- |
| Identity | `linux-web-document-root`, content `1.0.0` |
| Engine | `linux-service`, contract 1, behavior `linux-service-1` |
| Required capabilities | `virtual-filesystem`, `virtual-file-editor`, `service-lifecycle`, `service-journal` |
| Domain schema | 1; `filesystem`, `cwd`, `editable_files`, `service` |
| Filesystem nodes | Canonical absolute virtual path → kind, owner, group, mode, content |
| Service | Name, config path, required port, permitted document-root base |
| Rubric | `configuration_valid`, `document_root_accessible`, `service_running_current_config`; empty params, positive weights totaling 100 |
| Identity digest | Existing `oll-json-v1` over the entire envelope; no exclusions |
| New attempt envelope | Schema 4, exact content and engine pin, domain-validated applied/draft state |

The initial runtime is derived from pack data by the pinned engine's startup
behavior. No scenario ID, service name, config path, document root or port is
hardcoded in application behavior. The UI component and predicate implementations
are trusted shipped code; packs cannot register code or name components.

Limits: 64 initial virtual nodes, 128 runtime nodes, 8 KiB UTF-8 per file,
64 KiB aggregate file text, 16 objectives, 512 command characters, 16 KiB terminal
result text, 100 recent service events, 100 recalled commands and 500 console
lines. Existing 256 KiB pack / 10 MiB attempt limits also apply. Invalid topology
of the virtual tree, unknown fields/identities, links, permissions, versions,
capabilities or predicates fail before installation. Unsatisfiable arbitrary
service packs are not exhaustively searched; this supplied scenario is tested.

Networking portable records remain schema 3; legacy schemas/paths and bytes stay
unchanged. Schema 4 is new, not a migration. Newer records or mismatched pins stay
read-only; corrupt records use existing backup recovery with originals retained.
Updates create separate content/version entries and do not alter resumed attempts.
Scenario export retains original pack bytes and no personal state; History export
is separate and may contain drafts, commands, logs and assessments. Personal
history import is still deferred.

## Validation and acceptance

See the delivery results added below. All mutating checks use temporary profiles.
The historical `proof-code-freeze.json` remains unchanged: it records the earlier
networking data-only authoring proof. The regression now compares the networking
core and original packs to that manifest, rather than forbidding every future
application change. The old frozen-code native proof script is historical and
is not a current-feature acceptance gate.

Reproduce automated checks:

```bash
python3 -B -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software python3 -B tests/linux_service_acceptance.py --label linux-offscreen-100 --offscreen --expected-dpr 1
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1.5 python3 -B tests/linux_service_acceptance.py --label linux-offscreen-150 --offscreen --expected-dpr 1.5
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software QT_SCALE_FACTOR=2 python3 -B tests/linux_service_acceptance.py --label linux-offscreen-200 --offscreen --expected-dpr 2
```

Offscreen environment overrides apply only to the test process. No desktop
settings are changed. Offscreen screenshots are not native-session evidence.
For a native run, omit `--offscreen`, use the normal Wayland environment and
set `--expected-dpr` to the actual display scale. QtTest inputs still do not prove
physical keyboard delivery. Native picker interaction is manual.

### Hands-on acceptance — outstanding

- [ ] Import via the native file chooser; cancel/reopen and reject an invalid pack.
- [ ] Complete both repair paths with physical keys. Check Tab/Shift+Tab out of
  the editor, multiline editing, console Enter/Up/Down, Alt+1/2/3, F6/Shift+F6.
- [ ] Inspect native rendering at 800×600, 1024×768, 1180×860 and 1280×900 logical
  pixels and 100/150/200% display scale; verify scroll access to Mission, Applied
  text, terminal and help, plus fallback theme and mixed-monitor movement.
- [ ] Cancel/confirm draft submission, reset, mode and lab-switch dialogs; verify
  visible focus returns and drafts/hints remain in the appropriate attempt.
- [ ] Close normally and reopen the same temporary profile with unfinished text
  and command input. Check all four labs, current state and prior history.
- [ ] Export scenario and personal attempt through their separate native dialogs;
  test cancel/overwrite in disposable files and reimport the scenario.
- [ ] Review accessibility/reading order and screen-reader behavior if used.

These items stay outstanding until owner evidence exists. Earlier native evidence
for networking is historical and does not validate this changed application.

## Delivery results

- Baseline verified: `66fd1fb8dacfada03e0a211c1c7615d5dcdd93fd`, initially clean.
  Git metadata remained untouched. All delivered changes are uncommitted.
- Fresh [regression log](../evidence/linux-service-tests.txt): **118 tests pass**,
  including 16 Linux tests. Isolated fixtures cover two repair paths, wrong fixes,
  stale loaded configuration, permissions/traversal, hostile syntax, virtual
  limits, malformed packs/records, pinned schema handling, corruption recovery,
  no host APIs, hints/modes, duplicate grades, reset/history, restart and exports.
- Linux offscreen UI: [100%](../evidence/linux-offscreen-100.json),
  [150%](../evidence/linux-offscreen-150.json), [200%](../evidence/linux-offscreen-200.json).
  **71 checks per run**, four supported logical sizes, synthesized key input,
  both fixes, long-text cursor visibility, rejected oversize edits, separate
  Applied text, dialogs, theme fallback, four-lab switching and fresh-process resume.
  No QML runtime errors were recorded.
- Original networking UI: [100%](../evidence/linux-network-regression-offscreen.json),
  [150%](../evidence/linux-network-regression-offscreen-150.json),
  [200%](../evidence/linux-network-regression-offscreen-200.json): **190 checks each**.
  Existing Qt warning about disabling `activeFocusOnTab` on an active field remains;
  these flows pass, but physical keyboard acceptance remains open.
- Screenshots (**offscreen only**): [initial lab](../evidence/linux-offscreen-100-initial.png),
  [800×600 Applied editor](../evidence/linux-offscreen-100-editor-800.png),
  [150% editor](../evidence/linux-offscreen-150-editor-1280.png),
  [200% Challenge review](../evidence/linux-offscreen-200-challenge-review.png).
  Small panes intentionally scroll; geometry tests separately focus draft/applied
  text, ensure cursor visibility and reserve a readable terminal output line.
- Native Wayland blocked by this environment: socket connect returns errno 1,
  `Operation not permitted`. No current native visual, physical-keyboard or
  native-picker success is claimed.
- Runtime: Omarchy `4.0.4-1`, Python `3.14.7-1`, PySide6/Shiboken6 `6.11.2-1`,
  Qt base `6.11.2-3`, Qt declarative `6.11.2-1`. No dependencies installed.
- Recovery: all **eight snapshots verified**, including
  `/home/drak/.local/state/omarchy-learning-lab/recovery/linux-service-before-20261003T002027918603Z`.
  [Verification](../evidence/linux-recovery-verification.json) compares the copied
  contents to manifests and confirms real personal progress/configuration are
  unchanged, including bytes, modes and modification times. Backups remain outside
  source; none overwritten. Networking engine and original packs remain unchanged.

Generated evidence is ignored by the existing `.gitignore`; it remains local for
review. No staging, commit, push, packaging, deployment or real data migration.

### Changed files

New simulation and data:

- `learning_lab/linux_service/{__init__,engine,vfs,adapter}.py`
- `learning_lab/domains.py`, `learning_lab/domain_attempts.py`
- `examples/linux-web-document-root.lab.json`
- `learning_lab/qml/LinuxServiceWorkspace.qml`

Integration and preserved-layout adaptation:

- `learning_lab/{bridge,catalog,networking,pinned_storage,portable,session}.py`
- `learning_lab/qml/{Main,DiagnosticsDock,MissionPanel}.qml`

Tests and documentation:

- `tests/{test_linux_service,linux_service_acceptance,linux_service_restart_probe}.py`
- `tests/{test_networking_adapter,test_pack_proof}.py` (expanded registry and
  historical-freeze scope, respectively)
- `README.md`, `docs/{framework,framework-acceptance,pack-format,linux-service}.md`

Remaining model limitations: one virtual service, one editable config file,
owner/group/other rwx without ACLs or links, bounded recent console/journal,
no HTTP content check, no real systemd or Linux shell. The framework now has two
tested domains; this does not establish arbitrary-domain extensibility.
