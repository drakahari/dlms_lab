# Distribution preparation review — 2026-10-04

Preparation baseline: `8b53f8dd96d058997b9418feeb38a44234909cf8`.
The reviewed source commits `126acab` and `8b53f8d` were pushed without force;
live origin/main matched that baseline. This is source publication, not a VM
release. This batch does not approve dependency or image redistribution.

## Artifacts and evidence

The machine-readable [inventory](distribution-inventory.json) records exact
binary/source versions, hashes, origins, notices, configuration observations and
uncertainties. It is an audit snapshot, not an installer lockfile, runtime catalog,
SPDX conformance claim or legal clearance. Artifact paths in it are relative to:

`~/.local/state/omarchy-learning-lab/recovery/release-preparation-20261004T211404598174Z/`

That private directory contains the collected binaries, source archives, selected
notices, public verification material, recipes, download log and integrity manifest.
It is outside Git. No guest disk or profile was copied there. An independent
tracked-source recovery snapshot was verified before repository changes.

Space admission observed approximately 823 GiB available. Collection was planned
below 12 GiB, individual downloads capped at 2 GiB (smaller bounds for metadata),
with four concurrent downloads at most, 30-second socket and 900-second file
limits. Failed partials/logs were retained; existing artifacts were preserved.
Archives were read as data and selected regular documents copied with bounded
sizes and safe paths. No downloaded source/build script was executed or collected third-party software
installed. Only our own locally built application wheel was installed for the
isolated packaging check described below. No disk mounting, QEMU launch or interaction with the active guest.

| Scope | Verified preparation | Remaining work |
|---|---|---|
| Learning Lab original application | MIT text, exact source baseline, wheel/sdist legal metadata; source and runtime resources preserved | Choose public application release/version and retention |
| Candidate offline Python dependencies | Four exact Linux x86-64 6.11.2 wheels: PySide6, Essentials, Addons, shiboken6; PyPI SHA-256/size; matching PySide and Qt sources | Complete vendor patches/build-option/component mapping; recipient notices and LGPL/GPL compliance route |
| Qt bundled code | 173 Qt/lib library entries, including filename aliases; 3,012 selected notice/attribution documents from Qt/PySide sources; 205 attribution records | Nine attribution documents contain unescaped control characters and fail strict JSON parsing; raw documents retained. Source declarations do not prove binary inclusion. Chromium/other embedded code needs per-file/build audit |
| Extra wheel libraries | ICU 73.2 and FFmpeg 7.1.5 identified in an existing isolated verified-wheel environment; matching sources/notices retained | ICU's historical signing key is expired; Qt vendor patches/build provenance and complete linkage obligations remain open |
| Existing local Debian test guest | All 199 exact guest binaries mapped; 199 copyright notices, 189 exact source packages including incorporated-source closure collected | Fresh release candidate, per-file/non-code licensing review, exact modified-file inventory and independent installation acceptance |
| Host tools | Python, QEMU/GTK/KVM and optional gpgv are user-obtained prerequisites, not proposed release contents | Document target ABI/prerequisites on a fresh Omarchy installation; separately approve any host package changes |

The current application dependency range is `PySide6>=6.11,<6.12`; it does not pin
6.11.2 or wheel hashes. The collected set is a concrete offline candidate, not a
promise that a future online installation resolves identically. No dependencies
were changed. Host observations: Arch Python 3.14.7-1, QEMU x86/img/GTK 11.1.1-1,
GnuPG 2.4.9-3; retained build environment setuptools 84.0.0 and pip 26.2.1.
Host C/C++/OpenSSL/display/font libraries remain external ABI requirements.

## Source and verification details

Debian 13.7.0 DVD-1 was rehashed and its checksum signature reverified using the
previously reviewed CD fingerprint. Selected binary files were checked against
the DVD index's SHA-256 and sizes. The current main/security Sources indexes were
checked against signed InRelease metadata; signatures also verify using the archive
keyring extracted from that verified DVD. Every collected source file matches
those authenticated SHA-256/size entries. Logs retain exact signer fingerprints.
This reuses the existing CD trust basis; an HTTPS key download alone is not an
independent trust establishment. Upstream `.asc` signatures are retained where
listed, but not every upstream signer is separately authenticated. The Debian
archive authentication chain is verified.

Source closure goes beyond the binary's Source field: signed kernel binaries
require `linux` 6.12.107-1 in addition to `linux-signed-amd64` 6.12.107+1;
`sqv` declares Rust Built-Using/Static-Built-Using dependencies; grub and libslang
also declare incorporated sources. All 189 versions were available and collected.
187 source copyright files were separately readable; libxcrypt/pcre2 source
patches/diffs are retained without reconstructing or executing them. Their exact
binary notices are collected. Twelve binary notices use free-form text rather than
DEP-5 License labels. Those labels, when present, are literal and not normalized
license expressions. Full texts, exceptions and copyright holders are authoritative. The legacy notice
review records GCC runtime exceptions, Kerberos embedded/non-code terms and SCOWL
wordlist conditions. os-prober explicitly notes unspecified GPL versions for some
contributors; libxcrypt identifies some files with unknown licensing statements.
Those specific uncertainties require resolution on the files actually distributed.

Qt/PySide archives match the exact official HTTPS mirrorlist sizes and SHA-256:
Qt `6dcfbca271d76a6502741a2c0dc6fc98ef7dd0b7b4cfd0abcebb285a86a26f33`,
PySide `cba47efbaad1bedd529725cbc14e21f156c7a19366f07b3edfbb076ffd7afdf8`.
No independently verified detached signature was found for these archives.
The official mirror redirect was checked against Qt's published mirror list.
Version matching does not establish every vendor patch or build configuration.

FFmpeg reports **7.1.5**, LGPL 2.1-or-later, and a retained configuration including
OpenSSL. This differs from the general Qt documentation's FFmpeg version; use the
actual binary evidence. Its source signature verifies with exact official release
fingerprint `FCF986EA15E6E293A5644F10B4322F04D67658D8`.
ICU reports **73.2**. Its official SHA-512 matches. Both archive/checksum signatures
have VALIDSIG for `3DA35301A7C330257B8755754058F67406EAA6AB`, but also EXPKEYSIG:
the key expired in September 2024. Current official KEYS still produces that warning.
This is recorded as unresolved historical signing trust, not unconditional success.
No production trust was created or changed.

The full Addons wheel actually contains Qt Charts and Qt Data Visualization,
whose open-source terms are GPLv3, even though this app does not import them.
Redistribution of unused binaries still requires their applicable terms. Do not
represent the whole wheelhouse as uniformly LGPL. The current app wheel includes
none of these binaries. Qt PDF and Chromium-derived contents need their separate
module/component review. No commercial entitlement is asserted.
[Qt Charts](https://doc.qt.io/qt-6.11/qtcharts-index.html),
[Qt Data Visualization](https://doc.qt.io/qt-6.11/qtdatavisualization-index.html),
[Qt component documentation](https://doc.qt.io/qt-6.11/licenses-used-in-qt.html),
[Qt obligations](https://www.qt.io/development/open-source-lgpl-obligations).

## Size and source retention

The four wheel candidates total **256,016,078 bytes** (244.2 MiB).
Debian corresponding-source closure totals **700,795,160 bytes** (668.3 MiB).
Qt/PySide/ICU/FFmpeg source archives total **1,075,285,046 bytes** (1.001 GiB).
Sources alone total approximately **1.65 GiB**, before notices/recipes/indexes.
The prior application wheel is 246,009 bytes; the new packaging is measured in the
local verification report. The prior local test image bundle is **476,721,837
bytes** (454.6 MiB) with a **16-GiB logical raw disk**. That measured test artifact
is not distributable approval or a guaranteed future image compression ratio.
A download of app + candidate dependencies + similarly compressed guest + all
sources would be roughly **2.34 GiB**, plus notices/metadata. Release sizes must be
measured again on the actual candidate; installed disks/retained generations use
much more space and filesystem compression/sparsity is not a quota.

Retain exact source versions, Debian patches, available signatures, public keys,
authenticated indexes, notice texts, recipe/configuration changes and hashes for
each shipped binary/image. Publish source alongside binaries and include it in an
optional offline source set. Do not depend on upstream URLs remaining available.
Prefer direct corresponding-source provision over an unsupported written offer.
If an offer is chosen, review its license-specific duration and fulfillment duties;
a generic three-year policy is not a universal substitute. Keep an independent
recovery copy and test source retrieval. Never remove sources while related
binaries remain available or any applicable obligation remains.

## Hosting and signing decisions

Recommend the **existing GitHub repository's Releases** initially: small app
wheel/sdist, signed image bundle, hashes/notices and separately named exact source
archives/sets. Every individual asset must be **under 2 GiB**. GitHub documents no
total release-size or bandwidth limit. Current measured artifacts fit individually;
check each final file before upload. Avoid Git/LFS for image/source payloads.
If a later indivisible image exceeds 2 GiB, do not split a bundle and imply the
current importer accepts multipart input.
[GitHub release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).

For larger indivisible objects, **Cloudflare R2** is a practical alternative:
5-TiB object limit, 5-GiB single-part uploads, larger multipart uploads; use an
approved custom domain for production, since r2.dev has variable rate limits and
is not intended for production. Published standard storage is $0.015/GB-month,
with operation charges and zero direct egress charges. A 10-GB immutable release
set is about $0.15/month in storage before free allowances/operations; actual costs,
account/payment and domain setup need approval. No account or upload was made.
Limits/pricing checked 2026-10-04:
[R2 limits](https://developers.cloudflare.com/r2/platform/limits/),
[R2 pricing](https://developers.cloudflare.com/r2/pricing/).

The owner must choose release artifact scope (app-only with upstream dependency
installation versus a separately reviewed offline wheelhouse), notice/source
compliance review, historical ICU trust handling, fresh Debian inputs/version,
hosting/retention ownership, and signing custody before publication.
Recommend an owner-controlled offline OpenPGP primary key with a bounded signing
subkey, encrypted independent recovery backup and offline revocation certificate.
Do not share private keys with the app or automate key generation in an installer.
Distribute the full initial fingerprint through an independently verified owner
channel and review/commit the public key plus exact immutable release-manifest
allowlist. A valid signature or matching image name alone must never admit content.

Define who can approve/sign releases, where recovery material is held, subkey
expiry/renewal and compromise response. Rotation needs a reviewed trust update and
an independent new-fingerprint check; cross-signing helps continuity only when the
old key is still trusted. Preserve required exact legacy descriptors, image versions
and lesson revisions for pinned sessions/rollback. Never silently migrate disks.
Withdrawing admission must preserve recovery data and verified Stop for a running
guest. Production keys and release allowlists remain empty in this batch.

## Next authorized stage

Use the [fresh release-image procedure and acceptance checklist](vm-preview/release-image.md).
Prepare a clean candidate only after approving inputs, source/notice disposition
and test plan. Complete all eight guest lessons and installed lifecycle on another
disposable installation before requesting publication. This batch gathers evidence
and drafts the procedure; it builds no image and performs no native guest test.
Physical-keyboard, accessibility and exhaustive native scaling gaps remain open.

## Batch verification

- Full existing suite: **488 tests passed**. Known baseline warning remains:
  `gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.
- Own wheel and sdist built with retained setuptools 84.0.0; MIT metadata/legal
  files checked. Sdist contains exact readiness report, inventory and image
  procedure. All 119 wheel application resources match the baseline byte-for-byte.
- Own wheel installed into a fresh test environment outside the checkout.
  Previously installed isolated PySide dependencies were reused read-only through
  a test-only path file; no collected third-party software was installed. Start
  and reopen offscreen smoke passed with 22 packs, four collections, all eight VM
  lesson resources and simulation/authoring Learn/Challenge persistence. This is
  not a fresh dependency installation, native guest boot or file-dialog acceptance.
- Relative document links, JSON consistency, artifact hashes, empty production
  trust, unchanged runtime/pack/recipe files and whitespace checked. Candidate
  files contain documentation/inventory and build-source copying only. Downloads,
  environments, public-key material and runtime evidence remain outside Git.

## Older administrator image: supplemental provenance

The earlier Debian guest rows above describe the original unprivileged-image
inventory and must not be reused as the administrator inventory. The older
`debian13-admin-local-v1` image contains 216 packages; its original 204-row export
preceded installer finalization. Supplemental exact-version material collection
now covers 216 binary/notice mappings and 204 source versions (635 files), with
the early inventory and every runtime image/descriptor/pin preserved.
See [the remediation report](vm-preview/admin-provenance-remediation.md) and
[machine-readable supplement](vm-preview/admin-finalized-provenance.json).

This closes the identified inventory/material-collection omission. It does not
complete per-file/component license review, provide Intel microcode implementation
source, resolve the Qt/ICU blockers, or authorize public image distribution.
Production bundle admission remains empty and no new image was prepared.
