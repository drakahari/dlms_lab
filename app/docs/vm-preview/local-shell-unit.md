# Local Shell & Filesystem Administration

Ten real-guest lessons, **self-reviewed and unscored**. Library → **Real Linux VM preview…** → **Local Shell & Filesystem Administration** → lesson → Learn or Challenge → Start. This is guest practice, not the simulated terminal. The application displays commands and records your review; it neither runs those commands nor assesses guest state.

## Preparation

Complete the Bash, Regex & Safe File Changes unit, ordinary file permissions, and the scoped sudo/identity introductions before lessons 8–9. Use a disposable lesson disk and enter commands in its native console. Keep fit enabled beside Learning Lab. No clipboard, shared folders or guest network is available.

Lessons 1–7 and 10 use the unchanged **debian13-jobs-local-v1** unprivileged image. Lessons 8–9 use the unchanged **debian13-admin-local-v1** image and its already approved guest-only sudo policy. Missing images are errors, never reasons to substitute the privileged image. Locked/non-login `ll-service` and `nobody` already exist in that image; `runuser` exercises those identities through guest sudo without creating credentials or changing accounts.

## Sequence and evidence

| Lesson / stable suffix (`real-linux-local-…`) | Observable evidence and incorrect approach | Narrow objective scope |
| --- | --- | --- |
| **startup** — Trace shell startup without changing your account | Isolated HOME; login PROFILE but not RC/FALLBACK, interactive non-login RC, clean child neither; actual flags and login_shell. Do not assume every login shell omits .bashrc: a profile can explicitly source it. | Partial 105.1 shell startup files; shell-variable reinforcement |
| **history** — Edit isolated history and verify persistence | Controlled two-entry history, delete the observed obsolete entry, write/reopen the isolated HISTFILE. Clearing memory alone does not clear disk. `history -s` inserts text; it does not execute that command. After an explicit write, the exercise unsets HISTFILE inside that child to prevent a second exit-time save; no parent-shell setting is changed. | Partial 103.1 history inspection/editing |
| **editor** — Choose an editor through a real consumer | Temporary VISUAL=vi and EDITOR=nano passed to `sensible-editor`; actual Vim Tiny opens and saves edited-original, before-copy unchanged. An environment value without a consuming command proves no selection. | Partial 103.8 default editor selection; 105.1 temporary environment reinforcement |
| **hardlinks** — Prove hard-link identity and deletion semantics | Same device/inode, link count two, shared changes/mode; unlink one name leaves content and count one. Independent before-copy retained. Pathnames alone are not identity. | Partial 104.6 hard links |
| **symlinks** — Repair a relative dangling link | `-L` versus `-e`, link text relative to its parent, read from two working directories; original bytes and mode/link count unchanged. Do not rewrite the target or use broad forced replacement. | Partial 104.6 symbolic links |
| **copies** — Choose independent copies instead of shared names | Separate inode for copy, shared inode for alias, deliberate original/alias change versus independent before-copy; `cp -P` retains a symlink while ordinary `cp` dereferences. No ACL/xattr completeness claim. | Partial 104.6; 103.3 reinforcement |
| **search** — Find files and justify filesystem placement | Quoted name/type/size/time criteria in a small model tree; distinguish completed 24-hour `-mtime` buckets and minute-based `-mmin`. Explain model etc, var/log, usr/local/share placements. Do not run destructive find actions or change real /etc. | Partial 103.3 find; partial 104.7 FHS interpretation |
| **sticky** — Separate shared-directory writing from deletion | Actual nobody uses an existing-file GNU dd append on ll-service's writable file but cannot unlink it; file owner and directory owner can unlink. Immediate return status and surviving file prove the denial. Root is an exception. | Partial 104.5 sticky semantics |
| **priority** — Audit special bits and verify a scoped priority change | Read-only /usr/bin audit; owned sleep PID/start identity; actual niceness 5, denied unprivileged return to 0, approved guest-root return to 0. Nice values are not a CPU allocation guarantee. No executable setuid fixture is created. | Partial 110.1 special-bit audit; 103.6 existing-process priority, 104.5 awareness |
| **handover** — Repair links and deliver an independent handover | Repair wrong relative link and unsafe hard-linked copy; preserve source checksum/mode/link count and stale original, distinct handover inode/mode, factual report and explanatory review. | Reinforcement/independent transfer of 104.6/104.7; not a new complete objective |

Challenge shows initial fixture materials and independent outcomes; it hides the Learn command walkthrough and hints. The application does not prepare faults. Set up the declared small fixture manually, then choose an equivalent valid repair/inspection sequence. Learn's demonstrated reference solution is not an automatic transcript requirement. There is no automatic meaning/causal grading of your explanation.

## Scope, collision guards and cleanup

Every lesson creates a **unique learner-owned private workspace** with its exact `local-<lesson>.XXXXXX` prefix, directly under the guest learner HOME. `here` checks physical location, direct parent, ownership/mode and no symlink; `fresh` refuses existing and dangling names. Read and retain the exact path. Do not substitute another lesson's workspace.

The displayed `clean_local` preflights exact members and expected regular-file/directory/link types before deleting named files. Unexpected members, substituted directories, and failed enumeration are refusals: retain the workspace for inspection. No recursive deletion, broad globs or shared-account edits. Copies deliberately changed during hard-link demonstrations are distinguished from protected before-copies.

Sticky practice uses one unique `/tmp/ll-sticky.XXXXXX` directory, exact a/b names and an additional `sg` guard: direct /tmp parent, real directory, learner:1777, regular non-symlink single-link files at most 1 KiB, successful enumeration and no unknown members. This is not an authentication exercise. The guard stops on any failed containment/query check.

The pinned guest has `fs.protected_regular=2`. Shell `>>` opens with O_CREAT and is additionally refused for another user's file in this sticky directory. The lesson uses bounded GNU `dd` with append/nofollow, notrunc and nocreat to write only its known existing regular file; it verifies exact contents, owner/mode and refused unlink separately. A missing target stays absent. No kernel policy is changed. This is GNU-specific, not a general portable-shell interface. [Kernel protection](https://docs.kernel.org/admin-guide/sysctl/fs.html#protected-regular) and [GNU dd flags](https://www.gnu.org/software/coreutils/manual/html_node/dd-invocation.html).

Priority practice uses one **sleep 120** task, no CPU worker. Check learner UID, command and /proc start identity before every renice/signal. Capture a dynamic PID, never use a fixed PID, broad kill or stale job number. If the task has already expired, do not target another process; repeat only the bounded practice task if needed. Terminate and wait for that exact owned task.

These checks prevent ordinary practice mistakes; they are **not a race-resistant sandbox against guest root**. The existing host controller maintains the separate host boundary. Guest root can bypass guest checks and permissions. No host account, permissions, authentication, controller or image changes are part of this unit.

## Interruption, reopening and review

A clean Stop followed by Resume boots the same disk; it does not restore RAM, shell variables, functions, jobs or editor state. Reconstruct only the recorded workspace and guard definitions after confirming their identity. Do not rerun `mktemp` and pretend it is the old workspace. Preserve originals and observations until your review passes. If an operation or cleanup refuses, inspect its status and retained files before retrying. Unclean disks use the existing confirmed Reset path; never force Resume. Reset retains the old generation. VM disks/evidence are excluded from profile backups.

The fixtures are small (individual supplied records below 1 KiB); no load, disk-exhaustion, process-exhaustion or broad system audit is required. Historical disk generations are retained separately and are not a unit-wide storage quota. The native test harness also checks unexpected names, types, path substitution, failed queries, incorrect/incomplete outcomes and actual identities; it is developer acceptance, **not runtime learner assessment**.

## Coverage and remaining breadth

[Official LPIC-1 objectives](https://www.lpi.org/our-certifications/exam-101-102-objectives/), **version 5.0, exams 101-500/102-500**, rechecked 2026-10-11. These are original partial exercises with no LPI affiliation. They add real link practice previously missing, isolated history/startup/editor practice, find/FHS breadth, sticky access and scoped priority/audit evidence. They do not complete any whole objective: cross-filesystem hard-link limits, broader FHS/locate/updatedb, persistent account customization, Emacs/platform selection, special-file/setuid execution, ACLs or comprehensive security administration remain outside this batch. Lessons 11–12 were omitted because further variations would repeat these outcomes.

Physical-keyboard, wheel/trackpad and assistive-technology checks remain outstanding. Native automated input and offscreen rendering are separately recorded in [acceptance](local-shell-acceptance.md). The diagnosed upstream PySide shutdown warning is unchanged; public release and Qt/ICU obligations remain deferred.
