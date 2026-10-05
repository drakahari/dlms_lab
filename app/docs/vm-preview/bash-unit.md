# LPIC-1 Foundations: Bash, Regex & Safe File Changes

Library → **Real Linux VM preview…** → **Choose a real-Linux collection** →
**LPIC-1 Foundations: Bash, Regex & Safe File Changes**. Choose any of its twelve
lessons; sequence is guidance, never an unlock. Start opens the native GTK guest
console. Type there, not in a host terminal. Core simulations need neither QEMU
nor an image. This unit uses the existing **unprivileged** offline image; it never
substitutes the administrator image. No packages or guest policy changed.

Prerequisites: paths, ordinary file permissions and text/filter basics. Learn
shows commands, explanations and expected observations. Challenge retains setup,
small fixtures and safety rules, but hides guided solutions and hints. Completion
is **self-reviewed, unscored**. Advancing instructions does not verify execution.

| # | Lesson | Evidence to retain | Partial LPIC-1 v5.0 subset |
|---|---|---|---|
| 1 | Select files safely | Scoped discovery; exact spaced/backslash filenames, copied bytes/modes and unchanged originals. | 103.3 globbing; 104.7 find reinforcement |
| 2 | Understand your shell environment | Local/exported child values; command lookup; exact PATH restoration. | 103.1; 105.1 environment |
| 3 | Quote arguments correctly | Literal/expanded arguments; glob boundaries; quoted substitution; literal command-like text stays data. | 103.1; 103.3 reinforcement |
| 4 | Separate output from errors | stdout/stderr artifacts, truncation and default/pipefail status comparison. | 103.4; 105.2 preparation |
| 5 | Search with basic and extended regex | Anchored BRE/ERE matches; fixed versus wildcard dot; blank line, no-match and invalid-pattern statuses. | 103.7 |
| 6 | Preview a text transformation | Anchored sed preview; one-line diff; checked candidate, original hash and rollback. | 103.2 sed; 103.7 |
| 7 | Edit confidently with vi | Modes/navigation/search/change/yank/delete; exact saved file and original backup. | 103.8 |
| 8 | Recover from a mistaken edit | Undo, unsaved discard, saved-mistake retention and exact restoration. | 103.8; 103.3 reinforcement |
| 9 | Write and run a small Bash script | Interpreter, arguments, executable bit, syntax and behavior/status/error checks. | 105.2 |
| 10 | Guard a script’s inputs | Readable regular file, empty/nonmatching/denied inputs and distinct failure statuses. | 105.2 conditions/status |
| 11 | Process records without losing data | Function, literal whitespace/backslashes, empty/unterminated records and enforced bounds. | 105.2 loops/read; 105.1 functions |
| 12 | Repair a file-processing workflow | Preserved original; correct report, rejected malformed input, guarded publication and rollback handover. | 105.2; prior skills reinforced |

Lesson 10's full outcome is **“Guard script inputs and report failures predictably
before declaring success.”** It repairs the truncated proposal description.
Official objective version rechecked 2026-10-05. Objective mapping is partial: these lessons do not establish full Bash, vi or LPIC
mastery. Reference: [official LPIC-1 v5.0 objectives](https://www.lpi.org/our-certifications/exam-101-102-objectives/).

## Small fixtures, bounded practice

Each lesson creates a unique `mktemp -d` guest-home workspace and prints its path.
Stop if creation/cd fails. Type the small supplied fixture manually; no clipboard
sharing is assumed. Record the workspace path. On Resume, locate it explicitly:
variables and shell jobs are not restored. Keep fit enabled beside the Lab;
manual zoom needs a sufficiently large floating console. Reopening returns to
fit, not a saved manual zoom percentage.

Normal script inputs are at most **20 records / 2048 bytes**. Deliberate failure
checks use 21 records or 2049 bytes. Keep total small files/notes under **64 KiB**;
no large downloads or workload. Use `timeout -k 2s 5s` for script experiments,
with counters and size checks as additional bounds. No background workers.
Timeout supervises a process group; suspended/uninterruptible processes can exceed
wall-clock expectations. Syntax validity is separate from correct behavior.

Single quotes protect literal data. Double quotes preserve expanded argument
boundaries. A shell glob is not a regex; quote patterns passed to find/grep.
Do not parse `ls` output, use `eval`, or expand untrusted names into a deletion
command. No broad process termination or recursive cleanup is needed.

## Errors and safe changes

`>` truncates before a command reads input; failures can leave empty/partial
output. `pipefail` changes status, not file side effects. `set -e` has exceptions
and is not universal error handling. Capture statuses immediately and inspect
stderr. grep 1 means no selected records; invalid expressions produce 2. diff 1
means differences. Inspect exact files rather than treating every nonzero as the
same failure.

Preserve originals with `cp -p` and record hashes. Preview an anchored change,
inspect the candidate and publish it only after success. Publication in this
exercise is deliberate copying, not a claimed transactional deployment system.
The capstone parses only its documented `name|ok/fail` format; it is not a general
CSV/log parser. Empty input produces zero counts; malformed rows may leave partial
candidate output, which must never replace a prior good report.

Vim Tiny provides the installed `vi`; nano is used for manually entered scripts.
Escape leaves insertion. `u` undoes within the editor; `:q!` discards unsaved
changes, not changes already saved. Restore a saved mistake from the retained
original and compare bytes/mode. Controlled interruption is not power-loss,
swap-file, filesystem, boot or rescue recovery.

Cleanup remains inside the recorded workspace and names exact exercise files.
Keep originals and evidence. No `rm -r`, `rm -rf`, deletion glob, sudo, startup-file
edit, device write or host operation. Leave the directory and use `rmdir` only
when empty. Reset retains the old disk generation and boots a fresh disk; confirm
its warning. VM disks and VM practice records remain excluded from profile
backups/exports. Preserve them separately if needed.

## Compatibility and remaining curriculum gaps

Trusted registry limits: **4 units, 16 lessons per unit, 36 total** (formerly 24).
The registry remains bundled, bounded display-only data, never an execution or
external import format. Every new default points explicitly to
`debian13-jobs-local-v1`. Original 24 lesson bytes, descriptors, mappings, pins and
special legacy session location remain unchanged. Missing images fail rather than
falling back to a privileged guest.

Still deferred: complete startup/profile customization, advanced shell features,
mail/scheduling, links/archives, comprehensive text tools and vi, ACL/ownership
administration, boot/kernel/storage/rescue, networking and multi-host work.
The current unit prepares useful skills for administration; it does not complete
LPIC-1 or LPIC-2. Public release, UI polish and outstanding Qt/ICU redistribution
review remain separate work.
