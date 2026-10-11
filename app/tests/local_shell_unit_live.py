"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from local_shell_guest_fixtures import COMMANDS,UNIT,DATA
from guest_screen import marker as acknowledgement,matches,locate_calibration,vi_ready,nano_ready
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process,verify_launch
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
assert a.vm_home.is_absolute() and a.vm_home.parent.is_dir() and not a.vm_home.parent.is_symlink() and a.vm_home.parent.stat().st_uid==os.getuid(), 'Owned persistent evidence parent required'
out=Path(tempfile.mkdtemp(prefix='local-shell-live-',dir=a.vm_home.parent));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name('local_shell_guest_fixtures.py').read_bytes())
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
  qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});time.sleep(.04)
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
 interactive='sensible-editor note.txt' in t
 marker=acknowledgement(command_sequence)
 text_to_send=t if interactive else "if { "+t+"; }; then printf '\\n"+marker+"\\n'; else echo LOCAL_COMMAND_FAILED; fi"
 key('ctrl-u');text(text_to_send);key('ret')
 if interactive:
  # VISUAL=vi is deliberate; EDITOR=nano is the lower-priority alternative.
  ocr_until(label,lambda v:re.search(r'(?m)^"note[.]txt["”]\s+1 line, 9 bytes\s*$',v) is not None)
 else:await_ack(label,marker)
def shot(name):
 path=out/(name+'.png');qmp('screendump',{'filename':str(path),'format':'png'});return path
def assert_guest(command,label):
 record_event('independent-assertion',label=label,command=command)
 line(command);check(label,True)

def clean(fixture):
 assert_guest(fixture['cleanup_command'],'displayed preflight and exact cleanup '+fixture['id'])
 assert_guest('! clean_local && test ! -e "$w" && test ! -L "$w"','repeated cleanup refuses missing workspace '+fixture['id'])

for fixture in DATA:
 id=fixture['id'];slug=fixture['slug']
 if a.only and id!=a.only:continue
 if a.from_lesson and list(COMMANDS).index(id)<list(COMMANDS).index(a.from_lesson):continue
 for mode in a.modes:
  active=sessions.manager(id);running=False;info={'id':id,'mode':mode};started=time.monotonic()
  try:
   saved=active.reset(mode,True);active.start(mode);running=True;boot_ready()
   assert_guest('test "$(id -un)" = learner && test "$(ls /sys/class/net)" = lo','ordinary learner and offline '+id)
   if fixture['admin']:
    assert_guest('test "$(sudo -n id -u)" = 0 && sudo passwd -S learner | grep -q " L "','approved guest policy '+id)
    line('protected=$( { getent passwd learner root ll-service nobody; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)')
   sessions.select(LEGACY_ID)
   check('running controls associated '+id,sessions.view(LEGACY_ID)['running_lesson_id']==id)
   foreign=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest()).manager(LEGACY_ID)
   try:foreign.start();raise AssertionError('Foreign VM started')
   except Refused as exc:check('cross-profile refusal '+id,'already running' in str(exc))
   report.setdefault('candidate_hashes',{})[id]=hashlib.sha256(Path(__file__).with_name('local_shell_guest_fixtures.py').read_bytes()).hexdigest()
   for command in (fixture['commands'] if mode=='Learn' else fixture['challenge_commands']):
    line(command)
    if slug=='sticky' and 'sg()' in command:
     assert_guest('sg && hold_s="$s" && bad=$(mktemp -d /tmp/ll-sticky.XXXXXX) && chmod 1777 "$bad" && ln -s "$bad" "$bad/a" && s="$bad" && ! sg && test -L "$s/a" && rm -- "$s/a" && chmod 0700 "$bad" && ! sg && chmod 1777 "$bad" && parent_s=$(mktemp -d /tmp/ll-sticky.XXXXXX) && mkdir "$parent_s/nested" && chmod 1777 "$parent_s/nested" && s="$parent_s/nested" && ! sg && rmdir -- "$s" "$parent_s" && s="$bad" && find() { return 23; } && ! sg && unset -f find && sg && rmdir -- "$bad" && s="$hold_s" && sg','sticky containment/type/query failure refusal '+id)
    if 'sensible-editor note.txt' in command:
     key('i');text('edited-');key('esc');key('shift-semicolon');text('wq');key('ret')
   for i,command in enumerate(fixture['assertions']):assert_guest(command,id+' expected '+str(i))
   for i,command in enumerate(fixture['negative']):assert_guest(command,id+' incorrect alternative '+str(i))
   # Repeat fixture creation cannot silently overwrite a present or dangling name.
   assert_guest('here && printf "retained\\n" > collision.txt && ! fresh collision.txt && grep -qx retained collision.txt && rm -- collision.txt && ln -s missing dangling && ! fresh dangling && rm -- dangling','collision and dangling refusal '+id)
   # The exact displayed guard rejects a substituted directory; restore only our
   # verified fresh fixture name, never delete any unknown or owner directory.
   assert_guest('here && held="$w.held" && test ! -e "$held" && test ! -L "$held" && mv -- "$w" "$held" && ln -s "$held" "$w" && ! here && test -L "$w" && rm -- "$w" && mv -- "$held" "$w" && here','directory substitution refusal '+id)
   if fixture['admin']:assert_guest('test "$protected" = "$( { getent passwd learner root ll-service nobody; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)"','accounts and sudo unchanged '+id)
   definition=fixture['cleanup_command'].removesuffix('; clean_local')
   assert_guest(definition+'; printf "retain\\n" > unexpected.txt && ! clean_local && here && grep -qx retain unexpected.txt && rm -- unexpected.txt','cleanup unexpected member retains workspace '+id)
   if slug not in ('sticky','priority'):
    leaf={'startup':'login.txt','history':'history.txt','editor':'note.txt','hardlinks':'original.txt','symlinks':'before.meta','copies':'copy.txt','search':'placement.txt','handover':'report.txt'}[slug]
    assert_guest('here && mv -- '+leaf+' '+leaf+'.held && mkdir '+leaf+' && ! clean_local && here && test -f '+leaf+'.held && rmdir -- '+leaf+' && mv -- '+leaf+'.held '+leaf,'cleanup substituted file type refuses before deletion '+id)
   clean(fixture);shot(id+'-'+mode+'-verified')
   if mode=='Learn':active.progress('next');active.progress('hint')
   else:
    for op in ('next','hint'):
     try:active.progress(op);raise AssertionError('Challenge guidance permitted')
     except Refused:pass
   active.progress('complete');record=active.status()['session']
   check('self-reviewed unscored '+id,record['completion']['kind']=='self-reviewed' and 'score' not in record)
   check('clean Stop '+id,active.stop()=='Cleanly stopped');running=False;runtime_event('clean-stop')
   check('reopen exact record '+id,Sessions(a.vm_home,sessions.profile).manager(id).status()['session']==record)
   with active.access() as (root,g,p):
    fd=active.image(root)
    try:check('unchanged base '+id,sha256(fd)==active.spec['sha256'])
    finally:os.close(fd)
   info.update(result='PASS',pin=saved['pin'],session=saved['session'],generation=saved['generation'],seconds=round(time.monotonic()-started,2))
  except Exception as exc:
   info.update(result='FAIL',error=repr(exc));raise
  finally:
   if running:
    try:info['failure_cleanup']=active.stop()
    except Exception as exc:info['failure_cleanup']='BLOCKED: '+str(exc)
   report['lessons'].append(info);report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2));print('Evidence',out,flush=True)
