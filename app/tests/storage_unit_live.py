"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from storage_guest_fixtures import COMMANDS,UNIT,CLEANUP
from guest_screen import marker as acknowledgement,matches,locate_calibration,vi_ready,nano_ready
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process,verify_launch
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
assert a.vm_home.is_absolute() and a.vm_home.parent.is_dir() and not a.vm_home.parent.is_symlink() and a.vm_home.parent.stat().st_uid==os.getuid(), 'Owned persistent evidence parent required'
out=Path(tempfile.mkdtemp(prefix='storage-unit-live-',dir=a.vm_home.parent));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name('storage_guest_fixtures.py').read_bytes())
# Reliable host visibility before launch. Never clear or replace coordination to
# make tests pass; every Start acquires the normal shared lifetime lock.
processes=subprocess.run(['ps','-eo','pid,uid,args'],capture_output=True,text=True,check=True).stdout
(out/'host-processes-before.txt').write_text(processes)
assert not any(re.search(r'^\s*\d+\s+\d+\s+\S*qemu-system-x86_64(?:\s|$)',s) for s in processes.splitlines()),'Guest active: native portion blocked; no stop sent'

def record_event(kind,**details):
 with (out/'events.jsonl').open('a') as f:f.write(json.dumps({'at':time.monotonic_ns(),'pid':os.getpid(),'kind':kind,**details})+'\n')
def runtime_event(kind):
 record_event(kind,record=json.loads((active.gate_root/'running.json').read_text()),profile=active.profile,pin=active.pin)
def check(name,condition):
 if not condition:raise AssertionError(name)
 checks.append(name);print(name,flush=True)
def qmp(command,args=None):
 r=json.loads((active.gate_root/'running.json').read_text())
 assert r['state']=='running' and r['profile']==active.profile and r['store']==active.binding and same_process(r),'Not our verified guest; no developer control sent'
 verify_launch(r,str(active.gate_root/r['run']/'qmp'))
 with socket.socket(socket.AF_UNIX) as sock:
  sock.settimeout(5);sock.connect(str(active.gate_root/r['run']/'qmp'));f=sock.makefile('rwb');f.readline()
  def op(c,args):
   f.write((json.dumps({'execute':c,'arguments':args or {}})+'\n').encode());f.flush()
   while True:
    raw=f.readline();assert raw,'QMP ended'
    v=json.loads(raw)
    if 'error' in v:raise AssertionError(v)
    if 'return' in v:return v['return']
  op('qmp_capabilities',{});return op(command,args)
def key(k):
 qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});time.sleep(.06)
 qmp('input-send-event',{'events':[{'type':'key','data':{'down':False,'key':{'type':'qcode','data':c}}} for c in ('ctrl','ctrl_r','shift','shift_r','alt','alt_r')]});time.sleep(.02)
def text(t):
 basic={' ':'spc','-':'minus','=':'equal','/':'slash','.':'dot',',':'comma',"'":'apostrophe',';':'semicolon','[':'bracket_left',']':'bracket_right','\\':'backslash','`':'grave_accent'}
 shifted={'!':'1','@':'2','#':'3','$':'4','%':'5','^':'6','&':'7','*':'8','(':'9',')':'0','_':'minus','+':'equal',':':'semicolon','"':'apostrophe','<':'comma','>':'dot','?':'slash','|':'backslash','~':'grave_accent','{':'bracket_left','}':'bracket_right'}
 for c in t:
  k=('shift-'+c.lower() if c.isupper() else c) if c.isascii() and c.isalnum() else basic[c] if c in basic else 'shift-'+shifted[c]
  qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});time.sleep(.012)
command_sequence=0
glyphs=None
def ocr_until(label,predicate,seconds=30,header=False):
 deadline=time.monotonic()+seconds
 while True:
  path=shot(label);ocr_path=path
  if header:
   from PySide6.QtGui import QImage
   im=QImage(str(path));ocr_path=out/(label+'-header.png');assert im.copy(0,0,im.width(),16).scaled(im.width()*2,32).save(str(ocr_path))
  elif label.startswith('command-'):
   from PySide6.QtGui import QImage
   from PySide6.QtCore import Qt
   im=QImage(str(path));im.invertPixels();im=im.scaled(im.width()*3,im.height()*3,Qt.IgnoreAspectRatio,Qt.FastTransformation)
   ocr_path=out/(label+'-ocr.png');assert im.save(str(ocr_path))
  value=subprocess.run(['/usr/bin/tesseract',str(ocr_path),'stdout','--psm','7' if header else '6'],capture_output=True,text=True,check=True).stdout
  (out/(path.name+'.txt')).write_text(value)
  if predicate(value):return
  assert time.monotonic()<deadline,'Guest readiness/completion timeout: '+label
  time.sleep(.1)
def boot_ready():
 global glyphs
 runtime_event('running')
 ocr_until('boot-ready-'+uuid.uuid4().hex[:8],lambda value:re.search(r'learner@[^\n]*[$]',value) is not None,90)
 key('ctrl-u');text("printf '\\nPASSED\\n'");key('ret');deadline=time.monotonic()+15
 label='font-calibration-'+uuid.uuid4().hex[:8]
 while True:
  path=shot(label);tsv=subprocess.run(['/usr/bin/tesseract',str(path),'stdout','--psm','6','tsv'],capture_output=True,text=True,check=True).stdout
  (out/(label+'.tsv')).write_text(tsv)
  try:glyphs=locate_calibration(str(path),tsv);break
  except ValueError:assert time.monotonic()<deadline,'Guest font calibration failed';time.sleep(.1)
 record_event('font-calibrated',image=str(path),glyphs={k:[v.hex() for v in rows] for k,rows in glyphs.items()})
def await_ack(label,expected):
 deadline=time.monotonic()+120
 while True:
  path=shot(label)
  if matches(str(path),expected,glyphs):
   record_event('command-complete',label=label,marker=expected,screenshot=str(path));return
  assert time.monotonic()<deadline,'Exact guest acknowledgement absent: '+label
  time.sleep(.1)

def line(t,delay=.45):
 global command_sequence
 command_sequence+=1;label='command-'+str(command_sequence).zfill(4)
 record_event('guest-command',sequence=command_sequence,command=t)
 interactive=t=='vi note.txt' or t.endswith('; vi note.txt') or t.startswith('nano ') or t.endswith('; nano report.sh')
 marker=acknowledgement(command_sequence)
 text_to_send=t if interactive else "if { "+t+"; }; then printf '\\n"+marker+"\\n'; else echo STORAGE_COMMAND_FAILED; fi"
 key('ctrl-u');text(text_to_send);key('ret')
 if interactive:
  if 'nano ' in t:ocr_until(label,lambda v:nano_ready(v,t.rsplit('nano ',1)[1]),header=True)
  else:ocr_until(label,vi_ready)
 else:await_ack(label,marker)
def shot(name):
 path=out/(name+'.png');qmp('screendump',{'filename':str(path),'format':'png'});return path
def read_marker(name,marker):
 for attempt in range(3):
  key('ctrl-q');line('clear');line('if [ -s ~/backup-fixture-failures ] || [ \"$(wc -l < ~/backup-fixture-successes)\" -ne '+str(assertion_count)+' ]; then echo FAILED; cat ~/backup-fixture-failures; else echo '+marker+'; fi')
  path=shot(name+'-'+str(attempt));ocr=subprocess.run(['/usr/bin/tesseract',str(path),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout;(out/(path.name+'.txt')).write_text(ocr)
  if re.search(r'(?m)^'+marker+r'\s*$',ocr):return path.name
  if re.search(r'(?m)^FAILED\s*$',ocr):raise AssertionError('Guest assertion failure: '+ocr)
 raise AssertionError('Unreadable guest evidence, not PASS: '+str(out))
assertion_count=0
def assertion(command,label):
 global assertion_count
 assertion_count+=1
 line(command+' && echo '+label+' >> ~/backup-fixture-successes || echo '+label+' >> ~/backup-fixture-failures')




def assert_guest(command,label):
 record_event('independent-assertion',label=label,command=command)
 line(command);check(label,True)

def verify(n):
 if n==1:return
 assert_guest('guard && test "$(stat -c %s disk.img)" = 134217728 && test "$(df -Pk . | awk \'NR==2 {print $4}\')" -ge 1048576','bounded image and reserve')
 # Independent refusal checks after cleanup: no stale device must become valid.
 assert_guest('! dev_ok /dev/vda1 disk.img && ! dev_ok /dev/loop999p1 disk.img && test -z "$(sudo losetup -j "$w/disk.img")"','system foreign and stale mapping refusals')
 assert_guest('before=$(sha256sum disk.img); ! (set -o noclobber; : > disk.img) && test "$(sha256sum disk.img)" = "$before"','image collision refusal preserves bytes')
 assert_guest('mv disk.img held.img && ln -s /dev/vda disk.img && ! file_ok disk.img && rm -- disk.img && mv held.img disk.img && ln disk.img hardlink && ! file_ok disk.img && rm -- hardlink && file_ok disk.img','symlink and hardlink substitution refused')
 assert_guest('test "$(find . -maxdepth 1 -type f -name \'*.img\' | wc -l)" -le 2','two-image aggregate exercise bound')
 if n in (7,8):assert_guest('sha256sum -c original.sha256 && test "$(stat -c %s repair.img)" = 134217728 && test "$(cat expected.txt)" = "Storage practice: known content."','retained original and independent expectation')
 if n==6:assert_guest('sudo sha256sum -c live-fstab.sha256','live fstab unchanged')
 assert_guest('test ! -e output-bound.log && (ulimit -f 8; timeout -k 1s 2s head -c 65536 /dev/zero > output-bound.log); rc=$?; test "$rc" -ne 0 && test "$(stat -c %s output-bound.log)" -le 8192 && rm -- output-bound.log','real per-file output bound')
 assert_guest('timeout -k 1s 1s sleep 3; rc=$?; test "$rc" = 124 && guard','interrupted bounded worker and reserve intact')

for id,commands in COMMANDS.items():
 if a.only and id!=a.only:continue
 if a.from_lesson and list(COMMANDS).index(id)<list(COMMANDS).index(a.from_lesson):continue
 n=list(COMMANDS).index(id)+1
 for mode in a.modes:
  active=sessions.manager(id);running=False;started=time.monotonic();info={'id':id,'mode':mode}
  try:
   saved=active.reset(mode,True);active.start(mode);running=True;boot_ready()
   sessions.select(LEGACY_ID);check(id+' running controls accessible',sessions.view(LEGACY_ID)['running_lesson_id']==id)
   foreign=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest()).manager(id)
   try:foreign.start();raise AssertionError('Foreign VM started')
   except Refused as exc:check(id+' cross-profile refusal','already running' in str(exc))
   assert_guest('test "$(id -un)" = learner && test "$(sudo id -u)" = 0 && test "$(cat /usr/local/share/learning-lab/image-id)" = debian13-admin-local-v1 && test "$(ip -o link show | wc -l)" = 1 && test "$(ss -lntu | wc -l)" = 1','exact unchanged image guest-root policy offline')
   # Both modes perform actual guest practice. Challenge uses an independent
   # outcome checklist, not automatic assessment or one required transcript.
   for i,c in enumerate(commands):
    line(c)
    if n>=4 and i==6 and n!=6:
     assert_guest('dev_ok "$part" disk.img && mounted "$part" && ! off "$part" disk.img && ! target_ok','mounted offline-check and occupied mountpoint refusal')
    if n in (7,8) and 'COPY_PRESERVED' in c:pass
   verify(n)
   line(CLEANUP[n]);assert_guest('test ! -e /home/learner/ll-storage-'+str(n),'exact cleanup')
   assert_guest('test ! -e /home/learner/ll-storage-'+str(n),'repeated cleanup already absent')
   line(commands[0]);assert_guest('guard() { test "$(pwd -P)" = "$w"; }; guard','repeated setup after cleanup')
   line('rmdir -- mnt && cd -- /home/learner && rmdir -- "$w"')
   if mode=='Learn':active.progress('next');active.progress('hint')
   else:
    for op in ('next','hint'):
     try:active.progress(op);raise AssertionError('Challenge solution exposed')
     except Refused:pass
   active.progress('complete');record=active.status()['session'];check(id+' '+mode+' self-reviewed unscored',record['completion']['kind']=='self-reviewed' and 'score' not in record)
   check(id+' '+mode+' clean Stop',active.stop()=='Cleanly stopped');running=False;runtime_event('clean-stop')
   check(id+' '+mode+' reopened exact session',Sessions(a.vm_home,sessions.profile).manager(id).status()['session']==record)
   with active.access() as (root,g,p):
    fd=active.image(root)
    try:check(id+' '+mode+' base hash unchanged',sha256(fd)==active.spec['sha256'])
    finally:os.close(fd)
   info.update(result='PASS',pin=saved['pin'],session=saved['session'],generation=saved['generation'],seconds=round(time.monotonic()-started,2))
  finally:
   if running:
    try:info['failure_cleanup']=active.stop()
    except Exception as exc:info['failure_cleanup']='BLOCKED: '+str(exc)
   report['lessons'].append(info);report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Evidence',out,flush=True)
