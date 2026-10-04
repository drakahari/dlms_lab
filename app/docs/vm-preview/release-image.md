# Fresh release-image preparation — proposed procedure

This is a procedure/checklist for a future authorized build, not a completed public
candidate. The existing `debian13-jobs-local-v1` image and test bundles remain local
preview evidence. Do not derive a distributable image from them, an owner proof
disk, practice overlay, credentials or history. No new image was built in this batch.
See [distribution readiness](../distribution-readiness.md) for source/notice gaps.

## Preparation inputs and build

1. Approve one exact official Debian stable amd64 installation ISO/repository
   snapshot, source closure and target Omarchy/QEMU requirements. Reverify the
   checksum signature against independently established Debian fingerprints and
   the entire ISO hash. If choosing a newer release than the existing pinned DVD,
   review the recipe pin change first. Never resolve `current` silently.
2. Use a new private build directory with free-space admission for ISO, a 16-GiB
   raw image, source set and disposable generations. Preserve old builds/evidence.
   Record host versions, recipe commit and file hashes, ISO/signature/key hashes,
   package component/architecture/version and binary/source hashes. No privileged
   host installation or service/group/security change belongs to image building.
3. Review the existing `tools/vm_image/prepare.py`, `preseed.cfg` and
   `finish-image.sh` before using them as a starting recipe. They install from
   scratch offline, with no network/share. Run the normal-user build under normal
   VM exclusion only when no guest is active. Do not overwrite coordination records.
   A repeatable recipe is not a demonstrated byte-for-byte reproducible image:
   UUIDs, timestamps, package-generated identity and build logs must be documented.
4. Keep the approved policy: unprivileged `learner`, console-only tty1 autologin,
   locked root/learner password entries, no sudo entitlement, no SSH/remote login,
   no extra capabilities/groups. Retain Debian notices and common-license files.
   Guest-specific preparation scripts must be supplied as corresponding modified
   configuration/build material, with exact hashes and descriptions.
5. Capture a fresh package inventory with binary/source names and versions,
   Built-Using and Static-Built-Using closure, notices and changes. Include the
   unsigned Linux source behind signed-kernel packaging. Recompute this on the
   candidate; today's 199 packages/189 sources are a local-test-image snapshot.
   Retain exact Debian patches/original source and required non-code notices.
6. Before clean shutdown, remove installer history and temporary preparation
   scripts, root/learner command histories, logs containing build paths/state,
   random seed and machine identity using a reviewed guest-only procedure. Inspect
   authorized keys, SSH keys/services, sudoers, supplementary groups, environment,
   home files, cached packages/repository paths and temporary files. Never clear
   required notices. The current recipe removes some state; that alone does not
   prove a full release scrub. Document expected clean files and exact deltas.
7. Cleanly shut down; verify the actual QEMU process ended. Hash the whole raw
   disk and make the base read-only. Record logical size, allocated/compressed size
   and package/recipe/notice/source-inventory digests. Never clean or test the base
   by booting it writable. All lesson checks use unique disposable overlays.
8. After licensing and acceptance review, define a new image identity/revision
   and exact immutable descriptor/manifest digest. Keep the original image and
   lesson descriptors accessible to old sessions. Sign and add a release allowlist
   only under separate authorization; no matching-name/signature-only admission.
   Package only the bounded six-member offline format accepted by the existing
   importer; corresponding-source sets are separate artifacts, not extra ZIP members.

## Acceptance checklist (all outstanding for a fresh public candidate)

- Verify approved guest policy, tool versions, no personal credentials/history,
  no remote-login service/listener, and notices retained. The guest has no external
  network interface; QEMU launch has no host shares, clipboard, USB/raw devices or
  listening console ports. Run QEMU as the normal user. This is not a claim of
  hostile-malware containment. Test from a new installation without owner data.
- Test all eight lessons on disposable overlays: **Identify your processes**;
  **Move between foreground and background**; **Manage a background job**;
  **Signal the intended process**; **Read a live process view**;
  **Keep work running after logout**; **Adjust process priorities safely**;
  **Process handover practice**. Use bounded owned processes and actual PIDs/job
  identifiers. Verify STOP/CONT/TERM and scoped selection, top/watch observations,
  huponexit-off default and practice-shell-only huponexit experiment, nohup/disown
  after logout, actual NI after accepted/denied changes (nice may still execute),
  and cleanup. No new privileges/packages to make lessons pass silently.
- Verify completion stays **self-reviewed, no verification score**. Guidance step
  clicks are not guest verification. Logout survival is distinct from reboot;
  Resume boots the existing disk and does not restore RAM/jobs/processes.
- Build/install the application wheel into a new user-local test environment
  outside the checkout; test all packaged resources, prerequisite errors, core
  simulation startup without QEMU/image, native GTK launch beside the Lab in
  800×600 fit mode, accessible controls and honest manual-zoom limitations.
  Native keyboard/accessibility/scaling checks need actual evidence, not offscreen
  substitution. Use only approved existing tools or obtain specific permission.
- Test Start, verified clean Stop, application close/reopen and disk Resume;
  switching lessons while running; no second VM across profiles; exact lesson,
  image and mode associations. Test new sessions and an unchanged old pinned
  preview session from disposable copies, including app rollback. Missing or
  incompatible files must fail clearly without choosing a different image.
- Marker persists across clean reboot/Stop/Resume; confirmed Reset creates a new
  generation, marker disappears, previous generation remains intact and base hash
  is unchanged. Test interrupted operations, crash/unclean Resume refusal, forged
  process records, unavailable/withdrawn pins and verified Stop routing with a real
  native guest. Preserve recovery evidence; do not replace tests with force-stop.
- Verify symlink/substitution/backing-chain/external-data rejection, private
  allowlisted QMP/process identity, per-file disk ceiling and ENOSPC failures,
  admission/monitoring behavior and unique durable generation publication. No
  aggregate quota/free-space guarantee. Run the existing security regressions.
- Validate/import an actual full-size signed candidate with isolated preparation
  trust first; check exact size/hash, damaged/truncated/tampered cases, conflicts,
  duplicate no-op and interrupted publication. Production importer must still reject
  test trust. A candidate cannot be admitted until its production trust/manifest
  is separately reviewed and approved. Offline sources need an accompanying
  inventory/hashes and retrieval test.
- Profile backup round trips preserve simulation data while explicitly excluding
  VM disks/sessions/self-review records. Do not claim a backup restores a missing VM.
  Keep updates/rollback from rewriting old pins, disks or retained generations.
- On another disposable Omarchy test installation, complete the entire installed
  workflow: install app, check/approve prerequisites, verify/import candidate,
  choose lesson, Start, practice, Stop, Resume, Reset and reopen. Leave owner
  installation/profiles/images/active guest untouched. Record exact versions,
  evidence, limits and failures before asking to publish.

## Distribution and retention

Supply an exact license/source inventory, original Debian source and patch files,
project preparation modifications and applicable notices alongside the image.
Provide offline source delivery or a license-compliant alternative after review;
a package list/upstream link alone is insufficient. Measure final asset sizes and
retain immutable source/image/lesson revisions for existing recipients and pins.
Image updates require a new reviewed release; no automatic migration or deletion.
Hosting, key custody/recovery and independent fingerprint verification are owner
choices described in the readiness report. No key, upload or production admission
is created by this procedure. It does not authorize a future host-package upgrade.
