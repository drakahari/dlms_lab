# System Discovery & Package Fundamentals

**Replacement acceptance:** a separate recipe2 candidate restores the predeclared 204-package set after correcting installer ordering. The old candidate is retained withdrawn; all eight lessons in both modes and the installed-wheel native lifecycle pass on the replacement. See [finalization evidence](discovery-acceptance.md).

Eight manual lessons on the exact **debian13-package-admin-local-v1** image. Select **Real Linux VM preview → System Discovery & Package Fundamentals**. Completion is self-reviewed and unscored. Lesson text is display-only; the app never executes it or verifies learner mastery.

## Sequence

1. Identify distribution, running kernel, CPU and virtual PCI hardware.
2. Correlate loaded modules and built-in drivers, without altering either.
3. Read current-boot events, kernel arguments, target and health separately.
4. Map trusted `/usr/bin/cat` to libc, loader cache and package ownership.
5. Separate installed package state/ownership from dormant archive metadata.
6. Interpret dpkg verification/audit and demonstrate a checksum mismatch on a **learner-owned copy**.
7. Actually install, upgrade, remove and purge two trusted offline fixture packages.
8. Repair a missing dependency and **actual package-owned content**, then verify and clean up.

Prerequisites: Bash quoting/statuses, files/permissions and deliberate guest-only sudo. Choose any lesson; sequence is guidance. Each lesson has Learn steps, independent Challenge outcomes, hints, evidence and cleanup. Start with a fresh lesson disk and enter short commands manually; no clipboard is assumed.

## Real commands and limits

The existing guest probes ran uname/lscpu/lspci, lsmod and absolute `/sbin/modinfo`, journalctl/dmesg/systemctl, ldd and `/sbin/ldconfig -p`, dpkg/dpkg-query/dpkg-deb and APT. `/sbin` is absent from the ordinary learner PATH. `virtio_pci` is built into this kernel: `(builtin)` is not a module filename. USB tooling, readelf, file and debsums are absent; no exercises or coverage are claimed for them. No module loading, boot setting changes, library installation, storage repair, RPM or networking.

Use ldd only on the known trusted program. `ldconfig -p` prints, rather than rebuilds, the loader cache. Merged /usr paths may differ from recorded package paths. A default target does not establish overall boot health, and one warning does not establish a root cause.

`dpkg --verify` compares recorded MD5 content metadata where present; it is not a complete permission check, signature check or security audit. `dpkg --audit` diagnoses package/database state. A checksum on a learner file is not package-owned verification. Lesson8 changes only the declared fixture-owned `/usr/share/ll-discovery/message.txt`, detects the actual mismatch and reinstalls the known archive. Neither an editable database nor a checksum reference authenticates itself.

## Trusted offline fixture and transaction boundary

Two project-owned MIT fixture identities: **ll-discovery-data 1.0-1**, **ll-discovery-report 1.0-1/1.1-1**. Three archives, each <=64KiB, built twice with fixed inputs and compared. The report depends on the data version plus already-installed dash/coreutils. No maintainer scripts, triggers, services, accounts, setuid files or links. Root-owned archives/source under `/opt/learning-lab/package-fixtures` start uninstalled and are not writable by ordinary learner; guest root can override protection.

APT previews and execution use the same guest-root identity, LC_ALL=C, explicit archives, no-download, assume-yes and no-recommends settings, and identical empty local source configuration. **No-download alone does not bound dependency decisions**, and preview is neither execution proof nor a package lock. Inspect every Inst/Conf/Remv/Purg name: only the two fixture identities are permitted. Assume-yes is used only after the reviewed preview and scope check; it is not permission for unrelated operations. The teaching guard rejects any other name; stop on an unexpected or unrecognized proposal. Compare unrelated package state and learner/sudo policy immediately before/after execution. No force, broad autoremove or unrestricted fix-broken operations. APT may suggest autoremove after the repair exercise; that informational suggestion is not an instruction to execute it. Purge each declared fixture explicitly in the shown order.

Native testing found that no-download plus an unstaged local archive fails before installation. Lessons therefore copy the reviewed archives into their own small cache and verify hashes against the protected source before preview. Preview and execution use that same cache. They do not enable fetching, attach media, trust an arbitrary archive or alter global APT sources. The guest has cached DVD indexes, but those are not a guarantee of available payloads.

`dpkg -i` without the declared dependency can unpack files and then fail configuration. It is not an automatic dependency resolver. This guest requires --fix-broken for the deliberately unconfigured state; use it only with the explicit dependency/application archives and the reviewed two-name preview. Supply those archives to the scoped APT operation; verify installed status and real output. Remove retains declared configuration; purge removes it. Root can bypass cooperative teaching guards; this is not a hostile-guest sandbox.

## Recovery and cleanup

Private `/home/learner/ll-discovery-N` workspaces refuse existing entries, links and parent substitution. Require at least64MiB guest free space; evidence/cache stay below256KiB. Inspect exact members before removing only known reports and the three private cache files. The cache cleanup uses guest sudo for those exact names plus its private lock, since copied archives retain read-only mode and APT creates root-owned entries; it never removes global package locks. Remove known reports, then empty directories. Never use recursive/force deletion, globs or unrelated package names. Remove/purge report before data. Retain evidence first; repeat cleanup by inspecting remaining exact items, treating absent ones as already clean.

Keep failed transaction logs and inspect status before repair. Tests interrupt a bounded APT wait **before package-lock acquisition**; they do not establish mid-write/power-loss package recovery. Do not remove lock files or kill unrelated package processes. Existing unclean-disk policy applies: preserve the disk, do not force Resume, and use confirmed retained Reset where required.

VM disks/reports are excluded from profile backups. Resume boots disk state, not RAM/jobs. Existing images/pins stay available; these new lessons never fall back to an older image. Physical-keyboard/accessibility acceptance is separate from native synthesized testing.

## Coverage and release boundary

Official [LPIC-1 v5.0](https://www.lpi.org/our-certifications/exam-101-102-objectives/) and [LPIC-2 v4.5](https://www.lpi.org/our-certifications/exam-201-202-objectives/), checked2026-10-06. Partial101.1 hardware observations,101.2 boot logs,102.3 library discovery,102.4 scoped Debian package information/transactions, and201.3 kernel/module querying. Target observations reinforce101.3/202.1. No full objective claim, RPM, online repository administration, kernel build/runtime alteration or boot/storage recovery claim.

Registry: eight units,68total,16per unit. Retained lessons/default maps:68; separate image/key/release/compatibility limits remain64, with original byte/depth/node limits. Further revisions require deliberate capacity review. Public release stays deferred; unfinished Qt review and ICU signing-key warning remain blockers. Production keys/releases remain empty. See provenance and acceptance reports for exact hashes and evidence.
