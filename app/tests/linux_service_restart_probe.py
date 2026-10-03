"""Fresh-process check for a test-created profile, including all domain state."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from learning_lab.__main__ import build_application

root=Path(sys.argv[1]);expected=json.loads((root/'expected.json').read_bytes())
app,engine,b,lock=build_application(root/'data',root/'config')
assert b.view['labKey']==expected['selected']
for name,attempt in expected['attempts'].items():
    assert b.labs[name].session.attempt==attempt,name
assert b.view['commandDraft']==expected['command']
assert b.view['mode']=='Challenge' and b.view['grade']['score']==100
assert b.view['virtualFileDraft']=='unfinished draft'
assert b.view['historyCount']==1 and b.force_fallback
b.restart('Challenge')
assert b.view['historyCount']==2 and b.session.engine.grade()['score']==30
assert not b.view['dirty'] and b.view['commandDraft']=='' and b.view['console']==''
assert b.session.attempt['applied']['cwd']=='/srv'
assert '/srv/site' not in b.session.attempt['applied']['filesystem']
assert b.session.attempt['applied']['service']['status']=='failed'
engine.rootObjects()[0].close();app.processEvents();lock.unlock()
print('PASS: four labs resumed exactly; Linux drafts, logs, pins, grade, mode, hints, cwd and history retained; reset restored initial state.')
