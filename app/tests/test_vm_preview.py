"""VM safety fixtures use private disposable directories; no real profiles."""
import json,os,struct,subprocess,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from learning_lab.vm_preview.files import Directory,Refused
from learning_lab.vm_preview.manager import Manager
from learning_lab.vm_preview.policy import inspect_overlay,launch_arguments
from learning_lab.vm_preview.process import Qmp,process_identity

class FilesTests(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def test_symlink_components(self):
  (self.root/'real').mkdir(mode=0o700);(self.root/'link').symlink_to('real',target_is_directory=True)
  with self.assertRaises(OSError):Directory.absolute(self.root/'link')
  with Directory.absolute(self.root) as d:
   (self.root/'bad').symlink_to('/etc/passwd')
   with self.assertRaises(OSError):d.open('bad')
 def test_descriptor_survives_path_substitution(self):
  with Directory.absolute(self.root) as d:
   fd=d.open('disk',True,True);os.write(fd,b'original')
   os.rename(self.root/'disk',self.root/'retained');(self.root/'disk').symlink_to('/etc/passwd')
   self.assertEqual(os.pread(fd,8,0),b'original');os.close(fd)
   with self.assertRaises(OSError):d.open('disk')
 def test_no_replace_publication(self):
  with Directory.absolute(self.root) as d:
   d.write('record.json',{'original':1})
   with self.assertRaises(OSError):d.write('record.json',{'replacement':2})
   self.assertEqual(d.json('record.json'),{'original':1})
 def test_hardlink_fifo_traversal(self):
  (self.root/'file').write_text('x');os.link(self.root/'file',self.root/'linked');os.mkfifo(self.root/'fifo')
  with Directory.absolute(self.root) as d:
   for name in ('file','linked','fifo','../file'):
    with self.assertRaises((Refused,OSError)):d.open(name)
 def test_generation_collision(self):
  with Directory.absolute(self.root) as d:
   with d.child('generation',create=True,exclusive=True) as g:g.write('kept.json',{'x':1})
   with self.assertRaises(Refused):d.child('generation',create=True,exclusive=True)
   with d.child('generation') as g:self.assertEqual(g.json('kept.json'),{'x':1})

@unittest.skipUnless(Path('/usr/bin/qemu-img').exists(),'Optional QEMU tooling absent')
class PolicyTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.disk=Path(self.temp.name)/'disk.qcow2';subprocess.run(['qemu-img','create','-f','qcow2',str(self.disk),'16G'],check=True,capture_output=True)
 def tearDown(self):self.temp.cleanup()
 def test_header_embedded_backing_rejection(self):
  fd=os.open(self.disk,os.O_RDWR)
  try:
   self.assertFalse(inspect_overlay(fd)['dirty']);os.pwrite(fd,struct.pack('>Q',4096),8)
   with self.assertRaisesRegex(Refused,'backing'):inspect_overlay(fd)
  finally:os.close(fd)
 def test_external_data_and_extensions_rejected(self):
  original=self.disk.read_bytes()
  for offset,value in ((72,struct.pack('>Q',4)),(80,struct.pack('>Q',1)),(112,struct.pack('>II',0x44415441,8)),(104,b'\x01')):
   self.disk.write_bytes(original);fd=os.open(self.disk,os.O_RDWR)
   try:
    os.pwrite(fd,value,offset)
    with self.assertRaises(Refused):inspect_overlay(fd)
   finally:os.close(fd)
 def test_fixed_graph(self):
  a=launch_arguments(7,8,9,str(uuid.uuid4()),'/run/user/1000/private/qmp')
  nodes=[json.loads(a[i+1]) for i,v in enumerate(a) if v=='-blockdev']
  self.assertEqual(nodes[-1]['backing'],'base');self.assertTrue(nodes[1]['read-only'])
  self.assertEqual({n['filename'] for n in nodes if 'filename' in n},{'/dev/fdset/1','/dev/fdset/2'})
  self.assertNotIn('-netdev',a);self.assertNotIn('-fsdev',a)
 def test_qmp_rejects_arbitrary_calls(self):
  q=object.__new__(Qmp)
  for cmd in ('human-monitor-command','guest-exec','blockdev-add','migrate','screendump'):
   with self.assertRaises(Refused):q.call(cmd)
 def test_current_process_is_not_qemu(self):
  with self.assertRaises(Refused):process_identity(os.getpid())

@unittest.skipUnless(Path('/usr/bin/qemu-img').exists(),'Optional QEMU tooling absent')
class ManagerFixture(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.base=self.root/'fake-base';self.base.write_bytes(b'fixture')
  self.m=Manager(self.root/'vm','a'*64,self.root/'gate')
  self.p1=patch.object(self.m,'admission');self.p1.start()
  self.p2=patch.object(self.m,'image',side_effect=lambda root:os.open(self.base,os.O_RDONLY));self.p2.start()
 def tearDown(self):self.p2.stop();self.p1.stop();self.temp.cleanup()
 def current(self):
  with self.m.access() as (_,gate,p):return self.m.current(p)

class ManagerTests(ManagerFixture):
 def test_reset_confirmation_and_retention(self):
  with self.assertRaises(Refused):self.m.reset()
  first=self.m.reset(confirmed=True);path=self.root/'vm'/'profiles'/('a'*64)/'generations'/first['generation']/'disk.qcow2';before=path.read_bytes()
  self.m.progress('hint');self.m.progress('complete');second=self.m.reset('Challenge',True)
  self.assertNotEqual(first['generation'],second['generation']);self.assertEqual(path.read_bytes(),before)
  self.assertEqual(second['hints'],0);self.assertIsNone(second['completion'])
  with self.assertRaises(Refused):self.m.progress('hint')
 def test_reopen_missing_disk(self):
  first=self.m.reset(confirmed=True);self.m.progress('next');self.m.progress('complete')
  other=Manager(self.root/'vm','a'*64,self.root/'gate');self.assertEqual(other.status()['session']['session'],first['session'])
  self.assertEqual(other.status()['session']['completion']['kind'],'self-reviewed')
  path=self.root/'vm'/'profiles'/('a'*64)/'generations'/first['generation']/'disk.qcow2';path.rename(path.with_name('retained.qcow2'))
  self.assertEqual(other.status()['state'],'disk-missing')
 def test_cross_profile_cross_store_lock(self):
  with self.m.access() as (_,gate,p):fd=self.m.gate(gate)
  try:
   for home,profile in ((self.root/'vm','b'*64),(self.root/'other','a'*64)):
    other=Manager(home,profile,self.root/'gate')
    with self.assertRaisesRegex(Refused,'already running'):other.start()
    with self.assertRaisesRegex(Refused,'already running'):other.reset(confirmed=True)
  finally:os.close(fd)
 def test_interrupted_publication_preserves_active(self):
  first=self.m.reset(confirmed=True);original=Directory.write
  def fail(d,name,value,replace=False):
   if name=='current.json':raise OSError(28,'No space left on device')
   return original(d,name,value,replace)
  with patch.object(Directory,'write',fail):
   with self.assertRaises(OSError):self.m.reset(confirmed=True)
  self.assertEqual(self.current(),first)
  self.assertEqual(len(list((self.root/'vm'/'profiles'/('a'*64)/'generations').iterdir())),2)
 def test_generation_collision_cannot_replace(self):
  first=self.m.reset(confirmed=True)
  with patch('learning_lab.vm_preview.manager.uuid.uuid4',return_value=uuid.UUID(first['generation'])):
   with self.assertRaises(Refused):self.m.reset(confirmed=True)
  self.assertEqual(self.current(),first)
 def test_older_pins_preserved(self):
  self.m.reset(confirmed=True);path=self.root/'vm'/'profiles'/('a'*64)/'current.json';before=path.read_bytes();self.m.pin={**self.m.pin,'backend':'unavailable-version'}
  with self.assertRaisesRegex(Refused,'older'):self.m.status()
  self.assertEqual(path.read_bytes(),before)
 def test_forged_process_record_no_signal(self):
  self.m.reset(confirmed=True)
  with self.m.access() as (_,gate,p):
   s=self.m.current(p);gate.write('running.json',{'schema_version':1,'run':str(uuid.uuid4()),'store':self.m.binding,'profile':self.m.profile,'session':s['session'],'generation':s['generation'],'state':'running','process':{'pid':os.getpid(),'start':'0','boot':'fake','argv_sha256':'fake'}})
  with self.assertRaises(Refused):self.m.stop()
 def test_dead_launch_intent_recovers(self):
  first=self.m.reset(confirmed=True)
  with self.m.access() as (_,gate,p):gate.write('running.json',{'schema_version':1,'run':str(uuid.uuid4()),'store':self.m.binding,'profile':self.m.profile,'session':first['session'],'generation':first['generation'],'state':'intent','process':None})
  with self.assertRaisesRegex(Refused,'Interrupted'):self.m.status()
  second=self.m.reset(confirmed=True);self.assertNotEqual(first['generation'],second['generation'])
 def test_missing_image_preserves_session(self):
  first=self.m.reset(confirmed=True);self.p2.stop()
  with self.assertRaises((Refused,FileNotFoundError)):self.m.reset(confirmed=True)
  self.assertEqual(self.current(),first)

class MoreManagerTests(ManagerFixture):
 def test_missing_whole_generation_reset_retains_metadata(self):
  first=self.m.reset(confirmed=True);p=self.root/'vm'/'profiles'/('a'*64);g=p/'generations'/first['generation'];g.rename(g.with_name('unavailable-generation'))
  second=self.m.reset(confirmed=True)
  self.assertNotEqual(first['generation'],second['generation']);self.assertTrue(list(p.glob('retained-*.json')))
 def test_operation_lock_across_processes(self):
  with self.m.access() as (_,gate,p):
   script='import fcntl,os,sys; f=os.open(sys.argv[1],os.O_RDWR); fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)'
   r=subprocess.run([os.sys.executable,'-c',script,str(self.root/'gate'/'operations.lock')],capture_output=True)
   self.assertNotEqual(r.returncode,0);self.assertIn(b'BlockingIOError',r.stderr)
 def test_tampered_generation_refuses_start(self):
  first=self.m.reset(confirmed=True);p=self.root/'vm'/'profiles'/('a'*64)/'generations'/first['generation']/'origin.json';v=json.loads(p.read_text());v['session']=str(uuid.uuid4());p.write_text(json.dumps(v))
  with self.assertRaisesRegex(Refused,'provenance'):self.m.start()
 def test_launch_rejects_changed_file_size_and_chain(self):
  first=self.m.reset(confirmed=True);p=self.root/'vm'/'profiles'/('a'*64)/'generations'/first['generation']/'disk.qcow2'
  fd=os.open(p,os.O_RDWR);os.pwrite(fd,struct.pack('>Q',4096),8);os.close(fd)
  with self.assertRaisesRegex(Refused,'backing'):self.m.start()
 def test_missing_socket_not_treated_as_stopped(self):
  first=self.m.reset(confirmed=True)
  r={'schema_version':1,'run':str(uuid.uuid4()),'store':self.m.binding,'profile':self.m.profile,'session':first['session'],'generation':first['generation'],'state':'running','process':{'pid':9876,'start':'1','boot':'fixture','argv_sha256':'0'*64}}
  with self.m.access() as (_,gate,p):gate.write('running.json',r)
  with patch('learning_lab.vm_preview.manager.same_process',return_value=True),patch('learning_lab.vm_preview.manager.verify_launch'):
   with self.assertRaisesRegex(Refused,'control is unavailable'):self.m.status()
  self.assertEqual(self.current(),first)
 def test_prepare_crash_before_origin_leaves_unpublished_generation(self):
  first=self.m.reset(confirmed=True);original=Directory.write
  def fail(d,name,value,replace=False):
   if name=='origin.json':raise OSError(28,'No space left on device')
   return original(d,name,value,replace)
  with patch.object(Directory,'write',fail):
   with self.assertRaises(OSError):self.m.reset(confirmed=True)
  self.assertEqual(self.current(),first)

 def test_host_reboot_missing_runtime_preserves_unclean_disk(self):
  first=self.m.reset(confirmed=True)
  with self.m.access() as (_,gate,p):self.m.journal(p,first['generation'],'running')
  path=self.root/'vm'/'profiles'/('a'*64)/'generations'/first['generation']/'disk.qcow2';before=path.read_bytes()
  self.assertEqual(self.m.status()['state'],'unclean')
  with self.assertRaisesRegex(Refused,'Unclean'):self.m.start()
  self.assertEqual(path.read_bytes(),before)
  self.m.reset(confirmed=True);self.assertEqual(path.read_bytes(),before)
 def test_missing_journal_cannot_resume(self):
  first=self.m.reset(confirmed=True);p=self.root/'vm'/'profiles'/('a'*64)/'generations'/first['generation']
  (p/'lifecycle.json').rename(p/'retained-journal.json')
  with self.assertRaisesRegex(Refused,'journal is missing'):self.m.start()
  self.m.reset(confirmed=True);self.assertTrue((p/'disk.qcow2').exists())
 def test_clean_journal_allows_resume_policy(self):
  first=self.m.reset(confirmed=True)
  with self.m.access() as (_,gate,p):
   self.m.journal(p,first['generation'],'stopped');self.assertEqual(self.m.lifecycle(p,first['generation']),'stopped')
  self.assertEqual(self.m.status()['state'],'stopped')
 def test_free_space_admission(self):
  self.p1.stop()
  from types import SimpleNamespace
  with patch('learning_lab.vm_preview.manager.os.fstatvfs',return_value=SimpleNamespace(f_bavail=1,f_frsize=4096)):
   with self.assertRaisesRegex(Refused,'Insufficient'):self.m.reset(confirmed=True)
  self.assertIsNone(self.current())

class BoundaryTests(unittest.TestCase):
 def test_imported_vm_engine_rejected(self):
  from learning_lab.authoring import resource
  from learning_lab.portable import load_portable
  value=json.loads(resource('permissions.lab.json'));value['engine']['id']='real-linux-vm'
  with self.assertRaises(ValueError):load_portable(json.dumps(value).encode())
 def test_stale_record_rejected(self):
  from learning_lab.vm_preview.process import same_process
  actual={'pid':123,'start':'new','boot':'current','argv_sha256':'a'*64}
  with patch('learning_lab.vm_preview.process.process_identity',return_value=actual):
   with self.assertRaisesRegex(Refused,'Stale'):same_process({'process':{**actual,'start':'old'}})
 def test_qmp_wrong_peer_rejected(self):
  import socket,stat,struct
  from types import SimpleNamespace
  from unittest.mock import MagicMock
  fake=MagicMock();fake.getsockopt.return_value=struct.pack('3i',456,os.getuid(),os.getgid())
  with patch('learning_lab.vm_preview.process.same_process',return_value=True),patch('learning_lab.vm_preview.process.os.stat',return_value=SimpleNamespace(st_mode=stat.S_IFSOCK,st_uid=os.getuid())),patch('learning_lab.vm_preview.process.socket.socket',return_value=fake):
   with self.assertRaisesRegex(Refused,'peer'):Qmp(SimpleNamespace(fd=3),{'process':{'pid':123}})
  fake.close.assert_called_once();fake.sendall.assert_not_called()


class ReviewPolicyTests(unittest.TestCase):
 def test_forged_matching_digest_cannot_change_launch_policy(self):
  from learning_lab.vm_preview.policy import verify_arguments
  run=str(uuid.uuid4());socket_path='/private/'+run+'/qmp'
  args=launch_arguments(7,8,9,run,socket_path);verify_arguments(args,run,socket_path)
  for mutation in (args+['-netdev','user,id=escape'],[a.replace('"read-only":true','"read-only":false') for a in args],args[:-2],args+['-add-fd','fd=7,set=1']):
   with self.assertRaises(ValueError):verify_arguments(mutation,run,socket_path)
 def test_parent_substitution_does_not_redirect_descriptor_write(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'private').mkdir(mode=0o700)
   with Directory.absolute(root/'private') as pinned:
    (root/'private').rename(root/'retained');(root/'private').mkdir(mode=0o700)
    pinned.write('record.json',{'pinned':True})
   self.assertTrue((root/'retained/record.json').exists());self.assertFalse((root/'private/record.json').exists())
 @unittest.skipUnless(Path('/usr/bin/qemu-img').exists(),'Optional QEMU absent')
 def test_actual_external_data_image_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);disk=root/'external.qcow2'
   subprocess.run(['/usr/bin/qemu-img','create','-f','qcow2','-o','data_file='+str(root/'data.raw')+',data_file_raw=on',str(disk),'16G'],check=True,capture_output=True)
   fd=os.open(disk,os.O_RDONLY)
   try:
    with self.assertRaises(Refused):inspect_overlay(fd)
   finally:os.close(fd)
 def test_runner_checks_survive_python_optimization(self):
  runner=Path(__file__).parents[1]/'learning_lab/vm_preview/runner.py'
  result=subprocess.run([os.sys.executable,'-I','-O','-B',str(runner),'1','/usr/bin/false'],capture_output=True,text=True)
  self.assertNotEqual(result.returncode,0);self.assertIn('Invalid file ceiling',result.stderr)

class ReviewLifecycleTests(ManagerFixture):
 def record(self,state='stopped'):
  first=self.m.reset(confirmed=True)
  r={'schema_version':1,'run':str(uuid.uuid4()),'store':self.m.binding,'profile':self.m.profile,'session':first['session'],'generation':first['generation'],'state':state,'process':None}
  with self.m.access() as (_,gate,p):gate.write('running.json',r)
  return first,r
 def test_missing_or_stopped_record_with_live_lock_never_claims_stopped(self):
  first,r=self.record()
  for missing in (False,True):
   with self.m.access() as (_,gate,p):
    if missing:os.rename('running.json','retained-runtime.json',src_dir_fd=gate.fd,dst_dir_fd=gate.fd)
    fd=self.m.gate(gate)
   try:
    with self.assertRaisesRegex(Refused,'already running'):self.m.stop()
    with self.assertRaisesRegex(Refused,'already running'):self.m.status()
   finally:os.close(fd)
 def test_interrupted_stop_publication_blocks_resume(self):
  first,r=self.record('stopped')
  with self.m.access() as (_,gate,p):self.m.journal(p,first['generation'],'running')
  self.assertEqual(self.m.status()['state'],'unclean')
  with self.assertRaisesRegex(Refused,'Unclean'):self.m.start()
 def test_unclean_runtime_cannot_be_overridden_by_clean_journal(self):
  first,r=self.record('unclean')
  with self.m.access() as (_,gate,p):self.m.journal(p,first['generation'],'stopped')
  with self.assertRaisesRegex(Refused,'Unclean runtime'):self.m.start()
 def test_final_record_with_reused_pid_does_not_signal_it(self):
  first,r=self.record();r['process']={'pid':os.getpid(),'start':'old','boot':'old','argv_sha256':'old'}
  with self.m.access() as (_,gate,p):gate.write('running.json',r,replace=True)
  self.assertIn('lifetime lock is free',self.m.stop())


class RealIoReviewTests(unittest.TestCase):
 @unittest.skipUnless(Path('/usr/bin/qemu-io').exists(),'Optional QEMU I/O fixture absent')
 def test_real_qemu_enospc_injection(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'disk.raw').write_bytes(bytes(8192));(root/'fault.conf').write_text('[inject-error]\nevent = "write_aio"\nerrno = "28"\n')
   result=subprocess.run(['/usr/bin/qemu-io','-f','raw','-c','write 0 4096',f'blkdebug:{root}/fault.conf:{root}/disk.raw'],capture_output=True,text=True,env={**os.environ,'LC_ALL':'C'},timeout=10)
   self.assertNotEqual(result.returncode,0);self.assertIn('No space left on device',result.stdout+result.stderr)
   self.assertEqual((root/'disk.raw').read_bytes(),bytes(8192))
 def test_root_vm_refusal_is_lazy(self):
  with tempfile.TemporaryDirectory() as d,patch('learning_lab.vm_preview.manager.os.getuid',return_value=0):
   manager=Manager(Path(d)/'vm','f'*64,Path(d)/'gate')
   with self.assertRaisesRegex(Refused,'ordinary user'):manager.status()
   self.assertFalse((Path(d)/'vm').exists())

class StopCompletionTests(ManagerFixture):
 """Guest shutdown is a fixture; lifetime and operation locks are real flock calls.
 Native installed tests separately verify the QMP/process-exit boundary.
 """
 record=ReviewLifecycleTests.record
 def stop_fixture(self):
  from contextlib import ExitStack
  from unittest.mock import MagicMock
  first,r=self.record('running');r['process']={'pid':12345,'start':'fixture','boot':'fixture','argv_sha256':'fixture'}
  with self.m.access() as (_,gate,p):
   gate.write('running.json',r,replace=True)
   with gate.child(r['run'],create=True):pass
   self.m.journal(p,first['generation'],'running')
   held=self.m.gate(gate)
  stack=ExitStack();self.addCleanup(stack.close)
  stack.enter_context(patch('learning_lab.vm_preview.manager.same_process',return_value=True))
  stack.enter_context(patch('learning_lab.vm_preview.manager.verify_launch'))
  q=MagicMock();q.__enter__.return_value=q;q.powerdown.return_value=True
  stack.enter_context(patch('learning_lab.vm_preview.manager.Qmp',return_value=q))
  return first,r,held,q
 def test_delayed_lock_release_precedes_publication(self):
  import threading,time
  first,r,held,q=self.stop_fixture();shutdown=threading.Event();observed=[]
  q.powerdown.side_effect=lambda _:shutdown.set() or True
  def release():
   shutdown.wait(2);time.sleep(.2)
   observed.append(json.loads((self.root/'gate/running.json').read_text())['state'])
   os.close(held)
  thread=threading.Thread(target=release);thread.start()
  try:self.assertEqual(self.m.stop(),'Cleanly stopped')
  finally:thread.join(3)
  self.assertEqual(observed,['running'])
  self.assertEqual(self.m.status()['state'],'stopped')
  self.assertEqual(self.current(),first)
 def test_timeout_retains_records_and_never_claims_completion(self):
  import time
  first,r,held,q=self.stop_fixture();runtime=self.root/'gate/running.json';journal=self.root/'vm/profiles'/self.m.profile/'generations'/first['generation']/'lifecycle.json'
  before=(runtime.read_bytes(),journal.read_bytes());started=time.monotonic()
  try:
   with self.assertRaisesRegex(Refused,'Stop completion was not published'):self.m.stop()
   self.assertGreaterEqual(time.monotonic()-started,5)
   self.assertEqual((runtime.read_bytes(),journal.read_bytes()),before)
   with self.m.access() as (_,gate,p):
    with self.assertRaisesRegex(Refused,'already running'):self.m.gate(gate)
  finally:os.close(held)
 def test_competing_acquisition_blocked_through_publication(self):
  first,r,held,q=self.stop_fixture();q.powerdown.side_effect=lambda _:os.close(held) or True
  original=self.m.journal;results=[]
  def publish(profile,generation,state):
   # Separate processes must fail to take either lock during final publication.
   for name in ('running.lock','operations.lock'):
    script='import os,fcntl,sys; f=os.open(sys.argv[1],os.O_RDWR); fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)'
    child=subprocess.run([os.sys.executable,'-I','-B','-c',script,str(self.root/'gate'/name)],capture_output=True,timeout=5)
    results.append(child.returncode!=0 and b'BlockingIOError' in child.stderr)
   return original(profile,generation,state)
  with patch.object(self.m,'journal',side_effect=publish):self.assertEqual(self.m.stop(),'Cleanly stopped')
  self.assertEqual(results,[True,True]);self.assertEqual(self.current(),first)
