"""Execute the actual previous reader against disposable v1/v2 backups.

Run from app: python3 -B tests/backup_compatibility_acceptance.py
Requires the committed baseline in local Git, never writes Git or real profiles.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios, ProfileLocks
from learning_lab.catalog import CatalogBridge
from learning_lab.profile_backup import read_backup

BASELINE = '673e4f0c2e435920188da629744a52196f589e41'
app = QCoreApplication([])
with tempfile.TemporaryDirectory(prefix='backup-previous-reader-') as temp:
    root = Path(temp)
    previous = root/'previous/app'
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE,
                                     'app/learning_lab'], cwd=ROOT.parent).decode().splitlines()
    assert names
    for name in names:
        path = root/'previous'/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(subprocess.check_output(['git', 'show', BASELINE+':'+name], cwd=ROOT.parent))
    data = root/'source/data'; config = root/'source/config'
    data.mkdir(parents=True); config.mkdir()
    locks = ProfileLocks(data, config)
    bridge = CatalogBridge(load_bundled_scenarios()[0], data, config)
    bridge.profile_locks = locks
    try:
        v1 = root/'v1.llbackup'; v2 = root/'v2.llbackup'
        assert bridge.backupProfile(str(v1)) and read_backup(v1).manifest['schema_version'] == 1
        assert bridge.setLibraryState('gateway-dns', 'hidden')
        assert bridge.backupProfile(str(v2)) and read_backup(v2).manifest['schema_version'] == 2
        probe = '''
import json,sys
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from learning_lab import profile_backup as pb
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
root=Path(sys.argv[1]); previous=Path(sys.argv[2])
assert Path(pb.__file__).resolve().is_relative_to(previous) and pb.VERSION==1
app=QCoreApplication([])
data=root/'old-open/data';config=root/'old-open/config'
data.mkdir(parents=True);config.mkdir()
b=CatalogBridge(load_bundled_scenarios()[0],data,config)
def contents(): return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
before=contents(); before_tree={str(p.relative_to(root)) for p in root.rglob("*")}
try: pb.read_backup(root/'v2.llbackup')
except ValueError as exc: rejection=str(exc)
else: raise AssertionError('previous reader accepted v2')
destination=root/'rejected-destination'
try: pb.restore(pb.read_backup(root/'v2.llbackup'),destination,confirmed=True)
except ValueError: pass
else: raise AssertionError('previous restore accepted v2')
assert not destination.exists()
assert not b.previewRestore(str(root/'v2.llbackup'),str(root))
assert b.restore_pending is None and not b.confirmRestore(True)
assert contents()==before and {str(p.relative_to(root)) for p in root.rglob('*')}==before_tree
assert not list(root.glob('Learning-Lab-restored-*'))
# Positive control proves the old reader is usable, not just broken generally.
assert b.previewRestore(str(root/'v1.llbackup'),str(root))
destination=b.restore_pending[1]
assert b.confirmRestore(True) and (destination/'data/current.json').is_file()
for lab in b.labs.values():lab.timer.stop()
print(json.dumps({'result':'PASS','reader_version':pb.VERSION,'v2_rejection':rejection,
 'v2_low_level_rejected':True,'v2_preview_rejected':True,'no_partial_restore':True,
 'open_profile_unchanged':True,'v1_positive_control_restored':True}))
'''
        result = subprocess.run([sys.executable, '-B', '-c', probe, str(root), str(previous)],
            cwd=previous, env={**os.environ, 'PYTHONPATH':str(previous)}, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout+result.stderr
        print(json.dumps({'baseline':BASELINE, **json.loads(result.stdout)}, indent=2))
    finally:
        for lab in bridge.labs.values(): lab.timer.stop()
        locks.unlock()
