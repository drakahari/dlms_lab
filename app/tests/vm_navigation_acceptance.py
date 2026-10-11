"""Real Qt navigation input, isolated profiles, no guest launch or image access.

Native mode floats/resizes only this process's test window on a named monitor.
Screenshots are app-window captures. Never substitutes UI mocks for VM evidence.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

p = argparse.ArgumentParser()
p.add_argument('--native', action='store_true')
p.add_argument('--installed', action='store_true')
p.add_argument('--quick', action='store_true')
p.add_argument('--expected-dpr', type=float, default=1)
p.add_argument('--monitor', default='eDP-1')
p.add_argument('--evidence-root', type=Path)
a = p.parse_args()
if not a.installed:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt, QPoint, QPointF, QUrl, QObject, qInstallMessageHandler, QCoreApplication, QEvent
from PySide6.QtQml import QQmlComponent, QQmlExpression
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.theme import contrast
from learning_lab.vm_preview.registry import units
import learning_lab

out = Path(tempfile.mkdtemp(prefix='navigation-', dir=a.evidence_root))
profile = out / 'profile'
messages = []
qInstallMessageHandler(lambda kind, context, message: (messages.append(message), print('QML:', message, file=sys.stderr)))
app, engine, b, lock = build_application(profile/'data', profile/'config', profile/'vm')
w = engine.rootObjects()[0]
engine.rootContext().setContextProperty('testNavigationWindow',w)
vm = b.vm_preview
vm.sessions.gate_root = profile/'gate'
for m in vm.sessions.managers.values():
    m.gate_root = profile/'gate'
start_guard=patch('learning_lab.vm_preview.manager.Manager.start',side_effect=AssertionError('UI test must never launch a guest'))
start_mock=start_guard.start()
checks = []
colors = []
sizes = []
class PointerObserver(QObject):
    def __init__(self):
        super().__init__();self.position=None
    def eventFilter(self,obj,event):
        if event.type()==QEvent.MouseMove:self.position=event.position()
        return False
pointer=PointerObserver();w.installEventFilter(pointer)


def move_pointer(pos):
    target=QPoint(round(pos.x()),round(pos.y()))
    pointer.position=None
    QTest.mouseMove(w,target)
    until(lambda:pointer.position==QPointF(target),'window received pointer position')


def check(name, condition):
    assert condition, name
    checks.append(name)
    with (out/'checks.jsonl').open('a') as f:
        f.write(json.dumps({'check': name})+'\n')


def until(condition, name, seconds=10):
    end = time.monotonic()+seconds
    while not condition():
        assert time.monotonic()<end, name
        QTest.qWait(10)


def ready():
    until(lambda: not vm.view['busy'] and vm._pending is None, 'VM adapter idle')
    check('adapter has no error', not vm.view['error'])


def item(name):
    def walk(x):
        if x.objectName()==name and x.isVisible():
            return x
        for child in x.childItems():
            found = walk(child)
            if found is not None:
                return found
    result = walk(w.contentItem())
    if result is None:
        result=w.findChild(QObject,name)
        if result is not None and not result.property('visible'):result=None
    assert result is not None, name
    return result


def ev(obj, expression):
    q = QQmlExpression(engine.rootContext(), obj, expression)
    value, undefined = q.evaluate()
    assert not q.hasError() and not undefined, q.error().toString()
    return value


def click(x):
    pos=x.mapToScene(x.boundingRect().center())
    QTest.mouseClick(w, Qt.LeftButton, Qt.NoModifier, QPoint(round(pos.x()), round(pos.y())))


def opened(x):
    return ev(x, 'popup.visible')


def open_choice(x):
    ready()
    # Use the actual scrollbar thumb when compact content exceeds the viewport.
    # Synthetic wheel input failed to move scrolling in retained diagnostics;
    # its event sink is not established. Do not retry until a preferred result.
    viewport=item('vmContents') if x.objectName() else None
    if viewport is not None:
        top=viewport.mapToScene(QPointF(0,0)).y();bottom=top+viewport.height()
        y=x.mapToScene(QPointF(0,0)).y()
        if y<top or y+x.height()>bottom:
            bar=next(c for c in viewport.childItems() if 'ScrollBar' in c.metaObject().className() and c.height()>c.width())
            thumb=ev(bar,'contentItem')
            start=thumb.mapToScene(thumb.boundingRect().center())
            target_y=0 if y<top else ev(viewport,'contentItem.contentY')+y+x.height()-bottom+20
            extent=ev(viewport,'contentHeight')-viewport.height()
            fraction=max(0,min(1,target_y/extent))
            end=bar.mapToScene(QPointF(bar.width()/2,2+thumb.height()/2+fraction*(bar.height()-4-thumb.height())))
            QTest.mousePress(w,Qt.LeftButton,Qt.NoModifier,start.toPoint())
            move_pointer(end)
            QTest.mouseRelease(w,Qt.LeftButton,Qt.NoModifier,end.toPoint())
            until(lambda:x.mapToScene(QPointF(0,0)).y()>=top and x.mapToScene(QPointF(0,0)).y()+x.height()<=bottom,'scrollbar drag reaches control')
            check('mouse scrollbar exposes '+x.objectName(),True)
    if viewport is not None:
        until(lambda:not ev(viewport,'contentItem.moving'),'scroll motion finished')
    click(x)
    try:until(lambda: opened(x), 'mouse opens '+x.objectName())
    except AssertionError:
        pos=x.mapToScene(QPointF(0,0))
        (out/'failed-open.json').write_text(json.dumps({'control':x.objectName(),'enabled':x.isEnabled(),'focus':x.hasActiveFocus(),'reason':str(x.property('focusReason')),'position':[pos.x(),pos.y()],'size':[x.width(),x.height()],'busy':vm.view['busy'],'windowActive':w.isActive(),'scroll':ev(viewport,'contentItem.contentY') if viewport else None},indent=2))
        w.grabWindow().save(str(out/'failed-open.png'));raise
    check('popup focus '+x.objectName(), x.hasActiveFocus())


def keyboard_ready(x):
    # Native pointer-enter delivery can lag a synthetic mouse move. Acknowledge
    # the pointer leaving the delegates before testing independent key input.
    panel=item('vmPreview')
    move_pointer(QPoint(round(panel.property('x')+12),round(panel.property('y')+10)))
    until(lambda:ev(x,'''(function(){for(var i=0;i<count;i++) {
        var r=popup.contentItem.itemAtIndex(i);if(r && r.hovered)return false;
        }return true;})()'''),'pointer has left popup delegates')


def escape(x):
    QTest.keyClick(w, Qt.Key_Escape)
    until(lambda: not opened(x), 'Escape closes popup')
    check('Escape restores selector focus', x.hasActiveFocus())


def row(x, index=None):
    expression = '''JSON.stringify((function() {
        var r=popup.contentItem.itemAtIndex(highlightedIndex);
        if(!r) return null;
        var p=r.mapToItem(testNavigationWindow.contentItem,0,0);
        return {text:String(r.contentItem.color),background:String(r.background.color),
          x:p.x,y:p.y,width:r.width,height:r.height,
          textWidth:r.contentItem.width,contentWidth:r.contentItem.contentWidth,
          lines:r.contentItem.lineCount,index:r.index}; })())'''
    if index is not None:
        expression=expression.replace('itemAtIndex(highlightedIndex)','itemAtIndex('+str(index)+')')
    raw=ev(x,expression)
    return json.loads(raw)


def readable(x, label, index=None):
    until(lambda: row(x,index) is not None, 'row instantiated')
    r = row(x,index)
    ratio = contrast(r['text'], r['background'])
    colors.append({'label':label, 'contrast':ratio, **r})
    check(label+' actual delegate contrast >= 4.5', ratio >= 4.5)
    check(label+' text wraps without clipping', r['contentWidth']<=r['textWidth']+1)
    return r


def hypr(expression):
    result=subprocess.run(['hyprctl','dispatch',expression], capture_output=True, text=True, timeout=5)
    assert result.returncode==0 and result.stdout.strip()=='ok', result.stdout+result.stderr


def resize(size):
    if a.native:
        # Explicit PID selector: do not change any owner's window/configuration.
        hypr('hl.dsp.window.resize({x='+str(round(size[0]*a.expected_dpr/monitor_scale))+',y='+str(round(size[1]*a.expected_dpr/monitor_scale))+',relative=false,window="pid:'+str(os.getpid())+'"})')
    else:
        w.resize(*size)
    until(lambda: (w.width(),w.height())==size, 'actual requested window size')
    QTest.qWait(40)
    sizes.append({'requested':list(size),'actual':[w.width(),w.height()]})

try:
    check('exposed', QTest.qWaitForWindowExposed(w,5000))
    if a.native:
        monitors=json.loads(subprocess.check_output(['hyprctl','monitors','-j'],text=True))
        monitor_scale=next(m['scale'] for m in monitors if m['name']==a.monitor)
        hypr('hl.dsp.window.float({action="set",window="pid:'+str(os.getpid())+'"})')
        hypr('hl.dsp.window.move({monitor="'+a.monitor+'",follow=true,window="pid:'+str(os.getpid())+'"})')
        w.requestActivate()
        check('native active', QTest.qWaitForWindowActive(w,5000))
    until(lambda: abs(w.devicePixelRatio()-a.expected_dpr)<.01, 'expected display scaling')
    check('platform',app.platformName()==('wayland' if a.native else 'offscreen'))
    item('vmPreviewButton').forceActiveFocus(Qt.TabFocusReason);QTest.keyClick(w,Qt.Key_Return)
    until(lambda:w.findChild(QObject,'vmPreview').property('visible'),'VM panel opened');ready()
    panel=item('vmPreview');unit=item('vmUnitChoice');lesson=item('vmLessonChoice')
    for fallback in (False, True):
        b.fallbackTheme(fallback);app.processEvents()
        label='fallback' if fallback else 'omarchy'
        for size in ((800,600),(1280,900)):
            resize(size)
            for choice in (unit, lesson):
                open_choice(choice)
                original=vm.view['selected_lesson_id']
                QTest.keyClick(w,Qt.Key_Home);QTest.keyClick(w,Qt.Key_Down)
                until(lambda: choice.property('highlightedIndex')==1,'keyboard highlight')
                readable(choice,label+' highlighted '+choice.objectName()+' '+str(size))
                readable(choice,label+' normal '+choice.objectName(),0)
                readable(choice,label+' selected '+choice.objectName(),choice.property('currentIndex'))
                check('visible focus border',ev(choice,'background.border.width')==2)
                hover=row(choice,0)
                QTest.mouseMove(w,QPoint(round(hover['x']+20),round(hover['y']+hover['height']/2)))
                until(lambda:choice.property('highlightedIndex')==0,'mouse hover highlight')
                readable(choice,label+' hovered '+choice.objectName())
                # Finish the mouse-hover case before the independent keyboard
                # persistence case. Native cursor-enter delivery is asynchronous.
                escape(choice);open_choice(choice);keyboard_ready(choice)
                QTest.keyClick(w,Qt.Key_Home);QTest.keyClick(w,Qt.Key_Down)
                until(lambda:choice.property('highlightedIndex')==1,'restore keyboard highlight')
                # Hold an actual asynchronous adapter refresh, not a synthetic
                # busy property. Model notifications occur before and after it.
                entered=threading.Event();release=threading.Event()
                original_view=vm.sessions.view
                def held(selected):
                    entered.set();assert release.wait(5);return original_view(selected)
                with patch.object(vm.sessions,'view',side_effect=held):
                    try:
                        vm.refresh();until(entered.is_set,'refresh entered')
                        check('refresh marked read-only', vm.view['busy'] and vm.view['refreshing'])
                        check('refresh keeps menu enabled/open', choice.isEnabled() and opened(choice))
                        check('refresh keeps highlighted index', choice.property('highlightedIndex')==1)
                        check('refresh does not enable VM actions',not item('vmStart').isEnabled() and not item('vmReset').isEnabled() and not item('vmStop').isEnabled())
                    finally:
                        release.set();ready()
                check('finished refresh keeps popup/highlight '+repr({'visible':opened(choice),'index':choice.property('highlightedIndex'),'active':w.isActive(),'focus':choice.hasActiveFocus()}), opened(choice) and choice.property('highlightedIndex')==1)
                check('navigation does not select/start',vm.view['selected_lesson_id']==original and not start_mock.called and not list((profile/'vm').rglob('current.json')) and not list((profile/'vm').rglob('*.qcow2')))
                if not a.quick and size==(1280,900) and choice is lesson:
                    # The production Timer must also poll while navigation remains open.
                    transitions=[];epoch=time.monotonic()
                    def state_event(*unused):
                        transitions.append({'seconds':round(time.monotonic()-epoch,3),'open':opened(choice),'index':choice.property('highlightedIndex'),'current':choice.property('currentIndex'),'enabled':choice.isEnabled(),'busy':vm.view['busy'],'refreshing':vm.view['refreshing'],'active':w.isActive(),'focus':choice.hasActiveFocus()})
                    ev(choice,'(popup.objectName="periodicPopup",true)')
                    popup=choice.findChild(QObject,'periodicPopup')
                    assert popup is not None,'periodic popup QObject'
                    for signal in (popup.visibleChanged,choice.highlightedIndexChanged,vm.changed,w.activeChanged):signal.connect(state_event)
                    state_event()
                    QTest.qWait(5300);ready()
                    for signal in (popup.visibleChanged,choice.highlightedIndexChanged,vm.changed,w.activeChanged):signal.disconnect(state_event)
                    with (out/'periodic-transitions.jsonl').open('a') as f:f.write(json.dumps(transitions)+'\n')
                    check('periodic refresh preserves open popup '+repr(transitions),opened(choice) and choice.property('highlightedIndex')==1)
                w.grabWindow().save(str(out/f'{label}-{size[0]}-{choice.objectName()}.png'))
                escape(choice)
                open_choice(choice)
                # Deliberate click outside the popup but inside the panel title.
                pos=QPointF(panel.property('x')+12,panel.property('y')+10)
                QTest.mouseClick(w,Qt.LeftButton,Qt.NoModifier,QPoint(round(pos.x()),round(pos.y())))
                until(lambda:not opened(choice),'outside click closes')
            open_choice(unit);QTest.keyClick(w,Qt.Key_Home)
            for _ in range(3):QTest.keyClick(w,Qt.Key_Down)
            QTest.keyClick(w,Qt.Key_Return);ready()
            check('collection changes to exact first lesson',vm.view['selected_lesson_id']==units()[3]['entries'][0]['id'])
            check('lesson list scoped to chosen collection',lesson.property('count')==12)
            open_choice(lesson);QTest.keyClick(w,Qt.Key_End)
            until(lambda:lesson.property('highlightedIndex')==11,'long list End')
            rr=readable(lesson,label+' long list')
            # Mouse activation uses the actual visible last delegate.
            QTest.mouseClick(w,Qt.LeftButton,Qt.NoModifier,QPoint(round(rr['x']+rr['width']/2),round(rr['y']+rr['height']/2)))
            ready();check('mouse activates exact last lesson',vm.view['selected_lesson_id']==units()[3]['entries'][-1]['id'])
            check('selection closes popup',not opened(lesson))
            check('summary matches collection/lesson/mode',vm.view['lesson']['title'] in item('vmSelectedSummary').property('text') and vm.view['unit']['title'] in item('vmSelectedSummary').property('text'))
            summary=item('vmSelectedSummary');pos=summary.mapToScene(QPointF(0,0))
            check('selected summary always visible',pos.y()>=0 and pos.y()+summary.height()<=w.height())
            mode=item('vmMode');mode.forceActiveFocus(Qt.TabFocusReason);app.processEvents()
            view=item('vmContents')
            def mode_visible():
                vpos=view.mapToScene(QPointF(0,0));mpos=mode.mapToScene(QPointF(0,0))
                return mpos.y()>=vpos.y() and mpos.y()+mode.height()<=vpos.y()+view.height()
            until(mode_visible,'keyboard mode focus scrolls into view')
            check('keyboard mode focus scrolls into view',mode_visible())
            for k in (Qt.Key_Space,Qt.Key_End,Qt.Key_Return):QTest.keyClick(w,k)
            check('Challenge reflected in visible summary','Challenge' in item('vmSelectedSummary').property('text'))
            until(lambda:not opened(mode),'mode activation completes popup close')
            # Return to original unit through the normal keyboard path.
            open_choice(unit)
            for k in (Qt.Key_Home,Qt.Key_Return):QTest.keyClick(w,k)
            ready()
            for _ in range(3):
                open_choice(lesson);QTest.keyClick(w,Qt.Key_Down);escape(lesson)
            check('repeated navigation never launches guest',not start_mock.called and not list((profile/'vm').rglob('current.json')) and not list((profile/'vm').rglob('*.qcow2')))
            for n in ('vmStart','vmStop','vmReset','vmClose'):
                x=item(n);pos=x.mapToScene(QPointF(0,0))
                check('footer reachable '+n+' '+str(size),pos.y()>=0 and pos.y()+x.height()<=w.height() and pos.x()>=0 and pos.x()+x.width()<=w.width())
    # Independent review gate: activation DURING polling queues one exact ID.
    open_choice(unit)
    QTest.keyClick(w,Qt.Key_Home);QTest.keyClick(w,Qt.Key_Down)
    entered=threading.Event();release=threading.Event();original_view=vm.sessions.view
    def held(selected):
        entered.set();assert release.wait(5);return original_view(selected)
    target=units()[1]['entries'][0]['id']
    with patch.object(vm.sessions,'view',side_effect=held):
        try:
            vm.refresh();until(entered.is_set,'queued selection poll entered')
            QTest.keyClick(w,Qt.Key_Return)
            check('activation during refresh intentionally closes popup',not opened(unit))
            check('queue pins exact intended lesson',vm._pending is not None and vm._pending[2]==target)
            check('queued selection keeps Start disabled',not item('vmStart').isEnabled())
        finally:
            release.set();ready()
    check('queued activation selects intended collection/lesson',vm.view['selected_lesson_id']==target)
    open_choice(lesson)
    entered=threading.Event();release=threading.Event();original_view=vm.sessions.view
    with patch.object(vm.sessions,'view',side_effect=held):
        try:
            vm.selectLesson(target);until(entered.is_set,'selection operation entered')
            check('actual selection is not passive refresh',vm.view['busy'] and not vm.view['refreshing'])
            check('actual operation disables selectors',not unit.isEnabled() and not lesson.isEnabled() and not item('vmMode').isEnabled())
            check('actual operation closes popup',not opened(lesson))
        finally:
            release.set();ready()
    check('selectors reenabled after operation',unit.isEnabled() and lesson.isEnabled())
    # Exercise the actual shared control with data-only UI fixtures: a single
    # item, long words/labels, empty and stale selection. Not new lab content.
    c=QQmlComponent(engine,QUrl.fromLocalFile(str(Path(learning_lab.__file__).parent/'qml/LabChoice.qml')))
    fixture=c.create();assert fixture is not None,[e.toString() for e in c.errors()]
    fixture.setParent(engine);fixture.setParentItem(w.contentItem());fixture.setWidth(360);fixture.setX(60);fixture.setY(60)
    # Close only the VM panel to expose the standalone control test.
    ev(panel,'(close(), true)');app.processEvents()
    fixture.setProperty('model',['One lesson with a long readable title and normal words '*4]);fixture.setProperty('currentIndex',0)
    open_choice(fixture);readable(fixture,'single long title');check('long title is multiline',row(fixture)['lines']>1);escape(fixture)
    fixture.setProperty('model',['LongUnbrokenName'+'x'*180]);fixture.setProperty('currentIndex',0)
    open_choice(fixture);readable(fixture,'unbroken long title');check('unbroken title is multiline',row(fixture)['lines']>1);escape(fixture)
    fixture.setProperty('currentIndex',-1);check('stale selection is explicit',fixture.property('displayText')=='No selection available')
    fixture.setProperty('enabled',False)
    check('disabled text contrast',ev(fixture,'palette.mid.toString()') and contrast(ev(fixture,'String(contentItem.color)'),ev(fixture,'String(background.color)'))>=4.5)
    fixture.setProperty('model',[]);check('empty model stays unselected',fixture.property('count')==0 and fixture.property('currentIndex')==-1)
    # Verify existing lifecycle button routing using an isolated QObject backend.
    # This never calls the real Manager/controller or pretends to boot/Stop a VM.
    from PySide6.QtCore import Signal, Slot, Property
    class FixtureBackend(QObject):
        changed=Signal()
        def __init__(self):
            super().__init__();self.calls=[]
            self.value={**vm.view,'busy':False,'refreshing':False,'prerequisites':True,
                        'state':'not-started','session':None,'running_lesson_id':'',
                        'other_profile_running':False}
        @Property('QVariantMap',notify=changed)
        def view(self):return self.value
        @Slot()
        def refresh(self):pass
        @Slot(str)
        def start(self,mode):self.calls.append(['start',self.value['selected_lesson_id'],mode])
        @Slot()
        def stop(self):self.calls.append(['stop',self.value['running_lesson_id']])
        @Slot(str,bool)
        def reset(self,mode,confirmed):self.calls.append(['reset',self.value['selected_lesson_id'],mode,confirmed])
    fake=FixtureBackend();fake.setParent(engine);panel.setProperty('backend',fake)
    ev(panel,'(open(), true)');panel.setProperty('chosenMode','Learn');app.processEvents()
    click(item('vmStart'));check('Start routes selected lesson/mode',fake.calls[-1]==['start',target,'Learn'])
    fake.value={**fake.value,'state':'stopped','session':{'mode':'Challenge','step':0,'hints':0,'completion':None}}
    fake.changed.emit();app.processEvents()
    check('Resume label keeps disk distinction',item('vmStart').property('text')=='Resume disk')
    click(item('vmStart'));check('Resume routes pinned session mode',fake.calls[-1]==['start',target,'Challenge'])
    owner=units()[0]['entries'][0]['id']
    fake.value={**fake.value,'state':'not-started','session':None,'running_lesson_id':owner,'running_title':'Fixture running lesson','running_state':'running'}
    fake.changed.emit();app.processEvents()
    check('second Start blocked with another running lesson',not item('vmStart').isEnabled())
    click(item('vmStop'));check('Stop routes running owner not selection',fake.calls[-1]==['stop',owner])
    fake.value={**fake.value,'running_lesson_id':''};fake.changed.emit();app.processEvents()
    click(item('vmReset'));dialog=w.findChild(QObject,'vmResetConfirmation')
    until(lambda:dialog.property('visible'),'Reset confirmation opened')
    before=list(fake.calls);QTest.keyClick(w,Qt.Key_Escape)
    check('Reset cancellation does not dispatch',fake.calls==before)
    click(item('vmReset'));until(lambda:dialog.property('visible'),'Reset confirmation reopened')
    ok=ev(dialog,'standardButton(0x400)')
    click(ok);app.processEvents()
    check('Reset remains explicit and selected-lesson scoped',fake.calls[-1][0:2]==['reset',target] and fake.calls[-1][-1] is True)
    ev(panel,'(close(), true)');panel.setProperty('backend',vm);app.processEvents()
    # An unavailable collection/lesson must not display a fallback selection
    # or offer Start/Reset. This is a transient UI fixture, never a saved record.
    stale={**vm.view,'units':[],'choices':[],'selected_lesson_id':'missing'}
    panel.setProperty('info',stale);app.processEvents()
    check('stale selection invalidates actions',not ev(panel,'vmSelectionValid'))
    check('empty collection has no implicit choice',unit.property('count')==0 and unit.property('currentIndex')==-1 and not unit.isEnabled())
    check('empty lesson has no implicit choice',lesson.property('count')==0 and lesson.property('currentIndex')==-1 and not lesson.isEnabled())
    # Stale indices must not cross into backend operations.
    with patch.object(vm,'selectLesson') as select_lesson,patch.object(vm,'selectUnit') as select_unit:
        ev(panel,'(chooseLesson(-1), true)');ev(panel,'(chooseLesson(999), true)');ev(panel,'(chooseUnit(-1), true)');ev(panel,'(chooseUnit(999), true)')
        check('invalid indices cause no operation',not select_lesson.called and not select_unit.called)
    check('no guest storage created',not start_mock.called and not list((profile/'vm').rglob('current.json')) and not list((profile/'vm').rglob('*.qcow2')))
    # The unchanged baseline emits this Qt/GTK portal-registration warning.
    # Keep it visible and recorded; reject every QML or other unexpected warning.
    portal='Failed to register with host portal QDBusError("org.freedesktop.portal.Error.Failed", "Could not register app ID: Connection already associated with an application ID")'
    check('no QML or unexpected warnings',all(m==portal for m in messages))
finally:
    actual_dpr=w.devicePixelRatio()
    ready();b.flush();lock.unlock();w.hide();start_guard.stop();engine.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)
    report={'checks':checks,'colors':colors,'sizes':sizes,'messages':messages,'platform':app.platformName(),'DPR':actual_dpr,'Qt':__import__('PySide6').__version__,'source':str(Path(learning_lab.__file__).parent),'input':'QtTest; physical keyboard and accessibility unverified','evidence':str(out)}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
