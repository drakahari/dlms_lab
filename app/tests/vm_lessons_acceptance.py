"""Qt selection fixtures, isolated profiles. Native rendering is not physical input."""
import argparse,contextlib,json,os,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt,QPointF,qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.vm_preview.bridge import VmBridge
from learning_lab.vm_preview.registry import LEGACY_ID,catalog,entries,units
from learning_lab.profile_backup import snapshot,write_backup,read_backup,restore
p=argparse.ArgumentParser();p.add_argument('--scale',type=float,default=1);p.add_argument('--native',action='store_true');p.add_argument('--storage-only',action='store_true',help='Review changed storage resources plus shared lifecycle controls');p.add_argument('--evidence-root',type=Path,help='Existing owned directory for persistent screenshots/checks; profile fixtures stay temporary');a=p.parse_args()
if a.evidence_root:
 assert a.evidence_root.is_absolute() and a.evidence_root.is_dir() and not a.evidence_root.is_symlink() and a.evidence_root.stat().st_uid==os.getuid()
out=Path(tempfile.mkdtemp(prefix='vm-lessons-ui-',dir=a.evidence_root));sizes=[];messages=[];qInstallMessageHandler(lambda t,c,m:messages.append(m));checks=[]
# Preserve disposable fixtures and failure evidence; no personal profile is used.
with contextlib.nullcontext(tempfile.mkdtemp(prefix='vm-lessons-profile-',dir=out)) as d:
 root=Path(d);app,engine,b,lock=build_application(root/'data',root/'config',root/'vm');w=engine.rootObjects()[0];vm=b.vm_preview;vm.sessions.gate_root=root/'gate'
 for manager in vm.sessions.managers.values():manager.gate_root=root/'gate'
 fake=root/'fixture';fake.write_bytes(b'fixture')
 def check(n,c):
  if not c:
   (out/'failed-check.json').write_text(json.dumps({'check':n,'busy':vm.view['busy'],'pending':vm._pending is not None,'window_active':w.isActive(),'size':[w.width(),w.height()]},indent=2))
  assert c,n;checks.append(n)
  with (out/'completed-checks.jsonl').open('a') as trace:trace.write(json.dumps({'check':n})+'\n')
 def item(name):
  def visit(x):
   if x.objectName()==name and x.isVisible():return x
   for child in x.childItems():
    v=visit(child)
    if v is not None:return v
  v=visit(w.contentItem());assert v is not None,name;return v
 def wait(error=False):
  end=time.monotonic()+15
  while (vm.view['busy'] or vm._pending is not None) and time.monotonic()<end:QTest.qWait(20)
  assert not vm.view['busy'] and vm._pending is None
  if not error:assert not vm.view['error'],vm.view['error']
 def focus_ready(name):
  # Refresh can temporarily disable controls; native activation/scrolling is
  # asynchronous. Require actual readiness, not a fixed 100 ms focus assumption.
  wait()
  if a.native:
   w.requestActivate();assert QTest.qWaitForWindowActive(w,5000),'Native test window not active'
  deadline=time.monotonic()+5
  while True:
   target=item(name)
   if not vm.view['busy'] and target.isEnabled():
    target.forceActiveFocus(Qt.TabFocusReason);app.processEvents()
    if target.hasActiveFocus() and target.isEnabled():return target
   assert time.monotonic()<deadline,'Input not ready: '+name
   QTest.qWait(10)
 def press(name):
  item(name).forceActiveFocus(Qt.TabFocusReason);QTest.keyClick(w,Qt.Key_Return);QTest.qWait(100)
 def select(id):vm.selectLesson(id);wait()
 ids=[e['id'] for e in entries()]
 try:
  check('exposed',QTest.qWaitForWindowExposed(w,5000));check('DPR',abs(w.devicePixelRatio()-a.scale)<.01);check('platform',app.platformName()==('wayland' if a.native else 'offscreen'));check('lazy optional startup',not (root/'vm').exists())
  press('vmPreviewButton');wait();item('vmLessonChoice').forceActiveFocus(Qt.TabFocusReason)
  display_text=item('vmDisplayGuidance').property('text')
  for phrase in ('Zoom To Fit enabled beside the Lab','floating window','Reopening returns to fit','percentage is not saved'):
   check('display guidance '+phrase,phrase in display_text)
  for key in (Qt.Key_Space,Qt.Key_Home,Qt.Key_Return):QTest.keyClick(w,key)
  QTest.qWait(100);wait();check('keyboard ComboBox selection',vm.view['selected_lesson_id']==ids[0])
  item('vmUnitChoice').forceActiveFocus(Qt.TabFocusReason)
  for key in (Qt.Key_Space,Qt.Key_Home,Qt.Key_Down,Qt.Key_Return):QTest.keyClick(w,key)
  QTest.qWait(100);wait();check('keyboard unit selection',vm.view['selected_lesson_id']==ids[8])
  for id in ([ids[0]]+[id for id in ids if id.startswith('real-linux-storage-')] if a.storage_only else ids):
   select(id);m=vm.manager
   check(id+' collection matches',vm.view['unit']['id']==next(u['id'] for u in units() if any(e['id']==id for e in u['entries'])))
   check(id+' unit selector visible',item('vmUnitChoice').width()>250)
   with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda root:os.open(fake,os.O_RDONLY)):
    m.reset(confirmed=True);vm.refresh();wait();check(id+' Learn command',item('vmCommand').property('text')==m.lesson['steps'][0]['command'])
    press('vmNext');wait();vm.progress('hint');wait();vm.progress('complete');wait();check(id+' self-review only',vm.view['session']['completion']['kind']=='self-reviewed' and 'score' not in vm.view['session'])
    m.reset('Challenge',True);vm.refresh();wait();check(id+' Challenge associated',vm.view['session']['mode']=='Challenge')
    if id in ids[8:]:
     check(id+' Challenge setup available',item('vmPracticeMaterial').property('text')==vm.view['support']['materials'][0])
     check(id+' interpretation remains available',item('vmInterpretationHeading').property('text')=='Interpretation questions')
    try:item('vmCommand');raise AssertionError('Challenge leaked guidance')
    except AssertionError as exc:assert str(exc)=='vmCommand'
    check(id+' Challenge keeps display guidance',item('vmDisplayGuidance').property('text')==display_text)
    m.progress('complete')
  legacy=vm.sessions.manager(LEGACY_ID)
  with patch.object(legacy,'admission'),patch.object(legacy,'image',side_effect=lambda root:os.open(fake,os.O_RDONLY)):legacy.reset(confirmed=True);legacy.progress('complete')
  before=legacy.status()['session'];first=vm.sessions.manager(ids[0]);r={'state':'running','store':first.binding,'profile':first.profile,'generation':first.status()['session']['generation']}
  first_record=first.status()['session']
  with patch('learning_lab.vm_preview.manager.Manager.reconcile',return_value=r),patch.object(first,'status',return_value={'state':'running','session':first_record}):
   select(ids[8]);check('cross-unit collection changed',vm.view['unit']['id']==units()[1]['id']);check('running lesson identified',vm.view['running_lesson_id']==ids[0]);check('Stop accessible',item('vmStop').isEnabled());check('second Start blocked',not item('vmStart').isEnabled());check('Reset while running blocked',not item('vmReset').isEnabled());check('return action available',item('vmReturnRunning').isEnabled())
   # The former live harness asserted focus after a 100 ms event-loop yield.
   # A refresh in that interval legitimately disables this button and removes
   # focus. Reproduce that interleaving explicitly, without launching a guest.
   import threading
   entered=threading.Event();release=threading.Event();original_view=vm.sessions.view
   target=item('vmReturnRunning');target.forceActiveFocus(Qt.TabFocusReason)
   check('focus probe initially focused',target.hasActiveFocus())
   def held_view(selected):
    entered.set();assert release.wait(5);return original_view(selected)
   with patch.object(vm.sessions,'view',side_effect=held_view):
    try:
     vm.refresh()
     deadline=time.monotonic()+5
     while not entered.is_set() and time.monotonic()<deadline:QTest.qWait(5)
     check('refresh probe entered',entered.is_set())
     QTest.qWait(100)
     check('refresh disables pending input',vm.view['busy'] and not target.isEnabled())
     check('old delayed focus assumption reproduced',not target.hasActiveFocus())
    finally:release.set();wait()
   check('readiness restored after refresh',not vm.view['busy'] and target.isEnabled())
   target.forceActiveFocus(Qt.TabFocusReason)
   check('ready focus immediately available',target.hasActiveFocus())
   press('vmReturnRunning');wait();check('return selects running lesson',vm.view['selected_lesson_id']==ids[0]);check('running Stop still enabled',item('vmStop').isEnabled());select(LEGACY_ID)
  vm.refresh();wait();check('legacy untouched by selection',legacy.status()['session']==before)
  for size in ((800,600),(1280,900)):
   select(ids[-2])
   w.resize(*size);QTest.qWait(100);sizes.append({'requested':list(size),'actual':[w.width(),w.height()]})
   for name in ('vmStart','vmStop','vmReset','vmClose'):
    x=item(name);pos=x.mapToScene(QPointF(0,0));check(name+' contained '+str(size),pos.x()>=0 and pos.y()>=0 and pos.x()+x.width()<=w.width() and pos.y()+x.height()<=w.height())
   check('selection width '+str(size),item('vmLessonChoice').width()>250);check('unit width '+str(size),item('vmUnitChoice').width()>250);w.grabWindow().save(str(out/f'{app.platformName()}-{a.scale}-{size[0]}.png'))
   guide=item('vmDisplayGuidance');pos=guide.mapToScene(QPointF(0,0))
   check('display guidance width '+str(size),pos.x()>=0 and pos.x()+guide.width()<=w.width() and guide.width()>250)
   check('display guidance wraps '+str(size),guide.property('lineCount')>1)
   material=item('vmPracticeMaterial');focus_ready('vmPracticeMaterial')
   check('setup focus '+str(size),material.hasActiveFocus())
   check('setup wraps '+str(size),material.property('lineCount')>1 and material.width()>250 and material.property('contentWidth')<=material.width()+1)
  # Long manually entered script instructions need full-height, plain wrapping
  # and reachable controls; no QML changes or native guest mocks-as-proof.
  for size in ((800,600),(1280,900)):
   w.resize(*size);QTest.qWait(100)
   for id in (() if a.storage_only else ('real-linux-bash-guards','real-linux-bash-records','real-linux-bash-handover')):
    select(id);m=vm.manager
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda root:os.open(fake,os.O_RDONLY)):
     m.reset('Learn',True);vm.refresh();wait()
    target=next(i for i,step in enumerate(m.lesson['steps']) if 'nano ' in step['command'])
    for _ in range(target):vm.progress('next');wait()
    command=item('vmCommand');focus_ready('vmCommand')
    check(id+' command focus '+str(size),command.hasActiveFocus())
    check(id+' command no horizontal clipping '+str(size),command.property('contentWidth')<=command.width()+1)
    def text_item(x,text):
     if x.isVisible() and x.property('text')==text:return x
     for child in x.childItems():
      found=text_item(child,text)
      if found is not None:return found
    explanation=text_item(w.contentItem(),m.lesson['steps'][target]['explanation'])
    check(id+' complete explanation '+str(size),explanation is not None and explanation.property('contentHeight')<=explanation.height()+1)
    check(id+' script wraps '+str(size),explanation.property('lineCount')>=len(m.lesson['steps'][target]['explanation'].splitlines()))
    from PySide6.QtQml import QQmlExpression
    plain=QQmlExpression(engine.rootContext(),explanation,'textFormat === 0')
    result=plain.evaluate()
    check(id+' plain text '+str(size),not plain.hasError() and result[0] is True and result[1] is False)
    focus_ready('vmNext');QTest.qWait(20)
    next_pos=item('vmNext').mapToScene(QPointF(0,0))
    check(id+' Next reachable after long script '+str(size),next_pos.y()>=0 and next_pos.y()+item('vmNext').height()<=w.height())
    w.grabWindow().save(str(out/f'{app.platformName()}-{a.scale}-{size[0]}-{id}.png'))
  for size in ((800,600),(1280,900)):
   w.resize(*size);QTest.qWait(100)
   for id in ([id for id in ids if id.startswith('real-linux-storage-')] if a.storage_only else ('real-linux-users-shared','real-linux-users-restrictions','real-linux-users-repair','real-linux-schedule-diagnose','real-linux-schedule-persistence','real-linux-schedule-assessment','real-linux-backup-damage','real-linux-backup-access','real-linux-backup-assessment','real-linux-discovery-identity','real-linux-discovery-kernel','real-linux-discovery-boot','real-linux-discovery-libraries','real-linux-discovery-ownership','real-linux-discovery-integrity','real-linux-discovery-lifecycle','real-linux-discovery-repair',*[id for id in ids if id.startswith('real-linux-storage-')])):
    select(id);m=vm.manager
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda root:os.open(fake,os.O_RDONLY)):
     vm.reset('Learn',True);wait()
    target=max(range(len(m.lesson['steps'])),key=lambda i:len(m.lesson['steps'][i]['command']))
    for _ in range(target):vm.progress('next');wait()
    command=item('vmCommand');focus_ready('vmCommand')
    check(id+' command focus '+str(size),command.hasActiveFocus())
    check(id+' command wraps without clipping '+str(size),command.property('contentWidth')<=command.width()+1 and command.property('contentHeight')<=command.height()+1)
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda root:os.open(fake,os.O_RDONLY)):
     vm.reset('Challenge',True);wait()
    material=item('vmPracticeMaterial');focus_ready('vmPracticeMaterial')
    check(id+' independent setup wraps '+str(size),material.property('contentWidth')<=material.width()+1 and material.property('contentHeight')<=material.height()+1)
    check(id+' setup focus '+str(size),material.hasActiveFocus())
    check(id+' self-review label '+str(size),'self-review' in vm.view['lesson']['coverage'].lower())
    w.grabWindow().save(str(out/f'{app.platformName()}-{a.scale}-{size[0]}-{id}.png'))
  select(ids[0]);m=vm.manager
  with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda root:os.open(fake,os.O_RDONLY)):
   press('vmReset');QTest.keyClick(w,Qt.Key_Escape);QTest.qWait(100);check('Reset cancel preserves completion',vm.view['session']['completion'] is not None)
   vm.reset('Challenge',True);wait();check('Challenge associated',vm.view['session']['mode']=='Challenge')
   try:item('vmCommand');raise AssertionError('Challenge leaked guidance')
   except AssertionError as exc:assert str(exc)=='vmCommand'
   check('Challenge completion fresh',vm.view['session']['completion'] is None)
   path=root/'vm/profiles'/m.profile/'current.json';path.rename(path.with_name('retained-current.json'));vm.refresh();wait(True)
   check('missing session explained','record is missing' in vm.view['error']);check('missing session Start blocked',not item('vmStart').isEnabled())
   vm.reset('Challenge',True);wait();check('missing session Reset retains evidence',(path.parent/'retained-current.json').is_file())
  b.flush();backup=snapshot(root/'data',root/'config',lock.locks);write_backup(backup,root/'backup.llbackup');saved=read_backup(root/'backup.llbackup');restore(saved,root/'restored',confirmed=True)
  check('backup excludes VM state',not any('vm' in n for n in backup.files));check('backup version unchanged',saved.manifest['schema_version'] in (1,2))
  reopen=VmBridge(root/'data',root/'config',root/'vm',gate_root=root/'gate');check('selection reopens',reopen.view['selected_lesson_id']==ids[0]);check('legacy record reopens exact',reopen.sessions.manager(LEGACY_ID).status()['session']==before)
  press('vmClose');check('focus returns',item('vmPreviewButton').hasActiveFocus());check('no QML warnings '+repr(messages),not messages)
 finally:
  w.close();app.processEvents()
  deadline=time.monotonic()+15
  while (vm.view['busy'] or vm._pending is not None) and time.monotonic()<deadline:QTest.qWait(10)
  assert not vm.view['busy'] and vm._pending is None,'Pending UI work at teardown'
  lock.unlock()
report={'checks':checks,'platform':app.platformName(),'DPR':a.scale,'evidence':str(out),'qml_messages':messages,'sizes':sizes,'input':'QtTest synthesized; physical keyboard/accessibility unverified'}
(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
