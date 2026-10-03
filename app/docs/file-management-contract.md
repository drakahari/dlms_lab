# Navigation contract 4: bounded virtual file management

This contract is an opt-in extension of `linux-navigation`, behavior
`linux-file-management-1`. Contracts 1–3 and their pinned behavior versions remain
unchanged. Portable format 1, attempt storage and backup formats are unchanged.
Packs supply JSON data only. This document precedes engine implementation.

## Supported syntax

One command per entry, up to 512 characters. Paths use letters, digits, `/`, `.`,
`_`, and `-`, up to 256 characters. Relative and absolute paths, `.` and `..`
are accepted. Traversal above virtual `/` is rejected. Whitespace separates words;
quoting, variables, glob expansion, redirects, pipelines and chaining are rejected.

| Syntax | Semantics and limits |
| --- | --- |
| `help`, `pwd`, `ls [-l] [PATH]`, `cd [PATH]`, `cat PATH` | Existing bounded navigation; `cd` with no argument returns to the scenario start. Reads/listing and search permissions are checked. |
| `mkdir [-p] PATH` | Create one directory, or missing parents with `-p`. Existing directory is a no-op only with `-p`; a file collision is an error. New directories are learner:learner 0755, representing default 0777 filtered by a fixed 0022 creation mask. |
| `cp -n SOURCE DEST` | One regular file only. Read permission on source and write/search on destination parent. Existing directory destination appends source basename. An existing target file is skipped without changes; no overwrite. New owner/group learner; ordinary source mode filtered by fixed 0022. No recursive copy or metadata-preservation options. |
| `mv -n SOURCE DEST` | One regular file only, same virtual filesystem. Directory destinations append basename. Preserve content, owner/group and mode; require write/search on both parents, not source file-read permission. Existing target file is skipped; no overwrite. No directory moves or cross-filesystem copy fallback. |
| `find PATH [-type f\|d] [-name NAME]` | Walk one virtual start, including the start itself; optional filters in either order, each once, combined with AND. NAME is an exact basename, not a wildcard. Sorted absolute output. Read/search on directories for descent; no file-read required to match names. If any directory cannot be searched/listed, report denial and award no discovery evidence. No `-exec`, deletion, size/time tests or other find expressions. |
| `rm PATH` | Remove one regular file. Require parent write/search; file write/read is not needed. No force, recursion, options or multiple operands. |
| `rmdir PATH` | Remove one empty directory. Require parent write/search; reject nonempty directories, the current directory/ancestors, and mutation roots. No `-p`. |

`-n` is recognized Linux no-clobber syntax. Bare `cp`/`mv` and unsupported options
are rejected with the supported syntax, rather than silently enabling clobbering.
This simulation reports outcomes, not host exit codes; GNU versions differ in
details of no-clobber exit status. It does not claim complete GNU compatibility.
The inspected target's GNU coreutils 9.11 marks `cp -n` deprecated while retaining
its skip-existing behavior; `mv -n` is also recognized. Newer GNU alternatives
such as `--update=none` are not part of this bounded contract. Do not assume every
distribution supports identical options or exit-status details. Source references:
[GNU cp](https://www.gnu.org/software/coreutils/manual/html_node/cp-invocation.html),
[GNU mv](https://www.gnu.org/software/coreutils/manual/html_node/mv-invocation.html),
and [GNU find](https://www.gnu.org/software/findutils/manual/html_mono/find.html).
Online GNU pages were unavailable during verification; local tool help and six
static reference checks in a disposable directory verified the supported forms.

On real Linux, `rm` removes directory entries and `mv` renames them: parent
permissions govern these actions. This simulation follows that rule. It has no
sticky bits, ACLs, supplementary groups, links, devices, mount boundaries or root
privilege override. Owner/group/other class selection uses the existing model.
`find` has one explicit simplification: Linux may print partial matches alongside
permission errors; this contract reports the error atomically without awarding
partial discovery evidence. No terminal command invokes a host API.

## Pack declaration and boundaries

Required capabilities: `virtual-filesystem`, `file-navigation`, `activity-evidence`,
`bounded-file-management`. Domain schema 2 contains the initial filesystem, cwd,
one or more canonical `mutable_roots`, and a lesson. Roots must be accessible,
learner-owned initial directories; their nodes remain fixed. Only descendants
may be created, copied into, renamed from/to or removed. Outside nodes are pinned
and immutable. Reads/discovery outside roots are allowed if permissions allow.

Limits: 64 initial nodes; 128 runtime nodes; 8 KiB per file; 64 KiB total UTF-8
file text; 16 objectives; 32 hints; 256 KiB pack; at most 128 distinct paths per
activity kind. Output is bounded to 16 KiB. All mutations occur on a candidate
dictionary and validate before commit. Errors, limit failures and collisions leave
the complete applied state unchanged. No external side effects or deletion.

## Declarative grading and Learn guidance

Allowlisted predicates:

- `node_exists`: canonical path and required file/directory kind.
- `file_matches_initial`: destination content equals a declared initial file.
- `original_preserved`: initial node still exists unchanged at its original path.
- `node_absent`: a declared initial disposable path no longer exists.
- `cwd_equals`: final virtual working directory.
- `activity_observed`: successful `pwd`, `ls`, `cd`, `cat` or `find` at a target.

Points total 100. Use final state for organization, content preservation and
cleanup; never require a specific copy/move transcript. Where read/discovery
verification matters, explicitly label it as action evidence. Every actual
filesystem mutation clears `cat`/`find` verification, so verify the final result.
No-op/skipped commands do not clear evidence. Other surviving activity is pruned
when its target disappears. Inspection/checking grades never manufactures activity.

Lessons contain one step per objective: trusted, parser-validated command text,
short explanation and expected result. Learn suggests one route; Challenge hides
these steps and hints and grades the same predicates. The validator simulates the
Learn route to prove structural goal feasibility, without installing or executing
code. It cannot establish teaching quality or complete real-Linux coverage.

The location lab assesses successful reads at representative configuration, log
and home paths plus a final directory. It does not assess an unsubmitted verbal
explanation of FHS roles. Other labs may accept alternate supported paths/order;
a `find` objective explicitly measures use of the declared discovery mechanism,
not one exact command string or traversal order.

## Compatibility and test gate

Implement trusted engine behavior and isolated tests before collection packs.
Test syntax, permissions, collisions, ancestor walking, complete failure atomicity,
limits, objective feasibility, hostile data/commands and host-API sentinels. Preserve
old pack bytes, runtime pins and command rejection; run all old regressions.
Only then add six data packs and the collection. Test both modes, alternate valid
approaches, reset, pinned attempts, same-profile reopen, export/reimport, backup,
installed resources and the existing UI at supported sizes/scales. If storage or
backup migration becomes necessary, stop before implementing it.
