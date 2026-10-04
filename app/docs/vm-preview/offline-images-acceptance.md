# Offline image foundation — implementation evidence

Baseline: `0a2de99a4bc0862e4b6737c9d4af722a22a6d7db`, branch main, initially clean.
Work is intentionally unstaged/uncommitted. No installed-app update, real profile
access, guest boot/control, production signing key, image publication or host
configuration change was performed.

Verified tracked-source recovery snapshot (284 files):
`/home/drak/.local/state/omarchy-learning-lab/recovery/offline-image-source-20261004T191015777256Z`.
All snapshot hashes were rechecked after implementation. No profiles, VM disks,
Git metadata or installation directories were copied.

## Final adversarial review

The complete 19-file candidate was reviewed against the approved design. Before
fixes, all 284 baseline snapshot hashes and the 19 prior candidate hashes matched.
A second source-only snapshot (296 files) was created and verified at:
`/home/drak/.local/state/omarchy-learning-lab/recovery/offline-image-adversarial-20261004T194433269331Z`.

Findings fixed within this batch:

1. **Mutable ZIP headers were reparsed after preflight.** Python's general ZIP
   reader could consume altered directory sizes/flags before the later agreement
   check. The importer now freezes six validated member byte ranges and reads
   only those ranges with bounded `pread` and streaming CRC checks. No general
   ZIP reader is constructed. A real header mutation at that boundary is covered,
   as is payload mutation, which fails CRC or the signed content hash. Local and
   central headers, ZIP64 extras and range consistency still undergo preflight.
2. **An exact-match retry omitted the publication sync.** A prior successful
   rename followed by failed parent sync could be reported as a verified no-op
   without completing durability. Retries now sync the existing directory and
   both publication parents; another sync failure is still an error. Both findings
   reproduced before their fixes (`/tmp/offline-adversarial-reproduce.log`).
3. **Signature status parsing admitted out-of-order records and duplicate SIG_ID.**
   It now checks the status sequence and rejects duplicate signature IDs. Real
   gpgv tests also reject another signer even when its key is present, reject two
   detached signatures, and reject a correctly signed but unlisted manifest.

Test review corrected the former “valid signature, unapproved manifest” fixture:
its edited manifest is now actually re-signed. Additional checks prove signature
failure occurs before payload reads/destination creation, exercise ZIP64 central
64-bit sizes/offsets and oversized values, and expand actual gzip output across
multiple bounded chunks. Unavailable retained pins cannot Start or Reset.
A forged running record naming the test Python process is rejected through real
`/proc` verification, with no mocked process identity or QMP.

The successful Stop routing/body checks still use synthetic running/QMP evidence;
they are **not a fresh native shutdown test**. The unchanged Stop/process/QMP code
is protected by baseline hashes/AST guards. Together these establish content-policy
independence and fail-closed forged-process handling, not renewed native guest
acceptance. An intact trusted application/catalog installation is required; this
feature does not repair corrupt installed application resources.

## Final verification

| Gate | Result |
|---|---|
| Full regression suite | **469 passed** (408 baseline + 61 new), 11.807 seconds; `/tmp/offline-adversarial-regressions.log` |
| Installed-wheel importer/catalog suite | **61 passed**, copied fixtures run from `/tmp` with isolated installed Python; `/tmp/offline-adversarial-installed-tests.log` |
| VM lesson UI | **75 checks per scale**, offscreen 100/150/200%, compact/wide, no QML warnings |
| Existing text-unit UI | **250 + 8 restart checks per scale**, offscreen 100/150/200%, no QML warnings |
| Actual wheel | Built with declared setuptools backend in a temporary environment, installed into a separate venv; pip check passes |
| Packaged source parity | **119 package files** match the reviewed source bytes |
| Installed app resource/start/reopen smoke | PASS outside checkout; four collections/22 packs, eight VM lesson resources and metadata resume, authored Learn/Challenge; no guest boot |
| Wheel/source-distribution exclusions | No tests, test trust/key material, fixtures, images, disks or generated evidence in inspected artifacts |
| Protected baseline bytes | All 277 baseline files outside the seven reviewed tracked edits are byte-identical, including accepted JSON packs/lessons, QML, simulation domain, persistence/backup modules and VM policy/process/files/runner/image |

Final wheel:
`/tmp/offline-adversarial-wheel/omarchy_learning_lab-0.1.0-py3-none-any.whl`
SHA-256: `68c29f2d3e74476079653100d1ce34a6adfe23e4fbf201490138d99968c030f2`.
Temporary installed environment: `/tmp/offline-image-installed-env`.
Standalone smoke: `/tmp/offline-adversarial-installed-smoke.log`.
Package parity/exclusion summary: `/tmp/offline-adversarial-artifacts.json`.
Source-distribution inspection path is recorded in that artifact summary.
Final 19 candidate hashes: `/tmp/offline-image-adversarial-reviewed-hashes.json`.
UI logs: `/tmp/offline-adversarial-{vm_lessons,text_unit}-{1,1.5,2}.log`.

The initial sandbox build could not resolve pypi.org. Normal elevated approval
allowed the declared dependency build/install in isolated temporary environments;
no system or working application environment was changed. Setuptools 84.0.0,
PySide6/Shiboken6 6.11.2, Python 3.14.7 and gpgv 2.4.9 were used. GnuPG's test-only
agent socket also required normal approval. Ephemeral test keys lived only in
private temporary homedirs and were cleaned up; no production credentials exist.

## Security and compatibility evidence

Tests use small nonbootable payloads and explicitly injected in-process catalogs.
Normal CLI calls have no trust/limit override. Production release/key lists remain
empty; the legacy local descriptor stays active. The current lesson/image/backend
pins and all eight lesson resource bytes are unchanged. A frozen baseline lifecycle
AST comparison permits exactly three new availability-hook calls and the no-op
legacy hook; all remaining lifecycle logic still matches the accepted controller.
Stop, process identity, private QMP, isolation argv and display policy are unchanged.

New coverage includes canonical authorization, real detached signatures, malformed/
ambiguous/wrong-signer status, actual verifier timeout/output overflow children,
unsupported versions/compatibility, compressed and raw hashes/sizes, bounded gzip,
ZIP/ZIP64 local/central agreement, pre-member-read directory/count bounds, duplicates,
unknown names, links, descriptors, comments, encryption, overlap/truncation and
unsupported extras. Importer process guards allow only gpgv, reject socket/shell
access and prove no QEMU invocation. Developer signing/fault fixtures are distinct
from application runtime and never interpret lesson JSON.

Publication tests cover exact no-op, different manifests for identical raw bytes,
changed receipts, legacy no-receipt conflicts, staging/source/destination
substitution, concurrent threads/process locks, a held guest lifetime lock,
short writes, ENOSPC/admission/fsync failures, destination collisions and retry.
Actual child-process abrupt exits before/after directory publication demonstrate
that staging remains inactive or a complete receipt is present, respectively.
Full-image hashing is tested outside the VM operation lock, including duplicate
verification, so import does not hold that lock for a full image hash pass.

Learn/Challenge records remain byte-identical after image/lesson defaults change;
retained revisions resolve exactly. Resume-only blocks new/Reset but permits Resume;
withdrawn blocks boot/Reset without terminating a guest. Unavailable image/lesson
pins and missing retained resources leave verified Stop routable. A controller
fixture exercises the inherited Stop body with synthetic QMP shutdown evidence;
it does not launch a VM or establish native shutdown success.
Rollback reads known legacy records and refuses newer unknown pins unchanged.
Accepted revision digests have permanent regression guards. Existing backup,
authoring, Library, simulation and installed-resource checks remain passing.

## Limits and remaining acceptance

- No public release is authorized; production validate/import deliberately refuses
  all bundles until separately reviewed manifests and keys are shipped.
- Small synthetic fixtures (up to 2.7 MB expanded data) test importer mechanics.
  No 16-GiB public-image import,
  fresh image preparation or eight-lesson release-image playtest is claimed.
- Importer ENOSPC/fsync faults are injected. Abrupt process exits are real, but no
  physical power loss or full-host-filesystem exhaustion was performed.
- Native guest/keyboard/accessibility checks were not run for this backend-only
  batch; the active practice guest was neither used nor stopped. Offscreen results
  are not native acceptance. The owner's specific report that the updated console
  looks better is recorded; it does not approve comprehensive input/accessibility.
- Staging (including failed/duplicate candidates) is retained and consumes space.
  Checks provide no aggregate quota/reservation. Same-user malicious host processes
  remain outside the isolation claim; they can replace application code itself.
- Offline old applications cannot know subsequent withdrawal decisions. Unknown
  pins fail closed; available supported legacy pins do not migrate. VM data remains
  excluded from simulation profile backups.
- Existing shutdown warning remains unchanged and unsuppressed:
  `gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.

## Complete changed-file list

Application/runtime resources:

- `app/learning_lab/vm_preview/bridge.py`
- `app/learning_lab/vm_preview/manager.py`
- `app/learning_lab/vm_preview/registry.py`
- `app/learning_lab/vm_preview/sessions.py`
- `app/learning_lab/vm_preview/catalog_manager.py`
- `app/learning_lab/vm_preview/image_catalog.py`
- `app/learning_lab/vm_preview/image-catalog.json`
- `app/learning_lab/vm_preview/bundle_archive.py`
- `app/learning_lab/vm_preview/bundle_signature.py`
- `app/learning_lab/vm_preview/image_bundle.py`

Tooling/packaging:

- `app/tools/register_vm_image.py`
- `app/tools/installed_smoke.py`
- `app/MANIFEST.in`

Tests (not distributed):

- `app/tests/test_vm_lessons.py`
- `app/tests/offline_image_fixtures.py`
- `app/tests/test_image_bundle.py`
- `app/tests/test_image_catalog.py`

Documentation:

- `app/docs/vm-preview/offline-images.md`
- `app/docs/vm-preview/offline-images-acceptance.md`
