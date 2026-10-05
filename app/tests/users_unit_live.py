"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from users_guest_fixtures import COMMANDS,UNIT
from guest_screen import marker as acknowledgement,matches,locate_calibration,vi_ready,nano_ready
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process,verify_launch
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
out=Path(tempfile.mkdtemp(prefix='users-unit-live-'));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name('users_guest_fixtures.py').read_bytes())
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
  qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});time.sleep(.025)
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
 deadline=time.monotonic()+30
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
 text_to_send=t if interactive else t+"; printf '\\n"+marker+"\\n'"
 key('ctrl-u');text(text_to_send);key('ret')
 if interactive:
  if 'nano ' in t:ocr_until(label,lambda v:nano_ready(v,t.rsplit('nano ',1)[1]),header=True)
  else:ocr_until(label,vi_ready)
 else:await_ack(label,marker)
def shot(name):
 path=out/(name+'.png');qmp('screendump',{'filename':str(path),'format':'png'});return path
def read_marker(name,marker):
 for attempt in range(3):
  key('ctrl-q');line('clear');line('if [ -s ~/users-fixture-failures ] || [ \"$(wc -l < ~/users-fixture-successes)\" -ne '+str(assertion_count)+' ]; then echo FAILED; cat ~/users-fixture-failures; else echo '+marker+'; fi')
  path=shot(name+'-'+str(attempt));ocr=subprocess.run(['/usr/bin/tesseract',str(path),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout;(out/(path.name+'.txt')).write_text(ocr)
  if re.search(r'(?m)^'+marker+r'\s*$',ocr):return path.name
  if re.search(r'(?m)^FAILED\s*$',ocr):raise AssertionError('Guest assertion failure: '+ocr)
 raise AssertionError('Unreadable guest evidence, not PASS: '+str(out))
assertion_count=0
def assertion(command,label):
 global assertion_count
 assertion_count+=1
 line(command+' && echo '+label+' >> ~/users-fixture-successes || echo '+label+' >> ~/users-fixture-failures')


def interrupted_process(name):
 global command_sequence
 command_sequence+=1;start_marker=acknowledgement(command_sequence)
 command_sequence+=1;end_marker=acknowledgement(command_sequence)
 command='sudo runuser -u '+name+' -- bash -c \'echo "$BASHPID" > "$HOME/interrupted.pid"; trap "exit 130" INT; printf "\\n'+start_marker+'\\n"; sleep 10\'; interrupted_rc=$?; printf "\\n'+end_marker+'\\n"'
 record_event('interrupted-guest-command',command=command,start=start_marker,end=end_marker)
 key('ctrl-u');text(command);key('ret');await_ack('interrupt-ready-'+name,start_marker)
 key('ctrl-c');await_ack('interrupt-complete-'+name,end_marker)
 assertion('test "$interrupted_rc" -eq 130 && ! sudo kill -0 "$(sudo cat /home/'+name+'/interrupted.pid)" 2>/dev/null','INTERRUPTED_EXACT_CHILD_GONE')


def verify(slug):
 assertion('test "$(id -u)" -ne 0 && test "$(sudo -n id -u)" -eq 0 && test "$(ls /sys/class/net)" = lo','POLICY')
 assertion('sudo passwd -S learner | grep -q " L " && sudo passwd -S root | grep -q " L " && test "$(getent passwd ll-service | cut -d : -f 7)" = /usr/sbin/nologin','PROTECTED_ACCOUNTS')
 if slug=='inspect':
  assertion('test "$(sudo runuser -u ll-u1 -- id -un)" = ll-u1 && test "$(id -g ll-u1)" = "$(getent group ll-u1 | cut -d : -f 3)" && sudo passwd -S ll-u1 | grep -q " L "','IDENTITY_PRIMARY_LOCK')
 if slug=='create':
  assertion('test "$(getent passwd ll-u2 | cut -d : -f 7)" = /bin/bash && test "$(sudo stat -c %U /home/ll-u2/note.txt)" = ll-u2 && sudo runuser -u ll-u2 -- grep -qx owned /home/ll-u2/note.txt','HOME_WRITE_READ')
  line('sudo touch /home/ll-u2/wrong.txt; sudo chmod 0600 /home/ll-u2/wrong.txt')
  assertion('! sudo runuser -u ll-u2 -- cat /home/ll-u2/wrong.txt','ROOT_OWNED_DENIED')
 if slug=='membership':
  assertion('sudo grep -qw ll-u3keep /home/ll-u3/old.before && ! sudo grep -qw ll-u3team /home/ll-u3/old.before && sudo cmp /home/ll-u3/old.before /home/ll-u3/old.after','OLD_PROCESS_GROUPS')
  assertion('sudo runuser -u ll-u3 -- id -Gn | grep -qw ll-u3team && id -Gn ll-u3 | grep -qw ll-u3keep','FRESH_GROUPS')
  line('sudo usermod -G ll-u3team ll-u3')
  assertion('! id -Gn ll-u3 | grep -qw ll-u3keep','INCORRECT_REPLACEMENT_DETECTED')
  line('sudo usermod -aG ll-u3keep ll-u3')
  assertion('id -Gn ll-u3 | grep -qw ll-u3keep && id -Gn ll-u3 | grep -qw ll-u3team','PRESERVED_OTHER_GROUP')
 if slug=='ownership':
  assertion('sudo runuser -u ll-u4 -- grep -qx handover /srv/ll-u4/note.txt && ! sudo runuser -u nobody -- cat /srv/ll-u4/note.txt && ! sudo runuser -u ll-u4 -- bash -c \'echo wrong >> /srv/ll-u4/note.txt\'','NARROW_READ_NOT_WRITE')
  line('sudo chmod 0644 /srv/ll-u4/note.txt')
  assertion('sudo runuser -u nobody -- cat /srv/ll-u4/note.txt','BROAD_MODE_EXPOSES')
  line('sudo chmod 0600 /srv/ll-u4/note.txt')
  assertion('! sudo runuser -u ll-u4 -- cat /srv/ll-u4/note.txt','INSUFFICIENT_MODE_DENIED')
  line('sudo chown ll-u4:ll-u4team /srv/ll-u4/note.txt; sudo chmod 0040 /srv/ll-u4/note.txt')
  assertion('! sudo runuser -u ll-u4 -- cat /srv/ll-u4/note.txt','OWNER_CLASS_PRECEDENCE')
  line('sudo chown root:ll-u4team /srv/ll-u4/note.txt; sudo chmod 0640 /srv/ll-u4/note.txt')
  assertion('sudo runuser -u ll-u4 -- grep -qx handover /srv/ll-u4/note.txt && test "$(sudo stat -c %a:%U:%G /srv/ll-u4/note.txt)" = 640:root:ll-u4team','REPAIRED_STATE')
 if slug=='shared':
  assertion('test "$(sudo stat -c %a:%G /srv/ll-u5/note.txt)" = 660:ll-u5team && test "$(sudo stat -c %a:%G /srv/ll-u5/sub)" = 2770:ll-u5team && sudo runuser -u ll-u5b -- grep -qx second /srv/ll-u5/note.txt','ACTUAL_SHARED_WRITE_INHERIT')
  assertion('! sudo runuser -u nobody -- cat /srv/ll-u5/note.txt','SHARED_OUTSIDER_DENIED')
  line('sudo chmod g-s /srv/ll-u5; sudo runuser -u ll-u5a -- touch /srv/ll-u5/no-setgid.txt')
  assertion('test "$(sudo stat -c %G /srv/ll-u5/no-setgid.txt)" = ll-u5a','MISSING_SETGID_WRONG_GROUP')
  line('sudo chmod 2770 /srv/ll-u5; sudo runuser -u ll-u5a -- bash -c \'umask 0077; echo tight > /srv/ll-u5/tight.txt\'')
  assertion('test "$(sudo stat -c %G /srv/ll-u5/tight.txt)" = ll-u5team && ! sudo runuser -u ll-u5b -- cat /srv/ll-u5/tight.txt','SETGID_NOT_PERMISSION_GRANT')
  line('sudo rm -- /srv/ll-u5/no-setgid.txt /srv/ll-u5/tight.txt')
 if slug=='umask':
  for n,f,d in ((22,644,755),(27,640,750),(77,600,700)):
   assertion('test "$(sudo stat -c %a /home/ll-u6/f'+str(n)+')" = '+str(f)+' && test "$(sudo stat -c %a /home/ll-u6/d'+str(n)+')" = '+str(d),'MASK_'+str(n))
  assertion('test "$(umask)" = "$original_mask"','PARENT_MASK_UNCHANGED')
  line('sudo runuser -u ll-u6 -- bash -c \'umask 0111; touch "$HOME/bit-filter"; stat -c %a "$HOME/bit-filter"\'')
  assertion('test "$(sudo stat -c %a /home/ll-u6/bit-filter)" = 666','BIT_FILTER_NOT_SUBTRACTION')
 if slug=='restrictions':
  line('sudo chage -E 2000-01-01 ll-u7; sudo su - ll-u7 -c id > ~/expired-out 2> ~/expired-error; rc=$?')
  assertion('test "$rc" -ne 0 && grep -q expired ~/expired-error && sudo runuser -u ll-u7 -- id -un | grep -qx ll-u7','EXPIRED_SU_RUNUSER_DISTINCTION')
  line('sudo chage -E -1 ll-u7; sudo usermod -s /usr/sbin/nologin ll-u7; sudo su - ll-u7 -c id > ~/shell-out 2> ~/shell-error; rc=$?')
  assertion('test "$rc" -ne 0 && grep -q "not available" ~/shell-out && sudo runuser -u ll-u7 -- id -un | grep -qx ll-u7','NOLOGIN_NOT_ROOT_EXECUTION_BLOCK')
  line('sudo usermod -s /bin/bash ll-u7')
  assertion('sudo passwd -S ll-u7 | grep -q " L " && sudo su - ll-u7 -c \'id -un\' | grep -qx ll-u7','RESTORED_SHELL_STILL_LOCKED')
 if slug=='repair':
  assertion('sudo runuser -u ll-u8 -- grep -qx checked /srv/ll-u8/note.txt && ! sudo runuser -u nobody -- cat /srv/ll-u8/note.txt','REPAIR_IDENTITY_ACCESS')
  assertion('test "$(sudo stat -c %a:%U:%G /srv/ll-u8/note.txt)" = 660:root:ll-u8team && test "$(sudo stat -c %a:%G /srv/ll-u8/new.txt)" = 660:ll-u8team && test "$(sudo stat -c %a /srv/ll-u8)" = 2770','REPAIR_MODES_INHERITANCE')
  assertion('id -Gn ll-u8 | grep -qw ll-u8keep && id -Gn ll-u8 | grep -qw ll-u8team && grep -q EVIDENCE ~/ll-u8-handover.txt','REPAIR_OTHER_GROUP_REPORT')
  line('sudo chmod 0777 /srv/ll-u8/note.txt')
  assertion('! sudo runuser -u nobody -- cat /srv/ll-u8/note.txt','PARENT_STILL_DENIES_OUTSIDER')
  assertion('test "$(sudo stat -c %a /srv/ll-u8/note.txt)" = 777','BITS_TOO_BROAD_DESPITE_DENIAL')
  line('sudo chmod 0660 /srv/ll-u8/note.txt')

CLEANUP={
'inspect':['sudo userdel -r ll-u1'],
'create':['sudo userdel -r ll-u2'],
'membership':['sudo userdel -r ll-u3','sudo groupdel ll-u3keep; sudo groupdel ll-u3team'],
'ownership':['sudo userdel -r ll-u4','sudo rm -- /srv/ll-u4/note.txt; sudo rmdir /srv/ll-u4; sudo groupdel ll-u4team'],
'shared':['sudo userdel -r ll-u5a; sudo userdel -r ll-u5b','sudo rm -- /srv/ll-u5/note.txt; sudo rmdir /srv/ll-u5/sub /srv/ll-u5; sudo groupdel ll-u5team'],
'umask':['sudo userdel -r ll-u6'],
'restrictions':['sudo userdel -r ll-u7'],
'repair':['sudo userdel -r ll-u8','sudo rm -- /srv/ll-u8/note.txt /srv/ll-u8/new.txt; sudo rmdir /srv/ll-u8; sudo groupdel ll-u8keep; sudo groupdel ll-u8team']}

def cleanup(slug):
 for c in CLEANUP[slug]:line(c)
 names={'shared':['ll-u5a','ll-u5b']}.get(slug,['ll-u'+str(list(COMMANDS).index('real-linux-users-'+slug)+1)])
 for name in names:assertion('! getent passwd '+name+' && ! getent group '+name+' && test ! -e /home/'+name,'CLEANED_'+name)
 groups={'membership':['ll-u3keep','ll-u3team'],'ownership':['ll-u4team'],'shared':['ll-u5team'],'repair':['ll-u8keep','ll-u8team']}.get(slug,[])
 for group in groups:assertion('! getent group '+group,'GROUP_REMOVED_'+group)
 if slug in ('ownership','shared','repair'):assertion('test ! -e /srv/ll-u'+str({'ownership':4,'shared':5,'repair':8}[slug]),'PATH_REMOVED')
 # Repeat cleanup only when getent confirms the named fixture still exists.
 for name in names:line('if getent passwd '+name+'; then sudo userdel -r '+name+'; fi')
 assertion('test "$protected_before" = "$( { getent passwd learner root ll-service; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)"','PROTECTED_METADATA_UNCHANGED')

for id,commands in COMMANDS.items():
 if a.only and id!=a.only:continue
 if a.from_lesson and list(COMMANDS).index(id)<list(COMMANDS).index(a.from_lesson):continue
 slug=id.removeprefix('real-linux-users-')
 for mode in a.modes:
  active=sessions.manager(id);running=False;started=time.monotonic();info={'id':id,'mode':mode}
  try:
   saved=active.reset(mode,True);active.start(mode);running=True;print('BOOT',id,mode,flush=True);boot_ready()
   sessions.select(LEGACY_ID);view=sessions.view(LEGACY_ID)
   check(id+' '+mode+' running controls across units',view['running_lesson_id']==id)
   foreign=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest()).manager(LEGACY_ID)
   try:foreign.start();raise AssertionError('Foreign VM started')
   except Refused as exc:check(id+' '+mode+' cross-profile refusal','already running' in str(exc))
   line(': > ~/users-fixture-failures; : > ~/users-fixture-successes; original_mask=$(umask); protected_before=$( { getent passwd learner root ll-service; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)');assertion_count=0
   for command in commands:line(command)
   verify(slug)
   if slug=='inspect':interrupted_process('ll-u1')
   # Repeated setup must refuse; do not adopt or overwrite the existing account.
   line('before=$(getent passwd '+('ll-u5a' if slug=='shared' else 'll-u'+str(list(COMMANDS).index(id)+1))+'); '+commands[0]+'; setup_rc=$?')
   assertion('test "$setup_rc" -ne 0 && test "$before" = "$(getent passwd '+('ll-u5a' if slug=='shared' else 'll-u'+str(list(COMMANDS).index(id)+1))+')"','COLLISION_REFUSED_NO_MUTATION')
   cleanup(slug)
   # Setup interruption is handled by inspecting/cleaning the partial fixture,
   # not by rerunning setup blindly. No persistent subprocess is left behind.
   line(commands[0]);
   for name in ({'shared':['ll-u5a','ll-u5b']}.get(slug,['ll-u'+str(list(COMMANDS).index(id)+1)])):line('sudo userdel -r '+name)
   if slug=='shared':line('sudo groupdel ll-u5team')
   assertion('test \"$protected_before\" = \"$( { getent passwd learner root ll-service; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)\"','INTERRUPTED_SETUP_METADATA')
   info['screenshot']=read_marker(id+'-'+mode,'PASSED')
   if mode=='Learn':active.progress('next');active.progress('hint')
   else:
    for op in ('next','hint'):
     try:active.progress(op);raise AssertionError('Challenge guidance allowed')
     except Refused:pass
   active.progress('complete');record=active.status()['session'];check(id+' '+mode+' self-reviewed unscored',record['completion']['kind']=='self-reviewed' and 'score' not in record)
   check(id+' '+mode+' clean Stop',active.stop()=='Cleanly stopped');running=False;runtime_event('clean-stop')
   check(id+' '+mode+' restart metadata',Sessions(a.vm_home,sessions.profile).manager(id).status()['session']==record)
   with active.access() as (root,g,p):
    fd=active.image(root)
    try:check(id+' '+mode+' base unchanged',sha256(fd)==active.spec['sha256'])
    finally:os.close(fd)
   info.update(result='PASS',pin=saved['pin'],session=saved['session'],generation=saved['generation'],seconds=round(time.monotonic()-started,2))
  finally:
   if running:
    try:info['failure_cleanup']=active.stop()
    except Exception as exc:info['failure_cleanup']='BLOCKED: '+str(exc)
   report['lessons'].append(info);report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2))
print('Evidence',out,flush=True)
