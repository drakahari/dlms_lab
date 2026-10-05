"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bash_guest_fixtures import COMMANDS,SCRIPT_ROWS
from guest_screen import marker as acknowledgement,matches,locate_calibration,vi_ready,nano_ready
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process,verify_launch
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
out=Path(tempfile.mkdtemp(prefix='bash-unit-live-'));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name('bash_guest_fixtures.py').read_bytes())
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
  key('ctrl-q');line('clear');line('if [ -s ~/bash-fixture-failures ] || [ \"$(wc -l < ~/bash-fixture-successes)\" -ne '+str(assertion_count)+' ]; then echo FAILED; cat ~/bash-fixture-failures; else echo '+marker+'; fi')
  path=shot(name+'-'+str(attempt));ocr=subprocess.run(['/usr/bin/tesseract',str(path),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout;(out/(path.name+'.txt')).write_text(ocr)
  if re.search(r'(?m)^'+marker+r'\s*$',ocr):return path.name
  if re.search(r'(?m)^FAILED\s*$',ocr):raise AssertionError('Guest assertion failure: '+ocr)
 raise AssertionError('Unreadable guest evidence, not PASS: '+str(out))
assertion_count=0
def assertion(command,label):
 global assertion_count
 assertion_count+=1
 line(command+' && echo '+label+' >> ~/bash-fixture-successes || echo '+label+' >> ~/bash-fixture-failures')

editor_counts={}
def editor(slug,command):
 editor_counts[slug]=editor_counts.get(slug,0)+1
 path=shot('editor-'+slug+'-'+uuid.uuid4().hex[:6])
 ocr=subprocess.run(['/usr/bin/tesseract',str(path),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout
 (out/(path.name+'.txt')).write_text(ocr)
 if 'nano ' in command:
  from PySide6.QtGui import QImage
  header=out/(path.stem+'-header.png');img=QImage(str(path));assert not img.isNull();img.copy(0,0,img.width(),16).scaled(img.width()*2,32).save(str(header))
  title=subprocess.run(['/usr/bin/tesseract',str(header),'stdout','--psm','7'],capture_output=True,text=True,check=True).stdout
  (out/(header.name+'.txt')).write_text(title)
  compact=''.join(title.split())
  assert 'GNUnano' in compact and ('handover.txt' if command=='nano handover.txt' else 'report.sh' if slug=='handover' else 'guarded.sh' if slug=='guards' else slug+'.sh' if slug!='script' else 'check-note.sh') in compact,'Nano header/file not verified: '+str(header)
  key('ctrl-home')
  if slug=='handover' and 'report.sh' in command:
   for _ in range(3):key('ctrl-k')
  rows=SCRIPT_ROWS[slug] if slug in SCRIPT_ROWS else []
  if command=='nano handover.txt':rows=['FAULT: count-only script lacked guards and names','CHANGE: bounded records, exact format, explicit statuses','EVIDENCE: two FAIL lines, ok=1 fail=2, bad input status 3','LIMIT: synthetic input; not live service diagnosis','ROLLBACK: original checksum/mode restored; corrected copy retained']
  for row in rows:text(row);key('ret')
  key('ctrl-o');key('ret');key('ctrl-x');time.sleep(.5)
 else:
  # Real interactive vi, not sed pretending to test an editor.
  key('esc');text('1G');key('j');key('0')
  if slug=='vi':
   text('cw');text('Beta revised');key('esc');text('yy');key('p');text('/Gamma');key('ret');text('dd');text(':wq');key('ret')
  else:
   key('k');text('cw')
   if editor_counts[slug]==1:
    text('wrong');key('esc');key('u');text('cw');text('UNSAVED');key('esc');text(':q!');key('ret')
   else:text('broken');key('esc');text(':wq');key('ret')
  time.sleep(.5)
def verify(slug):
 assertion('test "$(id -u)" -ne 0 && test ! -x /usr/bin/sudo && test "$(ls /sys/class/net)" = lo','UNPRIVILEGED_ISOLATION')
 if slug=='files':
  assertion('cmp "input/red note.txt" "picked/red note.txt" && cmp "input/blue\\path.txt" "picked/blue\\path.txt" && grep -qx keep input/keep.log','COPY_CONTENT')
  assertion('test "$(stat -c %a "input/red note.txt")" = "$(stat -c %a "picked/red note.txt")" && test "$(find picked -type f | wc -l)" -eq 2','COPY_MODES_COUNT')
  line('find input -maxdepth 1 -type f -name "*.txt" -print > discovery.txt; printf "<%s>\\n" no-match-*.absent > no-match.txt')
  assertion('test "$(wc -l < discovery.txt)" -eq 2 && grep -Fx "<no-match-*.absent>" no-match.txt','GLOB_FIND')
 if slug=='environment':
  assertion('test "$PATH" = "$saved_path" && test -z "${LAB_NOTE+x}" && test -z "${note+x}"','PATH_RESTORE')
  line('note="local value"; bash -c \'printf "%s\\n" "${note-unset}"\' > child-local.txt; LAB_NOTE="child value"; export LAB_NOTE; bash -c \'printf "%s\\n" "$LAB_NOTE"\' > child-export.txt; unset LAB_NOTE note')
  assertion('grep -qx unset child-local.txt && grep -qx "child value" child-export.txt','ENVIRONMENT')
 if slug=='quoting':
  line('printf "<%s>\\n" \'$value\' "two words" \'*.txt\' > expected.txt')
  assertion('cmp quoted.txt expected.txt && test ! -e surprise && test -f "back\\slash.txt" && test -f "red note.txt"','QUOTING')
  assertion('test "$(cat location.txt)" = "<$PWD>" && grep -Fx \'literal $(touch surprise)\' literal.txt','LITERAL_SUBSTITUTION')
 if slug=='streams':
  assertion('cmp input.txt copy.txt && test ! -s empty.txt && test -s errors.txt && test "$(cat count.txt)" = 0','STREAM_FILES')
  line('printf "%s\\n" failed=1 default=0 pipefail=1 > expected-status.txt')
  assertion('cmp status.txt expected-status.txt && grep -qx observed observed.txt','PIPELINE_STATUS')
 if slug=='regex':
  line('printf "%s\\n" "app-01 ok" "app-02 fail" > expected.txt')
  assertion('cmp bre.txt expected.txt && cmp ere.txt expected.txt && test "$(wc -l < fixed.txt)" -eq 1 && test "$(wc -l < wildcard.txt)" -eq 2','REGEX_MATCHES')
  assertion('test "$(wc -c < blank.txt)" -eq 1 && test ! -s none.txt && grep -qx none=1 status.txt && grep -qx invalid=2 status.txt && test -s invalid.txt','REGEX_ERRORS_EMPTY')
 if slug=='transform':
  assertion('cmp original.conf working.conf && cmp before.conf working.conf && sha256sum -c original.sha256 && grep -qx "# label=old" candidate.conf && grep -qx "label=new" candidate.conf','TRANSFORM_ROLLBACK')
  line('diff -u original.conf candidate.conf > changes.txt; test "$?" -eq 1 || echo DIFF_STATUS >> ~/bash-fixture-failures')
 if slug=='vi':
  line('printf "%s\\n" Alpha "Beta revised" "Beta revised" > expected.txt; printf "%s\\n" Alpha Beta Gamma > expected-original.txt')
  assertion('cmp note.txt expected.txt && cmp original.txt expected-original.txt && test "$(readlink -f /usr/bin/vi)" = /usr/bin/vim.tiny','VI_SAVED')
 if slug=='rollback':
  assertion('cmp note.txt original.txt && sha256sum -c original.sha256 && grep -qx broken saved-mistake.txt','ROLLBACK')
  line('vi note.txt',2);key('esc');text('1Gcw');text('INTERRUPTED');key('ctrl-c');key('esc');text(':q!');key('ret');time.sleep(.5)
  assertion('cmp note.txt original.txt && test "$(stat -c %a note.txt)" = "$(stat -c %a original.txt)"','INTERRUPTED_EDIT_ROLLBACK')
 if slug=='script':
  line('chmod u-x check-note.sh; timeout -k 2s 5s ./check-note.sh test > denied-out.txt 2> denied-error.txt; rc=$?; chmod u+x check-note.sh; test \"$rc\" -eq 126 || echo EXEC_PERMISSION_FAIL >> ~/bash-fixture-failures')
  assertion('grep -qx "target=<red note.txt>" target.txt && grep -qx run=0 status.txt && grep -qx usage=2 status.txt && test ! -s bad-output.txt && grep -q usage usage.txt','SCRIPT_BEHAVIOR')
  line('cp check-note.sh wrong.sh; sed -i "s/target/WRONG/" wrong.sh; bash -n wrong.sh && timeout -k 2s 5s bash wrong.sh test > wrong-output.txt')
  assertion('grep -qx "WRONG=<test>" wrong-output.txt','SYNTAX_NOT_BEHAVIOR')
 if slug=='guards':
  assertion('grep -qx "ready: ready note.txt" good.txt && test ! -s failed.txt && grep -qx good=0 status.txt && grep -qx missing=3 status.txt && grep -qx empty=4 status.txt && grep -qx content=5 status.txt && grep -qx args=2 status.txt && grep -q usage errors.txt','GUARDS_STATUSES')
  line('cp "ready note.txt" denied.txt; chmod 0000 denied.txt; timeout -k 2s 5s ./guarded.sh denied.txt > denied-out.txt 2> denied-error.txt; rc=$?; chmod 0600 denied.txt; test "$rc" -eq 3 || echo DENIED_STATUS >> ~/bash-fixture-failures')
  assertion('test ! -s denied-out.txt && grep -q unreadable denied-error.txt','PERMISSION_DENIED')
  line('timeout -k 2s 5s ./guarded.sh . > directory-out.txt 2> directory-error.txt; test "$?" -eq 3 || echo DIRECTORY_STATUS >> ~/bash-fixture-failures')
  line('for name in --help -q -; do printf \"READY\\n\" > \"$name\"; timeout -k 2s 5s ./guarded.sh \"$name\" > dash-out.txt 2> dash-error.txt; test \"$?\" -eq 0 || echo OPTION_FILENAME_FAIL >> ~/bash-fixture-failures; done')
  line('printf \"WAIT\\n\" > -q; timeout -k 2s 5s ./guarded.sh -q > dash-out.txt 2> dash-error.txt; test \"$?\" -eq 5 || echo FALSE_READY >> ~/bash-fixture-failures')
 if slug=='records':
  line('printf "%s\\n" "<two words>" "<back\\slash>" "<>" "<tail>" records=4 > expected.txt')
  assertion('cmp result.txt expected.txt && grep -qx records=0 empty-result.txt && test "$(wc -l < partial.txt)" -eq 20 && grep -q "too many" errors.txt','LITERAL_RECORDS')
  line('printf "%s\\n" " boundary spaces " > boundary.txt; timeout -k 2s 5s ./records.sh boundary.txt > boundary-out.txt')
  assertion('grep -Fx "< boundary spaces >" boundary-out.txt','BOUNDARY_WHITESPACE')
  line('head -n 20 too-many.txt > twenty.txt; timeout -k 2s 5s ./records.sh twenty.txt > twenty-out.txt; test "$?" -eq 0 || echo TWENTY_REJECTED >> ~/bash-fixture-failures')
  line('printf "%02049d" 0 > large.txt; timeout -k 2s 5s ./records.sh large.txt > large-out.txt; test "$?" -eq 3 || echo BYTE_BOUND_FAIL >> ~/bash-fixture-failures')
  line('printf "%s\\n" "while :; do :; done" > wrong-loop.sh; timeout -k 1s 1s bash wrong-loop.sh; test "$?" -eq 124 || echo TIMEOUT_FAIL >> ~/bash-fixture-failures',2)
 if slug=='handover':
  line('printf "%s\\n" "FAIL store\\east" "FAIL cache" "ok=1 fail=2" > expected.txt')
  assertion('cmp report.txt expected.txt && cmp repeated.txt expected.txt && cmp original.sh report.sh && sha256sum -c original.sha256 && test "$(stat -c %a original.sh)" = "$(stat -c %a report.sh)"','REPORT_ORIGINAL')
  assertion('grep -q EVIDENCE handover.txt && grep -q ROLLBACK handover.txt','HANDOVER_EVIDENCE')
  line('printf "%s\\n" ok > no-delimiter.txt; timeout -k 2s 5s ./corrected.sh no-delimiter.txt > rejected.txt 2> rejected-error.txt; test "$?" -eq 3 || echo MISSING_DELIMITER >> ~/bash-fixture-failures')
  line('printf "%s\\n" "x|fail" bad > partial-input.txt; timeout -k 2s 5s ./corrected.sh partial-input.txt > partial.txt 2> partial-error.txt; test "$?" -eq 3 || echo PARTIAL_STATUS >> ~/bash-fixture-failures')
  assertion('grep -qx "FAIL x" partial.txt && cmp report.txt expected.txt','PARTIAL_NOT_PUBLISHED')
 assertion('test "$(du -sk . | cut -f1)" -le 128','WORKSPACE_BOUND')


if a.legacy_profile_key or a.safety_only:
 # No mocks: boot the pre-batch session or a new disposable Bash session.
 from learning_lab.vm_preview.catalog_manager import CatalogManager
 id=LEGACY_ID if a.legacy_profile_key else 'real-linux-bash-script'
 active=CatalogManager(a.vm_home,a.legacy_profile_key,lesson_id=id) if a.legacy_profile_key else sessions.manager(id)
 running=False
 try:
  if a.legacy_profile_key:
   assert re.fullmatch('[a-f0-9]{64}',a.legacy_profile_key)
   saved=active.status()['session'];before=(a.vm_home/'profiles'/active.profile/'current.json').read_bytes()
   check('pre-batch legacy exact image',saved['pin']['image']['image_id']=='debian13-jobs-local-v1')
  else:saved=active.reset('Learn',True)
  active.start();running=True;boot_ready();line(': > ~/bash-fixture-failures; : > ~/bash-fixture-successes');assertion_count=0
  assertion('test "$(id -u)" -ne 0 && test ! -x /usr/bin/sudo && test "$(ls /sys/class/net)" = lo','LEGACY_POLICY')
  line('for tool in bash grep sed find diff nano vi timeout cp; do \"$tool\" --version > /tmp/bash-tool-version 2>&1; test \"$?\" -eq 0 || echo TOOL_RUN_FAIL >> ~/bash-fixture-failures; head -2 /tmp/bash-tool-version; done')
  shot('actual-tool-versions')
  if a.legacy_profile_key:
   assertion('f=$(find \"$HOME\" -maxdepth 2 -name note.txt -print -quit); test -n \"$f\" && grep -q \"guest editor works\" \"$f\"','PREBATCH_EDITOR_MARKER')
  else:line('printf "BASH-RESUME-MARKER\\n" > ~/bash-resume-marker')
  read_marker('lifecycle-first','PASSED');check('lifecycle clean Stop',active.stop()=='Cleanly stopped');running=False
  if a.legacy_profile_key:
   check('pre-batch saved-record bytes unchanged',(a.vm_home/'profiles'/active.profile/'current.json').read_bytes()==before)
  else:
   record=active.status()['session'];active=Sessions(a.vm_home,sessions.profile).manager(id)
   check('new process preserves exact lesson/image/generation',active.status()['session']==record)
   active.start();running=True;boot_ready()
   assertion('grep -qx BASH-RESUME-MARKER ~/bash-resume-marker','DISK_RESUME')
   read_marker('lifecycle-resume','PASSED');check('Resume clean Stop',active.stop()=='Cleanly stopped');running=False
   disk=a.vm_home/'profiles'/active.profile/'generations'/saved['generation']/'disk.qcow2'
   old_hash=hashlib.sha256(disk.read_bytes()).hexdigest();new=active.reset('Challenge',True)
   check('retained Reset disk exact bytes',hashlib.sha256(disk.read_bytes()).hexdigest()==old_hash)
   check('unique Reset generation and same pins',new['generation']!=saved['generation'] and new['pin']==saved['pin'])
   active.start('Challenge');running=True;boot_ready();line(': > ~/bash-fixture-failures; : > ~/bash-fixture-successes');assertion_count=0
   assertion('test ! -e ~/bash-resume-marker','RESET_FRESH_DISK')
   read_marker('lifecycle-reset','PASSED');check('fresh Reset clean Stop',active.stop()=='Cleanly stopped');running=False
  with active.access() as (root,g,p):
   fd=active.image(root)
   try:check('lifecycle base unchanged',sha256(fd)==active.spec['sha256'])
   finally:os.close(fd)
 finally:
  if running:report['failure_cleanup']=active.stop()
  report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2))
 print('Lifecycle evidence',out,flush=True);sys.exit(0)

for id,commands in COMMANDS.items():
 if a.only and id!=a.only:continue
 if a.from_lesson and list(COMMANDS).index(id)<list(COMMANDS).index(a.from_lesson):continue
 slug=id.removeprefix('real-linux-bash-');editor_counts[slug]=0
 for mode in a.modes:
  editor_counts[slug]=0;active=sessions.manager(id);running=False;started=time.monotonic();info={'id':id,'mode':mode}
  try:
   saved=active.reset(mode,True);active.start(mode);running=True;print('BOOT',id,mode,flush=True);boot_ready()
   sessions.select(LEGACY_ID);view=sessions.view(LEGACY_ID)
   check(id+' '+mode+' running controls available across units',view['running_lesson_id']==id)
   foreign=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest()).manager(LEGACY_ID)
   try:foreign.start();raise AssertionError('Foreign VM started')
   except Refused as exc:check(id+' '+mode+' real cross-profile exclusion','already running' in str(exc))
   line(': > ~/bash-fixture-failures; : > ~/bash-fixture-successes');assertion_count=0
   for command in commands:
    line(command,2 if 'vi ' in command or 'nano ' in command else .45)
    if command=='vi note.txt' or command.endswith('; vi note.txt') or command=='nano handover.txt' or 'nano report.sh' in command or command.startswith('nano '):editor(slug,command)
   verify(slug);info['screenshot']=read_marker(id+'-'+mode,'PASSED')
   if mode=='Learn':active.progress('next');active.progress('hint')
   else:
    try:active.progress('next');raise AssertionError('Challenge guidance allowed')
    except Refused:pass
    try:active.progress('hint');raise AssertionError('Challenge hint allowed')
    except Refused:pass
   active.progress('complete');record=active.status()['session'];check(id+' '+mode+' self-reviewed unscored',record['completion']['kind']=='self-reviewed' and 'score' not in record)
   check(id+' '+mode+' clean Stop',active.stop()=='Cleanly stopped');running=False;runtime_event('clean-stop')
   check(id+' '+mode+' exact restart metadata',Sessions(a.vm_home,sessions.profile).manager(id).status()['session']==record)
   with active.access() as (root,g,p):
    fd=active.image(root)
    try:check(id+' '+mode+' unchanged base',sha256(fd)==active.spec['sha256'])
    finally:os.close(fd)
   info.update(result='PASS',pin=saved['pin'],session=saved['session'],generation=saved['generation'],seconds=round(time.monotonic()-started,2))
  finally:
   if running:
    try:info['failure_cleanup']=active.stop()
    except Exception as exc:info['failure_cleanup']='BLOCKED: '+str(exc)
   report['lessons'].append(info);report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2))
print('Evidence',out,flush=True)
