# Author a Linux permissions lab

Start with [`templates/linux-permissions.lab.json`](../templates/linux-permissions.lab.json),
a valid, importable private-file exercise. The directory example is
[`examples/linux-directory-permissions.lab.json`](../examples/linux-directory-permissions.lab.json).
Both use the same trusted permissions engine and terminal UI. Edit JSON content;
packs cannot install mechanics or run code.

For a second directory example derived from this template, see
[Read the fieldwork handover](../examples/linux-archive-access.lab.json) and its
[reproducible derivation, compatibility review and workflow results](permissions-contract-review.md).

## Required fields

All listed fields are required; unknown fields are rejected.

| Field | Authoring rule |
| --- | --- |
| `format`, `schema_version` | `learning-lab.scenario`, `1` |
| `identity` | Unique stable `id`: lowercase letters, digits and hyphens, starting with a letter (≤64 chars); semantic `content_version`, e.g. `1.0.0` |
| `engine` | `id: linux-navigation`, `contract_version: 3`, `supported_behavior_versions: [linux-permissions-2]`; retain the template's seven required capabilities |
| `metadata` | `title` ≤120, `topic` ≤80, `difficulty` ≤40 characters; `minutes` 1–240 |
| `mission` | Plain-text `brief` and ≤32 `constraints`; state the Challenge goal, exact required modes and verification without a walkthrough |
| `objectives` | 1–16 unique `id`, `label`, positive integer `points` totaling 100, `predicate`, `params`; see below |
| `hints` | 0–32 short progressive strings, reasoning first; visible only in Learn and recorded without a score penalty |
| `assets` | `[]`; external assets, URLs and archives are unsupported |
| `domain` | `schema_version: 3`, `filesystem`, `cwd`, `permission_targets`, `lesson` |

Capabilities: `virtual-filesystem`, `file-navigation`, `activity-evidence`,
`mutable-permissions`, `directory-permissions`, `traversal-evidence`,
`directory-name-listing`. These select shipped code; they never load plugins.

## Virtual tree and permission goal

`filesystem` maps canonical absolute paths to nodes with exactly `kind` (`file`
or `directory`), `owner`, `group`, four-digit `mode` (`0000`–`0777`), and `content`.
Directories have empty content; every parent and `/` must exist. Paths are ≤256
characters and contain letters, digits, `/`, `.`, `_`, `-`; use normalized keys.
At most 64 nodes; text files ≤8 KiB each, total text ≤64 KiB; whole pack ≤256 KiB.

Virtual identities are `learner`, `root`, `www-data`. Commands always run as
`learner`, with the same-named primary group. Owner bits win if the user owns the
node; otherwise matching group bits apply, otherwise other bits. Classes are
never combined. There is no root impersonation, sudo, ACL or supplementary group.

`cwd` must initially be searchable. `permission_targets` lists 1–16 reachable,
learner-owned files/directories whose modes may change; never `/`. Their ancestors
must initially be searchable. All other mode bits, ownership, content and paths
are immutable. Each target needs a `mode_equals` objective. Make the final modes
sufficient for every declared read/traversal check and explain least privilege.

Example directory goal: start at `0400`, require **0500** to preserve name listing
and add search, without write or group/other access. Its readable child can remain
`0600`. **0700 and 0777 fail this stated goal.** A search-only `0100` permits entry
and access to a known readable child but loses the required name-listing access.

## Rubric and Learn steps

Allowed predicates and their exact parameters:

| Predicate | `params` | Meaning |
| --- | --- | --- |
| `mode_equals` | `{"path":"/absolute/target","mode":"0500"}` | Exact final mode on an enabled target |
| `traversal_verified` | `{"path":"/absolute/directory"}` | Successful `cd` after the last actual mode change |
| `read_verified` | `{"path":"/absolute/file"}` | Successful `cat` after the last actual mode change |

Verification paths may be fixed children, not just editable targets. Give labels
that distinguish final-state checks from action evidence. Diagnostics/Help do not
supply evidence. Actual mode changes clear both kinds of verification; no-op chmod
does not. Command spelling/order is not graded, and initial mistakes are never
required for credit. Final state alone cannot prove a read or entry occurred.

`lesson` has `goal` (≤240 chars) and 1–16 `steps`, each with `action`, absolute
`path`, short `explanation` and `expected` (≤512 chars each). Allowed actions:

- `inspect`: long-list the enabled target's parent to see its mode.
- `list`: list directory names; useful to distinguish read from execute.
- `try-enter` / `try-read`: optional diagnostic denial; automatically skipped if
  access already works. These are guidance, not rubric prerequisites.
- `repair`: derive a supported chmod toward that target's declared mode.
- `enter` / `read`: verification for the corresponding rubric objective.

Include a repair step for every mode goal and an enter/read step for every
verification objective. The engine shows the first unmet step; a fully passing
state shows completion. Challenge hides steps and hints. Keep the goal and rules
usable without them; do not repeat the entire walkthrough in mission text.

## Exact simulated commands and limits

```text
help
pwd
ls [-l] [PATH]
cd [PATH]
cat PATH
chmod u+r PATH
chmod u+x PATH
chmod NNN PATH
```

Numeric input is **three** octal digits; `500` works, `0500` input does not.
Symbolic forms only add the named owner bit, preserving others. No other forms,
recursion, multiple targets, quoting, wildcards, variables, pipes or shell syntax.
No learner input reaches the host filesystem, processes, shell or network.

Directory `r` permits `ls` names; `x` permits `cd` and access to known children.
`ls -l` needs `r+x` for child metadata. Without search it reports an error rather
than Linux-style partial metadata rows; inspect the directory using its parent's
long listing. Resolution checks each traversed component; intermediate `.` and
trailing `/` conservatively require search. Use an unadorned directory path for
read-only name listing. Above-root traversal is rejected instead of clamped.
Links, mounts, ownership changes, writing contents and execution are unsupported.
If search is removed while inside a directory, `pwd` still reports the recorded
cwd; use an accessible absolute path to leave or restore its mode.

## Validate, import and round-trip

From `app/`:

```bash
cp templates/linux-permissions.lab.json /tmp/my-permissions.lab.json
# Edit the copy: choose a new ID/title, then update paths and their references.
python3 -B tools/validate_scenario.py /tmp/my-permissions.lab.json
review_profile=$(mktemp -d /tmp/permissions-author-review.XXXXXX)
python3 -B -m learning_lab --data-dir "$review_profile/data" --config-dir "$review_profile/config"
```

The validator is read-only, uses the installed contract, and exits nonzero on
invalid content. It checks structure and final-goal feasibility, not teaching
quality. In Library, **Import scenario…** and select the copy. Check Learn and
Challenge, wrong fixes and equivalent paths, reset, switching, and reopening with
the **same** profile arguments. Verify final mode alone does not earn verification
credit. **Export scenario…**, revalidate and reimport into a second temporary
profile: identity/content should match, with no personal attempts included.
**Export this attempt…** is separate personal history export; history import does
not exist. Never copy real profile files into an authoring pack.

Run `python3 -B -m unittest discover -s tests -v` and add scenario-specific fixtures
for your new goals. Native keyboard/readability review is still needed after
offscreen UI checks. The directory example and renamed-template fixture demonstrate
this workflow on contract 3; mechanics outside the allowlist require reviewed
engine code and a new compatibility version.

## Versions and updates

Keep outer format schema **1**, domain schema **3**, engine contract **3** and
behavior **linux-permissions-2** distinct from your content version. The engine pin
and digest cover all pack content, including hints, steps and virtual text.
JSON formatting whitespace/key ordering alone does not change the canonical digest;
whitespace inside text content does. Increment
`content_version` for meaningful edits after publication; identical ID/version
with different content is rejected. Identical content reimport is idempotent.
Updates create separate pinned content; they do not rewrite resumed attempts or
historical evidence. Unknown versions fail safely. Existing contract-2 file labs
retain their old behavior; importing this template does not migrate their data.
