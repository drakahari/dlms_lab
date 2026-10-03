"""Isolated Qt navigation workflow. Synthesized events are not physical input."""
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

p=argparse.ArgumentParser()
p.add_argument('--label',default='linux-navigation')
p.add_argument('--expected-dpr',type=float,default=1)
p.add_argument('--offscreen',action='store_true')
p.add_argument('--probe',type=Path)
args=p.parse_args()
tmp=None if args.probe else tempfile.TemporaryDirectory(prefix='linux-navigation-ui-')
root=args.probe or Path(tmp.name)
messages=[];qInstallMessageHandler(lambda typ,ctx,msg:messages.append(msg))
app,engine,b,lock=build_application(root/'data',root/'config');w=engine.rootObjects()[0]
report={'platform':app.platformName(),'input':'QtTest synthesized events; physical keyboard unverified',
        'native_file_choosers':'unverified; controller import/export APIs used','checks':[],'qml_messages':messages}
out=Path('evidence');out.mkdir(exist_ok=True)

def check(name,condition):
    report['checks'].append({'name':name,'passed':bool(condition)})
    if not condition:raise AssertionError(name)

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
    widget=item(name)
    point=widget.mapToItem(w.contentItem(),QPointF(widget.width()/2,widget.height()/2)).toPoint()
    QTest.mouseClick(w,Qt.LeftButton,Qt.NoModifier,point);QTest.qWait(40)

def key(code,mod=Qt.NoModifier):QTest.keyClick(w,code,mod);QTest.qWait(5)
def command(text,run=False):
    click('commandInput');key(Qt.Key_A,Qt.ControlModifier)
    for c in text:key(ord(c))
    if run:click('runCommand')
    else:key(Qt.Key_Return)

def inside(child,parent):
    pt=child.mapToItem(parent,QPointF(0,0))
    return pt.x()>=-1 and pt.y()>=-1 and pt.x()+child.width()<=parent.width()+1 and pt.y()+child.height()<=parent.height()+1

def capture(name):
    QTest.qWait(100);pic=w.grabWindow();check('rendered '+name,not pic.isNull())
    pic.save(str(out/(args.label+'-'+name+'.png')))

try:
    check('window exposed',QTest.qWaitForWindowExposed(w,5000))
    if not args.offscreen:check('native Wayland',app.platformName()=='wayland')
    report['dpr']=w.devicePixelRatio();check('scale',abs(w.devicePixelRatio()-args.expected_dpr)<.01)
    w.resize(1280,900);QTest.qWait(100)
    if args.probe:
        expected=json.loads((root/'expected.json').read_text())
        check('six lab records resume exactly',{k:v.session.attempt for k,v in b.labs.items()}==expected['attempts'])
        check('pinned navigation selected',b.view['labKey']==expected['selected'])
        check('command draft resumed',b.view['commandDraft']=='cat welcome.txt')
        check('guide resumes step four',b.view['guide']['index']==3)
        check('retained layout resumed',b.view['workspaceLayout']==expected['layout'])
        b.navigate(1);QTest.qWait(100)
        check('no service editor',item('openVirtualEditor',False) is None)
        command('cat welcome.txt');command('cd /home/learner/Projects');b.submit()
        check('resumed actions earn 100',b.view['grade']['score']==100)
    else:
        packs={name:load_portable(Path('examples',name+'.lab.json').read_bytes()) for name in
               ('linux-file-navigation','linux-web-document-root','linux-service-basics')}
        for name in packs:check('import '+name,b.importPack(str(Path('examples',name+'.lab.json').resolve())))
        scenario=packs['linux-file-navigation'];b.selectLab(scenario.key,True);QTest.qWait(100)
        check('terminal visible by default',item('linuxConsole') is not None)
        check('fresh cue','Type help and press Enter.'==item('consoleOutput').property('text'))
        check('no tools or artificial divider',item('linuxTerminalDivider',False) is None)
        check('no unrelated editor or Apply',item('openVirtualEditor',False) is None and item('applyButton',False) is None)
        check('first step only',item('guideCommand').property('text')=='pwd' and b.view['guide']['index']==0)
        check('accurate learner prompt',item('terminalPrompt').property('text')=='learner@lab:/home/learner$')
        click('commandInput');check('input accepts direct click',w.activeFocusItem()==item('commandInput'))
        capture('initial')
        w.resize(800,600);QTest.qWait(150)
        check('compact Learn guide remains readable',item('guideExplanation').width()>=250 and item('guideExpected').property('font').pixelSize()>=13)
        check('compact Learn leaves command input usable',inside(item('commandInput'),item('linuxConsole')) and item('commandInput').width()>=150)
        item('missionPanel').forceActiveFocus();key(Qt.Key_PageDown)
        check('compact mission scroll exposes complete current step',all(inside(item(name),item('missionPanel')) for name in ('guideCommand','guideExplanation','guideExpected')))
        capture('initial-compact');w.resize(1280,900);QTest.qWait(100)
        command('pwd');check('Enter progresses step',b.view['guide']['index']==1)
        command('ls',True);check('Run progresses and returns focus',b.view['guide']['index']==2 and w.activeFocusItem()==item('commandInput'))
        command('cd Documents');check('relative navigation prompt',item('terminalPrompt').property('text').endswith('/Documents$'))
        command('cat welcome.txt');check('read file progresses',b.view['guide']['index']==4)
        command('cd /home/learner/Projects');check('all steps verified',b.view['guide']['verified'])
        check('completion text matches navigation','Navigation objectives met' in item('guideVerified').property('text'))
        b.test();check('diagnostics mention activity','activity' in b.view['message'])
        b.submit();check('Learn full credit',b.view['grade']['score']==100)
        click('missionDetailsButton');check('nonmodal reference opens',item('labDetailsView') is not None)
        command('pwd');check('commands leave details open',item('labDetailsView') is not None)
        click('openTerminalHelp');check('reference and command reference coexist',item('labDetailsView') is not None and item('terminalHelpTab') is not None)
        handle=item('linuxTerminalDivider');point=handle.mapToItem(w.contentItem(),QPointF(handle.width()/2,handle.height()/2)).toPoint()
        before=item('diagnosticsDock').height()
        QTest.mouseMove(w,point);QTest.qWait(50);QTest.mousePress(w,Qt.LeftButton,Qt.NoModifier,point)
        for n in range(1,6):QTest.mouseMove(w,point+QPoint(0,-6*n));QTest.qWait(30)
        QTest.mouseRelease(w,Qt.LeftButton,Qt.NoModifier,point+QPoint(0,-30));QTest.qWait(100)
        chosen=item('diagnosticsDock').height();check('divider drag changes height',abs(chosen-before)>10)
        for _ in range(3):command('ls');check('output preserves chosen size',abs(item('diagnosticsDock').height()-chosen)<1)
        saved=b.view['workspaceLayout']
        for size in ((800,600),(1024,768),(1180,860),(1280,900)):
            w.resize(*size);QTest.qWait(150)
            check('console/input bounds '+str(size),inside(item('commandInput'),item('linuxConsole')) and inside(item('linuxConsole'),w.contentItem()))
            check('readable input '+str(size),item('commandInput').width()>=150 and item('commandInput').property('font').pixelSize()==14)
            check('output line available '+str(size),item('consoleViewport').property('availableHeight')>=20)
            check('details own usable scroll '+str(size),item('labDetailsScroll').property('availableHeight')>=50)
            check('sidebar width '+str(size),item('missionPanel').width()>=320)
            check('prompt text retains full accessible path '+str(size),item('terminalPrompt').property('text')=='learner@lab:/home/learner/Projects$')
            command('pwd');check('entry with reference and tool '+str(size),item('labDetailsView') is not None)
            check('sizing preference survives resize '+str(size),b.view['workspaceLayout']==saved)
            capture('reference-'+str(size[0]))
        click('closeLinuxTools');check('close tool retains instructions and input focus',item('labDetailsView') is not None and w.activeFocusItem()==item('commandInput'))
        click('closeLabDetails');check('explicit close removes reference',item('labDetailsView',False) is None)
        b.restart('Challenge');QTest.qWait(50)
        check('Challenge hides guidance/hints',item('beginnerGuide',False) is None and item('hintButton',False) is None)
        check('Challenge retains goal','Documents' in item('missionGoal').property('text'))
        click('missionDetailsButton');check('Challenge rules accessible',item('labDetailsView') is not None and 'Four action objectives' in b.view['constraints'][0])
        for text in ('cat Documents/welcome.txt','cd /home/learner/Documents','ls ..','cd ..','pwd','cd ./Projects'):command(text)
        b.submit();check('Challenge alternatives full credit',b.view['grade']['score']==100);capture('challenge')
        b.restart('Learn');QTest.qWait(50);check('reset clears evidence',b.session.engine.grade()['score']==0 and b.view['guide']['index']==0)
        for text in ('pwd','ls','cd Documents'):command(text)
        b.setCommandDraft('cat welcome.txt');b.flush()
        for key in ('gateway-dns','subnet-boundary','service-firewall'):
            b.selectLab(key,True);QTest.qWait(40);check(key+' networking workspace intact',item('networkWorkspace') is not None)
        for name in ('linux-web-document-root','linux-service-basics'):
            b.selectLab(packs[name].key,True);QTest.qWait(40)
            check(name+' service remains available','systemctl' in b.view['terminalHelp'])
        b.selectLab(scenario.key,True);QTest.qWait(50)
        check('lab switch retains navigation',b.view['guide']['index']==3 and b.view['commandDraft']=='cat welcome.txt')
        check('previous attempts preserved',b.view['historyCount']==2)
        exported=root/'navigation.lab.json';check('scenario export',b.exportScenario(str(exported)))
        check('export exact bytes',exported.read_bytes()==scenario.original_bytes)
        check('reimport duplicate safe',b.importPack(str(exported)) and len(b.labs)==6)
        check('separate history export',b.exportAttempt(str(root/'personal.attempt.json'),b.view['attemptId']))
        b.flush();(root/'expected.json').write_text(json.dumps({'selected':scenario.key,
            'attempts':{k:v.session.attempt for k,v in b.labs.items()},'layout':b.view['workspaceLayout']}))
        w.close();app.processEvents();lock.unlock()
        cmd=[sys.executable,'-B',__file__,'--probe',str(root),'--label',args.label+'-restart','--expected-dpr',str(args.expected_dpr)]
        if args.offscreen:cmd.append('--offscreen')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
        report['restart']=result.stdout+result.stderr;check('fresh process resumes and completes',result.returncode==0)
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
    if tmp:tmp.cleanup()
sys.exit(0 if report['result']=='PASS' else 1)
