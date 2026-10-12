"""Live bounded capture for developer-only image preparation.

Always drain and hash the entire pipe, but retain at most the declared bound.
This is not a disk quota or a guest-control channel. The caller must retain
failed candidates and verify guest exit independently.
Saved capture JSON is diagnostic evidence, not an image-admission receipt. A
later I/O/directory-fsync failure can invalidate a record already written; callers
must require the completed worker's live result and the full build protocol.
"""
import hashlib
import json
import os


def write_all(output, data):
    view = memoryview(data)
    while view:
        written = output.write(view)
        if written is None or written <= 0 or written > len(view):
            raise OSError('Console log write made no valid progress')
        view = view[written:]


def capture_stream(stream, destination, state, limit, record_destination=None):
    digest = hashlib.sha256()
    state.update(bytes=0, retained_bytes=0, overflow=False, complete=False,
                 error=None, persisted=False)
    try:
        with destination.open('xb', buffering=0) as output:
            # BufferedReader.read(n) can wait for n bytes even when a guest is
            # waiting for input. os.read returns currently available pipe bytes.
            while True:
                chunk = os.read(stream.fileno(), 65536)
                if not chunk:
                    break
                before = state['bytes']
                state['bytes'] += len(chunk)
                digest.update(chunk)
                retained = chunk[:max(0, limit - before)]
                if retained:
                    write_all(output, retained)
                    state['retained_bytes'] += len(retained)
                if len(retained) != len(chunk):
                    state['overflow'] = True
            os.fsync(output.fileno())
        state['sha256'] = digest.hexdigest()
        state['complete'] = True
        if record_destination is not None:
            state['persisted'] = True
            with record_destination.open('xb', buffering=0) as record:
                write_all(record, (json.dumps(state, indent=2) + '\n').encode())
                os.fsync(record.fileno())
            fd = os.open(record_destination.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    except Exception as error:
        state['complete'] = False
        state['persisted'] = False
        state['error'] = repr(error)
