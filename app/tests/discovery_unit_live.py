"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from discovery_guest_fixtures import COMMANDS,UNIT,CLEANUP,CHALLENGE_FAULTS
from guest_screen import marker as acknowledgement,matches,locate_calibration,vi_ready,nano_ready
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process,verify_launch
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
out=Path(tempfile.mkdtemp(prefix='discovery-unit-live-'));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name('discovery_guest_fixtures.py').read_bytes())
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




def verify_after(n,i):
 if n==7 and i in (4,5):
  version='1.0-1' if i==4 else '1.1-1'
  assertion('test "$(dpkg-query -W -f=\'${Version} ${db:Status-Status}\' ll-discovery-report)" = "'+version+' installed" && test "$(dpkg-query -W -f=\'${db:Status-Status}\' ll-discovery-data)" = installed && ll-discovery-report | grep -F "Known offline fixture data."','ACTUAL_REPORT_VERSION_'+str(i))
 if n==7 and i==6:
  assertion('test "$(dpkg-query -W -f=\'${db:Status-Status}\' ll-discovery-report)" = config-files && test ! -e /usr/bin/ll-discovery-report && grep -Fx format=custom /etc/ll-discovery-report.conf','REMOVAL_RETAINS_DECLARED_CONFIGURATION')
 if n==8 and i==4:
  assertion('test "$(dpkg-query -W -f=\'${db:Status-Status}\' ll-discovery-report)" = unpacked && test "$(dpkg-query -W -f=\'${db:Status-Status}\' ll-discovery-data 2>/dev/null)" != installed','DEPENDENCY_FAILURE_IS_REAL_UNCONFIGURED_STATE')
  # Real POSIX-compatible lock contention: interrupt our bounded waiting APT
  # before acquisition; never kill a different package operation or remove a lock.
  line('sudo flock --fcntl -x /var/lib/dpkg/lock-frontend timeout -k 1s 60s sh -c \'echo ready > /home/learner/ll-discovery-8/lock-ready; while test ! -e /home/learner/ll-discovery-8/stop-lock; do sleep 0.2; done\' & locker=$!; for attempt in $(seq 1 40); do test -e lock-ready && break; sleep 0.1; done; test -e lock-ready')
  line('sudo timeout -k 1s 2s env LC_ALL=C "${apt_base[@]}" -oDpkg::Lock::Timeout=5 install --no-remove "$d" "$r1" > interrupted.txt 2>&1; interrupted_status=$?; : > stop-lock; wait "$locker"')
  assertion('test "$interrupted_status" = 124 && test "$(dpkg-query -W -f=\'${db:Status-Status}\' ll-discovery-report)" = unpacked && test "$(dpkg-query -W -f=\'${db:Status-Status}\' ll-discovery-data 2>/dev/null)" != installed && scope_ok','INTERRUPTED_LOCK_WAIT_PRESERVES_STATE')
 if n==8 and i==5:
  line('declare -p apt_base; sudo env LC_ALL=C "${apt_base[@]}" -s install --no-remove "$d" "$r1"; dpkg-query -W -f=\'${Package} ${db:Status-Status}\\n\' ll-discovery-data ll-discovery-report')
  assertion('test "$(dpkg-query -W -f=\'${db:Status-Status}\' ll-discovery-report)" = installed && ll-discovery-report | grep -F "Known offline fixture data."','DEPENDENCY_REPAIR_CONFIGURES_ACTUAL_REPORT')
 if n==8 and i==6:
  assertion('grep -F usr/share/ll-discovery/message.txt damaged.txt && test "$(cat /usr/share/ll-discovery/message.txt)" = "altered fixture data" && test ! -s verified-before.txt','REAL_PACKAGE_OWNED_CONTENT_MISMATCH')
 if n==8 and i==7:
  assertion('test ! -s verified-after.txt && test "$(cat /usr/share/ll-discovery/message.txt)" = "Known offline fixture data."','REAL_REINSTALL_RESTORES_PACKAGE_OWNED_BYTES')

def verify(n):
 assertion('scope_ok && cd /opt/learning-lab/package-fixtures && sha256sum -c SHA256SUMS > /home/learner/ll-discovery-'+str(n)+'/archive-check.txt && cd /home/learner/ll-discovery-'+str(n)+' && test ! -w /opt/learning-lab/package-fixtures/archives && guard','SOURCE_ARCHIVES_POLICY_AND_UNRELATED_STATE_UNCHANGED')
 assertion('test "$(sudo du -sk . | cut -f1)" -le 256 && test "$(df -Pk . | awk \'NR==2 {print $4}\')" -ge 65536','SMALL_BOUNDED_EVIDENCE_AND_RESERVE')
 if n==1:assertion('grep -F Debian system.txt && grep -F x86_64 system.txt && test -s pci.txt && test -s cpu.txt','REAL_SYSTEM_INVENTORY')
 if n==2:assertion('grep -F "(builtin)" driver.txt && test -s paths.txt && test -s modules.txt','REAL_BUILTIN_MODULE_EVIDENCE')
 if n==3:assertion('grep -F BOOT_IMAGE boot.txt && test -s kernel-log.txt && grep -F "Linux version" early.txt','REAL_CURRENT_BOOT_EVIDENCE')
 if n==4:assertion('grep -F libc.so.6 libraries.txt && grep -F libc.so.6 loader.txt && grep -F libc6 owner.txt','REAL_LIBRARY_AND_PACKAGE_CHAIN')
 if n==5:assertion('grep -F coreutils package.txt && grep -F "ll-discovery-data" archive.txt && grep -F usr/bin/ll-discovery-report members.txt && ! dpkg-query -W ll-discovery-report','ARCHIVE_IS_NOT_INSTALLED_STATE')
 if n==6:assertion('test ! -s verification.txt && test ! -s audit.txt && ! sha256sum -c expected.sha256 && test "$(cat note.txt)" = changed','PACKAGE_CHECKS_SEPARATE_FROM_LEARNER_COPY')
 if n>=7:
  assertion('test "$(dpkg-query -W -f=\'${db:Status-Status}\' ll-discovery-data 2>/dev/null)" != installed && ! dpkg-query -W ll-discovery-report && test ! -e /etc/ll-discovery-report.conf','FIXTURE_PURGE_ONLY')
  line('plan remove coreutils > rejected-plan.txt; rejection_status=$?')
  line('plan purge coreutils > rejected-purge.txt; purge_rejection_status=$?')
  assertion('test "$rejection_status" -ne 0 && test "$purge_rejection_status" -ne 0 && scope_ok','REAL_UNRELATED_APT_PLAN_REJECTED_NO_EXECUTION')
 # Repeat setup refuses the same path including symlink/parent substitution.
 line('inode_before=$(stat -c %i .); '+COMMANDS[list(COMMANDS)[n-1]][0]+'; collision_status=$?')
 assertion('test "$collision_status" -ne 0 && test "$inode_before" = "$(stat -c %i .)" && guard','WORKSPACE_COLLISION_PRESERVES_CONTENTS')
 line('ln -s /etc link-probe; guard; link_status=$?; rm -- link-probe')
 assertion('test "$link_status" -ne 0 && guard','WORKSPACE_LINK_SUBSTITUTION_REJECTED')


def cleanup(n):
 # Remove only extra developer evidence names, then execute the exact displayed
 # learner cleanup. Never substitute a find/delete sweep for those instructions.
 if n==8:line('guard && sudo rm -- lock-ready && rm -- interrupted.txt stop-lock')
 if n>=7:line('guard && rm -- rejected-plan.txt rejected-purge.txt')
 line('guard && rm -- archive-check.txt')
 line(CLEANUP[n])
 assertion('test ! -e /home/learner/ll-discovery-'+str(n),'EXACT_DISPLAYED_WORKSPACE_CLEANUP')
 assertion('test ! -e /home/learner/ll-discovery-'+str(n),'REPEATED_CLEANUP_ALREADY_ABSENT')

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
   line(': > ~/backup-fixture-failures; : > ~/backup-fixture-successes');assertion_count=0
   assertion('test \"$(id -un)\" = learner && test \"$(sudo id -u)\" = 0 && test \"$(cat /usr/local/share/learning-lab/image-id)\" = debian13-package-admin-local-v1 && test \"$(ip -o link show | wc -l)\" = 1 && ! test -x /usr/sbin/sshd && test \"$(ss -lntu | wc -l)\" = 1', 'EXACT_IMAGE_PRIVILEGE_NO_NETWORK_OR_LISTENERS')
   assertion('test "$(dpkg-query -W -f=\'${binary:Package}\\t${Version}\\t${source:Package}\\t${source:Version}\\n\' | sha256sum | cut -d \' \' -f1)" = 22c40a10a16f763fd74749bd36da66547f8619fd6970172cc25da474b43f462b && ! dpkg-query -W ll-discovery-data && ! dpkg-query -W ll-discovery-report','FRESH_EXACT_INVENTORY_FIXTURES_UNINSTALLED')
   assertion('test "$(sudo find /opt/learning-lab/package-fixtures ! -user root -o -type l | wc -l)" = 0 && test "$(sudo find /opt/learning-lab/package-fixtures -type f ! -perm 0444 | wc -l)" = 0','PROTECTED_SOURCE_AND_ARCHIVE_OWNERSHIP_MODES')
   # Fail before any lesson/package transaction if the finalized image differs.
   info['admission_screenshot']=read_marker(id+'-'+mode+'-image-admission','PASSED')
   for i,c in enumerate(commands):
    if mode=='Challenge' and n==8 and i in CHALLENGE_FAULTS:
     line(CHALLENGE_FAULTS[i])
     if i==6:line('sudo dpkg --verify ll-discovery-data > damaged.txt')
    else:line(c)
    verify_after(n,i)
   verify(n);info['screenshot']=read_marker(id+'-'+mode,'PASSED')
   cleanup(n)
   info['cleanup_screenshot']=read_marker(id+'-'+mode+'-cleanup','PASSED')
   line(commands[0]);line(commands[1]);assertion('guard','REPEATED_SETUP_AFTER_CLEANUP')
   line('cd /home/learner; rmdir -- /home/learner/ll-discovery-'+str(n))
   if mode=='Learn':active.progress('next');active.progress('hint')
   else:
    for op in ('next','hint'):
     try:active.progress(op);raise AssertionError('Challenge guidance exposed')
     except Refused:pass
   active.progress('complete');record=active.status()['session'];check(id+' '+mode+' self-reviewed unscored',record['completion']['kind']=='self-reviewed' and 'score' not in record)
   check(id+' '+mode+' clean Stop',active.stop()=='Cleanly stopped');running=False;runtime_event('clean-stop')
   check(id+' '+mode+' reopened pins/mode/progress',Sessions(a.vm_home,sessions.profile).manager(id).status()['session']==record)
   with active.access() as (root,g,p):
    fd=active.image(root)
    try:check(id+' '+mode+' base hash unchanged',sha256(fd)==active.spec['sha256'])
    finally:os.close(fd)
   info.update(result='PASS',pin=saved['pin'],session=saved['session'],generation=saved['generation'],seconds=round(time.monotonic()-started,2))
  finally:
   if running:
    try:info['failure_cleanup']=active.stop()
    except Exception as exc:info['failure_cleanup']='BLOCKED: '+str(exc)
   report['lessons'].append(info);report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2))
print('Evidence',out,flush=True)
