"""Explicit developer-only native fault proof; never imported by learner runtime.
Uses the reviewed base and a unique disposable VM profile. Retains every generation.
"""
import argparse,hashlib,json,os,resource,socket,sys,tempfile,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from learning_lab.vm_preview.manager import Manager
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.policy import FILE_CEILING
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);a=p.parse_args()
out=Path(tempfile.mkdtemp(prefix='vm-security-review-'));key=hashlib.sha256(uuid.uuid4().bytes).hexdigest();m=Manager(a.vm_home,key);checks=[];report={'profile_key':key,'evidence':str(out)}
def check(name,value):
 if not value:raise AssertionError(name)
 checks.append(name);print(name,flush=True)
def runtime():return json.loads((m.gate_root/'running.json').read_text())
def qmp(command,arguments=None):
 r=runtime()
 with socket.socket(socket.AF_UNIX) as sock:
  sock.settimeout(3);sock.connect(str(m.gate_root/r['run']/'qmp'));f=sock.makefile('rwb');f.readline()
  def op(c,args):
   f.write((json.dumps({'execute':c,'arguments':args or {}})+'\n').encode());f.flush()
   while True:
    raw=f.readline()
    if not raw:return None
    result=json.loads(raw)
    if 'error' in result:raise AssertionError(result)
    if 'return' in result:return result['return']
  op('qmp_capabilities',{});return op(command,arguments)
def guest(text):
 # Called only with the two fixed developer fixtures below.
 basic={' ':'spc','-':'minus','=':'equal','/':'slash','.':'dot',"'":'apostrophe',';':'semicolon'}
 shifted={'~':'grave_accent','|':'backslash','&':'7','!':'1','>':'dot','_':'minus'}
 qmp('human-monitor-command',{'command-line':'sendkey ctrl-u 5'});time.sleep(.1)
 for c in text:
  if c.isascii() and c.isalnum():key='shift-'+c.lower() if c.isupper() else c
  elif c in basic:key=basic[c]
  else:key='shift-'+shifted[c]
  qmp('human-monitor-command',{'command-line':'sendkey '+key+' 5'});time.sleep(.05)
 qmp('human-monitor-command',{'command-line':'sendkey ret 1'});time.sleep(.5)
def refused(action,fragment):
 try:action()
 except Refused as exc:check(fragment,fragment in str(exc))
 else:raise AssertionError('Expected refusal: '+fragment)
try:
 s=m.start();report['generation']=s['generation'];r=runtime();pid=r['process']['pid'];print('QEMU PID',pid,flush=True)
 other=Manager(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest())
 refused(other.start,'already running');refused(lambda:other.reset(confirmed=True),'already running')
 # A correctly hashed record still cannot grant a different launch policy (unit
 # tested); here corrupt the digest and verify no QMP mutation is sent.
 with m.access() as (_,g,p):
  forged=json.loads(json.dumps(r));forged['process']['argv_sha256']='0'*64;g.write('running.json',forged,replace=True)
 try:refused(m.stop,'Stale or forged')
 finally:
  with m.access() as (_,g,p):g.write('running.json',r,replace=True)
 with m.access() as (_,g,p):
  intent={**r,'state':'intent','process':None};g.write('running.json',intent,replace=True)
 check('live interrupted Start recovered under exact policy',m.status()['state']=='running')
 # Audit sockets owned by this exact QEMU; the host namespace contains unrelated
 # services, so only intersect kernel socket inodes with this process's descriptors.
 inodes=set()
 for fd in Path(f'/proc/{pid}/fd').iterdir():
  try:target=os.readlink(fd)
  except FileNotFoundError:continue
  if target.startswith('socket:['):inodes.add(target[8:-1])
 internet=[]
 for family in ('tcp','tcp6','udp','udp6'):
  for line in Path(f'/proc/{pid}/net/{family}').read_text().splitlines()[1:]:
   cols=line.split()
   if cols[9] in inodes:internet.append({'family':family,'state':cols[3]})
 listeners=[]
 for line in Path(f'/proc/{pid}/net/unix').read_text().splitlines()[1:]:
  cols=line.split()
  if cols[6] in inodes and int(cols[3],16)&0x10000:listeners.append(cols[7] if len(cols)>7 else '(unnamed)')
 check('no QEMU Internet sockets',not internet)
 check('only private QMP listener',listeners==[str(m.gate_root/r['run']/'qmp')])
 report['sockets']={'internet':internet,'unix_listeners':listeners}
 time.sleep(20)
 for command in ('id','command -v sudo || echo NO_SUDO','ls /sys/class/net','ss -lntu','test ! -e ~/.bash_history && echo NO_PRIOR_HISTORY'):
  guest(command)
 qmp('screendump',{'filename':str(out/'guest-access-and-listeners.png'),'format':'png'})
 disk=a.vm_home/'profiles'/key/'generations'/s['generation']/'disk.qcow2'
 before=resource.prlimit(pid,resource.RLIMIT_FSIZE);check('18 GiB kernel file limit inherited',before==(FILE_CEILING,FILE_CEILING))
 limit=disk.stat().st_size+2*1024**2;resource.prlimit(pid,resource.RLIMIT_FSIZE,(limit,limit))
 guest('dd if=/dev/zero of=~/growth-probe bs=1M count=32 conv=fsync')
 for _ in range(50):
  status=qmp('query-status')
  if status['status']=='io-error':break
  time.sleep(.1)
 check('real QEMU I/O paused on file ceiling',status['status']=='io-error')
 check('kernel ceiling not exceeded',disk.stat().st_size<=limit)
 report['file_limit']={'configured':before,'injected_ceiling':limit,'actual_size':disk.stat().st_size,'status':status}
 check('force stop marked unclean','unclean' in m.stop(force=True,confirmed=True))
 refused(m.start,'Unclean')
 digest=hashlib.sha256(disk.read_bytes()).hexdigest();m.reset(confirmed=True)
 check('faulted generation retained byte-for-byte',hashlib.sha256(disk.read_bytes()).hexdigest()==digest)
 report['retained_sha256']=digest
 with m.access() as (root,g,p):
  fd=m.image(root)
  try:check('pinned base hash unchanged',sha256(fd)==m.spec['sha256'])
  finally:os.close(fd)
 report['result']='PASS'
finally:
 r=runtime()
 if r['profile']==key and r['state']=='running':m.stop(force=True,confirmed=True)
 report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2));print('Evidence',out,flush=True)
