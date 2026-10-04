# Licensing and distribution readiness

## Scope and ownership

The owner approved the standard MIT license for Learning Lab's original code.
The copyright line is `Copyright (c) 2026 Mike Buchanan`, matching the established
Git author and configured owner name. The inspection found no earlier project
LICENSE, competing copyright statement or vendored third-party notice to replace.
The MIT grant does not override any third-party term, imported content license,
or guest-image copyright. See [the inventory](../THIRD_PARTY_NOTICES.md).

Repository-root `LICENSE` is canonical. `app/LICENSE` is a byte-identical packaging
copy because the Python project root is `app/`; setuptools license-file paths
must stay inside that project. Change both copies together. Tests detect drift.
The license text itself has no project-specific exclusions or altered clauses;
the scope and third-party exclusions are explained separately here and in README.

## Supported packaging

`app/pyproject.toml` uses PEP 639 `license = "MIT"` and explicit
`license-files = ["LICENSE", "THIRD_PARTY_NOTICES.md"]`. The minimum build backend
is `setuptools>=77.0.3`, which supports those fields. This is a build dependency,
not a system Python upgrade. [Setuptools configuration documentation](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html).

The wheel carries both files under `<distribution>.dist-info/licenses/`, and
METADATA declares `License-Expression: MIT` plus both `License-File` entries.
The sdist includes both files at its project root and matching PKG-INFO. Its
MANIFEST also includes this guide. Neither artifact contains dependency binaries,
a guest image, production/test signing keys or personal runtime state.
The user-local builder now copies the legal files into its isolated build source;
it must fail if they are missing rather than publish an artifact without them.

Build only (does not install or activate the application):

```bash
cd app
python3 -B tools/user_install.py build --output /absolute/new/wheel-output
```

For source distribution verification, make a disposable copy of the tracked app
source plus reviewed new licensing files, excluding evidence/caches/environments.
Create a build venv there and install the declared build-system requirements.
In that copied source directory, invoke the configured PEP 517 backend:

```bash
/path/to/build-venv/bin/python -I -B -c \
  'from setuptools.build_meta import build_sdist; build_sdist("/absolute/new/sdist-output")'
```

Build a second wheel from that sdist with isolated `pip wheel --no-deps`, then use
`tools/check_license_artifacts.py` to compare the direct wheel, sdist and rebuilt
wheel to the canonical license and the current notices. This verifies that neither
the repository parent nor untracked local files are needed by the sdist build.
Finally install the rebuilt wheel into a separate test venv, run `pip check`, and
run a copied `tools/installed_smoke.py --require-icon` with `python -I -B` from
outside the checkout. Keep all test profiles disposable and the working app intact.

## Release obligations still open

### Application alone versus bundled dependencies

The MIT application wheel is distinct from the PySide/Qt installation and an
optional offline wheelhouse or venv. The reviewed 6.11.2 PySide/Shiboken metadata
has an LGPL/GPL expression, but no separate notice/license files appeared in its
installed file records. Do not claim that this local observation is an exhaustive
upstream audit or that it makes the wheels compliant for redistribution. Before
shipping them, obtain matching upstream source/license inventories and supply
missing notices and required source material. Record exact wheel hashes and the
actual Qt modules, plugins and transitive components that travel with them.

Qt has module-specific and third-party terms; some open-source modules are GPL-only.
Retain all applicable notices, permit the required modification/replacement and
debugging rights, and verify the chosen LGPL/GPL compliance route against the
actual distributed artifacts. Merely calling the app MIT or using dynamic imports
is insufficient. This batch does not choose a commercial Qt license, replace
dependencies or create an offline dependency bundle.
[Qt obligations](https://www.qt.io/development/open-source-lgpl-obligations),
[Qt 6.11 licensing](https://doc.qt.io/qt-6.11/licensing.html).

### Debian guest release

The 199-line existing package/version list is useful provenance but lacks binary-to-
source mappings, complete copyright texts, source archives, Debian patches and
per-package redistribution decisions. It describes the local preview, not a new
release candidate. No image was mounted or modified in this licensing pass.

For a later fresh image, collect each installed package's binary and source names,
versions, architecture, repository/component, license files and exact source hashes.
Include the referenced `/usr/share/common-licenses` texts and any notices for
non-code contents. Review firmware/non-free material if present. Preserve the build
recipe, downstream modifications and installation/build scripts needed for the
applicable corresponding-source requirements. Make source available through a
license-permitted method matched to online AND offline distribution; a generic
Debian mirror link, a package list, or Learning Lab's sdist is not sufficient proof.
[Debian redistribution guidance](https://www.debian.org/doc/manuals/debian-faq/redistributing.en.html),
[Debian copyright-file policy](https://www.debian.org/doc/debian-policy/ch-docs.html#copyright-information).

The existing six-member image bundle can carry bounded notices/provenance, but it
is not an archive of all corresponding source. Plan separately versioned source
artifacts and clear retrieval/offline delivery instructions before publication;
no bundle-format change is made here. Do not reuse the owner's proof disk,
credentials, shell history or personal sessions.

### Explicit release gates

- Complete notice/source inventories for every artifact actually distributed.
- Decide release-signing ownership, key custody and independently established trust.
- Decide distribution/source hosting, retention and an offline source-delivery path.
- Prepare a fresh candidate; verify it and all lessons on a separate test installation.
- Review the final dependency/image licensing inventory before authorizing publication.

Production signing keys and release allowlists remain empty. Adding MIT does not
clear the complete VM bundle for publication or authorize a release/upload.
