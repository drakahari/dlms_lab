import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from learning_lab.__main__ import build_application
root=Path(sys.argv[1]);expected=json.loads((root/'expected.json').read_bytes())
app,engine,b,lock=build_application(root/'data',root/'config')
for key,value in expected.items():
 a=b.labs[key].session.attempt
 assert all(a[k]==v for k,v in value.items()),key
assert b.labs['service-firewall'].command_draft=='connect portal.lab.test 22'
assert b.labs['service-firewall'].session.attempt['draft']['firewall']['rules'][0]['port']=='bad'
assert b.force_fallback
engine.rootObjects()[0].close();app.processEvents();lock.unlock()
print('PASS: fresh process retained all labs, drafts, assessments, modes, console input, and fallback')
