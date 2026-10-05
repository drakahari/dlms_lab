# LPIC-2 Foundations: Resource Diagnosis & Capacity Evidence

Library → **Real Linux VM preview…** → **Choose a real-Linux collection** →
**LPIC-2 Foundations: Resource Diagnosis & Capacity Evidence**. Select any of its
eight lessons; no unlocks. Use the existing unprivileged offline guest and type
only in its GTK console. Core simulations remain usable without QEMU/image.

Prerequisites: paths, text/report basics and Processes, Jobs & Priorities. Learn
provides progressive guidance. Challenge retains necessary setup, synthetic data
and safety rules, while hiding guided commands/hints. Completion is **self-reviewed
and unscored**; advancing guidance is not guest assessment.

| Lesson | Evidence and interpretation | Partial objective |
|---|---|---|
| Record a resource baseline | Timestamp, CPU count, load, available memory, filesystem bytes/inodes and snapshot limits. | 200.1 |
| Compare CPU before, during and after | Interval samples, actual supervisor/child identities and status; utilization versus lifetime averages/load. | 200.1 |
| Interpret available memory and cache | Live counters and a labeled synthetic example; low free memory alone does not establish pressure. | 200.1 |
| Observe bounded file I/O | Reserve, exact payload bytes, timings/errors; cache/virtualization prevent a hardware benchmark claim. | 200.1 |
| Separate space from inode capacity | Live counters and hypothetical shortages; no exhaustion is manufactured. | 200.1 |
| Read a synthetic growth trend | Exact weekly table, rounded text chart and interval growth. | 200.2 |
| Forecast with assumptions and uncertainty | Reserve-aware arithmetic and an irregular case with insufficient evidence. | 200.2 |
| Write an evidence-based recommendation | Edited report separating observed, calculated, assumed and unknown statements. | 200.1/200.2 |

## Bounds and cleanup

Each lesson creates a unique private guest-home workspace with `mktemp -d` and
prints its path. Stop if setup/cd fails. Repeat creates a new workspace, preserving
previous evidence. Never assume variables survive logout/Resume. Cleanup targets
only exact known files in the recorded workspace; no recursive removal.

- **One CPU worker**: `timeout -k 2s 12s`, TERM at 12 seconds/KILL grace 2 seconds.
  Guard refuses another worker while this shell has any job. Track `$!`, actual
  child PID and `/proc/PID/stat` start tick. Cleanup signals only a matching
  current-shell job; no fixed/stale PID or broad process termination. If interrupted
  before identity capture, let the timer finish and reap it. Repeat cleanup safely.
- `vmstat 1 3/4` has an eight-second timer/two-second grace. Its first row normally
  averages since boot; later rows describe intervals. No fixed live threshold.
- **One 16 MiB regular scratch file**, 15-second timer/two-second grace per I/O
  operation. Child-only Bash `ulimit -f 16384` limits each file to 16 MiB using
  this pinned shell's default 1024-byte units. Check **540672 KiB / 528 MiB**
  available first, preserving a **512 MiB** reserve after the payload. Notes are
  under 8 KiB per lesson. Admission is not a permanent reservation/aggregate quota.
- Ctrl-C interrupts foreground I/O. After the prompt returns, remove only `io.bin`
  while PWD equals the recorded workspace; repeated cleanup is safe. Keep notes.
- Timers are practical supervision limits, not hard wall-clock guarantees for a
  suspended VM or uninterruptible kernel wait. Errors/partial files invalidate
  speed claims. A rounded zero duration cannot be a throughput denominator.

No disk/inode exhaustion, OOM pressure, cache dropping, direct-device writes,
privileges, network, packages, host shares or clipboard. Guest scheduling, page
cache and host virtual storage limit conclusions about physical performance and
durability. `conv=fsync` requests synchronization; it does not prove physical-media
behavior. Inconclusive observations are valid.

## Small datasets and independent arithmetic

**Practice setup and supplied data** includes exact guest-local `printf` commands
in both modes. Historical examples are explicitly synthetic, not VM measurements:

```text
day used_MiB
0 200
7 270
14 340
21 410
```

Every seven-day interval grows 70 MiB: **10 MiB/day**. One `#` per full 50 MiB
produces 4, 5, 6 and 8 symbols; retain exact values because the chart rounds down.
Policy is hypothetical capacity **1000 MiB**, reserve **100 MiB**, last sample
**day 21**, independent of actual VM disk capacity. Threshold is 900 MiB;
headroom is 900−410=**490 MiB**; 490/10=**49 days after the last sample**;
21+49=**day 70**. Without reserve, day 80. Choose an earlier review checkpoint
with a reason; this forecast is conditional, not a guaranteed failure date.

An irregular table has 200,190,300,210 MiB on the same days, changes −10,+110,−90.
A positive endpoint average exists, but reversals do not justify steady-growth
forecasting. Request longer history, workload/retention context. Zero/negative
growth cannot establish finite linear exhaustion either.

The final skeleton is not a completed answer. Use the existing guest nano to add
actual dated values, label synthetic planning, explain assumptions and uncertainty,
and propose scoped next evidence. No app command execution or report assessment.

## Registry, compatibility and coverage

Trusted application-owned `units.json` schema 1 names bundled simple JSON filenames
only. No external index or VM lesson import. Bounds: **4 units, 16 lessons per unit,
16 total lessons, 64 KiB/resource, 32 steps/lesson, 4096 characters/text and 16 items
per support list**. Former global 16-lesson limit is retained and now filled by two
units of eight. Future increases require explicit review. Duplicate unit IDs,
resources and cross-unit lesson IDs fail closed. New support fields are display-only
materials, observations, questions and limitations; no executable actions.

The original eight lessons, order, resource bytes, IDs, canonical pins and accepted
background-job binding are unchanged. `catalog()` still defaults to that unit;
global lookup/running-control discovery covers both. Unit choice derives from the
existing persisted lesson ID: no storage/selection/backup migration. Return/Stop
remains available across units, and a second VM remains excluded across profiles.
Only new lesson compatibility pairs/defaults are added to the retained image
catalog; original pairs, image descriptor/hash, controller and launch policy are
unchanged. Production keys/releases remain empty.

VM records/disks/reports remain excluded from profile backup/exports. Resume boots
files, not RAM/jobs. Reset retains generations. Console fit behavior is unchanged.

Verified objectives **2026-10-04**: LPIC-2 **4.5** (201-450/202-450), partial **200.1**
measurement/interpretation and **200.2** trends/forecasting.
[Official objectives](https://www.lpi.org/our-certifications/exam-201-202-objectives/).
CPU work reinforces LPIC-1 v5.0 103.5. No network measurements, sar/iostat/iotop,
privileged attribution, hardware benchmarks, monitoring-platform configuration or
full LPIC-2 coverage/affiliation is claimed.

Roadmap continues toward genuine accounts/scheduling, services/logs and recoverable
storage. Guest privileges, packages/disks and networking require separate approval.
Public release remains deferred for broader curriculum and licensing/image-release
gates. UI polish and shorter explanations are later work.
