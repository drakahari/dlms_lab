"""Fresh-process native restart acceptance; launched only by the test harness."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application

app,engine,bridge,lock=build_application(Path(sys.argv[1]),Path(sys.argv[2]))
window=engine.rootObjects()[0]
assert QTest.qWaitForWindowExposed(window,5000)
assert bridge.session.attempt['id']==sys.argv[3]
assert bridge.pack['lab_id']=='service-firewall'
assert bridge.session.attempt['mode']=='Challenge'
assert bridge.session.attempt['applied']['firewall']['rules'][0]['action']=='deny'
assert bridge.session.attempt['draft']['firewall']['rules'][0]['action']=='allow'
assert bridge.session.attempt['draft']['firewall']['rules'][0]['source']=='192.168.50.20/32'
rows,count,_=bridge.store.history(bridge.session.attempt['id'])
assert count==3
assert any(a['hints']==3 and any(r['score']==100 for r in a['assessments'].values()) for a in rows)
assert bridge.selectLab('subnet-boundary',True)
assert bridge.session.attempt['mode']=='Challenge'
assert bridge.session.attempt['applied']['prefix']==28
assert bridge.session.attempt['draft']['prefix']=='24'
rows,count,_=bridge.store.history(bridge.session.attempt['id'])
assert count==2
assert any(a['hints']==3 and a['assessments'].get('1',{}).get('score')==100 for a in rows)
assert bridge.selectLab('gateway-dns',True)
assert bridge.session.attempt['applied']['gateway']=='192.168.50.254'
assert bridge.session.attempt['draft']['gateway']=='192.168.50.1'
rows,count,_=bridge.store.history(bridge.session.attempt['id'])
assert count==2
assert any(a['hints']==1 and a['assessments'].get('2',{}).get('score')==100 for a in rows)
assert bridge.force_fallback
bridge.flush()
window.close();app.processEvents();lock.unlock()
print(json.dumps({'fresh_process_restart':'PASS','platform':app.platformName(),'all_three_labs_drafts_and_history_preserved':True}))
