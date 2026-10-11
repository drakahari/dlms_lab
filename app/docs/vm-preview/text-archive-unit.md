# Text & Archive Tools

Eight real-guest lessons extend the earlier Bash, links/search and backup units.
Use **Real Linux VM preview → Text & Archive Tools → Lesson → Learn/Challenge →
Start**. The existing unprivileged image is required; no administrator-image
fallback. These are display-only instructions. Learning Lab executes neither
lesson text nor imported scripts. Completion is **self-reviewed, unscored**.

Prerequisites: quoting, paths, permissions, ordinary Bash status and array syntax,
small file checksums, earlier backup and separate-destination recovery. The
sequence is guidance, not an unlock requirement. Initial fixtures remain visible
in Challenge; the repair and interpretation must be worked out independently.

| Lesson / stable ID suffix `real-linux-textarchive-` | Distinct outcome | Incorrect/incomplete evidence | Partial objective |
|---|---|---|---|
| `streams` — Route errors without losing their status | Trace descriptor order, save stdout/stderr and producer status7 | A later successful consumer does not erase the failing producer | 103.4 redirection |
| `tee` — Keep partial output and inspect every pipeline stage | tee preserves partial bytes; immediate PIPESTATUS and the owning shell’s pipefail | grep1 differs from input error2; a valid output file is not successful processing | 103.4 pipelines/tee; 105.2 reinforcement |
| `xargs` — Pass awkward filenames without splitting them | Literal NUL-separated spaces/backslashes, bounded batches and empty-input `-r` | Harmless printf demonstrates whitespace splitting; never interpolate names as shell source | 103.3 names/xargs; 103.4 composition |
| `join` — Reconcile sorted records without hiding missing keys | Consistent C locale, checked sort order, join/comm preserve missing keys | Unmatched is UNKNOWN, not zero; duplicates need a separate policy | 103.2 filters |
| `find` — Group a bounded search and batch safe inspections | Prune a declared subtree, group suffixes under `-type f`, inspect with `{} +` | Wrong precedence includes a misleading directory; all queries are read-only | 103.3 find; 103.4 composition |
| `cpio` — Restore a trusted relative newc archive separately | NUL members, exact listing/reference hash, fresh separate restore, contents and modes | A listing or successful exit does not prove the correct bytes | 103.3 cpio |
| `composition` — Reject a valid compressed partial backup | Save failed tar/successful gzip stages, retain candidate, retry separately | gzip validation does not establish archive completeness; failure is not transactional | 103.4; 103.3/105.2 and LPIC-2 206.2 reinforcement |
| `handover` — Recover text evidence and hand over uncertainty | Select correct report by independent expected bytes, retain context and wrong valid candidate | A timestamped filename or ERROR record alone does not prove cause | Transfer/reinforcement, not new objective breadth |

## Bounds and cleanup

Every lesson creates a unique learner-owned mode 0700 HOME workspace, applies a
private umask and records a physical containment guard. Source/restore directory
checks reject substituted symlinks before nested archive I/O. Creation rejects
existing and dangling targets. Cleanup first enumerates exact allowed names and
checks types; unexpected members, failed enumeration and changed types refuse
before removal. It deletes only listed files and removes empty declared
subdirectories, never recursively. Repeated cleanup refuses the missing workspace.

These are **cooperative practice guards**, not race-resistant containment against
hostile guest root. Preserve evidence on refusal; do not bypass it. No arbitrary
archive extraction, devices, parent paths, links or live system targets are taught.
The fixtures contain at most three small source files; the cpio archive and complete tar retry are measured at no more than 64 KiB.
Displayed cpio creation/extraction, tar creation/extraction, find and xargs have
8-second timeouts plus 1-second kill grace. Listing, checksum, gzip tests and
small decompressions operate on these fixed tiny fixtures without a universal
timeout wrapper. Measurement is not a general output quota. The free-space
check is an admission observation, not a guaranteed reserve. No workload or
parallel xargs execution is necessary.

After app reopening, Resume boots the existing disk, not RAM, jobs or variables.
Re-establish the recorded workspace and guard definitions; do not create a new
workspace and silently call it the resumed exercise. VM disks and sessions remain
excluded from profile backup. Reset explicitly retains the old generation and
creates a fresh guest disk; all files in that fresh disk start from the pinned image.

## Honest scope

Active [LPIC-1 v5.0 objectives](https://www.lpi.org/our-certifications/exam-101-102-objectives/)
(101-500/102-500) and [LPIC-2 v4.5.0 objectives](https://www.lpi.org/our-certifications/exam-201-202-objectives/)
(201-450/202-450) were checked 2026-10-11. The LPIC-2 v5 draft is not relabeled
as active. These lessons add narrow tools/composition practice, not complete
objectives, certification readiness, automatic reasoning assessment or LPI endorsement.

GNU [Bash redirection/pipelines](https://www.gnu.org/software/bash/manual/bash.html),
[Findutils/xargs](https://www.gnu.org/software/findutils/manual/html_mono/find.html),
[Coreutils join/comm](https://www.gnu.org/software/coreutils/manual/coreutils.html)
and [cpio](https://www.gnu.org/software/cpio/manual/cpio.html) define real-tool
semantics; the actual guest exercises test the chosen forms. Static simulator GNU
fixtures are separate evidence. cpio 2.15 is available; xz and at are absent and
are not taught or silently replaced.

Physical keyboard, trackpad/wheel, screen-reader and exhaustive accessibility
acceptance remain outstanding. See the batch acceptance report for actual evidence.
