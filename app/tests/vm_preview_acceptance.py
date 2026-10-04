"""UI-only fixture: private VM metadata, no guest launch or personal profile."""
import argparse,json,os,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt,QPointF,qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.vm_preview.manager import Manager
from learning_lab.profile_backup import snapshot,write_backup,read_backup,restore
p=argparse.ArgumentParser();p.add_argument('--scale',type=float,default=1);p.add_argument('--native',action='store_true');a=p.parse_args()
messages=[];qInstallMessageHandler(lambda t,c,m:messages.append(m));checks=[];sizes=[]
out=Path('/tmp/learning-lab-vm-preview-evidence');out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='vm-preview-ui-') as d:
 root=Path(d);app,engine,b,lock=build_application(root/'data',root/'config',root/'vm');w=engine.rootObjects()[0];vm=b.vm_preview
 m=Manager(root/'vm',vm.manager.profile,root/'gate');vm.manager=m
 fake=root/'fixture-base';fake.write_bytes(b'fixture')
 def check(name,value):
  assert value,name
  checks.append(name)
 def item(name):
  def visit(x):
   if x.objectName()==name and x.isVisible():return x
   for ch in x.childItems():
    found=visit(ch)
    if found is not None:return found
  found=visit(w.contentItem());assert found is not None,name;return found
 def wait():
  end=time.monotonic()+8
  while vm.view['busy'] and time.monotonic()<end:QTest.qWait(20)
  assert not vm.view['busy'];assert not vm.view['error'],vm.view['error']
 def press(name):
  x=item(name);x.forceActiveFocus(Qt.TabFocusReason);QTest.keyClick(w,Qt.Key_Return);QTest.qWait(100)
 try:
  check('window exposed',QTest.qWaitForWindowExposed(w,5000));check('scale',abs(w.devicePixelRatio()-a.scale)<.01)
  check('native platform' if a.native else 'offscreen platform',app.platformName()==('wayland' if a.native else 'offscreen'))
  check('core startup does not create VM store',not (root/'vm').exists())
  for size in ((800,600),(1280,900)):
   w.resize(*size);QTest.qWait(100);sizes.append({'requested':size,'actual':[w.width(),w.height()]});press('vmPreviewButton');wait()
   check('backup exclusion visible', 'NOT included' in item('vmBackupWarning').property('text'))
   check('footer remains inside window',item('vmClose').mapToScene(QPointF(0,0)).y()+item('vmClose').height()<=w.height())
   check('fresh Start label',item('vmStart').property('text')=='Start')
   w.grabWindow().save(str(out/f'ui-{app.platformName()}-{a.scale}-{size[0]}.png'));press('vmClose')
   check('focus returns to entry',item('vmPreviewButton').hasActiveFocus())
  with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda root:os.open(fake,os.O_RDONLY)):
   m.reset(confirmed=True);press('vmPreviewButton');wait();check('Learn command guidance',item('vmCommand').property('text')=='sleep 300 &')
   press('vmNext');wait();check('next guidance',item('vmCommand').property('text')=='jobs -l')
   press('vmReset');QTest.keyClick(w,Qt.Key_Escape);QTest.qWait(100);check('cancel Reset preserves progress',m.status()['session']['step']==1)
   vm.progress('complete');wait();check('self-review no score',vm.view['session']['completion']['kind']=='self-reviewed' and 'score' not in vm.view['session'])
   b.flush();backup=snapshot(root/'data',root/'config',lock.locks)
   check('backup excludes VM data',not any('vm' in k for k in backup.files));write_backup(backup,root/'saved.llbackup');restored=read_backup(root/'saved.llbackup');restore(restored,root/'restored',confirmed=True)
   check('backup version unchanged',restored.manifest['schema_version'] in (1,2))
   reopened=Manager(root/'vm',m.profile,root/'gate');check('same VM completion reopens',reopened.status()['session']==m.status()['session'])
   vm.reset('Challenge',True);wait();check('Challenge no guidance',vm.view['session']['mode']=='Challenge')
   try:item('vmCommand');raise AssertionError('Challenge exposed guidance')
   except AssertionError as e:assert str(e)=='vmCommand'
   check('Challenge fresh completion',vm.view['session']['completion'] is None);press('vmClose')
  check('no QML warnings: '+repr(messages),not messages)
 finally:
  w.close();app.processEvents();lock.unlock()
 report={'checks':checks,'sizes':sizes,'platform':app.platformName(),'scale':a.scale,'qml_messages':messages,'input':'QtTest synthesized, not physical-keyboard/accessibility acceptance'}
 (out/f'ui-{app.platformName()}-{a.scale}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
