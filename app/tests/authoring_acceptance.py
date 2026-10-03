"""Rendered authoring controls using disposable profiles and QtTest, not native dialogs."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QObject, QMetaObject, Qt, QPointF, qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application

p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--expected-dpr',type=float,default=1);args=p.parse_args()
messages=[];qInstallMessageHandler(lambda kind,context,message:messages.append(message))
report={'checks':[], 'scope':'Offscreen rendering and synthesized keys; native file pickers/physical keyboard unverified'}
out=Path('evidence');out.mkdir(exist_ok=True)
def check(name,value):
    report['checks'].append({'name':name,'passed':bool(value)})
    if not value:raise AssertionError(name)
with tempfile.TemporaryDirectory(prefix='authoring-ui-') as temp:
    root=Path(temp);app,e,b,lock=build_application(root/'data',root/'config');w=e.rootObjects()[0]
    def item(name):
        result=w.findChild(QObject,name)
        if result is None:raise AssertionError('Missing '+name)
        return result
    def activate(name):
        o=item(name);o.forceActiveFocus(Qt.TabFocusReason);QTest.qWait(40);QTest.keyClick(w,Qt.Key_Return);QTest.qWait(60)
    def fits(name):
        o=item(name);at=o.mapToScene(QPointF(0,0))
        return at.x()>=0 and at.y()>=0 and at.x()+o.width()<=w.width()+1 and at.y()+o.height()<=w.height()+1
    def snap(name):
        image=w.grabWindow();check('render '+name,not image.isNull());image.save(str(out/(args.label+'-'+name+'.png')))
    try:
        check('exposed',QTest.qWaitForWindowExposed(w,5000));check('DPR',abs(w.devicePixelRatio()-args.expected_dpr)<.01)
        report['platform']=app.platformName()
        for width,height in ((800,600),(1024,768),(1280,900)):
            w.resize(width,height);b.navigate(0);QTest.qWait(80)
            activate('createLabButton');check('guide visible',item('authoringDialog').property('visible'))
            check('initial guide focus',item('authorGuideTab').hasActiveFocus())
            for name in ('saveStarterButton','validateAuthorLabButton','importValidatedButton','closeAuthoring'):
                check(name+' fits '+str(width),fits(name))
            check('readable font',item('authorReferenceText').property('font').pixelSize()==15)
            check('no implicit import',not item('importValidatedButton').isEnabled())
            snap('guide-'+str(width))
            activate('authorExampleTab');check('complete example shown','permission_targets' in item('authorReferenceText').property('text'))
            activate('authorPromptTab');activate('copyAuthorReference')
            check('copy prompt and schema',app.clipboard().text()==b.authoring.view['prompt'])
            source=root/('long-authoring-folder-name-'*5);source.mkdir(exist_ok=True);source=source/'my-new-permissions.lab.json'
            check('prepare starter',b.authoring.prepareStarter(str(source)))
            QMetaObject.invokeMethod(item('starterConfirmation'),'open');QTest.qWait(80)
            check('safe Cancel focus',item('cancelStarterSave').hasActiveFocus())
            check('path and confirmation fit',fits('starterDestination') and fits('confirmStarterSave'))
            snap('save-'+str(width));activate('cancelStarterSave');check('cancel no file',not source.exists())
            b.authoring.prepareStarter(str(source));QMetaObject.invokeMethod(item('starterConfirmation'),'open');QTest.qWait(60)
            activate('confirmStarterSave');check('starter saved',source.exists())
            before=len(b.portables);check('validate',b.authoring.validateLab(str(source)))
            activate('authorResultTab');check('summary read only',item('authorReferenceText').property('readOnly'))
            check('summary not playtesting','not a gameplay test' in item('authorReferenceText').property('text'))
            check('validate not install',len(b.portables)==before);snap('summary-'+str(width))
            activate('importValidatedButton');check('explicit import',len(b.portables)==before+1 and b.page==0)
            check('import now disabled',not item('importValidatedButton').isEnabled())
            activate('closeAuthoring');check('Library focus restored',item('createLabButton').hasActiveFocus())
            # New iteration uses a new file and identity, not the previous one.
            source.rename(source.with_name('previous-'+str(width)+'.lab.json'))
        check('no QML errors',not any('Error' in m or 'Unable to assign' in m for m in messages))
        report['result']='PASS'
    finally:
        w.close();app.processEvents();lock.unlock();report['qml_messages']=messages
        (out/(args.label+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({'result':report['result'],'checks':len(report['checks']),'platform':report['platform']}))
