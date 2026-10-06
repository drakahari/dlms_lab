"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from backup_guest_fixtures import COMMANDS,UNIT
from guest_screen import marker as acknowledgement,matches,locate_calibration,vi_ready,nano_ready
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process,verify_launch
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
out=Path(tempfile.mkdtemp(prefix='backup-unit-live-'));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name('backup_guest_fixtures.py').read_bytes())
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




def verify(n):
 assertion('guard && test "$(find source -type f | wc -l)" -eq 2 && test -z "$(find . -type l -print)"','EXACT_TRUSTED_SOURCE')
 if n==1:
  assertion('(cd source && sha256sum -c ../expected.sha256) && test "$(wc -l < expected.metadata)" -eq 2 && grep -q RPO requirements.txt','INDEPENDENT_EXPECTATIONS')
 if n in (2,3,4,5):
  assertion("printf 'note.txt\\nspace name.txt\\n' | cmp - <(tar -tf v1.tar)",'EXACT_RELATIVE_MEMBERS')
 if n==3:
  assertion('gzip -t v1.tar.gz && sha256sum -c expected-backup.sha256 && gzip -cd v1.tar.gz | cmp - v1.tar','COMPRESSION_AND_RETAINED_REFERENCE')
 if n==4:
  assertion('tar -tf altered.tar && gzip -t altered.tar.gz && ! gzip -t truncated.gz && ! cmp source/note.txt restore/note.txt && sha256sum -c expected-backup.sha256','VERIFICATION_METHODS_DISTINGUISHED')
  assertion("printf 'Xlpha\\n' | cmp - restore/note.txt",'ALTERED_PAYLOAD_RESTORED_NOT_CORRECT')
 if n==5:
  assertion('cmp source/note.txt restore/note.txt && cmp "source/space name.txt" "restore/space name.txt" && test ! -e "incomplete/space name.txt" && test "$(stat -c %a restore/note.txt)" = 640 && test "$(stat -c %Y restore/note.txt)" = "$(stat -c %Y source/note.txt)"','COMPLETE_BYTES_METADATA_INCOMPLETE_DETECTED')
 if n in (6,8):
  assertion('test "$(stat -c %a v1.tar)" = 600'+(' && test "$(stat -c %a v2.tar)" = 600 && test "$(stat -c %a versions.sha256)" = 600' if n==8 else ''),'PRIVATE_BACKUP_NOT_WORLD_READABLE')
  name='ll-b'+str(n)
  assertion('test "$(sudo runuser -u '+name+' -- id -un)" = '+name+' && test "$(sudo stat -c %U:%G restore/note.txt)" = '+name+':'+name+' && test "$(sudo stat -c %a restore/note.txt)" = 600 && ! cat restore/note.txt', 'ACTUAL_USER_PRIVATE_OWNER_AND_DENIAL')
  assertion("sudo runuser -u "+name+" -- cat restore/note.txt | cmp - <(printf 'alpha\\n')",'INTENDED_IDENTITY_CONTENT_READ')
  line('sudo chmod 0644 restore/note.txt')
  assertion('cat restore/note.txt && test "$(sudo stat -c %a restore/note.txt)" != 600','INCORRECT_BROAD_REPAIR_DETECTED')
  line('sudo chmod 0600 restore/note.txt')
  assertion('! cat restore/note.txt && sudo runuser -u '+name+' -- test -r restore/note.txt','NARROW_ACCESS_RESTORED')
 if n in (7,8):
  assertion("printf 'alpha-v2\\n' | cmp - source/note.txt && printf 'alpha\\n' | sudo cmp - restore/note.txt && sha256sum -c versions.sha256",'OLD_VERSION_RECOVERED_NEW_VERSION_AND_BACKUPS_RETAINED')
 if n==8:
  assertion('test "$(sudo stat -c %Y restore/note.txt)" = 1767225600 && test -s handover.txt','EXPECTED_METADATA_AND_RECOVERY_HANDOVER')
 assertion('test "$(du -sk . | cut -f1)" -le 256 && test "$(df -Pk . | awk \'NR==2 {print $4}\')" -ge 65536','SMALL_FIXTURE_AND_GUEST_RESERVE')

def safety(n,commands):
 # Repeated setup must not adopt existing paths; dangling links aren't absence.
 line('before_workspace=$(stat -c %i .); '+commands[0]+'; repeat_rc=$?')
 assertion('test "$repeat_rc" -ne 0 && test "$before_workspace" = "$(stat -c %i .)"','REPEATED_SETUP_REFUSED')
 line('ln -s /etc link-probe; guard; link_guard_rc=$?')
 assertion('test "$link_guard_rc" -ne 0','LINK_ESCAPE_GUARD_REFUSED')
 line('rm -- link-probe')
 line('cd ..; guard; parent_guard_rc=$?; cd -- /home/learner/ll-backup-'+str(n))
 assertion('test "$parent_guard_rc" -ne 0 && guard','PARENT_PATH_GUARD_REFUSED')
 if n in (2,5):
  line(': > interrupted.tar; mkfifo interrupted.fifo; timeout -k 1s 8s tar -cf interrupted.tar -T interrupted.fifo & archiver=$!; sleep 0.2; kill -INT "$archiver"; wait "$archiver"; interruption_rc=$?; rm -- interrupted.fifo')
  assertion('test "$interruption_rc" -ne 0 && test -f interrupted.tar && ! kill -0 "$archiver" 2>/dev/null && test -f v1.tar','INTERRUPTED_ARCHIVE_RETAINED_EXACT_PROCESS_GONE')
  line('test ! -e retry.tar && timeout -k 1s 10s tar -cf retry.tar -C source -- note.txt "space name.txt"')
  assertion('tar -tf retry.tar && test -f interrupted.tar && test -f v1.tar','SEPARATE_RETRY_RETAINS_EVIDENCE')
 if n in (6,7,8):
  line('prior=$(sudo sha256sum v1.tar source/note.txt); '+commands[4]+'; archive_collision_rc=$?')
  assertion('test "$archive_collision_rc" -ne 0 && test "$prior" = "$(sudo sha256sum v1.tar source/note.txt)"','EXISTING_BACKUP_REFUSED_BEFORE_SOURCE_CHANGE')
 # Test a destination link is rejected BEFORE extraction, while outside unchanged.
 line('test ! -e trap-restore && ln -s /etc trap-restore; test ! -e trap-restore && test ! -L trap-restore && mkdir trap-restore; destination_rc=$?')
 assertion('test "$destination_rc" -ne 0 && test -L trap-restore','DESTINATION_LINK_COLLISION_REFUSED')
 line('rm -- trap-restore')

def cleanup(n):
 # Remove only explicitly named files; never recursive/force/glob/root paths.
 files=['source/note.txt','source/space name.txt']
 extra={1:['requirements.txt','expected.sha256','expected.metadata'],2:['v1.tar','interrupted.tar','retry.tar'],3:['v1.tar','v1.tar.gz','expected-backup.sha256'],4:['v1.tar','expected-backup.sha256','altered.tar','altered.tar.gz','truncated.gz','restore/note.txt','restore/space name.txt'],5:['v1.tar','restore/note.txt','restore/space name.txt','incomplete.tar','incomplete/note.txt','interrupted.tar','retry.tar'],6:['v1.tar','restore/note.txt'],7:['v1.tar','v2.tar','versions.sha256','wrong/note.txt','wrong/space name.txt','restore/note.txt','restore/space name.txt'],8:['v1.tar','v2.tar','versions.sha256','restore/note.txt','handover.txt']}
 dirs={1:['source'],2:['source'],3:['source'],4:['source','restore'],5:['source','restore','incomplete'],6:['source','restore'],7:['source','wrong','restore'],8:['source','restore']}
 line('guard && sudo rm -- '+' '.join("'"+x+"'" for x in files+extra[n])+' && sudo rmdir -- '+' '.join(dirs[n])+' && cd -- /home/learner && rmdir -- /home/learner/ll-backup-'+str(n))
 assertion('test ! -e /home/learner/ll-backup-'+str(n)+' && test ! -L /home/learner/ll-backup-'+str(n),'EXACT_WORKSPACE_CLEANUP')
 if n in (6,8):
  line('umask "$saved_umask"')
  line('sudo userdel ll-b'+str(n)+'; if getent group ll-b'+str(n)+'; then sudo groupdel ll-b'+str(n)+'; fi')
  assertion('! getent passwd ll-b'+str(n)+' && ! getent group ll-b'+str(n),'DISPOSABLE_IDENTITY_CLEANUP')
 # Conditional repeat doesn't remove unrelated paths.
 assertion('test ! -e /home/learner/ll-backup-'+str(n),'REPEATED_CLEANUP_NO_ADOPTION')

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
   line(': > ~/backup-fixture-failures; : > ~/backup-fixture-successes; protected_before=$( { getent passwd learner root ll-service; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)');assertion_count=0
   line('tar --version | head -n 1; gzip --version | head -n 1; stat --version | head -n 1; command -v tar gzip sha256sum cmp timeout stat runuser')
   for command in commands:line(command)
   verify(n);safety(n,commands);cleanup(n)
   # Fresh setup and clean-up after the previous fixture was fully removed.
   line(commands[0]);line(commands[1]);assertion('guard','SETUP_AFTER_CLEANUP')
   line('cd -- /home/learner; rmdir -- /home/learner/ll-backup-'+str(n))
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
