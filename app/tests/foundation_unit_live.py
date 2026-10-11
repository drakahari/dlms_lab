"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,base64,gzip,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--family',choices=['text','operations'],required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
if a.family=='text':
 from text_archive_guest_fixtures import COMMANDS,UNIT,DATA
 fixture_name='text_archive_guest_fixtures.py'
else:
 from operations_guest_fixtures import COMMANDS,UNIT,DATA
 fixture_name='operations_guest_fixtures.py'
from guest_screen import marker as acknowledgement,matches,locate_calibration,vi_ready,nano_ready
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process,verify_launch
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
assert a.vm_home.is_absolute() and a.vm_home.parent.is_dir() and not a.vm_home.parent.is_symlink() and a.vm_home.parent.stat().st_uid==os.getuid(), 'Owned persistent evidence parent required'
out=Path(tempfile.mkdtemp(prefix='foundation-live-',dir=a.vm_home.parent));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name(fixture_name).read_bytes())
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
 qmp('input-send-event',{'events':[{'type':'key','data':{'down':False,'key':{'type':'qcode','data':c}}} for c in ('ctrl','ctrl_r','shift','shift_r','alt','alt_r')]})
 record_event('control-key',key=k,hold_ms=50)
 qmp('human-monitor-command',{'command-line':'sendkey '+k+' 50'});time.sleep(.08)
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

def send_line(t,delay=.45):
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
deferred=None
def assert_guest(command,label):
 if deferred is not None:
  deferred.append((command,label));return
 record_event('independent-assertion',label=label,command=command)
 line(command);check(label,True)

def clean(fixture):
 assert_guest(fixture['cleanup_command'],'displayed preflight and exact cleanup '+fixture['id'])
 assert_guest('! clean_family && test ! -e "$w" && test ! -L "$w"','repeated cleanup refuses missing workspace '+fixture['id'])


def line(command):
 # Compression only transports a STATIC developer literal through normal guest
 # console keystrokes; no agent/share/network or application JSON execution.
 assert len(command.encode())<=16384 and '\x00' not in command
 payload=command+'\n';raw=payload.encode();encoded=base64.b64encode(gzip.compress(raw,mtime=0)).decode()
 digest=hashlib.sha256(raw).hexdigest();record_event('static-fixture-source',command=command,sha256=digest)
 (out/('static-'+str(command_sequence+1).zfill(4)+'.sh')).write_bytes(raw)
 assert re.fullmatch('[A-Za-z0-9+/=]+',encoded)
 transport='test -f "$dev" && test ! -L "$dev" && test "$(stat -c %U:%a:%h "$dev")" = learner:600:1 && printf %s '+"'"+encoded+"'"+' | base64 -d | gzip -d > "$dev" && test "$(sha256sum "$dev" | cut -d " " -f1)" = '+digest+' && . "$dev"'
 assert len(transport)<4096
 send_line(transport)

def line_many(values):
 """Same-shell STATIC steps; pause after each exact acknowledgement for capture.
 Every original command is unchanged; its function status stops the batch on
 failure. No assertion is passed until its marker is observed. No set-e/retry.
 """
 global command_sequence
 values=list(values)
 while values:
  group=[];script=''
  for command,label in values:
   seq=command_sequence+len(group)+1;token=acknowledgement(seq)
   addition='fixed_developer_step() { '+command+'; }; if fixed_developer_step; then printf "\\n'+token+'\\n"; else echo LOCAL_COMMAND_FAILED; return 1; fi; '
   trial=script+addition+'IFS= read -r _developer_continue || return 1; '
   encoded=base64.b64encode(gzip.compress(trial.encode(),mtime=0)).decode()
   if len(trial.encode())>16000 or len(encoded)+550>=4096:
    assert group,'One fixed step exceeds transport bounds';break
   script=trial;group.append((command,label,seq,token))
  script=script.removesuffix('IFS= read -r _developer_continue || return 1; ')+'\n'
  raw=script.encode();digest=hashlib.sha256(raw).hexdigest();encoded=base64.b64encode(gzip.compress(raw,mtime=0)).decode()
  for command,label,seq,token in group:
   record_event('static-fixture-source',command=command,sha256=hashlib.sha256((command+'\n').encode()).hexdigest(),sequence=seq,label=label)
   (out/('batch-step-'+str(seq).zfill(4)+'.sh')).write_text(command+'\n')
  (out/('batch-'+str(group[0][2]).zfill(4)+'.sh')).write_bytes(raw)
  transport='if test -f "$dev" && test ! -L "$dev" && test "$(stat -c %U:%a:%h "$dev")" = learner:600:1 && printf %s '+"'"+encoded+"'"+' | base64 -d | gzip -d > "$dev" && test "$(sha256sum "$dev" | cut -d " " -f1)" = '+digest+'; then . "$dev"; else echo LOCAL_COMMAND_FAILED; fi'
  assert len(transport)<4096 and len(raw)<=16384
  record_event('batch-transport',sha256=digest,command=transport,steps=[{'sequence':i,'label':l} for _,l,i,_ in group])
  key('ctrl-u');text(transport);key('ret')
  for index,(command,label,seq,token) in enumerate(group):
   await_ack('batch-command-'+str(seq).zfill(4),token)
   command_sequence=seq;check(label,True)
   if index<len(group)-1:key('ret')
  values=values[len(group):]

for fixture in DATA:
 ident=fixture['id'];slug=fixture['slug']
 if a.only and ident!=a.only:continue
 if a.from_lesson and list(COMMANDS).index(ident)<list(COMMANDS).index(a.from_lesson):continue
 for mode in a.modes:
  active=sessions.manager(ident);running=False;info={'id':ident,'mode':mode};started=time.monotonic()
  try:
   saved=active.reset(mode,True);active.start(mode);running=True;boot_ready()
   send_line('dev=$(mktemp "$HOME/developer-static.XXXXXX") && test "$(stat -c %U:%a:%h "$dev")" = learner:600:1')
   assert_guest('test "$(id -un)" = learner && test "$(ls /sys/class/net)" = lo','ordinary learner and offline '+ident)
   if fixture['admin']:
    assert_guest('test "$(sudo -n id -u)" = 0 && sudo passwd -S learner | grep -q " L "','approved guest policy '+ident)
    line('protected=$( { getent passwd learner root ll-service nobody; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)')
   sessions.select(LEGACY_ID)
   check('running controls associated '+ident,sessions.view(LEGACY_ID)['running_lesson_id']==ident)
   foreign=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest()).manager(LEGACY_ID)
   try:foreign.start();raise AssertionError('Foreign VM started')
   except Refused as exc:check('cross-profile refusal '+ident,'already running' in str(exc))
   report.setdefault('candidate_hashes',{})[ident]=hashlib.sha256(Path(__file__).with_name(fixture_name).read_bytes()).hexdigest()
   chosen=fixture['commands'] if mode=='Learn' else fixture['challenge_commands']
   line_many([(c,ident+' '+mode+' actual step '+str(i)) for i,c in enumerate(chosen)])
   deferred=[]
   for i,command in enumerate(fixture['assertions']):assert_guest(command,ident+' expected '+str(i))
   for i,command in enumerate(fixture['negative']):assert_guest(command,ident+' incorrect alternative '+str(i))
   assert_guest('here && printf "retained\\n" > collision.txt && ! fresh collision.txt && grep -qx retained collision.txt && rm -- collision.txt && ln -s missing dangling && ! fresh dangling && rm -- dangling','collision and dangling refusal '+ident)
   assert_guest('here && held="$w.held" && test ! -e "$held" && test ! -L "$held" && mv -- "$w" "$held" && ln -s "$held" "$w" && ! here && test -L "$w" && rm -- "$w" && mv -- "$held" "$w" && here','workspace substitution refusal '+ident)
   for directory in fixture['directories']:
    assert_guest('here && mv -- '+__import__('shlex').quote(directory)+' '+__import__('shlex').quote(directory+'.held')+' && ln -s '+__import__('shlex').quote(Path(directory).name+'.held')+' '+__import__('shlex').quote(directory)+' && ! dir_ok '+__import__('shlex').quote(directory)+' && rm -- '+__import__('shlex').quote(directory)+' && mv -- '+__import__('shlex').quote(directory+'.held')+' '+__import__('shlex').quote(directory)+' && dir_ok '+__import__('shlex').quote(directory),'nested substitution refusal '+ident+' '+directory)
   definition=fixture['cleanup_command'].removesuffix('; clean_family')
   assert_guest(definition+'; printf "retain\\n" > unexpected.txt && ! clean_family && here && grep -qx retain unexpected.txt && rm -- unexpected.txt','cleanup unexpected member preserves workspace '+ident)
   leaf=fixture['files'][0]
   from foundation_guest_fixtures import quote
   assert_guest('here && test "$(stat -c %s -- '+quote(leaf)+')" -le 4096 && saved_leaf=$(base64 -w0 -- '+quote(leaf)+') && saved_mode=$(stat -c %a -- '+quote(leaf)+') && other_before=$(sha256sum -- '+ ' '.join(quote(f) for f in fixture['files'][1:]) +') && rm -- '+quote(leaf)+' && mkdir '+quote(leaf)+' && ! clean_family && here && test "$other_before" = "$(sha256sum -- '+ ' '.join(quote(f) for f in fixture['files'][1:]) +')" && rmdir -- '+quote(leaf)+' && printf %s "$saved_leaf" | base64 -d > '+quote(leaf)+' && chmod "$saved_mode" '+quote(leaf),'isolated cleanup wrong type preserves other files '+ident)
   if fixture['admin']:assert_guest('test "$protected" = "$( { getent passwd learner root ll-service nobody; id learner; sudo sha256sum /etc/sudoers.d/learning-lab; } | sha256sum)"','accounts and sudo unchanged '+ident)
   clean(fixture)
   queued=deferred;deferred=None;line_many(queued)
   send_line('test -f "$dev" && test ! -L "$dev" && test "$(stat -c %U:%a:%h "$dev")" = learner:600:1 && rm -- "$dev"')
   shot(ident+'-'+mode+'-verified')
   if mode=='Learn':active.progress('next');active.progress('hint')
   else:
    for op in ('next','hint'):
     try:active.progress(op);raise AssertionError('Challenge guidance permitted')
     except Refused:pass
   active.progress('complete');record=active.status()['session']
   check('self-reviewed unscored '+ident,record['completion']['kind']=='self-reviewed' and 'score' not in record)
   check('clean Stop '+ident,active.stop()=='Cleanly stopped');running=False;runtime_event('clean-stop')
   check('reopen exact record '+ident,Sessions(a.vm_home,sessions.profile).manager(ident).status()['session']==record)
   with active.access() as (root,g,p):
    fd=active.image(root)
    try:check('unchanged base '+ident,sha256(fd)==active.spec['sha256'])
    finally:os.close(fd)
   info.update(result='PASS',pin=saved['pin'],session=saved['session'],generation=saved['generation'],seconds=round(time.monotonic()-started,2),fixture=fixture)
  except Exception as exc:info.update(result='FAIL',error=repr(exc));raise
  finally:
   if running:
    try:info['failure_cleanup']=active.stop()
    except Exception as exc:info['failure_cleanup']='BLOCKED: '+str(exc)
   report['lessons'].append(info);report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2));print('Evidence',out,flush=True)
