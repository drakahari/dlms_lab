# Native framework and portable scenario domains

## Boundaries

```text
Main.qml — Library / Current Lab / History and attempt dialogs
  MissionPanel + trusted domain workspace + DiagnosticsDock
  CatalogBridge — selection, transfer, layout and one root writer lock
    Bridge — Qt presentation / debounce / workspace sidecars
      Session — attempt lifecycle, drafts, Apply, hints, submissions
        NetworkingDomain — capabilities, diagnostics, workspace presentation
          domain/Engine — IPv4, routing, DNS, endpoint and TCP/firewall rules
        LinuxServiceDomain / LinuxSession — virtual editor and stateful commands
          linux_service/ServiceEngine + VirtualFS — dictionary-only simulation
    Store — unchanged legacy records and paths
    PinnedStore — portable record envelope with exact content/runtime pin
    PackRepository — validated, immutable local scenario copies
```

`scenario_identity.py` defines generic identity and canonicalization. `portable.py`
validates the envelope and maps networking data through the existing engine
validator. `networking.py` is an application-shipped adapter, registered in a
static trusted registry in `domains.py`. Packs cannot name Python modules or QML URLs.
`workspace_state.py` persists pending command text and structured diagnostic
results separately from attempt records. Theme input remains read-only.

### Scope of the proof

The original networking proof has one editable workstation,
optional router TCP policy, connected IPv4 routes and one default gateway; no
static route editor, real shell, real sockets, or operating-system commands.
Settings and firewall editing remain in the networking session/bridge. The
[Linux service extension](linux-service.md) supplies its own trusted engine,
session actions and workspace. The shell now obtains sessions and presentation
fields from each domain and selects one of two statically declared QML components.
Shared attempt/history/mode/transfer behavior works for both domains. The Linux
session reuses lifecycle methods from `Session`; a full domain-neutral session
API and arbitrary future domains remain future work, not established by this proof.

The three legacy packs and legacy serialization remain intact. The explicit
bundled catalog and gateway's original storage root are compatibility exceptions.
Console source names, topology, diagnostics, DNS names, endpoints, constraints,
editable fields and firewall router labels now come from validated content.
Exactly three hints is a legacy-format rule; portable networking accepts 0–32.

The [Linux usability extension](linux-usability.md) registers a second explicit
Linux contract/behavior pair for healthy stopped-service lessons. Original Linux
packs retain contract 1 / `linux-service-1`; beginner packs opt into contract 2 /
`linux-service-2`. Runtime resolution is a static application allowlist, not pack
code. Existing attempt pins are neither upgraded nor rewritten.

## Workspace

- Library headings and each card's status belong to their own scope. Current Lab
  shows the active scenario, version, mode, attempt and applied revision. History
  identifies the selected lab/version or explicitly displays a recent page per lab.
- The mission pane stays beside the workspace and submission review. Full brief,
  objectives, constraints and hints are scrollable; there is no blocking brief dialog.
- Connected segment buses lead to inspectable devices. Settings show Draft and
  Applied values together. Firewall rules have an explicit Applied-policy viewer.
- The console and structured diagnostics share a resizable dock. Diagnostics name
  the tested revision and become stale after Apply. Unsent command text survives
  tool/lab changes, reset archives and restart.
- Submit records a rubric result; Run diagnostics does not submit. Review is a
  separate workspace page. Submitting with drafts requires explicit confirmation.
- At widths below 1000 logical pixels the mission pane moves above the work area.
  When the work area is short, topology becomes a tool tab. Panes can be resized
  with split handles or +/− controls; ↺ restores default sizes. All instructions
  remain accessible by scrolling. Supported minimum is 800×600 logical pixels.
- Tab/Shift+Tab, Enter, Alt+1/2/3, F6/Shift+F6 and scroll-panel PageUp/PageDown are
  supported. Reset/mode/switch dialogs preserve pending edits and restore focus.

## Portable scenario format

See [complete gateway example](../examples/gateway-dns.lab.json). The structure is:

```json
{
  "format": "learning-lab.scenario",
  "schema_version": 1,
  "identity": {"id": "gateway-dns", "content_version": "1.0.0"},
  "engine": {
    "id": "networking", "contract_version": 1,
    "supported_behavior_versions": ["networking-1"],
    "required_capabilities": ["ipv4-routing", "dns", "portal-reachability"]
  },
  "metadata": {"title": "Restore gateway & DNS", "topic": "Networking", "difficulty": "Foundation", "minutes": 10},
  "mission": {"brief": "Complete instructions", "constraints": ["Preserve the assigned address and /24"]},
  "objectives": [{"id": "ip", "label": "Preserve address", "points": 20, "predicate": "address_equals", "params": {"device": "WS-01", "value": "192.168.50.20"}}],
  "hints": ["A progressive hint"],
  "assets": [],
  "domain": {
    "schema_version": 1, "source_device": "WS-01",
    "topology": {"segments": [], "devices": []},
    "initial_state": {}, "editable_fields": {},
    "diagnostics": [{"id": "remote", "label": "Application server", "operation": "reach", "target": "10.20.0.10"}]
  }
}
```

This abbreviated outline is not an importable scenario: topology, initial state,
editable fields and the 100-point rubric must be complete. Actual examples are
fully validated. Networking devices/interfaces and predicates retain the
[engine data contract](pack-format.md). Optional `domain.firewall` and
`domain.tcp_services` use that existing tested contract. Diagnostic operations
are `reach`, `resolve`, `portal`, and capability-gated `connect`; target values
must reference known topology addresses or names. A connect diagnostic declares
an expected `connected` or `denied` result. Diagnostic results never replace
rubric predicates.

### Identity and compatibility

Format/schema version, author content version, engine contract version and engine
behavior version are separate. Networking domain data also has its own schema
version. `networking-1` is the shipped behavior declaration, not the Qt version
or an automatically computed code hash. Changes to simulation/grade semantics
require a new behavior version and explicit compatibility review.

The **entire portable envelope** is hashed by `oll-json-v1`, including format,
identity, engine requirements, all metadata, mission/constraints, topology,
initial/editable state, diagnostics, objectives, hints and the empty assets list.
There are no excluded content fields. The digest itself is not embedded in the
pack, avoiding a self-reference. Exact [canonical rules](scenario-identity.md)
are unchanged: object-key/formatting differences are ignored; arrays and string
contents are preserved. A digest identifies content; it does not authenticate it.

Portable networking attempts retain schema 3 envelopes. New Linux attempts use
schema 4 with domain-delegated state validation. Both contain the exact scenario identity
(digest and canonicalization included), engine ID/contract/behavior, and attempt.
The installed content is kept under its digest and that attempt store is keyed
by the same digest. New content versions coexist; they cannot replace a resumed
attempt's content. Unavailable/mismatched behavior or a newer record schema is
preserved read-only, with no fallback to a differently pinned backup. This
release does not retain arbitrary old engine implementations. Keep matching
source snapshots to reopen evidence after a future behavior change.

Legacy records contain only ID/content version. No original digest or engine
provenance is invented. They continue through their compatibility path and
existing validation. A converted portable pack starts independent pinned
attempts; it does not absorb the legacy history.

### Import, limits and safe failure

Import accepts one local, regular, UTF-8 `.lab.json` file. There is no downloader,
archive extraction, external asset resolution, script, expression evaluator,
plugin loader or automatic update mechanism. ZIP/gzip, BOM, invalid UTF-8,
duplicate JSON keys, floats, unsupported schemas/capabilities/engines, unknown
fields and inconsistent topology/objectives are rejected before installation.
Paths, URLs and executable fields cannot occur as resources: `assets` must be
empty, and no pack field controls a host filesystem path. Linux virtual paths
are dictionary keys only; see its separate domain contract. All content is plain text.
Unknown imported files remain untouched.

Shared limits: 256 KiB raw and canonical content, depth 32, signed 64-bit integers,
32 hints, 32 constraints, and 256 installed JSON files. Networking limits:
32 devices, 64 segments, 8 interfaces/device, 64 DNS records/device,
32 endpoints/device, 32 objectives, 32 hints, 32 diagnostics, 32 constraints,
16 firewall rules, 32 TCP service declarations/ports, and 256 installed JSON
files. Metadata title/topic/difficulty limits are 120/80/40 characters;
objective/diagnostic labels 512; general text 16,384. Feasibility validation
allows at most 128 gateway/DNS candidate combinations; complex scenarios beyond
this budget fail explicitly. Console input is 512 characters and parser actions
are allowlisted. Existing progress and console limits remain in force.

Repository filenames are generated solely from validated digests. Installation
uses same-directory temporary files, fsync and atomic replacement under the app's
single writer. Exact duplicate ID/version/content is idempotent, including
formatting differences. The same ID/version with different content is rejected;
a new content version installs alongside the old. Corrupt/unavailable repository
entries and symlinks remain on disk with a visible warning. No content is pruned.
A capacity or write failure preserves existing packs/attempts. Imported file
bytes are retained for scenario export.

### Scenario versus personal export

**Export scenario** contains only pack data. Exporting an original bundled lab
converts its content in memory to the portable envelope. **Export this attempt**
in History writes a separate `learning-lab.attempt-history` JSON document with
record JSON, workspace sidecar and explicit provenance limitations. It may
contain personal command/draft/history information. Attempt export is not an
importable scenario; personal-history import/merge is deferred. Current recovery
placeholders cannot be exported as if they were valid historical records.

## Storage and rollback

Legacy paths and schemas are unchanged. New app-owned locations:

```text
<data>/portable/packs/<content-sha256>.json
<data>/portable/attempts/<content-sha256>/{current.json,current.backup.json,attempts/}
<each attempt store>/workspace/<attempt-UUID>.json
<config>/workspace-layout.json
```

Workspace sidecars are versioned, capped at 256 KiB and atomically replaced.
Unknown/corrupt sidecars preserve the file and put that attempt in recovery mode;
there is no silent reset. Main record and sidecar are separate atomic files,
not a multi-file transaction: a crash may leave an older pending command or
stale diagnostic evidence. Applied revision labels distinguish stale diagnostics.
Reset saves the old sidecar before archiving and creating a fresh attempt.
Archives and sidecars are never automatically deleted.

No real progress migration is performed. All mutating tests use temporary
profiles. Before future migration, close the app and take a verified external
source/config/data snapshot. Obtain approval for real data migration/deletion.
Rollback should first copy the **newest** complete profile to another private
location; do not overwrite it with an earlier backup. Run the matching recovery
source with isolated copies of its matching data/config. An older app cannot
read portable attempts; preserve those files for the matching newer app.
See [recovery instructions](recovery.md). Git metadata is never repaired or
reinitialized as part of recovery.

## Review checkpoints

1. Existing checkpoint: deterministic identity, compatibility adapter and recovery.
2. Trusted networking adapter: original tests and command/diagnostic parity.
3. Portable repository and pinned attempt tests: invalid imports, conflicts,
   capabilities, unknown versions, recovery, unchanged legacy bytes, modes.
4. Native workspace: geometry and keyboard flows at supported sizes/scales,
   drafts, hints, grade/reset/history, save failure and reopen.
5. Frozen-code proof: convert gateway data, author a different DNS-misdirection
   scenario using only data, and exercise import/modes/grade/reopen/export/reimport.
6. Preserve original bundles; offer portable examples for the other two labs,
   verify conversion parity and separate personal export. Real history migration,
   broad cross-domain support, marketplace/accounts, arbitrary plugins and a
   visual authoring tool remain outside this implementation.

Owner review remains necessary for physical keyboard/compositor input,
native file-picker interaction, accessibility/assistive technology and subjective
layout comfort. Automated QtTest input is identified separately in the evidence.
