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

p=argparse.ArgumentParser();p.add_argument('--label',default='organize-unit');p.add_argument('--offscreen',action='store_true')
p.add_argument('--expected-dpr',type=float,default=1);p.add_argument('--probe',type=Path);args=p.parse_args()
temp=None if args.probe else tempfile.TemporaryDirectory(prefix='organize-unit-ui-')
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
    unit=b.view['collections'][2]
    check('six new entries',unit['id']=='lpic-file-management' and len(unit['rows'])==6)
    if args.probe:
        expected=json.loads((root/'expected.json').read_text())
        check('exact attempts reopen',{k:l.session.attempt for k,l in b.labs.items()}==expected['attempts'])
        check('pending input retained',b.view['commandDraft']=='find . -type f')
        check('both mode counts retained',b.view['collections'][2]['completed']=={'Learn':6,'Challenge':6})
        check('no editor or service controls',not b.view['canEditVirtualFile'] and b.view['workspaceTools']==['terminal'])
    else:
        activate('fundamentalsHeading');activate('lpic-foundationsHeading')
        for width,height in ((800,600),(1024,768),(1280,900)):
            w.resize(width,height);QTest.qWait(120);focus('lpic-file-managementHeading')
            check('heading fits '+str(width),inside(item('lpic-file-managementHeading'),item('libraryPage')))
            capture('collection-'+str(width))
            for i in range(6):
                focus('start-lpic-file-management-'+str(i))
                check('card fits '+str((width,i)),inside(item('lpic-file-managementCard-'+str(i)),item('libraryPage')))
                activate('start-lpic-file-management-'+str(i))
                check('terminal/input visible '+str((width,i)),inside(item('commandInput'),item('linuxConsole')))
                check('input available '+str((width,i)),item('commandInput').isEnabled())
                command('help');check('recognized help '+str((width,i)),'Simulated Linux' in b.view['console'])
                activate('missionDetailsButton');check('nonmodal details available '+str((width,i)),item('labDetailsView') is not None)
                command('pwd');check('details survives command '+str((width,i)),item('labDetailsView') is not None)
                capture('lab-'+str(i)+'-'+str(width))
                activate('missionDetailsButton');check('input available after close '+str((width,i)),item('commandInput').isEnabled())
                activate('libraryNav')
            activate('lpic-file-managementHeading');check('collection collapsed '+str(width),w.property('collapsedCollections').toVariant()['lpic-file-management'])
            activate('lpic-file-managementHeading')
        from learning_lab.linux_navigation.file_management import guide as management_guide
        from learning_lab.linux_navigation.engine import guide as navigation_guide
        for i in range(6):
            activate('start-lpic-file-management-'+str(i))
            g=navigation_guide if i==0 else management_guide
            for mode in ('Learn','Challenge'):
                if mode=='Challenge':activate('modeButton');activate('confirmRestart')
                check('correct mode '+str((i,mode)),b.view['mode']==mode)
                if mode=='Challenge':check('guided solution hidden '+str(i),b.view['guide']=={})
                for _ in range(64):
                    if b.session.engine.grade()['complete']:break
                    command(g(b.pack,b.session.attempt['applied'])['command'])
                b.submit();check('UI commands complete '+str((i,mode)),b.view['grade']['score']==100)
                if i==5:capture('assessment-'+mode)
            activate('libraryNav')
        check('separate mode completion counts',b.view['collections'][2]['completed']=={'Learn':6,'Challenge':6})
        focus('lpic-file-managementHeading');capture('completed-collection')
        activate('start-lpic-file-management-5');b.setCommandDraft('find . -type f');b.flush()
        (root/'expected.json').write_text(json.dumps({'attempts':{k:l.session.attempt for k,l in b.labs.items()}}))
        w.close();app.processEvents();lock.unlock()
        cmd=[sys.executable,'-B',__file__,'--probe',str(root),'--label',args.label+'-restart','--expected-dpr',str(args.expected_dpr)]
        if args.offscreen:cmd.append('--offscreen')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
        report['restart']=result.stdout+result.stderr;check('fresh process reopen',result.returncode==0)
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
