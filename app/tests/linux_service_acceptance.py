"""Isolated Qt UI acceptance; synthesized input never proves physical keys.

Use --offscreen for sandbox rendering. Native runs require the owner's existing
GUI session; this script does not change compositor or monitor settings.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QObject, QPointF, Qt, qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.portable import load_portable

p=argparse.ArgumentParser()
p.add_argument('--label',required=True)
p.add_argument('--expected-dpr',type=float,default=1)
p.add_argument('--offscreen',action='store_true')
args=p.parse_args()
messages=[];qInstallMessageHandler(lambda typ,ctx,msg:messages.append(msg))
tmp=tempfile.TemporaryDirectory(prefix='linux-service-acceptance-');root=Path(tmp.name)
app,engine,b,lock=build_application(root/'data',root/'config');w=engine.rootObjects()[0]
out=Path('evidence');out.mkdir(exist_ok=True)
report={'label':args.label,'platform':app.platformName(),'checks':[],
        'input':'QtTest synthesized events; physical keyboard unverified',
        'native_file_choosers':'unverified; imports/exports use controller API',
        'qml_messages':messages}
def check(name,condition):
    report['checks'].append({'name':name,'passed':bool(condition)})
    if not condition:raise AssertionError(name)
def key(code,modifier=Qt.NoModifier):
    QTest.keyClick(w,code,modifier);QTest.qWait(8)
def current():return w.activeFocusItem().objectName() if w.activeFocusItem() else ''
def in_region(name):
    focus=w.activeFocusItem()
    while focus:
        if focus.objectName()==name:return True
        focus=focus.parentItem()
    return False
def tab_to(name):
    trail=[]
    for _ in range(180):
        if current()==name:return
        key(Qt.Key_Tab);trail.append(current())
    raise AssertionError('Tab cannot reach '+name+'; trail='+str(trail[-40:]))
def activate(name):
    # Linux tools now open on demand; the terminal owns the main workspace.
    if name in ('virtualEditorTab','terminalHelpTab'):
        tab_to('openVirtualEditor' if name=='virtualEditorTab' else 'openTerminalHelp');key(Qt.Key_Return)
    tab_to(name);key(Qt.Key_Return)
def replace(name,text):
    tab_to(name);key(Qt.Key_A,Qt.ControlModifier)
    for char in text:key(Qt.Key_Return if char=='\n' else ord(char))
def command(text):replace('commandInput',text);key(Qt.Key_Return)
def item(name):
    def walk(obj):
        if obj.objectName()==name and obj.isVisible():return obj
        for child in obj.childItems():
            found=walk(child)
            if found is not None:return found
    found=walk(w.contentItem())
    if found is None:
        candidate=w.findChild(QObject,name)
        if candidate is not None and candidate.property('visible'):found=candidate
    if found is None:raise AssertionError('Missing visible item '+name)
    return found
def inside(child,parent):
    pt=child.mapToItem(parent,QPointF(0,0))
    return pt.x()>=-1 and pt.y()>=-1 and pt.x()+child.width()<=parent.width()+1 and pt.y()+child.height()<=parent.height()+1
def capture(name):
    QTest.qWait(100);image=w.grabWindow();check('rendered '+name,not image.isNull())
    image.save(str(out/(args.label+'-'+name+'.png')))
try:
    check('window exposed',QTest.qWaitForWindowExposed(w,5000))
    if not args.offscreen:check('native Wayland',app.platformName()=='wayland')
    w.resize(1280,900);QTest.qWait(150)
    report.update(dpr=w.devicePixelRatio(),graphics_api=str(w.rendererInterface().graphicsApi()))
    check('expected scale',abs(w.devicePixelRatio()-args.expected_dpr)<.01)
    example=Path('examples/linux-web-document-root.lab.json');scenario=load_portable(example.read_bytes())
    check('import Linux data pack',b.importPack(str(example.resolve())))
    activate('open-'+scenario.key);check('Linux terminal workspace visible',item('linuxTerminalWorkspace') is not None)
    capture('initial')
    activate('consoleTab')
    for text in ('help','systemctl status lab-web','journalctl -u lab-web','cat /etc/lab-web.conf','ls -l /srv'):command(text)
    check('diagnosis names missing root','/srv/site' in b.view['console'])
    command('mkdir site');command('systemctl start lab-web')
    activate('testButton');activate('submitButton');check('directory repair earns full credit',b.view['grade']['score']==100)
    activate('hintButton');check('hint no penalty',b.view['hintCount']==1 and b.view['grade']['score']==100)
    capture('learn-review')
    old=b.view['attemptId'];activate('modeButton');key(Qt.Key_Escape)
    check('mode cancel restores focus',current()=='modeButton' and b.view['attemptId']==old)
    activate('modeButton');activate('confirmRestart')
    check('Challenge starts clean',b.view['mode']=='Challenge' and b.view['hintCount']==0 and b.session.engine.grade()['score']==30)
    activate('virtualEditorTab');replace('virtualFileEditor','DocumentRoot=/srv/www\nPort=8080\n')
    key(Qt.Key_Tab);check('Tab exits editor to Applied toggle',current()=='appliedVersionToggle')
    key(Qt.Key_Tab,Qt.ShiftModifier);check('Shift Tab returns editor',current()=='virtualFileEditor')
    key(Qt.Key_Tab,Qt.ShiftModifier);check('Shift Tab exits editor to tools',current()=='terminalHelpTab')
    check('editor makes separate draft',b.view['dirty'] and '/srv/site' in b.view['virtualFileApplied'])
    activate('submitButton');check('pending draft dialog visible',item('submitDraftDialog') is not None)
    key(Qt.Key_Escape);check('pending draft cancel retains edit',b.view['dirty'] and current()=='submitButton')
    activate('applyButton');check('apply saves text without starting service',not b.view['dirty'] and b.session.engine.grade()['score']==60)
    activate('consoleTab');command('systemctl restart lab-web');activate('testButton');activate('submitButton')
    check('configuration repair earns full credit',b.view['grade']['score']==100)
    capture('challenge-review');activate('continueWorking')
    activate('consoleTab');tab_to('commandInput')
    key(Qt.Key_F6);check('F6 terminal to mission',in_region('missionPanel'))
    key(Qt.Key_F6)
    focus=w.activeFocusItem()
    while focus and focus.objectName()!='domainWorkspace':focus=focus.parentItem()
    check('F6 mission to domain workspace',focus is not None)
    key(Qt.Key_F6);check('F6 workspace to diagnostics',in_region('diagnosticsDock'))
    for width,height in ((800,600),(1024,768),(1180,860),(1280,900)):
        w.resize(width,height);QTest.qWait(100);activate('virtualEditorTab')
        check(f'{width} actual window geometry',w.width()==width and w.height()==height)
        check(f'{width} mission accessible',item('missionPanel').height()>=80 and inside(item('missionPanel'),w.contentItem()))
        if not item('appliedVersionToggle').property('checked'):activate('appliedVersionToggle')
        for name in ('virtualFileEditor','virtualFileApplied'):
            widget=item(name);widget.forceActiveFocus();QTest.qWait(60)
            rect=widget.property('cursorRectangle');point=widget.mapToItem(item('virtualEditorViewport'),QPointF(rect.x(),rect.y()))
            check(f'{width} {name} cursor reachable',point.y()>=-1 and point.y()+rect.height()<=item('virtualEditorViewport').height()+1)
        check(f'{width} console input accessible',inside(item('commandInput'),item('diagnosticsDock')))
        check(f'{width} terminal output has a readable line',item('consoleViewport').property('availableHeight')>=20)
        check(f'{width} console does not overlap footer',item('commandInput').mapToItem(w.contentItem(),QPointF(0,0)).y()+item('commandInput').height()<=item('draftWarning').mapToItem(w.contentItem(),QPointF(0,0)).y())
        capture('editor-'+str(width))
        if width==800:
            widget=item('virtualFileEditor');original=widget.property('text');widget.forceActiveFocus()
            widget.setProperty('text','# virtual comment\n'*100+original);QTest.qWait(80)
            for direction in (Qt.Key_Home,Qt.Key_End):
                key(direction,Qt.ControlModifier)
                rect=widget.property('cursorRectangle');point=widget.mapToItem(item('virtualEditorViewport'),QPointF(rect.x(),rect.y()))
                check('long editor cursor visible '+str(direction),point.y()>=-1 and point.y()+rect.height()<=item('virtualEditorViewport').height()+1)
            accepted=b.view['virtualFileDraft'];widget.setProperty('text','x'*8193);QTest.qWait(50)
            check('oversize edit rejected visibly without replacing draft',b.view['virtualFileDraft']==accepted and widget.property('text')==accepted and '8 KiB' in b.view['message'])
            widget.setProperty('text',original);QTest.qWait(50)
            check('editor can return to applied text',not b.view['dirty'])
    w.resize(1280,900);activate('resetButton');key(Qt.Key_Escape)
    check('reset cancel restores focus',current()=='resetButton')
    activate('virtualEditorTab');replace('virtualFileEditor','unfinished draft')
    b.setCommandDraft('journalctl -n 3');b.flush()
    for lab in ('gateway-dns','subnet-boundary','service-firewall'):
        b.selectLab(lab,True);QTest.qWait(40);check(lab+' networking workspace intact',item('networkWorkspace') is not None)
    b.selectLab(scenario.key,True);QTest.qWait(40)
    check('switch retains draft',b.view['virtualFileDraft']=='unfinished draft')
    exported=root/'export.lab.json';check('scenario export',b.exportScenario(str(exported)))
    check('scenario exact bytes without attempt data',exported.read_bytes()==scenario.original_bytes)
    check('reimport idempotent',b.importPack(str(exported)) and len(b.labs)==4)
    personal=root/'history.attempt.json';check('separate personal export',b.exportAttempt(str(personal),old))
    b.fallbackTheme(True);capture('fallback')
    expected={'selected':scenario.key,'attempts':{name:lab.session.attempt for name,lab in b.labs.items()},'command':'journalctl -n 3'}
    b.flush();(root/'expected.json').write_text(json.dumps(expected));w.close();app.processEvents();lock.unlock()
    restart=subprocess.run([sys.executable,'-B','tests/linux_service_restart_probe.py',str(root)],capture_output=True,text=True,timeout=20)
    report['restart']=restart.stdout+restart.stderr;check('fresh process resumes four labs',restart.returncode==0)
    check('no QML errors',not any(any(word in msg for word in ('ReferenceError','TypeError','Binding loop','Cannot assign')) for msg in messages))
    report['result']='PASS'
except Exception as exc:
    report.update(result='FAIL',error=str(exc))
    report['state_on_failure']={'readOnly':b.view['readOnly'],'message':b.view['message'],'mode':b.view['mode']}
    try:report['editor_on_failure']={name:item('virtualFileEditor').property(name) for name in ('enabled','visible','activeFocusOnTab','focus')}
    except Exception:pass
    try:capture('failure')
    except Exception:pass
finally:
    w.close();app.processEvents();lock.unlock()
    (out/(args.label+'.json')).write_text(json.dumps(report,indent=2))
    print(json.dumps({k:report.get(k) for k in ('label','result','error','platform','dpr','restart')}|{'checks':len(report['checks']),'qml_messages':messages[-10:]},indent=2))
    tmp.cleanup()
sys.exit(0 if report['result']=='PASS' else 1)
