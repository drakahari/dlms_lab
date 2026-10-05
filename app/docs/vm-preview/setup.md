# Local image preparation and preview launch

The separate [Services, Logs & Safe Recovery unit](admin-unit.md) uses its own
administrator image and explicit lesson/image mappings. The original image and
unprivileged recipe below remain unchanged.

The simulator installation is unchanged. QEMU remains an optional, separately
approved host prerequisite; the app does not install packages or change groups,
services, networking, authentication or desktop settings. This recipe is for a
reviewed **local build**, not a signed public image release or a VM image importer.

## Inputs and reproducibility

Reviewed Debian stable amd64 DVD: **Debian 13.7.0**, downloaded from
https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/debian-13.7.0-amd64-DVD-1.iso
with SHA256SUMS and SHA256SUMS.sign from that directory. Follow Debian's procedure:
https://www.debian.org/CD/verify

Pinned ISO SHA-256:
`347b6c67a3cc0b7ddb60b178f683470c4e2b7ac426c996d9337a2ff36c1a32d2`

Signing fingerprint:
`DF9B9C49EAA9298432589D76DA87E80D6294BE9B` (Debian CD signing key).
The builder rechecks the signed checksum and full ISO hash. `current` changes;
never substitute a different filename/version without a new review and pin. Keep
the verified inputs for offline rebuilds. No download or guest network is performed
by the builder. Required existing host tools: QEMU x86/KVM, qemu-img, bsdtar, cpio,
gpgv and Python. Missing prerequisites require separate approval, not auto-install.

From the repository root, using a **new** destination beneath the dedicated VM root:

```bash
python3 -B app/tools/vm_image/prepare.py \
  --verified-inputs /home/drak/.local/share/learning-lab-vm/debian-verification-20261003T192431 \
  --destination /home/drak/.local/share/learning-lab-vm/NEW-REVIEWED-BUILD
```

This installs from scratch, with reviewed preseed/initramfs additions, no host
shares/NIC and no personal proof disk. It writes a sparse 16-GiB raw disk, a recipe
hash/argv record, installer logs, exact package/version inventory and image hash.
Guest-only preparation locks root and learner passwords, removes any sudo/SSH
server, restricts learner supplementary groups, enables tty1 unprivileged autologin,
and removes installation history/machine identity. D-Bus/libpam-systemd support
logind's clean ACPI shutdown. Root is not accessible to the learner. Autologin is
console-only, not a remote service. This is a repeatable preparation **procedure**;
filesystem UUIDs/timestamps make independent builds non-bit-identical. Each actual
build must be reviewed/tested and pinned by its full digest; never pretend a rebuild
has the previous identity.

Package copyright/licence notices remain inside `/usr/share/doc/*/copyright`.
The local build inventory is retained with the image and committed as documentation.
Before public distribution, review every included package's redistribution/source
obligations, preserve notices, publish matching source/provenance and sign a release
manifest. None of that public release work is claimed complete here. No owner proof
image, credentials or history may be included. No image has been uploaded.

## Reviewed local image

Build directory: `/home/drak/.local/share/learning-lab-vm/preview-image-20261004T0209`

Image SHA-256:
`a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d`

After review, `image.json` pins the approved output. The explicit registration tool
accepts **only that exact hash/size**, requires a new digest directory and refuses
replacement. It copies sparse extents and verifies the copy. The tool has already
registered this build in `preview-v1`; do not rerun it over that existing directory.

```bash
python3 -B app/tools/register_vm_image.py /path/to/reviewed/prepared.raw \
  --vm-home /home/drak/.local/share/learning-lab-vm/preview-v1
```

Images are raw/read-only. Unique qcow2 generation files have no embedded backing
filename; only the trusted controller supplies the pinned raw backing descriptor.
Updates retain old images/generations, and an incompatible pin fails closed. There
is no automatic image update, garbage collection, disk export or image download.

## Disposable app review (does not update the installed app)

Run from `app/`, with the existing Python/PySide6 environment:

```bash
QT_QPA_PLATFORMTHEME='' python3 -B -m learning_lab \
  --data-dir /tmp/learning-lab-vm-owner-review/data \
  --config-dir /tmp/learning-lab-vm-owner-review/config \
  --vm-home /home/drak/.local/share/learning-lab-vm/preview-v1
```

Library → **Real Linux VM preview…** → choose a collection and lesson → choose Learn → **Start**.
The [Processes, Jobs & Priorities](processes-unit.md) and
[Resource Diagnosis & Capacity Evidence](resource-unit.md) units share the same
optional unprivileged image. The separate [Services, Logs & Safe Recovery](admin-unit.md)
unit requires its exact administrator image; it is never substituted for an old lesson.
All use the unchanged controller; each lesson retains its own pinned session. Type commands
in the separate native GTK console. The app's guidance is not a command runner.
Use **Stop** for clean guest shutdown, then **Resume disk** for the same files.
Reset is enabled only while stopped and requires confirmation; choose the new mode
in that confirmation. Reset retains the prior generation and self-review metadata.
On an unclean/interrupted generation Resume is refused to preserve evidence; Reset
creates a fresh disk. A control error never authorizes killing an arbitrary PID.

Self-review records no verification score. Closing the app offers a warning before
leaving a guest running. Reopen the same profile for controls. Files and all VM
session records are excluded from simulation profile backups/exports; moving a
profile does not move its VM. Recovery generations must be managed manually while
stopped; no deletion is performed by this preview. Keep at least 22 GiB free before
starting; this check and monitoring do not reserve space or cap aggregate usage.

## Native console display

New graphical launches use a readable 800×600 VGA mode with aspect-preserving
Zoom To Fit. Manual Zoom In/Out disables fit and is not persisted across QEMU
processes. Keep View → Zoom To Fit enabled beside the Lab. For manual zoom, use
a sufficiently large floating window; undersized tiles can distort the console
and menu targets. Reopening returns to fit; the manual percentage is not saved.
See [display behavior and native verification](display.md).
No global scaling, guest image, privileges or isolation settings are changed.
