# Permissions contract review and second authoring proof

## Scope decision

The original directory exercise could not be represented accurately by committed
contract 2. It restricted mutable targets to regular files, fixed guided repair
to 0600, recorded reads but not successful entry, and required read plus execute
for every directory listing. Changing JSON alone would either fail validation or
teach the wrong read-versus-search distinction.

The preceding implementation added opt-in contract 3 to the same trusted engine.
The assistant explained those gaps before editing, but interpreted “explain the
gap and proposed scope before implementing” as allowing continuation after the
explanation. That did not honor the owner's intended scope gate: it should have
stopped for a response. The extension was left uncommitted and reviewable;
the owner has since authorized the local commit described below.

**This follow-up changes no application or validator code.** It adds one example,
four regression tests, and this review; it links the proof from the guide.

## Backward compatibility review

- Dispatch is explicit: contract 1 remains navigation, contract 2 remains file
  permissions with `linux-permissions-1`, and contract 3 selects
  `linux-permissions-2` in the existing permissions domain. Validation requires
  the matching domain schema and an installed behavior version.
- Old packs were not edited or upgraded. Contract-2 state retains its original
  evidence fields, command grammar, file-only mutation boundary and guide. The
  new directory/listing/lesson paths are conditional on the opt-in schema.
- The shared virtual filesystem, networking/service engines, QML, storage and
  attempt envelopes were not changed. Pins still bind exact scenario digest and
  engine runtime; incompatible saved pins are preserved read-only, not migrated.
- An isolated comparison against committed
  `6276c552eb87a1d9790f42d1b627f2f19f2db272` matched **18 contract-2 commands**:
  pin, state after each command, output, grade and Learn guide. It includes valid
  and invalid chmod, broad modes, read denial, repair and unsupported syntax.
  This is sampled differential coverage, not an exhaustive equivalence proof.
- The full **172-test suite** passes, including prior networking, service,
  navigation and permissions regressions and pinned-record preservation tests.

## Imported-pack validation review

The shared boundary accepts bounded UTF-8 JSON only (256 KiB), rejects duplicate
keys, unsupported formats/contracts/behaviors, unknown fields, archives and
nonempty assets. The canonicalizer also limits depth and representable values.
Contract 3 requires its exact shipped capability set; packs cannot install code.

Virtual paths are canonical names in a dictionary, not host paths. Nodes have
allowlisted kinds/identities and ordinary octal permission bits; parents must
exist. Contract 3 limits the tree to 64 nodes, each text file to 8 KiB, and total
text to 64 KiB. Mutable targets must be reachable learner-owned objects, never
the virtual root. Each requires an exact final-mode objective. Verification
targets must have the correct kind; the declared final tree must permit the
required reads and entry. Predicates and Learn actions are allowlisted with exact
parameter fields. Hints and steps are bounded data, not expressions or commands
executed by a host interpreter.

Validation is structural and checks final-goal feasibility. It does **not** prove
that every possible author-written explanation or guide order teaches well; the
author still needs to complete both modes. Simulation limits remain: no full
chmod/shell semantics, no partial `ls -l` metadata, and conservative search checks
for intermediate `.` and trailing `/`. The guide discloses these differences.

Repository identity/version conflicts reject without replacement; identical
reimport is idempotent. New tests try malformed JSON, duplicate keys, oversized
data, archive bytes, boolean versions, unavailable behavior, extra capabilities,
schema mismatch, executable actions/fields, wrong ownership, impossible goals,
asset paths and conflicting content. Every rejection preserves the input bytes
and existing repository files. Existing host-API poison tests and plain-text
rendering checks remain in place. History export is separate; no history import
is claimed. Selecting an import file intentionally reads that user-selected local
JSON file; virtual paths and learner commands do not provide host access.

## Reproducible content-only proof

[`examples/linux-archive-access.lab.json`](../examples/linux-archive-access.lab.json)
is **Read the fieldwork handover**. It is derived directly from
[`templates/linux-permissions.lab.json`](../templates/linux-permissions.lab.json),
not by changing or registering another engine.

`derive_from_template()` in
[`tests/test_directory_authoring_proof.py`](../tests/test_directory_authoring_proof.py)
records the exact JSON edits and asserts equality with the delivered pack. It
retains the template's format, schemas, engine requirements and capabilities;
replaces identity, mission, objectives, hints and lesson text; replaces the notes
target with `/srv/fieldwork/Archive` and `handover.txt`; and changes the starting
directory to `/srv/fieldwork`.

Archive starts at 0400, its note at 0600, ancestors at 0755. The goal is 0500
(70 points), successful entry (15), and successful read (15). Learn uses five
steps: inspect, list names, repair, read through a path, then enter. There is no
failed-command step. Challenge accepts `u+x` or `500`, equivalent paths and either
verification order. `600` still fails traversal; `777` loses least-privilege
points. This proves another scenario on the new directory contract, not a new
mechanic or cross-domain generalization.

Tests exercise the real catalog import/export APIs in temporary profiles:
validate → import → complete Learn → reset → reopen the same profile → complete
Challenge → export exact pack bytes → import into a fresh profile → complete
again. Reset restores the fault and retains completed history; scenario import
does not bring personal attempts into the second profile. A separate attempt
export is rejected as scenario input.

```bash
cd /home/drak/Documents/dlms_lab/app
python3 -B tools/validate_scenario.py examples/linux-archive-access.lab.json
review_profile=$(mktemp -d /tmp/archive-author-review.XXXXXX)
python3 -B -m learning_lab --data-dir "$review_profile/data" --config-dir "$review_profile/config"
```

Choose Library → Import scenario and select the new example. Keep the same
profile arguments when reopening. Nothing was imported into real personal data
during this work.

## Verification and exact change categories

This follow-up: **one pack**, **one test file containing four tests**, **this new
document and a guide link**. Application/tool files match their pre-follow-up
SHA-256 hashes. All 14 existing recovery snapshots verified before editing.

Final comparison found that the real profile differs from the older pre-extension
snapshot: four progress files were added, ten existing progress files have only
metadata changes, and one configuration file has changed bytes. All these
modification times precede this follow-up's code-hash capture; no existing
progress-file bytes were removed or changed relative to that snapshot. These
files were left untouched. This is not a claim that the current real profile
still equals the older snapshot. Tests used disposable profiles throughout.

Accumulated changes across the preceding implementation and this follow-up,
relative to `6276c552` (paths below are relative to `app/`):

| Category | Files |
| --- | --- |
| Pack content (3) | `templates/linux-permissions.lab.json`; `examples/linux-directory-permissions.lab.json`; `examples/linux-archive-access.lab.json` |
| Application code (5) | `learning_lab/domains.py`; `learning_lab/portable.py`; `learning_lab/linux_navigation/permissions.py`; `learning_lab/linux_navigation/permissions_adapter.py`; `learning_lab/linux_navigation/permissions_lesson.py` |
| Authoring tool (1; executable developer code) | `tools/validate_scenario.py` |
| Tests (4) | `tests/test_linux_permissions.py`; `tests/test_permissions_authoring.py`; `tests/directory_permissions_acceptance.py`; `tests/test_directory_authoring_proof.py` |
| Documentation (5) | `README.md`; `docs/framework-acceptance.md`; `docs/directory-permissions.md`; `docs/permissions-authoring.md`; `docs/permissions-contract-review.md` |

Ignored local evidence contains test logs, reports and offscreen screenshots; it
is not pack content or application code. No progress, temporary profile, recovery
copy or Git metadata was added to the source changes. At that review, nothing
was staged.

Local evidence:

- [172 regressions](../evidence/permissions-second-scenario-regressions.txt)
- [Contract-2 differential sample](../evidence/permissions-contract-two-parity.json)
- [Second-pack offscreen UI results](../evidence/archive-authoring-ui.json)
- [Application/tool preservation](../evidence/permissions-followup-preservation.json)

Second-pack rendering and controller workflows passed at 800×600 and 1280×900,
at 100/150/200%. The earlier seven-suite UI matrix is unchanged evidence for the
first directory pack. No new native acceptance is claimed: physical keyboard,
file choosers, accessibility and native scaling still need owner testing. The
previous native Wayland probe returned `Operation not permitted`.

## Local commit review

The owner reports that the new directory lab looks good and authorizes the local
commit **Add directory-permissions labs and reusable authoring workflow**.
This records owner-reported visual approval only. Physical keyboard, native file
choosers, accessibility, native scaling and mixed-monitor checks remain outstanding.

The reviewed scope is the 18 files in the category table above, against baseline
`6276c552eb87a1d9790f42d1b627f2f19f2db272`. Review includes the opt-in engine
branches, declarative validation, exact template derivation, isolated lifecycle
tests and documentation. The complete regression suite was rerun: **172 passed**.
All seven offscreen UI suites passed at 100/150/200% (21 runs). The second
directory pack also passed fresh rendering and Learn/Challenge controller checks
at 800×600 and 1280×900 at all three scales. These are automated checks, not
physical-keyboard or native file-dialog tests.
Generated logs, screenshots, recovery copies and personal profiles are excluded
from the commit candidates and preserved locally. No credential values were
printed during the file scan. Local commit execution and any Git-write blocker
are reported separately; this document does not assert that a commit succeeded.

Current ignored evidence: `evidence/directory-commit-regressions.txt` and
`evidence/directory-commit-ui-results.json`. Offscreen tests do not establish
native acceptance.
