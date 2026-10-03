"""Fallback resource-path proof; a declared package copy is NOT a built wheel.

Copies only Python modules and declared package data, never examples/templates.
Run from app. For real wheel verification, use tools/installed_smoke.py instead.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

APP=Path(__file__).resolve().parents[1]
manifest=tomllib.loads((APP/'pyproject.toml').read_text())
patterns=manifest['tool']['setuptools']['package-data']['learning_lab']
with tempfile.TemporaryDirectory(prefix='authoring-resource-copy-') as temp:
    root=Path(temp);package=root/'isolated/learning_lab';source=APP/'learning_lab'
    names=set(source.rglob('*.py'))
    for pattern in patterns:names.update(source.glob(pattern))
    for path in names:
        dest=package/path.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
    probe='''
import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from learning_lab import authoring
from learning_lab.__main__ import build_application
assert Path(authoring.__file__).is_relative_to(Path(sys.argv[1]))
root=Path(sys.argv[2]);app,e,b,lock=build_application(root/'data',root/'config')
try:
    assert e.rootObjects() and 'complete' in b.authoring.view['guide']
    assert 'permission_targets' in b.authoring.view['example']
    assert 'learning-lab.scenario' in b.authoring.view['prompt']
    path=root/'original.lab.json'
    assert b.authoring.prepareStarter(str(path)) and b.authoring.confirmStarter(True)
    assert b.authoring.validateLab(str(path)) and b.authoring.importValidated()
    key=next(iter(b.portables));assert b.selectLab(key)
    for _ in range(4):b.execute(b.view['guide']['command'])
    b.submit();assert b.view['grade']['score']==100
    b.restart('Challenge');b.execute('chmod 600 notes.txt');b.execute('cat notes.txt');b.submit()
    assert b.view['grade']['score']==100
    print(json.dumps({'result':'PASS','scope':'Isolated declared package copy; NOT a built wheel','resources':3,'learn':100,'challenge':100,'source_examples_used':False}))
finally:
    e.rootObjects()[0].close();app.processEvents();lock.unlock()
'''
    import os
    result=subprocess.run([sys.executable,'-I','-B','-c',probe,str(root/'isolated'),str(root/'profile')],cwd=root,
        env={**os.environ,'QT_QPA_PLATFORM':'offscreen','QT_QPA_PLATFORMTHEME':'','QT_QUICK_BACKEND':'software'},capture_output=True,text=True,timeout=30)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    print(result.stdout.strip())
