# Locale, Encoding, Time & Offline Jobs / RPM & Offline Package Administration

These two real-guest units add ten and eight activities to the accepted twelve
units/102 lessons. Sequence is guidance, not an unlock. Completion is visibly
**self-reviewed and unscored**; developer tests verify known fixtures, not a
learner’s reasoning. Simulated commands remain in their separate engines.

## Before starting

Use a disposable profile and the exact prepared local image for the selected
lesson. Missing images fail without substitution. Existing lessons and sessions
retain their exact previous image and content pins. No network, host shares,
clipboard, remote login or new host privileges are used. Guest root can override
guest-side limits and cooperative path guards.

Read Local Shell, Text & Archive, Users/Access and Cron/Timers first. Record each
unique guest workspace and any root-only snapshot path before logging out.
Resume boots the same disk; it does not restore shell variables, RAM or jobs.
Restore displayed shell definitions against the recorded path, inspect retained
evidence, and refuse collisions. Reset retains the old generation and starts
from the pinned base; it is not policy rollback within the current disk.

## Foundation unit

| Order | Activity | Retain and explain |
|---|---|---|
| 1 | Choose the locale scope deliberately | LANG/category/LC_ALL precedence, unchanged parent/default, one-command correction. |
| 2 | Compare localized formats without corrupting data | Decimal/weekday/currency metadata; actual C/German sorts and original UTF8 bytes. |
| 3 | Convert text strictly and preserve a recovery path | Explicit source encoding, independent Latin1 octets, round trip, ASCII refusal and partial output. |
| 4 | Make a guest locale default reversible | Protected resolved-target snapshot, unchanged old shell, actual new login, byte-exact rollback. |
| 5 | Interpret timezones without changing the clock | Fixed winter/summer UTC instants, offset, epoch continuity, exact original link restored. |
| 6 | Inspect an xz stream and recover exact bytes | Bounded compression/inspection, rejected truncated stream, low-memory refusal, independent restored bytes. |
| 7 | Inspect and cancel the exact one-off job | ID/owner/body, only owned cancellation, cancelled output absent after deadline, comparison job retained until its cleanup. |
| 8 | Prove a one-off job’s environment and result | Actually failed environment, preserved failure, corrected UID/cwd/umask/locale/limit/status/result. |
| 9 | Test scheduler access as the intended identity | Specific denied identity, allowed actual execution, wrong-owner cancellation refusal and exact policy rollback. |
| 10 | Deliver a localized offline job handover | Correct encoding and summer timezone facts, finite owned job result, preserved originals and self-reviewed interpretation. |

Jobs use `at -M`; no mail delivery is claimed. Observation deadlines, finite
children and output limits are explicit in each lesson. Cancellation compares a
harmless job scheduled thirty minutes ahead; finish within the fifteen-minute
comparison budget or inspect/recover rather than claiming a vanished job was
preserved. The exact separate comparison cleanup is mandatory.

At-access uses existing locked practice identities via root `runuser`. A locked
password or nologin shell does not establish an at.allow/deny denial; the actual
specific scheduler result is checked. Learner sudo remains root-only, so a
nonroot `sudo -u` password prompt is not accepted as scheduler evidence.

## RPM unit

| Order | Activity | Retain and explain |
|---|---|---|
| 1 | Identify RPM package state and file providers | Actual NEVRA, source/license fields, installed bash provider versus unowned archive. |
| 2 | Inspect an offline RPM before admitting it | Three exact unsigned hashes, paths/metadata/requirements, no scripts/triggers, truncated private-copy refusal. |
| 3 | Observe a dependency failure without forcing installation | Same root-context test/actual refusal, unchanged inventory, report requires data2. |
| 4 | Resolve the offline fixture dependency explicitly | Concrete forbidden-operation refusal, exact pair plan, deliberate APPLY and actual report bytes. |
| 5 | Retain edited configuration during an RPM upgrade | Original/local edit, data1→data2, configuration retained and .rpmnew preserved. |
| 6 | Repair package-owned contents with independent verification | Real rpm -V failure, reinstall, expected data SHA and unprivileged read, unchanged configuration. |
| 7 | Remove only intended packages and explain retained files | Dependent-removal refusal, report then data, .rpmsave and unrelated note preserved. |
| 8 | Repair an offline package incident and hand it over | Reject misleading handover/invalid upgrade, repair actual data2, independent report/config/content verification. |

The visibly invoked fixed helper supports only `status`, and `preview`/`apply`
for data1, pair, upgrade, reinstall, remove-report and remove-data. There is no
data2 operation. It validates the actual resolved DNF transaction and applies the
same object; `--no-download` alone is not the transaction boundary. Confirmation
expires after sixty seconds. The three unsigned fixture archives have narrowly
scoped local verification treatment, not a general official-package exception.

The fixture configuration uses %config(noreplace); removal may produce .rpmsave.
Preserve and compare exact regular single-link candidates before their explicit
removal. Cleanup queries accept only the specific missing-package result, not
arbitrary nonzero errors. Helper records and private workspaces remain evidence;
there is no broad recursive deletion or silent retry of an interrupted transaction.

## Coverage and omissions

Verified 2026-10-12: [LPIC-1 active5.0 /101-500,102-500](https://www.lpi.org/our-certifications/exam-101-102-objectives/)
and [LPIC-2 active4.5 /201-450,202-450](https://www.lpi.org/our-certifications/exam-201-202-objectives/).
Locale/encoding are partial107.3, at is partial108.2 (the earlier planning107.2
mapping was an error:107.2 is X11). Timezone configuration is only the relevant
107.3/108.1 subskill, not clock/RTC/NTP administration. xz reinforces103.2/103.3
and partial206.2. RPM practices portions of102.5; DNF4 is not original YUM,
DNF5 or Zypper proficiency. No complete objective, exam readiness or endorsement.

No packages, authentication policy, clock or source image are changed by app
lesson selection. Commands are display-only practice instructions inside the
approved guest, not executable imported lesson actions or host commands.

## Reusable local review profiles

These commands use the already registered isolated candidates. They do not
replace the installed app or its profile. Run only one guest at a time and Stop
it before switching VM homes. A new profile does not mean the shared guest lock
can be bypassed.

```bash
cd /home/drak/Documents/dlms_lab/app
review_root=/home/drak/.local/state/omarchy-learning-lab/recovery/platform-expansion-20261012T020417739056Z
QT_QPA_PLATFORMTHEME='' python3 -B -m learning_lab \
  --data-dir "$review_root/owner-foundation-review/data" \
  --config-dir "$review_root/owner-foundation-review/config" \
  --vm-home "$review_root/debian-policy-vmhome"
```

Select **Real Linux VM preview… → Locale, Encoding, Time & Offline Jobs**.
Choose Learn and **Choose the locale scope deliberately**, then Start. Inspect
locale precedence and unchanged parent/default; Stop cleanly and reopen with the
same command to Resume the saved disk. Completion is a deliberate self-review.

For the RPM unit, close the app after verified Stop, then use:

```bash
QT_QPA_PLATFORMTHEME='' python3 -B -m learning_lab \
  --data-dir "$review_root/owner-rpm-review/data" \
  --config-dir "$review_root/owner-rpm-review/config" \
  --vm-home "$review_root/alma-policy-vmhome"
```

Select **RPM & Offline Package Administration → Identify RPM package state and
file providers**. The later dependency lesson demonstrates a refused transaction
and an explicitly admitted pair; preserve the preview and actual evidence.
Other collections remain visible but need their own exact images; these review
VM homes do not make every historical image available.
