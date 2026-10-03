"""Disposable rendered profile-transfer checks; QtTest is not physical input."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QObject, QMetaObject, Qt, QPointF, qInstallMessageHandler
from PySide6.QtTest import QTest
from PySide6.QtQml import QQmlExpression, QQmlEngine
from learning_lab.__main__ import build_application

parser=argparse.ArgumentParser();parser.add_argument('--label',default='profile-backup');parser.add_argument('--expected-dpr',type=float,default=1)
args=parser.parse_args();messages=[];qInstallMessageHandler(lambda kind,context,message:messages.append(message))
report={'input':'QtTest synthesized keyboard; not physical-keyboard acceptance','checks':[]}
out=Path('evidence');out.mkdir(exist_ok=True)

def check(name,value):
    report['checks'].append({'name':name,'passed':bool(value)})
    if not value:raise AssertionError(name)

with tempfile.TemporaryDirectory(prefix='profile-backup-ui-') as temp:
    root=Path(temp);app,e,b,lock=build_application(root/'data',root/'config');w=e.rootObjects()[0]
    report['platform']=app.platformName()
    def obj(name):
        item=w.findChild(QObject,name)
        if item is None:
            def visit(parent):
                if parent.objectName()==name:return parent
                for child in parent.childItems():
                    found=visit(child)
                    if found is not None:return found
            item=visit(w.contentItem())
        if item is None:raise AssertionError('Missing '+name)
        return item
    def click(name):
        obj(name).forceActiveFocus(Qt.TabFocusReason);QTest.keyClick(w,Qt.Key_Return);QTest.qWait(80)
    def popup(name):
        QMetaObject.invokeMethod(obj(name),'open');QTest.qWait(60)
    try:
        check('window renders',QTest.qWaitForWindowExposed(w,5000))
        check('requested DPR',abs(w.devicePixelRatio()-args.expected_dpr)<.01)
        b.setCommandDraft('pwd');b.flush()
        check('backup saves',b.backupProfile(str(root/'profile.llbackup')))
        long_parent=root/('long-destination-'+('a'*70))/('nested-'+('b'*70))/('profile-parent-'+('c'*70))
        long_parent.mkdir(parents=True)
        for size in ((800,600),(1024,768),(1280,900)):
            w.resize(*size);b.navigate(0);QTest.qWait(100)
            for name in ('backupProfileButton','restoreProfileButton'):
                item=obj(name);point=item.mapToScene(QPointF(0,0))
                check(f'{name} visible {size}',item.isVisible() and point.x()>=0 and point.y()>=0 and point.x()+item.width()<=w.width() and point.y()+item.height()<=w.height())
                check(f'{name} label fits {size}',item.width()>=item.implicitWidth()-1)
            library=obj('libraryPage')
            heading=obj('pageHeading'); point=heading.mapToItem(library,QPointF(0,0))
            check('shared Library insets '+str(size),point.x()>=20 and point.y()>=20)
            check('heading font preserved',heading.property('font').pixelSize()==27)
            for name in ('backupProfileButton','fundamentalsHeading','fundamentalsCard-0'):
                item=obj(name); point=item.mapToItem(library,QPointF(0,0))
                check('Library edges '+name+str(size),point.x()>=20 and point.x()+item.width()<=library.width()-32)
            w.grabWindow().save(str(out/(args.label+'-library-'+str(size[0])+'.png')))
            check('preview validates '+str(size),b.previewRestore(str(root/'profile.llbackup'),str(long_parent)))
            destination=b.restore_pending[1]
            popup('restoreProfilePreview')
            check('cancel receives initial focus',obj('cancelProfileRestore').hasActiveFocus())
            scroll=obj('profilePreviewScroll'); text=obj('previewSummary')
            point=text.mapToItem(scroll,QPointF(0,0))
            check('shared dialog insets '+str(size),point.x()>=20 and point.y()>=20 and point.x()+text.width()<=scroll.width()-32)
            check('prose word wrapping',QQmlExpression(QQmlEngine.contextForObject(text),text,'wrapMode === Text.WordWrap').evaluate()[0])
            check('prose font preserved',text.property('font').pixelSize()==15)
            path=obj('previewPath0')
            check('long destination exact/selectable',path.property('text')==str(destination) and len(str(destination))>260 and path.property('readOnly') and path.property('selectByMouse'))
            w.grabWindow().save(str(out/(args.label+'-summary-'+str(size[0])+'.png')))
            path.forceActiveFocus(Qt.TabFocusReason);QTest.qWait(40)
            QTest.keyClick(w,Qt.Key_Return);check('path Enter never confirms restore',not destination.exists() and b.restore_pending is not None)
            QTest.keyClick(w,Qt.Key_End);QTest.keyClick(w,Qt.Key_A,Qt.ControlModifier);QTest.keyClick(w,Qt.Key_C,Qt.ControlModifier)
            check('keyboard copies full path',app.clipboard().text()==str(destination))
            QTest.keyClick(w,Qt.Key_Tab);QTest.qWait(40)
            check('Tab reaches Copy',obj('previewPath0Copy').hasActiveFocus())
            app.clipboard().setText('copy sentinel')
            QTest.keyClick(w,Qt.Key_Return);QTest.qWait(40)
            check('Copy action exact',app.clipboard().text()==str(destination))
            check('focused field scrolled into view',path.mapToItem(scroll,QPointF(0,0)).y()>=0 and path.mapToItem(scroll,QPointF(0,path.height())).y()<=scroll.height())
            check('long contents scroll',scroll.property('contentHeight')>scroll.height())
            for name in ('cancelProfileRestore','confirmProfileRestore'):
                button=obj(name); point=button.mapToScene(QPointF(0,0))
                check('confirmation remains visible '+name,button.isVisible() and point.y()>=0 and point.y()+button.height()<=w.height())
            picture=w.grabWindow();check('preview capture',not picture.isNull())
            picture.save(str(out/(args.label+'-preview-'+str(size[0])+'.png')))
            click('cancelProfileRestore');check('cancel creates nothing',not destination.exists() and b.restore_pending is None)
        check('final preview',b.previewRestore(str(root/'profile.llbackup'),str(long_parent)))
        destination=b.restore_pending[1];popup('restoreProfilePreview');click('confirmProfileRestore')
        check('explicit confirmation restores',destination.joinpath('data/current.json').is_file())
        check('result shown',obj('profileResult').property('visible'))
        check('success explains profile unchanged','open profile is unchanged' in b.transfer_message)
        check('result separates destination',obj('resultPath0').property('text')==str(destination))
        click('resultPath1Copy');check('launch arguments copied',app.clipboard().text().startswith('--data-dir ') and str(destination) in app.clipboard().text())
        w.grabWindow().save(str(out/(args.label+'-result.png')))
        QMetaObject.invokeMethod(obj('profileResult'),'close');QTest.qWait(60)
        check('original pending command retained',b.view['commandDraft']=='pwd')
        # Opening/canceling actual Qt file-picker surfaces; not native portal proof.
        for button,dialog in (('backupProfileButton','backupProfileFileDialog'),('restoreProfileButton','restoreProfileFileDialog')):
            click(button);check('picker opens '+button,obj(dialog).property('visible'))
            QMetaObject.invokeMethod(obj(dialog),'reject');QTest.qWait(60)
            # Offscreen Qt needs simulated reactivation after a separate picker
            # window closes. Native compositor focus restoration is outstanding.
            w.requestActivate(); QTest.qWait(80)
            check('focus returns '+button,obj(button).hasActiveFocus())
        check('no QML binding errors',not any('Error' in m or 'Unable to assign' in m for m in messages))
        report['result']='PASS';report['qml_messages']=messages
    finally:
        w.close();app.processEvents();lock.unlock()
        (out/(args.label+'.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({'result':report['result'],'checks':len(report['checks']),'platform':report['platform']}))
