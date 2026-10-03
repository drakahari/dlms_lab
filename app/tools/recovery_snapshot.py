"""Create a new private, verified recovery copy; never overwrite old snapshots."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat


def inventory(root):
    files, directories = {}, []
    for p in sorted(root.rglob('*')):
        info = p.lstat(); rel = str(p.relative_to(root))
        if stat.S_ISDIR(info.st_mode): directories.append(rel)
        elif stat.S_ISREG(info.st_mode):
            files[rel] = {'bytes': info.st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                          'mode': stat.S_IMODE(info.st_mode), 'mtime_ns': info.st_mtime_ns}
        else: raise RuntimeError('Unsupported file type: ' + str(p))
    return {'directories': directories, 'files': files}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', required=True)
    args = parser.parse_args()
    if not re.fullmatch('[a-z0-9-]{1,64}', args.label): raise SystemExit('Invalid snapshot label.')
    os.umask(0o077)
    parent = Path.home()/'.local/state/omarchy-learning-lab/recovery'
    snapshots = sorted(parent.glob('*/manifest.json'))
    if not snapshots: raise SystemExit('No previous recovery manifest. Stop and inspect.')
    for path in snapshots:
        manifest = json.loads(path.read_bytes())
        for name, expected in manifest['components'].items():
            if inventory(path.parent/name) != expected: raise SystemExit('Recovery verification failed: ' + str(path))
        if hashlib.sha256((path.parent/'Omarchy-Learning-Lab-v0.1-Spec.docx').read_bytes()).hexdigest() != manifest['spec_sha256']:
            raise SystemExit('Specification copy failed verification.')
    roots = {k: Path(v) for k, v in manifest['original_roots'].items()}
    def idle():
        if (roots['progress']/'writer.lock').exists(): raise SystemExit('Close the real Learning Lab before snapshotting.')
        for p in Path('/proc').glob('[0-9]*/cmdline'):
            try: command = p.read_bytes().split(b'\0')
            except OSError: continue
            if any(command[i:i+2] == [b'-m', b'learning_lab'] for i in range(len(command)-1)):
                raise SystemExit('Learning Lab is running; close it before snapshotting.')
    idle()
    before = {k: inventory(v) for k, v in roots.items()}
    dest = parent/(args.label+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    dest.mkdir(mode=0o700)
    for name, root in roots.items(): shutil.copytree(root, dest/name, copy_function=shutil.copy2)
    spec = roots['source'].parent/'Omarchy-Learning-Lab-v0.1-Spec.docx'
    shutil.copy2(spec, dest/spec.name)
    idle()
    if before != {k: inventory(v) for k, v in roots.items()} or before != {k: inventory(dest/k) for k in roots}:
        raise SystemExit('Snapshot verification FAILED; preserve partial copy and stop.')
    manifest = {'snapshot_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
                'original_roots': {k: str(v) for k,v in roots.items()}, 'components': before,
                'spec_sha256': hashlib.sha256(spec.read_bytes()).hexdigest(), 'git': 'Metadata untouched.'}
    if hashlib.sha256((dest/spec.name).read_bytes()).hexdigest() != manifest['spec_sha256']:
        raise SystemExit('Specification changed during copy.')
    (dest/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (dest/'VERIFIED.json').write_text(json.dumps({'result':'PASS','previous_snapshots_verified':len(snapshots)},indent=2)+'\n')
    for p in dest.rglob('*'):
        if p.is_file():
            with p.open('rb') as stream: os.fsync(stream.fileno())
    print(json.dumps({'snapshot':str(dest),'result':'PASS','previous_snapshots_verified':len(snapshots)},indent=2))


if __name__ == '__main__': main()
