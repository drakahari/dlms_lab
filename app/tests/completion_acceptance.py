"""Learning guide and truthful review UI; no guests, disposable profiles only."""
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
p.add_argument('--collection',default='lpic-network-evidence');p.add_argument('--layout-only',action='store_true');p.add_argument('--installed',action='store_true');p.add_argument('--evidence-root',type=Path)
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
        x=item(args.collection+'Heading');y=item('libraryPage');point=x.mapToItem(y,QPointF(0,0));report['failure_geometry']={'heading':[point.x(),point.y(),x.width(),x.height()],'viewport':[y.width(),y.height()]}
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
    if not args.offscreen:
        import os,time
        end=time.monotonic()+8
        while not any(c['pid']==os.getpid() for c in json.loads(subprocess.check_output(['hyprctl','-j','clients']))):
            assert time.monotonic()<end,'Native client publication timeout';QTest.qWait(25)
    initial_lab=b.view['labKey']
    initial_attempts=json.dumps({k:l.session.attempt for k,l in b.labs.items()},sort_keys=True)
    check('guide collapsed by default',not w.property('learningGuideOpen'))
    check('DPR',abs(w.devicePixelRatio()-args.expected_dpr)<.01)
    if args.probe:
        expected=json.loads((root/'expected.json').read_text())
        check('exact attempts reopen',{k:l.session.attempt for k,l in b.labs.items()}==expected['attempts'])
        check('pending command retained',b.view['commandDraft']=='cat HELP.txt')
    else:
        for width,height in ((800,600),(1280,900)):
            resize(width,height);activate('learningGuideButton')
            check('guide expanded '+str(width),w.property('learningGuideOpen'))
            for name in ('learningPathHelp','simulationHelp','scoringHelp','reportHelp','vmLearningHelp'):
                reveal(name);check('readable guide '+str((width,name)),inside(item(name),item('libraryPage')))
                check('wrapping without clipped horizontal prose '+name,item(name).property('contentWidth')<=item(name).width()+1)
            capture('guide-'+str(width))
            activate('learningGuideButton');check('explicit collapse '+str(width),not w.property('learningGuideOpen'))
            activate('learningGuideButton');activate('learningGuideButton')
            check('repeated keyboard toggle '+str(width),not w.property('learningGuideOpen'))
            check('no lesson started by guide',not b.view['console'])
            check('selection and exact attempts unchanged '+str(width),b.view['labKey']==initial_lab and json.dumps({k:l.session.attempt for k,l in b.labs.items()},sort_keys=True)==initial_attempts)
        from learning_lab.collections import load_collections
        scenario=next(c for c in load_collections() if c['id']=='lpic-resource-evidence')['entries'][0]['scenario']
        b.selectLab(scenario.key,False)
        for mode in ('Learn','Challenge'):
            if mode=='Challenge':activate('modeButton');activate('confirmRestart')
            command('pwd');b.setCommandDraft('cat HELP.txt');b.flush()
            activate('libraryNav');activate('learningGuideButton');activate('learningGuideButton');activate('labNav')
            check('guide does not discard pending input '+mode,b.view['commandDraft']=='cat HELP.txt')
            if mode=='Challenge':check('Challenge guidance hidden',b.view['guide']=={})
            command('head -n 1 snapshot.txt > baseline.txt');activate('submitButton')
            check('incomplete report not complete '+mode,not b.view['grade']['complete'])
            activate('continueWorking')
            from learning_lab.linux_text.engine import guide
            for _ in range(64):
                if b.session.engine.grade()['complete']:break
                command(guide(b.pack,b.session.attempt['applied'])['command'])
            activate('submitButton');check('retry complete '+mode,b.view['grade']['score']==100)
            for width,height in ((800,600),(1280,900)):
                resize(width,height);check('explicit score boundary '+str((mode,width)),'does not verify diagnostic reasoning' in item('scoreBoundary').property('text'))
                check('score boundary wraps '+str((mode,width)),item('scoreBoundary').property('contentWidth')<=item('scoreBoundary').width()+1)
                capture('review-'+mode+'-'+str(width))
            activate('continueWorking');check('terminal focus after review '+mode,item('commandInput').hasActiveFocus())
        b.selectLab(initial_lab,False);activate('submitButton')
        check('network baseline fault still graded',not b.view['grade']['complete'] and not w.property('linux'))
        check('network review boundary available','Only the listed objectives' in item('scoreBoundary').property('text'))
        activate('continueWorking');check('network review returns to workspace',not w.property('reviewing'))
        b.selectLab(scenario.key,False)
        b.setCommandDraft('cat HELP.txt');b.flush()
        (root/'expected.json').write_text(json.dumps({'attempts':{k:l.session.attempt for k,l in b.labs.items()}}))
        w.close();app.processEvents();lock.unlock()
        cmd=[sys.executable,'-B',__file__,'--probe',str(root),'--label',args.label+'-restart','--expected-dpr',str(args.expected_dpr),'--evidence-root',str(out)]
        if args.offscreen:cmd.append('--offscreen')
        if args.installed:cmd.append('--installed')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
        report['restart']=result.stdout+result.stderr;check('separate process exact reopening',result.returncode==0)
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
