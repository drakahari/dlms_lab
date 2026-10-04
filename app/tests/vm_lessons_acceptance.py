"""Qt selection fixtures, isolated profiles. Native rendering is not physical input."""
import argparse,json,os,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt,QPointF,qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.vm_preview.bridge import VmBridge
from learning_lab.vm_preview.registry import LEGACY_ID,catalog
from learning_lab.profile_backup import snapshot,write_backup,read_backup,restore
p=argparse.ArgumentParser();p.add_argument('--scale',type=float,default=1);p.add_argument('--native',action='store_true');a=p.parse_args()
out=Path(tempfile.mkdtemp(prefix='vm-lessons-ui-'));sizes=[];messages=[];qInstallMessageHandler(lambda t,c,m:messages.append(m));checks=[]
with tempfile.TemporaryDirectory(prefix='vm-lessons-profile-') as d:
 root=Path(d);app,engine,b,lock=build_application(root/'data',root/'config',root/'vm');w=engine.rootObjects()[0];vm=b.vm_preview;vm.sessions.gate_root=root/'gate'
 for manager in vm.sessions.managers.values():manager.gate_root=root/'gate'
 fake=root/'fixture';fake.write_bytes(b'fixture')
 def check(n,c):
  assert c,n;checks.append(n)
 def item(name):
  def visit(x):
   if x.objectName()==name and x.isVisible():return x
   for child in x.childItems():
    v=visit(child)
    if v is not None:return v
  v=visit(w.contentItem());assert v is not None,name;return v
 def wait(error=False):
  end=time.monotonic()+15
  while vm.view['busy'] and time.monotonic()<end:QTest.qWait(20)
  assert not vm.view['busy']
  if not error:assert not vm.view['error'],vm.view['error']
 def press(name):
  item(name).forceActiveFocus(Qt.TabFocusReason);QTest.keyClick(w,Qt.Key_Return);QTest.qWait(100)
 def select(id):vm.selectLesson(id);wait()
 ids=[e['id'] for e in catalog()['entries']]
 try:
  check('exposed',QTest.qWaitForWindowExposed(w,5000));check('DPR',abs(w.devicePixelRatio()-a.scale)<.01);check('platform',app.platformName()==('wayland' if a.native else 'offscreen'));check('lazy optional startup',not (root/'vm').exists())
  press('vmPreviewButton');wait();item('vmLessonChoice').forceActiveFocus(Qt.TabFocusReason)
  display_text=item('vmDisplayGuidance').property('text')
  for phrase in ('Zoom To Fit enabled beside the Lab','floating window','Reopening returns to fit','percentage is not saved'):
   check('display guidance '+phrase,phrase in display_text)
  for key in (Qt.Key_Space,Qt.Key_Home,Qt.Key_Return):QTest.keyClick(w,key)
  QTest.qWait(100);wait();check('keyboard ComboBox selection',vm.view['selected_lesson_id']==ids[0])
  for id in ids:
   select(id);m=vm.manager
   with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda root:os.open(fake,os.O_RDONLY)):
    m.reset(confirmed=True);vm.refresh();wait();check(id+' Learn command',item('vmCommand').property('text')==m.lesson['steps'][0]['command'])
    press('vmNext');wait();vm.progress('hint');wait();vm.progress('complete');wait();check(id+' self-review only',vm.view['session']['completion']['kind']=='self-reviewed' and 'score' not in vm.view['session'])
    m.reset('Challenge',True);vm.refresh();wait();check(id+' Challenge associated',vm.view['session']['mode']=='Challenge')
    try:item('vmCommand');raise AssertionError('Challenge leaked guidance')
    except AssertionError as exc:assert str(exc)=='vmCommand'
    check(id+' Challenge keeps display guidance',item('vmDisplayGuidance').property('text')==display_text)
    m.progress('complete')
  legacy=vm.sessions.manager(LEGACY_ID)
  with patch.object(legacy,'admission'),patch.object(legacy,'image',side_effect=lambda root:os.open(fake,os.O_RDONLY)):legacy.reset(confirmed=True);legacy.progress('complete')
  before=legacy.status()['session'];first=vm.sessions.manager(ids[0]);r={'state':'running','store':first.binding,'profile':first.profile,'generation':first.status()['session']['generation']}
  first_record=first.status()['session']
  with patch('learning_lab.vm_preview.manager.Manager.reconcile',return_value=r),patch.object(first,'status',return_value={'state':'running','session':first_record}):
   select(LEGACY_ID);check('running lesson identified',vm.view['running_lesson_id']==ids[0]);check('Stop accessible',item('vmStop').isEnabled());check('second Start blocked',not item('vmStart').isEnabled());check('Reset while running blocked',not item('vmReset').isEnabled());check('return action available',item('vmReturnRunning').isEnabled())
   press('vmReturnRunning');wait();check('return selects running lesson',vm.view['selected_lesson_id']==ids[0]);check('running Stop still enabled',item('vmStop').isEnabled());select(LEGACY_ID)
  vm.refresh();wait();check('legacy untouched by selection',legacy.status()['session']==before)
  for size in ((800,600),(1280,900)):
   w.resize(*size);QTest.qWait(100);sizes.append({'requested':list(size),'actual':[w.width(),w.height()]})
   for name in ('vmStart','vmStop','vmReset','vmClose'):
    x=item(name);pos=x.mapToScene(QPointF(0,0));check(name+' contained '+str(size),pos.x()>=0 and pos.y()>=0 and pos.x()+x.width()<=w.width() and pos.y()+x.height()<=w.height())
   check('selection width '+str(size),item('vmLessonChoice').width()>250);w.grabWindow().save(str(out/f'{app.platformName()}-{a.scale}-{size[0]}.png'))
   guide=item('vmDisplayGuidance');pos=guide.mapToScene(QPointF(0,0))
   check('display guidance width '+str(size),pos.x()>=0 and pos.x()+guide.width()<=w.width() and guide.width()>250)
   check('display guidance wraps '+str(size),guide.property('lineCount')>1)
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
 finally:w.close();app.processEvents();lock.unlock()
report={'checks':checks,'platform':app.platformName(),'DPR':a.scale,'evidence':str(out),'qml_messages':messages,'sizes':sizes,'input':'QtTest synthesized; physical keyboard/accessibility unverified'}
(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
