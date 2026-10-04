# Offline image foundation — no public releases yet

This is infrastructure for later reviewed distribution. Production signing keys
and bundle release allowlists are **empty**. The commands are packaged, but no
bundle (including a test-signed bundle) is currently admitted by a normal app.
The existing local preview image remains active with its original Reset behavior.
No online acquisition, guest preparation, new UI or public image is included.

## Packaged commands

Use the Python belonging to a trusted Learning Lab installation, from any directory:

```bash
/path/to/venv/bin/python -I -B -m learning_lab.vm_preview.image_bundle validate /path/to/release.llvmimage
/path/to/venv/bin/python -I -B -m learning_lab.vm_preview.image_bundle import /path/to/release.llvmimage --vm-home /absolute/private/vm-store
```

Validation reports integrity/compatibility only, never successful gameplay. It
uses a disposable temporary directory and does not install or alter a profile.
Import requires an explicit private VM destination. Neither operation boots,
mounts or probes an image with QEMU. There are no custom-keyring/catalog/test-mode
CLI options or environment overrides. Missing `/usr/bin/gpgv` gives an actionable
refusal; nothing is installed automatically. Simulations and existing VM sessions
do not need that verifier. Keep the application and VM stores separate.

Source-only exact local registration remains available through
`tools/register_vm_image.py`; it accepts only the existing image.json hash/size.
It now publishes atomically and recognizes an exact historical installation as a
no-op. It does not create a bundle receipt or claim release-signature provenance.

## Trust and pinning

`image-catalog.json` is application-owned, bounded data, with exact image
**descriptors**, retained lesson resource/digest entries, explicit image/lesson
compatibility pairs, availability, defaults, signing keys and release entries.
Imports cannot add keys, descriptors, lesson revisions or release authorization.
A release entry authorizes the SHA-256 of the complete canonical manifest bytes,
its descriptor digest and one exact signer fingerprint. Names and signatures alone
never admit other content. The descriptor digest is SHA-256 of compact sorted-key
ASCII-escaped JSON without a trailing newline. Existing saved descriptor objects,
lesson digests, backend IDs and session records are not rewritten.

The manifest uses that same encoding **with one terminal newline**. Only UTF-8
input exactly equal to the canonical ASCII encoding is accepted. Duplicate/unknown
fields, floats, non-finite numbers, nesting over 32 and more than 8192 JSON values
are rejected. Manifest schema 1 has exactly: `schema_version`, `release_id`,
`descriptor`, `backend`, `lessons`, `members`. Members describe exact byte counts
and SHA-256 hashes; descriptor holds exact raw size/hash. Lesson compatibility must
match the catalog's ordered ID/digest list. The backend fixes amd64, raw format and
16-GiB virtual size; bundle data cannot select launch arguments or privileges.

The detached binary OpenPGP signature covers those exact manifest bytes. The
verifier uses only an explicit packaged keyring in a private temporary homedir,
never the user's keyring. Timeout is 15 seconds, combined output limit 64 KiB,
keyring limit 64 KiB. Success requires exit zero, exactly one NEWSIG/GOODSIG/VALIDSIG,
exact permitted signing/primary fingerprint and recognized unambiguous status
in the expected order, with at most one signature-ID record.
Supported signatures: OpenPGP v4, binary class 00, RSA/ECDSA/EdDSA, SHA-2 hashes,
no signature expiry. Unknown/error/revocation/expiration statuses fail closed.
Key validity/withdrawal policy belongs to the shipped trust catalog: gpgv alone
is not a current revocation service. Offline older apps cannot learn future
withdrawals until trusted application metadata is updated. No production keys
have been made or shipped. Independent fingerprint establishment and release
signing remain later owner decisions.

Session resolution uses the exact stored image descriptor and lesson digest.
Trusted older lesson resources must be retained when editing a current lesson;
never replace their bytes under an old digest. Unavailable pins fail closed without
substitution or disk migration. A compatible application rollback reads the same
records. An older app which does not know a newer pin refuses it unchanged.

- **active:** import/new sessions/Resume/Reset allowed.
- **resume-only:** exact reacquisition and existing Resume allowed; new sessions
  and Reset refused with an explanation. No alternative image is substituted.
- **withdrawn:** import/new sessions/Resume/Reset refused. Existing guest processes
  are not terminated; verified Stop remains independent of content availability.

Availability applies to the exact image and lesson revision. Catalog release and
image availability must agree. Unknown/missing retained content does not authorize
execution. Stop still uses the original process, private QMP and lifetime-lock
checks; importing does not signal a guest. Corrupt application installation files
are not repaired by this mechanism.

## Restricted bundle format

A `.llvmimage` is ZIP/ZIP64 with exactly these regular-file members:

| Member | Maximum bytes |
|---|---:|
| manifest.json | 65,536 |
| manifest.sig | 16,384 |
| image.raw.gz | 8 GiB |
| packages.json | 1 MiB |
| provenance.json | 1 MiB |
| notices.txt | 8 MiB |

Archive maximum: 8 GiB + 16 MiB. Central directory maximum: 16 KiB and exactly six
entries, checked before any member is read. Fixed-size headers are parsed with
Python's `struct` primitives. The six validated data offsets, lengths and CRCs
are captured once; member reads use bounded `pread` and streaming CRC checks.
The importer never constructs `ZipFile` or reparses mutable source headers.
The parser cross-checks local/central names, CRCs, flags, sizes, offsets and byte
ranges. Outer compression must be ZIP_STORED. Only required ZIP64 size/offset
extras and the fixed ZIP64 end/locator records are supported. Data descriptors,
encryption, comments, unknown extras, split archives, prefix/trailing bytes, gaps,
overlaps, duplicate/unknown names, traversal, directory/link/special-file entries
are refused. Source path components may not be symlinks; the file must be owned,
regular, singly linked and not group/world writable.

The inner payload is one gzip stream, no concatenated member or trailing data.
Metadata is bounded JSON/plain UTF-8 text. No member contains executable lesson
actions, host paths or shell commands interpreted by the importer.

Verification order is: structural bounds; canonical manifest and release digest;
trust/compatibility/signature; exact metadata hashes; compressed payload count/hash;
bounded decompression; exact raw count/hash and destination readback; publication.
Compressed data is first copied to private staging and fully verified, then
processed from that descriptor. Source replacement cannot redirect the opened
input. Buffer size is 1 MiB; raw output is capped by the descriptor. Synthetic
small sizes are injectable only by in-process developer fixtures; production
catalogs require 16 GiB and cannot obtain test policy through a CLI/profile/pack.

## Registration, recovery and storage

New writable state is confined to the selected VM root:

- `imports.lock`: per-store advisory import serialization.
- `staging/<random-id>/`: private incomplete/prepared candidate; never active.
- `images/<raw-sha256>/`: base.raw, manifest.json, manifest.sig, packages.json,
  release-provenance.json, notices.txt, provenance.json (exact image descriptor),
  and receipt.json (schema/kind/manifest/descriptor/signature hashes).

The complete directory is fsynced before no-replace atomic rename. **Publication
is registration**; there is no second installed-image index. The receipt exists
before publication. Member hashes are sealed outside the VM operation lock; descriptor identity,
size, mode and modification/change timestamps are rechecked at publication. Final parent directories are fsynced. Receipt data is evidence,
not a source of new trust: launch still requires the trusted exact descriptor
and full base hash. Old local directories remain valid without receipt migration.

Before publication, cancellation/crash leaves inactive staging. After publication,
the complete image remains installed even if the reply is lost; retry verifies it.
An fsync failure reports failure/uncertain durability rather than claiming success.
An exact-match retry also syncs the existing image directory and publication
parents before reporting a no-op, completing a previously interrupted sync.
Cancellation cannot undo a completed commit. No automatic repair or removal occurs.
The importer briefly shares the existing VM operation lock at publication, without
acquiring the guest lifetime lock. Long validation does not block Stop. A busy lock
refuses publication and retains preparation for inspection/retry.

An existing installation is a no-op **only if every registered member matches**.
Same raw bytes with a different manifest, signature receipt, provenance or missing
receipt conflict; the existing directory is preserved. In particular, a bundle
cannot adopt a legacy directory without a receipt. Local-only registration can
recognize the exact historical two-file directory without migrating it. Retries
revalidate from the input, not from an untrusted journal. Failed and duplicate
candidate staging directories are retained; there is no automatic pruning.

Admission budgets full raw expansion plus compressed staging, 16 MiB metadata and
4 GiB margin; checks continue while decompressing. Sparse copying in the legacy
registrar is only an optimization. This is not allocation reservation or an
aggregate quota. Start independently retains its 22-GiB free-space/3-GiB RAM checks,
18-GiB per-file limit and best-effort monitoring. Repeated retained imports and VM
generations consume space. No disk is mounted or repaired to reclaim it.

Existing image/lesson bytes, bindings, profile/backup formats, launch policy,
QMP/process identity, isolation, retained generations and display defaults are
preserved. VM images, registrations, sessions and disks remain excluded from
simulation profile backups. No backup migration or disk export is introduced.

## Later work, separately authorized

Prepare one fresh release candidate and complete licensing/source inventory;
choose project licensing, signer/custody and independent fingerprint distribution.
Run all eight lessons plus an installed-app lifecycle on another test installation.
Only then add guided online acquisition using this importer and decide hosting/
publication. The present recipe is repeatable, not demonstrated byte-identical.
