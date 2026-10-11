# Offline Network / DNS / Web evidence acceptance

## Baseline, protection and inventory

Started clean on main at `1201aaa69d409f765d54e81cf8ce0b42e35560ca`; fetched live origin/main matched, with no outgoing/incoming commits. The accepted navigation repair remains unchanged.

Verified recovery snapshot:
`/home/drak/.local/state/omarchy-learning-lab/recovery/offline-evidence-20261011T034639363368Z`
(**469** baseline source files, copied/hash verified). Personal profiles were not copied or modified; every mutating check used disposable profiles. Installed app, owner sessions/images and production trust were untouched. No real guest or host service was started for this task.

Before: 5 simulator collections, 30 appearances, 26 unique Linux packs +3 networking labs. After: **8 collections, 42 appearances, 38 unique Linux packs +3 networking labs**. Maximum remains 8 collections/32 labs per collection; overflow rejected. VM inventory/bounds remain **9 units/76 lessons**.

**203** previous application/resource files are byte-identical to baseline (all prior `app/learning_lab` files except the collection index). The first five index descriptors remain exactly equal. All previous packs, engine/QML modules, VM lessons, pins/default maps, controller, images, profile and backup formats are unchanged. New scenario IDs are unique, version 1.0.0, contract 5. Only twelve new packs, three collection manifests and appended index descriptions affect application resources.

## Collection checkpoints and independent review

| Checkpoint | Focused behavior | Independent technical review |
|---|---|---|
| Network, 4 labs | 8 test methods, both modes, wrong/empty/incomplete reports, retry, reset, restart/pins, export/import/backup/isolation | Passed after clarifying header capture as `curl -i` and distinguishing a failed route lookup from an attempted connection |
| DNS, 4 labs | Same focused methods over 8 accumulated labs /16 modes | Passed: negative response categories, AA/RA/RD, real CNAME conflict, parent glue/child answers and separately supplied cache trace |
| Web, 4 labs | Final 10 methods over all 12 labs /24 modes | Passed: scoped listener, Apache address/port/Host order, explicit fatal TLS verification, nginx upstream evidence and timestamp tie semantics |

Independent final review also found no blocker in checker truthfulness, instructional value, profile isolation, bounds, legacy preservation, test count updates or wheel completeness. Interpretation and suggested next checks remain self-reviewed, not keyword graded. Report format is exact and disclosed; equivalent filters/paths are tested. No engine extension was needed.

Failures are retained in recovery, not removed or marked passed. Initial Web proxy validation rejected the Learn route because equal timestamps were in the wrong bytewise record order. Expected output and the explanation of tie ordering were corrected; focused/GNU/UI tests reran. Earlier network UI runs precede its source-labeling correction; only `*-final-*` evidence counts. Several developer-script writes used an incorrect relative working directory and were rejected; corrected absolute paths were used, and a zero-test run was not counted. See `authoring-failures.txt` and `web-focused.log`.

## Final automated evidence

- **642 full non-browser regression tests PASS**, 44.997 seconds: `full-regression.log`.
- **44 existing GNU text fixtures +5 resource fixtures +12 new static text-selection fixtures PASS**. New fixtures compare status, stderr, stdout and resulting virtual report bytes. They do not validate live network/DNS/HTTP/TLS services. Logs: `text-gnu.log`, `resource-gnu.log`, `offline-gnu.json`.
- Source collection UI, each at compact **800×600** and wide **1280×900** logical sizes:
  - Native Wayland: per collection **111 checks +9 separate-process reopening checks** at DPR1; **86 layout checks** at DPR1.5 and DPR2.
  - Offscreen: per collection **110 +8 reopening checks** at DPR1; **85 layout checks** at DPR1.5 and DPR2.
  - Both modes complete through actual UI commands at DPR1. Larger scales check all four layouts, terminal entry, Help/details, scroll exposure and collapse/open behavior; they are not repetitions of every assessment.
- Preserved navigation suite at all three scales, compact/wide and **current Omarchy +built-in fallback themes**: **379 native /378 offscreen checks per scale**. Mouse and synthesized keyboard navigation, selected-row contrast ≥4.5, long titles/lists, Escape/outside click and collection/lesson synchronization pass. The non-quick suite waits **5.3 seconds** across production polling and verifies the open highlighted menu remains intact. No guest is launched; VM Start/Stop/Resume/Reset safety/wiring is covered by existing isolated fixtures, not new guest evidence.
- No QML ReferenceError/TypeError/binding/assignment errors in these UI runs. Actual screenshots and per-check JSON are under `ui/`.

Runtime: Omarchy **4.0.4-1**, kernel **7.2.5-3-omarchy**, Hyprland **0.56.2**, Python **3.14.7**, PySide6/Qt **6.11.2**, Qt Quick Basic/software. Native tests use eDP-1 at host scale2 with QT_SCALE_FACTOR 0.5/0.75/1 and assert actual DPR1/1.5/2. Offscreen uses 1/1.5/2. Host display settings were not changed; only task-window positions/sizes were adjusted.

## Installed wheel, outside checkout

Built using the declared setuptools dependency in an existing isolated build environment, with `--no-index --no-deps --no-build-isolation`; installed into a **new** user-local test venv with existing PySide6. No system packages or working installation changed. `pip check` passed (the unwritable pip-cache warning remains recorded; no permission changes).

Wheel SHA256:
`9a935b5314f8e31a3176e6c618a307fbc0f8fe65ace474bd5cde025d4817386d`

All **219** packaged Python/QML/JSON/text/icon resources match the candidate bytes, including all twelve packs and three manifests (`wheel-package-hashes.json`). Copied `installed_smoke.py` runs with `python -I -B` outside checkout/examples: all8 collections/38 unique Linux packs load, all12 new activities complete both modes, and a separate process reopens exact saved attempts. Core startup with QEMU unavailable and authoring/legacy resources remains functional. VM guest-boot claims are deliberately false in this smoke.

Installed-wheel native Web collection: **111 checks +9 separate-process reopening checks PASS**, all four lessons/both modes, compact/wide at DPR1, from `installed-run/` using the wheel-installed interpreter. This is native QtTest evidence, not physical-keyboard or native-file-dialog approval. Installed smoke and native logs are retained.

## Representative actual screenshots

These links point to retained disposable-profile evidence outside Git; generated PNGs are excluded from the source commit.

- [Native Network collection, compact DPR1](/home/drak/.local/state/omarchy-learning-lab/recovery/offline-evidence-20261011T034639363368Z/ui/network-native-final-1-collection-800.png): wrapped heading in the scrollable Library.
- [Native DNS lab, wide DPR1.5](/home/drak/.local/state/omarchy-learning-lab/recovery/offline-evidence-20261011T034639363368Z/ui/dns-native-final-1.5-lab-0-1280.png): source Help, non-modal details and command entry.
- [Native TLS lab, compact DPR2](/home/drak/.local/state/omarchy-learning-lab/recovery/offline-evidence-20261011T034639363368Z/ui/web-native-final-2-lab-2-800.png): readable terminal/input while details has independent scrolling.
- [Installed-wheel Web Challenge assessment](/home/drak/.local/state/omarchy-learning-lab/recovery/offline-evidence-20261011T034639363368Z/ui/installed-web-native-assessment-Challenge.png): factual-report score, not verified diagnosis.

## Outstanding acceptance and boundaries

Physical keyboard, wheel/trackpad scrolling, screen-reader/accessibility certification and native file-dialog acceptance remain **unverified**. Automated input does not establish them. Owner approval of the earlier navigation fixes is not extended to these twelve activities.

Known baseline warning retained, not suppressed or claimed fixed:
`ResourceWarning: gc: 5 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them`.
This content-only batch does not expand scope to fix it. Qt/ICU redistribution and other public-release obligations remain open. No public release, real service assessment, guest changes or full LPIC objective coverage is claimed.

Task-owned UI windows/processes were closed on completion. Profile fixtures and generated evidence remain excluded from Git. Exact reviewed paths/file hashes and canonical scenario identities are in recovery (`reviewed-files.sha256`, `final-inventory.json`). Commit/push results are reported separately; pushing source does not update the installed app or publish a VM bundle.

## Safe owner launch and short check

Run from your current graphical session; this creates/reuses only the disposable review profile:

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -B -m learning_lab \
  --data-dir /home/drak/.local/state/omarchy-learning-lab/recovery/offline-evidence-20261011T034639363368Z/owner-review/data \
  --config-dir /home/drak/.local/state/omarchy-learning-lab/recovery/offline-evidence-20261011T034639363368Z/owner-review/config \
  --vm-home /home/drak/.local/state/omarchy-learning-lab/recovery/offline-evidence-20261011T034639363368Z/owner-review/vm
```

1. In Library expand each new **Offline Evidence (Simulator / Offline snapshots)** collection; all four labs are available without importing or a VM.
2. Choose a lab, read `reference.txt`/`HELP.txt`, follow Learn or independently extract the Challenge report; Submit after `cat report.txt`. Compare your explanation separately.
3. Try an incomplete report, retry, Reset, then close/reopen using the same command. Practice keyboard/scrolling as desired; no further routine owner walkthrough is a completion gate.

The [twelve-lab guide](lpic-2-offline-evidence.md) lists every outcome, checked fact, self-review question and honest objective mapping.
