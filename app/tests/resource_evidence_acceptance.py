"""Qt-rendered Library collection; synthesized input is not physical acceptance."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
if '--installed' not in sys.argv:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QPointF, Qt, qInstallMessageHandler
from PySide6.QtQml import QQmlExpression
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application

p=argparse.ArgumentParser();p.add_argument('--label',default='text-unit');p.add_argument('--offscreen',action='store_true')
p.add_argument('--installed',action='store_true');p.add_argument('--evidence-root',type=Path)
p.add_argument('--monitor',default='eDP-1')
p.add_argument('--expected-dpr',type=float,default=1);p.add_argument('--probe',type=Path);args=p.parse_args()
temp=None if args.probe else tempfile.TemporaryDirectory(prefix='text-unit-ui-')
root=args.probe or Path(temp.name);messages=[]
qInstallMessageHandler(lambda kind,context,message:messages.append(message))
app,engine,b,lock=build_application(root/'data',root/'config',root/'vm');w=engine.rootObjects()[0]
report={'checks':[],'platform':app.platformName(),'input':'QtTest synthesized keyboard; physical keyboard unverified'}
out=args.evidence_root or Path('evidence');out.mkdir(parents=True,exist_ok=True)

def check(name,ok):
    report['checks'].append({'name':name,'passed':bool(ok)})
    if not ok:
        w.grabWindow().save(str(out/(args.label+'-failure.png')))
        x=item('lpic-resource-evidenceHeading');y=item('libraryPage');point=x.mapToItem(y,QPointF(0,0));report['failure_geometry']={'heading':[point.x(),point.y(),x.width(),x.height()],'viewport':[y.width(),y.height()]}
        raise AssertionError(name)

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

def focus(name):
    w.contentItem().forceActiveFocus(Qt.OtherFocusReason);QTest.qWait(100)
    item(name).forceActiveFocus(Qt.TabFocusReason);QTest.qWait(70)
def activate(name):focus(name);QTest.keyClick(w,Qt.Key_Return);QTest.qWait(80)
def command(value):
    focus('commandInput');QTest.keyClick(w,Qt.Key_A,Qt.ControlModifier)
    for c in value:QTest.keyClick(w,ord(c))
    QTest.keyClick(w,Qt.Key_Return);QTest.qWait(60)
native_prepared=False
def resize(width,height):
    global native_prepared
    if args.offscreen:
        w.resize(width,height)
    else:
        import os
        pid=os.getpid()
        monitors=json.loads(subprocess.check_output(['hyprctl','-j','monitors']))
        scale=next(m['scale'] for m in monitors if m['name']==args.monitor)
        expressions=[]
        if not native_prepared:
            expressions=[f'hl.dsp.window.float({{action="set",window="pid:{pid}"}})',f'hl.dsp.window.move({{monitor="{args.monitor}",follow=true,window="pid:{pid}"}})']
            native_prepared=True
        expressions.append(f'hl.dsp.window.resize({{x={round(width*args.expected_dpr/scale)},y={round(height*args.expected_dpr/scale)},relative=false,window="pid:{pid}"}})')
        for expr in expressions:
            subprocess.run(['hyprctl','dispatch',expr],check=True,capture_output=True)
    end=__import__('time').monotonic()+8
    while (w.width(),w.height())!=(width,height):
        assert __import__('time').monotonic()<end,('actual size',w.width(),w.height(),width,height)
        QTest.qWait(20)
    QTest.qWait(100)
    check('actual size '+str((width,height)),(w.width(),w.height())==(width,height))

def reveal(name):
    child=item(name);viewport=item('libraryPage')
    if inside(child,viewport):return
    def ev(obj,expression):
        expr=QQmlExpression(engine.rootContext(),obj,expression);value,undefined=expr.evaluate()
        assert not expr.hasError() and not undefined,expr.error().toString()
        return value
    bar=next(c for c in viewport.childItems() if 'ScrollBar' in c.metaObject().className() and c.height()>c.width())
    thumb=ev(bar,'contentItem');start=thumb.mapToScene(thumb.boundingRect().center())
    point=child.mapToItem(viewport,QPointF(0,0))
    extent=ev(viewport,'contentHeight')-viewport.height()
    target=max(0,min(extent,ev(viewport,'contentItem.contentY')+point.y()-20))
    fraction=target/extent if extent else 0
    end=bar.mapToScene(QPointF(bar.width()/2,2+thumb.height()/2+fraction*(bar.height()-4-thumb.height())))
    QTest.mousePress(w,Qt.LeftButton,Qt.NoModifier,start.toPoint())
    QTest.mouseMove(w,end.toPoint());QTest.mouseRelease(w,Qt.LeftButton,Qt.NoModifier,end.toPoint());QTest.qWait(150)
    check('mouse scrollbar exposes '+name,inside(child,viewport))

def capture(name):
    pic=w.grabWindow();check('render '+name,not pic.isNull());pic.save(str(out/(args.label+'-'+name+'.png')))

try:
    check('window exposed',QTest.qWaitForWindowExposed(w,5000))
    if not args.offscreen:check('native Wayland',app.platformName()=='wayland')
    check('requested scale',abs(w.devicePixelRatio()-args.expected_dpr)<.01)
    unit=b.view['collections'][4]
    check('four resource entries',unit['id']=='lpic-resource-evidence' and len(unit['rows'])==4)
    if args.probe:
        expected=json.loads((root/'expected.json').read_text())
        check('exact attempts reopen',{k:l.session.attempt for k,l in b.labs.items()}==expected['attempts'])
        check('pending input retained',b.view['commandDraft']=='cat HELP.txt')
        check('both mode counts retained',b.view['collections'][4]['completed']=={'Learn':4,'Challenge':4})
        check('no editor or service controls',not b.view['canEditVirtualFile'] and b.view['workspaceTools']==['terminal'])
    else:
        activate('fundamentalsHeading');activate('lpic-foundationsHeading');activate('lpic-file-managementHeading')
        activate('lpic-text-streamsHeading')
        for width,height in ((800,600),(1280,900)):
            resize(width,height);focus('lpic-resource-evidenceHeading');reveal('lpic-resource-evidenceHeading')
            check('heading fits '+str(width),inside(item('lpic-resource-evidenceHeading'),item('libraryPage')))
            capture('collection-'+str(width))
            for i in range(4):
                focus('start-lpic-resource-evidence-'+str(i))
                check('card fits '+str((width,i)),inside(item('lpic-resource-evidenceCard-'+str(i)),item('libraryPage')))
                activate('start-lpic-resource-evidence-'+str(i))
                check('terminal/input visible '+str((width,i)),inside(item('commandInput'),item('linuxConsole')))
                check('input available '+str((width,i)),item('commandInput').isEnabled())
                command('cat HELP.txt');check('model reference visible '+str((width,i)),'Model interpretation' in b.view['console'])
                command('help');check('recognized help '+str((width,i)),'Simulated Linux' in b.view['console'])
                activate('missionDetailsButton');check('nonmodal details available '+str((width,i)),item('labDetailsView') is not None)
                command('pwd');check('details survives command '+str((width,i)),item('labDetailsView') is not None)
                capture('lab-'+str(i)+'-'+str(width))
                activate('missionDetailsButton');check('input available after close '+str((width,i)),item('commandInput').isEnabled())
                activate('libraryNav')
            activate('lpic-resource-evidenceHeading');check('collection collapsed '+str(width),w.property('collapsedCollections').toVariant()['lpic-resource-evidence'])
            activate('lpic-resource-evidenceHeading')
        from learning_lab.linux_text.engine import guide as text_guide

        for i in range(4):
            activate('start-lpic-resource-evidence-'+str(i))
            g=text_guide
            for mode in ('Learn','Challenge'):
                if mode=='Challenge':activate('modeButton');activate('confirmRestart')
                check('correct mode '+str((i,mode)),b.view['mode']==mode)
                if mode=='Challenge':check('guided solution hidden '+str(i),b.view['guide']=={})
                for _ in range(64):
                    if b.session.engine.grade()['complete']:break
                    command(g(b.pack,b.session.attempt['applied'])['command'])
                b.submit();check('UI commands complete '+str((i,mode)),b.view['grade']['score']==100)
                if i==3:capture('assessment-'+mode)
            activate('libraryNav')
        check('separate mode completion counts',b.view['collections'][4]['completed']=={'Learn':4,'Challenge':4})
        focus('lpic-resource-evidenceHeading');capture('completed-collection')
        activate('start-lpic-resource-evidence-3');b.setCommandDraft('cat HELP.txt');b.flush()
        (root/'expected.json').write_text(json.dumps({'attempts':{k:l.session.attempt for k,l in b.labs.items()}}))
        w.close();app.processEvents();lock.unlock()
        cmd=[sys.executable,'-B',__file__,'--probe',str(root),'--label',args.label+'-restart','--expected-dpr',str(args.expected_dpr)]
        if args.offscreen:cmd.append('--offscreen')
        if args.installed:cmd.append('--installed')
        cmd.extend(['--evidence-root',str(out),'--monitor',args.monitor])
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
