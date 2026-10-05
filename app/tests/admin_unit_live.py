"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--availability-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from admin_guest_fixtures import COMMANDS
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
out=Path(tempfile.mkdtemp(prefix='admin-unit-live-'));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name('admin_guest_fixtures.py').read_bytes())
# Reliable host visibility before launch. Never clear or replace coordination to
# make tests pass; every Start acquires the normal shared lifetime lock.
processes=subprocess.run(['ps','-eo','pid,uid,args'],capture_output=True,text=True,check=True).stdout
(out/'host-processes-before.txt').write_text(processes)
assert not any(re.search(r'^\s*\d+\s+\d+\s+\S*qemu-system-x86_64(?:\s|$)',s) for s in processes.splitlines()),'Guest active: native portion blocked; no stop sent'

def check(name,condition):
 if not condition:raise AssertionError(name)
 checks.append(name);print(name,flush=True)
def qmp(command,args=None):
 r=json.loads((active.gate_root/'running.json').read_text())
 assert r['state']=='running' and r['profile']==active.profile and r['store']==active.binding and same_process(r),'Not our verified guest; no developer control sent'
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
def line(t,delay=.45):
 key('ctrl-u');text(t);key('ret');time.sleep(delay)
def shot(name):
 path=out/(name+'.png');qmp('screendump',{'filename':str(path),'format':'png'});return path
def read_marker(name,marker):
 for attempt in range(3):
  key('ctrl-q');line('clear');line('if [ -s ~/admin-fixture-failures ]; then echo FAILED; cat ~/admin-fixture-failures; else echo '+marker+'; fi')
  path=shot(name+'-'+str(attempt));ocr=subprocess.run(['/usr/bin/tesseract',str(path),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout;(out/(path.name+'.txt')).write_text(ocr)
  if re.search(r'(?m)^'+marker+r'\s*$',ocr):return path.name
  if re.search(r'(?m)^FAILED\s*$',ocr):raise AssertionError('Guest assertion failure: '+ocr)
 raise AssertionError('Unreadable guest evidence, not PASS: '+str(out))
def assertion(command,label):line(command+' || echo '+label+' >> ~/admin-fixture-failures')
def edit(slug):
 entry=shot('editor-'+slug+'-'+uuid.uuid4().hex[:8])
 visible=subprocess.run(['/usr/bin/tesseract',str(entry),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout
 (out/(entry.name+'.txt')).write_text(visible)
 assert 'GNU nano' in visible, 'Editor was not active; no report text sent: '+str(entry)
 key('ctrl-home')
 if slug=='incident':
  rows=['SYMPTOM: missing config and disabled service','EVIDENCE: unreadable config in journal, original retained','CHANGE: install root ll-service 0640, enable and start','VERIFIED: LAB_READY unprivileged and enabled state','LIMIT: no reboot proof in this incident; see boot lesson','ROLLBACK: stop disable, preserve config then remove exact restored path']
 else:
  counts={'override':4,'logs':3,'rotation':8}
  for _ in range(counts[slug]):key('ctrl-k')
  rows={'override':['[Service]','ExecStart=','ExecStart=/usr/local/lib/learning-lab/admin-worker override'], 'logs':['local5.notice /var/log/learning-lab/events.log'], 'rotation':['/var/log/learning-lab/rotation.log {','    size 1k','    rotate 2','    missingok','    notifempty','    create 0640 root adm','}']}[slug]
 for row in rows:text(row);key('ret')
 key('ctrl-o');key('ret');key('ctrl-x');time.sleep(.5)
def verify(slug):
 assertion('test "$(id -u)" -ne 0 && test "$(sudo -n id -u)" -eq 0','SUDO_POLICY_FAIL')
 assertion('test "$(ls /sys/class/net)" = lo && test ! -x /usr/sbin/sshd','ISOLATION_FAIL')
 assertion('sudo passwd -S root | grep -q " L " && sudo passwd -S learner | grep -q " L " && sudo passwd -S ll-service | grep -q " L "','LOCK_POLICY_FAIL')
 assertion('getent passwd ll-service | grep -q /usr/sbin/nologin','ACCOUNT_FAIL')
 if slug=='change':assertion('cmp "$work/original.conf" /etc/learning-lab/change.conf && test "$(stat -c %a /etc/learning-lab/change.conf)" = 644','ROLLBACK_FAIL')
 if slug=='lifecycle':assertion('test "$(systemctl is-active ll-lifecycle)" = inactive && sudo journalctl -u ll-lifecycle --no-pager | grep -q LAB_READY','LIFECYCLE_FAIL')
 if slug=='boot':
  assertion('test "$(cut -d " " -f 1 /var/lib/ll-boot/last-start)" = "$(cat /proc/sys/kernel/random/boot_id)"','BOOT_MARKER_FAIL')
  assertion('test "$(systemctl is-enabled ll-boot)" = disabled && test "$(systemctl is-active ll-boot)" = inactive','BOOT_CLEANUP_FAIL')
 if slug in ('override','access','incident'):
  assertion('sudo journalctl -u ll-'+slug+' --no-pager | grep -q LAB_READY','SERVICE_FAIL')
  assertion('test "$(systemctl show ll-'+slug+' -p User --value)" = ll-service && test "$(systemctl is-active ll-'+slug+')" = inactive','SERVICE_USER_FAIL')
  assertion('test "$(systemctl show ll-'+slug+' -p MemoryMax --value)" = 67108864 && test "$(systemctl show ll-'+slug+' -p TasksMax --value)" = 8','BOUNDS_FAIL')
 if slug in ('access','incident'):
  assertion('test "$(stat -c %a /etc/learning-lab/'+slug+'.conf)" = 640 && test "$(stat -c %U:%G /etc/learning-lab/'+slug+'.conf)" = root:ll-service','MODE_FAIL')
  assertion('sudo runuser -u ll-service -- cat /etc/learning-lab/'+slug+'.conf','READ_FAIL')
  line('if sudo runuser -u nobody -- cat /etc/learning-lab/'+slug+'.conf; then echo BROAD_ACCESS >> ~/admin-fixture-failures; fi')
 if slug=='logs':
  assertion('sudo grep -q "LAB_EVENT after" /var/log/learning-lab/events.log && sudo journalctl -t ll-admin --no-pager | grep -q "LAB_EVENT after"','LOG_ROUTE_FAIL')
  assertion('test "$(sudo stat -c %s /var/log/learning-lab/events.log)" -lt 8192','LOG_BOUND_FAIL')
 if slug=='rotation':
  assertion('sudo grep -q "LAB_ROTATE retained record" /var/log/learning-lab/rotation.log.1 && test "$(stat -c %a /var/log/learning-lab/rotation.log)" = 640 && test ! -s /var/log/learning-lab/rotation.log','ROTATION_FAIL')
 if slug=='incident':assertion('grep -q VERIFIED handover.txt && grep -q ROLLBACK handover.txt','HANDOVER_FAIL')
def safety_proof():
 global active
 id='real-linux-admin-lifecycle';active=sessions.manager(id);running=False
 try:
  first=active.reset('Learn',True);active.start();running=True;time.sleep(20)
  line(': > ~/admin-fixture-failures')
  assertion('test -z "$(sudo dpkg --audit)" && sudo apt-get check','DEPENDENCIES_FAIL')
  assertion('test "$(sudo cat /etc/sudoers.d/learning-lab)" = "learner ALL=(root) NOPASSWD: ALL"','SUDO_RULE_FAIL')
  assertion('test "$(stat -c %a:%U:%G /etc/sudoers.d/learning-lab)" = 440:root:root && sudo visudo -c','SUDO_FILE_FAIL')
  assertion('test -z "$(sudo ss -H -lntu)"','LISTENER_FAIL')
  assertion('test "$(ls /sys/class/net)" = lo && test ! -x /usr/sbin/sshd','NETWORK_FAIL')
  # Initial failed permissions, unsuccessful 0600 repair, unsafe 0644 repair,
  # and least-privilege repair exercise actual access as two different users.
  line('if sudo runuser -u ll-service -- cat /etc/learning-lab/access.conf; then echo INITIAL_ACCESS >> ~/admin-fixture-failures; fi')
  line('sudo chmod 0600 /etc/learning-lab/access.conf')
  line('if sudo runuser -u ll-service -- cat /etc/learning-lab/access.conf; then echo WRONG_0600 >> ~/admin-fixture-failures; fi')
  line('sudo chmod 0644 /etc/learning-lab/access.conf')
  assertion('sudo runuser -u nobody -- cat /etc/learning-lab/access.conf','BROAD_MODE_NOT_DETECTED')
  line('sudo chgrp ll-service /etc/learning-lab/access.conf; sudo chmod 0640 /etc/learning-lab/access.conf')
  assertion('sudo runuser -u ll-service -- cat /etc/learning-lab/access.conf','NARROW_READ_FAIL')
  line('if sudo runuser -u nobody -- cat /etc/learning-lab/access.conf; then echo BROAD_ACCESS >> ~/admin-fixture-failures; fi')
  # Syntactically valid ExecStart can still fail at runtime; no restart loop.
  line('printf "[Service]\\nExecStart=\\nExecStart=/bin/false\\n" | sudo tee /etc/systemd/system/ll-override.service.d/broken.conf')
  assertion('sudo systemd-analyze verify ll-override.service && sudo systemctl daemon-reload','SYNTAX_FAIL')
  line('sudo systemctl start ll-override; sleep 1')
  assertion('test "$(systemctl is-active ll-override)" = failed','RUNTIME_FAILURE_NOT_OBSERVED')
  assertion('test "$(systemctl show ll-override -p Restart --value)" = no','RESTART_LOOP')
  # Original selector is valid configuration, but it does not route local5.
  line('logger -t ll-safety -p local5.notice "WRONG_ROUTE_MARKER"; sleep 1')
  assertion('sudo journalctl -t ll-safety --no-pager | grep -q WRONG_ROUTE_MARKER','JOURNAL_MISSING')
  line('if sudo grep -q WRONG_ROUTE_MARKER /var/log/learning-lab/events.log; then echo WRONG_ROUTE >> ~/admin-fixture-failures; fi')
  assertion('sudo rsyslogd -N1','ORIGINAL_LOG_SYNTAX_FAIL')
  # A failed debug preview must not create state or mutate the source log.
  line('printf "first\\n" | sudo tee /var/log/learning-lab/rotation.log; sudo chmod 0640 /var/log/learning-lab/rotation.log')
  line('before=$(sudo sha256sum /var/log/learning-lab/rotation.log)')
  line('if sudo logrotate --debug --state /var/lib/learning-lab/rotation.state /etc/learning-lab/rotation.conf; then echo INVALID_ROTATE_ACCEPTED >> ~/admin-fixture-failures; fi')
  assertion('test "$before" = "$(sudo sha256sum /var/log/learning-lab/rotation.log)" && test ! -e /var/lib/learning-lab/rotation.state','DEBUG_MUTATION')
  line('sudo sed -i "s/0999/0640/" /etc/learning-lab/rotation.conf')
  assertion('sudo logrotate --debug --state /var/lib/learning-lab/rotation.state /etc/learning-lab/rotation.conf','VALID_ROTATION_FAIL')
  line('for n in 1 2 3; do printf "record %s\\n" "$n" | sudo tee /var/log/learning-lab/rotation.log; sudo logrotate --force --state /var/lib/learning-lab/rotation.state /etc/learning-lab/rotation.conf; done')
  assertion('sudo grep -qx "record 3" /var/log/learning-lab/rotation.log.1 && sudo grep -qx "record 2" /var/log/learning-lab/rotation.log.2','ROTATION_ORDER_FAIL')
  assertion('test ! -e /var/log/learning-lab/rotation.log.3 && test ! -s /var/log/learning-lab/rotation.log && test "$(stat -c %a:%U:%G /var/log/learning-lab/rotation.log)" = 640:root:adm','ROTATION_BOUND_FAIL')
  # Test the actual cgroup values, not just unit-file strings. No exhaustion.
  bound_started=time.monotonic()
  line('started=$(date +%s); sudo systemctl start ll-lifecycle; pid=$(systemctl show ll-lifecycle -p MainPID --value)')
  assertion('test "$(cat /sys/fs/cgroup/system.slice/ll-lifecycle.service/memory.max)" = 67108864','MEMORY_LIMIT_FAIL')
  assertion('test "$(cat /sys/fs/cgroup/system.slice/ll-lifecycle.service/pids.max)" = 8','TASK_LIMIT_FAIL')
  assertion('test "$(cat /sys/fs/cgroup/system.slice/ll-lifecycle.service/cpu.max)" = "20000 100000"','CPU_LIMIT_FAIL')
  assertion('sudo cat /proc/"$pid"/limits | grep -E "Max file size +1048576 +1048576"','FILE_LIMIT_FAIL')
  assertion('test "$(ps -o user= -p "$pid" | tr -d " ")" = ll-service','WORKER_ROOT')
  shot('live-service-limits')
  # Worker itself exits at 120s and RuntimeMaxSec independently bounds it;
  # either orderly inactive or timeout/failed is valid at the boundary race.
  line('while [ "$(systemctl show ll-lifecycle -p MainPID --value)" != 0 ] && [ "$(($(date +%s)-started))" -lt 127 ]; do sleep 1; done; elapsed=$(($(date +%s)-started)); printf "%s\\n" "$elapsed" > ~/admin-runtime-seconds',delay=.2)
  time.sleep(max(0,124-(time.monotonic()-bound_started)))
  assertion('test "$(systemctl show ll-lifecycle -p MainPID --value)" = 0','RUNTIME_BOUND_FAIL')
  # Successful inactive units can lose cached ExecMain timestamps (both zero).
  # Capture elapsed time at the polling observation, and retain journal evidence.
  assertion('test "$(cat ~/admin-runtime-seconds)" -ge 119 && test "$(cat ~/admin-runtime-seconds)" -le 126','RUNTIME_TIMING_FAIL')
  line('sudo journalctl -u ll-lifecycle -o short-monotonic --no-pager > ~/admin-runtime-journal.txt; cat ~/admin-runtime-seconds; cat ~/admin-runtime-journal.txt')
  shot('runtime-duration')
  line('printf "message=%0121d\\n" 0 | sudo tee /etc/learning-lab/lifecycle.conf; sudo systemctl start ll-lifecycle; sleep 1')
  assertion('test "$(systemctl is-active ll-lifecycle)" = failed && sudo journalctl -u ll-lifecycle --no-pager | grep -q LAB_CONFIG_TOO_LONG','CONFIG_BOUND_FAIL')
  assertion('test "$(sudo journalctl -u ll-lifecycle --no-pager | wc -c)" -lt 16384','OUTPUT_BOUND_FAIL')
  line('sudo systemctl stop ll-lifecycle ll-override; printf "retained-marker\\n" > ~/admin-resume-marker')
  read_marker('safety-first','PASSED');check('actual incorrect repairs and guest bounds',True)
  check('safety clean Stop',active.stop()=='Cleanly stopped');running=False
  record=active.status()['session'];active=Sessions(a.vm_home,sessions.profile).manager(id)
  check('same-profile process restart pins',active.status()['session']==record)
  active.start();running=True;time.sleep(20)
  assertion('test "$(cat ~/admin-resume-marker)" = retained-marker','RESUME_DISK_FAIL')
  assertion('test -z "$(pgrep -u ll-service -f admin-worker)"','RESUMED_PROCESS_FAIL')
  read_marker('disk-resume','PASSED');check('disk Resume preserved marker not worker RAM',True)
  check('Resume clean Stop',active.stop()=='Cleanly stopped');running=False
  disk=a.vm_home/'profiles'/active.profile/'generations'/first['generation']/'disk.qcow2'
  with disk.open('rb') as f:before=hashlib.file_digest(f,'sha256').hexdigest()
  new=active.reset('Challenge',True)
  with disk.open('rb') as f:check('Reset retained generation bytes',hashlib.file_digest(f,'sha256').hexdigest()==before)
  check('Reset unique generation and pins',new['generation']!=first['generation'] and new['pin']==first['pin'])
  active.start('Challenge');running=True;time.sleep(20)
  line(': > ~/admin-fixture-failures')
  assertion('test ! -e ~/admin-resume-marker && test "$(stat -c %a:%U:%G /etc/learning-lab/access.conf)" = 640:root:root','RESET_INITIAL_STATE_FAIL')
  read_marker('fresh-reset','PASSED');check('Reset fresh guest and original faults',True)
  check('Reset clean Stop',active.stop()=='Cleanly stopped');running=False
  with active.access() as (root,g,p):
   fd=active.image(root)
   try:check('safety base unchanged',sha256(fd)==active.spec['sha256'])
   finally:os.close(fd)
 finally:
  if running:report['failure_cleanup']=active.stop()
  report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2))
 print('Safety evidence',out,flush=True)
if a.availability_only:
 # Isolated in-memory catalog changes only. No bundled trust/resource or existing
 # session is altered. Exercise actual verified process/QMP Stop, not a mock.
 from learning_lab.vm_preview.image_catalog import digest
 for id in (LEGACY_ID,'real-linux-admin-change'):
  active=sessions.manager(id);running=False
  try:
   saved=active.reset('Learn',True);active.start();running=True;time.sleep(20)
   record=json.loads((active.gate_root/'running.json').read_text())
   check(id+' verified live process',same_process(record))
   before=(a.vm_home/'profiles'/active.profile/'current.json').read_bytes()
   cat=active.catalog;image_key=digest(active.spec)
   cat.images[image_key]['state']='withdrawn'
   for operation in ('new','resume','reset'):
    try:cat.allow(saved['pin'],id,operation);raise AssertionError('withdrawn allowed')
    except Refused:check(id+' withdrawal blocks '+operation,True)
   # Stop discovery must survive missing retained content without resolving pins.
   cat.images.pop(image_key)
   selected='real-linux-capacity-baseline';sessions.select(selected)
   view=sessions.view(selected)
   check(id+' missing descriptor routes control-only Stop',view['running_lesson_id']==id and view['running_state']=='control-only')
   check(id+' unavailable clean Stop',sessions.running_manager(selected).stop()=='Cleanly stopped');running=False
   check(id+' real process exited',not same_process(record))
   check(id+' saved pins and progress unchanged',(a.vm_home/'profiles'/active.profile/'current.json').read_bytes()==before)
   lifecycle=json.loads((a.vm_home/'profiles'/active.profile/'generations'/saved['generation']/'lifecycle.json').read_text())
   check(id+' clean lifecycle durable',lifecycle['state']=='stopped')
   for action in (active.start,lambda:active.reset(confirmed=True)):
    try:action();raise AssertionError('unavailable allowed')
    except Refused:check(id+' unavailable boot/reset refused',True)
   # The base check does not need the now-unavailable catalog revision.
   with active.access() as (root,g,p):
    fd=active.image(root)
    try:check(id+' unchanged base',sha256(fd)==active.spec['sha256'])
    finally:os.close(fd)
  finally:
   if running:report['failure_cleanup']=active.stop()
   report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2))
 print('Availability evidence',out,flush=True);sys.exit(0)

if a.legacy_profile_key:
 from learning_lab.vm_preview.catalog_manager import CatalogManager
 assert re.fullmatch('[a-f0-9]{64}',a.legacy_profile_key)
 active=CatalogManager(a.vm_home,a.legacy_profile_key,lesson_id='real-linux-capacity-baseline')
 current=a.vm_home/'profiles'/a.legacy_profile_key/'current.json';before=current.read_bytes();saved=active.status()['session'];running=False
 try:
  check('prior session uses exact unprivileged image',saved['pin']['image']['image_id']=='debian13-jobs-local-v1')
  active.start();running=True;time.sleep(20)
  line(': > ~/admin-fixture-failures')
  assertion('test "$(cat ~/installed-wheel-smoke.txt)" = wheel-smoke-marker','LEGACY_MARKER_FAIL')
  assertion('test "$(id -u)" -ne 0 && test ! -e /etc/sudoers.d/learning-lab','LEGACY_PRIVILEGE_CHANGED')
  line('if sudo -n true; then echo LEGACY_SUDO >> ~/admin-fixture-failures; fi')
  read_marker('legacy-resume','PASSED');check('actual pre-batch disk resumed unprivileged',True)
  check('legacy clean Stop',active.stop()=='Cleanly stopped');running=False
  check('old session bytes unchanged',current.read_bytes()==before)
  with active.access() as (root,g,p):
   fd=active.image(root)
   try:check('old base unchanged',sha256(fd)==active.spec['sha256'])
   finally:os.close(fd)
 finally:
  if running:report['failure_cleanup']=active.stop()
  report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2))
 print('Legacy evidence',out,flush=True);sys.exit(0)

if a.safety_only:
 safety_proof();sys.exit(0)

started_sequence=not bool(a.from_lesson)
for entry in catalog('linux-administration-services-logs-recovery')['entries']:
 id=entry['id'];slug=id.removeprefix('real-linux-admin-')
 if a.from_lesson==id:started_sequence=True
 if not started_sequence:continue
 if a.only and a.only!=id:continue
 for mode in a.modes:
  active=sessions.manager(id);running=False;started=time.monotonic();info={'id':id,'mode':mode}
  try:
   # Each mode uses a new disk; no real learning/profile/session is touched.
   s=active.reset(mode,True);active.start(mode);running=True;print('BOOT',id,mode,flush=True);time.sleep(20)
   sessions.select(LEGACY_ID);view=sessions.view(LEGACY_ID)
   check(id+' '+mode+' cross-unit Stop routing',view['running_lesson_id']==id)
   try:sessions.manager(LEGACY_ID).start();raise AssertionError('Second VM allowed')
   except Refused as exc:check(id+' '+mode+' second launch refused','already running' in str(exc))
   line(': > ~/admin-fixture-failures')
   line('sudo -n true || echo PRIVILEGE_FAIL >> ~/admin-fixture-failures')
   for command in COMMANDS[id]:
    if command=='sudo systemctl reboot':
     line('cat /proc/sys/kernel/random/boot_id > ~/admin-previous-boot')
     line(command,delay=20)
     assertion('test "$(cat ~/admin-previous-boot)" != "$(cat /proc/sys/kernel/random/boot_id)"','NO_REBOOT')
    else:line(command,delay=2 if 'nano ' in command else 1)
    if 'nano ' in command:edit(slug)
   verify(slug);info['screenshot']=read_marker(id+'-'+mode,'PASSED')
   active.progress('complete');record=active.status()['session'];check(id+' '+mode+' self-review only',record['completion']['kind']=='self-reviewed' and 'score' not in record)
   stop=sessions.running_manager(LEGACY_ID).stop();running=False;check(id+' '+mode+' clean Stop',stop=='Cleanly stopped')
   check(id+' '+mode+' same-profile reopen',Sessions(a.vm_home,sessions.profile).manager(id).status()['session']==record)
   with active.access() as (root,g,p):
    fd=active.image(root)
    try:check(id+' '+mode+' base unchanged',sha256(fd)==active.spec['sha256'])
    finally:os.close(fd)
   info.update(result='PASS',session=s['session'],generation=s['generation'],seconds=round(time.monotonic()-started,2),stop=stop)
  finally:
   if running:
    try:info['failure_cleanup']=active.stop()
    except Exception as exc:info['failure_cleanup']='BLOCKED: '+str(exc)
   report['lessons'].append(info);report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2))
print('Evidence',out,flush=True)
