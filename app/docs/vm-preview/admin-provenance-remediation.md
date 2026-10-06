# Older administrator image: supplemental provenance

## Result and boundaries

This documentation/source-only correction starts at
`9640c5bf1390836ead422c56496a012bd72719e0`. The four existing local commits remain
intact. It does not rebuild, register, mount, boot or modify any guest image.
No package transaction, application/runtime change, profile migration or
production image admission is involved.

The older `debian13-admin-local-v1` image has **216 installed binary packages**.
The [original 204-row inventory](admin-packages.tsv) is preserved byte-for-byte.
The [separate finalized inventory](admin-finalized-packages.tsv) has SHA-256
`2271bd8b719e7d51c40810d5f08f10ce9feb80ae1ae9d8962a08d68a52520cd8`.
All original 204 rows remain present with identical versions/source mappings.

Raw image SHA-256 remains
`f956d5c98848296f6887235c742ee4cc44ed5981acd0d2efd0a593b16d8a578f`.
The complete canonical runtime descriptor remains
`dcbdec81fc5aab2b775168cde1a350364ec8e017e67d1c25e1035f74cc8fb25d`.
Its `packages_sha256` still identifies the early inventory; it is not a claim
that that inventory is complete. Changing this descriptor would change the exact
compatibility key used by saved sessions. Supplemental documents are not runtime
descriptors, receipts or release-admission manifests, and are kept outside all
registered image directories.

## Cause and exact additions

`07preseed` ran the inventory-exporting late command before `08hw-detect`.
The later hook detected KVM/QEMU and installed `qemu-guest-agent` with
recommendations, then installed queued Intel CPU microcode. Dependencies and
recommendations account for the twelve additions. All came from the verified
Debian 13.7.0 DVD; no online guest package transaction was involved.

| Additional binary | Binary version | Source/version |
|---|---|---|
| intel-microcode | 3.20251111.1~deb13u1 | intel-microcode, same version |
| iucode-tool | 2.3.1-3 | iucode-tool, same version |
| libatomic1:amd64 | 14.2.0-19 | gcc-14 14.2.0-19, already retained |
| libffi8:amd64 | 3.4.8-2 | libffi, same version |
| libglib2.0-0t64:amd64; libglib2.0-data | 2.84.4-3~deb13u5 | glib2.0, same version |
| libnuma1:amd64 | 2.0.19-1 | numactl, same version |
| liburing2:amd64 | 2.9-1 | liburing, same version |
| libxml2:amd64 | 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | libxml2, same version |
| qemu-guest-agent | 1:10.0.13+ds-0+deb13u1 | qemu, same version |
| shared-mime-info | 2.4-5+b2 | shared-mime-info **2.4-5** |
| xdg-user-dirs | 0.18-2 | xdg-user-dirs, same version |

The retained live audit found 216 rows with the same finalized inventory hash.
This correction reuses that evidence and the installer-hook analysis; it does
not infer the final guest state solely from a package dependency list.

## Collected and verified materials

The new, non-overwriting evidence directory is:

`/home/drak/.local/state/omarchy-learning-lab/recovery/admin-provenance-closure-20261006T225345241379Z`

It contains a verified 436-file source snapshot, `collected-material-manifest.json`,
the additional binaries, controls, notices, sources, metadata and verification
logs. [Supplemental provenance](admin-finalized-provenance.json) pins the material
manifest hash and enumerates the twelve binary hashes and ten source versions.
Previously retained materials are referenced and rehashed, not overwritten.

- All 216 exact binary hashes and copyright mappings are covered. The twelve
  additions were extracted as data from the hash/signature-verified DVD.
- The DVD microcode pool entry is a hard link to its `firmware/` archive member.
  The initial empty extraction failed the hash check; the verified member target
  was then read and matched to the expected package hash. No host link was followed.
- `libatomic1` uses a package-relative documentation link to the exact installed
  `gcc-14-base`; its copyright is retained and explicitly mapped. The other eleven
  additional binary copyright files are retained directly.
- Ten missing source versions were collected: **32 files, 71,395,070 bytes**.
  Together with the previous 194 source versions/603 files, the recorded material
  closure is **204 source versions/635 files**.
- Debian main/security Release signatures and their source-index hashes were
  reverified. The additional non-free-firmware index matches the SHA-256 in the
  same authenticated Debian Release. Each source file matches its exact signed
  index record; `.dsc` identity and referenced-file hashes were cross-checked.
  This authenticates historical inputs, not their current security-update status.
  Separate maintainer-key signature verification is not claimed.
- All twelve new control files were inspected: none declares `Built-Using` or
  `Static-Built-Using`. The retained 204-binary control review's incorporated-source
  references remain covered by the exact combined source set.
- Ten source-package copyright files and 23 common-license texts are retained.
  Common licenses came from the exact verified guest `base-files` archive, not
  from the host. No downloaded source or maintainer script was executed.

Collection used bounded, exact-size/hash downloads from official Debian sources.
The restricted environment's DNS refusal required normal network approval; it
did not result in bypassing authenticity checks. The native-format Intel source
archive was inspected as such rather than assuming every package uses a separate
Debian patch archive.

## Intel microcode terms and remaining obligations

The exact retained microcode notice permits redistribution/use in unmodified
binary form subject to preserving the copyright and disclaimer, not using Intel
or supplier names for endorsement without permission, and its prohibition on
reverse engineering, decompilation and disassembly. Its Debian packaging is
GPL-2.0-or-later; the referenced GPL-2 text is retained. The full notice is
authoritative, not this summary.

The authenticated Debian source package includes packaging and microcode data;
it does **not** establish availability of Intel's microcode implementation source.
Do not label proprietary firmware as MIT or claim complete implementation-source
availability merely because its Debian source archive was collected.

The identified inventory/material omission is now accounted for. These remain
open: per-file/component redistribution review (including QEMU bundled content),
the unfinished Qt review, the ICU signing-key warning, and fresh public-release
preparation/signing/distribution decisions. No public-release clearance is claimed.

## Runtime and compatibility

The prior audit found `qemu-guest-agent` installed but inactive/static, no running
agent and no guest-agent channel. The controller exposes no guest-agent channel.
The approved guest sudo rule and locked password entries were unchanged. The
inventory omission is not evidence of a runtime or isolation failure; package
presence remains a separate policy/attack-surface consideration. No packages were
removed to match the early inventory.

All application runtime, descriptors, lesson bytes/defaults, session formats,
image hashes, registered-directory membership and receipts are preserved. No
personal profile or active guest was controlled. Historical native workflow
evidence applies only to its unchanged artifacts; it does not verify licensing.
Physical-keyboard/accessibility gaps remain outstanding.

## Validation

Material checks cover exact inventories, binary/source/notice hashes, authenticated
metadata, `.dsc` references and declared incorporated-source closure. Consistency
tests cover the historical/final inventory relationship, immutable descriptor and
pin resolution, source mappings and production-admission exclusion. Full regression
and GNU-reference results, protected-artifact comparisons and final candidate hashes
are retained in this correction's evidence directory. No new native walkthrough
is required for these unchanged runtime artifacts.

Final checks for this correction:

| Check | Result |
|---|---|
| Full regression suite | **602 passed**, including three new provenance consistency tests; `regression-approved.log` |
| GNU reference fixtures | **44 passed**; `gnu.log` |
| Actual wheel build/install | Passed in separate recovery-directory environments, offline dependency reuse; `pip check` passed |
| Installed-wheel resources | **189 application/resource files** match; revised packaged notices match; installed offscreen smoke passed outside the checkout |
| Preservation | All eight recorded base copies, registered-image members/receipts and 430 unchanged tracked source files checked against the pre-task records |

The first restricted regression run could not start GPG's agent for two test
classes; its failed log is retained. The authorized rerun with local IPC access
passed, using only ephemeral test trust. No production key/allowlist changed.
The existing shutdown warning remains unsuppressed:
`ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.
This source-only correction does not investigate or claim to fix that baseline warning.
