# Users, Groups & Access Administration

Select **Real Linux preview → Linux Administration: Users, Groups & Access**.
Eight ordered lessons are guidance, not unlock gates. Use the existing, separately
prepared **debian13-admin-local-v1** image; missing content fails without choosing
another image. The core simulated app still needs neither QEMU nor this image.

## Scope and safety

These commands run only in the offline disposable guest. The image already gives
learner passwordless full guest root through sudo; nothing grants host privileges.
Do not modify learner, root, ll-service, sudoers, PAM, host users, networking or
login services. No passwords, keys or credentials are created. New accounts stay
password locked. Guest root can override guest-side safeguards.

Use exactly the displayed `ll-u1`…`ll-u8` fixtures (`ll-u5a`/`ll-u5b` for sharing),
their same-named homes and `/srv/ll-u4`, `/srv/ll-u5`, `/srv/ll-u8`. Setup refuses
existing names/paths. Stop on a collision; inspect the existing fixture or perform
its exact documented cleanup before retrying. Never adopt an unrelated account.
Each lesson uses its own pinned disk. Fresh Start supplies an unchanged image;
Resume retains files and accounts but boots a new OS, not RAM/processes/groups.
Confirmed Reset retains the previous disk. Unclean disks cannot Resume.

Before cleanup, inspect `pgrep -u NAME -a`. Do not delete a user with running
processes or signal an arbitrary PID. Membership practice has one 30-second
holder; wait for its exact launcher. `userdel -r` is restricted in these instructions
to the named disposable accounts and their homes. Delete only the explicitly
listed `/srv/ll-uN` files; use `rmdir` to refuse nonempty directories. Retain your
small learner-owned observations/handover. Interrupted setup requires inspection,
not blind repetition. The app does not execute these display-only lesson commands.

## Sequence and observed evidence

| Lesson | Outcome and retained evidence | Partial objective |
|---|---|---|
| Inspect users and their groups | Database vs process `id`; UID/GID, home, shell, primary vs supplementary groups | 107.1 |
| Create a disposable local account | Explicit home and Bash; real create/read as the account; locked status | 107.1 |
| Refresh group membership safely | Preserve keep with `-aG`; old process groups differ from a fresh process | 107.1 |
| Diagnose ownership and group access | Root-owned group-readable note; intended user reads, cannot write; outsider denied | 104.5; 107.1 reinforcement |
| Build a shared setgid directory | Cross-user append; inherited group on file/subdirectory; outsider denied | 104.5; 107.1 reinforcement |
| Compare creation masks | Files 644/640/600 and directories 755/750/700; existing file and parent mask unchanged | 104.5 |
| Distinguish account restrictions | Separate lock, account expiry, shell restriction and root's explicit execution | 107.1 |
| Repair access and leave a safe handover | Membership, traversal, read/append, inherited new note, outsider denial, exact cleanup | 107.1/104.5 integration |

Learn gives short commands, reasoning and expected observations. Challenge states
independent goals and, where needed, supplies only the initial faulty fixture.
Equivalent narrow solutions are acceptable: review actual access and constraints,
not a transcript. An initial failed read is useful diagnosis, not mandatory
Challenge credit. Completion is **self-reviewed and unscored**; there is no automatic
verification. Mode bits alone are insufficient access evidence. Use real
`sudo runuser -u NAME -- COMMAND` identities; root reading does not prove user access.

## Important distinctions

- `id USER` queries current account/group information. `id` in an existing process
  describes its credentials; a membership edit does not rewrite them. Use a fresh
  login/session, not an unnecessary reboot. `usermod -G` replaces supplementary
  membership; `-aG` preserves unrelated groups.
- Primary-group membership need not appear in the group's member list. Numeric
  IDs are allocated by this guest, not fixed by lesson text.
- Owner/group/other selection uses the owner class first: group bits do not rescue
  an owner lacking owner-read. Check parent-directory traversal too.
- Directory setgid inherits group ownership; it does not itself grant file access.
  GNU chmod may preserve directory setgid on short numeric modes such as 0770;
  inspect the resulting mode and use explicit `chmod g-s` to remove that bit.
  A restrictive umask can still block cooperation. Shared-directory write/search
  permits removing names; this lesson does not install sticky-bit protection.
- umask removes requested bits (`requested & ~mask`), not decimal subtraction.
  Ordinary new files normally request 0666, directories 0777. umask does not change
  existing objects or add execute to a regular file. No default ACL is set here;
  real ACLs/application creation modes can change results elsewhere.
- This pinned Debian guest refuses an expired account through `su`'s account check.
  Root's explicit `runuser -u` still runs a command; its policy differs from `su`.
  A `nologin` shell makes shell-based `su` exit, but root's explicit command does not
  use it. Neither mechanism kills existing processes. Locked status was already L;
  locking again is idempotent, not a demonstrated password login failure. No password
  login, alternative credential, SSH or remote-authentication flow is tested.

## Objective verification and limitations

Verified **2026-10-05** against official [LPIC-1 Exam 101/102 objectives v5.0](https://www.lpi.org/our-certifications/exam-101-102-objectives/):
107.1 local account/group administration and partial 104.5 ownership, group access,
setgid directories and masks. These are partial objectives, not complete LPIC
preparation. Special-file permissions, setuid/sticky policy, password provisioning,
full account lifecycle and additional security cases remain outside this unit.

Official [LPIC-2 Exam 201/202 objectives v4.5 (4.5.0)](https://www.lpi.org/our-certifications/exam-201-202-objectives/)
were also checked. This unit prepares for 210.2 but does **not** implement PAM/SSSD
configuration or LDAP. Existing ACL, remote authentication and security-policy gaps
remain. Original instructional material; no affiliation with LPI is implied.

Behavior references: GNU Coreutils [directory setuid/setgid behavior](https://www.gnu.org/software/coreutils/manual/html_node/Directory-Setuid-and-Setgid.html); Debian's [passwd](https://manpages.debian.org/trixie/passwd/passwd.1.en.html),
[usermod](https://manpages.debian.org/trixie/passwd/usermod.8.en.html),
[runuser](https://manpages.debian.org/trixie/util-linux/runuser.1.en.html) and
[su](https://manpages.debian.org/trixie/util-linux/su.1.en.html) manuals. The image's
actual command results, not a package inventory alone, govern expected observations.

## Compatibility and limits

Only trusted bundled content is read: **5 units, 16 lessons per unit, 44 lessons
total**. Overflow is rejected before reading the overflowing unit's lesson files;
all preexisting string/file/resource limits remain. Original 36 lessons and image
pins are retained. New eight routes explicitly select the administrator descriptor;
no image/controller, launch-policy, process/QMP, disk, session or backup-format
change is part of this batch. Production bundle keys/allowlists remain empty.

VM disks/session records are excluded from profile backups and scenario/history
exports. A restored simulation profile does not restore VM practice. Public release
remains deferred, including outstanding Qt/ICU obligations.

## Disposable source launch

After tests have stopped and the shared VM exclusion is available, use the source
app with new data/config directories and the verified private image store. From
`/home/drak/Documents/dlms_lab/app`:

```bash
review_root=/home/drak/.local/state/omarchy-learning-lab/recovery/users-unit-20261005T181156411096Z
python3 -B -m learning_lab \
  --data-dir "$review_root/owner-review/data" \
  --config-dir "$review_root/owner-review/config" \
  --vm-home "$review_root/runtime"
```

This does not update the installed application or real profile. Select **Real Linux
preview → Linux Administration: Users, Groups & Access**, choose a lesson/mode,
then Start. Stop before changing the active guest; Resume boots the same disk.
The app records only your self-review. Manual testing is optional, not a commit gate.

## Next useful batch (not implemented)

Scheduling and operational automation would build on Bash, services and accounts:
bounded oneshot services, systemd timer schedules, missed-run behavior, evidence and
rollback (partial 107.2). Assess the existing guest tools first; cron/at may require
separately approved packages. Another bounded registry expansion would need explicit
approval. Networking, additional images and public distribution remain deferred.
