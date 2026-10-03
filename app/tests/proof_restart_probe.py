"""Fresh native process for isolated portable proof restart."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
root=Path(sys.argv[1]);expected=json.loads((root/'expected.json').read_bytes())
app,engine,b,lock=build_application(root/'data',root/'config');w=engine.rootObjects()[0]
assert QTest.qWaitForWindowExposed(w,5000)
assert len(b.labs)==len(expected)==5
for key,saved in expected.items():
    lab=b.labs[key]
    assert lab.session.attempt==saved['attempt'],key
    assert lab.workspace_state()==saved['workspace'],key
assert b.view['labId']=='resolver-misdirection'
assert b.view['mode']=='Challenge' and b.view['grade']['score']==100
assert b.view['commandDraft']=='nslookup orders.lab.test'
assert b.store.history(b.session.attempt['id'])[1]==2
w.close();app.processEvents();lock.unlock()
print('PASS: fresh process preserved all original and portable attempts, pins, modes, grades, drafts, pending console text and history')
