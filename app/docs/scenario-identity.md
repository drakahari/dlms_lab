# Scenario identity — checkpoint 1

This document records the checkpoint-1 boundary. Later portable-format support
and attempt pinning are described in [framework.md](framework.md); the exact
`oll-json-v1` rules below remain authoritative.

This checkpoint identifies the existing gateway/DNS pack in memory. It does not
define or accept a new portable pack format, migrate records, or add import/export.
The three bundled JSON files and the existing engine, session, storage, and QML
remain unchanged.

## Four separate versions

| Identifier | Current gateway value | Meaning |
| --- | --- | --- |
| Format ID and version | `omarchy-learning-lab.legacy-network`, `1` | The shape and validation rules of the existing pack; version comes from `schema_version` |
| Content version | `1.0.0` | The author's scenario revision, read from `content_version` |
| Engine contract version | `1` | The trusted adapter's compatibility declaration for the existing networking API |
| Engine behavior version | `legacy-1` | The unchanged engine baseline reviewed at checkpoint 1 |

`oll-json-v1` separately versions the content canonicalization and hashing rules.
It is neither a pack format version nor an engine version.

The adapter accepts only legacy format 1 and ID `gateway-dns`. The existing
subnet and firewall loaders retain their original behavior. A valid different
content version does not imply a different format or engine; for example,
`2.0.0` still needs the same structural and feasibility validation. This is not
an update-selection mechanism.

`NETWORK_ENGINE` is declared by trusted application code, not extracted from
legacy JSON. Unknown engines, contract versions, behavior versions, pack schemas,
or capabilities are rejected before the adapter returns a scenario. Future
behavior changes must receive a new behavior label and compatibility review;
the current label does not implement engine version retention or selection.

## Exact digest rules: oll-json-v1

Input to the gateway adapter is at most 262,144 bytes of UTF-8 JSON, without a
BOM. It rejects malformed text, duplicate keys at any depth, non-finite values,
and unsupported legacy content. The canonicalizer itself operates on decoded
JSON values; it is not an importer or domain validator.

Canonicalization is defined as follows:

1. Permit objects with string keys, arrays, strings, signed 64-bit integers,
   booleans, and null. Reject floating-point values (including `1.0`), non-JSON
   types, and unpaired Unicode surrogates. A JSON integer token `-0` decodes to
   zero. There are no floating-point rounding rules.
2. Root depth is zero; each object key/value or array element increases depth by
   one. Reject values deeper than 32. The canonical byte output is limited to
   262,144 bytes.
3. Sort object keys recursively in Unicode code-point order. Preserve every
   array's order, including capabilities, devices, interfaces, objectives, and
   hints. Do not sort arrays as sets.
4. Preserve string contents exactly: no Unicode normalization, case folding,
   whitespace trimming, or newline conversion. Equivalent JSON escape spellings
   decode to the same string. Precomposed and decomposed Unicode remain distinct.
5. Serialize as compact JSON without indentation, separating fields with `,`
   and keys/values with `:`. Use lowercase JSON literals, decimal integers, and
   standard JSON string escaping. Leave valid non-ASCII characters and `/`
   unescaped. Encode as UTF-8 without BOM or trailing newline. The reference
   operation is Python `json.dumps(value, sort_keys=True, ensure_ascii=False,
   separators=(',', ':'), allow_nan=False).encode('utf-8')`, after the checks above.
6. Hash `b'oll-json-v1\x00' + canonical_bytes` with SHA-256. Represent the result
   as `sha256:` followed by 64 lowercase hexadecimal digits.

These are application-specific rules, not a claim of RFC 8785 compliance.
Changing any rule requires a new canonicalization identifier and test vectors.

Known vector:

```text
Input:             {"z": [3, true, null], "a": "é"}
Canonical UTF-8:   {"a":"é","z":[3,true,null]}
Digest:            sha256:0c53765a3f019f951678673b2530db5ed0903eca29f596c006f3a99777eac0e8
```

### Covered content

The entire decoded legacy pack is hashed, with no field projection or exclusions:

- Schema version, stable lab ID, content version, and required capabilities.
- Every metadata field, including the full brief.
- Complete topology, interfaces, forwarding, DNS records, and endpoints.
- Initial state and editable fields.
- Objective IDs, labels, points, predicate IDs, and all predicate parameters.
- Hint text and order.

Changing any of this can change the digest even if the author forgets to bump
the content version. JSON formatting, object-member order, and equivalent escape
spellings do not change it. Some semantically equivalent array permutations do
change it intentionally; identity is conservative about ordered content.

File location, filesystem timestamps, engine implementation, engine declaration,
application/Qt versions, UI preferences, and personal progress are not pack
content and are not included. The format ID remains a separate identity field.
The original bytes are retained in the in-memory adapter so the legacy dictionary
can be reconstructed without changing its original object order. The recovery
manifest separately hashes exact file bytes, including formatting.

A digest establishes content identity, not authorship or authenticity. It is not
written into or used to reinterpret existing attempts in this checkpoint.

## Compatibility adapter and application boundary

`scenario_identity.py` contains frozen identity/runtime values and the generic
canonicalizer. It has no Qt, filesystem, simulation, grading, or hint-count rules.

`legacy_scenario.py` validates the gateway pack with the existing loader, computes
its identity, and returns a frozen wrapper. `legacy_pack()` returns a fresh
dictionary parsed from the retained original bytes. Mutating that dictionary
cannot alter the wrapper or its identity.

`__main__.load_bundled_scenarios()` retains the explicit three-file catalog and
duplicate-ID validation. Startup supplies the adapted gateway dictionary to the
unchanged catalog and retains `bridge.gateway_scenario` only as Python runtime
metadata. It is absent from the QML view and all record serialization.

### Hints

The shared identity layer accepts arbitrary JSON arrays and makes no requirement
about hint count. The untouched legacy format, session, and UI still require and
display the existing three hints. Removing that legacy restriction belongs to a
later framework change; it is not silently relaxed here.

### Historical provenance

Legacy attempts record `lab_id` and `content_version`. They do **not** record a
content digest, engine contract version, or engine behavior version. The runtime
declaration describes what is loaded now and cannot prove which engine or exact
pack bytes produced an earlier result. No provenance fields are backfilled.

The original storage paths, schemas, byte serialization, backup behavior,
validation/regrading, hint usage, and assessment idempotency remain unchanged.
In particular, historical grading still uses the current legacy engine; durable
attempt pinning and safer version-aware historical verification remain later work.
