"""Qt-rendered Library collection; synthesized input is not physical acceptance."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QPointF, Qt, qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application

p=argparse.ArgumentParser();p.add_argument('--label',default='fundamentals');p.add_argument('--offscreen',action='store_true')
p.add_argument('--expected-dpr',type=float,default=1);p.add_argument('--probe',type=Path);args=p.parse_args()
temp=None if args.probe else tempfile.TemporaryDirectory(prefix='fundamentals-ui-')
root=args.probe or Path(temp.name);messages=[]
qInstallMessageHandler(lambda kind,context,message:messages.append(message))
app,engine,b,lock=build_application(root/'data',root/'config');w=engine.rootObjects()[0]
report={'checks':[],'platform':app.platformName(),'input':'QtTest synthesized keyboard; physical keyboard unverified'}
out=Path('evidence');out.mkdir(exist_ok=True)

def check(name,ok):
    report['checks'].append({'name':name,'passed':bool(ok)})
    if not ok:raise AssertionError(name)

def item(name):
    def visit(o):
        if o.objectName()==name and o.isVisible():return o
        for child in o.childItems():
            found=visit(child)
            if found is not None:return found
    found=visit(w.contentItem())
    if found is None:raise AssertionError('Missing '+name)
    return found

def inside(child,parent):
    point=child.mapToItem(parent,QPointF(0,0))
    return point.x()>=-1 and point.y()>=-1 and point.x()+child.width()<=parent.width()+1 and point.y()+child.height()<=parent.height()+1

def focus(name):item(name).forceActiveFocus(Qt.TabFocusReason);QTest.qWait(50)
def activate(name):focus(name);QTest.keyClick(w,Qt.Key_Return);QTest.qWait(80)
def command(value):
    focus('commandInput');QTest.keyClick(w,Qt.Key_A,Qt.ControlModifier)
    for c in value:QTest.keyClick(w,ord(c))
    QTest.keyClick(w,Qt.Key_Return);QTest.qWait(60)
def capture(name):
    pic=w.grabWindow();check('render '+name,not pic.isNull());pic.save(str(out/(args.label+'-'+name+'.png')))

try:
    check('window exposed',QTest.qWaitForWindowExposed(w,5000))
    if not args.offscreen:check('native Wayland',app.platformName()=='wayland')
    check('requested scale',abs(w.devicePixelRatio()-args.expected_dpr)<.01)
    if args.probe:
        expected=json.loads((root/'expected.json').read_bytes())
        check('exact attempts after process restart',{k:lab.session.attempt for k,lab in b.labs.items()}==expected['attempts'])
        check('same selected attempt',b.view['labKey']==expected['selected'])
        check('pending command retained',b.view['commandDraft']=='pwd')
        check('Learn completion stays separate',b.view['fundamentals'][4]['status']=='Learn: Completed · Challenge: In progress')
        b.navigate(0);QTest.qWait(60);activate('start-fundamentals-4')
        check('Continue resumes Challenge',b.view['mode']=='Challenge' and b.view['commandDraft']=='pwd')
    else:
        check('fresh profile has no portable installations',not b.repository.root.exists())
        for size in ((800,600),(1024,768),(1280,900)):
            w.resize(*size);QTest.qWait(120)
            focus('start-fundamentals-0');capture('library-top-'+str(size[0]))
            for i in range(6):
                focus('start-fundamentals-'+str(i))
                check('reachable card '+str((size,i)),inside(item('fundamentalsCard-'+str(i)),item('libraryPage')))
                check('visible Start '+str((size,i)),item('start-fundamentals-'+str(i)).property('text')=='Start')
            capture('library-bottom-'+str(size[0]))
        # Start the last lab first: there are no completion locks.
        activate('start-fundamentals-5');check('last lab starts without prerequisites',b.view['labId']=='linux-web-document-root')
        check('terminal unchanged',item('linuxConsole') is not None)
        b.edit('/etc/lab-web.conf','unapplied draft');activate('libraryNav');activate('start-fundamentals-0')
        check('existing draft confirmation shown',item('confirmSwitch') is not None)
        activate('confirmSwitch');check('confirmed Start works',b.view['labId']=='linux-file-navigation')
        check('service draft retained',next(l for l in b.labs.values() if l.pack['lab_id']=='linux-web-document-root').session.attempt['draft'])
        # Start every other curated entry, without a file picker.
        for i in (1,2,3,4):
            activate('libraryNav');activate('start-fundamentals-'+str(i));check('opens entry '+str(i),b.view['labKey']==b.view['fundamentals'][i]['labKey'])
        check('exactly six pinned packs plus original networking',len(b.labs)==9)
        check('no duplicate curated cards in other list',len(b.view['otherLabs'])==3)
        for c in ('chmod 500 Archive','cat Archive/handover.txt','cd Archive'):command(c)
        b.submit();check('fieldwork Learn complete',b.view['grade']['score']==100)
        activate('libraryNav');check('Learn status isolated',b.view['fundamentals'][4]['status']=='Learn: Completed · Challenge: Not started')
        focus('start-fundamentals-4');capture('completed');activate('start-fundamentals-4')
        activate('modeButton');activate('confirmRestart');check('Challenge fresh',b.view['mode']=='Challenge' and b.session.engine.grade()['score']==0)
        command('ls Archive');b.setCommandDraft('pwd');b.flush();activate('libraryNav')
        check('Challenge in progress separately',b.view['fundamentals'][4]['status']=='Learn: Completed · Challenge: In progress')
        check('Continue label',item('start-fundamentals-4').property('text')=='Continue')
        activate('start-fundamentals-4');check('Continue keeps draft command',b.view['commandDraft']=='pwd')
        b.flush();(root/'expected.json').write_text(json.dumps({'selected':b.view['labKey'],'attempts':{k:l.session.attempt for k,l in b.labs.items()}}))
        w.close();app.processEvents();lock.unlock()
        command_line=[sys.executable,'-B',__file__,'--probe',str(root),'--label',args.label+'-restart','--expected-dpr',str(args.expected_dpr)]
        if args.offscreen:command_line.append('--offscreen')
        result=subprocess.run(command_line,capture_output=True,text=True,timeout=20)
        report['restart']=result.stdout+result.stderr;check('fresh-process Continue',result.returncode==0)
    check('no QML errors',not any(any(x in m for x in ('ReferenceError','TypeError','Binding loop','Cannot assign')) for m in messages))
    report['result']='PASS'
except Exception as exc:
    report.update(result='FAIL',error=str(exc))
finally:
    w.close();app.processEvents();lock.unlock();report['qml_messages']=messages
    (out/(args.label+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report.get(k) for k in ('result','error','platform','restart')}|{'checks':len(report['checks'])},indent=2))
    if temp:temp.cleanup()
sys.exit(0 if report['result']=='PASS' else 1)
