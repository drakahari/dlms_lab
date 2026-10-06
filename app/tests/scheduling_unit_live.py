"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scheduling_guest_fixtures import COMMANDS,UNIT
from guest_screen import marker as acknowledgement,matches,locate_calibration,vi_ready,nano_ready
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process,verify_launch
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
out=Path(tempfile.mkdtemp(prefix='scheduling-unit-live-'));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name('scheduling_guest_fixtures.py').read_bytes())
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
  key('ctrl-q');line('clear');line('if [ -s ~/scheduling-fixture-failures ] || [ \"$(wc -l < ~/scheduling-fixture-successes)\" -ne '+str(assertion_count)+' ]; then echo FAILED; cat ~/scheduling-fixture-failures; else echo '+marker+'; fi')
  path=shot(name+'-'+str(attempt));ocr=subprocess.run(['/usr/bin/tesseract',str(path),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout;(out/(path.name+'.txt')).write_text(ocr)
  if re.search(r'(?m)^'+marker+r'\s*$',ocr):return path.name
  if re.search(r'(?m)^FAILED\s*$',ocr):raise AssertionError('Guest assertion failure: '+ocr)
 raise AssertionError('Unreadable guest evidence, not PASS: '+str(out))
assertion_count=0
def assertion(command,label):
 global assertion_count
 assertion_count+=1
 line(command+' && echo '+label+' >> ~/scheduling-fixture-successes || echo '+label+' >> ~/scheduling-fixture-failures')



def property(n,key,value,user=False):
 scope=' --user' if user else ''
 return 'test "$(systemctl'+scope+' show ll-s'+str(n)+'.service -p '+key+' --value)" = '+value

def cleanup(n):
 if n==5:
  line('systemctl --no-pager --user stop ll-s5.timer ll-s5.service ll-s5-timeout.service; systemctl --no-pager --user reset-failed ll-s5-timeout.service; rm -- "$HOME/ll-s5/job.sh" "$HOME/ll-s5/report.txt"; rmdir "$HOME/ll-s5"')
  assertion('test ! -e "$HOME/ll-s5"','USER_WORKSPACE_GONE')
  return
 if n in (6,7,8):
  timer='ll-s'+str(n)+'.timer'
  line('sudo systemctl --no-pager disable --now '+timer+(' ll-s7-overlap.timer' if n==7 else '')+'; sudo systemctl --no-pager stop ll-s'+str(n)+'.service; sudo systemctl --no-pager clean --what=state '+timer)
  line('sudo rm -- /etc/systemd/system/ll-s'+str(n)+'.service /etc/systemd/system/'+timer+(' /etc/systemd/system/ll-s7-overlap.timer' if n==7 else '')+'; sudo systemctl --no-pager daemon-reload; sudo systemctl --no-pager reset-failed ll-s'+str(n)+'.service')
  assertion('test "$(systemctl --no-pager show ll-s'+str(n)+'.timer -p LoadState --value)" = not-found','NAMED_UNIT_REMOVED')
 line('if sudo test -e /var/spool/cron/crontabs/ll-s'+str(n)+'; then sudo crontab -u ll-s'+str(n)+' -r; fi')
 assertion('! pgrep -u ll-s'+str(n),'NO_DISPOSABLE_PROCESSES')
 line('sudo userdel -r ll-s'+str(n))
 assertion('! getent passwd ll-s'+str(n)+' && test ! -e /home/ll-s'+str(n),'FIXTURE_REMOVED')
 line('if getent passwd ll-s'+str(n)+'; then sudo userdel -r ll-s'+str(n)+'; fi')

def verify(n):
 assertion('test "$(id -u)" -ne 0 && test "$(sudo -n id -u)" -eq 0 && test "$(ls /sys/class/net)" = lo','GUEST_POLICY')
 if n==1:
  assertion('test "$(sudo runuser -u ll-s1 -- id -un)" = ll-s1 && systemctl --no-pager is-active --quiet cron && systemctl --no-pager --user is-system-running | grep -qx running && ! command -v at','ACTUAL_CAPABILITIES')
 if n in (2,3,4,6,8):
  assertion('sudo runuser -u ll-s'+str(n)+' -- grep -qx user=ll-s'+str(n)+' /home/ll-s'+str(n)+'/report.txt && test "$(sudo stat -c %a:%U /home/ll-s'+str(n)+'/report.txt)" = 600:ll-s'+str(n)+' && test "$(sudo stat -c %s /home/ll-s'+str(n)+'/report.txt)" -le 256','PRIVATE_REPORT_IDENTITY_CONTENT')
 if n==2:
  line('old=$(sudo sha256sum /home/ll-s2/report.txt); sudo /home/ll-s2/job.sh; bad=$?')
  assertion('test "$bad" -eq 2 && test "$old" = "$(sudo sha256sum /home/ll-s2/report.txt)"','WRONG_IDENTITY_NO_DAMAGE')
 if n in (3,4,8):
  assertion('test "$(sudo cat /home/ll-s'+str(n)+'/status.txt)" = 0','REAL_CRON_EXIT_ZERO')
 if n in (3,8):
  assertion('! sudo test -e /var/spool/cron/crontabs/ll-s'+str(n),'CRONTAB_REMOVED')
 if n==4:
  line('sudo chmod 0600 /home/ll-s4/bin/report-helper; sudo runuser -u ll-s4 -- env -i HOME=/home/ll-s4 PATH=/usr/bin:/bin /bin/bash /home/ll-s4/job.sh; denied=$?')
  assertion('test "$denied" -eq 126','HELPER_DENIED')
  line('sudo chmod 0700 /home/ll-s4/bin/report-helper; sudo runuser -u ll-s4 -- /home/ll-s4/job.sh')
  assertion('sudo test ! -s /home/ll-s4/error.txt','REAL_CRON_SUCCESS_OVERWRITES_ERROR')
 if n==5:
  assertion('grep -qx user=learner "$HOME/ll-s5/report.txt" && test "$(stat -c %a:%U "$HOME/ll-s5/report.txt")" = 600:learner && test "$(wc -l < "$HOME/ll-s5/report.txt")" -eq 1','USER_REPORT_CONTENT_OWNER_MODE')
  assertion(property(5,'LoadState','loaded',True)+' && '+property(5,'Type','exec',True)+' && '+property(5,'Result','success',True)+' && '+property(5,'ExecMainStatus','0',True)+' && '+property(5,'RuntimeMaxUSec','5s',True)+' && '+property(5,'MemoryMax','67108864',True)+' && '+property(5,'TasksMax','16',True),'LOADED_USER_LIMITS')
  assertion('test "$(systemctl --no-pager --user show ll-s5-timeout.service -p LoadState --value)" = loaded && test "$(systemctl --no-pager --user show ll-s5-timeout.service -p Type --value)" = exec && test "$(systemctl --no-pager --user show ll-s5-timeout.service -p Result --value)" = timeout && test "$(systemctl --no-pager --user show ll-s5-timeout.service -p RuntimeMaxUSec --value)" = 2s && test "$(systemctl --no-pager --user show ll-s5-timeout.service -p MainPID --value)" = 0','REAL_RUNTIME_TIMEOUT_LOADED')
  line('timedout_group=$(systemctl --no-pager --user show ll-s5-timeout.service -p ControlGroup --value); remaining_tasks=; if test -n "$timedout_group" && test -e "/sys/fs/cgroup$timedout_group/cgroup.procs"; then remaining_tasks=$(cat "/sys/fs/cgroup$timedout_group/cgroup.procs"); fi')
  assertion('test -z "$remaining_tasks"','TIMED_OUT_CGROUP_NO_TASKS')
 if n in (6,7):
  assertion(property(n,'Result','success')+' && '+property(n,'ExecMainStatus','0')+' && '+property(n,'ActiveState','inactive'),'FINAL_SYSTEM_RESULT_NOT_JUST_TRIGGER')
 if n in (6,7,8):
  assertion(property(n,'LoadState','loaded')+' && '+property(n,'User','ll-s'+str(n))+' && '+property(n,'MemoryMax','67108864')+' && '+property(n,'TasksMax','16')+' && '+property(n,'RuntimeMaxUSec',str(8 if n==7 else 6)+'s'),'LOADED_SYSTEM_LIMITS')
 if n==7:
  assertion('test "$worker" -gt 0 && test "$worker" = "$current_worker" && test "$active_count" -eq 1 && test "$(sudo cat /home/ll-s7/events | wc -l)" -eq 2 && sudo grep -q "^BEGIN 1 " /home/ll-s7/events && sudo grep -qx "END 1" /home/ll-s7/events && test "$(sudo cat /home/ll-s7/count)" -eq 1','ACTIVE_SERVICE_SINGLE_INSTANCE')
  assertion('test "$(sudo stat -c %s /home/ll-s7/events)" -le 512','EVENT_CAP')
 if n==8:
  assertion(property(8,'Result','success')+' && '+property(8,'ExecMainStatus','0')+' && grep -q EVIDENCE "$HOME/ll-s8-handover.txt"','FINAL_SUCCESS_HANDOVER')

def negative_persistence():
 line('sudo systemctl --no-pager stop ll-s7.timer ll-s7-overlap.timer ll-s7.service; sudo sed -i "s/Persistent=true/Persistent=false/" /etc/systemd/system/ll-s7.timer; sudo systemctl --no-pager daemon-reload; sudo runuser -u ll-s7 -- sh -c \'printf "0\\n" > /home/ll-s7/count; : > /home/ll-s7/events; printf "1\\n" > /home/ll-s7/delay\'')
 line('sudo systemctl --no-pager start ll-s7.timer; end=$((SECONDS+15)); until test "$(sudo cat /home/ll-s7/count)" -gt 0; do test "$SECONDS" -lt "$end" || break; sleep 1; done; sudo systemctl --no-pager stop ll-s7.timer; sleep 2; baseline_count=$(sudo cat /home/ll-s7/count); sleep 25')
 line('end=$((SECONDS+12)); until test "$(( $(date +%s) % 10 ))" -eq 2; do test "$SECONDS" -lt "$end" || break; sleep 0.1; done; sudo systemctl --no-pager start ll-s7.timer; sleep 3; nonpersistent_count=$(sudo cat /home/ll-s7/count); sudo systemctl --no-pager stop ll-s7.timer')
 assertion('test "$nonpersistent_count" -eq "$baseline_count"','NONPERSISTENT_NO_IMMEDIATE_CATCHUP')
 line('sudo sed -i "s/Persistent=false/Persistent=true/" /etc/systemd/system/ll-s7.timer; sudo systemctl --no-pager daemon-reload')

def interrupted_process(name):
 global command_sequence
 command_sequence+=1;start_marker=acknowledgement(command_sequence)
 command_sequence+=1;end_marker=acknowledgement(command_sequence)
 command='sudo runuser -u '+name+' -- bash -c \'echo "$BASHPID" > "$HOME/interrupted.pid"; trap "exit 130" INT; printf "\\n'+start_marker+'\\n"; sleep 10\'; interrupted_rc=$?; printf "\\n'+end_marker+'\\n"'
 record_event('interrupted-guest-command',command=command,start=start_marker,end=end_marker)
 key('ctrl-u');text(command);key('ret');await_ack('interrupt-ready-'+name,start_marker)
 key('ctrl-c');await_ack('interrupt-complete-'+name,end_marker)
 assertion('test "$interrupted_rc" -eq 130 && ! sudo kill -0 "$(sudo cat /home/'+name+'/interrupted.pid)" 2>/dev/null','INTERRUPTED_EXACT_CHILD_GONE')


for id,commands in COMMANDS.items():
 if a.only and id!=a.only:continue
 if a.from_lesson and list(COMMANDS).index(id)<list(COMMANDS).index(a.from_lesson):continue
 n=list(COMMANDS).index(id)+1
 for mode in a.modes:
  active=sessions.manager(id);running=False;started=time.monotonic();info={'id':id,'mode':mode}
  try:
   saved=active.reset(mode,True);active.start(mode);running=True;print('BOOT',id,mode,flush=True);boot_ready()
   sessions.select(LEGACY_ID);check(id+' running controls',sessions.view(LEGACY_ID)['running_lesson_id']==id)
   foreign=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest()).manager(LEGACY_ID)
   try:foreign.start();raise AssertionError('Foreign VM started')
   except Refused as exc:check(id+' cross-profile refusal','already running' in str(exc))
   line(': > ~/scheduling-fixture-failures; : > ~/scheduling-fixture-successes; protected_before=$( { getent passwd learner root ll-service; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)');assertion_count=0
   for i,command in enumerate(commands):
    if n in (3,4,8) and command.startswith('sudo test ! -e /var/spool/cron/crontabs/'):
     # Real root-owned spool collision; test the exact installation pipeline.
     spool='/var/spool/cron/crontabs/ll-s'+str(n)
     end_install=' | sudo crontab -u ll-s'+str(n)+' -'
     attempt=command[:command.index(end_install)+len(end_install)]
     line('sudo test ! -e '+spool+' && sudo install -m 0600 /dev/null '+spool+'; before_spool=$(sudo sha256sum '+spool+'); '+attempt+'; spool_collision_rc=$?')
     assertion('test "$spool_collision_rc" -ne 0 && test "$before_spool" = "$(sudo sha256sum '+spool+')"','EXACT_CRONTAB_COLLISION_REFUSED_UNCHANGED')
     line('sudo rm -- '+spool)
    if n==4 and i==4:command=command.replace('; printf', '; minimal_rc=$?; printf')
    line(command)
    if n==4 and i==3:assertion('test "$(sudo cat /home/ll-s4/status.txt)" -eq 127 && sudo grep -q "not found" /home/ll-s4/error.txt','REAL_CRON_LOOKUP_FAILURE')
    if n==4 and i==4:assertion('test "$minimal_rc" -eq 126','MINIMAL_ENV_ACCESS_FAILURE')
    if n==7 and i==3:assertion('test "$(sudo cat /home/ll-s7/count)" -eq "$before"','MISSED_SLOTS_NO_EXECUTION')
    if n==7 and i==4:assertion('test "$(sudo cat /home/ll-s7/count)" -eq "$((before+1))"','SINGLE_CATCHUP')
    if n==8 and i==3:
     # Both failure states are inspected while the file-backed unit stays loaded.
     assertion('test "$initial_status" -eq 2 && test "$(systemctl --no-pager show ll-s8.service -p ExecMainStatus --value)" -eq 1 && test "$(sudo stat -c %U /home/ll-s8/report.txt)" = root','IDENTITY_REPAIR_STILL_ACCESS_FAILURE')
   verify(n)
   if n==7:negative_persistence()
   if n==2:interrupted_process("ll-s2")
   # No fixture adoption on repeated setup.
   if n!=5:
    line('before_account=$(getent passwd ll-s'+str(n)+'); '+commands[0]+'; repeat_rc=$?')
    assertion('test "$repeat_rc" -ne 0 && test "$before_account" = "$(getent passwd ll-s'+str(n)+')"','COLLISION_REFUSED')
   cleanup(n)
   assertion('test "$protected_before" = "$( { getent passwd learner root ll-service; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)"','PROTECTED_METADATA_UNCHANGED')
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
