# Backup & Safe File Recovery

Eight manual lessons on the existing approved administrator image. Choose **Real Linux VM preview → Backup & Safe File Recovery**. Completion is **self-reviewed**, unscored; the app does not execute lesson JSON or inspect guest outcomes automatically.

## Sequence and prerequisites

1. Define recovery requirements: exact members, byte contents, modes, owner/group, timestamps, RPO and RTO.
2. Create and inspect a scoped relative-member tar archive.
3. Retain raw/compressed backups and an independently preserved checksum reference.
4. Diagnose a truncated stream and a well-formed archive with altered payload.
5. Restore separately, compare bytes/metadata and detect an incomplete archive.
6. Repair ownership/access and actually read as the intended disposable identity.
7. Select the right recovery point while retaining both backups and current source.
8. Independently recover a private earlier version and write an evidence handover.

Prerequisites: Bash quoting and exit statuses, file ownership/modes, privileged guest-only identity switching. The approved guest has GNU tar 1.35, gzip 1.13 and coreutils 9.7; actual runtime probes and results are recorded in [acceptance](backup-acceptance.md). No new packages, credentials, networking or image changes.

## Practice boundary and command semantics

Each fresh lesson uses its exact `/home/learner/ll-backup-N` directory. Creation refuses existing paths, including dangling symlinks. `guard` checks physical location, learner ownership and absence of links before mutation. Stop on a failed guard or unexpected member. These are cooperative practice safeguards, not a general hostile-archive extractor. Trusted fixtures contain only two small regular files; do not introduce absolute/parent members, links, devices or arbitrary archives.

`tar -cf FILE -C source -- note.txt 'space name.txt'` stores explicit relative members. `tar -tf` and `-tvf` inspect member names and header metadata. `tar -xf FILE -C restore --no-same-owner --same-permissions` extracts only our known archive into a **new empty, separate** directory, restores file modes, and leaves ownership with the extracting learner. Lesson 6 deliberately shows that ownership may require a declared, narrowly scoped guest-root repair; `runuser -- cat` tests actual access, not authentication.

`gzip -c` retains the input; `gzip -t` checks stream/trailer integrity. `sha256sum -c` compares against an independently retained reference. `cmp`, exact inventory and `stat` compare expected bytes and relevant metadata. Neither a tar listing nor valid gzip CRC proves intended contents. Hash equality does not authenticate an editable or untrusted reference. RPO specifies acceptable data loss; RTO specifies a recovery-time target. This small practice has no measured production recovery-time guarantee. The reference lives separately from the archive in this guest for demonstration; it is not a separate-device disaster backup. Real operations need independently protected reference material and an appropriate recovery failure domain.

## Bounds, collision handling and cleanup

Fixtures contain less than 256 KiB of disk allocation; each archive/compressed payload must be <=64 KiB. Archive/compression operations use `timeout -k 1s 10s`; timeout or nonzero status requires inspection, not an assumed success. Admission checks for at least 64 MiB guest free space are observations, not hard quotas/reserve guarantees. Guest root can override guest-side limits.

Do not reuse a destination, overwrite a backup or extract over source/system configuration. On interruption retain the candidate, inspect it and create a **different** named retry. Cleanup uses exact quoted file names, then `rmdir`; never recursive/force deletion or globs. Inspect the inventory first; unexpected members stop cleanup. Repeat by checking which exact items remain. Lessons 6/8 save the existing shell umask, use 077 for private backup/reference creation, explicitly protect the root-created archive, and restore the saved umask during cleanup. They use only locked, non-login `ll-b6`/`ll-b8` accounts and remove them after their files and processes are gone. Learner/root accounts and sudo policy remain untouched. Keep originals and backups until the recovery review is complete; cleanup is a separate deliberate final step.

## Coverage and omissions

Verified against [LPIC-1 objectives v5.0, exams 101-500/102-500](https://www.lpi.org/our-certifications/exam-101-102-objectives/) and [LPIC-2 objectives v4.5, exams 201-450/202-450](https://www.lpi.org/our-certifications/exam-201-202-objectives/) on 2026-10-06. Demonstrates **partial 103.3** (tar/gzip file management) and **partial 206.2** (manual backup, integrity checks and restoration), reinforcing 104.5 ownership/permissions. It does not cover full objectives, ACLs/xattrs, rsync, cpio, tape/media rotation, remote backup, backup suites, authentication/signatures or production recovery architecture.

VM disks and guest reports are excluded from profile backups. Retain observations before confirmed Reset; Resume boots retained disk state, not RAM/jobs. Physical keyboard, accessibility and exhaustive owner-driven native scaling checks remain outstanding. Public release remains deferred, including the unresolved Qt review and ICU signing-key warning.
