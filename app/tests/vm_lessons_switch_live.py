"""Actual native app/GTK routing proof, disposable profile; retains all disks."""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True)
p.add_argument('--lesson', choices=('real-linux-background-job','real-linux-capacity-baseline'), default='real-linux-background-job')
p.add_argument('--installed',action='store_true',help='Use the isolated wheel package, never insert the checkout')
p.add_argument('--smoke-phase',choices=('start','resume'))
p.add_argument('--profile',type=Path,help='Same disposable /tmp profile for separate-process installed phases')
a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if a.smoke_phase:
 assert a.installed and a.profile and a.profile.is_absolute() and a.profile.resolve().is_relative_to('/tmp')
 assert not a.profile.is_symlink()
from PySide6.QtCore import Qt,QPointF,qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.vm_preview.registry import catalog,LEGACY_ID,entries,units,session_binding
from learning_lab.vm_preview.process import same_process
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.files import Refused
out=a.profile if a.smoke_phase else Path(tempfile.mkdtemp(prefix='vm-lessons-switch-live-'))
out.mkdir(exist_ok=True);messages=[];qInstallMessageHandler(lambda t,c,m:messages.append(m));checks=[]
app,engine,b,lock=build_application(out/'data',out/'config',a.vm_home);w=engine.rootObjects()[0];vm=b.vm_preview;ids=[e['id'] for e in catalog()['entries']]
def check(n,c):
 assert c,n;checks.append(n);print(n,flush=True)
def wait(error=False):
 deadline=time.monotonic()+240
 while vm.view['busy'] and time.monotonic()<deadline:QTest.qWait(5);time.sleep(.05)
 assert not vm.view['busy']
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
  wait(True);x=item(name);assert x.isEnabled(),name
  x.forceActiveFocus(Qt.TabFocusReason);QTest.qWait(100)
  assert x.hasActiveFocus(),name+' focus'
  (out/(a.smoke_phase+'-'+name+'-before.json')).write_text(json.dumps({'target':name,'window':[w.width(),w.height()],'focus':w.activeFocusItem().objectName(),'state':vm.view['state'],'running':vm.view['running_lesson_id'],'error':vm.view['error']}))
  QTest.keyClick(w,Qt.Key_Space)
 else:
  item(name).forceActiveFocus(Qt.TabFocusReason);QTest.keyClick(w,Qt.Key_Return)
 QTest.qWait(100);wait()
def select(id):wait();vm.selectLesson(id);wait();check('selection applied '+id,vm.view['selected_lesson_id']==id)
def installed_smoke():
 # Fixed developer input only: these operations are not runtime QMP operations,
 # imported lesson actions, or application guest assessment.
 import learning_lab
 package=Path(learning_lab.__file__).resolve().parent
 check('isolated installed package',package.is_relative_to(Path(sys.prefix)) and 'site-packages' in package.parts)
 check('both installed units and sixteen lessons',len(units())==2 and len(entries())==16)
 check('original unit still eight',len(catalog()['entries'])==8)
 check('accepted lesson bytes',hashlib.sha256((package/'vm_preview/lesson.json').read_bytes()).hexdigest()=='246f12b80f72fff3fae2a6484de185706c90dedf6ecd68f92417aea2ff6881da')
 check('native exposed',app.platformName()=='wayland' and QTest.qWaitForWindowExposed(w,5000))
 press('vmPreviewButton');select(a.lesson);m=vm.manager
 binding=hashlib.sha256((str((out/'data').absolute())+'\0'+str((out/'config').absolute())).encode()).hexdigest()
 check('exact session binding',m.profile==session_binding(binding,a.lesson))
 if a.lesson==LEGACY_ID:check('accepted canonical pin',m.pin['lesson_sha256']=='cc71a87e9cc21224b84803a4175dffdfd83da793700402e20ffe3515eeb59180')
 else:check('capacity baseline selected',vm.view['unit']['id']=='lpic-resource-diagnosis-capacity' and m.lesson['id']==a.lesson)
 expected=out/'expected-session.json'
 if a.smoke_phase=='start':check('fresh fixture',not expected.exists() and vm.view['session'] is None)
 else:
  saved=json.loads(expected.read_text());check('application restart preserved session',vm.view['session']==saved)
  check('clean disk Resume available',vm.view['state']=='stopped' and item('vmStart').property('text')=='Resume disk')
 press('vmStart');QTest.qWait(20000);wait();check('GTK guest running',vm.view['running_lesson_id']==a.lesson)
 if a.lesson!=LEGACY_ID:
  select(LEGACY_ID)
  check('installed cross-unit running controls',item('vmStop').isEnabled() and item('vmReturnRunning').isVisible() and not item('vmStart').isEnabled())
  press('vmReturnRunning');check('installed Return selects capacity lesson',vm.view['selected_lesson_id']==a.lesson)
  foreign=Sessions(a.vm_home,hashlib.sha256((str(out)+'-foreign').encode()).hexdigest()).manager(LEGACY_ID)
  try:foreign.start();raise AssertionError('Cross-profile second VM started')
  except Refused as exc:check('installed real cross-profile exclusion','already running' in str(exc))
 def qmp(c,args=None):
  r=json.loads((m.gate_root/'running.json').read_text())
  assert r['state']=='running' and r['profile']==m.profile and r['store']==m.binding and same_process(r), 'Not our verified fixture guest'
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
 def line(t):
  basic={' ':'spc','-':'minus','=':'equal','/':'slash','.':'dot',',':'comma',"'":'apostrophe',';':'semicolon','[':'bracket_left',']':'bracket_right','\\':'backslash','`':'grave_accent'}
  shifted={'!':'1','@':'2','#':'3','$':'4','%':'5','^':'6','&':'7','*':'8','(':'9',')':'0','_':'minus','+':'equal',':':'semicolon','"':'apostrophe','<':'comma','>':'dot','?':'slash','|':'backslash','~':'grave_accent','{':'bracket_left','}':'bracket_right'}
  key('ctrl-u')
  for c in t:
   k=('shift-'+c.lower() if c.isupper() else c) if c.isascii() and c.isalnum() else basic[c] if c in basic else 'shift-'+shifted[c]
   qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});QTest.qWait(50)
  key('ret');QTest.qWait(800)
 if a.smoke_phase=='start':
  commands=[': > ~/fixture-failures','sleep 300 & p=$!','jobs -l','ps -o pid,ppid,stat,comm -p "$p"','kill -STOP "$p"; sleep 1','test "$(ps -o stat= -p "$p" | cut -c1)" = T || echo STOP_FAIL >> ~/fixture-failures','bg %+','kill "$p"; wait "$p"; test $? = 143 || echo TERM_FAIL >> ~/fixture-failures','printf "wheel-smoke-marker\\n" > ~/installed-wheel-smoke.txt']
 else:
  check('same pinned disk generation',vm.view['session']==saved)
  commands=[': > ~/fixture-failures','test "$(cat ~/installed-wheel-smoke.txt)" = wheel-smoke-marker || echo DISK_FAIL >> ~/fixture-failures','test -z "$(pgrep -u learner -x sleep)" || echo PROCESS_FAIL >> ~/fixture-failures']
 if a.lesson!=LEGACY_ID:
  if a.smoke_phase=='start':commands=[': > ~/fixture-failures','work=$(mktemp -d "$HOME/capacity-installed.XXXXXX"); cd "$work"','{ date -Is; nproc; uptime; free -m; df -Pk .; df -Pi .; } > baseline.txt','grep -q Mem baseline.txt || echo BASELINE_FAIL >> ~/fixture-failures','printf "%s\\n" "$work" > ~/installed-capacity-workspace','printf "wheel-smoke-marker\\n" > ~/installed-wheel-smoke.txt']
  else:commands+=['work=$(cat ~/installed-capacity-workspace); cd "$work"; grep -q Mem baseline.txt || echo BASELINE_RESUME_FAIL >> ~/fixture-failures']
 for c in commands:line(c)
 key('ctrl-q');line('clear');line('if [ -s ~/fixture-failures ]; then echo FAILED; cat ~/fixture-failures; else echo PASSED; fi')
 screenshot=out/(a.smoke_phase+'-guest.png');qmp('screendump',{'filename':str(screenshot),'format':'png'})
 text=subprocess.run(['/usr/bin/tesseract',str(screenshot),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout
 (out/(a.smoke_phase+'-guest.txt')).write_text(text)
 check('guest assertions passed',re.search(r'(?m)^PASSED\s*$',text) is not None)
 if a.smoke_phase=='start':vm.progress('next');wait();vm.progress('complete');wait()
 press('vmStop');check('clean Stop',vm.view['state']=='stopped' and not vm.view['running_lesson_id'])
 if a.smoke_phase=='start':expected.write_text(json.dumps(vm.view['session'],indent=2))
 else:check('progress and pins retained',vm.view['session']==saved)
 w.grabWindow().save(str(out/(a.smoke_phase+'-app.png')))
 check('zero QML warnings',not messages)
 (out/(a.smoke_phase+'-report.json')).write_text(json.dumps({'checks':checks,'package':str(package),'session':vm.view['session'],'input':'Synthesized native input; physical keyboard/accessibility unverified'},indent=2))
 print(json.dumps({'phase':a.smoke_phase,'checks':len(checks),'evidence':str(out)}),flush=True)
if a.smoke_phase:
 try:installed_smoke()
 finally:
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
 disk=a.vm_home/'profiles'/manager.profile/'generations'/first['generation']/'disk.qcow2';digest=hashlib.sha256(disk.read_bytes()).hexdigest()
 vm.reset('Challenge',True);wait();check('Reset retained prior disk',hashlib.sha256(disk.read_bytes()).hexdigest()==digest);check('fresh Challenge no inherited self-review',vm.view['session']['mode']=='Challenge' and vm.view['session']['completion'] is None)
 w.grabWindow().save(str(out/'challenge-reset.png'));check('no QML warnings',not messages)
finally:
 try:
  vm.refresh();wait(True)
  if vm.view['running_lesson_id']:vm.stop();wait()
 finally:w.close();app.processEvents();lock.unlock()
report={'checks':checks,'evidence':str(out),'vm_profile':vm.sessions.profile,'qml_messages':messages,'input':'QtTest synthesized native input; no physical keyboard/accessibility claim'}
(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
