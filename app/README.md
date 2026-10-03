# Omarchy Learning Lab — native workspace and portable scenarios

Three networking labs and a six-lab Linux Fundamentals collection in a standalone, offline Qt Quick window.

## Launch

For an isolated user-local venv and application-menu entry, see the reviewed
[installation, update, rollback and uninstall workflow](docs/user-installation.md).
The owner-run command is:

```bash
python3 -B /home/drak/Documents/dlms_lab/app/tools/user_install.py install
```

It prepares and tests a new wheel installation before activating it. Personal
progress/configuration keep their established locations. Development verification
used temporary destinations. The owner subsequently reports successful installation
and Omarchy menu launch, with the Learning Lab entry and icon visible.

From the existing Omarchy graphical session:

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -m learning_lab
```

Installed and verified: Python 3.14.7, PySide6 6.11.2, Shiboken6 6.11.2, Qt 6.11.2. The approved official `extra/pyside6` and `extra/shiboken6` packages were installed at distribution revision `6.11.2-1`. No Python environment, server, shell plugin, desktop entry, or package build is required.

Minimum supported window: **800 × 600 logical pixels**. Hyprland tiling can force a smaller allocation despite Qt's minimum. Use the existing **Super+T** floating toggle or **Super+Alt+F** maximize binding when needed; the app does not install window rules.

## Use

### Create your own lab

**Library → Create a lab…** offers a permissions starter, a complete worked
example, a plain-language quick guide and an optional copyable AI prompt. Save
and edit JSON in your text editor; **Validate lab…** checks it without installing.
Read the summary, then explicitly import. Packs supply data to supported engines;
they cannot add commands or run scripts. See the [disposable beginner walkthrough](docs/in-app-authoring.md).

### Hide or remove Library entries

Use a card's **Actions ▾** menu to hide a built-in or reversibly remove an imported
version. **Show hidden / removed** provides **Restore and resume**, history and
**Restore to Library** actions;
**Restore visibility** shows all hidden built-ins. Nothing is deleted. Removed
and hidden entries retain their attempts but require restoration before any practice.
Restore to Library does not launch; Restore and resume confirms the exact saved attempt.
Choices are profile-local and included in version-2 profile backups; old backups
remain readable. See [identity rules and a disposable owner test](docs/library-cleanup.md).

### Profile backup and restore

Library includes **Backup profile…** and **Restore profile…**, separate from
scenario/history exports. Backup briefly pauses app actions, saves pending work,
and creates a validated personal `.llbackup` file. Restore previews and requires
confirmation before creating a **new** profile folder; the open profile stays
unchanged. See [included files, compatibility, safety and disposable test](docs/profile-backup.md).
These source changes do not update the working installed application.

### Linux Fundamentals

The Library offers six short labs in a suggested order, from file navigation to
recovering a web service. Choose **Start** or **Continue** on any card; there are
no completion prerequisites and no file-picker import is required. Cards show a
short skill description and separate Learn/Challenge progress when records are
reliable. Existing exact imports resume their pinned attempts without duplicates.
Custom imports and networking labs remain below the collection.

Packs are installed from validated application resources on first Start. Merely
viewing the Library does not create Linux attempts. Same-ID/version conflicts are
reported and preserved, not replaced. See [collection behavior and verification](docs/linux-fundamentals.md).

### Author permissions scenarios / directory permissions

Use the [authoring guide](docs/permissions-authoring.md) and valid
[`templates/linux-permissions.lab.json`](templates/linux-permissions.lab.json).
Validate a copy with `python3 -B tools/validate_scenario.py path/to/pack.json`, then
import it from Library in an isolated review profile.

Open **Why can’t I enter this directory?** in Linux Fundamentals. Its standalone
pack is `examples/linux-directory-permissions.lab.json`. It teaches name listing versus traversal, restoring only owner
execute permission while preserving private read access. This uses an explicit
contract-3 extension of the existing permissions engine; older packs retain their
original behavior. See [scope and acceptance](docs/directory-permissions.md).

### Beginner Linux file permissions

Open **Restore access to your file** in Linux Fundamentals
(`examples/linux-file-permissions.lab.json`). Inspect your unreadable notes, restore private owner
read/write access, and read the contents to verify the repair. Learn explains
permission classes and each step; Challenge hides the walkthrough.

This pack explicitly enables simulated `chmod u+r PATH` and `chmod NNN PATH`
(exactly three octal digits). Only its declared learner-owned notes file is
mutable. `777` permits reading but fails the private-access requirement. Existing
navigation and service packs continue to reject `chmod`.
See [permissions syntax, results and owner checklist](docs/linux-permissions.md).

### Beginner Linux file navigation

Open **Find your way around Linux** in Linux Fundamentals
(`examples/linux-file-navigation.lab.json`).
This five-minute exercise teaches `pwd`, `ls`, `cd` and `cat`. Learn shows one
explained step at a time; Challenge keeps the goal and grading rules in **Lab
details ▾** without a walkthrough. No service or file editor is involved.

Four objectives retain successful simulated activity; the last checks the current
directory when you submit. Equivalent paths and different command orders count.
See [navigation rules, architecture, test results and owner checklist](docs/linux-navigation.md).

### Linux service troubleshooting

For a first lesson, open **Start your first service** in Linux Fundamentals
(`examples/linux-service-basics.lab.json`). Its configuration is healthy: inspect the stopped
service, start it, then verify it is running. Learn explains one command and its
expected result at a time; Challenge hides that guidance.

Open **Recover a failed web service** in Linux Fundamentals
(`examples/linux-web-document-root.lab.json`).
The bounded **Terminal · Simulated Linux** console contains output, a current-directory
prompt and command entry. Type `help` and press Enter, or use Run. **Command reference**,
**Virtual file editor** and **Diagnostics** open a separate lower pane; Close returns
its space and focus to the terminal. Drag the divider, or focus it and use Up/Down. The selected height survives output updates, lab switching
and reopening; small windows temporarily clamp it and restore it when space allows.
Linux sizing preferences are separate from networking preferences. Nothing typed into the terminal runs on
the host. The original networking labs and their history remain separate.

Start with `help`, `systemctl status lab-web`, `journalctl -u lab-web`,
`cat /etc/lab-web.conf`, and `ls -l /srv`. Repair the missing virtual directory or
change the document root using the editor and **Apply changes**. Start/restart
loads applied configuration. Grade reflects the resulting state, including
permissions and declared constraints; no particular command sequence is required.

See [Linux commands, model, tests and outstanding acceptance](docs/linux-service.md).
The sidebar shows the goal, progress, current Learn step and Hint. **Lab details ▾**
opens a non-modal, independently scrolling reference in that area. It stays open
while typing and editing, and resizes beside the workspace or above it in compact
windows. The virtual editor has padded draft/applied groups; Applied is collapsible.
See [current reference/editor changes and owner checks](docs/linux-reference.md), and
[the original divider fix and beginner results](docs/linux-usability.md).

### Gateway and DNS

1. Open the gateway/DNS lab and inspect WS-01, RTR-01 and APP-01.
2. Compare `ping 10.20.0.10` with `nslookup portal.lab.test` in the simulated console.
3. In Settings, preserve `192.168.50.20/24`, change gateway to `192.168.50.1` and DNS to `10.20.0.10`, then **Apply**.
4. **Test** the applied state and **Submit** for the final-state rubric.

### Subnet boundary

1. Open **Correct a subnet boundary**, read the persistent **Mission** pane, and inspect PEER-01.
2. At the initial `/28`, `ping 192.168.50.21` works; `ping 192.168.50.1` and `ping 10.20.0.10` fail. `ip route` shows `192.168.50.16/28`.
3. Preserve `192.168.50.20`. Change the prefix to `/24` and Apply. Gateway and DNS are correct, fixed scenario settings.
4. Test peer, gateway and remote server, then Submit. Exact `/24` earns 30 points; preserving the address earns 20, peer reachability 20, gateway 10, remote server 20. A working `/16` earns only 70/100.

### Service firewall

1. Open **Repair a service firewall**. DNS and ping work initially; `connect portal.lab.test 443` is blocked by `block-portal`, and TCP 22 is blocked by the explicit deny default.
2. Open **Firewall**. Rules match source/destination IPv4 selectors, TCP and destination port; the first match wins. The default applies only when no rule matches.
3. Correct the existing rule to **allow**, with source `192.168.50.20/32`, destination `10.20.0.10/32` and port `443`. Or add a matching narrow allow and move it above the deny. **Apply** validates and commits the entire draft policy atomically.
4. **Test** or run `connect portal.lab.test 443` and `connect portal.lab.test 22`. Each connection names its matching rule or default policy. Use **Inspect Applied policy** to compare with drafts.
5. Submit for the final-state rubric: DNS/endpoint reachability 15, ping 15, TCP 443 access 40, TCP 22 denied by policy 10, narrow effective permission 20. Full credit requires that only the specified source/destination/port is allowed. Broad source, destination or port rules lose credit, even when a separate rule blocks SSH.

The isolation check evaluates the effective first-match policy over all IPv4 selectors and TCP ports, including selectors without a currently instantiated device. It accepts redundant or shadowed rules and any safe ordering that yields the required permission; it does not require a particular rule ID or command sequence.

The portal check still models **DNS resolution and reachability only**. The firewall lab adds explicit **simulated TCP** permission, declared listening services and return routing. Replies to an allowed connection are treated as established; there is no TCP stack, TLS negotiation or HTTP response. The engine performs no real network traffic or host command execution.

The three original labs retain three Learn hints without a score penalty; portable packs may provide 0–32 hints. Challenge hides hints. Reset and mode changes require confirmation and archive the complete prior attempt, including drafts, console and hint usage. Returning to Library or History preserves the current lab session. Switching labs saves and resumes each independent attempt; switching with drafts asks for confirmation and retains those drafts without applying them. The resizable, scrollable **Mission** pane keeps the complete instructions, objectives, constraints and hints alongside the work. History is paged; attempts are never automatically pruned.

Keyboard: F6/Shift+F6 moves between mission, workspace and diagnostics regions; Tab/Shift+Tab moves within them; Enter activates controls; Alt+1/2/3 opens Library/Lab/History. In Console, Enter runs a command and Up/Down browses history. Focus a scroll panel and use PageUp/PageDown or Up/Down. Escape cancels the reset/mode dialog; focus returns to its origin.

Supported **networking** console syntax:

```text
help
clear
ipconfig
ip addr
ip route
ping <IPv4-or-hostname>
nslookup <hostname>
traceroute <IPv4-or-hostname>
connect <IPv4-or-hostname> <port>
```

`connect` is available only in the firewall lab and accepts a numeric port from 1 through 65535. Commands are case sensitive; DNS names are case insensitive. No options or shell syntax are supported. Console commands originate at the pack’s designated workstation (WS-01 in the original labs). A valid but incorrect configuration may be applied so its effects can be diagnosed; the rubric enforces the assigned address and exact prefix.

## Data and recovery

Qt resolves the XDG data/config locations. Default paths:

- `~/.local/share/omarchy-learning-lab/current.json`: gateway/DNS current attempt (existing location retained).
- `~/.local/share/omarchy-learning-lab/current.backup.json`: last-known-good snapshot.
- `~/.local/share/omarchy-learning-lab/attempts/<UUID>.json`: retained prior attempts.
- `~/.local/share/omarchy-learning-lab/labs/subnet-boundary/`: subnet current/backup files and its own `attempts/` directory.
- `~/.local/share/omarchy-learning-lab/labs/service-firewall/`: firewall schema 2 current/backup files and retained attempts, including applied and draft rules.
- `~/.config/omarchy-learning-lab/selection.json`: last selected lab; unsupported files are preserved.
- `~/.config/omarchy-learning-lab/preferences.json`: built-in palette preference.

One writer is allowed. Saves use same-directory temporary files, fsync and atomic replacement. Current console output is limited to 500 lines and command recall to 100 entries. Attempt records are capped at 10 MiB individually; exceeding that limit reports a save failure, never silently trims attempts. Historical disk usage grows with use. No history deletion or automatic pruning is implemented.

See [recovery instructions](docs/recovery.md) for corruption and newer schemas. CLI `--data-dir` and `--config-dir` select isolated acceptance locations; bundled packs cannot supply paths.

The theme adapter reads only the installed `~/.local/state/omarchy/current/theme/colors.toml`. It accepts bounded TOML and hex colors, checks text contrast, and provides a built-in fallback. No hooks or shell imports are used.

## Tests and evidence

```bash
python3 -m unittest discover -s tests -v
```

See [current framework acceptance](docs/framework-acceptance.md), [unit results](evidence/framework-unit-tests.txt), and [portable format and architecture](docs/framework.md). Earlier native reports describe the previous UI; the framework scripts supersede those UI probes.

Native screenshots are QQuickWindow captures from real Wayland windows. Keyboard acceptance uses QtTest key events sent to those windows, without mouse events. Physical keyboard input through the compositor and assistive-technology behavior require the included manual checklist.

## Implementation map

- `learning_lab/domain/`: pure simulation, allowlisted commands, pack validation and objective grading. `firewall.py` implements bounded first-match policy and exact permission analysis.
- `session.py`: drafts, Apply, hints, submission idempotency and attempt transitions.
- `storage.py`: schema validation, atomic snapshots, backup recovery and retained archives.
- `bridge.py`: per-lab Qt presentation state and typed actions.
- `catalog.py`: bundled library selection and independent progress stores under one writer lock.
- `theme.py`: read-only Omarchy palette adapter.
- `qml/`: native library, topology, settings, console, feedback, history and dialogs.
- `packs/gateway-dns.json`, `packs/subnet-boundary.json`, `packs/service-firewall.json`: validated data-only scenarios.

All three specified labs are bundled. This is original learning content with no CompTIA affiliation. Packaging, integration and distribution remain deferred.

## Portable scenarios and workspace

Use **Import scenario…** in Library to install a local data-only JSON pack. The `examples/` folder contains portable versions of the three original labs and a DNS-misdirection proof scenario. Portable entries are labeled separately and start independent pinned attempts. They do not replace original labs or migrate their history. Use **Export scenario…** for content alone; **Export this attempt…** in History is a separate personal-data operation.

The workspace preserves pending settings, firewall edits and console input. Diagnostics report their applied revision; submission review is separate. Split handles and +/− buttons resize panes, with ↺ restoring defaults. Narrow windows use a topology tool tab.

See [architecture, format, limits, pinning and rollback](docs/framework.md).
The Linux service lab exercises a second trusted domain; this is a bounded
two-domain implementation, not evidence that arbitrary future domains need no
framework changes. Its current visual tests are offscreen, not native acceptance.

## Checkpoint 1: scenario identity (historical)

Gateway/DNS now passes through an in-memory identity and legacy compatibility
adapter. Pack JSON, the three labs' behavior, storage paths, and saved-record
formats are unchanged. See [digest rules and version meanings](docs/scenario-identity.md)
and [recovery snapshot, changed files, and checkpoint tests](docs/checkpoint-1.md).
Legacy records have not been assigned content or engine provenance they did not record.
