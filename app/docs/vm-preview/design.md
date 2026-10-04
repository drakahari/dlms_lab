# Optional local VM preview — implementation boundary

This preview is separate from the trusted simulated engines. Learner commands are
entered in QEMU's native GTK console and execute only in the guest. No commands,
paths, scripts, QEMU options or VM lessons are accepted from imported scenario JSON.
The core application has no QEMU package dependency and continues to run simulations
without KVM, QEMU or a prepared image. Setup is explicit; no privileged installer runs.

## Scope and trust

One bundled lesson, **Manage a background job**, supports Learn guidance and
Challenge, with **self-reviewed completion**, no score and no guest assessment.
Guidance advancement is a learner action, not evidence of command execution.
QMP is controller-only: status/identity queries, ACPI shutdown, pause on storage
pressure, and explicitly confirmed force quit. No HMP, guest commands, file transfer,
migration, hotplug or user-supplied QMP. Developer fixtures are separate from runtime.

A fixed 2-vCPU, 2-GiB, legacy-BIOS guest has one 16-GiB virtual disk, no NIC, no host
shares, serial backend, listening TCP console, clipboard or passthrough. GTK uses the
local desktop. QEMU runs as the current ordinary user. This reduces exposure; it is
**not a sandbox for hostile malware** or protection against a compromised same-user
host process. QEMU/kernel/GTK vulnerabilities remain relevant. No remote login or
privileged learner account is provisioned. No password is requested or saved.

## Containment and lifecycle

Storage is opened component-by-component with directory descriptors and NOFOLLOW.
Files must be regular, owned, singly linked and not group/world writable; directories
are private. QEMU receives already opened base/overlay descriptors through fdsets.
The base is raw, read-only and SHA-256 checked before every Start/Reset. Overlays
must be bounded qcow2 v3 with the narrowly supported header/features and **no embedded
backing path**. The controller supplies the entire block graph explicitly, including
the raw base node. qemu-img only checks; it never repairs/rebases/commits disks.

A per-user runtime operation lock serializes controllers across profiles and VM
roots. QEMU inherits a separate lifetime lock, so an app crash does not allow a
second launch or Reset. PID, host boot ID, start ticks, executable inode, command-line
digest, peer credentials and QMP UUID identify a process. Both normal control and interrupted launch adoption require exact trusted argv
reconstruction. A missing or terminal record does not establish that the lifetime
lock is free. A missing socket is not
proof of exit. Unverifiable ownership stops control actions without signaling a PID.

Each Reset creates a new random generation directory with exclusive creation,
fsyncs disk/metadata/directories, then atomically publishes current.json. Prior
metadata is retained under a unique name; prior disks never move or get overwritten.
Interrupted publication leaves the previous generation active or the new one fully
published; orphan/staged evidence is retained. No automatic deletion or repair.
Resume boots the existing disk: **RAM, processes and shell jobs are not resumed**.
Clean Stop requires guest shutdown evidence and process exit. Failed shutdown offers
explicit force-stop confirmation; the disk is marked unclean and retained. A durable per-generation lifecycle journal also survives host reboot. An unclean or
interrupted generation blocks Resume so its evidence is not modified. A failed
read-only consistency check also blocks Resume. Reset can create a new session without
claiming the old disk is repaired. Closing the app may leave QEMU running, explicitly
disclosed; reopen the same profile for controls. GTK window close may be unclean.

## Storage limits

The QEMU child has an inherited **18-GiB per-file RLIMIT_FSIZE**, covering overlay
file extent (and any output file). SIGXFSZ is ignored in that child so EFBIG reaches
QEMU; werror=stop pauses guest I/O. This was exercised with a lower ceiling on a real
disposable guest, not inferred from a mock. The virtual disk is 16 GiB; qcow metadata
has headroom. New Start/Reset admits only with 22 GiB available disk and 3 GiB available
RAM. While the preview page is open, periodic checks pause a running VM below 4 GiB
free or near its file ceiling. This is **best-effort monitoring**, not an aggregate
quota, allocation reservation, or guaranteed free-space reserve. Other writers and
retained generations can exhaust the filesystem. ENOSPC/error leaves evidence intact.
No automatic retention pruning. The owner must manage space separately while stopped.

## Separate records and backups

Default VM root: ~/.local/share/learning-lab-vm/preview-v1 (explicit --vm-home for
isolated tests). Per-profile key hashes the absolute app data/config locations.
Moving/restoring a profile to other locations creates a different VM binding.
VM root holds image digests, per-profile version-pinned session metadata, guidance,
hint use and self-review, and unique disk generations. Runtime records/sockets/logs
are under /run/user/UID/oll-vm-preview. Bases and all generations are retained.

**Current profile backup, scenario export and history export exclude all VM sessions,
completion records and disks.** There is no VM export/import and no backup schema
change. Restored simulation profiles do not acquire a missing VM disk or completion.
The preview warns before Start and in existing backup UI. An unavailable exact
lesson/image/backend is preserved and refused, not silently upgraded. Old image
versions are never automatically removed. No personal profile was migrated.

### Complete writable-state inventory

- `profiles/<binding>/generations/<uuid>/disk.qcow2`: the only persistent guest-writable
  state. Reset selects a new empty overlay over the same verified base.
- Generation `origin.json` and `lifecycle.json`, profile `current.json` and uniquely
  named `retained-*.json`: controller-owned metadata. Retained records are never
  interpreted as the active reference.
- `/run/user/UID/oll-vm-preview/`: operation/lifetime locks, running.json, unique run
  directories, private QMP socket and qemu.log. These are runtime records, not guest
  disks; the durable generation journal survives their loss on host reboot.
- No RAM snapshot, writable firmware/NVRAM, TPM, auxiliary disk, host share, serial
  file or network state exists in the launched guest. The pinned raw base is opened
  read-only. Image-builder logs/files are separate and are never active VM state.

Missing journals fail closed, including when the runtime directory is lost. Reset
retains that generation rather than attempting to infer or repair it. Existing
uncommitted development fixtures predating a tightened pin/journal can be refused;
they are intentionally preserved, not migrated into usable sessions.
