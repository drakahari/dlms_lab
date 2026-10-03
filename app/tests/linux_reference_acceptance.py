"""Qt pointer/keyboard and layout-state checks; native status is explicit."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QPoint, QPointF, Qt, qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.portable import load_portable

p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--expected-dpr',type=float,default=1);p.add_argument('--offscreen',action='store_true');args=p.parse_args()
tmp=tempfile.TemporaryDirectory(prefix='linux-reference-');root=Path(tmp.name)
messages=[];qInstallMessageHandler(lambda typ,ctx,msg:messages.append(msg))
app,engine,b,lock=build_application(root/'data',root/'config');w=engine.rootObjects()[0]
report={'platform':app.platformName(),'input':'QtTest synthesized pointer and key events; not physical input','checks':[],'qml_messages':messages}
out=Path('evidence')
def check(name,ok):
    report['checks'].append({'name':name,'passed':bool(ok)})
    if not ok:raise AssertionError(name)
def item(name,required=True):
    def visit(obj):
        if obj.objectName()==name and obj.isVisible():return obj
        for child in obj.childItems():
            found=visit(child)
            if found is not None:return found
    found=visit(w.contentItem())
    if required and found is None:raise AssertionError('Missing '+name)
    return found
def click(name):
    widget=item(name);widget.forceActiveFocus();QTest.qWait(30)
    pt=widget.mapToItem(w.contentItem(),QPointF(widget.width()/2,widget.height()/2)).toPoint()
    QTest.mouseClick(w,Qt.LeftButton,Qt.NoModifier,pt);QTest.qWait(50)
def key(code,mod=Qt.NoModifier):QTest.keyClick(w,code,mod);QTest.qWait(10)
def command(text):
    item('commandInput').forceActiveFocus();key(Qt.Key_A,Qt.ControlModifier)
    for c in text:key(ord(c))
    key(Qt.Key_Return)
def capture(name):
    QTest.qWait(100);pic=w.grabWindow();check('rendered '+name,not pic.isNull());pic.save(str(out/(args.label+'-'+name+'.png')))
def inside(child,parent):
    pt=child.mapToItem(parent,QPointF(0,0))
    return pt.x()>=-1 and pt.y()>=-1 and pt.x()+child.width()<=parent.width()+1 and pt.y()+child.height()<=parent.height()+1
try:
    check('exposed',QTest.qWaitForWindowExposed(w,5000))
    if not args.offscreen:check('native Wayland',app.platformName()=='wayland')
    check('scale',abs(w.devicePixelRatio()-args.expected_dpr)<.01);report['dpr']=w.devicePixelRatio()
    w.resize(1280,900);QTest.qWait(100)
    packs={n:load_portable(Path('examples',n+'.lab.json').read_bytes()) for n in ('linux-web-document-root','linux-service-basics')}
    for n in packs:check('import '+n,b.importPack(str(Path('examples',n+'.lab.json').resolve())))
    b.selectLab(packs['linux-web-document-root'].key,True);QTest.qWait(100)
    check('details initially collapsed',item('labDetailsView',False) is None)
    click('missionDetailsButton');check('nonmodal details opens',item('labDetailsView') is not None)
    check('wide reference has readable width',item('missionPanel').width()>=320)
    item('missionDetailsButton').forceActiveFocus()
    for _ in range(100):
        if w.activeFocusItem()==item('commandInput'):break
        key(Qt.Key_Tab)
    check('Tab can leave reference and reach input',w.activeFocusItem()==item('commandInput'))
    field=item('commandInput');pt=field.mapToItem(w.contentItem(),QPointF(field.width()/2,field.height()/2)).toPoint()
    QTest.mouseClick(w,Qt.LeftButton,Qt.NoModifier,pt);QTest.qWait(30)
    check('details permits direct input click',w.activeFocusItem()==field)
    command('pwd');check('command executes with instructions open','/srv' in b.view['console'] and item('labDetailsView') is not None)
    key(Qt.Key_Escape);check('Escape in terminal does not dismiss details',item('labDetailsView') is not None)
    click('openVirtualEditor');check('details and editor coexist',item('labDetailsView') is not None and item('virtualFileEditor') is not None)
    check('applied version initially collapsed',item('virtualFileApplied',False) is None)
    editor=item('virtualFileEditor');draft=b.view['virtualFileDraft']+'# retained reference draft\n';editor.setProperty('text',draft);QTest.qWait(50)
    check('draft padding and font preserved',editor.property('padding')==10 and editor.property('font').pixelSize()==14)
    editor_width=editor.width();mission_width=item('missionPanel').width()
    command('ls /srv');check('terminal does not close details or discard edit',item('labDetailsView') is not None and b.view['virtualFileDraft']==draft)
    click('terminalHelpTab');check('switching tool retains instructions and draft',item('labDetailsView') is not None and b.view['virtualFileDraft']==draft)
    click('virtualEditorTab');item('virtualFileEditor').forceActiveFocus();QTest.qWait(50)
    check('tool switch keeps sidebar width',item('missionPanel').width()==mission_width)
    key(Qt.Key_Tab);check('editor Tab reaches applied disclosure',w.activeFocusItem()==item('appliedVersionToggle'))
    key(Qt.Key_Return);QTest.qWait(50);check('applied disclosure opens',item('virtualFileApplied',False) is not None)
    check('applied remains separate',item('virtualFileApplied').property('text')!=draft)
    key(Qt.Key_Tab);check('Tab enters applied view',w.activeFocusItem()==item('virtualFileApplied'))
    key(Qt.Key_Tab,Qt.ShiftModifier);check('Shift Tab returns disclosure',w.activeFocusItem()==item('appliedVersionToggle'))
    key(Qt.Key_Return);check('applied collapses without changing draft',item('virtualFileApplied',False) is None and b.view['virtualFileDraft']==draft)
    # Details has its own scroll position, unaffected by terminal output/tools.
    ref=item('labDetailsScroll');ref.forceActiveFocus();key(Qt.Key_PageDown);QTest.qWait(50)
    top=ref.property('contentItem').property('contentY');check('independent reference scroll works',top>0)
    b.execute('pwd');b.refreshTheme();QTest.qWait(50)
    check('refresh preserves reference scroll and focus',ref.property('contentItem').property('contentY')==top and w.activeFocusItem()==ref)
    ref.property('contentItem').setProperty('contentY',0)
    capture('wide-details-editor')
    item('virtualFileEditor').forceActiveFocus();QTest.qWait(60)
    key(Qt.Key_Home,Qt.ControlModifier);QTest.qWait(60)
    capture('editor-padding')
    for size in ((800,600),(1024,768),(1180,860),(1280,900)):
        w.resize(*size);QTest.qWait(150)
        check('details still open at '+str(size),item('labDetailsView') is not None)
        check('reference and input have separate bounds at '+str(size),inside(item('labDetailsView'),item('missionPanel')) and inside(item('commandInput'),item('linuxConsole')))
        check('input width at '+str(size),item('commandInput').width()>=150)
        check('output line at '+str(size),item('consoleViewport').property('availableHeight')>=20)
        check('reference readable viewport at '+str(size),item('labDetailsScroll').property('availableHeight')>=50)
        check('editor text not squeezed at '+str(size),item('virtualFileEditor').width()>=350 and item('virtualFileEditor').property('font').pixelSize()==14)
        tools=item('linuxServiceWorkspace');footer=item('draftWarning')
        check('tools above footer at '+str(size),tools.mapToItem(w.contentItem(),QPointF(0,tools.height())).y()<=footer.mapToItem(w.contentItem(),QPointF(0,0)).y())
        command('pwd');check('entry with all panels at '+str(size),item('labDetailsView') is not None and b.view['virtualFileDraft']==draft)
        # Resize the existing framing divider, horizontally wide and vertically compact.
        mission=item('missionPanel');horizontal=size[0]>=1000
        pt=mission.mapToItem(w.contentItem(),QPointF(mission.width()+3,mission.height()/2) if horizontal else QPointF(mission.width()/2,mission.height()+3)).toPoint()
        before=mission.width() if horizontal else mission.height();delta=QPoint(30,0) if horizontal else QPoint(0,-8)
        QTest.mouseMove(w,pt);QTest.qWait(60);QTest.mousePress(w,Qt.LeftButton,Qt.NoModifier,pt);QTest.qWait(30)
        for n in range(1,6):QTest.mouseMove(w,pt+delta*n/5);QTest.qWait(20)
        QTest.mouseRelease(w,Qt.LeftButton,Qt.NoModifier,pt+delta);QTest.qWait(100)
        after=mission.width() if horizontal else mission.height()
        check('reference divider resizes at '+str(size),abs(after-before)>=5)
        command('pwd');check('reference size survives command at '+str(size),(mission.width() if horizontal else mission.height())==after)
        check('draft survives reference resize at '+str(size),b.view['virtualFileDraft']==draft)
        if size==(800,600):
            handle=item('linuxTerminalDivider');pt=handle.mapToItem(w.contentItem(),QPointF(handle.width()/2,handle.height()/2)).toPoint()
            QTest.mouseMove(w,pt);QTest.qWait(60);QTest.mousePress(w,Qt.LeftButton,Qt.NoModifier,pt);QTest.qWait(30)
            for n in range(1,6):QTest.mouseMove(w,pt+QPoint(0,-n));QTest.qWait(20)
            chosen=item('diagnosticsDock').height()
            QTest.mouseRelease(w,Qt.LeftButton,Qt.NoModifier,pt+QPoint(0,-5));QTest.qWait(100)
            check('compact terminal drag retains actual chosen size',abs(item('diagnosticsDock').height()-chosen)<=1 and b.view['workspaceLayout']['dock_height']==round(chosen))
            command('pwd');check('compact terminal drag survives output',abs(item('diagnosticsDock').height()-chosen)<=1)

        capture('combined-'+str(size[0]))
    click('closeLinuxTools');check('closing tools leaves details open',item('labDetailsView') is not None)
    click('openVirtualEditor');check('reopening restores draft',b.view['virtualFileDraft']==draft)
    b.selectLab(packs['linux-service-basics'].key,True);QTest.qWait(100)
    check('lab switching keeps details open',item('labDetailsView') is not None)
    b.restart('Challenge');QTest.qWait(50);check('Challenge reference hides hints',item('revealedDetailHint0',False) is None and item('labDetailsView') is not None)
    b.selectLab(packs['linux-web-document-root'].key,True);QTest.qWait(50)
    check('returning retains file draft',b.view['virtualFileDraft']==draft)
    click('missionDetailsButton');check('explicit collapse closes reference',item('labDetailsView',False) is None)
    click('missionDetailsButton');click('closeLabDetails');check('explicit Close closes reference',item('labDetailsView',False) is None)
    check('no QML errors',not any(any(e in m for e in ('ReferenceError','TypeError','Binding loop','Cannot assign')) for m in messages))
    report['result']='PASS'
except Exception as exc:
    report.update(result='FAIL',error=str(exc))
    try:capture('failure')
    except Exception:pass
finally:
    w.close();app.processEvents();lock.unlock()
    (out/(args.label+'.json')).write_text(json.dumps(report,indent=2))
    print(json.dumps({k:report.get(k) for k in ('result','error','platform','dpr','restart')}|{'checks':len(report['checks']),'qml_messages':messages[-10:]},indent=2))
    tmp.cleanup()
sys.exit(0 if report['result']=='PASS' else 1)
