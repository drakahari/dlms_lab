"""Fixed developer guest fixtures only. Not imported by the application.
Requires reviewed local image. Uses unique profile bindings, retains every overlay.
Screenshot results need explicit review; input is synthesized, not physical UAT.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');a=p.parse_args()
out=Path(tempfile.mkdtemp(prefix='vm-process-lessons-live-'));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'profile':sessions.profile,'lessons':[]}
def check(n,c):
 if not c:raise AssertionError(n)
 checks.append(n);print(n,flush=True)
def qmp(command,arguments=None):
 r=json.loads((Path('/run/user')/str(os.getuid())/'oll-vm-preview/running.json').read_text())
 with socket.socket(socket.AF_UNIX) as sock:
  sock.settimeout(4);sock.connect(str(Path('/run/user')/str(os.getuid())/'oll-vm-preview'/r['run']/'qmp'));f=sock.makefile('rwb');f.readline()
  def op(c,args):
   f.write((json.dumps({'execute':c,'arguments':args or {}})+'\n').encode());f.flush()
   while True:
    raw=f.readline()
    if not raw:return None
    v=json.loads(raw)
    if 'error' in v:raise AssertionError(v)
    if 'return' in v:return v['return']
  op('qmp_capabilities',{});return op(command,arguments)
def key(k):
 qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});time.sleep(.15)
 # Developer input hygiene only; never part of the app's QMP allowlist.
 qmp('input-send-event',{'events':[{'type':'key','data':{'down':False,'key':{'type':'qcode','data':code}}} for code in ('ctrl','ctrl_r','shift','shift_r','alt','alt_r')]})
 time.sleep(.05)
def line(t):
 basic={' ':'spc','-':'minus','=':'equal','/':'slash','.':'dot',',':'comma',"'":'apostrophe',';':'semicolon','[':'bracket_left',']':'bracket_right','\\':'backslash','`':'grave_accent'}
 shifted={'!':'1','@':'2','#':'3','$':'4','%':'5','^':'6','&':'7','*':'8','(':'9',')':'0','_':'minus','+':'equal',':':'semicolon','"':'apostrophe','<':'comma','>':'dot','?':'slash','|':'backslash','~':'grave_accent','{':'bracket_left','}':'bracket_right'}
 key('ctrl-u')
 for c in t:
  k=('shift-'+c.lower() if c.isupper() else c) if c.isascii() and c.isalnum() else basic[c] if c in basic else 'shift-'+shifted[c]
  qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});time.sleep(.05)
 key('ret');time.sleep(.8)
def lines(*values):
 for t in values:line(t)
def shot(id,suffix):
 time.sleep(1)
 name=id+'-'+suffix+'.png';qmp('screendump',{'filename':str(out/name),'format':'png'});return name
def result(id):
 lines('sleep 1','test -z "$(pgrep -u learner -x sleep)" || echo LEFTOVER >> ~/fixture-failures')
 for attempt in range(3):
  key('ctrl-q') # Resume any terminal flow stop before reading developer evidence.
  lines('clear','if [ -s ~/fixture-failures ]; then echo GUESTCHECKFAIL; cat ~/fixture-failures; else echo GUESTCHECKPASS; fi')
  image=shot(id,'result-'+str(attempt))
  text=subprocess.run(['/usr/bin/tesseract',str(out/image),'stdout','--psm','6'],capture_output=True,text=True,check=True).stdout
  (out/(image+'.txt')).write_text(text)
  if re.search(r'(?m)^GUESTCHECKPASS\s*$',text):return image
  if re.search(r'(?m)^GUESTCHECKFAIL\s*$',text):raise AssertionError('Guest fixture failed: '+text)
 raise AssertionError('Guest evidence not readable; do not claim this exercise passed: '+str(out))
# Static developer fixtures, deliberately independent of executable lesson content.
def inspection():
 lines('sleep 600 & p=$!','ps -o pid,ppid,user,stat,args -p "$p"','ps -u learner -o pid,ppid,ni,stat,args --sort=-pid','ps -o pid,ppid,stat,args -p "$$"','test "$(ps -o ppid= -p "$p" | tr -d " ")" = "$$" || echo PARENT_FAIL >> ~/fixture-failures','kill "$p"; wait "$p"; test $? = 143 || echo TERM_FAIL >> ~/fixture-failures','ps -p "$p" && echo EXIT_FAIL >> ~/fixture-failures')
def foreground():
 line('sleep 600');key('ctrl-z');lines('jobs -l','p=$(jobs -p %+)','ps -o pid,stat,args -p "$p"','bg %+','fg %+');key('ctrl-c');line('test $? = 130 || echo INT_FAIL >> ~/fixture-failures')
def background():
 lines('sleep 300 &','p=$!','jobs -l','ps -o pid,ppid,stat,comm -p "$p"','kill -STOP %+','sleep 1; ps -o pid,stat,args -p "$p"','test "$(ps -o stat= -p "$p" | cut -c1)" = T || echo STOP_FAIL >> ~/fixture-failures','bg %+','job_pid=$(jobs -p %+); kill "$job_pid"; wait "$job_pid"; test $? = 143 || echo TERM_FAIL >> ~/fixture-failures')
def signals():
 lines('sleep 600 & first=$!','sleep 601 & second=$!','pgrep -a -u learner -P "$$" -f "^sleep 600$"','pkill -TERM -u learner -P "$$" -f "^sleep 600$"','wait "$first"; test $? = 143 || echo TARGET_FAIL >> ~/fixture-failures','ps -o pid,user,stat,args -p "$second"','kill -0 "$second" || echo COMPANION_FAIL >> ~/fixture-failures','kill -KILL "$second"; wait "$second"; test $? = 137 || echo KILL_FAIL >> ~/fixture-failures')
def monitor():
 lines('sleep 600 & p=$!','top -u learner');shot('monitor','top');key('q');lines('ps -u learner -o pid,pcpu,pmem,ni,stat,comm --sort=-pcpu',"watch -n 2 'ps -u learner -o pid,ni,stat,comm'");shot('monitor','watch');key('ctrl-c');lines('uptime; free -h','kill "$p"; wait "$p"')
def logout():
 lines('mkdir -p ~/jobs-lab','shopt -s huponexit; shopt -p huponexit','nohup sleep 900 > ~/jobs-lab/nohup.log 2>&1 < /dev/null &','echo $! > ~/jobs-lab/nohup.pid','sleep 900 &','echo $! > ~/jobs-lab/ordinary.pid','sleep 900 &','echo $! > ~/jobs-lab/disowned.pid; disown -h %+','jobs -l','exit');time.sleep(4)
 lines('shopt -p huponexit; jobs -l','ps -o pid,user,ppid,stat,args -p "$(cat ~/jobs-lab/nohup.pid)"','ps -o pid,user,stat,args -p "$(cat ~/jobs-lab/ordinary.pid)"','ps -o pid,user,stat,args -p "$(cat ~/jobs-lab/disowned.pid)"','kill -0 "$(cat ~/jobs-lab/nohup.pid)" || echo NOHUP_FAIL >> ~/fixture-failures','kill -0 "$(cat ~/jobs-lab/disowned.pid)" || echo DISOWN_FAIL >> ~/fixture-failures','kill -0 "$(cat ~/jobs-lab/ordinary.pid)" 2>/dev/null && echo ORDINARY_FAIL >> ~/fixture-failures');shot('logout','observations')
 line('kill "$(cat ~/jobs-lab/nohup.pid)" "$(cat ~/jobs-lab/disowned.pid)"')
def priorities():
 lines('sleep 600 & normal=$!','nice -n 12 sleep 600 & low=$!','ps -o pid,user,ni,stat,args -p "$normal,$low"','renice -n 15 -p "$low"','renice -n 0 -p "$low"','test "$(ps -o ni= -p "$low" | tr -d " ")" = 15 || echo RENICE_FAIL >> ~/fixture-failures','nice -n -1 sleep 600 & denied=$!','ps -o pid,user,ni,stat,args -p "$denied"','test "$(ps -o ni= -p "$denied" | tr -d " ")" = 0 || echo NICE_FAIL >> ~/fixture-failures');shot('priorities','observations');line('kill "$normal" "$low" "$denied"; wait')
def handover():
 lines('mkdir -p ~/handover-lab','sleep 600 & p=$!','nohup nice -n 10 sleep 900 > ~/handover-lab/task.log 2>&1 < /dev/null &','echo $! > ~/handover-lab/task.pid','ps -o pid,user,ppid,ni,stat,args -p "$p,$(cat ~/handover-lab/task.pid)"','kill -STOP "$p"; sleep 1; ps -o pid,stat,args -p "$p"','test "$(ps -o stat= -p "$p" | cut -c1)" = T || echo STOP_FAIL >> ~/fixture-failures','kill -CONT "$p"; kill "$p"; wait "$p"','ps -o pid,user,ppid,ni,stat,args -p "$(cat ~/handover-lab/task.pid)" > ~/handover-lab/report.txt','shopt -s huponexit; exit');time.sleep(4)
 lines('ps -o pid,user,ni,stat,args -p "$(cat ~/handover-lab/task.pid)"; cat ~/handover-lab/report.txt','test "$(ps -o ni= -p "$(cat ~/handover-lab/task.pid)" | tr -d " ")" = 10 || echo SURVIVOR_FAIL >> ~/fixture-failures','test -s ~/handover-lab/report.txt || echo REPORT_FAIL >> ~/fixture-failures');shot('handover','observations');line('kill "$(cat ~/handover-lab/task.pid)"')
fixtures=[inspection,foreground,background,signals,monitor,logout,priorities,handover]
for index,e in enumerate(catalog()['entries']):
 if a.only and e['id']!=a.only:continue
 id=e['id'];m=sessions.manager(id);started=False
 try:
  s=m.start();started=True;print('BOOT',id,flush=True);time.sleep(20)
  other=catalog()['entries'][(index+1)%8]['id'];sessions.select(other);v=sessions.view(other)
  check(id+' running control stays accessible',v['running_lesson_id']==id)
  try:sessions.manager(other).start();raise AssertionError('second VM allowed')
  except Refused as exc:check(id+' second launch blocked','already running' in str(exc))
  foreign=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest())
  try:foreign.manager(id).start();raise AssertionError('foreign launch allowed')
  except Refused as exc:check(id+' cross-profile blocked','already running' in str(exc))
  lines(': > ~/fixture-failures');fixtures[index]();image=result(id)
  m.progress('complete');check(id+' completion self-review only',m.status()['session']['completion']['kind']=='self-reviewed')
  stop=sessions.running_manager(other).stop();started=False;check(id+' Stop from other selection',stop=='Cleanly stopped')
  reopened=Sessions(a.vm_home,sessions.profile).manager(id);check(id+' session reopens',reopened.status()['session']['session']==s['session'])
  with m.access() as (root,g,p):
   fd=m.image(root)
   try:check(id+' base unchanged',sha256(fd)==m.spec['sha256'])
   finally:os.close(fd)
  report['lessons'].append({'id':id,'generation':s['generation'],'result_screenshot':image,'guest_assertions':'GUESTCHECKPASS marker verified by developer OCR; screenshot retained for review','stop':stop})
 finally:
  if started:m.stop()
  report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2))
print('Evidence',out,flush=True)
