"""Isolated Qt private-note workflow. Synthesized events are not physical input."""
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
p.add_argument('--label',default='private-note')
p.add_argument('--expected-dpr',type=float,default=1)
p.add_argument('--offscreen',action='store_true')
p.add_argument('--probe',type=Path)
args=p.parse_args()
tmp=None if args.probe else tempfile.TemporaryDirectory(prefix='private-note-ui-')
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
    check('window exposed', QTest.qWaitForWindowExposed(w,5000))
    if not args.offscreen: check('native Wayland', app.platformName()=='wayland')
    report['dpr']=w.devicePixelRatio()
    check('scale', abs(w.devicePixelRatio()-args.expected_dpr)<.01)
    w.resize(1280,900); QTest.qWait(100)
    pack=Path(__file__).resolve().parents[1]/'examples/linux-private-note.lab.json'
    scenario=load_portable(pack.read_bytes())
    if args.probe:
        expected=json.loads((root/'expected.json').read_text())
        check('same-profile exact attempt restart', b.session.attempt==expected['attempt'])
        check('same pinned content', b.portables[scenario.key].pin==scenario.pin)
        check('pending command retained', b.view['commandDraft']=='cat notes.txt')
        check('history retained', b.view['historyCount']==2)
        b.navigate(1); QTest.qWait(100); command('cat notes.txt'); b.submit()
        check('reopened verification completes', b.view['grade']['score']==100)
    else:
        check('explicit import', b.importPack(str(pack)))
        b.selectLab(scenario.key,True); QTest.qWait(100)
        check('terminal primary', item('linuxConsole') is not None)
        check('no unrelated editor', item('openVirtualEditor',False) is None)
        check('title', b.view['metadata']['title']=='Make an overexposed note private')
        for size in ((800,600),(1024,768),(1280,900)):
            w.resize(*size); QTest.qWait(100)
            check('input inside console '+str(size),inside(item('commandInput'),item('linuxConsole')) and item('commandInput').width()>=150)
            check('heading within window '+str(size),inside(item('labHeading'),w.contentItem()))
            panel=item('missionPanel');panel.forceActiveFocus()
            for name in ('guideCommand','guideExplanation','guideExpected'):
                for _ in range(24):
                    if inside(item(name),panel):break
                    key(Qt.Key_Down)
                check('guide reachable '+name+' '+str(size),inside(item(name),panel))
            check('readable font '+str(size),item('guideExplanation').property('font').pixelSize()>=13)
            capture('learn-'+str(size[0]));panel.property('contentItem').setProperty('contentY',0)
        command('cat notes.txt'); b.submit()
        check('readable does not mean private',b.view['grade']['score']==30)
        command('ls -l .');check('Learn repair step',b.view['guide']['index']==1)
        command('chmod 600 notes.txt');check('verification required',b.session.engine.grade()['score']==70)
        command('cat notes.txt',True);b.submit()
        check('Learn completed',b.view['grade']['score']==100)
        check('Run returns input focus',w.activeFocusItem()==item('commandInput'))
        click('missionDetailsButton');command('pwd')
        check('details stay open while typing',item('labDetailsView') is not None)
        click('openTerminalHelp')
        for size in ((800,600),(1280,900)):
            w.resize(*size);QTest.qWait(100);command('pwd')
            check('reference and details coexist '+str(size),item('terminalHelpTab') is not None and item('labDetailsView') is not None)
            check('input with panels '+str(size),inside(item('commandInput'),item('linuxConsole')))
            capture('details-'+str(size[0]))
        click('closeLinuxTools');check('tool close restores focus',w.activeFocusItem()==item('commandInput'))
        click('closeLabDetails');b.restart('Challenge');QTest.qWait(100)
        check('Challenge hides solutions',item('beginnerGuide',False) is None and item('hintButton',False) is None)
        command('chmod 644 notes.txt');command('cat notes.txt');b.submit()
        check('644 too broad',b.view['grade']['score']==30)
        command('chmod 600 ./notes.txt');command('cat /home/learner/notes.txt');b.submit()
        check('Challenge completed',b.view['grade']['score']==100);capture('challenge-complete')
        b.restart('Learn');check('reset restores 777',b.session.attempt['applied']['filesystem']['/home/learner/notes.txt']['mode']=='0777')
        command('chmod 600 notes.txt');b.setCommandDraft('cat notes.txt');b.flush()
        (root/'expected.json').write_text(json.dumps({'attempt':b.session.attempt}))
        w.close();app.processEvents();lock.unlock()
        cmd=[sys.executable,'-B',__file__,'--probe',str(root),'--label',args.label+'-restart','--expected-dpr',str(args.expected_dpr)]
        if args.offscreen:cmd.append('--offscreen')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=25)
        report['restart']=result.stdout+result.stderr
        check('fresh-process reopen',result.returncode==0)
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
