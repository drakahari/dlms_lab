#!/usr/bin/env python3
"""Explicit developer-only fresh Alma preparation, never invoked by lesson data.

Authenticated frozen inputs only. Normal shared VM exclusion; no owner sessions,
network, host mount/share, system package installation or production image trust.
"""
import argparse,base64,fcntl,gzip,hashlib,json,os,re,stat,subprocess,sys,threading,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'foundation'))
from learning_lab.vm_preview.files import Directory,require
from preparation_visibility import require_no_guest
from bounded_capture import capture_stream
from preparation_console import PreparationConsole
from inspect_fixtures import inspect as inspect_fixture, NAMES as FIXTURE_NAMES
p=argparse.ArgumentParser();p.add_argument('--verified-inputs',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--kind',choices=('builder','learner'),required=True);p.add_argument('--fixtures',type=Path);a=p.parse_args()
require(os.getuid()!=0,'Run as normal user')
os.umask(0o022)  # Developer process only; delivery inputs never ordinary-user writable.
require((a.kind=='builder' and a.fixtures is None) or
        (a.kind=='learner' and a.fixtures is not None), 'Learner requires a finalized reviewed builder directory')
recipe=Path(__file__).resolve().parent
frozen=json.loads((recipe/'frozen-inputs.json').read_text())
require(frozen['format_version']==1 and len(frozen['packages'])==283,'Unsupported frozen input set')
inputs=a.verified_inputs;iso=inputs/'AlmaLinux-9.8-x86_64-minimal.iso'
for name,digest in frozen['verification_material'].items():
 payload=(inputs/'metadata'/name).read_bytes()
 require(len(payload)<=65536 and hashlib.sha256(payload).hexdigest()==digest,'Verification material changed')
verification=subprocess.run(['/usr/bin/gpgv','--homedir',str(inputs.parent/'input-gpg'),'--status-fd','1','--keyring',str(inputs/'metadata/alma9-keyring.gpg'),str(inputs/'metadata/Alma9.8-CHECKSUM')],capture_output=True,timeout=60,check=False)
require(len(verification.stdout)+len(verification.stderr)<=131072,'Signature output bound exceeded')
valid=[line.split() for line in verification.stdout.decode('ascii').splitlines() if line.startswith('[GNUPG:] VALIDSIG ')]
require(verification.returncode==0 and len(valid)==1 and valid[0][2]==valid[0][-1]==frozen['vendor_fingerprint'], 'Exact vendor signature missing')
require(not any(word in verification.stdout.decode('ascii') for word in ('BADSIG','ERRSIG','EXPSIG','EXPKEYSIG','REVKEYSIG','NO_PUBKEY')), 'Unacceptable signature status')
require('SHA256 (AlmaLinux-9.8-x86_64-minimal.iso) = '+frozen['iso_sha256'] in (inputs/'metadata/Alma9.8-CHECKSUM').read_text().splitlines(), 'Pinned checksum missing from signed material')
require(iso.is_file() and not iso.is_symlink(),'Unexpected ISO')
with iso.open('rb') as f:require(hashlib.file_digest(f,'sha256').hexdigest()==frozen['iso_sha256'],'ISO changed')
fixture_manifest=None; fixture_bytes={}; fixture_sources={}
if a.kind=='learner':
 require(a.fixtures.is_dir() and not a.fixtures.is_symlink(),'Unexpected builder directory')
 def receipt(name,maximum=16384):
  parts=name.split('/');require(all(part and part not in ('.','..') for part in parts),'Invalid receipt member')
  with Directory.absolute(a.fixtures) as base:
   parent=os.dup(base.fd)
   try:
    for part in parts[:-1]:
     child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
     os.close(parent);parent=child;metadata=os.fstat(parent)
     require(metadata.st_uid==os.getuid() and not metadata.st_mode&0o022,'Untrusted receipt directory')
    fd=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
    with os.fdopen(fd,'rb') as stream:
     before=os.fstat(stream.fileno())
     require(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_nlink==1 and not before.st_mode&0o022 and before.st_size<=maximum,'Invalid bounded receipt')
     payload=stream.read(maximum+1);after=os.fstat(stream.fileno())
     key=lambda m:(m.st_dev,m.st_ino,m.st_mode,m.st_uid,m.st_gid,m.st_nlink,m.st_size,m.st_mtime_ns,m.st_ctime_ns)
     require(key(before)==key(after) and len(payload)==before.st_size and len(payload)<=maximum,'Receipt changed or exceeded bound')
     return payload
   finally:os.close(parent)
 result=json.loads(receipt('image-result.json'))
 require(result['kind']=='builder-only-not-admitted' and result['bytes']==16*1024**3,'Unsupported builder receipt')
 inventory=receipt('packages.tsv',65536)
 require(inventory==(recipe/'expected-builder.tsv').read_bytes() and hashlib.sha256(inventory).hexdigest()==result['packages_sha256'],'Builder inventory differs')
 capture=json.loads(receipt('finalization-capture.json'))
 require(capture['complete'] and capture['persisted'] and not capture['overflow'] and capture['error'] is None,'Incomplete builder capture')
 console=receipt('finalization-console.log',4*1024**2)
 require(len(console)==capture['bytes'] and hashlib.sha256(console).hexdigest()==capture['sha256'],'Builder evidence changed')
 rounds=re.findall(rb'LL_FIXTURE_BUILD_ROUND ([ab]) ([0-9]+)',console)
 require(len(rounds)==2 and [row[0] for row in rounds]==[b'a',b'b'] and int(rounds[1][1])>=int(rounds[0][1])+2,'Independent build rounds not established')
 require(console.count(b'LL_FIXTURE_REPRODUCIBLE_PASS')==1 and console.count(b'LL_ALMA_IMAGE_FINALIZED')==1,'Builder finalization absent')
 for source in (recipe/'fixtures').rglob('*'):
  if source.is_file():
   relative=str(source.relative_to(recipe/'fixtures'))
   payload=receipt('executed-recipe/rpm/fixtures/'+relative,65536)
   require(not source.is_symlink() and source.read_bytes()==payload,'Fixture source differs from native build')
   fixture_sources[relative]=payload
 require(receipt('executed-recipe/rpm/build-fixtures.sh',65536)==(recipe/'build-fixtures.sh').read_bytes(),'Build recipe differs')
 archive_root=a.fixtures/'fixtures'
 require(archive_root.is_dir() and not archive_root.is_symlink(),'Invalid artifact directory')
 require(set(p.name for p in archive_root.iterdir())==set(FIXTURE_NAMES)|{'manifest.json'},'Unexpected built artifact')
 reviewed={}
 for name in FIXTURE_NAMES:
  record=inspect_fixture(archive_root/name,recipe/'fixtures')
  reviewed[name]={key:record[key] for key in ('sha256','bytes')}
  payload=receipt('fixtures/'+name,131072)
  require(len(payload)==record['bytes'] and hashlib.sha256(payload).hexdigest()==record['sha256'],'Archive changed after inspection')
  fixture_bytes[name]=payload
 for relative,payload in fixture_sources.items():
  require((recipe/'fixtures'/relative).read_bytes()==payload,'Fixture source changed during inspection')
 require(reviewed==result['fixture_archives'],'Built archive receipt differs')
 fixture_manifest=receipt('fixtures/manifest.json',8192)
 require(json.loads(fixture_manifest)=={'schema_version':1,'archives':reviewed},'Fixture manifest differs from inspected archives')
with Directory.absolute(Path(f'/run/user/{os.getuid()}/oll-vm-preview'),create=True) as gate:
 op=gate.open('operations.lock',write=True,new=not gate.exists('operations.lock'));fcntl.flock(op,fcntl.LOCK_EX|fcntl.LOCK_NB)
 life=gate.open('running.lock',write=True,new=not gate.exists('running.lock'));fcntl.flock(life,fcntl.LOCK_EX|fcntl.LOCK_NB)
 visibility=require_no_guest()
 require(os.statvfs(a.destination.parent).f_bavail*os.statvfs(a.destination.parent).f_frsize>=80*1024**3,'80GiB free required')
 root=a.destination.absolute();root.mkdir(mode=0o700,exist_ok=False)
 # Keep the exact executable preparation inputs: later edits must not make a
 # failed run's line-cache or recipe provenance ambiguous.
 retained=root/'executed-recipe';retained.mkdir(mode=0o700)
 retained_hashes={}
 for area,source_root in (('rpm',recipe),('foundation',recipe.parent/'foundation')):
  for source in sorted(source_root.rglob('*')):
   if source.is_dir():continue
   require(source.is_file() and not source.is_symlink(),'Unexpected recipe member')
   if '__pycache__' in source.parts:continue
   payload=source.read_bytes();require(len(payload)<=1048576,'Preparation recipe member bound')
   name=area+'/'+str(source.relative_to(source_root))
   target=retained/name;target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb') as out:out.write(payload);out.flush();os.fsync(out.fileno())
   retained_hashes[name]=hashlib.sha256(payload).hexdigest()
 with (root/'executed-recipe.sha256.json').open('x') as out:
  json.dump(retained_hashes,out,sort_keys=True,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
 (root/'visibility.json').write_text(json.dumps(visibility,indent=2)+'\n')
 (root/'iso-signature.log').write_bytes(verification.stdout+verification.stderr)
 incoming=root/'ll-inputs';incoming.mkdir(mode=0o700)
 files=('post-policy.sh','finalize-image.sh','installer_admission.py','patch_installer.py')
 if a.kind=='builder':files+=('install-builder.py','build-fixtures.sh')
 for filename in files:
  (incoming/filename).write_bytes((retained/'rpm'/filename).read_bytes())
 (incoming/'expected.tsv').write_bytes((recipe/('expected-'+a.kind+'.tsv')).read_bytes())
 (incoming/'LICENSE').write_bytes(recipe.parents[3].joinpath('LICENSE').read_bytes())
 # Every learner binary is on the authenticated DVD. Builder additions are
 # individually authenticated whole-content vendor-signed archives from A.
 extras=[row for row in frozen['packages'] if row['builder_only']]
 require(len(extras)==93,'Unexpected builder additions')
 builder=incoming/'builder';builder.mkdir()
 for row in frozen['packages']:
  source=inputs/('alma-builder-rpms' if row['builder_only'] else 'alma-learner-rpms')/row['file']
  require(source.is_file() and not source.is_symlink() and source.stat().st_size==row['bytes'],'Frozen package type/size mismatch')
  with source.open('rb') as f:require(hashlib.file_digest(f,'sha256').hexdigest()==row['sha256'],'Frozen package hash mismatch')
  if row['builder_only'] and a.kind=='builder':(builder/row['file']).write_bytes(source.read_bytes())
 if a.kind=='builder':(builder/'manifest.json').write_text(json.dumps({'format_version':1,'packages':extras},indent=2)+'\n')
 else:
  builder.rmdir()
  fixtures=incoming/'fixtures';fixtures.mkdir()
  for name in FIXTURE_NAMES:(fixtures/name).write_bytes(fixture_bytes[name])
  (fixtures/'manifest.json').write_bytes(fixture_manifest)
  helper=(retained/'rpm/transaction-helper.py').read_text()
  require(helper.count("MANIFEST_SHA256 = 'FIXTURE_MANIFEST_SHA256'")==1,'Unexpected helper template')
  helper=helper.replace("MANIFEST_SHA256 = 'FIXTURE_MANIFEST_SHA256'", "MANIFEST_SHA256 = '"+hashlib.sha256(fixture_manifest).hexdigest()+"'")
  (incoming/'transaction-helper.py').write_text(helper)
  delivery={'manifest_sha256':hashlib.sha256(fixture_manifest).hexdigest(),
            'helper_sha256':hashlib.sha256(helper.encode()).hexdigest(),
            'archive_hashes':reviewed,
            'source_hashes':{name:hashlib.sha256(payload).hexdigest() for name,payload in fixture_sources.items()}}
  (root/'learner-delivery.json').write_text(json.dumps(delivery,sort_keys=True,indent=2)+'\n')
 sources=incoming/'source';sources.mkdir()
 for source in sorted((recipe/'fixtures').rglob('*')):
  target=sources/source.relative_to(recipe/'fixtures')
  require(not source.is_symlink(),'Unexpected fixture source link')
  if source.is_dir():target.mkdir()
  else:
   require(source.is_file() and source.stat().st_size<=65536,'Fixture source bound')
   relative=str(source.relative_to(recipe/'fixtures'))
   target.write_bytes(fixture_sources[relative] if a.kind=='learner' else (retained/'rpm/fixtures'/relative).read_bytes())
 # Installer payload is190 exact media NEVRAs, not a mutable group/environment.
 learner=[row for row in frozen['packages'] if not row['builder_only']]
 (incoming/'learner-manifest.json').write_text(json.dumps({'format_version':1,'packages':learner},separators=(',',':'))+'\n')
 package_lines=[row['name']+'-'+(row['epoch']+':' if row['epoch']!='0' else '')+row['version']+'-'+row['release']+'.'+row['arch'] for row in learner]
 if a.kind=='builder':kind_post='''mv /opt/ll-build-delivery/builder /opt/learning-lab-builder-inputs
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux-9
/usr/bin/python3 -I /opt/ll-build-delivery/install-builder.py
install -m 0755 /opt/ll-build-delivery/build-fixtures.sh /usr/local/sbin/ll-build-fixtures
'''
 else:kind_post='''mv /opt/ll-build-delivery/fixtures /opt/learning-lab/rpm-fixtures
chown -R root:root /opt/learning-lab/rpm-fixtures /opt/learning-lab-rpm-source
chmod 0755 /opt/learning-lab /opt/learning-lab/rpm-fixtures /opt/learning-lab-rpm-source
find /opt/learning-lab-rpm-source -type d -exec chmod 0755 '{}' ';'
find /opt/learning-lab-rpm-source -type f -exec chmod 0444 '{}' ';'
chmod 0444 /opt/learning-lab/rpm-fixtures/*
install -d -m 0700 /var/lib/learning-lab-rpm
install -m 0755 /opt/ll-build-delivery/transaction-helper.py /usr/local/sbin/ll-rpm-fixture
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux-9
'''
 ks='''#version=RHEL9
text
cdrom
lang en_US.UTF-8
keyboard us
timezone UTC --utc --nontp
rootpw --lock
user --name=learner --lock --shell=/bin/bash
selinux --enforcing
ignoredisk --only-use=vda
zerombr
clearpart --all --initlabel --drives=vda
bootloader --location=mbr --boot-drive=vda --append="console=tty0 console=ttyS0,115200n8"
part /boot --fstype=ext4 --size=512 --ondisk=vda
part swap --fstype=swap --size=512 --ondisk=vda
part / --fstype=ext4 --size=1024 --grow --ondisk=vda
shutdown
%addon com_redhat_kdump --disable
%end
%pre --erroronfail --log=/dev/ttyS0
set -eu
test -f /ll-inputs/installer-admission-ready.json && test ! -L /ll-inputs/installer-admission-ready.json
%end
%packages --nocore --exclude-weakdeps
'''+ '\n'.join(package_lines)+'''
-kernel
-kexec-tools
-NetworkManager
-openssh-server
-openssh-clients
-cloud-init
-qemu-guest-agent
-firewalld
-sssd
-sssd-common
-sssd-kcm
-chrony
-microcode_ctl
-linux-firmware
-rpm-build
%end
%post --nochroot --erroronfail --log=/dev/ttyS0
set -eu
test -d /mnt/sysroot && test ! -L /mnt/sysroot
test -d /ll-inputs && test ! -L /ll-inputs
cp -a /ll-inputs /mnt/sysroot/opt/ll-build-delivery
%end
%post --erroronfail --log=/dev/ttyS0
set -eu
install -d -m 0755 /usr/local/sbin /usr/local/share/learning-lab /opt/learning-lab
install -m 0644 /opt/ll-build-delivery/LICENSE /usr/local/share/learning-lab/LICENSE
install -m 0644 /opt/ll-build-delivery/expected.tsv /usr/local/sbin/ll-expected.tsv
install -m 0755 /opt/ll-build-delivery/finalize-image.sh /usr/local/sbin/ll-finalize
mv /opt/ll-build-delivery/source /opt/learning-lab-rpm-source
'''+kind_post+'''/bin/sh /opt/ll-build-delivery/post-policy.sh
%end
'''
 (root/'ks.cfg').write_text(ks)
 hook=root/'usr/lib/dracut/hooks/pre-pivot/51-ll-copy-inputs.sh';hook.parent.mkdir(parents=True)
 members=sorted(incoming.rglob('*'),key=lambda p:(len(p.parts),str(p)))
 copy='''#!/usr/bin/sh
ll_deliver() {
 test ! -e /sysroot/ll-inputs && test ! -L /sysroot/ll-inputs || return 1
 mkdir /sysroot/ll-inputs || return 1
'''
 for member in members:
  rel=str(member.relative_to(root))
  if member.is_dir():copy+=' mkdir /sysroot/'+rel+' || return 1\n'
  else:copy+=' test -f /'+rel+' && test ! -L /'+rel+' || return 1\n cp -- /'+rel+' /sysroot/'+rel+' || return 1\n'
 copy+=' chroot /sysroot /usr/bin/python3 -I /ll-inputs/patch_installer.py || return 1\n'
 copy+='}\nif ll_deliver; then printf "LL_INPUT_DELIVERY_PASS\\n" >/dev/ttyS0; else printf "LL_INPUT_DELIVERY_FAIL\\n" >/dev/ttyS0; fi\n'
 hook.write_text(copy);hook.chmod(0o755)
 paths=['usr/lib/dracut/hooks/pre-pivot/51-ll-copy-inputs.sh','ks.cfg','ll-inputs']+[str(m.relative_to(root)) for m in members]
 cpio=subprocess.run(['cpio','--create','--format=newc','--owner=0:0'],input=('\n'.join(paths)+'\n').encode(),cwd=root,capture_output=True,check=True).stdout
 boot=inputs/'alma-boot'
 for name,digest in [('vmlinuz','6680128c01a4b27bc3760b4ea85b28be9ffefb719a4724adc45b8536a20c594a'),('initrd.img','67c0551070da0493fef8d0ff4aac56aa1b7ee58f41ad717e722aa3f74242d381')]:
  payload=(boot/name).read_bytes();require(hashlib.sha256(payload).hexdigest()==digest,'Verified boot input changed')
  (root/name).write_bytes(payload+(gzip.compress(cpio,mtime=0) if name=='initrd.img' else b''))
 disk=root/'prepared.raw'
 with disk.open('xb') as f:f.truncate(16*1024**3)
 common=['/usr/bin/qemu-system-x86_64','-add-fd',f'fd={life},set=3','-name','Learning Lab fresh offline Alma '+a.kind,'-machine','q35,accel=kvm','-cpu','host','-smp','2','-m','2048','-nodefaults','-no-user-config','-device','VGA,xres=800,yres=600','-drive',f'file={disk},format=raw,if=virtio','-nic','none','-display','gtk,zoom-to-fit=on','-monitor','none','-serial','stdio','-no-reboot']
 installer=common+['-drive',f'file={iso},format=raw,media=cdrom,readonly=on','-kernel',str(root/'vmlinuz'),'-initrd',str(root/'initrd.img'),'-append','inst.stage2=hd:LABEL=AlmaLinux-9-8-x86_64-dvd inst.repo=cdrom inst.ks=file:/ks.cfg inst.text inst.cmdline console=ttyS0,115200n8']
 fcntl.flock(op,fcntl.LOCK_UN);os.close(op)
 def run(args,phase,seconds):
  run_id=str(uuid.uuid4())
  control_name='prep-'+uuid.uuid4().hex
  control_dir=gate.child(control_name,create=True,exclusive=True)
  args=args+['-uuid',run_id,'-qmp',f'unix:/proc/self/fd/{control_dir.fd}/qmp,server=on,wait=off']
  (root/(phase+'-argv.json')).write_text(json.dumps(args,indent=2)+'\n')
  process=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True,pass_fds=(life,control_dir.fd))
  control_path=str(Path(f'/run/user/{os.getuid()}/oll-vm-preview')/control_name)
  print(phase,root,'PID',process.pid,'CONTROL',control_path,flush=True)
  capture={'bytes':0,'overflow':False,'complete':False,'error':None}
  def drain():
   capture_stream(process.stdout,root/(phase+'-console.log'),capture,4*1024**2,root/(phase+'-capture.json'))
  control=None;thread=None
  try:
   thread=threading.Thread(target=drain,daemon=True);thread.start()
   ticks=Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()[19]
   (root/(phase+'-process.json')).write_text(json.dumps({'pid':process.pid,'start_ticks':ticks,'uid':os.getuid(),'argv':args,'uuid':run_id,'private_control_directory':control_path},indent=2)+'\n')
   control=PreparationConsole(control_dir,process,args,run_id)
   (root/(phase+'-control-ready.json')).write_text(json.dumps({'private_directory':str(Path(f'/run/user/{os.getuid()}/oll-vm-preview')/control_name),'uuid':run_id,'verified_process':control.identity,'status':control.status(),'allowed_operations':['query-status','system_powerdown']},indent=2)+'\n')
  except BaseException as error:
   if control is not None:control.close()
   try:
    (root/(phase+'-incomplete.json')).write_text(json.dumps({'pid':process.pid,'private_control_directory':control_path,'reason':'Post-launch setup failed; candidate not admitted; inspect exact process before any further action','error':repr(error)})+'\n')
   except Exception as recording_error:
    print('INCOMPLETE PID',process.pid,'CONTROL',control_path,'EVIDENCE FAILURE',repr(recording_error),file=sys.stderr,flush=True)
   control_dir.close()
   raise
  # QMP permits one client: do not occupy it while an installer waits.
  # A reconnect must retain the original identity, never adopt a recycled PID.
  bound_identity=dict(control.identity)
  control.close()
  try:code=process.wait(timeout=seconds)
  except subprocess.TimeoutExpired:
   try:
    require(process.poll() is None,'Preparation process already exited')
    control=PreparationConsole(control_dir,process,args,run_id,expected_identity=bound_identity)
    require(control.identity==bound_identity,'Preparation identity changed before shutdown')
    clean=control.powerdown()
   except Exception as error:clean=False;shutdown_error=repr(error)
   else:shutdown_error=None
   thread.join(timeout=5)
   (root/(phase+'-incomplete.json')).write_text(json.dumps({'pid':process.pid,'reason':'Deadline; candidate/evidence retained and not admitted','clean_powerdown_observed':clean,'shutdown_error':shutdown_error,'events':control.events})+'\n')
   raise RuntimeError('Build deadline; inspect retained guest/process state')
  finally:
   control.close();control_dir.close()
  thread.join(timeout=5)
  require(code==0 and not thread.is_alive() and capture['complete'] and capture['persisted'] and not capture['overflow'] and capture['error'] is None,'Build output/exit incomplete')
  return (root/(phase+'-console.log')).read_text(errors='replace')
 console=run(installer,'installer',1800)
 require(console.count('LL_ACTUAL_INSTALLER_ADMISSION_PASS')==1,'Actual installer transaction admission absent')
 require(console.count('LL_ALMA_INSTALL_CONFIGURED')==1,'Installer incomplete, candidate retained')
 console=run(common,'finalization',900)
 require(console.count('LL_ALMA_IMAGE_FINALIZED')==1 and (a.kind=='learner' or console.count('LL_FIXTURE_REPRODUCIBLE_PASS')==1),'Finalization incomplete, candidate retained')
 match=re.search(r'LL_FINAL_INVENTORY_BEGIN\r?\n(.*?)LL_FINAL_INVENTORY_END',console,re.S)
 require(match is not None,'Final inventory absent')
 inventory=match.group(1).replace('\r','').encode();require(inventory==(recipe/('expected-'+a.kind+'.tsv')).read_bytes(),'Final exact inventory mismatch')
 (root/'packages.tsv').write_bytes(inventory)
 expected_names={'ll-rpm-data-1.0-1.noarch.rpm','ll-rpm-data-2.0-1.noarch.rpm','ll-rpm-report-1.0-1.noarch.rpm'}
 archive_dir=root/'fixtures';archive_dir.mkdir();found={}
 for match in re.finditer(r'LL_FIXTURE_BEGIN ([A-Za-z0-9.-]+) ([a-f0-9]{64})\r?\n(.*?)LL_FIXTURE_END \1',console,re.S):
  name,digest,encoded=match.groups();require(name in expected_names and name not in found,'Unexpected fixture output')
  payload=base64.b64decode(''.join(encoded.split()),validate=True);require(len(payload)<=131072 and hashlib.sha256(payload).hexdigest()==digest,'Fixture output hash/size mismatch')
  (archive_dir/name).write_bytes(payload);found[name]={'sha256':digest,'bytes':len(payload)}
 require(set(found)==expected_names if a.kind=='builder' else not found,'Unexpected or missing fixture output')
 if a.kind=='learner':
  # These were already inspected and admitted from the finalized builder.
  # A learner does not rebuild/re-emit them on its console. Retain their exact
  # delivered bytes and provenance rather than writing an empty artifact receipt.
  for name,payload in fixture_bytes.items():(archive_dir/name).write_bytes(payload)
  found={name:{'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}
         for name,payload in fixture_bytes.items()}
  require(found==reviewed,'Retained learner fixture receipt differs')
  (archive_dir/'manifest.json').write_bytes(fixture_manifest)
 else:
  (archive_dir/'manifest.json').write_text(json.dumps({'schema_version':1,'archives':found},sort_keys=True,indent=2)+'\n')
 with disk.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 disk.chmod(0o444)
 (root/'image-result.json').write_text(json.dumps({'kind':'builder-only-not-admitted' if a.kind=='builder' else 'learner-candidate-policy-unverified','sha256':digest,'bytes':disk.stat().st_size,'packages_sha256':hashlib.sha256(inventory).hexdigest(),'fixture_archives':found,'fixture_manifest_sha256':hashlib.sha256(fixture_manifest).hexdigest() if fixture_manifest else None},indent=2)+'\n')
 print('FROZEN_ALMA_'+a.kind.upper()+'_FINALIZED',digest,flush=True)
 os.close(life)
