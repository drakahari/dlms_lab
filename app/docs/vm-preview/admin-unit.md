# Linux Administration: Services, Logs & Safe Recovery

Library → **Real Linux VM preview…** → **Linux Administration: Services, Logs & Safe
Recovery**. Eight independent sessions, with Learn guidance or Challenge goals and
evidence checklists. Completion is **self-reviewed and unscored**. The application
does not inspect guest work or execute lesson text.

This unit requires the separate `debian13-admin-local-v1` image. Its console logs
in as ordinary `learner`, with the explicitly approved guest sudo rule:

```text
learner ALL=(root) NOPASSWD: ALL
```

This gives full root inside this disposable guest. Root can override every
guest-side resource limit and damage the guest. Password entries remain locked;
there are no owner credentials, SSH service, external NIC, host shares, clipboard,
or remote console. QEMU still runs as the ordinary host user under the unchanged
controller. This is not protection against hostile malware. The original image,
its sixteen lessons, saved pins and sessions remain unprivileged and unchanged.

## Sequence and evidence

| Lesson | Practice and retained evidence |
|---|---|
| Make a controlled administrative change | Identity, sudo, protected-write refusal, quoting, exit status, `&&`, redirection, backup, diff and verified rollback. |
| Manage a local service | Stopped/running state, actual PID/user, restart events and scoped clean Stop. |
| Separate running from enabled at boot | Enable links, changed boot ID and current-boot start evidence; finish disabled/inactive. |
| Repair a broken service override | Effective unit, executable error, preserved drop-in, validation, reload and successful invocation. |
| Restore access for a service account | Locked/non-login identity, root ownership, service-group read and unrelated-user denial; no 777 or root worker. |
| Follow an event through local logs | Facility/priority, journal filtering, local rsyslog rule, validation and correlated new marker. |
| Rotate a lab log safely | Invalid-mode refusal, debug preview, isolated state file, retained record and new-file ownership/mode. |
| Recover an incident and write a handover | Missing configuration, access and startup policy; repair evidence, uncertainty and exact rollback. |

Paths, basic file copying, permissions, text filters, nano and process inspection
are prerequisites. Lesson 1 includes the short shell bridge; advanced scripting
is not required. Reading a supplied compound command does not establish scripting
mastery. Challenge retains necessary scope/cleanup information while hiding the
guided repair and hints. Different valid commands and order are acceptable.

Every lesson starts from its own dormant fixture on a fresh overlay. Resume keeps
changes, so it does not recreate initial faults. All fixtures are present in the
new base with distinct `ll-*` names; no application-side command prepares a lesson.
The bounded helper runs as locked/non-login `ll-service`, reads one data line
(never sources/evaluates it), emits a few lines, and waits at most 120 seconds.
Units set 64 MiB memory, 8 tasks, 20% of one CPU, 1 MiB per-file limits, a 5-second
stop timeout, no restart loop, and guest filesystem restrictions. These do not
limit an administrator who deliberately changes them.

These are the dedicated `ll-*` teaching workers. Standard guest system services,
including journald and rsyslog, retain Debian's normal service privileges; the
worker limits are not claimed for them. The log exercises send only a few records.
Journal size settings are management targets, not a strict aggregate disk quota.

The service can expire while a learner reads instructions. Retain the timestamped
event and restart only the named lab unit if needed. Startup evidence uses a
boot-ID marker and current-boot journal; it does not require catching a short-lived
process. Guest Stop/Resume preserves files, never RAM or shell variables/jobs.

## Scope, rollback and storage

Repairs are limited to lab units, `/etc/learning-lab`, the exact lab drop-in/logging
rule and `/var/log/learning-lab`. Keep copies and validate before applying changes.
Do not edit authentication/PAM, sudoers, essential mounts, bootloaders or networking.
Log inputs are only a few records; journal use is configured to 32 MiB persistent
and 16 MiB runtime targets. The rotation exercise uses its own configuration/state
and retains two archives. Rotation is not an archival backup. No log flood or
storage exhaustion is part of this unit.

To recover, stop only the named unit, restore its saved configuration, validate and
reload/restart as appropriate. A deliberate rollback can restore the original
fault; leave that fixture stopped. Confirmed app Reset creates a clean generation
and retains the previous disk. Unclean disks are preserved and refused for Resume.
VM disks, session records, reports and self-reviews remain excluded from profile
backup and scenario/history export. No backup or session format changed.

## Image defaults and compatibility

The trusted bundled catalog optionally has `default_images`, a complete mapping
from each default lesson ID to an exact descriptor digest. The old catalog form
retains its historical single default. A new explicit mapping must cover all
defaults, refer to retained descriptors and match their exact lesson compatibility
pairs. Missing/null/unknown/incompatible mappings fail; no privileged fallback is
selected. Existing session pins bypass defaults and resolve their original exact
lesson/image versions. No imported VM lessons or image routing are accepted.

Registry limits are **4 units, 16 lessons/unit, 24 total**, with existing 64 KiB
resource, 4096-character text, 32-step and support-list bounds unchanged. Production
release allowlists and signing keys remain empty. The image is a locally reviewed
build, not a distributable release. Stop a guest before rolling the application
back; an older app cannot open lessons/descriptors it never included. Preserve
those records and reinstall a compatible version rather than migrating them.

## Local preparation and disposable launch

See `tools/vm_image/admin/preseed.cfg`, `finish-image.sh` and `prepare.py`. The recipe
installs independently from the signature/hash-verified Debian 13.7.0 amd64 DVD
whose SHA-256 is recorded in [setup](setup.md). It uses existing approved host tools,
normal shared VM exclusion and no guest network. It does not derive from the old
base or a practice overlay. This is a historical build recipe: its inventory
export occurred before later installer hooks completed. Do not describe the
early [admin-packages.tsv](admin-packages.tsv) as the finalized package set or
use this recipe as an approved fresh-release finalization procedure. The exact
216-row set is [admin-finalized-packages.tsv](admin-finalized-packages.tsv).
[Supplemental provenance](admin-finalized-provenance.json) accounts for the late
packages and collected sources/notices without changing the existing image or
its pins. See the [scope and remaining obligations](admin-provenance-remediation.md).

```bash
python3 -B app/tools/vm_image/admin/prepare.py \
  --verified-inputs /path/to/retained/verified-Debian-inputs \
  --destination /path/to/NEW-private-build
```

Independent builds vary in UUIDs/timestamps. Do not reuse a former digest for a
new disk. Review and pin a build before registration. The developer registration
tool accepts only the exact administrator descriptor bundled in this source and
uses the existing containment, collision and durable-publication guards:

```bash
python3 -B app/tools/vm_image/admin/register.py /path/to/exact-reviewed/prepared.raw \
  --vm-home /path/to/NEW-private-test-runtime
```

An arbitrary rebuild will correctly fail that hash check. It does not authorize a
production bundle or add keys. Keep every prior image/generation. Run the source
app with explicit disposable data/config paths and the prepared test runtime:

```bash
cd app
QT_QPA_PLATFORMTHEME='' python3 -B -m learning_lab \
  --data-dir /tmp/learning-lab-admin-review/data \
  --config-dir /tmp/learning-lab-admin-review/config \
  --vm-home /path/to/prepared-test-runtime
```

## Coverage and deferred work

Verified official objectives 2026-10-04: [LPIC-2 v4.5.0, 201/202](https://www.lpi.org/our-certifications/exam-201-202-objectives/),
partial **202.1** systemd service administration; [LPIC-1 v5.0, 101/102](https://www.lpi.org/our-certifications/exam-101-102-objectives/),
partial **108.2** local logs/rotation, **104.5** ownership/access, limited **107.1**
service-account inspection and **101.3** guest reboot. Lesson 1 reinforces basic
shell skills. Full account lifecycle, SysV/targets, GRUB/rescue recovery, remote
logging and complete objectives are not covered. No LPI affiliation is implied.

Next work can address accounts/scheduling and recoverable storage, subject to its
own privileges/packages/device approvals. Networking needs a separate proposal.
Public release and UI polish remain deferred. Existing Qt redistribution review
and the ICU signing-key warning remain open release obligations.
