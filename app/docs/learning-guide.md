# Learning Lab: choose a path, practice and review

Library → **Learning guide ▾** gives the same essential guidance inside the
installed app. Every simulator lab is available without QEMU. Choose any lab;
suggested preparation is guidance, never a completion lock.

## Choose the right kind of practice

| Simulator collection | Labs | Preparation / what you learn |
| --- | ---: | --- |
| Linux Fundamentals | 6 | Start here if new: paths, a stopped service, permissions and a configuration fault. |
| LPIC-1 Foundations: Files & Permissions | 6 | Navigation first; ordinary private file/directory access, then search-only access and handover. Four shared labs reuse Fundamentals progress. |
| LPIC-1 Foundations: Organize and Find Files | 6 | Comfortable with paths and `cat`; create a workspace, copy/move regular files, find and verify a handover. |
| LPIC-1 Foundations: Text, Filters & Reports | 8 | Paths and file access; samples, literal filtering, counts, deduplication, fields, pipelines and saved reports. |
| LPIC-2 Resource Evidence — Offline Snapshots | 4 | Text/report skills; baseline context, memory/cache, space/inodes and cautious trends. |
| Network Diagnosis — Offline Evidence | 4 | Text/report skills; interface/address facts, routes/tests, name resolution and incident timeline. |
| DNS Operations — Offline Evidence | 4 | Text/report skills; supplied lookup roles/status, records/serials, delegation consistency and handover. |
| Web-Service Diagnosis — Offline Evidence | 4 | Text/report skills; listener/request evidence, virtual hosts, TLS facts and proxy handover. |

There are **42 collection appearances / 38 distinct Linux scenarios**. Shared
exact versions share Learn/Challenge progress wherever they appear. Three original
networking simulations below the collections add gateway/DNS, subnet and ordered
firewall practice: **41 distinct simulator activities**, not 45. Imports with different identities or versions may coexist. Exact matching imports
share their pinned version; different content under the same identity/version is
a conflict, not a new independent lab, and is refused without replacement. Hiding a shared
lab applies everywhere; Show hidden / removed lets you restore without losing
attempts. Inactive labs must be restored before practice.

The original networking labs change simulated network state. Linux simulator
commands operate on virtual files/state. Offline-evidence labs read **supplied
fictional snapshots**: an `ip`, `dig`, `curl` or log file is not execution of that
utility, a live diagnosis or a change to a service. No host command, filesystem,
process or network access is available to learner commands.

## A useful learning cycle

1. Choose a collection and Start/Continue. Read the short goal and current step;
   open **Lab details** for all objectives, rules and limits. Details stays open
   while you use the terminal or virtual file editor where supported.
2. In supported guided Linux packs, **Learn** gives one command, explanation and
   expected observation at a time. Networking labs use tasks, device settings,
   diagnostics and hints instead of a command walkthrough.
   Hints have no hidden penalty. **Challenge** hides guided commands and hints;
   necessary rules and supplied reference material remain available. It is an
   independent task, not a guarantee that model answers are inaccessible.
3. Type `help` for supported syntax. In evidence labs, `cat HELP.txt` provides
   fixture context, model interpretation and common mistakes. Commands differ
   by contract: do not assume all labs support `chmod`, editing or redirection.
4. Investigate, change, apply where applicable, then test. Settings/editor drafts
   remain separate from applied state; Apply validates atomically. Console report
   writes take effect immediately and follow the documented redirection rules.
5. **Submit** checks the applied state and declared activity evidence. Review each
   objective's points and PASS/FAIL evidence. Continue working, correct and retry;
   diagnostic runs alone do not record a submission.
6. Reset or changing modes confirms a fresh attempt and preserves previous
   history. Close normally and reopen the **same profile** to resume its pinned
   content, mode, progress, drafts and pending command. A new profile is separate.

## What a report score does — and does not — establish

Text/evidence objectives require specified UTF-8 records, units, LF line endings
and ordering, plus declared inspection evidence. This engine compares report
bytes; it does **not** normalize prose or accept merely similar wording. Required
format is explicit in Lab details and the fixture reference. Equivalent supported
paths/pipelines count if they produce the correct report and actions. Do not add
free-form reasoning to an exact factual report.

Write first, then perform the required final reading. Any later actual write
invalidates prior inspection evidence, including source readings where required.
`>` opens/truncates before execution; a failed command does not undo truncation.
After correcting a report, read it again before resubmitting. Missing/incorrect
records and missing verification can fail different objectives.

Resource snapshots assign 50 points to reports, 20 source readings, 20 final
readings and 10 enforced source preservation. Network/DNS/Web snapshots assign
80 to the factual report and 20 to final reading. Invariants are not proof of a
learner skill. A **100/100 objective score does not assess explanations, causal
conclusions, diagnostic mastery or forecasts**. Compare reasoning with the model
and uncertainty questions yourself; retain personal reasoning in your own notes.
There is no general free-form answer editor or semantic reasoning checker here.

Try an incomplete report, inspect the failed objective, correct it and retry.
For details use [Resource guidance](lpic-2-resource-simulator.md),
[Network/DNS/Web guidance](lpic-2-offline-evidence.md) and the
[precise bounded text grammar](text-stream-contract.md).

## Separate optional real-Linux path

**Real Linux VM preview…** opens a separate selector, not a simulator lab.
Twelve units / 102 lessons cover Processes; Resources; Services & Recovery; Bash;
Users & Access; Scheduling; Backup; Discovery & Packages; Storage; [Local Shell & Filesystem Administration](vm-preview/local-shell-unit.md); and [Text & Archive Tools](vm-preview/text-archive-unit.md). Use each
unit's stated prerequisites and exact approved image. Missing images fail clearly;
there is no privileged-image fallback or automatic software installation.

Start opens a native guest console; Stop shuts it down; Resume boots existing
disk files, **not RAM or shell jobs**. Reset requires confirmation and preserves
retained disk generations. Completion is **self-reviewed, unscored**, not guest
assessment. Keep fit enabled beside Learning Lab; manual zoom needs a sufficiently
large floating console, and reopening returns to fit. See [VM setup](vm-preview/setup.md).

Profile backup restores simulator progress/imported packs/settings into a new
empty profile. **VM disks and sessions are excluded**, not portable through that
backup. Scenario export contains content; attempt/history export contains personal
evidence and is not a restorable profile. See [backup rules](profile-backup.md).

## Coverage and unfinished work

Official objectives rechecked **2026-10-11**: [LPIC-1 v5.0](https://www.lpi.org/our-certifications/exam-101-102-objectives/)
and [LPIC-2 v4.5.0](https://www.lpi.org/our-certifications/exam-201-202-objectives/).
The snapshot collections reinforce selected resource, network, DNS and web
interpretation skills. They do not provide live administration or complete exam
preparation. No LPI affiliation is implied. The [objective inventory](curriculum-coverage.md)
and [completion checklist](completion-checklist.md) name demonstrated partial
coverage and missing skills. Future live services, broader storage/boot practice
and automatic reasoning checks need separately approved capabilities.

The owner reports the latest offline-evidence labs work well. Physical-keyboard,
wheel/trackpad, accessibility and exhaustive native-dialog checks remain
outstanding; that feedback is not expanded into those claims.

## Text & Archive completion-family checkpoint

[Eight real-guest lessons](vm-preview/text-archive-unit.md) add descriptor routing, tee/statuses, safe xargs, sorted reconciliation, grouped find, newc cpio and independent recovery transfer. Existing lessons/pins and images remain exact; completion is self-reviewed/unscored. Whole-objective rollups remain unchanged; xz/at are absent. [Acceptance](vm-preview/text-operations-acceptance.md) records actual boundaries and outstanding physical-input/accessibility checks.

## Accounts, Scheduling, Logging & Recovery checkpoint

[Eight real-guest lessons](vm-preview/operations-unit.md) add fabricated account-pair consistency, exact cron ownership, loaded timer outcomes, journal cursor/field semantics, open-descriptor rotation, local notices and independent recovery transfer. Existing images and guest policies remain unchanged. Completion is self-reviewed and unscored; at/mesg remain absent. [Acceptance](vm-preview/text-operations-acceptance.md) distinguishes native automation from physical input and accessibility.
