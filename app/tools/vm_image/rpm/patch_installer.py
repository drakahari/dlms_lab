"""Fresh guest installer only: hash-pinned insertion of a refusal-only gate.

The original GPL Anaconda file remains in the private preparation evidence.
Its error/quit protocol is preserved; no resolved transaction is replaced.
"""
import hashlib
import json
import os
from pathlib import Path
import sys

ORIGINAL = 'b7812f3cb0fa566635abe47cf79ebce28dea01a60fac3086a2dd8178a92e02f2'
TARGET = Path('/usr/lib64/python3.9/site-packages/pyanaconda/payload/dnf/utils.py')
ANCHOR = '        base.do_transaction(display=display)\n'
INSERT = '''        import importlib.util
        ll_spec = importlib.util.spec_from_file_location('ll_installer_admission', '/ll-inputs/installer_admission.py')
        ll_gate = importlib.util.module_from_spec(ll_spec)
        ll_spec.loader.exec_module(ll_gate)
        ll_gate.guard(base)
'''


def patched(data):
    if hashlib.sha256(data).hexdigest() != ORIGINAL:
        raise ValueError('Installer transaction source differs from verified Alma RPM')
    source = data.decode('utf-8')
    if source.count(ANCHOR) != 1:
        raise ValueError('Ambiguous installer transaction boundary')
    return source.replace(ANCHOR, INSERT + ANCHOR).encode('utf-8')


if __name__ == '__main__':
    if os.geteuid() != 0 or not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError('Explicit isolated guest-root preparation required')
    fd = os.open(TARGET, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as source:
        data = source.read(65537)
    output = patched(data)
    # Fresh installer overlay, never a learner base or the host installation.
    temporary = TARGET.with_name('ll-transaction-utils.tmp')
    with temporary.open('xb') as dest:
        dest.write(output); dest.flush(); os.fsync(dest.fileno())
    temporary.chmod(0o644)
    os.replace(temporary, TARGET)
    with Path('/ll-inputs/installer-admission-ready.json').open('x') as record:
        json.dump({'original_sha256': ORIGINAL, 'patched_sha256': hashlib.sha256(output).hexdigest()}, record)
        record.write('\n'); record.flush(); os.fsync(record.fileno())
