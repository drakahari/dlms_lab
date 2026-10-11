# LPIC-2 Resource Evidence — Offline Snapshots (Simulator)

Four short **simulator** activities in Library. Start anywhere; suggested order is
baseline → memory/cache → space/inodes → trend handover. Preparation: Text,
Filters & Reports, including paths, `cat`, bounded filters and redirection.
No QEMU or VM image is needed. These original fictional-host snapshots are not
measurements of your computer or guest.

## What is checked

The score means **evidence/report objectives met**, not diagnostic mastery:

- Exact factual report records: values, units, ordering and missing-data markers.
- Required actions: display each complete source and final report using `cat`
  **after the last write**. Equivalent paths count; other reading tools do not
  satisfy the declared `cat` actions. Report construction may use any supported
  filters producing the same bytes, rather than a fixed command transcript.
- Source preservation is an enforced invariant, not proof of a preservation skill.

The source files and `HELP.txt` are read-only virtual data. Only the declared
report files are writable. `>` truncates before reading; errors do not undo it.
Every actual write clears earlier inspection evidence. The rubric assigns 50
points to reports, 20 to source readings, 20 to final readings and 10 to preserved
sources. For space/inodes these are split across the two tables/reports.

**Self-reviewed:** interpretation, calculations, uncertainty, forecasts and next
checks. The engine has no prose, semantic diagnosis or numeric-answer checker.
Do not add free-form reasoning to the exact factual reports; discuss or retain it
outside the graded report. Challenge hides guided commands and hints, but sources
and model interpretations remain available. Reading the model earns no reasoning
credit. Learn guides report construction and final verification one step at a time.

## Quick owner walkthrough

Open Library and expand **LPIC-2 Resource Evidence — Offline Snapshots (Simulator)**.
Choose Start/Continue, then Learn or Challenge using the existing mode control.
Changing mode starts a fresh attempt while preserving history. Nothing is locked.

| Activity | Factual report | Separate self-review |
| --- | --- | --- |
| Read a supplied resource baseline | `baseline.txt`: first five snapshot records, including host/time, interval and CPU/memory/I/O units; omit note | Why does one interval not demonstrate a persistent bottleneck? What context/measurements are missing? |
| Separate available memory from cache | `memory-report.txt`: eight final data records, including all seven meminfo fields and the swap interval | Why is low free memory insufficient? Why distinguish occupied swap from swap-in/out? |
| Compare space and inode evidence | `space-report.txt` and `inode-report.txt`: two data rows each, no headers | Which resource is constrained on each mount? What should be checked before cleanup? |
| Prepare a cautious trend handover | `handover.txt`: four dated records sorted chronologically, preserving the missing observation | What trend is observed, what uncertainty remains, and what evidence is needed before forecasting? |

1. Read the mission and use **Lab details** for requirements and boundaries.
2. Type `help` for the supported command subset; type `cat HELP.txt` for this lab's
   context, model interpretation and common mistakes. Neither accesses host files.
3. Follow Learn steps or construct reports independently in Challenge.
4. Finish every write, `cat` each source and final report, and Submit.
5. Compare your explanation with the model; a 100/100 report score does not check it.
6. Reset confirms and restores supplied data/removes reports, preserving history.
   Close/reopen the same disposable profile to resume its exact pinned attempt,
   mode, console and pending command. Scenario export exports content; history
   export exports personal evidence; profile backup is the separate restore workflow.

## Semantics and limits

The baseline is annotated procps `vmstat` evidence, not a raw transcript. It uses
one-second **second-report** CPU/I/O fields, rather than since-boot averages;
memory fields are instantaneous. Memory uses KiB, block I/O uses KiB/s, CPU fields
percent of CPU time. The sample is intentionally small and inconclusive.

Memory is a selected Linux `/proc/meminfo` subset: kernel `kB` here means KiB.
MemAvailable is an estimate, not MemFree plus all cache. Cached/slab categories
are not independent parts to add blindly. Swap occupancy does not prove current
thrashing; zero interval activity cannot rule out intermittent pressure.

Filesystem tables are synthetic `df -P -k` / `df -P -i` subsets with simplified
allocation/reservation. Block-space units are 1024 bytes; inode fields are counts.
They are not accessible devices. Matching mounts, not just row order, matters.
No exhaustion, cleanup, mounting or repair is implemented.

Historical rows use fixed-width ISO dates in UTC; bytewise sorting is chronological
for this representation. A missing sample is not zero. The model's endpoint
average (96 GiB over three days = 32 GiB/day) is supplied reasoning, not automatically
assessed forecasting, and is insufficient for a reliable capacity deadline.

Existing text contract 5 / behavior `linux-text-streams-1` is unchanged. See
[text command grammar and limits](text-stream-contract.md). No arbitrary editor,
regex, calculator, live `free`/`df`/`vmstat`, host execution or new engine exists.
The fifth simulator collection fits the existing eight-collection/32-item bounds;
VM capacity remains nine units/76 lessons.

## Coverage and real practice

Official objectives verified **2026-10-10**: LPIC-2 **4.5.0**, exams 201-450/202-450.
Baseline, memory and space/inodes offer **limited interpretation reinforcement**
for 200.1. Trend handover offers limited reinforcement for 200.2. They do not
satisfy live measurement, monitoring, throughput troubleshooting or forecasting
requirements, or full exam preparation. Original content; no LPI affiliation.
[Official LPI objectives](https://www.lpi.org/our-certifications/exam-201-202-objectives/)

For actual observations, bounded workloads and capacity reasoning, use the
separate [real-VM resource unit](vm-preview/resource-unit.md). For actual mounts,
permissions and offline ext4 repair, use the [real-VM storage unit](vm-preview/storage-unit.md).
Those activities are self-reviewed and require the optional approved guest.
No VM is launched by these simulator labs.

Primary field references: [Debian procps vmstat manual](https://manpages.debian.org/trixie/procps/vmstat.8.en.html),
[Linux kernel proc/meminfo documentation](https://docs.kernel.org/filesystems/proc.html),
[GNU df manual](https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html).
