# Storage unit acceptance — 2026-10-07

Baseline: `6d8098202eebdb8ccb0bfff254ddc9493439685a`, main, initially clean; five existing commits ahead of local origin/main. No push, installation update, real-profile change, host change or production admission was performed.

Evidence and verified recovery snapshot:
`/home/drak/.local/state/omarchy-learning-lab/recovery/storage-unit-20261007T172146943549Z/`.
All evidence, failed runs, isolated profiles and retained disk generations are on the home filesystem, outside Git. The snapshot contains 439 tracked source files, each rehashed against the pre-edit manifest. The original 33-file delivery manifest `storage-unit-reviewed.sha256` is preserved. The focused review saved and verified every original candidate under `focused-review-20261007T211643Z/candidate-before/`; corrected final paths/hashes are in that review directory's `storage-unit-review-final.sha256`.

Runtime: Omarchy 4.0.4, kernel 7.2.5-3-omarchy, Python 3.14.7, PySide6/Qt 6.11.2, QEMU 11.1.1. The native monitor is 2880×1920 at desktop scale 2; test-process scale factors produce effective Qt DPR 1, 1.5 and 2 without changing desktop settings.

## Feasibility and scope

The real disposable-guest probe passed before lesson implementation (`probe-run-5.log`, `discovery-unit-live-0tfvmuh0`). Existing sfdisk/losetup and kernel partition discovery, ext4 creation, mounting, actual learner access, unmounting, offline checking and copy repair work. No package installation, new image, QEMU disk or controller extension was necessary. Every native launch used normal shared exclusion and positively verified task ownership; no owner guest or coordination record was cleared to make a test run.

The unchanged administrator image has SHA-256
`f956d5c98848296f6887235c742ee4cc44ed5981acd0d2efd0a593b16d8a578f`.
Both the original base and private read-only test copy were independently rehashed and remain mode 0444 (`base-hashes-delivery.json`). Existing supplemental administrator provenance remains applicable; the historical descriptor/inventory is not rewritten.

The eight lessons are display-only trusted resources. Completion remains **self-reviewed, unscored**, with independent Challenge goals. Recovery Challenges explicitly explain manual fault preparation: a fresh guest has no preinstalled storage fault. Lesson JSON never executes setup or assessment.

## Initial delivery results (historical)

These results describe the original delivery. The focused review below supersedes lesson/helper and packaged-resource evidence after its corrections; unchanged controller/provenance evidence is reused. Failed runs remain retained.

| Gate | Result and evidence |
|---|---|
| Full regression | **613 passed**, 42.366s; `regression-delivery-final.log`. Includes backup compatibility, legacy sessions, optional startup, registry/catalog bounds and unchanged protected bytes. |
| GNU comparisons | **44 passed**; `gnu-content-final.log`. Expected output/errors/status and relevant final virtual-file state are recorded. Developer fixtures only. |
| Eight lessons, both modes | **16 passing initial delivery pins**; `final-lesson-evidence.json`. First six lessons use `storage-unit-live-dtx68b76`; final recovery lessons were repeated after wording clarification in `storage-unit-live-89ewyzhv`. Static command bytes and every chosen lesson/image pin match initial delivery source. |
| Additional real safety checks | **20 checks passed across four guests**, all cleanly stopped; `safety-native-corrected.log`, `storage-unit-live-evo243yu/report.json`. |
| UI | **935 checks per run**, six runs: offscreen and native Wayland, each at 100/150/200%, 800×600 and 1280×900 logical sizes. `ui-final-summary.json` links screenshots and individual logs. Input is synthesized QtTest, not physical-keyboard or accessibility acceptance. |
| Actual wheel | Built with existing declared build dependencies, installed into a separate environment, pip check passed. Outside-checkout `python -I -B` smoke passed; **198 packaged files** match initial delivery application bytes, all nine units/76 lessons and eight storage resources present. `wheel-content-final.log`, `installed-parity-content-final.json`. |
| Installed native lifecycle | **Start, separate-process restart/same-disk Resume, and confirmed retained Reset passed**, 17/20/22 checks. `installed-native-corrected-{start,resume,reset}.log` and `installed-profile-corrected/run-*/` contain real GTK console screenshots, identity/lifecycle events and reports. Same pins/generation/marker on Resume; Reset preserves prior disk bytes and removes the marker in a new generation. Cross-unit controls and real cross-profile refusal/owning Stop passed in every phase. All three guests cleanly stopped. |

Wheel: `wheels-content-final/omarchy_learning_lab-0.1.0-py3-none-any.whl`, SHA-256 `cacfe3b3ee6b342f53e63cfb8815c0ad6e4fb0d0b67e5d17d9f96e35a348c006`. This isolated installation does not replace the working app.

Real lesson checks include wrong system/foreign/stale device refusal, image collisions, symlink/hardlink substitution, backing-path **and inode** checks, actual permissions/read-only failures, mounted-check refusal, unchanged live fstab, offline copy repair, original hash preservation, independent content/metadata expectations and plain learner reads, repeated setup/cleanup and clean session reopening. Extra cases establish failed-query refusal, actual wrong mapped partition refusal, duplicate UUID rejection before mounting, interrupted exact cleanup, kernel file limits, bounded output and an actual timeout. Final safety test source is retained beside its report.

## Limits and corrections demonstrated

- Two images maximum per exercise, each at most 256 MiB; supplied images are 128 MiB. Admission requires 1600 MiB free and guards retain at least 1 GiB. Unit ceiling: 4 GiB image payload plus 144 MiB logs/notes/capture allowance across eight current workspaces; supplied image payload is at most 2 GiB. Historical VM generations are separate. No aggregate host quota or guaranteed host reserve is claimed.
- Actual worker soft/hard regular-file limit is 268435456 bytes. A larger truncate failed; output capture stopped at 1048576 bytes with explicit overflow status. A 35-second worker was stopped by the 30-second timeout. Writes through loop block devices are bounded by the fixed image/partition geometry, not by RLIMIT_FSIZE. Guest root can override guest-side safeguards.
- A copied filesystem UUID is ambiguous until resolved. Tests reject actual duplicate UUIDs before a UUID mount. A new filesystem UUID does not change duplicated GPT PARTUUIDs; exact-device recovery is required, not PARTUUID substitution.
- Repair is never issued for mounted filesystems. Tested corruption is a controlled inode link-count defect in an offline copy; arbitrary corruption recovery and power-loss repair are not claimed.
- Guards are cooperative accident prevention, not protection against adversarial guest root or concurrent privileged mutation. No raw host disks, live guest fstab edits, broad deletion, force/lazy unmount, detach-all, exhaustion or new host access.

## Retained failures and their resolution

All failed candidates/logs were retained, not counted as passes:

1. Initial private test-directory mode and harness return-type assumptions were corrected in disposable test setup; the launched guest was verified cleanly stopped.
2. An initial superblock-counter fault did not produce the expected read-only checker status; replaced with the tested copy-only inode link-count defect.
3. The initial 1 MiB worker file ceiling blocked GPT writes at the end of a 128 MiB image. A preserved-copy reproducer produced SIGXFSZ/status153. The lesson limit was corrected to the approved 256 MiB ceiling and retested.
4. blkid can return status0 for GPT partition metadata without a filesystem. Blank probing now checks selected TYPE/PTTYPE/USAGE and accepts only the documented status/empty-signature combination before a fresh offline check.
5. Failed mount queries initially looked like an unmounted device. A real guest reproducer demonstrated that defect without a write; the lesson guards now fail closed. All sixteen lesson/mode cases were repeated after this correction.
6. A diagnostic typing attempt hit Bash history expansion before reaching its probe; a quoted repeat demonstrated the actual query issue. A vanished harness PID was refused without sending a signal.
7. Interim GUI runs rejected changed lesson digests during edits; initial native scale expectation mismatched the desktop DPR. Final frozen-content runs pass at explicit effective DPR without global changes.
8. Restricted signing-fixture tests could not start their GPG agent. The full isolated-fixture gate was repeated with normal approved host permissions and passed. Production keys/releases remain empty.
9. The oversized-file safety test correctly hit the kernel limit but then waited at rm's prompt for a root-owned test file (`storage-unit-live-ca7n_p9j`). It cleanly stopped. The isolated harness now precreates that probe as learner; real enforcement and cleanup passed on repeat. No lesson/controller change was needed.
10. The copied installed-native harness still asserted eight units/68 lessons and failed before guest launch. Its isolated copy now checks the approved nine/76; the failed profile/logs remain retained.

Known baseline shutdown warning remains visible:
`gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.
This batch neither suppresses it nor claims it is fixed. The final installed native runs recorded no live Qt warnings; the harness retains its exact known-baseline dialog diagnostic policy rather than suppressing unknown messages.

## Compatibility and outstanding acceptance

All original 68 lesson bytes/identities and image descriptors remain unchanged. Removing the eight new catalog entries/routes gives the exact prior canonical catalog. Controller, process/QMP authority, launch policy, generation handling, backup/session formats, QML and simulated packs/engines are byte-identical. Only registry/retained/default limits and corresponding messages change: nine units, 76 total, 16 per unit; 77 lessons, a tenth unit, 17 per unit and overflowing maps are rejected. Image/key/release/per-image compatibility limits remain 64. Catalog is 47686 bytes; new unit is 64060 bytes, both below the unchanged 65536-byte parser ceiling. Further growth requires a bounded capacity review.

VM disks and guest evidence remain excluded from profile backups. Resume boots a clean existing disk, not prior RAM, jobs, shell variables or loop mappings. Unclean generations remain subject to existing Reset policy. Physical-keyboard navigation, assistive technology and exhaustive owner-native acceptance remain outstanding. Qt/ICU release-compliance blockers and public distribution remain deferred.

See [unit guidance](storage-unit.md) and [coverage inventory](../curriculum-coverage.md). The source batch stays unstaged and uncommitted after focused safety review; no next unit is started.

## Focused adversarial review — corrections and evidence

Review baseline remains `6d8098202eebdb8ccb0bfff254ddc9493439685a`; the five local commits and empty index are preserved. The original manifest matched all 33 candidates before corrections. Evidence below is under `focused-review-20261007T211643Z/` unless a sibling guest directory is named. The verified 439-file pre-implementation recovery snapshot is intact; 421 tracked files outside the approved batch remain byte-identical to baseline.

Findings are ranked by possible **guest** consequences. No controller, QMP, launch-policy, host, base-image or privilege change was needed.

| Severity | Finding reproduced | Narrow correction / refusal proof |
|---|---|---|
| High | An `attach` precondition followed by a semicolon allowed a second loop mapping. An unmounted alias could pass the old offline check while the same backing file was mounted through its first mapping. | Explicit early return; require exactly one backing mapping, matching inode/path, zero offset/size limit and exact partition geometry. Real second-map refusal tested without issuing repair. |
| High | Failed loop queries could look like an empty mapping list; cleanup could report detachment success while a mapping remained. | Successful query required; distinguish error from present/absent. Final cleanup preflights both mapping queries before deleting any file. Injected query failures preserve the full candidate. |
| High | A device mounted somewhere was accepted without proving that the practice path referred to it. | Verify exact device/root at the exact mountpoint with no nested mount. Empty target required before mount; real alternate-mount and note-link cases refused. |
| High | The private fstab trusted a mutable UUID variable separately from verification of the intended partition. A table naming the root filesystem UUID passed the old predicate. | Read the verified partition UUID afresh and compare the exact table entry; unrelated/stale UUID refused. The reproducer tested only authorization, never mounted the root UUID. |
| Medium | Workspace/log membership and cleanup preflight were incomplete; unknown entries could be discovered only after partial deletion. | Literal workspace, canonical paths, bounded learner-owned single-link known members, no unknown/hidden extras; preflight before mutation/deletion. Reject log symlinks, nonempty targets and note symlink/hardlink substitution. |
| Medium | Negated UUID checks conflated query failure with a proven duplicate; repair sequencing could reach a later recheck after a failed initial precondition. | Require explicit duplicate status from both partitions; group repair/recheck behind successful offline validation. Static shell and final real-guest fault-injection tests prove no UUID change/recheck on failure. |

`reproducer.log` and sibling `storage-unit-live-v_mtqkez/` retain four demonstrated original defects and clean shutdown. No destructive repair or root-filesystem mount was used in that reproducer. Corrections are present in the commands displayed to learners, not only in a test wrapper: tests compare every static command array and the first three Learn/Challenge guard definitions exactly. The remaining Challenge fixture text supplies the same attachment/UUID helpers and bounded fault setup, without claiming automatic assessment.

All 16 lesson/mode cases were rerun because shared displayed helpers changed: sibling `storage-unit-live-w5cs09cw/` records **272 checks**, 16 PASS entries, exact pinned content, clean Stops, reopen identity and unchanged base hashes. Every recovery run verifies independent expected bytes, checksum, owner/group/mode and an actual unprivileged learner read; a mount/checker exit alone is insufficient. `native-candidate-parity.json` verifies current source commands and pins against those records.

Additional real safety cases: sibling `storage-unit-live-5qfvyftx/` records 24 checks across four guests; partition/mount/fstab cases match the final commands. Its earlier repair case remains historical and is superseded by `storage-unit-live-9mvt2his/` (**six checks**, final repair fixture). These include query failures, second mappings, wrong mount paths, links, altered UUID tables, exact cleanup, real timeout/output/file-limit enforcement and preserved original content. All guests stopped cleanly. Executed fixture copies and per-command acknowledgement screenshots are retained.

Six new static shell-control-flow regressions use a disposable working directory, no command search path, and stub executors. During development the first stub test lacked an isolated cwd and created two harmless redirected stub-output files; it made no privileged call. Both files and failing results are preserved under `static-shell-precondition-failure/` / `pending-scope-repro.log`. The fixture now asserts that rejection creates no file at all. The final targeted suite passes **17 tests** (`targeted-final.log`).

Final validation against the corrected application/resources:

| Gate | Final result / retained file |
|---|---|
| Regression | **619 passed**, 43.066s; `regression-final.log`. Includes the six additional shell-control-flow tests. |
| GNU fixtures | **44 passed**; `gnu-final.log`. Static developer reference execution only. |
| Actual guest lessons | **16/16**, **272 checks**; `lessons-final.log`, `native-candidate-parity.json`. Both modes; original preservation, contents/metadata/plain learner access, cleanup and clean reopen. |
| Focused safety | Matching partition/mount/fstab cases plus final repair case as identified above; final repair refusal on query/precondition errors demonstrated. |
| UI | **207 checks × six runs**: offscreen and native Wayland at DPR 1/1.5/2, each 800×600 and 1280×900. `ui-final-summary.json` links all reports/screenshots. No recorded QML messages. Source UI unchanged; QtTest input remains synthesized. |
| Actual wheel | Isolated build/install/pip check and outside-checkout `python -I -B` smoke passed; **198 packaged application files** byte-match, nine units/76 lessons, eight exact storage resources. `build-wheel.log`, `installed-parity-content-final.json`. |
| Installed native lifecycle | **17/20/22 checks** for Start, separate-process same-disk Resume and retained Reset; all clean Stops. `installed-lifecycle-final.json`, `installed-native-corrected-{start,resume,reset}.log`. Exact lesson/image pins and generation/marker continuity on Resume; old disk bytes retained and marker absent after Reset. Each phase proves real cross-profile refusal and owning-profile Stop. |

Final wheel SHA-256: `3625bea9cf603c8fe3b7e7133b01bdc54290a2873a614bd2fb54a65d6937d7ba` (`wheels-content-final/omarchy_learning_lab-0.1.0-py3-none-any.whl`). No working installation was updated. Final host-process inspection found no QEMU guest and the normal shared record was `stopped` (`host-processes-final.txt`, `gate-final.json`); no locks/records were bypassed or cleared. Both original and private read-only base hashes match the accepted value (`base-hashes-final.json`).

**Review conclusion:** no remaining blocking finding within the approved storage batch; ready for a separately authorized commit. Exactly 33 source/test/documentation candidates remain unstaged and uncommitted. No profiles, disks, credentials, signing material or generated evidence are included. All original 68 lesson/image pins, controller behavior and backup formats remain unchanged.

Physical-keyboard and assistive-technology acceptance remain outstanding; native automation does not establish them. Long manually entered guard definitions remain a usability limitation of the approved display-only/no-sharing workflow. They were not shortened by dropping safety checks. The known baseline shutdown ResourceWarning remains present in the final regression log and is neither suppressed nor reclassified as fixed.

## Disposable review launch

From `app/`, with the existing Python/PySide6 environment:

```bash
python3 -B -m learning_lab \
  --data-dir /home/drak/.local/state/omarchy-learning-lab/recovery/storage-unit-20261007T172146943549Z/owner-review/data \
  --config-dir /home/drak/.local/state/omarchy-learning-lab/recovery/storage-unit-20261007T172146943549Z/owner-review/config \
  --vm-home /home/drak/.local/state/omarchy-learning-lab/recovery/storage-unit-20261007T172146943549Z/runtime
```

Library → **Real Linux VM preview…** → **Linux Storage: Filesystems, Mounts & Safe Maintenance**. Select a lesson and Learn or Challenge; Start opens the native console. This is optional owner review, not a routine gate. Physical-keyboard/A11y checks still needed: tab/focus/scroll throughout long guards at compact sizes, native console/menu keyboard operation, screen-reader labels and contrast with the owner's theme. Do not start alongside another guest; existing shared exclusion remains enforced.
