# Descriptor enumeration correction

Baseline: `b080d589cfcbd9d6b6f98b8e6280369fa72c3c0e`.
Scope: the shared `Directory.names()` helper, regression tests and isolated acceptance
harnesses. No catalog admission, session, image, backup, launch-policy or QMP change.

## Cause and minimal reproduction

The failed full-size import opened its staging directory while empty, populated it,
then enumerated the same open-file description. `os.listdir(fd)` returned an empty
first listing and all eight members on its second call. The publication guard
correctly refused the mismatch. Both failed stages and their logs remain retained.

On the actual home Btrfs filesystem and `/tmp` tmpfs, a single-threaded probe did:

1. Create an exclusive private directory and open a descriptor while empty.
2. Optionally enumerate it before writes.
3. Create/fsync four files using that descriptor and fsync the directory.
4. List through the original descriptor, a `dup`, a fresh descriptor-relative
   `open(".")`, or an explicit seek followed by listing.
5. Record offsets passively using `/proc/self/fdinfo`, not `lseek`.

| Method | Home Btrfs first listing | tmpfs first listing |
|---|---|---|
| Original open-file description | empty | four members |
| `dup` of original description | empty | four members |
| Independent `open(".", dir_fd=fd)` | four members | four members |
| Seek original, then enumerate | four members | four members |

Prior empty enumeration did not change these results. All observable offsets were
zero before the failing call. Descriptor numbers were reused between independent
fixtures but remained open and bound to the correct inode within each fixture;
there was no concurrent writer. This isolates per-open enumeration state, rather
than FD-number reuse, a nonzero offset, lost files, decompression or a publication
race. Even `lseek(fd, 0, SEEK_CUR)` refreshed that state and masked the failure in
the first diagnostic probe. Passive inspection was necessary.

CPython 3.14's implementation duplicates the supplied FD, uses `fdopendir`, and
rewinds **after** enumeration. The upstream Btrfs implementation captures a
`last_index` at open, shares it through duplicated descriptors, and refreshes it
on seek. That mechanism explains the controlled results. This is a bug in our
assumption that a long-lived directory FD provides fresh enumeration, **not a
claim of a Btrfs defect**. The running kernel is `7.2.5-3-omarchy`; its full source
was not installed, so upstream source is corroboration, not an asserted audit of
the exact running kernel binary.

References:
- [CPython 3.14 posixmodule.c](https://github.com/python/cpython/blob/3.14/Modules/posixmodule.c), `_posix_listdir`.
- [Linux Btrfs inode.c](https://github.com/torvalds/linux/blob/master/fs/btrfs/inode.c), `btrfs_opendir`, `btrfs_dir_llseek`, `btrfs_real_readdir`.

## Narrow correction and security boundary

Each enumeration opens `.` relative to the verified directory FD using
`O_DIRECTORY | O_NOFOLLOW`, giving it an independent open-file description.
It never re-resolves an absolute pathname, follows a link or accesses a parent.
The helper captures device/inode identity when constructed. Before enumeration it
rejects a closed/reused descriptor, changed identity, unsafe type, ownership or
mode. It compares identity and directory metadata before/after opening and listing,
rejecting observed mutation (including a concurrent create/delete or rename).
It rejects duplicate names and closes its temporary FD even on failure.

There is one enumeration and no preferred-result retry. Empty directories remain
legitimate only when actually empty; no member guard is skipped. Metadata checks
are not a filesystem transaction or protection from an attacker with arbitrary
same-user process control. Existing locks, descriptor-relative member opens,
file-identity/hash checks and publication guards remain necessary and unchanged.

All callers reviewed:

- `seal_directory`: first listing now includes freshly written files; regular-file,
  link, hash and identity checks remain unchanged.
- `verify_identity`: still rejects any exact-member mismatch before publication
  and after publication; file substitution remains refused.
- `same_installation`: exact members, full content hashes, receipts and read-only
  base requirements still apply. Legacy directories cannot acquire new receipts
  by an empty-list shortcut or duplicate import.
- `Sessions.require_record`: a missing session record cannot overlook newly created
  retained evidence because the directory was opened before the evidence existed.

No caller relies on a directory cursor being advanced/reset. The new helper leaves
its original descriptor's cursor alone. Existing session bytes and all pins remain
unchanged. The frozen compatibility hash for `files.py` alone was updated; the
other launch/process/runner/image hashes and lifecycle AST guard were retained.

## Regression and evidence

`test_vm_directory_names.py` adds twelve real-filesystem tests: first/repeated
listing, prior enumeration, independent offsets, closed/reused FDs, pathname and
FD substitution, concurrent writers, concurrent readers, exact-member checking,
member identity/symlink rejection and unsafe mode rejection. The mutation test
coordinates a real writer with the real listing; its hook does not fabricate names
or successful checks. All twelve pass on both tmpfs and home Btrfs.

To rerun on a separately chosen private home-filesystem fixture root:

```bash
cd /home/drak/Documents/dlms_lab/app
OLL_ENUM_TEST_ROOT=/home/drak/.local/state/omarchy-learning-lab/recovery \
  python3 -B -m unittest discover -s tests -p test_vm_directory_names.py -v
```

The tests create and clean only their own temporary fixtures. Diagnostic failures,
large import candidates and native evidence are retained separately. The pre-fix
snapshot includes all 300 source/candidate files and was hash-verified:
`/home/drak/.local/state/omarchy-learning-lab/recovery/enumeration-before-fix-20261004T203619671601Z`.
