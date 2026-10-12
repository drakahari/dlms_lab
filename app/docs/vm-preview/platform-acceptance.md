# Two-image platform expansion acceptance

Verified 2026-10-12 against baseline main
`d5dcad728a7e2de3bae5d2444354bd43b5fe153f`.

Recovery and persistent evidence root:
`/home/drak/.local/state/omarchy-learning-lab/recovery/platform-expansion-20261012T020417739056Z`.
The original 553-file recovery snapshot verifies exactly. Of 181 protected runtime
files, only the five approved registry/catalog/index/caption integration files
differ. Original 102 lesson bytes, old descriptors, revisions and defaults are
exact. Existing catalog formatting changes are whitespace only.

## Delivered scope and bounds

- Ten **Locale, Encoding, Time & Offline Jobs** lessons and eight **RPM & Offline
  Package Administration** lessons; both modes are self-reviewed and unscored.
- Independently finalized Debian foundation and Alma learner candidates. Existing
  images, personal profiles, owner sessions and installed app are untouched.
- 14 units / 120 lessons / 16 per unit; retained/default maps bounded at 120.
  Unchanged limits: 64 per-image lesson revisions, 64 images/keys/releases,
  65,536 bytes, 8,192 nodes and depth 32. Independent boundary fixtures reach the
  intended validators, including acceptance and immediate overflow.
- Serialized catalog: **62,075 bytes; 3,461 bytes headroom**, above the required
  2 KiB. Original parsed descriptors and canonical lesson digests are preserved.
- No controller, QMP authority, launch policy, session/disk/backup format,
  simulator engine or host-configuration changes. Production keys/releases empty.

## Image and native feasibility evidence

The [provenance index](platform-image-provenance.json) binds exact images,
inventories and authenticated source/notice manifests. Normal boot independently
matches **206 Debian packages / 190 Alma software packages**. Alma additionally
has the separately validated vendor public-key RPM record; 190 is not the total
RPM-database record count. The separate builder has 283 software packages.

Normal boot verifies locked passwords, approved guest-only root sudo, Alma
SELinux Enforcing, only loopback, no TCP LISTEN entries, no NIC/shares and clean
Stop. Zero TCP listeners is not a claim that local Unix sockets are absent.
Guest root can override cooperative path guards and guest-side limits.

Checkpoint C uses actual disposable guests, not package-list inference:

- Locale precedence, strict conversion, collation and timezone rollback; a fresh
  getty login observes the changed default, followed by exact rollback.
- xz restored bytes, truncation refusal and real low-memory refusal. xz 5.8 reports
  “Memory usage limit is too low for the given filter setup”; it reports 674 MiB
  required against the imposed 1 MiB limit.
- at identity, specific policy denial, wrong-owner cancellation, finite result,
  working directory, umask, locale, file limit, status and exact policy rollback.
- RPM actual dependency/configuration/integrity/removal transactions, unchanged
  unrelated packages and learner/sudo policy. A resolved foreign e2fsprogs removal
  is rejected before execution; same resolved DNF object is inspected and applied.
- Actual 60-second confirmation expiry and owned interruption preserve state.
  Actual helper process limit is observed; separate kernel EFBIG exercises the
  file limit, not a claim that this fixture exhausted the helper's RPMDB write.
  RPMDB headroom was measured before admission. Logical retention and free-space
  admission are not an aggregate quota or guaranteed free-space reserve.

## Final gates

| Gate | Result | Retained evidence |
|---|---|---|
| All 18 lessons, Learn and Challenge | **36 passing cases** | `platform-final-native-lesson-bindings.json`: 20 foundation and 16 RPM records bind exact resource and entry hashes. |
| Final full regression | **731 passed, 53.357 s** | `platform-final-regression-after-native-fixes.log` |
| Static GNU comparisons | **44 text / 5 resource / 12 offline-evidence passed** | `platform-final-text-gnu-reference.log`, `platform-final-resource-gnu-corrected.log`, `platform-final-offline-evidence-gnu-corrected.log` |
| Actual wheel build/install and dependency check | **Passed** | Candidate 2 wheel, isolated venv 2, `platform-pip-check-2.log` |
| Installed resources outside checkout | **270 packaged files equal source; smoke passed** | `platform-wheel-resource-parity-2.json`, `platform-installed-smoke-2.log` |
| Installed native lifecycle, both images | **All six phases passed** | `platform-installed-native-final-driver-report.json`; Start, separate-process same-disk Resume and retained Reset for each image. |
| Native UI at 100/150/200% | **379 checks at each scale** | `platform-native-ui-driver-report.json`, `platform-navigation-native-{100,150,200}.log` |
| Offscreen UI at 100/150/200% | **378 checks at each scale** | `platform-navigation-offscreen-{100,150,200}.log` |

Native lifecycle uses the isolated installed wheel from outside the checkout.
Each phase verifies exact package/resource/lesson/image pins, normal shared
exclusion, real cross-profile refusal, running-lesson controls after selection
changes, guest files and clean owning Stop. Resume preserves the generation and
expected bytes across separate application processes; Reset retains the previous
disk byte-for-byte and boots a fresh generation. No RAM/job restoration is claimed.

Both supported themes and logical 800×600/1280×900 windows are checked for contrast,
wrapping, selector focus, long lists and refresh persistence beyond five seconds.
Native Wayland monitor: 2880×1920 at desktop scale 2. Application factors
0.5/0.75/1 produce verified DPR 1/1.5/2. Only task-owned windows are floated/resized;
no desktop setting is changed. Input is synthesized, not physical keyboard or
wheel/trackpad acceptance. Screenshots remain outside Git alongside reports.
GNU text fixtures do not establish DNS, DNF, at, xz or kernel/service behavior.

## Retained failures and corrections

No failed disk became an accepted base; evidence was neither overwritten nor
silently discarded.

- Failed preparations 1–7 are retained. Candidate 6's executable, full argv,
  disk and start identity were checked against its specific approval immediately
  before SIGTERM. It exited without SIGKILL. Its disk is **unclean and must not be
  reused/admitted**. Shared exclusion was acquired only after verified exit.
- Native source harness: Alma's bracketed prompt failed a Debian-only readiness
  expression; another run failed on multiline keyboard delivery. Both guests were
  cleanly stopped. Test-only delivery was corrected, retaining exact payload SHA
  and strict per-step acknowledgements.
- RPM cleanup: the test runner did not supply APPLY for its controlled variable
  operation. The helper correctly refused at its 60-second deadline. Exact test
  delivery was fixed and affected transactions repeated successfully; the helper
  gained no exception or weaker check.
- Installed native first RPM Start: `clear: command not found` failed strict
  command readiness. This frozen minimal image has no clear utility. The owning
  guest was cleanly stopped and all evidence retained. Test-only `printf` of fixed
  VT clear/home escapes replaced that unsupported harness assumption. Fresh
  profiles then passed all six lifecycle phases. No package/image change.
- Early restricted runs could not use local socket/GPG fixtures; permitted runs
  pass. Wrong script-name/working-directory attempts are retained as invocation
  errors, not application successes or failures.

Independent review added source/result collision guards, finite-job no-clobber,
failed-creation early returns and fail-closed xz scaffolding. Actual both-mode
runs exercise setup collisions, preserve the result sentinel, and verify
repeated-cleanup refusal without package changes. Installed readiness requires a
successful command; final PASS requires an existing private regular nonlink
learner-owned sentinel. Disk hashes stream, and provider checks require exact
bash output. No assertions were weakened to obtain passes.

## Independent review and remaining limitations

Independent review covered content accuracy, helper transaction restrictions,
original pins, bounds, runtime integration and installed harness. It found no
remaining substantive blocker after corrections. Documentation now accurately
separates already registered isolated review images from the legacy original-image
registration tool, and distinguishes package inventory from source closure.

Physical keyboard, wheel/trackpad, screen-reader/accessibility and exhaustive
platform acceptance remain outstanding. The diagnosed shutdown warning is
unchanged and unsuppressed:

`gc:0: ResourceWarning: gc: 5 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`

Qt/ICU obligations, including the recorded signing-key warning, and Alma
package-specific embedded-component/notice review remain open (40 binary notice
provider gaps). Corresponding signed sources do not alone resolve every
redistribution obligation. These are local development candidates, not public
releases or comprehensive LPIC preparation. DNF4 is not YUM, DNF5 or Zypper
proficiency. Completion does not automatically verify learner reasoning.

See the [unit guide](platform-unit.md) for exact reusable disposable launch
commands and a short optional walkthrough. Final candidate hashes, preservation,
base hashes, independent review and process cleanup are retained in the recovery
root; disks, trust material, private profiles and runtime evidence are excluded
from source commits.
