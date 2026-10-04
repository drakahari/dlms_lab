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

p=argparse.ArgumentParser();p.add_argument('--label',default='lpic-collections');p.add_argument('--offscreen',action='store_true')
p.add_argument('--expected-dpr',type=float,default=1);p.add_argument('--probe',type=Path);args=p.parse_args()
temp=None if args.probe else tempfile.TemporaryDirectory(prefix='lpic-collections-ui-')
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
        expected=json.loads((root/'expected.json').read_text())
        check('all attempts reopen exactly',{k:l.session.attempt for k,l in b.labs.items()}==expected['attempts'])
        check('shared visibility retained',b.visibility.entries==expected['visibility'])
        check('shared progress retained',b.view['collections'][0]['rows'][2]['status']==b.view['collections'][1]['rows'][1]['status'])
        check('pending command retained',b.view['commandDraft']=='help')
    else:
        check('four collections',len(b.view['collections'])==4)
        check('no portable profile writes before start',not b.repository.root.exists())
        for size in ((800,600),(1024,768),(1280,900)):
            w.resize(*size);QTest.qWait(120)
            # Collapse old collection to expose the new unit heading near the top.
            if not w.property('collapsedCollections').toVariant().get('fundamentals',False):activate('fundamentalsHeading')
            focus('lpic-foundationsHeading')
            check('unit heading reachable '+str(size),inside(item('lpic-foundationsHeading'),item('libraryPage')))
            capture('unit-heading-'+str(size[0]))
            for i in range(6):
                focus('start-lpic-foundations-'+str(i))
                check('card reachable '+str((size,i)),inside(item('lpic-foundationsCard-'+str(i)),item('libraryPage')))
                check('Start available '+str((size,i)),item('start-lpic-foundations-'+str(i)).isEnabled())
            capture('unit-bottom-'+str(size[0]))
            activate('lpic-foundationsHeading')
            check('section collapsed '+str(size),bool(w.property('collapsedCollections').toVariant().get('lpic-foundations')))
            capture('compact-collections-'+str(size[0]))
            activate('lpic-foundationsHeading')
        activate('start-lpic-foundations-1')
        command('chmod 600 notes.txt');command('cat notes.txt');b.submit()
        check('shared Learn complete',b.view['grade']['score']==100)
        shared=b.view['labKey'];attempt=b.view['attemptId']
        activate('libraryNav');activate('fundamentalsHeading');activate('start-fundamentals-2')
        check('same attempt from Fundamentals',b.view['attemptId']==attempt)
        activate('modeButton');activate('confirmRestart');command('pwd')
        activate('libraryNav');activate('start-lpic-foundations-1')
        check('same Challenge through LPIC',b.view['mode']=='Challenge')
        check('separate mode summaries match',b.view['collections'][0]['rows'][2]['status']==b.view['collections'][1]['rows'][1]['status']=='Learn: Completed · Challenge: In progress')
        activate('libraryNav');activate('actions-lpic-foundations-1')
        activate('actions-lpic-foundations-1Visibility')
        check('shared lab hidden once',b.view['hiddenCount']==1 and len(b.view['inactiveLabs'])==1)
        check('hidden completion remains truthful',all(c['completed']['Learn']==1 and c['inactiveCount']==1 for c in b.view['collections'][:2]))
        focus('showHiddenControl');QTest.keyClick(w,Qt.Key_Space);QTest.qWait(100);check('inactive discoverable',item('inactive-'+shared) is not None)
        activate('restore-primary-'+shared)
        activate('confirmLibraryResume')
        check('restore resumes correct mode',b.view['mode']=='Challenge' and b.visibility.state(shared)=='active')
        activate('libraryNav')
        if w.property('showHidden'):
            focus('showHiddenControl');QTest.keyClick(w,Qt.Key_Space);QTest.qWait(100)
        for i,identifier in ((3,'linux-private-note'),(4,'linux-search-only-directory')):
            activate('start-lpic-foundations-'+str(i))
            check('bundled pilot without import '+identifier,b.view['labId']==identifier)
            check('terminal remains available '+identifier,item('linuxConsole') is not None)
            for _ in range(4):
                if b.session.engine.grade()['complete']:break
                command(b.view['guide']['command'])
            b.submit();check('pilot completes '+identifier,b.view['grade']['score']==100)
            activate('libraryNav')
        # Collapse state survives controller refresh within this session.
        activate('lpic-foundationsHeading');b.refreshTheme();QTest.qWait(100)
        check('collapse retained after refresh',bool(w.property('collapsedCollections').toVariant().get('lpic-foundations')))
        activate('lpic-foundationsHeading');focus('lpic-foundationsHeading');capture('review')
        b.setLibraryState(shared,'hidden');b.selectLab(b.view['collections'][1]['rows'][4]['labKey'],True)
        b.setCommandDraft('help');b.flush()
        (root/'expected.json').write_text(json.dumps({'attempts':{k:l.session.attempt for k,l in b.labs.items()},'visibility':b.visibility.entries}))
        w.close();app.processEvents();lock.unlock()
        cmd=[sys.executable,'-B',__file__,'--probe',str(root),'--label',args.label+'-restart','--expected-dpr',str(args.expected_dpr)]
        if args.offscreen:cmd.append('--offscreen')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=25)
        report['restart']=result.stdout+result.stderr;check('fresh-process restart',result.returncode==0)
    check('no QML errors',not any(any(x in m for x in ('ReferenceError','TypeError','Binding loop','Cannot assign')) for m in messages))
    report['result']='PASS'
except Exception as exc:
    report.update(result='FAIL',error=str(exc))
finally:
    w.close();app.processEvents();lock.unlock();report['qml_messages']=messages
    (out/(args.label+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report.get(k) for k in ('result','error','platform','restart')}|{'checks':len(report['checks']),'qml_messages':messages[-10:]},indent=2))
    if temp:temp.cleanup()
sys.exit(0 if report['result']=='PASS' else 1)
