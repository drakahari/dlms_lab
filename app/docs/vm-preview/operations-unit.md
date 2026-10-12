# Accounts, Scheduling, Logging & Recovery

A connected extension to the existing users, scheduling, logging and backup units.
Use only a disposable guest of the existing approved administrator image. Nothing
here changes passwords, PAM, login policy or the learner's sudo entitlement.
Prerequisites: quoted paths, shell statuses, permissions, basic cron/timers,
journal queries and separate-destination recovery. Earlier units remain useful;
this unit adds evidence distinctions rather than repeating account creation.

## Eight lessons

| Lesson | Actual practice and evidence | Coverage and boundary |
|---|---|---|
| Check account evidence without changing login policy | Read existing ll-service identity/aging; validate fabricated alternate group/gshadow pairs, reject duplicates, repair a separate copy and preserve sources | Partial LPIC-1 107.1 database consistency; no credential or login-policy modification, no claim consistency grants access |
| Separate cron access policy from table ownership | Read current policy; distinguish ordinary-user -u denial; own one initially absent learner table; capture actual UID/output/exit; refuse a changed table and remove only exact retained bytes | Partial 107.2 access, execution reinforcement; no at or allow/deny edit |
| Separate timer activation from job success | Observe loaded limits and exit7; exercise a real oneshot timeout; preserve failure, retry a private job, verify UID/result/bytes and stop exact units | 107.2 timer-result reinforcement; root may override guest limits |
| Continue a journal investigation from an exact cursor | Retain the journal-compatible 32-hex boot ID/cursor; isolate a later event; reject malformed cursor; read disk use and boots | Partial108.2 cursor/persistence evidence; retention is not guaranteed and Resume restores no RAM |
| Match journal fields without conflating their logic | Generate four tiny real events from two existing UIDs; compare AND, same-field OR, + disjunction, severity threshold and exact priority | Partial108.2 field/severity semantics; tag text is not authenticated business content |
| Follow the open descriptor through a private log rotation | One explicit private config/state; retain inode through rename, demonstrate old writer and close/reopen | Partial108.2 rotation mechanics; no global rsyslog configuration or arbitrary daemon signals |
| Send a bounded local notice and retain its limits | Small wall notice actually visible on the guest console; capture sender status and TTY/time | 101.3 wall-tool preparation; no timed advance-notification, recipient understanding, remote delivery or mesg claim |
| Recover the right note and prove intended-user access | Two valid compressed candidates; independent expected payload, actual learner read refusal, repair only restored copy and verify originals |104.5/LPIC-2 206.2 reinforcement and independent transfer; no new complete-objective credit |

Learn supplies commands and expected observations. Challenge states independent
outcomes and initial fixture facts, without the repair walkthrough. Both modes
record **self-reviewed, unscored** completion. Retain factual files and explain
why a tick, status0, successful listing or privileged read can be misleading.
Reasoning is not automatically assessed by Learning Lab.

## Safety and recovery

Record the unique private guest workspace. Stop on failed guards or collisions;
never substitute a live path, global unit, unrelated table or authentication file.
The common cleanup enumerates exact members, verifies regular files/directories
and rejects symlinks, extra members and partial fixtures before deletion. It does
not pretend partial/interrupted exercises are complete: retain them on refusal.

Cron cleanup refuses while a table exists. First run the displayed exact-table
removal guard, which refuses a changed table and never removes an unrelated one.
Timer cleanup accepts a successful exact LoadState=not-found query, or loaded inactive/failed units with zero MainPID/ControlPID. A transient timer may already be collected; generic query failures never count as absence. Loaded service Stop still verifies User and exact argv.
Close only the declared writer FD9 before private log cleanup. These cooperative
single-user guards are not race-resistant isolation from guest root.

Setup checks do not reserve filenames. Repeat the displayed destination checks
immediately before journal output, timer launch/retry, rotation or restoration.
Refuse existing/dangling output paths before first creation; validate a reused
private regular single-link file before rewriting it. The notice send also
checks its size, one-line form and status destination before sending. Stop on
refusal and retain the workspace; never remove an unexpected path to make a
command pass.

Each task has small fixed output; subprocesses have explicit short bounds where
work can wait or persist. Cron waits at most 80 s, child 6 s; timer jobs are bounded by
loaded TimeoutStartSec=4s and a six-second outer timeout; private logrotate 5 s and
wall 5 s. File checks and read-only queries are not claimed to have a universal
output quota. The workspace free-space check is an observation, not a reservation.

No new packages: xz, at and mesg are absent and deferred. No image, controller,
network, host share, backup-format or privilege change. VM disks remain excluded
from profile backups. Disk Resume boots existing storage and does not restore
jobs, RAM, descriptors, shell variables or terminal history in memory.

The kernel prints a hyphenated boot UUID; `journalctl -b` on this guest requires
the 32-character hexadecimal form. The lesson removes only hyphens with `tr`.
Retain the workspace path to reconstruct its unique tag after reopening.

## Objective sources

Verified 2026-10-11: [LPIC-1 active v5.0,101-500/102-500](https://www.lpi.org/our-certifications/exam-101-102-objectives/)
and [LPIC-2 active v4.5.0,201-450/202-450](https://www.lpi.org/our-certifications/exam-201-202-objectives/).
LPIC-2 draft5 is distinct. These are limited practice and reinforcement, not full
objective coverage, exam readiness or LPI endorsement. Original fictional exercises.

Tool references matched to the Debian guest: [journalctl](https://manpages.debian.org/trixie/systemd/journalctl.1.en.html), [logrotate](https://manpages.debian.org/trixie/logrotate/logrotate.8.en.html), [crontab](https://manpages.debian.org/trixie/cron/crontab.1.en.html). The retained ordinary-user wall probe warned about -n but still delivered with a banner; suppressing that banner uses the already-approved guest sudo entitlement. This is not a new host privilege or a claim that ordinary wall delivery is denied.
