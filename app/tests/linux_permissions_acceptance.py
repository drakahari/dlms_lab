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
p.add_argument('--label',default='linux-permissions')
p.add_argument('--expected-dpr',type=float,default=1)
p.add_argument('--offscreen',action='store_true')
p.add_argument('--probe',type=Path)
args=p.parse_args()
tmp=None if args.probe else tempfile.TemporaryDirectory(prefix='linux-permissions-ui-')
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
        check('seven attempts resume exactly',{k:v.session.attempt for k,v in b.labs.items()}==expected['attempts'])
        check('selected pinned permissions lab',b.view['labKey']==expected['selected'])
        check('permission repair persisted',b.session.engine.grade()['score']==70)
        check('pending command resumed',b.view['commandDraft']=='cat notes.txt')
        check('guide resumes verification',b.view['guide']['index']==3)
        check('layout retained',b.view['workspaceLayout']==expected['layout'])
        b.navigate(1);QTest.qWait(100);command('cat notes.txt');b.submit()
        check('reopened verification earns 100',b.view['grade']['score']==100)
    else:
        names=('linux-file-permissions','linux-file-navigation','linux-web-document-root','linux-service-basics')
        packs={n:load_portable(Path('examples',n+'.lab.json').read_bytes()) for n in names}
        for n in names:check('import '+n,b.importPack(str(Path('examples',n+'.lab.json').resolve())))
        scenario=packs['linux-file-permissions'];b.selectLab(scenario.key,True);QTest.qWait(100)
        check('terminal visible by default',item('linuxConsole') is not None)
        check('no service editor or Apply',item('openVirtualEditor',False) is None and item('applyButton',False) is None)
        check('inspection guide visible',item('guideCommand').property('text')=='ls -l notes.txt')
        for size in ((800,600),(1024,768),(1180,860),(1280,900)):
            w.resize(*size);QTest.qWait(100)
            check('input accessible '+str(size),inside(item('commandInput'),item('linuxConsole')) and item('commandInput').width()>=150)
            check('guide readable width '+str(size),item('guideExplanation').width()>=240 and item('guideExplanation').property('font').pixelSize()>=13)
            # Each part of the long introductory explanation is scroll-reachable.
            panel=item('missionPanel');panel.forceActiveFocus()
            for name in ('guideCommand','guideExplanation','guideExpected'):
                for _ in range(12):
                    if inside(item(name),panel):break
                    key(Qt.Key_Down)
                check('guide scroll reach '+name+' '+str(size),inside(item(name),panel))
            capture('learn-'+str(size[0]))
            panel.property('contentItem').setProperty('contentY',0)
        command('ls -l notes.txt');check('inspection advances',b.view['guide']['index']==1)
        command('cat notes.txt');check('clear denial and next explanation','Permission denied (read)' in b.view['console'] and b.view['guide']['index']==2)
        command('chmod u+r notes.txt');check('symbolic repair and no early credit',b.session.engine.grade()['score']==70 and b.view['guide']['index']==3)
        command('cat notes.txt',True);check('Run verification and input focus',b.session.engine.grade()['score']==100 and w.activeFocusItem()==item('commandInput'))
        check('completion copy matches lesson','Private read/write access verified' in item('guideVerified').property('text'))
        b.submit();capture('learn-complete')
        click('missionDetailsButton');command('ls -l')
        check('nonmodal instructions remain open',item('labDetailsView') is not None)
        click('openTerminalHelp');check('reference coexists with instructions',item('terminalHelpTab') is not None and item('labDetailsView') is not None)
        handle=item('linuxTerminalDivider');pt=handle.mapToItem(w.contentItem(),QPointF(handle.width()/2,handle.height()/2)).toPoint()
        before=item('diagnosticsDock').height()
        QTest.mouseMove(w,pt);QTest.qWait(50);QTest.mousePress(w,Qt.LeftButton,Qt.NoModifier,pt)
        for n in range(1,6):QTest.mouseMove(w,pt+QPoint(0,-n*6));QTest.qWait(25)
        QTest.mouseRelease(w,Qt.LeftButton,Qt.NoModifier,pt+QPoint(0,-30));QTest.qWait(100)
        chosen=item('diagnosticsDock').height();check('divider moved',abs(chosen-before)>10)
        for _ in range(3):command('ls -l');check('output preserves split',abs(item('diagnosticsDock').height()-chosen)<1)
        click('closeLinuxTools');check('tool close returns focus',w.activeFocusItem()==item('commandInput'))
        click('closeLabDetails');check('explicit details close',item('labDetailsView',False) is None)
        b.restart('Challenge');QTest.qWait(80)
        check('Challenge hides hints and steps',item('beginnerGuide',False) is None and item('hintButton',False) is None)
        check('goal contains no command solution','chmod' not in item('missionGoal').property('text'))
        command('chmod 777 notes.txt');command('cat notes.txt');b.submit()
        check('777 fails least privilege',b.view['grade']['score']==30)
        command('chmod 600 notes.txt');check('mode change requires new read',b.session.engine.grade()['score']==70)
        command('cat notes.txt');b.submit();check('numeric Challenge repair',b.view['grade']['score']==100)
        capture('challenge-complete')
        b.restart('Learn');QTest.qWait(50);check('reset restores fault and empty evidence',b.session.engine.grade()['score']==0 and b.view['console']=='' and b.view['guide']['index']==0)
        command('chmod 600 notes.txt');b.setCommandDraft('cat notes.txt');b.flush()
        for key in list(b.labs):b.selectLab(key,True)
        b.selectLab(scenario.key,True);QTest.qWait(50)
        check('switch retains pending verification',b.view['commandDraft']=='cat notes.txt' and b.view['guide']['index']==3)
        check('history retains both prior attempts',b.view['historyCount']==2)
        exported=root/'permissions.lab.json';check('scenario export',b.exportScenario(str(exported)))
        check('exact scenario bytes',exported.read_bytes()==scenario.original_bytes)
        check('duplicate import safe',b.importPack(str(exported)) and len(b.labs)==7)
        check('separate personal export',b.exportAttempt(str(root/'personal.attempt.json'),b.view['attemptId']))
        b.flush();(root/'expected.json').write_text(json.dumps({'selected':scenario.key,'attempts':{k:v.session.attempt for k,v in b.labs.items()},'layout':b.view['workspaceLayout']}))
        w.close();app.processEvents();lock.unlock()
        cmd=[sys.executable,'-B',__file__,'--probe',str(root),'--label',args.label+'-restart','--expected-dpr',str(args.expected_dpr)]
        if args.offscreen:cmd.append('--offscreen')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
        report['restart']=result.stdout+result.stderr;check('fresh process resumes then verifies',result.returncode==0)
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
