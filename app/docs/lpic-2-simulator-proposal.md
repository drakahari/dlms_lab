# Proposal: LPIC-2 Resource Evidence — Offline Snapshots

Planning only; no new packs, collection, capabilities or contracts are included
in the navigation patch. Repository inventory: `dbcc237` plus that UI patch.

## Current inventory and coverage

The Library has four simulated Linux collections: Linux Fundamentals (6),
Files & Permissions (6), Organize and Find Files (6), Text, Filters & Reports (8).
Shared membership means 26 appearances but **22 distinct Linux scenarios**.
Three additional networking simulations cover gateway/DNS, subnet boundary and
ordered service firewall rules. These are original bounded simulations, not
real Linux network administration or complete LPIC networking coverage.

The separate real-VM selector has nine units, **76 lessons**:

| Unit | Lessons | Existing LPIC-2 contribution |
| --- | ---: | --- |
| Processes, Jobs & Priorities | 8 | Process observations supporting resource diagnosis |
| Resource Diagnosis & Capacity Evidence | 8 | Partial 200.1/200.2: actual observations, supplied trends/forecasts |
| Services, Logs & Safe Recovery | 8 | Partial startup/service work; not full boot recovery |
| Bash, Regex & Safe File Changes | 12 | Prerequisite skills |
| Users, Groups & Access Administration | 8 | Prerequisites; no directory-service administration |
| Cron and systemd Timers | 8 | Operational practice; not full system startup coverage |
| Backup & Safe File Recovery | 8 | Partial 206.2 |
| System Discovery & Package Fundamentals | 8 | Partial kernel/package inspection; not kernel compilation |
| Filesystems, Mounts & Safe Maintenance | 8 | Partial 203.1/203.2: actual ext4/mount/offline repair work |

All nine are **VM-only, self-reviewed and unscored**. None becomes a simulator
activity merely because its instructions appear in the app. See the existing
[objective-by-objective coverage inventory](curriculum-coverage.md) and linked
unit acceptance reports for demonstrated scope and omissions.

Official objectives rechecked **2026-10-10**: LPIC-2 **4.5.0**, exams 201-450 and
202-450. 200.1 concerns actual resource measurement and troubleshooting; 200.2
concerns monitoring, trends and capacity prediction. The proposed snapshots
support interpretation practice and reinforce these objectives; they do not
fulfil their measurement/monitoring requirements. No full exam coverage or LPI
affiliation is claimed. [Official LPI objectives](https://www.lpi.org/our-certifications/exam-201-202-objectives/)

## Smallest useful batch

Recommend **four data-only labs** using the existing `linux-navigation`
contract **5**, behavior `linux-text-streams-1`. Prerequisite: the existing Text,
Filters & Reports collection. Start any lab; no unlock system.

Files would contain small, labelled **synthetic snapshots**, including units,
timestamps, machine context and a warning that they are not live measurements.
Learn explains one observation/filter/report step at a time. Challenge gives
report requirements without the solution. Interpretation questions belong in
lesson text and remain self-reviewed; the engine cannot grade free-text reasoning.

| Proposed lab | Outcome and learner activity | Existing automatic feedback/checking | Real-VM boundary | New capability |
| --- | --- | --- | --- | --- |
| Read a resource baseline | Locate CPU, memory and filesystem observations in a supplied snapshot; inspect it and save the required baseline rows into a virtual report. Distinguish values, units and sampling time. | `stream_observed` checks a named inspection tool/source/output; `file_content` checks the exact final report; preserve supplied files. Equivalent supported paths/pipelines producing the same report count. | No execution of `free`, `top`, `vmstat` or `df`; no live machine measurement. Reinforcement for 200.1. | None |
| Separate available memory from cache | Read an annotated memory sample, extract the supplied MemAvailable/cache rows, and explain why low free memory alone is insufficient evidence of pressure. | Grade extraction and report accuracy; hints explain missing evidence. Do **not** claim the grade proves the learner's explanation is correct. | No kernel memory model, workload, OOM, reclamation or computed pressure assessment. Actual observations remain in the VM resource unit. | None |
| Compare space and inode evidence | Inspect separate labelled capacity/inode rows, retain both in a report, and identify in self-review which measurement would be relevant to each supplied incident. | Grade the required evidence report and final reading; incorrect/missing rows receive existing predicate feedback. The diagnostic choice is not automatically assessed. | No virtual filesystem exhaustion, `df` implementation, block-device administration or storage repair. 200.1 interpretation preparation; not 203.1/203.2 practice. | None |
| Prepare a trend handover | Extract a chronological column from a supplied historical dataset, include the flagged missing sample, and assemble a bounded report without altering originals. Explain why an incomplete series may not justify a forecast. | Exact report/inspection/original-preservation predicates. Use bytewise sort only where the fixture's representation makes that ordering valid; no implicit numeric sort. | No live monitoring, charting, arithmetic calculator or automatically checked forecast/recommendation. Limited reinforcement for 200.2. | None |

The text engine supports bounded `head`, `tail`, `grep -F`, `wc`, `sort`, `uniq`,
`cut`, `cat`, pipelines and declared `>`/`>>` output paths. It grades exact UTF-8
report contents and retained inspection evidence. It has **no general file
editor in this contract**, numeric/range predicate, calculator, condition parser,
multiple-choice grader or semantic configuration checker. Output writes clear
prior verification: inspect final reports after the last write. Existing identity,
pinning, Learn/Challenge, reset, import/export and backup mechanisms can be reused.

## Separate gaps; require a later approval

- **Independent capacity calculations and troubleshooting decisions:** a small
  trusted answer/evidence mechanism with numeric tolerance, units and explicit
  insufficient-evidence outcomes would be needed for meaningful automatic grading.
  Selecting a prewritten answer line using `grep` would only demonstrate recognition;
  it must not be sold as independently calculating a forecast.
- **Configuration analysis:** text extraction is available; semantic validation of
  `fstab`, systemd or resource limits is not. The existing service engine models
  only its declared web configuration fields, not arbitrary Linux configuration.
  Do not reuse its service-health predicates as a generic configuration checker.
- **Real administration:** workloads, tuning, mount/repair, service control and
  before/after resource effects belong in the accepted disposable VM units.
  No simulator CPU/memory/disk model is proposed here.

## Later acceptance gate

For an approved content-only batch, validate each pack and its feasible Learn
route; play both modes with alternative supported paths, incorrect/missing rows,
empty inputs and last-write verification invalidation. Check reset, same-profile
reopen, exact pins, scenario export/reimport, history separation, backup/restore
and visibility choices in disposable profiles. Run existing regressions and GNU
fixtures. Installed-wheel tests must load all new resources outside the checkout.
Check readable Library grouping and simulator labels at supported sizes/scales.
No guest is needed for snapshot grading; claims about real observations continue
to rely on the existing VM evidence.

Decision for a future task: approve these four evidence-report labs as a **limited
content-only complement**, or separately scope an interpretation/answer contract
before promising an automatically assessed capacity/diagnosis collection.
