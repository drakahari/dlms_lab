# License scope and third-party inventory

Learning Lab's original code is MIT licensed, copyright (c) 2026 Mike Buchanan.
The accompanying LICENSE is the unmodified MIT text. It does not relicense
third-party code, assets, dependencies, imported lessons or guest-image contents.
Existing third-party terms and copyright notices remain authoritative.
This inventory is not a substitute for their complete license texts or source.

## What this application distribution contains

The Learning Lab wheel contains the project's Python/QML code, original scenario
and lesson JSON, authoring text and its original `omarchy-learning-lab.svg` icon.
The source review found no vendored third-party library, font, icon set, copied Qt
example, or pre-existing third-party license/notice file in these application
resources. This is an inspected inventory, not a guarantee about unreviewed future
contributions. Preserve any third-party notice if such material is added later.
The root repository LICENSE and app/LICENSE are identical; the latter permits a
standalone build from the app source distribution.

The wheel does NOT contain Python, PySide6/Qt libraries, QEMU, firmware, gpgv, a
Debian ISO, guest disk, personal profile, runtime evidence or test signing key.
Declaring/installing a dependency does not change that dependency's license.
An offline wheelhouse, copied virtual environment or VM bundle is a separate
redistribution inventory and needs its own notices and source-compliance review.

## Dependencies and external components

| Component | Role and observed terms | Notice/source status |
|---|---|---|
| PySide6, PySide6_Essentials, PySide6_Addons, shiboken6 | Separately installed runtime dependencies; inspected 6.11.2 metadata declares `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only` | The inspected wheels' installed file records contain no separate license/copyright/notice files. This is an unresolved notice-packaging gap before redistributing those exact wheels or a venv, not permission to omit notices. |
| Qt libraries, plugins and their third-party code | Supplied through the Qt/PySide installation; module and component licenses vary | Audit the actual shipped binaries, including unused Addons if redistributed. Some Qt modules are GPL-only under the open-source offering. Retain applicable Qt and third-party texts, notices and matching sources; metadata alone is insufficient. |
| CPython / standard library | Host interpreter; PSF and component-specific terms | Not in the app wheel. Preserve Python's own license and bundled-component notices if an interpreter is distributed. |
| setuptools and pip | Build/installation tools, installed separately | Not vendored in the app wheel. Their own terms apply if a build-tool/offline dependency bundle is distributed. |
| QEMU and firmware | Optional host tools, not installed automatically or packaged here | QEMU is GPLv2 as a whole, with component exceptions and separately licensed firmware. Review exact packages and matching source if redistributed. |
| GnuPG gpgv | Optional offline signature verifier; host executable | Not bundled. Preserve its applicable GPL/component notices and source obligations if redistributed. |
| Debian guest packages, kernel, bootloader and documentation | Separate optional guest image, with many independent copyright holders/licenses | The local package/version list has 199 entries. The 2026-10-04 preparation audit collected all exact binary notices and a 189-source-package closure, including Built-Using/Static-Built-Using. See `docs/distribution-inventory.json`. Per-file licensing review and a fresh public candidate remain outstanding. |
| Omarchy theme inputs and host fonts | Read from the user's existing system | Not copied into the application artifacts by this build. Their terms are not changed. |

Runtime imports use QtCore, QtGui, QtQml, QtQuickControls2 and the QtQuick Controls,
Layouts and Dialogs QML modules. This is not a complete transitive binary inventory.
No commercial Qt entitlement is asserted. An MIT application may use the available
open-source Qt route only while satisfying the licenses of the components used.

## Redistribution obligations still open

Before redistributing dependency binaries, collect exact versions, hashes,
copyrights, license choices and third-party notices from their matching sources.
For LGPL components, preserve user modification/replacement and debugging rights;
include required LGPL/GPL texts and meet the applicable corresponding-source and
relinking/installation-information requirements. Do not assume dynamic linking or
an upstream URL alone discharges every obligation. GPL-only components need their
own applicable compliance route. See Qt's official guidance below.

Before publishing a Debian-based image, map every binary package to its exact
source package/version, retain source archives, Debian patches and build recipes,
and provide the corresponding source by a method allowed by each applicable
license. Preserve copyright files and referenced common-license texts, including
notices for documentation, fonts, firmware and other non-code material. Review
any non-free or separately restricted content individually. The existing local
image, proof disks and test bundles are NOT approved public release artifacts.
MIT for Learning Lab does not clear the complete VM bundle for publication.

## Primary references

- [Standard MIT text](https://opensource.org/license/mit)
- [Qt 6.11 licensing](https://doc.qt.io/qt-6.11/licensing.html)
- [Qt 6.11 third-party components](https://doc.qt.io/qt-6.11/licenses-used-in-qt.html)
- [Qt for Python third-party licenses](https://doc.qt.io/qtforpython-6/licenses.html) (rolling documentation; check the actual distributed version)
- [Qt GPL/LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations)
- [Python license](https://docs.python.org/3.14/license.html)
- [QEMU license](https://www.qemu.org/docs/master/about/license.html)
- [Debian redistribution guidance](https://www.debian.org/doc/manuals/debian-faq/redistributing.en.html)
- [Debian copyright-file policy](https://www.debian.org/doc/debian-policy/ch-docs.html#copyright-information)

Inventory reviewed 2026-10-04 against repository baseline 126acab16db65730c86b4975af289efcb5fdcc6b.
No guest image was mounted, rebuilt or changed for this inventory.

## Distribution-preparation evidence added 2026-10-04

The [readiness report](docs/distribution-readiness.md) and machine-readable
`docs/distribution-inventory.json` extend this inventory against baseline
8b53f8dd96d058997b9418feeb38a44234909cf8. Exact binary/source artifacts and selected
notices are retained in a private directory outside Git, not embedded in this
application wheel. Collection is not complete legal clearance or a release approval.

The full PySide6 6.11.2 candidate wheel set totals 256,016,078 bytes. Matching
Qt/PySide source archives and 3,012 selected notice/attribution documents were
collected; 173 Qt/lib entries were hashed. Source declarations are not an
exhaustive binary-to-component map. Nine attribution documents fail strict JSON
parsing; original documents remain unchanged for review. The actual Addons wheel
contains Qt Charts and Qt Data Visualization, with GPLv3 open-source terms.
Unused redistributed binaries still have their own obligations.

Extra bundled libraries identified in an existing isolated verified-wheel
environment include ICU 73.2 (Unicode and component terms) and FFmpeg 7.1.5
(LGPL 2.1-or-later reported by the binary). Their exact sources/notices were
collected. FFmpeg's published source signature verified; ICU's SHA-512 matches,
but its available signing key has an expired-key warning. Qt vendor patches,
build options, complete bundled component notices and source obligations remain
open. General Qt documentation lists a different FFmpeg version; it cannot replace
the actual binary inventory. See the report for hashes and precise verification.

For Debian, all 199 binary notices and 189 exact source versions are collected,
with binary/index/source hash checks and signed archive metadata verification.
This includes Linux source behind signed-kernel packaging and statically
incorporated Rust sources. Twelve notices use legacy free-form text and need
manual terms review. No Debian image, owner proof disk or personal history was
copied, mounted, booted or cleared for publication. Host Python/QEMU/gpgv remain
separate user-obtained prerequisites; their binaries are not redistributed here.

## Separate administrator development image

The Services, Logs & Safe Recovery unit adds a fresh, local-only Debian image;
its contents are not covered by Learning Lab's MIT license or included in the
application wheel. The finalized older image contains **216 binary packages**.
The original [204-row inventory](docs/vm-preview/admin-packages.tsv) was exported
before later Debian Installer hooks added twelve packages. It remains historical
evidence, not a complete installed-package inventory. See the separate
[216-row inventory](docs/vm-preview/admin-finalized-packages.tsv) and
[supplemental provenance](docs/vm-preview/admin-finalized-provenance.json).

The supplemental collection maps all 216 binaries to exact versions and notices,
and retains 204 source versions (635 authenticated source files), including the
ten previously missing source versions. Declared Built-Using/Static-Built-Using
references are covered. This describes verified material collection, not a
completed per-file/component licensing review. All materials remain outside Git.
The unchanged legacy descriptor still references the early inventory for exact
session compatibility; no image, descriptor, receipt or pin was rewritten.

Intel microcode's exact notice permits unmodified binary redistribution subject
to retaining its copyright/disclaimer, its endorsement restriction and its
reverse-engineering/decompilation/disassembly prohibition. Its Debian packaging
is GPL-2.0-or-later. The retained Debian source archive does **not** establish
availability of the microcode implementation source. Preserve the full notice
and applicable common-license texts; do not apply the project's MIT license to
firmware. See the [remediation report](docs/vm-preview/admin-provenance-remediation.md).
This does not replace the earlier image inventory or establish public release
clearance. Per-file licensing review, production signing/distribution decisions,
the unfinished Qt review and the ICU signing-key warning remain outstanding.


## Two additional local platform candidates (2026-10-12)

The independently prepared Debian foundation206-package and AlmaLinux learner
190-software-package images are local development artifacts, **not included in
this application wheel or a public release**. The separate Alma builder contains
283 software packages and remains builder-only. RPM vendor public-key state is
validated separately, not silently omitted from trust checks.

See [platform provenance](docs/vm-preview/platform-image-provenance.md) and its
[hash index](docs/vm-preview/platform-image-provenance.json). Debian exact source
closure127 versions, Alma learner127 and builder187 source versions, authenticated
binary/source manifests and available notices are retained outside Git. Alma’s
251 notices/40 unresolved binary-provider mappings are collection evidence, not
per-file licensing clearance. Its EULA and individual licenses remain applicable.
Modified Anaconda installer input and generated patch remain under their original
GPL terms; retaining corresponding source and patch does not relicense Anaconda.
Only the project-owned fixture source/spec/payload and original preparation code
use the project MIT license. Full images are not claimed byte-reproducible.

No production signing keys or release allowlists have been added. No published
image, generic upstream URL or project MIT statement substitutes for exact
corresponding-source and notice obligations. Qt/ICU review, the existing ICU
signing-key warning, embedded-component review and distribution/signing decisions
remain explicit public-release blockers.
