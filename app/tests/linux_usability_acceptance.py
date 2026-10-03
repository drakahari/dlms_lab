"""Qt pointer/keyboard and layout-state checks; native status is explicit."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QPoint, QPointF, Qt, qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.portable import load_portable
from learning_lab.theme import contrast

p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--expected-dpr',type=float,default=1);p.add_argument('--offscreen',action='store_true');args=p.parse_args()
tmp=tempfile.TemporaryDirectory(prefix='linux-usability-');root=Path(tmp.name)
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
def drag(delta,updates=False):
    handle=item('linuxTerminalDivider');pt=handle.mapToItem(w.contentItem(),QPointF(handle.width()/2,handle.height()/2)).toPoint()
    QTest.mouseMove(w,pt);QTest.qWait(60);QTest.mousePress(w,Qt.LeftButton,Qt.NoModifier,pt);QTest.qWait(30)
    for i in range(1,11):
        QTest.mouseMove(w,pt+QPoint(0,round(delta*i/10)));QTest.qWait(15)
        if updates:b.execute('journalctl');QTest.qWait(15)
    during=item('diagnosticsDock').height()
    QTest.mouseRelease(w,Qt.LeftButton,Qt.NoModifier,pt+QPoint(0,delta));QTest.qWait(100)
    check('drag release retains chosen height',abs(item('diagnosticsDock').height()-during)<=1)
    check('drag persists integral height',b.view['workspaceLayout']['dock_height']==round(during))
    return during
try:
    check('exposed',QTest.qWaitForWindowExposed(w,5000))
    if not args.offscreen:check('native Wayland',app.platformName()=='wayland')
    check('scale',abs(w.devicePixelRatio()-args.expected_dpr)<.01);report['dpr']=w.devicePixelRatio()
    w.resize(1280,900);QTest.qWait(100)
    packs={name:load_portable(Path('examples',name+'.lab.json').read_bytes()) for name in ('linux-web-document-root','linux-service-basics')}
    for name in packs:check('import '+name,b.importPack(str(Path('examples',name+'.lab.json').resolve())))
    b.selectLab(packs['linux-web-document-root'].key,True);QTest.qWait(100)
    check('terminal fills initial workspace',abs(item('diagnosticsDock').height()-item('linuxTerminalWorkspace').height())<=1)
    check('reference closed initially',item('terminalHelpTab',False) is None)
    check('Lab details closed initially',item('missionBrief',False) is None)
    check('no divider without tools',item('linuxTerminalDivider',False) is None)
    check('terminal heading and badge',item('consoleTab').property('text')=='Terminal')
    check('empty transcript teaches first action',item('consoleOutput').property('text')=='Type help and press Enter.')
    check('entry placeholder',item('commandInput').property('placeholderText')=='Type a command…')
    check('prompt is accurate',item('terminalPrompt').property('text')=='learner@lab:/srv$')
    check('bounded input and output',inside(item('commandInput'),item('linuxConsole')) and inside(item('consoleViewport'),item('linuxConsole')))
    for fg,bg in (('#eef4fc','#080e16'),('#b3c2d6','#142133'),('#eef4fc','#142133'),('#97beff','#080e16'),('#eef4fc','#243448')):
        check('console text contrast '+fg+' on '+bg,contrast(fg,bg)>=4.5)
    check('console boundary contrast',contrast('#63758c','#080e16')>=3)
    capture('terminal-first')
    # A real Qt pointer click: no forceActiveFocus precondition and no tool opened.
    field=item('commandInput');pt=field.mapToItem(w.contentItem(),QPointF(field.width()/2,field.height()/2)).toPoint()
    QTest.mouseClick(w,Qt.LeftButton,Qt.NoModifier,pt);QTest.qWait(40)
    check('direct entry click gains focus',w.activeFocusItem()==field)
    for c in 'pwd':key(ord(c))
    key(Qt.Key_Return);check('Enter executes in initial console','/srv' in b.view['console'])
    for c in 'cd /':key(ord(c))
    click('runCommand');check('Run executes and restores input focus',w.activeFocusItem()==field and b.view['serviceCwd']=='/')
    check('prompt follows simulated cd',item('terminalPrompt').property('text')=='learner@lab:/$')
    command('cd /srv')
    output=item('consoleOutput');output.forceActiveFocus();output.selectAll();selection=output.property('selectedText')
    b.refreshTheme();QTest.qWait(40)
    check('transcript selection survives ordinary refresh',bool(selection) and output.property('selectedText')==selection and w.activeFocusItem()==output)
    click('missionDetailsButton');check('Lab details opens instructions',item('missionBrief',False) is not None)
    capture('lab-details')
    click('closeLabDetails');check('details close restores trigger focus',w.activeFocusItem()==item('missionDetailsButton'))
    click('hintButton');click('hintButton')
    check('only latest hint occupies sidebar',item('latestHint').property('text')==b.view['hints'][-1] and item('revealedDetailHint0',False) is None)
    click('missionDetailsButton');check('previous hints can be reread',item('revealedDetailHint0').property('text').endswith(b.view['hints'][0]) and item('revealedDetailHint1').property('text').endswith(b.view['hints'][1]))
    click('closeLabDetails')
    check('simulation indicator remains in window',inside(item('simulationIndicator'),w.contentItem()))
    click('openTerminalHelp');check('reference label and focus',item('terminalHelpTab').property('text')=='Command reference' and w.activeFocusItem()==item('terminalHelpTab'))
    b.execute('pwd');b.refreshTheme();QTest.qWait(40)
    check('output does not steal reference focus',w.activeFocusItem()==item('terminalHelpTab'))
    click('closeLinuxTools');check('closing reference focuses input',w.activeFocusItem()==item('commandInput'))
    check('closing removes divider',item('linuxTerminalDivider',False) is None)
    click('openVirtualEditor');QTest.qWait(100)
    check('editor opens with focus',w.activeFocusItem()==item('virtualFileEditor'))
    draft=b.view['virtualFileDraft']+'# retained draft\n';item('virtualFileEditor').setProperty('text',draft)
    b.execute('pwd');b.refreshTheme();QTest.qWait(50)
    check('editor focus and draft survive output',w.activeFocusItem()==item('virtualFileEditor') and b.view['virtualFileDraft']==draft)
    click('closeLinuxTools');click('openVirtualEditor')
    check('closing editor preserves draft',b.view['virtualFileDraft']==draft)
    item('virtualFileEditor').setProperty('text',b.view['virtualFileApplied'])
    before=item('diagnosticsDock').height();chosen=drag(-80,updates=True)
    check('pointer actually moved divider',abs(chosen-before)>50)
    for i in range(20):
        b.execute('journalctl' if i%2 else 'ls -l /srv');b.refreshTheme();QTest.qWait(10)
        check('output refresh retains size '+str(i),abs(item('diagnosticsDock').height()-chosen)<=1)
        check('input remains visible '+str(i),inside(item('commandInput'),item('diagnosticsDock')))
    chosen=drag(45,updates=True)
    item('linuxTerminalDivider').forceActiveFocus();key(Qt.Key_Up);QTest.qWait(60)
    report['keyboard_resize']={'chosen':chosen,'height':item('diagnosticsDock').height(),'saved':b.view['workspaceLayout'],'focus':w.activeFocusItem().objectName()}
    check('keyboard resizes divider',abs(item('diagnosticsDock').height()-(chosen-20))<=1)
    key(Qt.Key_Down);QTest.qWait(60);check('keyboard resize restores and saves choice',b.view['workspaceLayout']['dock_height']==round(chosen))
    for size in ((800,600),(1024,768),(1180,860),(1280,900)):
        w.resize(*size);QTest.qWait(100)
        check('requested height retained at '+str(size),b.view['workspaceLayout']['dock_height']==round(chosen))
        check('input in terminal at '+str(size),inside(item('commandInput'),item('diagnosticsDock')))
        check('terminal in window at '+str(size),inside(item('diagnosticsDock'),w.contentItem()))
        check('console has output line at '+str(size),item('consoleViewport').property('availableHeight')>=20)
        check('tools fit window at '+str(size),inside(item('closeLinuxTools'),w.contentItem()))
        tools=item('linuxServiceWorkspace');footer=item('draftWarning')
        report['geometry_'+str(size)]={name:[item(name).height(),item(name).mapToItem(w.contentItem(),QPointF(0,0)).y()] for name in ('workspaceFraming','missionPanel','linuxTerminalWorkspace','linuxTerminalSplit','diagnosticsDock','linuxServiceWorkspace','draftWarning')}
        check('tools do not overlap footer at '+str(size),tools.mapToItem(w.contentItem(),QPointF(0,tools.height())).y()<=footer.mapToItem(w.contentItem(),QPointF(0,0)).y())
        check('prompt and command retain space at '+str(size),item('commandInput').width()>=150)
        click('closeLinuxTools');check('sole console has no divider at '+str(size),item('linuxTerminalDivider',False) is None)
        capture('console-'+str(size[0]))
        # A taller viewport must actually redraw text below the former clip boundary.
        viewport=item('consoleViewport');pos=viewport.mapToItem(w.contentItem(),QPointF(4,viewport.height()*0.7));dpr=w.devicePixelRatio();pic=w.grabWindow()
        count=sum(1 for y in range(round(pos.y()*dpr),round((pos.y()+viewport.height()*0.3-2)*dpr)) for x in range(round(pos.x()*dpr),round((pos.x()+viewport.width()-8)*dpr)) if all(channel>180 for channel in pic.pixelColor(x,y).getRgb()[:3]))
        check('transcript redraw fills expanded viewport at '+str(size),count>10)
        click('openVirtualEditor')
        for _ in range(3):b.execute('journalctl');QTest.qWait(15)
        if size==(800,600):capture('small-divider')
    check('expansion restores chosen size',abs(item('diagnosticsDock').height()-chosen)<=1)
    capture('retained-divider')
    click('closeLinuxTools');check('closing tools returns full terminal',abs(item('diagnosticsDock').height()-item('linuxTerminalWorkspace').height())<=1)
    click('openTerminalHelp');check('help is on demand',item('terminalHelpTab').property('checked'))
    check('reopening tools retains choice',abs(item('diagnosticsDock').height()-chosen)<=1)
    click('closeLinuxTools')
    b.selectLab(packs['linux-service-basics'].key,True);QTest.qWait(100)
    check('beginner clearly has no config fault','configuration' in b.view['missionGoal'] and b.session.attempt['applied']['service']['status']=='inactive')
    check('beginner editor hidden',item('openVirtualEditor',False) is None)
    check('only first command explained',b.view['guide']['index']==0 and item('guideCommand').property('text')=='systemctl status lab-web')
    check('compact progress replaces objective list',item('missionProgress').property('text')=='Not submitted · 1 objective')
    check('full instructions absent by default',item('missionBrief',False) is None)
    capture('beginner-inspect')
    click('openTerminalHelp');check('beginner Help describes fixed healthy configuration','read-only' in b.view['terminalHelp'])
    click('closeLinuxTools')
    command('systemctl status lab-web');check('next step explains start',b.view['guide']['index']==1)
    capture('beginner-start')
    command('systemctl start lab-web');check('next step explains verification',b.view['guide']['index']==2)
    command('systemctl status lab-web');check('running verified',b.view['guide']['verified'])
    b.submit();check('beginner full grade',b.view['grade']['score']==100);capture('beginner-verified')
    old=b.view['attemptId'];b.restart('Challenge');QTest.qWait(50)
    check('Challenge hides walkthrough and hints',b.view['guide']=={} and item('beginnerGuide',False) is None and item('hintButton',False) is None)
    click('missionDetailsButton');check('Challenge details have no revealed hint text',item('revealedDetailHint0',False) is None);click('closeLabDetails')
    check('Learn archive preserved',b.store.history(b.view['attemptId'])[0][0]['id']==old)
    command('systemctl start lab-web');b.submit();check('Challenge final-state grade',b.view['grade']['score']==100)
    b.restart('Learn');check('reset restores step one and stopped state',b.view['guide']['index']==0 and b.session.attempt['applied']['service']['status']=='inactive')
    b.selectLab(packs['linux-web-document-root'].key,True);click('openVirtualEditor')
    check('cross-lab size retained',abs(item('diagnosticsDock').height()-chosen)<=1)
    saved=dict(b.view['workspaceLayout']);b.selectLab('gateway-dns',True);check('networking layout independent',b.view['workspaceLayout']=={})
    b.selectLab(packs['linux-web-document-root'].key,True);b.flush()
    expected={'key':packs['linux-web-document-root'].key,'layout':saved,'intro':packs['linux-service-basics'].key}
    (root/'usability-expected.json').write_text(json.dumps(expected));w.close();app.processEvents();lock.unlock()
    process=subprocess.run([sys.executable,'-B','tests/linux_usability_restart_probe.py',str(root)],capture_output=True,text=True,timeout=20)
    report['restart']=process.stdout+process.stderr;check('fresh process retains layout and both labs',process.returncode==0)
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
