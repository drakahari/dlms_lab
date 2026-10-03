"""Rendered Library cleanup with QtTest input and disposable profiles."""
import argparse,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QObject,QPointF,Qt,qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.collections import linux_fundamentals
from learning_lab.portable import load_portable

p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--expected-dpr',type=float,default=1);args=p.parse_args()
messages=[];qInstallMessageHandler(lambda kind,context,message:messages.append(message))
report={'input':'QtTest synthesized keys; not physical keyboard acceptance','checks':[]}
out=Path('evidence');out.mkdir(exist_ok=True)
def check(name,value):
    report['checks'].append({'name':name,'passed':bool(value)})
    if not value:raise AssertionError(name)
with tempfile.TemporaryDirectory(prefix='cleanup-ui-') as temp:
    root=Path(temp);app,e,b,lock=build_application(root/'data',root/'config');w=e.rootObjects()[0];report['platform']=app.platformName()
    def item(name):
        def visit(o):
            if o.objectName()==name and o.isVisible():return o
            for child in o.childItems():
                found=visit(child)
                if found is not None:return found
        found=visit(w.contentItem())
        if found is None:
            found=w.findChild(QObject,name)
        if found is None:raise AssertionError('Missing '+name)
        return found
    def activate(name,key=Qt.Key_Return):
        control=item(name);control.forceActiveFocus(Qt.TabFocusReason);QTest.qWait(50)
        QTest.keyClick(w,key);QTest.qWait(80)
    def menu(button,action):
        activate(button)
        activate(button+action)
    def fits(name):
        control=item(name);point=control.mapToScene(QPointF(0,0))
        return point.x()>=0 and point.y()>=0 and point.x()+control.width()<=w.width()+1 and point.y()+control.height()<=w.height()+1
    def capture(name):
        picture=w.grabWindow();check('render '+name,not picture.isNull());picture.save(str(out/(args.label+'-'+name+'.png')))
    try:
        check('exposed',QTest.qWaitForWindowExposed(w,5000));check('DPR',abs(w.devicePixelRatio()-args.expected_dpr)<.01)
        # Custom imported version uses the existing permissions engine.
        value=linux_fundamentals()[2]['scenario'].value();value['identity']['id']='cleanup-ui-permissions'
        source=root/'cleanup.lab.json';source.write_text(json.dumps(value));check('import',b.importPack(str(source)))
        imported=load_portable(source.read_bytes());key=imported.key
        check('open import',b.selectLab(key));b.execute('chmod 600 notes.txt');b.execute('cat notes.txt');b.submit()
        check('completed imported state',b.view['grade']['score']==100)
        ended=b.session.attempt['id'];b.restart('Challenge');b.execute('chmod 600 notes.txt');b.execute('cat notes.txt');b.submit()
        attempt=b.session.attempt['id']
        b.setCommandDraft('pwd');b.flush();b.navigate(0)
        for size in ((800,600),(1024,768),(1280,900)):
            w.resize(*size);b.navigate(0);QTest.qWait(80)
            check('Actions label fits '+str(size),item('actions-fundamentals-0').width()>=item('actions-fundamentals-0').implicitWidth()-1)
            menu('actions-fundamentals-0','Visibility')
            check('built-in hidden '+str(size),b.view['hiddenCount']==1 and len(b.view['visibleFundamentals'])==5)
            check('not completed by hide',b.view['fundamentals'][0]['status']=='Learn: Not started · Challenge: Not started')
            activate('showHiddenControl',Qt.Key_Space)
            builtin=b.collection[0]['scenario'].key
            check('hidden entry discoverable',item('inactive-'+builtin).isVisible())
            activate('inactive-actions-'+builtin)
            check('hidden menu fits '+str(size),fits('inactive-actions-'+builtin+'Visibility'))
            capture('hidden-'+str(size[0]))
            activate('inactive-actions-'+builtin+'Visibility')
            check('restore visibility exact',b.view['hiddenCount']==0)
            activate('showHiddenControl',Qt.Key_Space)
            menu('actions-'+key,'Visibility')
            check('explicit confirmation opens',item('removeLibraryDialog').property('visible'))
            check('Cancel focus',item('cancelLibraryRemoval').hasActiveFocus());check('confirm fits',fits('confirmLibraryRemoval'))
            capture('confirmation-'+str(size[0]));activate('cancelLibraryRemoval')
            check('cancellation preserves entry',b.view['removedCount']==0)
        menu('actions-'+key,'Visibility');activate('confirmLibraryRemoval')
        check('removed',b.view['removedCount']==1)
        activate('showHiddenControl',Qt.Key_Space)
        check('inactive practice blocked',not b.selectLab(key) and not b.navigate(1))
        menu('inactive-actions-'+key,'History')
        check('history accessible without restore',b.view['page']==2 and b.visibility.state(key)=='removed')
        check('current and ended attempts visible',set(r['id'] for r in b.view['history'])=={attempt,ended})
        b.navigate(0);QTest.qWait(60)
        capture('inactive-completed')
        menu('inactive-actions-'+key,'Visibility')
        check('restore without launch',b.page==0 and b.visibility.state(key)=='active')
        check('restore without duplicate',len([r for r in b.view['otherLabs'] if r['labKey']==key])==1)
        b.setLibraryState(key,'removed',True);QTest.qWait(60)
        for size in ((800,600),(1024,768),(1280,900)):
            w.resize(*size);QTest.qWait(60)
            activate('restore-primary-'+key)
            check('restore preview opens '+str(size),item('resumeLibraryDialog').property('visible'))
            check('resume Cancel focus '+str(size),item('cancelLibraryResume').hasActiveFocus())
            check('resume confirmation fits '+str(size),fits('confirmLibraryResume'))
            check('exact current candidate among history records',b.resumableAttempts(key)[0]['id']==attempt and len(b.resumableAttempts(key))==1)
            capture('restore-resume-'+str(size[0]));activate('cancelLibraryResume')
            check('resume cancellation keeps inactive',b.visibility.state(key)=='removed' and b.page==0)
        activate('restore-primary-'+key);activate('resume-choice-0',Qt.Key_Space);activate('confirmLibraryResume')
        check('restore resumes same completed attempt',b.session.attempt['id']==attempt and b.view['grade']['score']==100 and b.page==1)
        check('pending command and mode retained',b.view['commandDraft']=='pwd' and b.view['mode']=='Challenge')
        check('normal controls restored',item('modeButton').isEnabled() and item('resetButton').isEnabled())
        # Same workflow for a hidden built-in already carrying a current attempt.
        b.navigate(0);b.setLibraryState('gateway-dns','hidden');QTest.qWait(60)
        builtin_attempt=b.labs['gateway-dns'].session.attempt['id']
        activate('restore-primary-gateway-dns');activate('confirmLibraryResume')
        check('hidden built-in restored and resumed',b.view['labKey']=='gateway-dns' and b.session.attempt['id']==builtin_attempt and b.visibility.state('gateway-dns')=='active' and b.page==1)
        check('no QML errors',not any('Error' in m or 'Unable to assign' in m for m in messages))
        report['result']='PASS'
    finally:
        w.close();app.processEvents();lock.unlock();report['qml_messages']=messages
        (out/(args.label+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({'result':report['result'],'checks':len(report['checks']),'platform':report['platform']}))
