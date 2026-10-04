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
| Debian guest packages, kernel, bootloader and documentation | Separate optional guest image, with many independent copyright holders/licenses | The local package/version inventory is `docs/vm-preview/packages.tsv` (199 entries). It is NOT a complete licensing or corresponding-source inventory. Guest notices are retained under `/usr/share/doc/*/copyright` and `/usr/share/common-licenses` according to the existing image recipe; a fresh release image still requires a package-by-package audit. |
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
