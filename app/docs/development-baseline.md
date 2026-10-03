# Development baseline readiness — 2 October 2026

## Result

**Application regression baseline ready; Git baseline unresolved.** The fresh
full suite passed **102 tests** in 0.918 seconds. No application source, pack,
real progress, Git metadata, remote, ownership or security setting was changed.
This audit changed only documentation and new evidence files and created one
additional private recovery copy.

- [Fresh regression log](../evidence/baseline-regression-tests.txt)
- [Recovery verification](../evidence/baseline-recovery-verification.json)
- [Read-only Git inspection](../evidence/baseline-git-inspection.json)
- [Acceptance status and owner checklist](framework-acceptance.md)

## Recovery

The completed snapshot verified successfully:

`/home/drak/.local/state/omarchy-learning-lab/recovery/framework-complete-20261002T233722814659Z`

Its 428 source/evidence files, seven progress files, two configuration files and
specification match the manifest. Verification includes file membership, size,
SHA-256, permissions and modification times. The other existing snapshots also
passed; none was overwritten. All 31 current application files match the
completed source snapshot and the frozen-code proof inventory.

The live profile has advanced since completion: it now has 12 progress files,
including the imported DNS-misdirection pack, its attempt and workspace state.
Gateway current/backup content and selected-lab configuration also changed;
no former files are missing. Their latest modification times predate this
regression run. This audit did not restore or migrate that newer data.

With the app closed and writer lock absent, a new independent recovery copy was
created and verified:

`/home/drak/.local/state/omarchy-learning-lab/recovery/development-baseline-20261002T235012708394Z`

It preserves the newer live progress/configuration as well as source. **Seven
verified snapshots now exist.** The acceptance clarification and this audit
report were written afterward; application source remains identical.

## Exact observed Git cause

The workspace is `/home/drak/Documents/dlms_lab`; the application is in `app/`.
Neither directory yields a Git root. No `.git` is visible in `app/` or its other
ancestors. The workspace's `.git` is a directory, not a gitfile or symlink.

The execution environment mounts that path as:

```text
TARGET:  /home/drak/Documents/dlms_lab/.git
SOURCE:  tmpfs
TYPE:    tmpfs
OPTIONS: ro,nosuid,nodev,relatime,mode=555,uid=1000,gid=1000,...
```

The surrounding workspace is a writable btrfs mount. The effective user and
metadata-directory owner are both UID/GID 1000 (`drak:drak`). The visible `.git`
is empty: `HEAD`, `objects`, `refs`, `config`, `commondir` and `gitdir` are absent.
Git directory/work-tree overrides and discovery overrides are unset.

Both normal discovery and an explicit `--git-dir` probe fail with exit 128.
The direct probe reports:

```text
fatal: not a git repository: '/home/drak/Documents/dlms_lab/.git'
```

**Immediate cause:** Git receives an empty mounted metadata directory rather
than a recognizable repository. Ownership is correct; no `safe.directory`
error occurred. Changing ownership, adding `safe.directory`, or enabling
cross-filesystem discovery would not supply the absent metadata.

**Boundary of certainty:** the mount obscures the underlying host path. This
session cannot establish whether that underlying repository is intact, absent,
or damaged. It does not establish that Git history was deleted. No attempt was
made to bypass the mounted view.

`git remote -v` also fails because no repository can be recognized, and local
`.git/config` is not visible. **The existing remote is unknown, not confirmed
absent.** The recovery snapshots intentionally excluded Git metadata, so they
cannot restore repository history or remote configuration.

## Least-destructive recovery proposal — approval pending

1. First inspect from a normal host terminal, where the repository metadata is
   not hidden by this execution environment. This is an inspection/access step;
   no metadata repair is justified yet. Suggested read-only checks:

   ```bash
   findmnt -T /home/drak/Documents/dlms_lab/.git -o TARGET,SOURCE,FSTYPE,OPTIONS
   stat -c '%U:%G %a %F %n' /home/drak/Documents/dlms_lab/.git
   git -C /home/drak/Documents/dlms_lab rev-parse --show-toplevel --absolute-git-dir
   git -C /home/drak/Documents/dlms_lab/app rev-parse --show-toplevel --absolute-git-dir
   git --no-optional-locks -C /home/drak/Documents/dlms_lab status --short --branch
   git -C /home/drak/Documents/dlms_lab remote -v
   ```

2. If the host repository is healthy, retain it unchanged and use an execution
   environment authorized to access that existing metadata. Recheck its actual
   root, status and remote before any Git write. No initialization or replacement
   should be needed.
3. If the host confirms missing/damaged metadata, preserve any surviving metadata
   before deciding on recovery. Confirm the real repository/remote or a Git
   backup first. A separately approved isolated checkout from a verified source,
   followed by comparison with the preserved working files, is preferable to
   overwriting this tree. Do not guess a remote or invent replacement history.

No repair, initialization, metadata replacement, reset, commit or push was
performed. Approval is requested for the next access/inspection step before
selecting any actual repair based on host-visible evidence.

## Acceptance and next feature gate

The acceptance document now explicitly distinguishes the fresh regression run,
previous native QtTest/geometry evidence, and outstanding owner checks. Native
GUI tests were not rerun during this audit. Physical-keyboard delivery, native
file pickers, owner visual review, continuous mixed-monitor movement and
assistive technology remain outstanding. An imported pack on disk does not
prove a particular input route or successful hands-on acceptance.

The next useful feature gate is one **simulated Linux service troubleshooting**
lab: status, editable configuration and service logs, with final-state checks for
valid configuration, enablement and running state. It should introduce a trusted
service engine and data-only pack, reuse modes/attempts/pinning/history, and work
without requiring a topology or terminal. Real services and host commands must
remain untouched. That would test a second domain; the current networking proof
does not establish this generality. No second-domain implementation began here.
