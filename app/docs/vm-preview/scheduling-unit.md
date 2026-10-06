# Scheduling & Operational Automation: Cron and systemd Timers

Eight connected real-Linux exercises using the unchanged offline administrator
image. Instructions are display-only; the app does not execute lesson JSON.
Completion is **self-reviewed and unscored**. Prerequisites: earlier Bash,
users/groups, ownership and service-unit lessons. Sequence guides, not locks.
Use Learn for explanations and Challenge for independent goals and fault setup.

## Sequence and evidence

| Lesson | Skill | Evidence beyond a timer trigger |
|---|---|---|
| 1. Inspect schedulers, clocks and execution identities | Cron/system/user scopes; clock versus monotonic time | Actual tools, timezone, loaded service metadata, disposable identity |
| 2. Prepare a bounded, repeatable report job | Environment, narrow access, overwrite | Two private reports; root invocation refused without damage |
| 3. Schedule a disposable user cron job | User-crontab grammar, execution/removal | Exact entry, minute-boundary output owner, entry removed |
| 4. Diagnose cron environment and access faults | Lookup versus executable access | Actual cron error, minimal-environment failure, narrow repair and cron success |
| 5. Run a monotonic user timer | Activation delay, loaded limits, timeout | Identity/result, configured loaded limits, actual timeout/no child |
| 6. Configure a calendar system timer | Explicit unprivileged service user | Loaded bounds, trigger, exit status, private output contents/owner |
| 7. Investigate missed calendar runs and overlap | Catch-up and associated-service activity | Stopped count, single catch-up, same live PID/count and ordered events |
| 8. Repair automation and hand over evidence | Identity/access repair and cleanup | Failed results, repaired timer/cron evidence, precise handover/cleanup |

No fixed PID or performance threshold is assumed. Inconclusive evidence is
valid to retain and investigate, not a reason to invent successful completion.

## Safety and limits

Use only ll-s1 through ll-s8, their dedicated homes and exact named units.
Lesson 5 uses /home/learner/ll-s5 and named transient user units. It changes no
learner account, groups, sudo policy or linger. All disposable accounts stay
locked, with no credentials or sudo entitlement. Guest learner's existing
passwordless root policy is unchanged. Never execute these commands on the host.

Guard every account/path/unit/crontab before setup. Stop on collisions.
Piping to crontab replaces that user's entire crontab: use only the freshly
created disposable account. Removing scheduling does not kill running work.
The Debian cron spool is root:crontab mode 1730: learner cannot traverse it.
The provided guest sudo absence check is essential; an unprivileged ! -e
can report absence simply because access was denied. Stop on a failed guard.
On interruption stop only the named timer, inspect its exact service/process,
wait for bounded work and perform the provided exact cleanup. Never broadly
delete files or terminate processes. Enter short printf lines manually or use
the installed vi; no clipboard sharing is assumed.

Reports overwrite one/two lines under 256 bytes. The overlap worker permits
only 1/6-second sleeps, four runs and eight short event lines under 512 bytes.
Cron jobs have a 5-second timeout and 1-second kill grace. System services use
Type=exec, RuntimeMax 6/8 seconds, MemoryMax 64 MiB and TasksMax 16, with independent
timeouts. The deliberate timeout proof uses RuntimeMax 2 seconds plus a separate
10-second timeout/1-second grace. **Guest root can override guest-side limits.**
These are not host quota or aggregate guest-storage guarantees.

Inspect properties while LoadState=loaded; collected transient units can show
defaults that do not prove enforcement. RuntimeMaxSec does not limit
Type=oneshot. The single-fire user exercise retains result state deliberately;
RemainAfterExit is not presented as a recurring-service pattern. The user
commands explicitly set Type=exec; systemd-run defaults to Type=simple.

Resume boots disk state, not RAM/jobs. Reset retains the previous generation.
VM disks/reports remain excluded from profile backups. Retain evidence first.

## Accurate scheduler semantics

A user crontab has five fields then a command, without a username; system
crontabs add a username. MAILTO is empty; no mail-delivery claim. Unescaped
percent in a cron command has special stdin semantics: keep formats in the
script. At, cron allow/deny administration and DST edge cases are outside scope.

OnActiveSec is monotonic; OnCalendar uses guest wall-clock time.
AccuracySec=1us avoids the default one-minute coalescing window for short proofs,
but guarantees no exact virtualized timing. No guest or host clock changes.

Persistent=true applies to calendar timers. It catches up once after missed
occurrences, not one execution per historical occurrence. An already-active
associated service is left alone; cron and independent units are not universally
serialized. RemainAfterExit=yes can prevent repeated activation until stopped.
Remove only the named persistent timer state while inactive.

## Objective mapping

Official objectives verified 2026-10-05:

- [LPIC-1 v5.0, exams 101-500/102-500](https://www.lpi.org/our-certifications/exam-101-102-objectives/):
  107.2 partial cron/systemd scheduling. At is absent; access-policy administration
  and full coverage are not claimed. Bash 105.2/journal 108.2 are reinforcement.
- [LPIC-2 v4.5, exams 201-450/202-450](https://www.lpi.org/our-certifications/exam-201-202-objectives/):
  202.1 startup/service reinforcement only; no full boot/targets/SysV coverage.

108.2 is logging context here (stderr routing), not new journal/rsyslog
administration or log-rotation coverage.

Guest versions: systemd 257.13-1~deb13u1, cron 3.0pl1-197.
Primary behavior references:
[Debian crontab(5)](https://manpages.debian.org/trixie/cron/crontab.5.en.html),
[systemd.timer(5)](https://manpages.debian.org/trixie/systemd/systemd.timer.5.en.html),
[systemd.service(5)](https://manpages.debian.org/trixie/systemd/systemd.service.5.en.html),
[systemd-run(1)](https://manpages.debian.org/trixie/systemd/systemd-run.1.en.html).

## Registry and launch

Bundled-only registry: six units, sixteen lessons/unit, fifty-two total.
Resource limits remain 64 KiB, 4096 characters/text, 32 steps. No external registry,
actions or imported VM lessons. All eight route exactly to the unchanged
debian13-admin-local-v1 image; unavailable content fails without substitution.
Original 44 lesson bytes/pins, controller and session/disk/backup formats remain
unchanged. Production trust remains empty.

Follow [setup.md](setup.md) using a disposable profile and the approved image.
Library → Real Linux VM preview… → select this unit in the collection selector
→ lesson → Learn/Challenge → Start. Practice in the native
guest console, then Stop. No packages, networking or clock changes.

## Next proposal — Backup & Safe File Recovery

A coherent eight-lesson follow-up: recovery requirements/tree inventory; scoped
archive creation/listing; bounded compression and integrity; staged extraction
and path review; compare restored contents/metadata; restore disposable-user
ownership/access; recover a deliberately damaged small fixture; evidence-based
recovery/cleanup assessment. Prerequisites are the completed Bash, access and
service units. Proposed new partial LPIC-1 103.3 archive practice, earlier file-management
reinforcement, and LPIC-2 206.2 partial
backup practice, not full coverage of rsync, tape, remote backups or disaster
recovery.

Actual disposable-guest probes verified GNU tar 1.35, gzip 1.13 and coreutils 9.7
creation/listing, separate-destination restoration of contents/mode/owner/mtime,
truncated-stream rejection and known-SHA-256 corruption detection. Tar listing
and gzip testing can pass after payload corruption and recompression: neither
authenticates content. Cpio is present but untested; rsync/getfacl/setfacl were
not found. Future ownership restoration for another disposable user still needs
its own actual access tests. Prefer these verified existing tools.
No host backups, shared folders or networking. Any missing package,
image change or capability needs separate approval. Keep fixtures small and
learner-owned; guest administrator only for the narrowly named ownership repair.
The registry is full: a seventh unit/sixty total requires a separately approved
bounded expansion, retaining sixteen per unit. This is a proposal only.
Public release/UI polish stay deferred; Qt/ICU obligations remain unresolved.

The overlap exercise's MainPID is the service's timeout wrapper; BEGIN records
its Bash child. They need not be equal. Compare MainPID with its own earlier
value, and inspect ordered events/counts rather than assuming a fixed PID.

Locked password entries do not mean cron cannot execute a job: cron applies its
account policy without authenticating with that user's password. These fixtures
remain unexpired. Root's runuser probes establish execution identity/access,
not successful password login or proof about every PAM restriction.

A service's Result can reflect a prior/default result while it is still running.
Inspect ActiveState/SubState and wait for this finite job to finish before
treating ExecMainStatus=0 as its final exit status. A trigger, an output file
appearing, or an active timer alone is insufficient.
