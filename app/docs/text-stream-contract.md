# Text-stream contract 5 — supported behavior before implementation

Opt-in `linux-navigation` contract 5, behavior `linux-text-streams-1`. No change to
contracts 1–4, portable format, identity rules, attempt or backup formats.
The interpreter remains dictionary-only. GNU commands are used only by a separate
developer reference harness with static fixtures in a temporary directory.

## Grammar and command matrix

`pipeline := command ( '|' command ){0,3} [ ('>' | '>>') PATH ]`

Words are separated by ASCII space/tab. Single or double quotes group a literal
word, including spaces or a delimiter such as `"|"`. Quotes may surround a whole
word only: no concatenation, escapes, variables or substitution, even inside
quotes. Unquoted `|`, `>` and `>>` are operators (whitespace optional). Reject
`;`, `&`, `<`, backticks, `$`, backslashes, command newlines; unquoted
wildcards, tilde expansion, parentheses, braces, brackets and comments;
unclosed quotes, empty stages, unsupported options, extra operands and unknown
commands before opening output. Paths retain existing virtual ASCII path rules;
quoted paths still cannot contain spaces. Patterns may be UTF-8; cut delimiters
must be one ASCII byte.
No host shell, process, filesystem, network, environment expansion or imports.

| Standard subset | Behavior |
| --- | --- |
| `head [-n N] [FILE]` | First N newline-delimited records; default 10; preserve unterminated last record. N is 0–4096 decimal with at most four digits, no signed/legacy counts. |
| `tail [-n N] [FILE]` | Last N records, default 10; no follow/byte mode. |
| `grep -F [-n] TEXT [FILE]` | One nonempty fixed string; case-sensitive byte matching. Optional line numbers. No regex, context, multiple patterns or recursive search. Matches gain a final newline even when input lacked one. Exit 0 for matches, 1 for none, 2 for read failure. Other filter read errors are status 1. |
| `wc -l\|-w\|-c [FILE]` | Exactly one option. Count LF bytes, ASCII-whitespace-separated words, or UTF-8 bytes (not Unicode characters). A filename is displayed only when FILE is supplied. No combined/default/multifile mode. |
| `sort [FILE]` | Bytewise lexical order, ascending, preserving duplicates; output records newline-terminated. No locale collation, numeric/key/reverse/unique options. |
| `uniq [-c] [FILE]` | Adjacent identical records only; optional GNU-style seven-column counts; output newline-terminated. No output-file operand. |
| `cut -d DELIM -f N [FILE]` | Single ASCII byte delimiter; one positive field 1–64 with at most two digits. Missing selected fields yield an empty line. A record without the delimiter is passed unchanged (GNU default, no -s). No field lists/ranges/character/byte modes. |
| `cat FILE`, `help`, `pwd`, `ls [-l] [PATH]`, `cd [PATH]` | Existing virtual navigation. cat participates in streams; navigation/help cannot be piped or redirected. No mkdir/cp/mv/rm/chmod in contract 5. |

The first stream stage requires one FILE; later stages may omit FILE to consume
stdin. Explicit FILE at a later stage reads that file instead of stdin. Up to four
stages; at most one final stdout redirect. No stdin/stderr redirection, tee, xargs,
pipefail, exit-status variables, terminal stdin, here-documents, jobs or full Bash.

## Encoding, locale, newlines and errors

Files are valid UTF-8 text using existing virtual-file limits (no NUL, CR or
other controls except LF/tab). Internally filters operate on UTF-8 bytes with
`LC_ALL=C` / `POSIXLY_CORRECT=1` reference semantics. Non-ASCII text is preserved;
wc -c counts encoded bytes, wc -w treats only ASCII whitespace as separators.
An empty input has zero records. A final nonempty unterminated record counts as a
record for head/tail/sort/uniq/cut/grep, but contributes no LF to wc -l. No implicit
newline is added by cat/head/tail. GNU filters' newline normalization is preserved.

Stages produce separate stdout, stderr and status. A read error produces no
stdout for this single-file subset; downstream stages still process empty input.
No-match grep is status 1 without stderr. Pipeline status is the last stage's
status (no pipefail). Successful downstream output does not erase upstream errors.
Diagnostics and statuses are clearly labeled in the simulated transcript.

## Redirection, permissions and nontransactional failure

Only declared `output_files` can receive writes. They can be initially absent;
ancestors must exist. Existing regular files need file write and ancestor search,
not parent write; creation needs parent write/search. New files learner:learner
0644 (fixed 0022 creation mask). No links, ACLs, sticky bits or privileged override.

After syntax validation, open the final output before reading command input:
`>` creates/truncates immediately; `>>` creates or opens for append. An input read
failure still leaves a created/truncated output. No rollback. Unsupported syntax/
options are preflight rejections, unlike an actual shell that may open outputs
before invoking an invalid utility option. Single-command input/output alias is
allowed: `cat report > report` reads the already-empty file;
GNU `cat report >> report` refuses a nonempty input/output alias (status 1); an
empty alias is harmless. Other filter self-append is unsupported and rejected
before opening; it can depend on buffering in real tools. With pipelines,
source/output alias is rejected before opening because real concurrent shell
ordering is nondeterministic. A failed output open prevents the final stage; no
write or evidence is awarded. The bounded simulator does not model scheduling,
SIGPIPE, buffered partial reads, devices, binary data or OS I/O faults.

Actual writes clear previous stream verification. A completed successful command
may then earn evidence for its final result. Nonzero/errored pipelines cannot earn
successful-outcome evidence, even when their last stage returns 0. Grades inspect
exact final report text; inspection/tool objectives additionally require observed
successful source/output results, not one command transcript. Only the final
visible stage can earn tool evidence; internal stages cannot.
wc observations normalize away the optional filename label but retain -l/-w/-c,
so equivalent paths/stdin work without confusing counting skills. An inspection result
must actually be shown in the console (not merely redirected). Reports can use
any equivalent supported approach. Verification is reset after later writes.

## Bounds and validation

512 command characters, 256 path characters, four stages, 64 initial/128 runtime
nodes, 8 KiB/file, 64 KiB total file text, 32 KiB/stage stdout, 16 KiB displayed
stdout, 16 objectives, 32 hints and 256 KiB pack. Display truncation never changes
filter input or saved report bytes. If a stage exceeds its bound, emit the bounded
UTF-8 prefix plus an explicit simulated-limit error. File/total write limits leave
the fitting UTF-8 prefix written and report failure: never pretend rollback.
These resource failures are simulation boundaries, not complete OS fault emulation.

Packs declare capabilities `virtual-filesystem`, `file-navigation`,
`activity-evidence`, `bounded-text-streams`; domain schema 3: filesystem, cwd,
output_files and lesson. Allowlisted grading: `stream_observed` (tool or pipeline,
source path and exact stdout; wc tool includes its single counting option and
expected count omits the display-only filename), `file_content` (declared output and exact text),
`original_preserved`, `cwd_equals`. Learn steps are parser-validated data;
bounded trusted simulation verifies feasibility. Imported content cannot add code.
Stored observations are objective IDs only, bounded by pack objectives. Historical
pins include the new engine behavior; earlier readers reject unavailable contracts
before restore activation. Existing histories/backup versions are unchanged.

## Internal gate

Before packs: reproducible GNU comparisons (empty/non-newline UTF-8 inputs,
adjacent/separated duplicates, missing fields, quoted delimiters, no matches,
failures, truncation/append/alias) plus permissions, hostile syntax, bounds,
validation, host API sentinels and contracts 1–4 compatibility. Then eight packs,
lifecycle/import/export/backup, installed wheel and UI regression checks. Wider
shell behavior, legacy changes or storage migration require a scope stop.
