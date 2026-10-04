# LPIC-1 Foundations: Processes, Jobs & Priorities

Eight bundled real-Linux lessons, approximately 60–90 minutes. Open Library →
**Real Linux VM preview…**, then choose a lesson. Sequence is guidance; no unlocks.
Start/Resume uses the reviewed optional offline Debian image and native GTK console.
Core simulations remain usable without QEMU or the image. Type commands in the
**guest**, never a host terminal. Clipboard integration remains disabled.

Prerequisites: command entry, paths, reading output. Each lesson has bounded owned
practice processes, Learn steps, explanations, expected observations, hints,
Challenge goals, troubleshooting and cleanup. Lesson 3 is the accepted background
job lesson with exact original bytes/identity/content version/pin; its existing
profile binding and session location are unchanged. Support notes are separate.

| # | Lesson | Outcomes for self-review | Objective subset |
|---|---|---|---|
| 1 | Identify your processes | Actual PID/PPID/owner/state; user filtering and sorting; cleanup. | 103.5 inspection/selection |
| 2 | Move between foreground and background | Ctrl-Z, bg, fg, Ctrl-C and the same shell's jobs. | 103.5 foreground/background/signals |
| 3 | Manage a background job | Reuse accepted inspection, STOP, continue, TERM and wait practice. Reinforcement. | 103.5 |
| 4 | Signal the intended process | Preview narrow user/parent/argument selection; companion unaffected; TERM versus KILL. | 103.5 selection/signals |
| 5 | Read a live process view | top/watch, snapshots, CPU averages, load and available memory; normal exits. | 103.5 monitoring |
| 6 | Keep work running after logout | Controlled huponexit comparison, nohup/disown, saved identities, new empty job table. | 103.5 logout persistence |
| 7 | Adjust process priorities safely | Actual default/positive NI; renice; denied increases; nice can still execute. | 103.6 partial |
| 8 | Process handover practice | Combined signals, priority, logout verification, guest-local report and cleanup. Reinforcement. | 103.5/103.6 |

LPIC-1 objectives **5.0**, exams 101-500/102-500:
[official objectives](https://www.lpi.org/our-certifications/exam-101-102-objectives/).
Partial coverage only: no screen/tmux, killall/pstree or privileged priority success.
The image has no sudo or remote login. No packages, guest privilege or image changes.
No claim of full objective mastery, LPIC preparation, affiliation or scored assessment.

## Learn, Challenge and completion

Learn shows one step at a time. Expected values say where timing/identifiers can
vary. Challenge hides step commands and hints; outcomes accept equivalent real-Linux
approaches. Command text is **display-only content**, never an executable app action.
Advancing guidance is a learner action, not evidence of execution. Completion is
explicitly **self-reviewed, no verification score**. Guest files/reports are personal
observations, not app-verified outcomes. No guest agent or imported VM lessons.

Before any signal, inspect actual owner, arguments and PID; numbers may be reused.
Never assume %1. %+ means this shell's current job; choose the actual identifier
when other jobs exist. Preview pgrep matches before pkill; avoid broad patterns.
Use bounded sleeps; if one expires, repeat honestly with a new PID. Clean up tasks
normally before Stop. TERM requests exit; KILL/STOP cannot be caught, and KILL does
not let programs clean up. Bash wait can reap only this shell's children.

### Logout experiment

This pinned image's default Bash login shell has huponexit **off**: an ordinary
background sleep can also survive logout. The exercise deliberately enables
`shopt -s huponexit` in the practice shell only, never a startup/system file.
Under that controlled condition Bash sends HUP to ordinary jobs on exit;
nohup-protected and disown -h jobs survive in the tested image. disown -h excludes
a job from Bash's HUP behavior; it does not install signal immunity or create a
multiplexer. nohup alone does not background a command; `&` and stream redirections
are separate. Sleep's explicitly redirected log may be empty.

`exit` logs out; tty1's console-only learner autologin opens a new shell. Its job
table is empty and huponexit returns to the image default. Reinspect saved PIDs,
owner and command with ps before cleanup. Do not blindly kill stale PID-file values.
Other session-manager policies can kill processes despite nohup/disown. These are
not universal persistence guarantees. Logout survival is not reboot survival.

### Priorities

Default NI is 0 here. Positive nice adjustments lower scheduling preference under
contention. This util-linux renice -n sets an absolute value. learner can increase
NI, but cannot reduce it again or request negative niceness (RLIMIT_NICE=0, no
capabilities). GNU nice warns when an adjustment is denied but still executes its
command at the existing NI. Check ps after both successful and denied changes.
Sleeping tasks provide no speed benchmark; NI is not a guaranteed CPU allocation.
PR and NI columns are different presentations. No sudo workaround is offered.

## Selection, persistence and recovery

The trusted bundled registry is `learning_lab/vm_preview/unit.json`; seven new
lesson files and original `lesson.json` are wheel resources. Registry limits:
64 KiB per resource, 1–16 trusted entries, unique bounded IDs, 1–32 steps, text up
to 4096 characters, 0–16 hints. Exact allowed fields only; no actions/scripts/import.
Registry content is validated and cached for the application's lifetime, with
copies returned to prevent accidental mutation. Installing new content requires
restart. Imported simulation JSON cannot select this backend.

New lessons derive a stable binding from application profile binding + lesson ID,
with a fixed domain separator. The original lesson keeps its exact old binding.
Manager gains only an optional trusted lesson-ID constructor argument; security,
launch/QMP, image pins and lifecycle operations are unchanged. Each session still
pins exact image/backend/canonical lesson digest; no upgrade/migration is automatic.
Selection is separate schema-1 metadata under `selections/<app-profile>.json` in
the VM root. Unsupported newer or unsafe selection records are preserved/refused.

Switching selection does not switch a disk or discard progress. A running-lesson
banner, **Return to running lesson**, and **Stop running** stay accessible. Stop
and Force stop target the verified running lesson in this application profile;
Reset targets the selected lesson and is blocked while any VM runs. Other profiles
cannot acquire controls. Existing global operation/lifetime locks still exclude a
second guest across lessons, profiles and stores.

Missing current-session evidence disables implicit Start/Resume; a confirmed Reset
can start fresh while retaining orphaned disks. Corrupt/newer/pin-mismatched records
are preserved/refused, not overwritten. A verified running guest remains stoppable
when its progress record is lost; completion/progress are never reconstructed.
Disk/journal loss, unclean disks and unverifiable control remain explicit blockers.

**Resume disk boots files, not RAM, processes or shell jobs.** Clean Stop/Resume
can retain notes, but stale PID files cannot identify newly running processes.
Reset retains old generations and creates a fresh disk only for the selected lesson.
No automatic repair, deletion, retention pruning, image updates or aggregate quota.
Eight separate overlays plus retained generations can consume substantial space;
existing admission/per-file limits and best-effort monitoring remain unchanged.

All VM sessions, selection, self-review records and disks remain **excluded** from
profile backup, scenario export and history export. Restoring a simulation profile
elsewhere does not restore a VM. No backup-format change or disk export.

## Disposable source launch

From the repository root (does not update the installed application):

```bash
PYTHONPATH=/home/drak/Documents/dlms_lab/app python3 -B -m learning_lab --data-dir /tmp/oll-process-owner/data \
  --config-dir /tmp/oll-process-owner/config \
  --vm-home /home/drak/.local/share/learning-lab-vm/preview-v1
```

Use a new disposable data/config destination;
this gives distinct VM bindings. Retain the supplied VM root to access the reviewed
base image. No installation occurs. Cleanup guest processes, use **Stop running**,
and leave retained overlays intact for review.
