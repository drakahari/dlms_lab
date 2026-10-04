# LPIC-1 Foundations: Text, Filters & Reports

Eight original beginner labs; approximately 40 minutes. Preparation: Unit 2 or
confidence with virtual paths, cat and directory access. The recommended sequence
is optional; every lab is available immediately. Existing Library/terminal design
and collections are preserved. All eight are built-in package resources.

LPIC-1 objectives v5.0 (101-500/102-500): partial **103.2** filter and **103.4**
stdout-pipeline/redirection coverage. Fixed-string search is preparation for
**103.7**, not regular-expression coverage. No claim of full coverage: no Bash
environment/expansion, stdin/stderr redirects, tee/xargs, regex, sed, archives,
interactive pagers or complete text-tool options. Original content, no affiliation.
[Official LPI objectives](https://www.lpi.org/our-certifications/exam-101-102-objectives/).

## Sequence, learning and grading

Packs live in `learning_lab/collections/packs/`, content version 1.0.0, all using
opt-in navigation contract 5 / `linux-text-streams-1`. Learn provides one current
step with command, explanation and expected result; hints explain reasoning.
Challenge hides these commands and hints and states the same desired outcomes.

| # | Title / stable scenario ID | Assessed outcome and common incorrect approach |
| --- | --- | --- |
| 1 | Inspect the beginning and end / `linux-log-slices` | Visible head first-two and tail last-two results (50 each). Printing the whole file does not demonstrate sampling. Head/tail preserve the last record's missing LF. 103.2 subset. |
| 2 | Select literal events / `linux-text-events` | Visible fixed-string ERROR records (50) and literal a.b record (50). aXb is not a match. Regex commands unsupported; 103.7 preparation only. |
| 3 | Count lines, words and bytes / `linux-text-counts` | Correct wc LF/word/byte option and visible result (30/30/40). Two LFs, five words, 23 UTF-8 bytes. An unterminated record is not another LF; bytes differ from characters. 103.2 subset. |
| 4 | Sort before removing duplicates / `linux-text-deduplicate` | Adjacent-only uniq result (40), sorted unique counts through a pipeline (60). uniq alone retains separated beta; sort alone retains duplicates. 103.2 plus selected 103.4 composition. |
| 5 | Extract a delimited field / `linux-text-fields` | Correct visible field-2/field-3 projections (50 each). Missing field on a delimited record yields an empty line; an undelimited record passes unchanged. Quoted pipe is a delimiter; unquoted pipe is an operator. 103.2 subset. |
| 6 | Build a useful pipeline / `linux-text-pipeline` | Visible sorted unique successful sites from the correct source (100), using at least two supported stages. Wrong status selection or unsorted duplicates fails. Alternate supported ordering is accepted when equivalent. 103.4 subset, reinforces filters. |
| 7 | Replace and append deliberately / `linux-text-report` | Exact replacement and appended reports (30 each), final reads after writes (20 each). Repeating append duplicates beta; a missing source after > still erases old output. Grade final report state, not mandatory redirect transcript. 103.4 subset. |
| 8 | Deliver a filtered report / `linux-text-handover` | Failed-site report (25), count (15), unchanged source (10), visible successful selection pipeline (20), final report reads (15 each). Count unique sites, not failed events. Source preservation already earns 10 initially and must remain true. Reinforcement/assessment, no additional objective coverage. |

Tool-specific inspection requires the correct source and displayed result, not a
fixed command string. Equivalent relative/absolute paths work. wc evidence ignores
its display-only filename label but retains the counting option. Only the final
visible stage supplies tool evidence; internal or redirected text is not inspection.
Pipeline evidence checks the final displayed result and source, not exact stage
order. Earlier failed commands are never required. Instructions/help alone earn
no activity evidence. Final report content can be produced by any supported route.

Actual writes invalidate previous stream inspection evidence. Verify after all
writes. Wrong-report feedback includes expected and actual text; tool feedback
names the expected source/result. Hints have no hidden score penalty.

## Semantics and boundaries

The [grammar and command matrix](text-stream-contract.md) were written before
coding, then corrected against static GNU fixtures. All learner command processing
is dictionary-only. The new engine reuses the virtual filesystem, terminal and
attempt lifecycle. It has no host filesystem/process/network API. No shell is run.

One UTF-8 file per stage, four stages maximum, fixed C bytewise semantics. Quotes
group literal words without expansion/escapes. Files are at most 8 KiB, total text
64 KiB; stage stdout 32 KiB, console display 16 KiB. Display limits do not change
stream/report bytes. Resource failures explicitly retain bounded UTF-8 prefixes.

Redirection is deliberately **not transactional**. Output is created/truncated
before reading input. Missing/unreadable input preserves those changes. Downstream
filters still process empty input after an upstream error; pipeline status belongs
to the last stage, but all errors remain visible. GNU cat refuses nonempty
input/output self-copy. Pipeline aliases and other filter self-append are rejected
before opening because scheduling/buffering behavior is outside the subset.
Unsupported syntax/options are preflight rejections, not an emulation of a full
shell invoking an invalid utility. No pipefail, SIGPIPE, binary input or OS faults.

Packs remain data-only and pass the authoritative import validator, including
bounded feasibility checks. Validation cannot add commands/code. The existing
in-app starter remains the supported permissions template; this unit does not
broaden that authoring template. No engine duplication or general-purpose shell.

Existing contracts 1–4, accepted pack bytes/identities and saved records are
preserved. New attempts pin contract 5. Older apps reject contract-5 packs/backups
before activation; use this candidate or a compatible newer app to resume them.
No storage migration or backup-format change. Scenario export preserves pack data;
history export is separate and is not history import. Profile backup restores
only to an empty destination using the established explicit confirmation workflow.

## Curriculum coverage summary — implemented and remaining

This table covers the three implemented LPIC Foundations units, with objective
version 5.0 checked against the official current 101/102 objectives. Completed labs
establish their declared simulated outcomes; they are not evidence of full exam
objective mastery. Reinforcement assessments add practice, not objective coverage.

| Objective | Implemented preparation / partial coverage | Remaining gaps |
| --- | --- | --- |
| 103.1 command line | Units 1–2: pwd/ls/cd/cat, relative/absolute paths; introductory preparation only. | Actual Bash environment, variables/export, PATH, history, quoting/expansion and command lookup. |
| 103.2 text filters | Unit 3: bounded head/tail, wc, sort/uniq and single-field cut. Partial coverage. | Broader options; sed/tr/nl/paste/split/od, checksums, compressed streams and pagers; binary/locale behavior. |
| 103.3 file management | Unit 2: mkdir, regular-file cp/mv, exact-name/type find, one-file rm and empty rmdir. Partial coverage. | Globs, recursive operations, richer find expressions/actions, archives/compression and dd/cpio. |
| 103.4 streams | Unit 3: bounded stdout pipelines and > / >>, with real-style truncation/error side effects. Partial coverage. | stdin/stderr redirects, tee/xargs, complete shell syntax, process timing, pipefail/SIGPIPE and exit-status handling. |
| 103.7 regex | Unit 3: fixed-string grep -F prepares for searching, **no regex coverage**. | BRE versus ERE, anchors/classes/quantifiers and regex substitutions; grep/sed beyond fixed strings. |
| 104.5 permissions | Unit 1: ordinary owner file modes and directory read/search; partial coverage. | chown/chgrp, richer chmod syntax, special bits, configurable umask and multi-user practice. ACLs also remain outside the simulator; no extra objective claim. |
| 104.7 locations / FHS | Unit 2: inspect representative /etc, /var/log and home files; introductory preparation. | Full FHS, standard-location reasoning and locating tools/files; verbal understanding is not graded here. |

103.5 processes, 103.6 priorities and 103.8 vi editing remain unimplemented.
Existing service labs are introductory service-diagnosis practice, not full 101.3
boot-target/shutdown coverage. Existing networking labs are conceptual preparation,
not demonstrated coverage of real Linux networking administration. Hardware/boot,
installation/package management, filesystem administration/links, Bash scripting,
desktops, accounts/scheduling, system services, networking and security still need
separate study and real-Linux practice. No full LPIC-1 or Exam 102 coverage claimed.

**Recommended next batch (proposal only): Processes, Jobs & Priorities**, using a
disposable VM with an interactive Bash terminal. Prerequisite: these file/text
units. Seven labs: identify a practice process (ps/pgrep); monitor/filter its state
(ps/top); suspend and resume a job (jobs/bg/fg); terminate an owned practice process
with TERM; keep a practice job alive after logout (nohup); launch and renice an
owned job at lower priority; independent diagnosis/cleanup assessment. This adds
selected 103.5/103.6 skills. It does not establish all process tooling or priorities.

The current engines cannot model TTY job control, live processes, signals,
scheduling or logout. A real VM is the better fit for accurate practice. No new
engine, host-command connection, VM provisioning or profile migration is proposed
as part of this commit. The smallest next deliverable would be reviewed manual VM
lab recipes and evidence criteria, scoped to newly created owned practice jobs;
application integration would require a separately approved design. Acceptance
would check real process/job states, signal outcomes, priority values, cleanup and
repeatability, rather than fixed PID values or command transcripts. No next-unit
implementation has started.

## Launch and optional disposable check

Do not update the working installation or use personal data for this check:

```bash
cd /home/drak/Documents/dlms_lab/app
text_profile=$(mktemp -d /tmp/learning-lab-text.XXXXXX)
printf 'Disposable profile: %s\n' "$text_profile"
python3 -B -m learning_lab --data-dir "$text_profile/data" --config-dir "$text_profile/config"
```

Find **LPIC-1 Foundations: Text, Filters & Reports**. Start the final assessment
in either mode. In its **Simulated Linux terminal**, enter each line separately:

```text
grep -F "|fail" checks.txt | cut -d "|" -f 1 | sort | uniq > failed-sites.txt
cat failed-sites.txt | wc -l > count.txt
grep -F "|fail" checks.txt | cut -d "|" -f 1 | sort | uniq
cat failed-sites.txt
cat count.txt
```

Submit: 100/100. A later `cat missing > count.txt` should report failure and leave
count.txt empty; its report/evidence credit must fail. Restore the count, display
the selection and read both reports again. Reset/mode change preserves old attempts.
Reopen with the same printed paths to retain results. This is optional, not a
standing completion gate; routine verification is agent-owned.

## Optional real Linux practice (manual, no VM provisioning)

Use a disposable directory in a Linux VM or local terminal. These are real shell
commands, **not commands to paste into the simulation**. They touch only newly
created exercise files and need no sudo. Keep the printed directory until finished.

```bash
text_exercise=$(mktemp -d /tmp/lpic-text-practice.XXXXXX)
printf 'Exercise directory: %s\n' "$text_exercise"
cd "$text_exercise"
printf 'alpha|ok\nbeta|fail\nzeta|fail\nbeta|fail\n' > checks.txt
grep -F '|fail' checks.txt | cut -d '|' -f 1 | sort | uniq > failed-sites.txt
cat failed-sites.txt
wc -l < failed-sites.txt
printf 'café tea\n猫 naps\nlast' > unicode.txt
LC_ALL=C POSIXLY_CORRECT=1 wc -l unicode.txt
LC_ALL=C POSIXLY_CORRECT=1 wc -c unicode.txt
cat nonexistent.txt > disposable-output.txt
ls -l disposable-output.txt
```

Observe truncation even after an input failure. Compare real shell stdout/stderr,
exit status, stdin redirection and quoting; these deserve real Linux practice.
Broader Bash/regex/process behavior is preferable in a disposable VM. No automated
VM provisioning or host commands from packs are introduced.

## Consolidated verification and changes — 3 October 2026

- Verified baseline `f9bbb91e65f0701ee7021093d9946d5aa53201ba`; pushed without
  force to the existing drakahari/dlms_lab origin; live remote hash matched.
- Source recovery: `/home/drak/.local/state/omarchy-learning-lab/recovery/text-unit-source-20261003T232209354141Z`.
  All 223 files rehashed; 66 protected old pack/engine/UI/storage/build files equal
  the baseline. No personal profile was used or copied.
- Engine internal checkpoint **315 tests passed before packs**. Final suite:
  **328 pass** (302 prior regressions, 15 new engine, 11 new pack/lifecycle cases).
- **44 GNU reference fixtures** passed using static developer commands in a
  disposable directory, comparing stdout, status, error presence and resulting
  file bytes. Includes empty inputs, unterminated records, UTF-8 bytes, C-locale
  words/order, duplicates, field gaps, quoted delimiters, no matches, upstream/final
  stage errors, failed reads after output opens, append, aliases and denied writes.
  Exact platform diagnostic wording is not claimed. Real GNU execution never
  accepts a learner command, imported pack or arbitrary input command line.
- All eight packs complete in Learn and Challenge with alternate supported paths/
  ordering. Tests distinguish wrong counts/fields, wrong selections, missing
  inspection and later-write invalidation. Reset, drafts, modes, history and exact
  state/pins survive reopening; all eight scenario exports reimport exactly.
  Profile backup/restore retains applied state, observations, visibility and drafts.
- Actual baseline code created contract-1/2/3/4 saved attempts; candidate reopening
  retained saved-record bytes. Old backup code rejects contract 5 before creating a
  destination. Backup v1/v2 regressions remain supported; no migration.
- **24 existing UI suite/scale combinations** passed (earlier collections,
  authoring, cleanup, backup/restore, Linux reference/editor, networking). New unit:
  **250 rendered checks + 8 fresh-process checks per scale** at 100/150/200%,
  across 800×600, 1024×768 and 1280×900 logical windows. New-unit checks were rerun
  after final instruction/feedback review. No QML errors. Input remains available,
  non-modal details stay open during commands, Challenge hides guidance, collection
  counts remain separate by mode, and exact state/pending input survive reopening.
- Final actual wheel: `/tmp/text-unit-wheel-verified/omarchy_learning_lab-0.1.0-py3-none-any.whl`.
  SHA-256 `387d7ee55610b622b8787b631074401a4313084f2172fa0f080155f5486ba41b`.
  Declared isolated setuptools build succeeded after an approved network retry.
  A separate temporary venv installed it; pip check passed. Copied standalone
  smoke ran with python -I from /tmp, loading all four collections / 22 unique packs
  and completing all eight new labs in both modes, then reopening exact attempts
  in a fresh process. All 93 wheel application files equal the final source.
- Runtime: Python 3.14.7, PySide6/Shiboken6 6.11.2 on Omarchy 4.0.4. GNU reference
  tools: coreutils 9.11 and grep 3.12-modified (actual local versions).

Application changes: pure `linux_text/engine.py`, adapter and package initializer;
contract dispatch in domains.py/portable.py. Content: eight packs, collection manifest
and index entry. Tests: contract, static GNU harness, lifecycle and rendered UI;
existing collection count assertions and installed smoke now include the fourth
collection. Documentation: grammar, this guide, framework acceptance and installation
smoke counts. No changes to QML, existing engines/grading/packs, storage, backup or installer
activation. Final review covers **27 files**, excludes secrets/personal data,
profiles, environments, snapshots and generated evidence; excluded files remain local.
The authorized local commit includes only reviewed files after exact staged-path,
content-hash and whitespace verification. No feature push or installed-app update;
real personal data remains untouched.

Local ignored evidence: `evidence/text-regressions-final.log`,
`text-gnu-reference.json`, `text-ui-matrix.json`, `text-final-*.json/.png`,
`text-installed-resource-hashes.json`, `text-review-hashes.json`, and wheel build
logs. Native Wayland connection remains blocked with PermissionError errno 1;
comprehensive native keyboard, accessibility, dialogs and scaling remain outstanding.
Offscreen synthesized QtTest input is not physical-keyboard acceptance. No new
owner acceptance is assumed. Optional owner testing is not a routine completion gate.

Known baseline warning (unchanged, not suppressed):

```text
gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them
```

## Commit review

Live `origin/main` was queried again before commit review and equals
`f9bbb91e65f0701ee7021093d9946d5aa53201ba`, confirming the prior Unit 2 push.
Review retained the exact 27-file scope. No application or pack change was needed.
GNU evidence now records expected/actual stdout bytes, statuses, error presence,
GNU/simulated messages, matching diagnostic categories and resulting input/output
file bytes for every fixture.
Platform diagnostic wording remains intentionally distinct. Grammar documentation
now states the supported count-token digit limits. The curriculum table separates
implemented partial objectives from remaining gaps; the next unit is a proposal.

Commit review reran all 328 regressions, all 44 fully recorded GNU fixtures, the
new-unit UI suite at each supported scale (250 checks + restart), and the matching
installed-wheel smoke/pip check. Runtime/package bytes were unchanged by review;
only documentation, reference evidence and standalone-check whitespace improved.
All previously generated local evidence remains excluded and preserved.
