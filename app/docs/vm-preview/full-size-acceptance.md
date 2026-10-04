# Full-size offline import and native Stop acceptance

The following records the first failed attempt. See the final results section
below and [enumeration review](directory-enumeration-review.md) for the approved
correction and subsequent acceptance. Original failed evidence is retained.

Baseline: `b080d589cfcbd9d6b6f98b8e6280369fa72c3c0e`.
This is local acceptance evidence, not a public release or permission to distribute
an image. Runtime application files, production trust, installed app and owner
profiles were not changed. Test/harness changes remain uncommitted.

## Recovery and isolated paths

Verified source-only recovery snapshot: 296 tracked files at
`/home/drak/.local/state/omarchy-learning-lab/recovery/full-size-source-20261004T201528956514Z`.

All large test artifacts and evidence are retained at:
`/home/drak/.local/state/omarchy-learning-lab/recovery/offline-image-acceptance-20261004T2020-a73c`.

The input was the approved read-only prepared image:
`/home/drak/.local/share/learning-lab-vm/preview-image-20261004T0209/prepared.raw`.
The existing registered base under `preview-v1/images` was read only for integrity
checks. No original proof disk, practice overlay or personal profile was copied.

The test ran the unchanged wheel-installed importer in
`/tmp/offline-image-installed-env`, outside the checkout, through its existing
in-process `_catalog` injection. There was no CLI trust override, signature/hash
bypass, fake filesystem or patched publication success. The streaming builder
uses 1-MiB reads, exclusive outputs, a compressed-size bound and the exact retained
image descriptor. It creates test metadata/signatures without changing image bytes.

## Actual results

| Check | Result |
|---|---|
| 80-GiB admission | PASS; approximately 828.81 GiB available at start |
| Initial prepared and existing registered base hashes/modes | PASS; exact 16 GiB, read-only |
| Streaming bundle creation | PASS; 84.892 seconds |
| Complete 16-GiB validation without installation | PASS; 27.614 seconds |
| Production CLI rejects test-signed bundle | PASS; exit 1, empty release allowlist refusal |
| Full-size import | **FAIL CLOSED**, before publication |
| Diagnostic import retry, new ephemeral signature | Same failure; original evidence retained |
| Duplicate/no-op full-size import | NOT RUN; no successful installation exists |
| Final source, existing base and both staged raw hashes | PASS; all match the accepted pin |
| Native Start/Stop/Resume and unavailable/withdrawn Stop routing | **NOT RUN**; no published isolated test image |
| Existing coordination record | Byte-identical before/after; no control operation sent |
| Regression suite | 473 passed, 12.424 seconds (469 prior + four streaming tests) |

The full-size run failed with:

```text
Refused: Staged image members changed after validation; publication refused
```

A diagnostic retry observed the real `Directory.names()` return values without
changing them or bypassing any validation. Its first call during sealing returned
`[]`; the next call returned all eight completed members. The consistency guard
correctly refused publication. Reopening and reading the retained stage afterward
finds all eight members and its content/identity verification passes.

A four-file probe reproduces this on the home Btrfs filesystem (compressed with
zstd): open a new directory descriptor, write/fsync files through it, fsync the
directory, and list it. The first listing is empty, later listings contain the
files. The same probe on `/tmp` tmpfs returns the files on its first call. This is
not a demonstrated decompression or raw-size error. The precise kernel/runtime
cause is not yet established. The prior synthetic suite used temporary files on
tmpfs and did not expose this filesystem-specific behavior.

No production fix, pre-reading workaround, retry-until-success, or guard weakening
was applied. Correcting the shared descriptor-directory enumeration helper and
adding a home-filesystem regression requires separate approval. Full-size import
and native lifecycle acceptance remain open until that correction is reviewed and
both runs pass. A successful synthetic QMP fixture is not native lifecycle evidence.

## Integrity, resource use and retained evidence

Accepted raw SHA-256 (prepared source, existing registered base, both staged copies):
`a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d`.

First test bundle SHA-256:
`90a248ce374870f705be314025f63ee0c08d4646a6cad6eebd412b5e487e7b22`.

- Raw payload: 17,179,869,184 bytes (16 GiB).
- Compressed payload: 476,712,619 bytes; bundle: 476,721,837 bytes.
- First run to failure: 155.094 seconds; process peak RSS: 28.51 MiB.
- Retained files after diagnostic retry: 33.33 GiB by summed `st_blocks` accounting.
  This includes two complete staged bases and compressed test artifacts. On this
  compressed Btrfs filesystem that is not a measurement of exclusive physical
  space. Final filesystem free space was approximately 825.36 GiB. No quota or
  space reservation is claimed.
- `vm/images/` is empty. Staging directories were not promoted, deleted or repaired.
- Ephemeral signing homes/private keys were removed by their fixture cleanup.
  No production key or allowlist was created. The first runner did not preserve its
  public key; the diagnostic retry retains its public key and in-memory test catalog
  under `diagnostic/`. The runner now retains these public test artifacts for future
  attempts; that evidence-retention addition has not received a second full-size run.

Evidence under the private root:

- `evidence/report.json`, `full-size-run.log`, `production-cli.txt`
- `evidence/final-integrity.json`, `native-blocked.json`, `regressions.log`
- `diagnostic/directory-observations.jsonl`, `small-directory-reproduction.json`
- `diagnostic/test-public-key.gpg`, `test-catalog.json`, `retry.llvmimage`
- `evidence/diagnostic-retry.py`, `diagnostic-retry.log`

## Native portion and remaining work

The normal elevated execution mechanism exposed the initial host process namespace
(PID 1 `systemd`, 1,045 visible processes); no QEMU was observed during that inventory.
This removed the earlier visibility blocker. Native shared-lock acquisition and
actual guest launch were not attempted after import failed. The owner's saved
coordination record remains unchanged, including its pre-existing `unclean` state.
No guest was started, stopped, signaled or force-stopped during this batch.

`tests/offline_image_native_stop.py` is a prepared but **unexecuted** harness. It
requires a successful full-size report, reliable host visibility, no existing QEMU,
and the normal shared exclusion locks. It preserves prior coordination evidence,
uses the existing controller unchanged and never deletes/replaces coordination
records to bypass a blocker. Normal controller lifecycle writes would occur only
for its own authorized test session after those checks. A QMP observation subclass
calls the real peer verification and original powerdown implementation, recording
actual SHUTDOWN events and process exit; it never fabricates success or force-stops.

The planned cases remain: normal clean Stop and same-profile application restart/
disk Resume; then real Stop while the pinned release is withdrawn, image revision
is unavailable, or lesson revision is unavailable, including selection of another
lesson. Native screenshots, real guest shutdown, lifecycle journals, physical
keyboard and accessibility acceptance remain unverified.

The unchanged baseline shutdown warning remains recorded and unsuppressed:
`gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.

## Corrected full-size acceptance (2026-10-04)

The owner authorized the shared enumeration correction after the failure above.
See `directory-enumeration-review.md` for the controlled reproduction and security
review. Only `learning_lab/vm_preview/files.py` changed in application runtime;
all other 118 packaged application files remain byte-identical to the baseline.
The publication guard, exact-member checks and production trust are unchanged.

New isolated artifact root (earlier failures remain untouched):
`/home/drak/.local/state/omarchy-learning-lab/recovery/offline-image-fixed-20261004T2050`.

An actual wheel was built with the declared build dependency and installed into
`/tmp/enumeration-installed-env`; `pip check` passed. All 119 packaged application
resources match the candidate source. No test harness, test keys, guest disks or
runtime records are packaged. `installed_smoke.py` was copied outside the checkout
and run with the venv's `python -I -B`; packaged resources, optional startup without
QEMU/image, scenario start/resume, retained VM pins and empty trust checks passed.
The full-size and native harnesses also run this installed wheel outside the checkout.

| Full-size check | Corrected result |
|---|---|
| 80-GiB free-space admission | PASS; 825.34 GiB available initially |
| Original prepared/existing registered base before and after | PASS; exact hash, size and read-only mode |
| Full 16-GiB validation, without creating VM storage | PASS; 36.843 seconds |
| Empty production allowlist rejects test-signed bundle | PASS; exit 1 |
| Full-size transactional import | PASS; 36.856 seconds |
| Imported raw base, manifest, receipt and descriptor | PASS; exact expected eight members |
| Exact duplicate import | PASS; `already-installed`, 45.666 seconds |
| Duplicate preserves registered file hashes and inodes | PASS |
| Production keys and release allowlist remain empty | PASS |
| Ephemeral private test-signing home removed | PASS; public test evidence retained privately |

Total run: 261.026 seconds. Peak RSS: 29,605,888 bytes (28.23 MiB).
Minimum sampled available filesystem space: 882,457,858,048 bytes (821.85 GiB).
Retained file allocation reported by summed `st_blocks`: 35,313,389,568 bytes
(32.89 GiB), including the duplicate's retained stage. This is not exclusive
physical usage on compressed Btrfs. No quota or free-space guarantee is claimed.

Raw source/imported pin remains:
`a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d`.
New test bundle SHA-256:
`7d54209fe9143fd30ed57a3d1c5d0da81bb6d886da135973d3116284ffe8277d`.
It contains a 17,179,869,184-byte raw payload; compressed bytes 476,712,619;
ZIP bundle bytes 476,721,837. This is a full-size **local test artifact**, not an
admitted production release or a redistributable licensed bundle.

### Native harness failure retained

The first native attempt acquired normal shared exclusion and opened the disposable
app, but timed out during pre-launch hashing. It launched no QEMU, wrote no session
record, and left the previous coordination record byte-identical. Its report and
screenshot remain in `evidence/native-active/`.

A minimal two-second hashing-worker probe identified the harness wait issue:
`QTest.qWait(30)` allowed 67 blocks; event processing plus `time.sleep(.03)` allowed
33,305. The QtTest loop was starving the Python worker through the GIL. The harness
now explicitly yields while waiting; it still uses the actual worker, unchanged
90-second deadline, actual controller, process identity and QMP shutdown path.
A unique run-label retains earlier reports rather than overwriting them. This is
a harness fix, not a runtime/QMP change or substituted success.

### Native results: all four cases passed

The yielding harness launched the actual installed app on Wayland and QEMU's GTK
console using the successfully imported base and one new disposable generation.
Each later invocation closed/reopened the application and booted that same cleanly
stopped disk (disk Resume, not RAM/job restoration). All controls were activated
through QtTest against the real QML. No mock Start/Stop result or forced shutdown
was used.

| Case | Result | Evidence |
|---|---|---|
| Fresh active lesson, switch selected lesson, normal Stop | PASS; 28 checks | `native-active-yielding/` |
| Reopen/Resume, withdraw pinned release while running, Stop | PASS; 32 checks | `native-withdrawn/` |
| Reopen/Resume, make image revision unavailable, control-only Stop | PASS; 33 checks | `native-missing-image/` |
| Reopen/Resume, make lesson revision unavailable, control-only Stop | PASS; 33 checks | `native-missing-lesson/` |

Availability changes were confined to the disposable manager's **in-memory** test
catalog after boot. They did not edit production resources, delete image/lesson
files, or admit untrusted content. Each unavailable/withdrawn case then verified
that Start and Reset were refused without changing the pinned attempt. Selection
of another lesson kept the running lesson identified and disabled a second Start.

Every case recorded a real QMP `SHUTDOWN` event with `guest: true`, reason
`guest-shutdown`, verified process exit, and `stopped` runtime/generation journals.
The QMP observer delegated to the original constructor and powerdown method,
including peer/UUID checks. Saved attempt bytes, exact image/lesson pins, Learn
mode and the unset self-review completion remained unchanged across Resume/Stop.

Final host inventory: no QEMU processes; normal operations/lifetime locks available;
test runtime and generation cleanly stopped. One retained overlay is 17,760,256
bytes logically, 17,698,816 bytes by `st_blocks`. App peak RSS was approximately
241–242 MiB in successful native cases; guest memory was configured at 2 GiB, not
a measured peak resident-set claim.

No practice guest was present during any native preflight. No existing session,
old run directory or coordination file was deleted/repaired to gain access. The
pre-existing terminal coordination record was archived with its exact hash before
normal controller Start published this test's runtime record. The shared gate now
contains the last **stopped test** record as expected from normal lifecycle use;
it was not replaced with an old record after testing. The initial hashing timeout
left that original record unchanged, as separately recorded.

Evidence in the new root includes `native-final.json`, per-case `result.json`,
`preflight.json`, guest and Lab screenshots, exact QMP events and process identities.
Screenshots show the real Debian learner console. No learner commands or completion
were entered. These prove native rendering and lifecycle routing, not physical
keyboard, assistive technology, comprehensive display scaling or lesson assessment.

### Final compatibility gates and remaining limits

- Full suite: **485 passed**, 12.673 seconds (469 baseline + four streaming tests +
  twelve enumeration regressions).
- Twelve focused enumeration tests also passed on the actual home filesystem.
- VM UI suite: **75 checks at each of 100%, 150%, 200%**, compact/wide sizes,
  offscreen QtTest input, no QML warnings. Not native scaling acceptance.
- Installed-wheel resource/start/resume smoke and `pip check`: passed; 119 resources
  match the candidate. Existing baseline optional-without-QEMU, backup exclusions,
  pins, security-controller and import rejection/race/failure gates passed.
- All six source/existing/imported/retained 16-GiB raw copies are rehashed in
  `final-integrity-after-native.json`; all must match the unchanged accepted pin.
- Production signing keys/release allowlists remain empty. No release image was
  prepared or published; licensing, production signing and distribution are still
  separate work. Full-size success uses isolated test trust and the existing local
  prepared image; it does not certify every possible release bundle.
- Earlier failures and all large candidates remain retained. Known baseline GC
  shutdown warning remains unsuppressed. Physical keyboard, accessibility and
  exhaustive native scaling remain outstanding.
- Working installation, real learning profile, proof VM and existing images/sessions
  were not updated. All source changes remain unstaged and uncommitted.

Changed files (nine total):

1. `learning_lab/vm_preview/files.py` — narrow enumeration/identity correction.
2. `tests/test_vm_directory_names.py` — twelve filesystem regressions.
3. `tests/test_vm_lessons.py` — reviewed helper hash; other security guards retained.
4. `tests/offline_image_fixtures.py` — bounded streaming test bundle builder.
5. `tests/test_image_streaming.py` — four builder/import regression tests.
6. `tests/offline_image_fullsize.py` — opt-in full-size installed-package harness.
7. `tests/offline_image_native_stop.py` — opt-in real lifecycle harness and yielding wait.
8. `docs/vm-preview/directory-enumeration-review.md` — cause, callers and safeguards.
9. `docs/vm-preview/full-size-acceptance.md` — chronological failed/passed evidence.
