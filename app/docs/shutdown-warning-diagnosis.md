# Shutdown warning diagnosis — 11 October 2026

Analysis at clean `67337af47561d6bccbb49cbba708bd1e1a4bb59e`; Python 3.14.7,
PySide6/Qt 6.11.2. No runtime code, assertions, warning filters, dependencies or owner profiles
were changed. This report concerns the garbage-collector warning, not every Qt
message or every possible crash.

## Exact warning and cause

Historical catalog/test output:

```text
gc:0: ResourceWarning: gc: 4 uncollectable objects at shutdown; use gc.set_debug(gc.DEBUG_UNCOLLECTABLE) to list them
```

Importing the VM presentation bridge as well changes the count to **5**. A single
independent Qt Property gives the same message with count **1**. The count is an
object count, not four/five failed saves, open disks or running guests.

The warning originates in CPython's final garbage collection. PySide properties
participate in reference cycles through their getter functions and their globals
or closures. The matching official PySide6 v6.11.2 implementation declares a
legacy non-null `Py_tp_del` slot for `Property`, as well as GC traversal/clear
slots. CPython documents that such C-extension objects can remain uncollectable.
Read-only stable-ABI inspection also confirms a non-null legacy finalizer slot
in the installed Property type. A deliberately isolated getter/closure cycle
leaves exactly one Qt Property in
`gc.garbage`. A Property without a getter produces no warning. These source and
runtime results explain the observed retention; they do not identify an upstream
fixed release or justify modifying the installed binding.
[CPython GC documentation](https://docs.python.org/3.14/library/gc.html#gc.garbage),
[matching Qt Property source](https://code.qt.io/cgit/pyside/pyside-setup.git/tree/sources/pyside6/libpyside/pysideproperty.cpp?h=v6.11.2).

Minimal ordinary shutdown reproduction, **no application/profile/VM**:

```bash
python3 -X dev -B -c 'from PySide6.QtCore import Property; p=Property(str, lambda self: "value")'
```

The warning is normally silent under Python's default warning policy. Developer
mode or an always/default warnings policy makes it visible; absence from a menu
launch's visible window is not proof it was fixed. No warning policy was changed
in the application.

The four catalog descriptors are `AuthoringBridge.view`, `Bridge.view`,
`CatalogBridge.authoring` and `CatalogBridge.view`; the fifth is `VmBridge.view`.
The [original investigation](lpic-unit-1.md#shutdown-warning-investigation)
reproduced the warning on untouched baseline `0c20fb7`, with 249 passing tests.
The prior completion recovery snapshot reproduced the same four/five descriptor
counts before and after that batch. This assessment needs no real guest.

## Practical impact and observations

| Controlled case | Actual result |
|---|---|
| Python, QtCore import, QCoreApplication, QObject subclass without Property | Exit0, no warning |
| Unattached Property with getter / QObject property subclass | Exit0, one retained Property warning |
| Catalog-only import / VM-bridge-only import / both | Exit0;4 /1 /5 warning objects respectively; no profile or controller constructed |
| Explicit temporary getter/closure cycle followed by `gc.collect()` | One Property retained in `gc.garbage`; warning on exit0 |
| Property without a getter / explicit noncyclic deletion probe | Exit0, no warning |
| Source and isolated installed-wheel offscreen QML close, then separate-process reopen | Both exit0; same attempt ID, setting draft, pending command and hint usage; no warning in these runs |
| Injected progress-save failure on close | Close refused; window still visible; retry required; prior saved record byte-identical |
| Retry, normal close, separate-process reopen | Exit0; saved state correct and same attempt; no warning in these runs |
| Existing focused workspace/storage/writer/retry/backup-failure tests | 20passed; both test processes exit0 with the four-object warning |

Normal QML closure stops every pending lab-save timer. No profile content file
remained open after close. Two **writer-lock** descriptors remained open while
the Python process was still alive: that is the intended single-writer lifetime,
not a leaked save handle. Each exact child PID/start-time was recorded and waited
for; after exit its process and writer-lock files were absent. Reopening acquired
the profile normally. These are process identities in the diagnostic execution
namespace, not a survey of all host processes. No broad process-name matching,
other-app control or guest launch occurred.

The initial diagnostic incorrectly asserted that all profile descriptors should
close before interpreter exit. It failed on the two intentional writer locks.
That failed script/results remain retained. The corrected diagnostic requires
that **only writer locks** remain, verifies their release after exit, and retains
all save/reopen assertions. No product test was weakened or edited.

**Conclusion:** a real binding-descriptor GC retention issue, with no observed
progress corruption, failed exit, unreleased writer lock or broken resume in the
checked cases. It is not merely dismissed because tests pass. Conversely, these
probes do not prove leak-free long-running operation, abrupt-kill recovery, all
Qt platforms or guest shutdown correctness. A forced termination can lose unsaved
in-memory work independently of this warning. The process OS reclaims its memory
on exit; accumulating dynamically created property cycles within one long-lived
process has not been characterized.

## Smallest proposed resolution — separate maintenance approval

1. Submit or match the minimal cycle reproducer to the PySide maintainers, with
   exact distribution/binding versions and the legacy finalizer slot evidence.
   Prefer a reviewed upstream binding correction; do not delete app class
   descriptors, clear `gc.garbage`, freeze/disable GC or filter the warning.
2. If a supported fixed binding becomes available, verify it in an isolated
   environment first. Changing the working runtime or installing packages needs
   separate approval. No fixed-version claim is made here.
3. Required regressions: import-only and explicit-cycle retention checks; actual
   normal-close flush; refused failed-save close; retry; both-mode exact-state
   separate-process reopen; writer-lock release/duplicate writer exclusion;
   repeated bridge lifetime/GC measurements. Preserve stderr and exit status.
   Native close on the supported desktop is an additional acceptance step.

App teardown changes are not established as the correction to this binding issue.
No fix is implemented or authorized by this report.

## Other diagnostic messages stay separate

[Scheduling acceptance](vm-preview/scheduling-acceptance.md) retains baseline
Dialog `implicitHeight` binding loops and QML null-binding messages during teardown.
They are a distinct UI issue, not the GC warning. The old report has file/line
contexts and failed native runs; its first failed run did not capture the exact
message and remains unknown. This task did not start a guest to reproduce those
lifecycle dialogs and makes no claim that they are resolved. A focused teardown/UI
maintenance proposal should recover their exact messages before changing code.

## Retained evidence and limits

Recovery root:
`/home/drak/.local/state/omarchy-learning-lab/recovery/coverage-diagnosis-20261011T160519193941Z`.
All 496 tracked baseline files were copied and SHA-256 verified. `warning/` contains
minimal source/logs/results, matching upstream source, original failed diagnostic,
final four source close/reopen results, two isolated installed-wheel results and
the20 focused test results. The reused isolated wheel environment has219 packaged
application files byte-identical to this accepted source; it was not rebuilt or
updated. The real menu-installed release was not launched. Profiles remain
there, outside Git. The current installed app was only inspected read-only;
normal-close tests used new disposable profiles and an empty optional VM root.
Offscreen closure is not native physical-keyboard or accessibility acceptance.
