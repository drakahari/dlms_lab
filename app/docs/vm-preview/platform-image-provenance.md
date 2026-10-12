# Two offline platform candidates: provenance and policy

These are independently prepared **local development candidates**, not public
releases. Production signing keys and release admission remain empty. Existing
images, including the older administrator image’s historical204/final216 package
inventory record, have not been rebuilt, replaced or repinned.

The [machine-readable evidence index](platform-image-provenance.json) binds
final raw/inventory hashes and retained source-verification manifests. Exact
inventories and acquisition manifests are in `tools/vm_image/foundation/` and
`tools/vm_image/rpm/`. Large ISOs, RPMs/debs, source archives, notices, disks and
private test records stay outside Git in the named recovery directory.

## Debian foundation

Debian13.7.0 amd64 DVD1 was authenticated using Debian’s signed SHA256SUMS and
pinned hash347b6c67a3cc0b7ddb60b178f683470c4e2b7ac426c996d9337a2ff36c1a32d2.
Build used the corrected independent installer/finalization sequence, never a
practice overlay. Installer exit is not inventory publication: a separate
bounded normal finalization boot finishes installation, captures the exact206
package TSV, shuts down, and only then hashes/protects the base. Normal-boot
inventory independently matched it.

Approved changes are xz-utils/liblzma5 5.8.1-1+deb13u2 and at3.2.5-2.2, including
at’s declared helpers/spool/PAM definitions and guest-only atd activation.
Recommends are disabled. en_US.UTF-8/de_DE.UTF-8 are generated; root and learner
passwords remain locked, console autologin and root-only passwordless learner
sudo remain the approved disposable-guest model. The existing locked practice
identities are used; no password creation or remote authentication service.
Exact authenticated binary/source metadata and hashes are retained.127 required
source versions reuse verified retained materials plus exact new at/xz sources;
this is retention evidence, not blanket legal clearance.

## Alma learner and separate builder

AlmaLinux9.8 x86_64 minimal ISO is pinned to
7762a4b45a66235726db145a573658964bf77bf7b9bc1c018afe86a4cf37cc2e;
vendor signer BF18AC2876178908D6E71267D36CB86CB86B3716. Metadata, full selected
RPM content signatures and exact hashes were authenticated before dependent
builds. Final software inventories190 learner/283 builder (excluding the separately
validated RPM public-key record) reflect the approved
kernel/boot dependencies: e2fsprogs/e2fsprogs-libs/libss1.46.5-8.el9 and
grubby8.40-69.el9. These derived requirements were resolved and reviewed, not
hidden as later inventory additions. Builder-only93 packages are not in the
learner image.127 learner and187 builder source versions are retained with exact
signature/hash evidence;251 notice files and40 unresolved binary notice-provider
mappings remain explicit. Signed corresponding SRPMs do not by themselves
resolve every embedded-component redistribution obligation.

SELinux remains enforcing, passwords locked, console-only learner autologin and
`learner ALL=(root) NOPASSWD: ALL` guest-only policy. No SSH, guest agent, cloud
provisioning, kdump, network manager/remote service or automatic update is enabled.
Normal-boot observations and launch arguments prove no NIC or host shares.
Reported zero TCP LISTEN entries are not a claim that all local Unix sockets
are absent. The separate rpm-trust.tsv record is exactly the pinned Alma vendor key
`gpg-pubkey 0:b86b3716-61e69f29 (none)`; it is not silently omitted from
trust verification or the lesson’s full before/after RPM-database comparison.
No host account, service, group, package or security setting changed.

## Original fixtures and bounded transactions

The builder compiled only ll-rpm-data1.0-1/2.0-1 and ll-rpm-report1.0-1. Fixed
source/spec/epoch1767225600 and two independent builds at least two seconds apart
produced matching archive hashes. This establishes fixture reproducibility for
this reviewed build, not byte-reproducible full guest images. Vendor brp-mangle
changed the report shebang to /usr/bin/sh; the actual bash provider was verified.
Payload inspection rejected script/trigger tags, links, capabilities, privileged
bits and malformed dependency/file arrays. Fixtures start uninstalled.

Source and three archives are root-owned/protected from ordinary learner writes;
guest root can override these permissions. The visible fixed helper inspects the
same actual resolved DNF transaction it later applies, rejects extra identities,
checks collisions, and keeps repositories/plugins/weak dependencies/automatic
removal disabled. Only the three hash-pinned unsigned archives receive the
per-command localpkg_gpgcheck exception; official verification is not disabled.

Helper limits are32 transactions,256MiB logical retained-record admission,
32MiB kernel per-file limit,60s confirmation/developer timeout, and observed1GiB
free-space admission. Neither periodic monitoring nor admission is an aggregate
quota or guaranteed reserve. Records are retained on interruption; retries must
inspect them. An actual foreign e2fsprogs removal in a resolved transaction was
rejected before execution; actual confirmation timeout and owned interruption
preserved package/policy state.

The learner preparation’s original host receipt omitted the fixture dictionary.
Its original receipt is retained, not rewritten. A narrow host-output correction
copies already admitted exact archives/manifest into future receipts; no guest or
image bytes changed. Independent artifact inspection and supplemental final
policy evidence identify the existing candidate. Failed candidates1–7, including
candidate6’s specifically authorized SIGTERM termination, remain unclean or
rejected evidence and never became accepted learner bases.

## Release boundaries

Alma EULA and every package license still apply to this modified image. Complete
package/source/embedded notice review, corresponding-source publication/retention,
release signing and a public distribution decision remain separate. Qt/ICU
obligations and the recorded ICU signing-key warning remain unresolved. No image
was published, no production key created/admitted, no working app updated.
