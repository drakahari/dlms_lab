# Optional VM preview acceptance — local review

## Baseline and preservation

Baseline `7a4182315a554c1580d680bec57cae6920cc4723`; initial working tree clean.
Verified recovery snapshot:
`/home/drak/.local/state/omarchy-learning-lab/recovery/vm-preview-source-20261004T013019011938Z`

The archive hash and all 242 baseline file hashes were checked. Only four pre-existing
files changed: `__main__.py`, `qml/Main.qml`, `pyproject.toml`, and
`tools/installed_smoke.py`. Every accepted pack, simulated engine, profile storage and
backup module remains byte-identical. New files implement the separate preview,
recipe, tests and documentation. The initial delivery made no commits, installed-app changes,
real-profile access, original proof changes, new host packages or host settings.

## Verified results

| Check | Evidence / result |
| --- | --- |
| Complete regression suite | **371 passed** (328 original + 43 VM tests). `/tmp/vm-final-review-regression.log` |
| Security/lifecycle fixtures | Descriptor containment, symlink/hardlink/FIFO refusal, path substitution, generation/record collisions, operation and lifetime locks, stale/forged PID records, wrong QMP peer, unsupported QMP calls, unexpected qcow features/backing paths, missing files/journals, old pins, interrupted publication and admission failure. |
| ENOSPC | Injected metadata-publication failure leaves old active record and new orphan evidence. Real QEMU blkdebug/qemu-io fixture returned error 28 with unchanged fixture bytes. No host filesystem was deliberately filled. |
| Live file ceiling | QEMU inherited 18 GiB soft/hard limits. Lowered only on a disposable fault-test process to **12,910,592 bytes**; disk stopped exactly at that size and QMP reported `io-error`. Unclean disk retained. This tests per-file growth, not an aggregate quota or guaranteed reserve. |
| Native guest | Fresh Debian console autologin; learner only in learner/users; root and learner passwords locked, no sudo/SSH server; network only `lo`. 2 CPUs / 2 GiB / 16-GiB virtual disk, fixed no-NIC/no-share command graph. |
| Native lesson | Started sleep, compared jobs/ps, STOP, bg, TERM/wait exit 143. Marker survived disk Resume, disappeared after Reset; retained old overlay hash unchanged. |
| Final integrated app proof | Native Wayland + GTK Start, guidance, self-review, clean Stop, same-generation Resume, deliberately unexpected QEMU exit, unclean Resume refusal, confirmed fresh Challenge Reset and retained crash-disk integrity. Base hash unchanged. All guest processes stopped afterward. |
| UI | 22 checks per run at effective 100/150/200%, separately offscreen and native Wayland. Learn/Challenge, Reset cancellation, focus return, footer reachability, reopen and backup round trip; no QML warnings. Input synthesized through QtTest/QMP. |
| Existing UI regressions | Text-unit acceptance: 250 checks + 8 restart checks at each 100/150/200% offscreen. |
| Core without virtualization | Core app launches/executes a simulated command with QEMU/KVM capabilities unavailable and process creation forbidden by fixtures. No VM root created at normal startup. No new Python runtime dependencies. |
| Installed wheel | Actual isolated setuptools wheel build, separate venv installation, `pip check`, and copied standalone smoke script run with `python -I` from `/tmp`. Bundled VM QML/lesson/image policy/runner present; existing 22 unique collection resources and start/resume/authoring workflows pass without source imports. Not native installed-app acceptance. |

The final wheel is under `/tmp/learning-lab-vm-preview-wheel-reviewed/`; test venv:
`/tmp/learning-lab-vm-preview-wheel-env/`. The first sandbox build hit blocked PyPI
DNS; a normally approved isolated build succeeded. No working installation changed.

Native compositor-assigned sizes differed from requested compact sizes:
100%: 1402×1820; 150%: 935×1213; 200%: 701×910. Native 1280×900 was verified at all
three scales. Exact 800×600 and 1280×900 were verified **offscreen** at all scales.
No host display settings were changed to force a native compact size.

## Images, runtime and evidence

Fresh verified build: `~/.local/share/learning-lab-vm/preview-image-20261004T0209/`.
Registered base: `~/.local/share/learning-lab-vm/preview-v1/images/` plus digest below.
SHA-256: `a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d`.
199-package inventory: [packages.tsv](packages.tsv); SHA-256
`b7fa4bd31fe10f95c7d3b6ea81de07d3099ba039813804260a618ca125a2367d`.
The original installer-trace-contaminated inventory extraction is retained alongside
the corrected inventory; the disk did not change. Earlier failed/minimal build
candidates and all test generations remain retained, not published as usable images.

Native evidence in `/tmp/learning-lab-vm-preview-evidence/`:
`04-corrected-image.png`, `05-resume-and-jobs.png`, `06-reset-marker-absent.png`,
`07-integrated-native-guest.png`, `08-native-app-controls.png`, `native-live.json`,
`disk-limit.json`, `enospc.json`, `reset-integrity.json`, `base-integrity.json`, and
scale-specific UI screenshots/reports. These generated files are outside commit
candidates. The original proof directory was neither adopted nor modified.

Host runtime: Omarchy kernel 7.2.5-3-omarchy, Python 3.14.7, Qt/PySide6 6.11.2,
QEMU packages 11.1.1-1. Guest Debian 13.7.0, kernel 6.12.107+deb13-amd64.
The first new minimal image lacked D-Bus/logind; Stop correctly timed out instead of
claiming success. The replacement fresh build added guest-only dbus/libpam-systemd;
clean ACPI shutdown passed. No correction was applied to the owner's original proof.

## Outstanding / explicit limits

- Physical keyboard, screen-reader/accessibility and exhaustive native combinations
  remain unverified. No owner UAT is represented as passing this new preview.
- Self-reviewed means learner-reported, never guest-verified or scored.
- No hostile-malware isolation claim. No aggregate storage quota, reserved host
  free space, unattended monitoring, automatic repair or retained-disk pruning.
- VM metadata and disks are excluded from current backups/exports. Unclean disks
  cannot Resume; Reset retains them. Older unavailable pins fail closed.
- Local image only: distribution licensing/source obligations, release signing,
  independent rebuild comparison and public delivery are not completed. Rebuilds
  are procedurally reproducible, not claimed bit-identical.
- Baseline warning remains unchanged and unsuppressed:
  `gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.

Use [setup.md](setup.md) for the exact disposable source-launch command. Optional
review: open the preview, Start, type `sleep 300 &` then `jobs -l` in GTK, Stop,
Resume, and confirm Reset. Routine owner review is not a completion gate.


## Final security/compatibility review

Reviewed the source diff, all candidate files, image recipe/build evidence, actual
native reports/screenshots, and wheel payload. The final review authorizes only a
local source commit; the image, working installation and personal profile stay put.
Additional source recovery snapshot (26 pre-review candidate files, verified):
`/home/drak/.local/state/omarchy-learning-lab/recovery/vm-preview-review-20261004T023948`.

In-scope defects corrected:

1. Normal control/recovery now verifies the **entire permitted launch argv**, not
   only a recorded hash, in addition to executable/UID/boot/start identity and QMP
   peer/UUID checks. Duplicate/aliased descriptor sets and altered block graphs or
   network options are rejected even when a record contains a matching hash.
2. Missing or terminal runtime records cannot prove the guest stopped while the
   lifetime lock remains held. A reused PID in an old terminal record is not
   signaled. Interrupted Stop publication and contradictory unclean/clean records
   block Resume and preserve the disk.
3. Root refusal is lazy to the optional VM operation, not core app construction.
   Launcher/image-verification checks no longer disappear under Python `-O`.

Added tests cover those cases, parent-directory substitution, a **real qemu-img
external-data-file image**, and real `qemu-io`/blkdebug ENOSPC. The existing
metadata-publication ENOSPC fixtures still preserve the old active reference.
This does not claim a full host-filesystem exhaustion test, nor power-cut testing
of physical storage hardware. Kernel EFBIG was exercised on the running guest;
ENOSPC was exercised in the real QEMU block-I/O utility and metadata fault fixtures.

Repeatable native security test:

```bash
python3 -B app/tests/vm_security_acceptance.py \
  --vm-home /home/drak/.local/share/learning-lab-vm/preview-v1
```

Latest security evidence: `/tmp/vm-security-review-5q9ojfql/report.json` and
`guest-access-and-listeners.png`. It verifies actual cross-profile rejection,
forged process-digest refusal, recovery of a live interrupted Start, and socket
inodes owned by the exact QEMU process: **no Internet sockets; only its private
Unix QMP listener**. Guest console inspection shows learner/users membership,
NO_SUDO, only lo, an empty `ss -lntu` table, and NO_PRIOR_HISTORY. Locked accounts
and no SSH server were additionally checked against the executed build recipe,
build console and 199-package inventory. The first screenshot attempt began typing
before login was ready; it was rejected as guest-policy evidence and retained.

That live test reads the inherited 18-GiB soft/hard RLIMIT_FSIZE, lowers it only in
its disposable QEMU process, and observes `io-error` exactly at the kernel ceiling.
Force Stop marks the disk unclean; Resume refuses it; Reset retains its bytes;
the pinned base hash still matches. This is a per-file limit, not aggregate quota
or a guaranteed free-space reserve. Monitoring remains best effort.

The native app lifecycle suite was rerun with the revised controller:
`/tmp/vm-final-review-native.log`; its screenshots/report remain under
`/tmp/learning-lab-vm-preview-evidence/`. Final offscreen preview UI checks are in
`/tmp/vm-final-review-ui.log`; unchanged QML retains the separate native/offscreen
scale evidence above. No physical-keyboard/accessibility approval is inferred.

Final isolated wheel: `/tmp/learning-lab-vm-final-security-wheel/`. All **103**
packaged source/resource files were byte-compared against this candidate.
Installation into the disposable venv and the copied `python -I` smoke harness
passed (`/tmp/vm-final-review-wheel-smoke.log`), including core startup with QEMU
capabilities unavailable and host process creation forbidden. No VM image is
needed for simulated labs. Existing engine, pack, storage and backup bytes remain
unchanged; profile backup versions 1/2 are preserved.

These controls do not authenticate mutable host records against a malicious
process already running as the same host user; such a process could also rewrite
application code. This is not a hostile-malware sandbox or tamper-proof assessment.
The native/physical accessibility and public-distribution limitations above remain.
