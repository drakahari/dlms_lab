"""STATIC developer fixtures on disposable guests, never a lesson JSON executor.
Uses normal shared controller exclusion; retains all disks/evidence. No force stop.
Native synthesized console input is not physical keyboard or accessibility proof.
"""
import argparse,hashlib,json,os,re,socket,subprocess,sys,tempfile,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--from-lesson');p.add_argument('--modes',nargs='+',choices=['Learn','Challenge'],default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');p.add_argument('--safety-only',action='store_true');p.add_argument('--legacy-profile-key');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from storage_guest_fixtures import COMMANDS,UNIT,CLEANUP
from guest_screen import marker as acknowledgement,matches,locate_calibration,vi_ready,nano_ready
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import catalog,LEGACY_ID
from learning_lab.vm_preview.files import Refused,sha256
from learning_lab.vm_preview.process import same_process,verify_launch
import learning_lab
if a.installed:assert Path(learning_lab.__file__).resolve().is_relative_to(Path(sys.prefix))
assert a.vm_home.is_absolute() and a.vm_home.parent.is_dir() and not a.vm_home.parent.is_symlink() and a.vm_home.parent.stat().st_uid==os.getuid(), 'Owned persistent evidence parent required'
out=Path(tempfile.mkdtemp(prefix='storage-unit-live-',dir=a.vm_home.parent));sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());checks=[];report={'evidence':str(out),'vm_home':str(a.vm_home),'profile':sessions.profile,'package':str(Path(learning_lab.__file__).resolve()),'lessons':[]};active=None
(out/'executed-fixture.py').write_bytes(Path(__file__).read_bytes())
(out/'executed-commands.py').write_bytes(Path(__file__).with_name('storage_guest_fixtures.py').read_bytes())
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
  qmp('human-monitor-command',{'command-line':'sendkey '+k+' 5'});time.sleep(.012)
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
 text_to_send=t if interactive else "if { "+t+"; }; then printf '\\n"+marker+"\\n'; else echo STORAGE_COMMAND_FAILED; fi"
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




for n in (2,4,6,7):
 id=list(COMMANDS)[n-1]
 if a.only and id!=a.only:continue
 commands=COMMANDS[id];active=sessions.manager(id);running=False;info={'id':id,'mode':'Learn','kind':'additional safety boundary'}
 try:
  saved=active.reset('Learn',True);active.start();running=True;boot_ready()
  stop={2:5,4:7,6:7,7:9}[n]
  for command in commands[:stop]:line(command)
  if n==2:
   line('off "$part" disk.img && timeout() { case "$*" in *" findmnt "*) return 2;; *) command timeout "$@";; esac; }; off "$part" disk.img; rc=$?; target_ok; target_rc=$?; unset -f timeout; test "$rc" -ne 0 && test "$target_rc" -ne 0 && off "$part" disk.img')
   check('failed mount queries refuse offline and mountpoint approval',True)
   line('before=$(sha256sum disk.img); mv disk.img repair.img && (set -o noclobber; : > disk.img) && timeout -k 2s 15s truncate -s 128M disk.img && ! dev_ok "$part" disk.img && rm -- disk.img && mv repair.img disk.img && dev_ok "$part" disk.img && test "$(sha256sum disk.img)" = "$before"')
   check('mapped backing inode substitution refused and original preserved',True)
   line('before=$(maps disk.img); attach disk.img; rc=$?; test "$rc" -ne 0 && test "$(maps disk.img)" = "$before"')
   line('sudo() { case "$*" in *" losetup "*) return 2;; *) command sudo "$@";; esac; }; nomap disk.img; rc=$?; unset -f sudo; test "$rc" = 19 && dev_ok "$part" disk.img')
   line('test ! -e evidence.txt && ln -s /etc/hostname evidence.txt && ! guard && rm -- evidence.txt && guard')
   line('test ! -e mnt/sentinel && printf preserved > mnt/sentinel && ! target_ok && test "$(cat mnt/sentinel)" = preserved && rm -- mnt/sentinel && target_ok')
   check('repeat attach, query errors, log symlinks and nonempty mountpoint refuse safely',True)
   line('off "$part" disk.img && test ! -e repair.img && timeout -k 2s 30s cp --reflink=never disk.img repair.img && file_ok repair.img && sha256sum disk.img > original.sha256; printf "label: gpt\\nstart=2048, size=245760, type=L\\n" | sudo timeout -k 2s 15s bash -c \'ulimit -f 1024; exec sfdisk "$1"\' bash "$w/repair.img" > evidence.txt 2>&1; rc=$?; printf "LOW_LIMIT_STATUS=%s\\n" "$rc"; head -n 12 evidence.txt; test "$rc" = 153 && sha256sum -c original.sha256 && test -z "$(sudo losetup -j "$w/repair.img")" && rm -- repair.img evidence.txt')
   check('old 1-MiB ceiling reproduces SIGXFSZ on a preserved copy',True)
   line('run head -c 1050000 /dev/zero > evidence.txt; rc=$?; test "$rc" = 20 && test "$(stat -c %s evidence.txt)" = 1048576 && test ! -e command-output.tmp && rm -- evidence.txt')
   check('real output capture ceiling and explicit overflow status',True)
   line('run awk \'$1=="Max" && $2=="file" && $3=="size" { if ($4 != 268435456 || $5 != 268435456) exit 1; print $4,$5; seen=1 } END { if (!seen) exit 1 }\' /proc/self/limits > evidence.txt && cat evidence.txt && rm -- evidence.txt')
   check('actual worker soft/hard file limit is exactly 256 MiB',True)
   line('test ! -e mount.log && (set -o noclobber; : > mount.log) && test "$(stat -c %u mount.log)" = "$(id -u)" && run truncate -s 268435457 mount.log > evidence.txt; rc=$?; test "$rc" -ne 0 && test "$(stat -c %s mount.log)" -le 268435456 && rm -- mount.log evidence.txt')
   check('real kernel regular-file ceiling',True)
   line('run sleep 35 > evidence.txt; rc=$?; test "$rc" = 124 && test ! -e command-output.tmp && rm -- evidence.txt')
   check('actual outer 30-second timeout enforcement',True)
  if n==4:
   line('dev_ok "$part" disk.img && mounted "$part" && ! target_ok; safe_repair() { off "$1" "$2" || return 19; run e2fsck -fy "$1"; }; safe_repair "$part" disk.img > evidence.txt; rc=$?; test "$rc" = 19 && test ! -s evidence.txt && cmp expected.txt mnt/note && rm -- evidence.txt')
   check('mounted repair and occupied mountpoint refused without destructive call',True)
   line('first=$part; alias=$(sudo timeout -k 2s 15s losetup --find --show --partscan "$w/disk.img"); [[ "$alias" =~ ^/dev/loop[0-9]+$ ]] && test "$(sudo losetup -n -O BACK-FILE "$alias")" = "$w/disk.img" && test "$(sudo losetup -n -O BACK-INO "$alias")" = "$(stat -c %i disk.img)" && test -b "${alias}p1" && ! dev_ok "$part" disk.img && ! off "${alias}p1" disk.img && ! on "$part" disk.img')
   line('mounted "${alias}p1"; rc=$?; test "$rc" = 1 && test "$(sudo losetup -n -O BACK-INO "$alias")" = "$(stat -c %i disk.img)" && sudo timeout -k 2s 15s losetup -d "$alias" && on "$part" disk.img && cmp expected.txt mnt/note')
   line('on "$part" disk.img && mv mnt/note mnt/retained-note && ln -s /etc/passwd mnt/note && ! note_ok "$part" disk.img && rm -- mnt/note && mv mnt/retained-note mnt/note && note_ok "$part" disk.img && ln mnt/note mnt/alias-note && ! note_ok "$part" disk.img && rm -- mnt/alias-note && note_ok "$part" disk.img && cmp expected.txt mnt/note')
   line('other=/home/learner/ll-storage-review-mount; test ! -e "$other" && test ! -L "$other" && mkdir -m 0700 "$other" && on "$part" disk.img && run umount "$w/mnt" && off "$part" disk.img && run mount -o nodev,nosuid,noexec "$part" "$other" && dev_ok "$part" disk.img && mounted "$part" && ! on "$part" disk.img')
   line('test "$(readlink -e "$other")" = /home/learner/ll-storage-review-mount && test "$(findmnt -rn -M "$other" -o MAJ:MIN)" = "$(lsblk -dnro MAJ:MIN "$part")" && run umount "$other" && rmdir -- "$other" && off "$part" disk.img && target_ok && run mount -o nodev,nosuid,noexec "$part" "$w/mnt" && on "$part" disk.img && cmp expected.txt mnt/note')
   check('duplicate mapping, note links and wrong mount location refused; content retained',True)
   line(commands[8])
  if n==6:
   prefix=commands[7].split('; tab_ok &&')[0];line(prefix)
   line('valid=$(cat practice.fstab); printf "/dev/vda1 %s ext4 defaults 0 0\\n" "$w/mnt" > practice.fstab; ! tab_ok && printf "%s\\n" "$valid" > practice.fstab && tab_ok')
   check('wrong private-fstab source/options refused before mount',True)
   line('valid=$(cat practice.fstab); original_uuid=$uuid; uuid=$(sudo timeout -k 2s 15s blkid -p -s UUID -o value "$(findmnt -n -o SOURCE /)"); test -n "$uuid" && test "$uuid" != "$original_uuid" && printf "UUID=%s %s ext4 noauto,nodev,nosuid,noexec 0 0\\n" "$uuid" "$w/mnt" > practice.fstab && ! tab_ok && printf "%s\\n" "$valid" > practice.fstab && tab_ok && uuid=$original_uuid')
   check('stale or unrelated UUID variable cannot authorize wrong fstab source',True)
  if n==7:
   line('dev_ok "$part" disk.img && dev_ok "$copy" repair.img && ! dev_ok "$copy" disk.img && ! dev_ok "$part" repair.img && sha256sum -c original.sha256')
   check('actual unrelated mapped partition refused; original unchanged',True)
   line('off "$part" disk.img && off "$copy" repair.img && uuid=$(sudo blkid -p -s UUID -o value "$part") && test "$(sudo blkid -c /dev/null -t UUID="$uuid" -o device | wc -l)" = 2')
   line(commands[9].split('; uuid=')[0])
   line('uuid_mount_safe() { unique_uuid "$part" disk.img || return 19; target_ok && run mount -U "$uuid" "$w/mnt"; }; uuid_mount_safe; rc=$?; test "$rc" = 19 && target_ok')
   check('real duplicate UUID refused before actual UUID mount',True)
   line('copy_before=$(sudo blkid -p -s UUID -o value "$copy"); sudo() { case "$*" in *" blkid "*) return 2;; *) command sudo "$@";; esac; }')
   line(commands[9]+'; rc=$?; unset -f sudo; test "$rc" -ne 0 && test "$(sudo blkid -p -s UUID -o value "$copy")" = "$copy_before" && sha256sum -c original.sha256')
   check('failed UUID query does not change copy UUID or claim duplicate success',True)
   line('off_calls=0; off() { off_calls=$((off_calls+1)); test "$off_calls" -gt 1; }; '+commands[11]+'; rc=$?; test "$rc" -ne 0 && test ! -e repair.log && test ! -e recheck.log')
   line('off() {'+commands[2].split('off() {',1)[1].split('; target_ok()',1)[0])
   check('failed repair precondition cannot reach recheck or stale success',True)

  line(commands[-1])
  if n==2:
   line('guard && test -z "$(sudo losetup -j "$w/disk.img")" && target_ok && test -f partition.log && test -f layout.log; timeout -k 1s 1s bash -c \'rm -- "$1/partition.log" && sleep 3 && rm -- "$1/layout.log"\' bash "$w"; rc=$?; test "$rc" = 124 && test ! -e partition.log && test -f layout.log && file_ok disk.img')
   check('interrupted exact cleanup retains remaining resources for safe repetition',True)
   line('before=$(sha256sum disk.img); printf retained > unknown')
   line(CLEANUP[n].rsplit("; cleanup",1)[0])
   line('cleanup; rc=$?; test "$rc" = 19 && test "$(sha256sum disk.img)" = "$before" && test "$(cat unknown)" = retained && test -d mnt && rm -- unknown && guard')
   line('sudo() { case "$*" in *" losetup "*) return 2;; *) command sudo "$@";; esac; }; cleanup; rc=$?; unset -f sudo; test "$rc" = 19 && test "$(sha256sum disk.img)" = "$before" && test -d mnt && guard')
   check('unknown members and loop-query errors preserve entire cleanup candidate',True)
  line(CLEANUP[n]);line('test ! -e /home/learner/ll-storage-'+str(n));check('exact safety fixture cleanup',True)
  check('safety clean Stop',active.stop()=='Cleanly stopped');running=False;runtime_event('clean-stop');info['result']='PASS';info['pin']=saved['pin']
 finally:
  if running:
   try:info['failure_cleanup']=active.stop()
   except Exception as exc:info['failure_cleanup']='BLOCKED: '+str(exc)
  report['lessons'].append(info);report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Evidence',out,flush=True)
