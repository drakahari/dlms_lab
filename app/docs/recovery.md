# Progress and recovery

## Normal saves

A process-wide `QLockFile` protects the app data directory. Gateway/DNS and subnet attempts use JSON schema 1; firewall attempts use schema 2. Unfinished invalid rule text can be saved as a bounded draft, but applied rules must validate. Draft edits save after a 300 ms debounce; actions and clean exit flush immediately. Each assessment is identified by attempt UUID plus applied revision. Repeated submission returns the existing result. A later Apply creates a new revision only when applied values actually change.

A save validates the new record, writes the previous validated primary to the backup, and atomically replaces the primary. A first save also creates the backup. Temporary files live beside their destination; file and directory fsync are used. An interrupted temporary file is never treated as progress.

Reset and mode changes write the prior attempt archive before saving a new current attempt. UUID filenames avoid collisions; a crash between those steps may leave the same attempt represented by an archive and current file. History deduplicates that ID. The old attempt is retained and subsequent reset is safe.

## Three labs, no record migration

Existing gateway/DNS records retain their original paths and schema/content versions. The subnet lab uses `labs/subnet-boundary/` below the same app data root, with its own primary, backup and archives. The firewall lab uses `labs/service-firewall/` with schema 2 records containing applied and draft TCP policy. One root writer lock covers all three stores. Switching labs flushes the current attempt and resumes the other; a failed save prevents switching. Reset and mode changes affect only the selected lab. Histories remain separate and none is pruned.

`selection.json` in the app config directory records the selected bundled ID at schema 1 using atomic replacement. Invalid, unknown newer, or unsupported selection files are preserved; selection then works for the session only. They do not contain attempt data. No migration is necessary for the new lab stores. Existing schema 1 snapshots are not rewritten into schema 2. Schema 2 is used only for firewall attempts; older incompatible applications must preserve it as unsupported/newer data.

## Automatic recovery

If the current record is corrupt but the backup validates, the exact damaged file is moved to `current.corrupt-<timestamp>.json`, then the valid backup is restored. The UI reports recovery and warns that the latest changes may be absent. A missing current file can also recover from the backup. Corrupt archived records remain on disk and are reported in History.

Unknown newer progress versions or a mismatched pack content version are preserved and opened in read-only recovery mode. The app never downgrades them by substituting an older backup. There are no record migrations in this release; future migrations must be explicit, sequential, backed up and fixture-tested.

## When neither record can be read

The app disables state-changing actions and shows the reason. It preserves both files. Do not delete them to dismiss the warning.

1. Close the app.
2. Copy the entire app data directory to a separate backup before any repair.
3. If the records use a newer schema/content version, reopen them with the matching application version.
4. Otherwise inspect the primary, backup and preserved corruption files. Restore a known-good compatible snapshot only after validating it.
5. To practice while recovery remains unresolved, launch with explicit new `--data-dir` and `--config-dir` locations. This leaves the original records untouched.

A storage permission or disk-space failure freezes editing and reports that changes remain only in memory. Keep the window open while resolving the issue, then use **Retry save**. Closing with unsaved changes requires an explicit discard confirmation. This release does not provide an interactive repair wizard or merge recovered histories automatically.

History is never permanently pruned automatically. The current console and recall list are bounded; previous attempt archives remain available. Each record has a 10 MiB load/save safety limit. There is no bulk export or delete UI. History now offers separate individual attempt export.

## Portable records and workspace sidecars

Portable attempts use pinned schema-3 envelopes in separate digest-keyed stores.
Content and engine mismatches remain read-only without backup downgrade. Unknown
workspace sidecars also freeze that attempt and are preserved. No automatic
legacy conversion or personal-history import is provided. See
[framework storage and rollback](framework.md#storage-and-rollback) for locations,
atomicity boundaries, and recovery-source considerations.
