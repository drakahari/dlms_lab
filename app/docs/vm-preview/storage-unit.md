# Linux Storage: Filesystems, Mounts & Safe Maintenance

Eight real-guest lessons, self-reviewed and unscored. Select this unit in **Library → Real Linux VM preview**; choose Learn for the guided steps or Challenge for independent goals. Use the existing administrator image, not the package-administrator image. The app displays instructions: it does not execute lesson commands or verify your guest work.

## Before starting

Prerequisites: Bash quoting/functions/statuses, permissions, scoped backup and deliberate guest-only sudo. Start a fresh disposable lesson disk. Read each guard before using it; stop on any failed identity, space or timeout check. Passwordless root exists inside this guest only. Guest root can bypass these cooperative safeguards.

Use a sufficiently large floating console with fit enabled. No host clipboard or file sharing is available; enter the small commands manually. Longer guard definitions are supplied explicitly rather than hiding execution behind a button. Resume boots the existing disk, not prior shell variables, loop mappings or RAM. After a clean reopen, inspect the exact practice backing files and reconstruct only verified mappings; do not guess a loop number. An unclean session requires confirmed Reset under the existing policy; retain its generation.

## Sequence and evidence

| Lesson | Retain and explain | Objective scope |
|---|---|---|
| 1. Identify storage and protected targets | Boot disk/root mount, free space, permitted regular-file scope; wrong-target refusals | 102.1 introductory preparation; partial104.3/203.1 inspection |
| 2. Plan and partition a disposable image | GPT dump,2048-sector start,245760-sector partition and dynamic loop backing identity | Partial104.1; layout preparation only |
| 3. Create and identify an ext4 filesystem | Filesystem type, label, UUID, block count; distinguish GPT PARTUUID | Partial104.1/104.2/203.2 |
| 4. Mount, use and unmount safely | Actual learner read/ownership, bytes across remount, mounted-check/occupied-target refusal | Partial104.3/203.1; access reinforcement |
| 5. Diagnose permissions and mount-option faults | Separate permission-denied read and read-only write; narrow fixes and unchanged expected content | Partial104.3/203.1;104.5 reinforcement |
| 6. Validate a separate practice fstab | Exact one-entry private table, validation plus actual explicit mount, unchanged live-fstab hash | Partial104.3/203.1; **no boot mounting** |
| 7. Check ext4 offline and repair a preserved copy | Original hash, duplicate UUID refusal, copy-only defect/check/repair/recheck, independent content/metadata/actual access | Partial104.2/203.2 |
| 8. Recover a bounded storage incident | Combine target, checker, mount/access and independent recovery evidence; exact cleanup | Reinforcement/integration of the above |

A successful mount or checker status does not prove file contents or intended-user access. Compare independently written expectations, hashes and owner/group/mode, then read as **learner**, not sudo. The checksum detects changes; it does not authenticate an untrusted source. Repair status1 means corrections; read-only check status4 means uncorrected errors. Inspect logs and status bits, not just whether text appeared. The tested defect is an incorrect inode link count on the offline repair copy; it is not a promise of arbitrary corruption recovery.

## Resource and target boundaries

- Two regular-file disk images maximum per exercise, including the preserved original and repair copy; each <=256 MiB. The supplied guard is stricter: each is exactly128 MiB with one120 MiB GPT partition. No third image, new virtual disk or raw system-disk writes.
- Admission requires1600 MiB free; retain>=1 GiB throughout. This includes512 MiB maximum image-write allowance plus bounded log/notes margin. Refuse insufficient reserve; do not manufacture exhaustion.
- Across eight current lesson workspaces: at most4 GiB image payload plus144 MiB logs/notes including capture temporaries under the declared ceiling (the supplied128 MiB fixtures use at most2 GiB). Historical Learn/Challenge/Reset generations are retained separately; this is **not** an aggregate host quota or a bound on retained VM disks. Monitor host space before Start/Reset using existing admission controls.
- Privileged operations use30s timeout plus2s kill grace and a kernel regular-file growth limit of256 MiB and separately bounded output capture of1 MiB. Image creation/copy is separately timeout-bounded. Logs are overwritten only under fixed private names, never appended; at most16 named log/notes files plus one bounded1 MiB+1-byte capture temporary. A failed/limited operation is not success: preserve files/logs and inspect before retrying.
- Guard the literal lesson workspace and canonical private paths. Preflight every top-level member, including hidden names: admit only the two named images, real mount directory and fixed bounded learner-owned single-link logs/notes. Refuse unknown members, symlinks, hardlinks and oversized files before mutation or cleanup. A backing file must have exactly one loop mapping with matching path **and inode**, zero offset/size limit, and the declared partition parent/number/start/size. Refuse a second alias even if that alias is unmounted. These checks prevent practice mistakes; they are not adversarial protection against guest root or concurrent privileged mutation.
- A mounted-device check alone does not authorize touching a path. `on` requires the verified filesystem root mounted exactly once at the practice mountpoint, with no nested foreign mount. `target_ok` requires an empty, canonical, unmounted directory. Before privileged note changes, verify a regular single-link note at that mount. No recursive deletion or traversal of unknown content is used.
- Copies share UUIDs initially. Uncached discovery must show uniqueness before a UUID mount. The copy exercise rejects duplicates, assigns a new UUID only to the **offline copy**, and uses a verified exact device for recovery. Never mount whichever matching UUID happens to appear first.
- Never run filesystem repair mounted, modify live `/etc/fstab`, use force/lazy unmount, detach all loops, recurse through cleanup or repair the preserved original. The private table uses`noauto`; explicit mounting does not demonstrate boot-mount behavior.

## Cleanup and interruption

Retain observations and the original until verification passes. Unmount only the verified device at the exact practice mountpoint, then detach only its verified loop. Preflight all workspace members and verify no mount or backing-file mapping remains before removing any exact named file or empty directory. A failed loop query is an error, never proof that a file is unmapped. Attachment and cleanup return immediately on a failed precondition. An absent workspace is already clean; an existing workspace with unexpected members must remain for inspection. No glob/recursive deletion, system-disk repair or broad loop detach.

Timeout/interruption coverage is bounded-worker interruption and retained files, not arbitrary mid-write crash repair. If a write is interrupted, keep the copy and logs, check offline, and preserve the original. If app/guest shutdown is unclean, follow confirmed Reset; never force Resume. Profile backups exclude VM disks and guest evidence.

## Honest coverage

Verified2026-10-07 against [LPIC-1 objectives v5.0](https://www.lpi.org/our-certifications/exam-101-102-objectives/) and [LPIC-2 objectives v4.5](https://www.lpi.org/our-certifications/exam-201-202-objectives/). This is partial GPT/ext4/mount/maintenance practice, not complete LPIC preparation. It does not cover swap, MBR, other filesystems, RAID/LVM, quotas, encryption, SMART/physical devices, AutoFS, systemd mount units or boot recovery. Boot/storage infrastructure remains a separate approved scope. Physical-keyboard/accessibility acceptance and Qt/ICU release obligations remain outstanding.

Read-only privileged device queries also use15s timeout plus2s grace. Blank-target probing checks TYPE, PTTYPE and USAGE, not the status of a whole-device probe: GPT partition metadata alone can produce status0 with no filesystem signature. Unexpected status or signature is a refusal, followed by another offline identity check before formatting.

Mount/device queries fail closed: diagnostic errors are not interpreted as an unmounted device or an available mountpoint. The offline gate accepts only a successful mount-list query with a verified device number absent from that list. UUID discovery must succeed and name exactly the verified device.

Challenge also starts from a fresh guest. It requires manual fixture preparation using the preceding skills; the recovery lessons show the bounded copy-only defect creation in Materials. That setup does not perform diagnosis or repair. No practice filesystem or fault is preinstalled, and lesson JSON never runs the setup.

Cloning also retains GPT disk/partition identities. Giving the copy a fresh filesystem UUID does not make its PARTUUID unique: do not substitute a PARTUUID-based mount for the verified exact-device procedure. Filesystem labels are descriptive, not proof of uniqueness.

The private-fstab guard reads the verified partition UUID again and compares the exact table entry to that value; changing a shell variable cannot authorize another source. Query errors are distinct from a proven duplicate UUID. The copy-UUID change requires the expected duplicate result from both verified partitions. Repair and its follow-up check are grouped behind the same successful offline precondition; a failed precondition cannot reach a later recheck or display stale success. Learn and Challenge receive the same guard definitions.
