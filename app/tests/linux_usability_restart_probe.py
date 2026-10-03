import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtTest import QTest
from PySide6.QtCore import QPointF, Qt
from learning_lab.__main__ import build_application

root=Path(sys.argv[1]);expected=json.loads((root/'usability-expected.json').read_bytes())
app,engine,b,lock=build_application(root/'data',root/'config');w=engine.rootObjects()[0];QTest.qWait(100)
b.navigate(1);QTest.qWait(100)
assert b.view['labKey']==expected['key']
assert b.view['workspaceLayout']==expected['layout']
def visit(obj,name):
    if obj.objectName()==name and obj.isVisible():return obj
    for child in obj.childItems():
        found=visit(child,name)
        if found is not None:return found
button=visit(w.contentItem(),'openVirtualEditor')
point=button.mapToItem(w.contentItem(),QPointF(button.width()/2,button.height()/2)).toPoint()
QTest.mouseClick(w,Qt.LeftButton,Qt.NoModifier,point);QTest.qWait(100)
assert abs(visit(w.contentItem(),'diagnosticsDock').height()-expected['layout']['dock_height'])<=1
b.selectLab(expected['intro'],True)
assert b.view['guide']['index']==0 and b.session.attempt['applied']['service']['status']=='inactive'
assert b.view['historyCount']==2
w.close();app.processEvents();lock.unlock()
print('PASS: saved terminal size restored after process restart; both Linux labs and beginner archives retained.')
