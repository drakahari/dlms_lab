"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from capacity_guest_fixtures import COMMANDS
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
out=Path(tempfile.mkdtemp(prefix='capacity-unit-live-'));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
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
  key('ctrl-q');line('clear');line('if [ -s ~/capacity-fixture-failures ]; then echo FAILED; cat ~/capacity-fixture-failures; else echo '+marker+'; fi')
  path=shot(name+'-'+str(attempt));ocr=subprocess.run(['/usr/bin/tesseract',str(path),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout;(out/(path.name+'.txt')).write_text(ocr)
  if re.search(r'(?m)^'+marker+r'\s*$',ocr):return path.name
  if re.search(r'(?m)^FAILED\s*$',ocr):raise AssertionError('Guest assertion failure: '+ocr)
 raise AssertionError('Unreadable guest evidence, not PASS: '+str(out))
def assertion(command,label):line(command+' || echo '+label+' >> ~/capacity-fixture-failures')
def nano_report():
 # Exercise actual editor, not a fabricated app assessment. Six known skeleton
 # lines are replaced with a small independent report inside the guest only.
 for i in range(6):key('ctrl-k')
 rows=['LIVE FACTS: timestamp and values retained in baseline.txt','SYNTHETIC PLAN: 10 MiB/day; 490 MiB headroom; 49 days from day 21','ASSUMPTIONS: unchanged growth and 100 MiB reserve','RECOMMENDATION: review by day 35, before threshold day 70','MISSING EVIDENCE: retention changes and longer history','CLEANUP: no worker or scratch payload remains']
 for row in rows:text(row);key('ret')
 key('ctrl-o');key('ret');key('ctrl-x');time.sleep(.5)
def verify(slug):
 assertion('test "$PWD" = "$work" && test -d "$work" && test ! -L "$work"','WORKSPACE_FAIL')
 if slug=='baseline':assertion('test -s baseline.txt && grep -q Mem baseline.txt','BASELINE_FAIL')
 if slug=='cpu':
  assertion('grep -q status=124 worker.txt && test -s before.txt && test -s during.txt && test -s after.txt','CPU_TIMER_FAIL')
  assertion('test -z "$(jobs -p)"','CPU_CHILD_FAIL')
  # Real interrupted/repeated cleanup and second-worker refusal on this shell.
  line('timeout -k 2s 12s bash -c \'while :; do :; done\' & worker=$!; sleep 1; birth=$(awk \'{print $22}\' "/proc/$worker/stat")')
  line('if [ -z "$(jobs -p)" ]; then echo SECOND_ALLOWED >> ~/capacity-fixture-failures; else echo SECOND_REFUSED; fi')
  cleanup=COMMANDS['real-linux-capacity-cpu'][4]
  line(cleanup);line(cleanup);assertion('test -z "$(jobs -p)"','CPU_REPEAT_CLEANUP_FAIL')
 if slug=='memory':assertion('grep -q available=1200 memory-example.txt','MEMORY_DATA_FAIL')
 if slug=='io':
  assertion('test ! -e io.bin && test -s write-time.txt && test -s read-time.txt','IO_CLEANUP_FAIL')
  assertion('test "$(df -Pk . | awk \'NR==2 {print $4}\')" -ge 524288','IO_RESERVE_FAIL')
  # Real kernel file-size limit, bounded failure payload; no disk exhaustion.
  line('(ulimit -c 0; ulimit -f 16384; dd if=/dev/zero of=file-limit.bin bs=1M count=17 status=none); limit_rc=$?')
  assertion('test "$limit_rc" -ne 0 && test "$(wc -c < file-limit.bin)" -eq 16777216','KERNEL_LIMIT_FAIL')
  line('rm -f -- file-limit.bin')
  line('available=1; if [ "$available" -ge 540672 ]; then touch refused.bin; fi')
  assertion('test ! -e refused.bin','ADMISSION_FAIL')
  # Foreground interruption: timeout supervises fixed slow regular-file writes.
  line('timeout -k 2s 5s bash -c \'for i in 1 2 3 4; do printf x >> interrupted.bin; sleep 1; done\'',delay=.25);key('ctrl-c');time.sleep(.5)
  assertion('test "$(wc -c < interrupted.bin)" -le 4','INTERRUPTION_LIMIT_FAIL');line('rm -f -- interrupted.bin')
  line(COMMANDS['real-linux-capacity-io'][-1]);line(COMMANDS['real-linux-capacity-io'][-1])
 if slug=='space-inodes':assertion('grep -q "A 1024 500000" shortages.txt && grep -q "B 1048576 0" shortages.txt','SHORTAGE_DATA_FAIL')
 if slug=='trends':
  assertion('test "$(wc -l < history.txt)" -eq 5 && test "$(wc -l < chart.txt)" -eq 4','TREND_ROWS_FAIL')
  assertion('test "$(tr -cd \'#\' < chart.txt | wc -c)" -eq 23','CHART_FAIL')
 if slug in ('forecast','recommendation'):
  assertion('grep -q "rate=10 MiB/day; headroom=490 MiB; days_after_last=49; threshold_day=70" forecast.txt','FORECAST_FAIL')
 if slug=='forecast':assertion('test "$(awk \'NR==2{a=$2} END{print $2-a}\' irregular.txt)" -eq 10 && grep -q "14 300" irregular.txt','IRREGULAR_FAIL')
 if slug=='recommendation':assertion('grep -q "review by day 35" recommendation.txt && ! grep -q "replace with" recommendation.txt','EDITED_REPORT_FAIL')
 # Retained notes after scratch cleanup are small. No stress/exhaustion inference.
 assertion('test "$(du -sk . | cut -f1)" -le 64','NOTE_SIZE_FAIL')

started_sequence=not bool(a.from_lesson)
for entry in catalog('lpic-resource-diagnosis-capacity')['entries']:
 id=entry['id'];slug=id.removeprefix('real-linux-capacity-')
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
   line(': > ~/capacity-fixture-failures')
   line('command -v vmstat free df du awk timeout dd nano; test "$(id -u)" -ne 0 && test ! -x /usr/bin/sudo || echo POLICY_FAIL >> ~/capacity-fixture-failures')
   for command in COMMANDS[id]:
    line(command,delay=15 if slug=='cpu' and command.startswith('if [ -z') else 3 if 'vmstat' in command else .5)
    if command=='nano recommendation.txt':nano_report()
    if slug=='io' and command.startswith('wc -c io.bin'):
     assertion('test "$(wc -c < io.bin)" -eq 16777216','IO_PAYLOAD_FAIL');shot(id+'-'+mode+'-payload')
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
