"""Explicit native developer proof. Requires registered image; isolated app profile.
Never imported by the app. Guest keys are fixed fixtures, not lesson/learner input.
"""
import argparse,hashlib,json,os,socket,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt,qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.vm_preview.files import sha256
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);a=p.parse_args()
root=Path(tempfile.mkdtemp(prefix='learning-lab-vm-live-'));out=Path('/tmp/learning-lab-vm-preview-evidence');out.mkdir(exist_ok=True)
messages=[];qInstallMessageHandler(lambda t,c,m:messages.append(m))
app,engine,b,lock=build_application(root/'data',root/'config',a.vm_home);w=engine.rootObjects()[0];vm=b.vm_preview;checks=[]
def check(n,v):
 assert v,n
 checks.append(n);print(n,flush=True)
def wait():
 deadline=time.monotonic()+240
 while vm.view['busy'] and time.monotonic()<deadline:
  QTest.qWait(5);time.sleep(.05)
 check('operation completed',not vm.view['busy']);check('no controller error: '+vm.view['error'],not vm.view['error'])
def item(name):
 def visit(x):
  if x.objectName()==name and x.isVisible():return x
  for y in x.childItems():
   f=visit(y)
   if f is not None:return f
 f=visit(w.contentItem());assert f is not None,name;return f
def press(name):
 w.requestActivate();item(name).forceActiveFocus(Qt.TabFocusReason);QTest.keyClick(w,Qt.Key_Return);QTest.qWait(150);wait()
def qmp(command,arguments=None):
 r=json.loads((vm.manager.gate_root/'running.json').read_text())
 with socket.socket(socket.AF_UNIX) as sock:
  sock.settimeout(3);sock.connect(str(vm.manager.gate_root/r['run']/'qmp'));f=sock.makefile('rwb');f.readline()
  def op(c,a):
   f.write((json.dumps({'execute':c,'arguments':a or {}})+'\n').encode());f.flush()
   while True:
    line=f.readline()
    if not line:return None
    v=json.loads(line)
    if 'error' in v:raise AssertionError(v)
    if 'return' in v:return v['return']
  op('qmp_capabilities',{});return op(command,arguments)
def guest_fixture():
 # Fixed developer fixture only. No general command endpoint in runtime.
 text="echo NATIVE_PREVIEW_OK; id; ls /sys/class/net; sleep 300 &"
 basic={' ':'spc',';':'semicolon','/':'slash','&':'shift-7','_':'shift-minus'}
 for c in text:
  key=basic.get(c,('shift-'+c.lower()) if c.isupper() else c)
  qmp('human-monitor-command',{'command-line':'sendkey '+key+' 1'});QTest.qWait(30)
 qmp('human-monitor-command',{'command-line':'sendkey ret 1'});QTest.qWait(300)
try:
 check('native Wayland',app.platformName()=='wayland');check('window exposed',QTest.qWaitForWindowExposed(w,5000))
 press('vmPreviewButton');press('vmStart');check('real guest running',vm.view['state']=='running');QTest.qWait(8000)
 guest_fixture();qmp('screendump',{'filename':str(out/'07-integrated-native-guest.png'),'format':'png'})
 w.grabWindow().save(str(out/'08-native-app-controls.png'))
 press('vmNext');check('guidance state',vm.view['session']['step']==1)
 vm.progress('complete');wait();check('self-review stored without score',vm.view['session']['completion']['kind']=='self-reviewed')
 press('vmStop');check('clean Stop',vm.view['state']=='stopped')
 first=vm.view['session'];press('vmStart');check('Resume same generation',vm.view['session']['generation']==first['generation'])
 # Simulate process exit without controller shutdown publication. Do not kill a PID.
 qmp('quit');QTest.qWait(500);vm.refresh();wait();check('crash classified unclean',vm.view['state']=='unclean')
 path=a.vm_home/'profiles'/vm.manager.profile/'generations'/first['generation']/'disk.qcow2';digest=hashlib.sha256(path.read_bytes()).hexdigest()
 try:vm.manager.start();raise AssertionError('unclean Resume permitted')
 except ValueError as exc:check('unclean Resume blocked','Unclean' in str(exc))
 vm.reset('Challenge',True);wait();check('Reset retained crash disk',hashlib.sha256(path.read_bytes()).hexdigest()==digest)
 check('Challenge new session',vm.view['session']['mode']=='Challenge' and vm.view['session']['completion'] is None)
 with vm.manager.access() as (r,g,p):
  fd=vm.manager.image(r);check('base hash unchanged',sha256(fd)==vm.manager.spec['sha256']);os.close(fd)
 check('no QML errors',not messages)
finally:
 if vm.view['state']=='running':vm.stop();wait()
 w.close();app.processEvents();lock.unlock()
report={'checks':checks,'profile':str(root),'vm_profile_key':vm.manager.profile,'platform':app.platformName(),'qml_messages':messages,'input':'Native rendering + QtTest/QMP synthesized keys; physical input unverified'}
(out/'native-live.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
