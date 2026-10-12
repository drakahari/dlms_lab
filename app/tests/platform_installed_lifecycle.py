"""Actual native app/GTK routing proof, disposable profile; retains all disks."""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
def disk_sha256(path):
 with path.open('rb') as stream:
  return hashlib.file_digest(stream,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True)
p.add_argument('--lesson',choices=('real-linux-foundation-encoding','real-linux-rpm-inventory'),required=True)
p.add_argument('--installed',action='store_true',help='Use the isolated wheel package, never insert the checkout')
p.add_argument('--smoke-phase',choices=('start','resume','reset'))
p.add_argument('--profile',type=Path,help='Same disposable temporary profile for installed phases; TMPDIR is supported')
a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if a.smoke_phase:
 temp_root=Path(tempfile.gettempdir()).resolve()
 assert a.installed and a.profile and a.profile.is_absolute() and a.profile.resolve().is_relative_to(temp_root)
 assert a.profile.resolve()!=temp_root, 'Use a dedicated disposable child profile'
 assert not a.profile.is_symlink()
from PySide6.QtCore import Qt,QPointF,qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.vm_preview.registry import catalog,LEGACY_ID,entries,units,session_binding,unit_for_lesson
from learning_lab.vm_preview.process import same_process,verify_launch
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.files import Refused
out=a.profile if a.smoke_phase else Path(tempfile.mkdtemp(prefix='vm-lessons-switch-live-'))
out.mkdir(exist_ok=True);evidence=out/('run-'+str(os.getpid())+'-'+uuid.uuid4().hex[:8]);evidence.mkdir();messages=[];checks=[];diagnostic_phase='live'
def capture_qt_message(kind,context,message):
 messages.append(message)
 # Retain exact diagnostics even when a later assertion aborts the run.
 with (evidence/'qt-messages.jsonl').open('a') as trace:
  trace.write(json.dumps({'phase':diagnostic_phase,'at':time.monotonic_ns(),'type':str(kind),'message':message,'file':context.file or '', 'line':context.line, 'category':context.category or ''})+'\n')
qInstallMessageHandler(capture_qt_message)
app,engine,b,lock=build_application(out/'data',out/'config',a.vm_home);w=engine.rootObjects()[0];vm=b.vm_preview;ids=[e['id'] for e in catalog()['entries']]
events=[]
def event(kind,**details):
 value={'at':time.monotonic_ns(),'pid':os.getpid(),'event':kind,**details};events.append(value)
 with (evidence/'events.jsonl').open('a') as f:f.write(json.dumps(value)+'\n')
vm.finished.connect(lambda result:event('operation-finished',result=result))
def ready(predicate,label,seconds=240):
 deadline=time.monotonic()+seconds
 while not predicate():
  assert time.monotonic()<deadline,label+' readiness timeout'
  QTest.qWait(5);time.sleep(.05) # Yield the GIL for image hashing; readiness stays predicate-driven.
def check(n,c):
 assert c,n;checks.append(n);print(n,flush=True)
def wait(error=False):
 ready(lambda:not vm.view['busy'] and vm._pending is None,'VM operation')
 if not error:assert not vm.view['error'],vm.view['error']
def item(name):
 def visit(x):
  if x.objectName()==name and x.isVisible():return x
  for child in x.childItems():
   v=visit(child)
   if v is not None:return v
 v=visit(w.contentItem());assert v is not None,name;return v
def press(name):
 # An expected failed Start leaves a visible error until the next operation.
 # It must not prevent exercising the still-enabled Return/Stop controls.
 wait(True);w.requestActivate()
 if a.smoke_phase:
  # Wait for native activation before choosing focus. Space activates the exact
  # Button instead of a restored dialog default; this is synthesized input.
  assert QTest.qWaitForWindowActive(w,5000), 'Native Lab activation unavailable'
  ready(lambda:w.isActive() and not vm.view['busy'] and vm._pending is None and item(name).isEnabled(),name)
  x=item(name);x.forceActiveFocus(Qt.TabFocusReason)
  # Do not yield after choosing focus: refresh may disable the button.
  event('input-ready',target=name,active=w.isActive(),busy=vm.view['busy'],enabled=x.isEnabled(),focused=x.hasActiveFocus())
  assert x.hasActiveFocus(),name+' focus'
  (evidence/(a.smoke_phase+'-'+name+'-before.json')).write_text(json.dumps({'target':name,'window':[w.width(),w.height()],'focus':w.activeFocusItem().objectName(),'state':vm.view['state'],'running':vm.view['running_lesson_id'],'error':vm.view['error']}))
  activated=[]
  def record_activation():
   activated.append(name)
   with (evidence/(a.smoke_phase+'-activations.jsonl')).open('a') as trace:trace.write(json.dumps({'target':name,'state':vm.view['state'],'error':vm.view['error']})+'\n')
  x.clicked.connect(record_activation)
  if name=='vmStop':
   # Lifecycle proof uses a targeted pointer click; keyboard acceptance is
   # separately reported, not inferred from successful shutdown.
   center=x.mapToScene(QPointF(x.width()/2,x.height()/2)).toPoint()
   QTest.mouseClick(w,Qt.LeftButton,Qt.NoModifier,center)
  else:QTest.keyClick(w,Qt.Key_Space)
  x.clicked.disconnect(record_activation)
  assert activated==[name],name+' exact activation'
 else:
  item(name).forceActiveFocus(Qt.TabFocusReason);QTest.keyClick(w,Qt.Key_Return)
 wait()
def select(id):wait();vm.selectLesson(id);wait();check('selection applied '+id,vm.view['selected_lesson_id']==id)
def installed_smoke():
 # Fixed developer input only: these operations are not runtime QMP operations,
 # imported lesson actions, or application guest assessment.
 import learning_lab
 package=Path(learning_lab.__file__).resolve().parent
 check('isolated installed package',package.is_relative_to(Path(sys.prefix)) and 'site-packages' in package.parts)
 from learning_lab.vm_preview.registry import MAX_UNITS,MAX_TOTAL_LESSONS
 check('installed bounded registry',len(units())==MAX_UNITS and len(entries())==MAX_TOTAL_LESSONS)
 check('original unit still eight',len(catalog()['entries'])==8)
 check('accepted lesson bytes',hashlib.sha256((package/'vm_preview/lesson.json').read_bytes()).hexdigest()=='246f12b80f72fff3fae2a6484de185706c90dedf6ecd68f92417aea2ff6881da')
 check('native exposed',app.platformName()=='wayland' and QTest.qWaitForWindowExposed(w,5000))
 press('vmPreviewButton');select(a.lesson);m=vm.manager
 binding=hashlib.sha256((str((out/'data').absolute())+'\0'+str((out/'config').absolute())).encode()).hexdigest()
 check('exact session binding',m.profile==session_binding(binding,a.lesson))
 if a.lesson==LEGACY_ID:check('accepted canonical pin',m.pin['lesson_sha256']=='cc71a87e9cc21224b84803a4175dffdfd83da793700402e20ffe3515eeb59180')
 else:check('selected lesson and unit match',vm.view['unit']['id']==unit_for_lesson(a.lesson)['id'] and m.lesson['id']==a.lesson)
 expected=out/'expected-session.json'
 if a.smoke_phase=='start':check('fresh fixture',not expected.exists() and vm.view['session'] is None)
 else:
  saved=json.loads(expected.read_text());check('application restart preserved session',vm.view['session']==saved)
  check('clean disk Resume available',vm.view['state']=='stopped' and item('vmStart').property('text')=='Resume disk')
 if a.smoke_phase=='reset':
  retained=a.vm_home/'profiles'/m.profile/'generations'/saved['generation']/'disk.qcow2'
  retained_hash=disk_sha256(retained);old_saved=saved
  event('confirmed-reset',old_session=saved)
  vm.reset('Learn',True);wait();saved=vm.view['session']
  check('Reset unique generation exact pins',saved['generation']!=old_saved['generation'] and saved['pin']==old_saved['pin'])
  check('Reset retained bytes',disk_sha256(retained)==retained_hash)
  (out/'expected-reset-session.json').write_text(json.dumps(saved,indent=2))
 press('vmStart');wait();check('GTK guest running',vm.view['running_lesson_id']==a.lesson)
 event('running-identity',record=json.loads((m.gate_root/'running.json').read_text()),session=vm.view['session'])
 if a.lesson!=LEGACY_ID:
  select(LEGACY_ID)
  check('installed cross-unit running controls',item('vmStop').isEnabled() and item('vmReturnRunning').isVisible() and not item('vmStart').isEnabled())
  press('vmReturnRunning');check('installed Return selects chosen lesson',vm.view['selected_lesson_id']==a.lesson)
  foreign=Sessions(a.vm_home,hashlib.sha256((str(out)+'-foreign').encode()).hexdigest()).manager(LEGACY_ID)
  try:foreign.start();raise AssertionError('Cross-profile second VM started')
  except Refused as exc:
   check('installed real cross-profile exclusion','already running' in str(exc));event('expected-foreign-start-refusal',foreign_profile=foreign.profile,error=str(exc),record=json.loads((m.gate_root/'running.json').read_text()))
 def qmp(c,args=None):
  r=json.loads((m.gate_root/'running.json').read_text())
  assert r['state']=='running' and r['profile']==m.profile and r['store']==m.binding and same_process(r), 'Not our verified fixture guest'
  verify_launch(r,str(m.gate_root/r['run']/'qmp'))
  with socket.socket(socket.AF_UNIX) as sock:
   sock.settimeout(5);sock.connect(str(m.gate_root/r['run']/'qmp'));f=sock.makefile('rwb');f.readline()
   def op(cmd,arguments):
    f.write((json.dumps({'execute':cmd,'arguments':arguments or {}})+'\n').encode());f.flush()
    while True:
     v=json.loads(f.readline())
     if 'error' in v:raise AssertionError(v)
     if 'return' in v:return v['return']
   op('qmp_capabilities',{});return op(c,args)
 def key(k):
  qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});QTest.qWait(150)
  qmp('input-send-event',{'events':[{'type':'key','data':{'down':False,'key':{'type':'qcode','data':code}}} for code in ('ctrl','ctrl_r','shift','shift_r','alt','alt_r')]});QTest.qWait(50)
 def screen(label):
  path=evidence/(label+'.png');qmp('screendump',{'filename':str(path),'format':'png'})
  ocr_path=path
  if label.startswith('command-'):
   from PySide6.QtGui import QImage
   im=QImage(str(path));im.invertPixels();im=im.scaled(im.width()*3,im.height()*3,Qt.IgnoreAspectRatio,Qt.FastTransformation)
   ocr_path=evidence/(label+'-ocr.png');assert im.save(str(ocr_path))
  value=subprocess.run(['/usr/bin/tesseract',str(ocr_path),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout
  (evidence/(label+'.txt')).write_text(value);return value
 def guest_ready():
  return re.search(r'learner@[^\n]*[$]',screen('boot-ready')) is not None
 ready(guest_ready,'guest console prompt',90);event('guest-prompt-ready')
 sequence=0
 def line(t):
  nonlocal sequence
  sequence+=1;marker='READY'+''.join('ABCDEFGHJKMNPQRSTUVWXYZ'[(sequence//(22**i))%22] for i in (2,1,0))
  event('guest-command',sequence=sequence,command=t)
  # Readiness proves the fixed command returned success, not merely that the
  # shell printed a marker after a failed setup. Sentinel-based assertions still
  # independently verify contents across separate application processes.
  t="if { "+t+"; }; then printf '\\n"+marker+"\\n'; else printf '\\nLOCAL_COMMAND_FAILED\\n'; fi"

  basic={' ':'spc','-':'minus','=':'equal','/':'slash','.':'dot',',':'comma',"'":'apostrophe',';':'semicolon','[':'bracket_left',']':'bracket_right','\\':'backslash','`':'grave_accent'}
  shifted={'!':'1','@':'2','#':'3','$':'4','%':'5','^':'6','&':'7','*':'8','(':'9',')':'0','_':'minus','+':'equal',':':'semicolon','"':'apostrophe','<':'comma','>':'dot','?':'slash','|':'backslash','~':'grave_accent','{':'bracket_left','}':'bracket_right'}
  key('ctrl-u')
  for c in t:
   k=('shift-'+c.lower() if c.isupper() else c) if c.isascii() and c.isalnum() else basic[c] if c in basic else 'shift-'+shifted[c]
   qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});QTest.qWait(50)
  key('ret')
  ready(lambda:re.search(r'(?m)^'+marker+r'\s*$',screen('command-'+str(sequence))) is not None,'guest command '+str(sequence),30)
 commands=[]
 from learning_lab.vm_preview.image_catalog import production_catalog,digest
 spec,content=production_catalog().defaults(a.lesson)
 wanted='debian13-foundation-admin-local-v1' if a.lesson.startswith('real-linux-foundation-') else 'almalinux9-rpm-admin-local-v1'
 check('exact new lesson/image pins',m.spec==spec and spec['image_id']==wanted and m.pin['lesson_sha256']==digest(content))
 if a.smoke_phase=='start':
  commands=['test ! -e ~/fixture-failures && test ! -L ~/fixture-failures && (umask 077; : > ~/fixture-failures)',
   'work=$(mktemp -d "$HOME/platform-installed.XXXXXX") && cd "$work" && umask 077',
   'printf "caf\\303\\251\\n" > original.txt && printf "wheel-smoke-marker\\n" > marker.txt',
   'sha256sum original.txt marker.txt > expected.sha',
   'printf "%s\\n" "$work" > ~/installed-platform-workspace']
  if a.lesson.startswith('real-linux-foundation-'):
   commands+=['locale -a > locales.txt && grep -Fx de_DE.utf8 locales.txt && timeout -k 1s 10s iconv -f UTF-8 -t ISO-8859-1 original.txt > latin1.txt && timeout -k 1s 10s iconv -f ISO-8859-1 -t UTF-8 latin1.txt > roundtrip.txt && cmp original.txt roundtrip.txt || echo ENCODING_FAIL >> ~/fixture-failures']
  else:
   commands+=['sudo /usr/local/sbin/ll-rpm-fixture status > packages-before.json && grep -F \'"fixtures": {}\' packages-before.json && rpm -qf /usr/bin/sh --qf \'%{NAME}\\n\' > provider.txt && grep -Fx bash provider.txt || echo RPM_FAIL >> ~/fixture-failures']
 elif a.smoke_phase=='resume':
  check('same pinned generation',vm.view['session']==saved)
  commands=['test -f ~/installed-platform-workspace && test ! -L ~/installed-platform-workspace && work=$(cat ~/installed-platform-workspace) && cd "$work" && sha256sum -c expected.sha && grep -Fx wheel-smoke-marker marker.txt || echo SAME_DISK_FAIL >> ~/fixture-failures']
  if a.lesson.startswith('real-linux-foundation-'):
   commands+=['cmp original.txt roundtrip.txt || echo ENCODING_RESUME_FAIL >> ~/fixture-failures']
  else:
   commands+=['sudo /usr/local/sbin/ll-rpm-fixture status > packages-after.json && cmp packages-before.json packages-after.json || echo RPM_RESUME_FAIL >> ~/fixture-failures']
 else:
  commands=['test ! -e ~/fixture-failures && test ! -L ~/fixture-failures && (umask 077; : > ~/fixture-failures)',
   'test ! -e ~/installed-platform-workspace && test ! -L ~/installed-platform-workspace || echo RESET_FAIL >> ~/fixture-failures']
 for c in commands:line(c)
 if a.lesson=='real-linux-admin-change':
  line('sudo -n id -u | grep -qx 0 || echo ADMIN_FAIL >> ~/fixture-failures')
 # The frozen Alma minimal image has ncurses libraries but no clear utility.
 # This static developer display operation uses the existing shell/VT console;
 # it is not a new lesson command or an image/package substitution.
 key('ctrl-q');line("printf '\\033[2J\\033[H'");line('if test -f ~/fixture-failures && test ! -L ~/fixture-failures && test "$(stat -c %U:%a:%h ~/fixture-failures)" = learner:600:1 && test ! -s ~/fixture-failures; then echo PASSED; else echo FAILED; fi')
 screenshot=evidence/(a.smoke_phase+'-guest.png');qmp('screendump',{'filename':str(screenshot),'format':'png'})
 text=subprocess.run(['/usr/bin/tesseract',str(screenshot),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout
 (evidence/(a.smoke_phase+'-guest.txt')).write_text(text)
 check('guest assertions passed',re.search(r'(?m)^PASSED\s*$',text) is not None)
 if a.smoke_phase=='start':vm.progress('next');wait();vm.progress('complete');wait()
 press('vmStop');check('clean Stop',vm.view['state']=='stopped' and not vm.view['running_lesson_id'])
 event('clean-stop',record=json.loads((m.gate_root/'running.json').read_text()),session=vm.view['session'])
 if a.smoke_phase=='reset':check('retained disk remains unchanged after new guest',disk_sha256(retained)==retained_hash)
 if a.smoke_phase=='start':expected.write_text(json.dumps(vm.view['session'],indent=2))
 else:check('progress and pins retained',vm.view['session']==saved)
 w.grabWindow().save(str(evidence/(a.smoke_phase+'-app.png')))
 # These two exact diagnostics reproduce on the unchanged baseline, including
 # a no-VM open/close probe. Keep them visible; do not ignore other warnings.
 baseline_messages={str((package/'qml/Main.qml').as_uri())+':'+str(n)+':5: QML Dialog: Binding loop detected for property "implicitHeight":\nqrc:/qt-project.org/imports/QtQuick/Controls/Basic/Dialog.qml:16:5' for n in (485,521)}
 baseline_seen=[message for message in messages if message in baseline_messages]
 for message in baseline_seen:print('Retained baseline Qt diagnostic: '+message,flush=True)
 check('no additional live Qt warnings',not [message for message in messages if message not in baseline_messages])
 (evidence/(a.smoke_phase+'-report.json')).write_text(json.dumps({'checks':checks,'package':str(package),'session':vm.view['session'],'baseline_qt_diagnostics':baseline_seen,'live_qt_messages':list(messages),'input':'Synthesized native input; physical keyboard/accessibility unverified'},indent=2))
 print(json.dumps({'phase':a.smoke_phase,'checks':len(checks),'evidence':str(evidence)}),flush=True)
if a.smoke_phase:
 try:installed_smoke()
 except BaseException as exc:
  event('failure',error=repr(exc),view=vm.view);raise
 finally:
  diagnostic_phase='cleanup'
  try:
   vm.refresh();wait(True)
   if vm.view['running_lesson_id']:vm.stop();wait()
  finally:w.close();app.processEvents();lock.unlock()
 sys.exit(0)
try:
 check('native exposed',app.platformName()=='wayland' and QTest.qWaitForWindowExposed(w,5000));press('vmPreviewButton');select(ids[0]);press('vmStart');QTest.qWait(20000);wait()
 first=vm.view['session'];check('first real guest running',vm.view['running_lesson_id']==ids[0]);vm.progress('complete');wait();check('self-review recorded before switch',vm.view['session']['completion']['kind']=='self-reviewed');select(ids[1])
 check('running controls survive selection',item('vmStop').isEnabled() and item('vmReturnRunning').isVisible());check('second Start disabled',not item('vmStart').isEnabled())
 vm.start('Learn');wait(True);check('API second launch refused','already running' in vm.view['error']);check('Stop stays enabled after refusal',item('vmStop').isEnabled())
 w.grabWindow().save(str(out/'running-other-selection.png'));press('vmReturnRunning');check('Return to running lesson',vm.view['selected_lesson_id']==ids[0]);select(ids[1]);press('vmStop');check('Stop targets running guest',not vm.view['running_lesson_id'])
 select(ids[0]);check('self-review stays with original lesson',vm.view['session']['completion']['kind']=='self-reviewed');press('vmStart');QTest.qWait(20000);wait();check('same generation Resume',vm.view['session']['generation']==first['generation'])
 manager=vm.manager;path=a.vm_home/'profiles'/manager.profile/'current.json';path.rename(path.with_name('retained-current.json'))
 select(ids[1]);check('lost running record control-only',vm.view['running_state']=='control-only' and item('vmStop').isEnabled());press('vmStop');check('lost-record guest clean Stop',not vm.view['running_lesson_id'])
 # Restore only this deliberate test fault. No application recovery/migration.
 path.with_name('retained-current.json').rename(path);select(ids[0]);check('restored fixture progress exact',vm.view['session']['session']==first['session'])
 disk=a.vm_home/'profiles'/manager.profile/'generations'/first['generation']/'disk.qcow2';digest=disk_sha256(disk)
 vm.reset('Challenge',True);wait();check('Reset retained prior disk',disk_sha256(disk)==digest);check('fresh Challenge no inherited self-review',vm.view['session']['mode']=='Challenge' and vm.view['session']['completion'] is None)
 w.grabWindow().save(str(out/'challenge-reset.png'));check('no QML warnings',not messages)
finally:
 diagnostic_phase='cleanup'
 try:
  vm.refresh();wait(True)
  if vm.view['running_lesson_id']:vm.stop();wait()
 finally:w.close();app.processEvents();lock.unlock()
report={'checks':checks,'evidence':str(out),'vm_profile':vm.sessions.profile,'qml_messages':messages,'input':'QtTest synthesized native input; no physical keyboard/accessibility claim'}
(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
