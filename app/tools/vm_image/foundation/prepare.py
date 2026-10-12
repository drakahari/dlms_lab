#!/usr/bin/env python3
"""Explicit developer-only local image build. Never called by lesson JSON/UI."""
import argparse, hashlib, json, os, pathlib, subprocess, time, fcntl, sys, threading
from bounded_capture import capture_stream
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from learning_lab.vm_preview.files import Directory
# Existing shared exclusion, with no replacement/deletion of coordination records.
gate = Directory.absolute(pathlib.Path(f"/run/user/{os.getuid()}/oll-vm-preview"), create=True)
gate.__enter__()
operation_fd=gate.open("operations.lock",write=True,new=not gate.exists("operations.lock"))
fcntl.flock(operation_fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
lifetime_fd=gate.open("running.lock",write=True,new=not gate.exists("running.lock"))
fcntl.flock(lifetime_fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
from preparation_visibility import require_no_guest
visibility=require_no_guest()
fcntl.flock(operation_fd,fcntl.LOCK_UN);os.close(operation_fd)
p=argparse.ArgumentParser();p.add_argument('--verified-inputs',type=pathlib.Path,required=True);p.add_argument('--approved-packages',type=pathlib.Path,required=True);p.add_argument('--destination',type=pathlib.Path,required=True);a=p.parse_args()
def require(ok,message):
 if not ok:raise RuntimeError(message)
require(os.getuid()!=0,'Run as normal user')
iso=a.verified_inputs/'debian-13.7.0-amd64-DVD-1.iso'
expected='347b6c67a3cc0b7ddb60b178f683470c4e2b7ac426c996d9337a2ff36c1a32d2'
subprocess.run(['gpgv','--keyring',str(a.verified_inputs/'DA87E80D6294BE9B.gpg'),str(a.verified_inputs/'SHA256SUMS.sign'),str(a.verified_inputs/'SHA256SUMS')],check=True)
require(expected+'  '+iso.name in (a.verified_inputs/'SHA256SUMS').read_text().splitlines(),'Pinned ISO checksum is absent from signed manifest')
with iso.open('rb') as f:require(hashlib.file_digest(f,'sha256').hexdigest()==expected,'ISO hash mismatch')
require(os.statvfs(a.destination.parent).f_bavail*os.statvfs(a.destination.parent).f_frsize>=80*1024**3,'80 GiB free required for preparation')
root=a.destination.absolute();root.mkdir(mode=0o700,parents=False,exist_ok=False)
(root/'visibility.json').write_text(json.dumps(visibility,indent=2)+'\n')
recipe=pathlib.Path(__file__).resolve().parent
for name in ('preseed.cfg','finish-image.sh','finalize-image.sh','expected-packages.tsv'):(root/name).write_bytes((recipe/name).read_bytes())
(root/'learning-lab-LICENSE').write_bytes(pathlib.Path(__file__).resolve().parents[4].joinpath('LICENSE').read_bytes())
for name,member in [('vmlinuz','install.amd/vmlinuz'),('initrd.original.gz','install.amd/initrd.gz')]:
 with (root/name).open('xb') as f:subprocess.run(['bsdtar','-xOf',str(iso),member],stdout=f,check=True)
# Inputs were authenticated against signed Debian metadata at Checkpoint A.
inputs = root/'ll-inputs'; inputs.mkdir(mode=0o700)
approved = {
 'liblzma5': ('liblzma5_5.8.1-1+deb13u2_amd64.deb','b38acab30f295bf1066a6632e31cbd0a1980f2924b38040cda131d5dea5384ec'),
 'xz-utils': ('xz-utils_5.8.1-1+deb13u2_amd64.deb','66b060ef2f09722c947ba019da5e9a63f6bac9d7bf90b32339a72c0390acc53f'),
 'at': ('at_3.2.5-2.2_amd64.deb','f7f36171c9166ef136221db2708cf24c72fd9e39ceb2aa41f31108593117896d'),
}
for name,(filename,digest) in approved.items():
 payload=(a.approved_packages/filename).read_bytes()
 require(hashlib.sha256(payload).hexdigest()==digest,'Approved package hash mismatch: '+name)
 (inputs/(name+'.deb')).write_bytes(payload)
# Debian Installer reads /preseed.cfg from its initramfs. Concatenated gzip/cpio
# archive adds only the six reviewed preparation files; no ISO changes or host mounts.
cpio=subprocess.run(['cpio','--create','--format=newc','--owner=0:0'],input=b'preseed.cfg\nfinish-image.sh\nfinalize-image.sh\nexpected-packages.tsv\nlearning-lab-LICENSE\nll-inputs\nll-inputs/liblzma5.deb\nll-inputs/xz-utils.deb\nll-inputs/at.deb\n',cwd=root,capture_output=True,check=True).stdout
import gzip
(root/'initrd.gz').write_bytes((root/'initrd.original.gz').read_bytes()+gzip.compress(cpio,mtime=0))
disk=root/'prepared.raw'
with disk.open('xb') as f:f.truncate(16*1024**3)
args=['/usr/bin/qemu-system-x86_64','-add-fd',f'fd={lifetime_fd},set=3','-name','Learning Lab fresh image preparation','-machine','q35,accel=kvm','-cpu','host','-smp','2','-m','2048','-nodefaults','-no-user-config','-device','VGA','-drive',f'file={disk},format=raw,if=virtio','-drive',f'file={iso},format=raw,media=cdrom,readonly=on','-kernel',str(root/'vmlinuz'),'-initrd',str(root/'initrd.gz'),'-append','auto=true priority=critical DEBIAN_FRONTEND=text console=ttyS0,115200n8','-nic','none','-display','none','-monitor','none','-serial','stdio','-no-reboot']
(root/'build.json').write_text(json.dumps({'source_iso_sha256':expected,'argv':args,'recipe_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('preseed.cfg','finish-image.sh','finalize-image.sh','expected-packages.tsv')}},indent=2)+'\n')
def launch_bounded(args, phase):
 # RLIMIT_FSIZE would also limit writes to the guest disk. Instead drain the
 # serial pipe continuously and retain at most 4 MiB per stage plus a digest of
 # the entire stream. Any excess is a failed build, not silently accepted.
 process=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True,pass_fds=(lifetime_fd,))
 evidence={'bytes':0,'retained_bytes':0,'overflow':False,'complete':False,'error':None}
 def capture():
  capture_stream(process.stdout,root/(phase+'-console.log'),evidence,4*1024**2,root/(phase+'-output.json'))
 thread=threading.Thread(target=capture,daemon=True);thread.start()
 (root/(phase+'.pid')).write_text(str(process.pid))
 try:
  start=(pathlib.Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split())[19]
  (root/(phase+'-process.json')).write_text(json.dumps({'pid':process.pid,'start_ticks':start,'argv':args,'uid':os.getuid()},indent=2)+'\n')
 except (FileNotFoundError,ProcessLookupError):pass
 return process,thread,evidence

def wait_bounded(process, seconds, phase):
 try:return process.wait(timeout=seconds)
 except subprocess.TimeoutExpired:
  (root/(phase+'-incomplete.json')).write_text(json.dumps({'pid':process.pid,'reason':'deadline exceeded; guest retained, no force-stop or publication'})+'\n')
  raise RuntimeError(phase+' deadline exceeded; task-owned guest may still be running')
process,thread,evidence=launch_bounded(args,'installer')
print('Build directory:',root,flush=True);print('QEMU PID:',process.pid,flush=True)
code=wait_bounded(process,1800,'installation');thread.join(timeout=5);require(not thread.is_alive() and evidence['complete'] and evidence['persisted'] and not evidence['overflow'] and evidence['error'] is None,'Installer output exceeded bound or capture incomplete');console=(root/'installer-console.log').read_text(errors='replace')
require(code==0 and 'LEARNING_LAB_INSTALL_CONFIGURED' in console,'Installation incomplete; retained disk, no publication')
# Boot the fully installed disk separately; no installer/media/kernel override.
final_args=['/usr/bin/qemu-system-x86_64','-add-fd',f'fd={lifetime_fd},set=3','-name','Learning Lab finalization','-machine','q35,accel=kvm','-cpu','host','-smp','2','-m','2048','-nodefaults','-no-user-config','-device','VGA','-drive',f'file={disk},format=raw,if=virtio','-nic','none','-display','none','-monitor','none','-serial','stdio','-no-reboot']
(root/'finalization-argv.json').write_text(json.dumps(final_args,indent=2)+'\n')
process,thread,evidence=launch_bounded(final_args,'finalization')
code=wait_bounded(process,300,'finalization');thread.join(timeout=5);require(not thread.is_alive() and evidence['complete'] and evidence['persisted'] and not evidence['overflow'] and evidence['error'] is None,'Finalization output exceeded bound or capture incomplete');console=(root/'finalization-console.log').read_text(errors='replace')
require(code==0 and console.count('LEARNING_LAB_IMAGE_FINALIZED')==1,'Finalization incomplete; retain disk and logs, no publication')
from final_inventory import finalized_inventory
inventory=finalized_inventory(console,(recipe/'expected-packages.tsv').read_bytes())
(root/'packages.tsv').write_bytes(inventory)
with disk.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
disk.chmod(0o444)
directory_fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
try:os.fsync(directory_fd)
finally:os.close(directory_fd)
require((root/'packages.tsv').read_bytes()==(recipe/'expected-packages.tsv').read_bytes(),'Exact package inventory differs; no substituted versions admitted')
(root/'image-result.json').write_text(json.dumps({'image_id':'debian13-foundation-admin-local-v1','sha256':digest,'bytes':disk.stat().st_size,'format':'raw','source_iso_sha256':expected,'packages_sha256':hashlib.sha256((root/'packages.tsv').read_bytes()).hexdigest()},indent=2)+'\n')
print('Prepared cleanly stopped image:',digest,flush=True)
