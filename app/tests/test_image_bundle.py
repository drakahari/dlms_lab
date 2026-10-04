"""Offline importer security/transaction fixtures. No real profile/image/VM."""
import copy,errno,gzip,hashlib,json,os,shutil,socket,stat,struct,subprocess,tempfile,threading,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from offline_image_fixtures import SigningFixture,hash_
from learning_lab.vm_preview import image_bundle as bundle, bundle_archive as archive, bundle_signature as signature
from learning_lab.vm_preview.image_catalog import Catalog,canonical,digest,production_catalog,resource
from learning_lab.vm_preview.files import Directory,Refused

@unittest.skipUnless(shutil.which('gpg') and shutil.which('gpgv'),'Optional GnuPG verifier/test signer absent')
class BundleTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.signer=SigningFixture()
 @classmethod
 def tearDownClass(cls):cls.signer.close()
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='oll-bundle-test-');self.root=Path(self.tmp.name);self.path=self.root/'test.llvmimage';self.home=self.root/'vm';self.gate=self.root/'gate'
  self.catalog,self.manifest,self.members=self.signer.bundle(self.path)
 def tearDown(self):self.tmp.cleanup()
 def install(self,**kwargs):return bundle.import_bundle(self.path,self.home,_catalog=self.catalog,_gate_root=self.gate,**kwargs)
 def target(self):return self.home/'images'/self.manifest['descriptor']['sha256']
 def inventory(self,root):return {str(p.relative_to(root)):hash_(p.read_bytes()) for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
 def rewrite(self,edit):
  m=copy.deepcopy(self.members);edit(m);self.signer.write(self.path,m)
 def test_signed_validation_does_not_install(self):
  self.assertEqual(bundle.validate_bundle(self.path,_catalog=self.catalog)['result'],'valid');self.assertFalse(self.home.exists())
 def test_production_empty_trust_rejects_test_bundle(self):
  self.assertFalse(production_catalog().releases);self.assertFalse(production_catalog().keys)
  with self.assertRaisesRegex(Refused,'allowlist'):bundle.validate_bundle(self.path)
  self.assertFalse(self.home.exists())
 def test_register_and_exact_duplicate_is_noop(self):
  self.assertEqual(self.install()['result'],'installed');before=self.inventory(self.target())
  self.assertEqual(self.install()['result'],'already-installed');self.assertEqual(before,self.inventory(self.target()))
  self.assertEqual((self.target()/'base.raw').stat().st_mode&0o222,0)
 def test_same_raw_different_manifest_conflicts(self):
  self.install();before=self.inventory(self.target())
  self.catalog,self.manifest,self.members=self.signer.bundle(self.path,manifest_edit=lambda m:m.update(release_id='another-test-release'))
  with self.assertRaisesRegex(Refused,'conflict'):self.install()
  self.assertEqual(before,self.inventory(self.target()))
 def test_different_receipt_preserved(self):
  self.install();p=self.target()/'receipt.json';p.chmod(0o600);p.write_bytes(b'{}');before=self.inventory(self.target())
  with self.assertRaisesRegex(Refused,'conflict'):self.install()
  self.assertEqual(before,self.inventory(self.target()))
 def test_legacy_without_receipt_never_adopted(self):
  dest=self.target();dest.mkdir(parents=True,mode=0o700);dest.parent.chmod(0o700);self.home.chmod(0o700)
  (dest/'base.raw').write_bytes(b'SYNTHETIC NOT BOOTABLE\n'*128);(dest/'base.raw').chmod(0o444)
  (dest/'provenance.json').write_bytes(canonical(self.manifest['descriptor'])+b'\n');before=self.inventory(dest)
  with self.assertRaisesRegex(Refused,'legacy receipt'):self.install()
  self.assertEqual(before,self.inventory(dest));self.assertFalse((dest/'receipt.json').exists())
 def test_valid_signature_unapproved_manifest_rejected(self):
  def signed_unapproved(m):
   m['manifest.json']=m['manifest.json'].replace(b'synthetic-test-only-1',b'synthetic-test-only-2')
   m['manifest.sig']=self.signer.sign(m['manifest.json'])
  self.rewrite(signed_unapproved)
  with self.assertRaisesRegex(Refused,'allowlist'):self.install()
 def test_signature_tampering_rejected(self):
  self.rewrite(lambda m:m.update({'manifest.sig':b'not a signature'}))
  with self.assertRaisesRegex(Refused,'Signature'):self.install()
  self.assertFalse(self.home.exists())
 def test_real_other_signer_and_multiple_signatures_fail_closed(self):
  other=SigningFixture()
  try:
   original=self.members['manifest.sig'];raw=self.members['manifest.json']
   self.catalog.keys[self.signer.fingerprint]=self.signer.public+other.public
   for sig in (other.sign(raw),original+original):
    self.rewrite(lambda m:m.update({'manifest.sig':sig}))
    with self.assertRaises(ValueError):self.install()
    self.assertFalse(self.home.exists())
  finally:other.close()
 def test_trust_and_signature_precede_payload_and_destination(self):
  real=archive.Archive.open;opened=[]
  def track(a,name):opened.append(name);return real(a,name)
  self.rewrite(lambda m:m.update({'manifest.sig':b'bad signature'}))
  with patch.object(archive.Archive,'open',track):
   with self.assertRaises(ValueError):self.install()
  self.assertEqual(opened,['manifest.json','manifest.sig']);self.assertFalse(self.home.exists())
 def test_mutated_payload_after_headers_fails_crc_or_signed_hash(self):
  real=archive.preflight
  def mutate(fd):
   members=real(fd);offset,size,crc=members['image.raw.gz']
   with self.path.open('r+b') as stream:stream.seek(offset);stream.write(b'X')
   return members
  with patch.object(archive,'preflight',side_effect=mutate):
   with self.assertRaises(ValueError):self.install()
  self.assertFalse(self.target().exists())
 def test_manifest_bounds_canonical_and_json(self):
  for raw in (b'{broken',b'[]',b'{"schema_version":1,"schema_version":1}',b' '*65537,self.members['manifest.json']+b' ',b'{"x":1.2}',b'{"x":NaN}',b'['*1500):
   with self.subTest(raw=raw[:40]):
    self.rewrite(lambda m:m.update({'manifest.json':raw}))
    with self.assertRaises((ValueError,zipfile.BadZipFile)):self.install()
 def test_unknown_version_backend_and_lessons(self):
  for edit in (lambda m:m.update(schema_version=2),lambda m:m.update(backend='new-backend'),lambda m:m.update(lessons=[{'id':'bad','sha256':'0'*64}]),lambda m:m.update(script='id')):
   self.catalog,self.manifest,self.members=self.signer.bundle(self.path,manifest_edit=edit)
   with self.assertRaises(ValueError):self.install()
 def test_withdrawn_and_resume_only_import(self):
  self.catalog,self.manifest,self.members=self.signer.bundle(self.path,state='withdrawn')
  with self.assertRaisesRegex(Refused,'withdrawn'):self.install()
  self.catalog,self.manifest,self.members=self.signer.bundle(self.path,state='resume-only')
  self.assertEqual(self.install()['result'],'installed')
 def test_compressed_and_metadata_tampering(self):
  for name in ('image.raw.gz','notices.txt','packages.json','provenance.json'):
   with self.subTest(name=name):
    self.rewrite(lambda m:m.update({name:bytes([m[name][0]^1])+m[name][1:]}))
    with self.assertRaises(ValueError):self.install()
    self.assertFalse(self.target().exists())
 def test_raw_digest_size_and_gzip_limits(self):
  cases=[{'descriptor':{'sha256':'0'*64}}, {'descriptor':{'bytes':1}}, {'descriptor':{'bytes':99999}},
         {'compressed':gzip.compress(b'SYNTHETIC NOT BOOTABLE\n'*128)[:-3]},
         {'compressed':gzip.compress(b'SYNTHETIC NOT BOOTABLE\n'*128)+b'junk'},
         {'compressed':gzip.compress(b'SYNTHETIC NOT BOOTABLE\n'*128)+gzip.compress(b'')},
         {'compressed':gzip.compress(b'x'*200000),'descriptor':{'bytes':16}}]
  for values in cases:
   with self.subTest(values=str(values)[:80]):
    self.catalog,self.manifest,self.members=self.signer.bundle(self.path,**values)
    with self.assertRaises((ValueError, __import__('zlib').error)):self.install()
    self.assertFalse(self.target().exists())
 def test_unknown_paths_duplicates_links_types(self):
  for name in ('../outside','/absolute','folder/file','folder/','manifest.json'):
   self.signer.write(self.path,self.members)
   import warnings
   with warnings.catch_warnings(record=True):
    warnings.simplefilter('always')
    with zipfile.ZipFile(self.path,'a') as z:z.writestr(name,b'x')
   with self.assertRaises(ValueError):self.install()
  for mode in (stat.S_IFLNK,stat.S_IFIFO,stat.S_IFDIR):
   with zipfile.ZipFile(self.path,'w') as z:
    for name,raw in self.members.items():
     info=zipfile.ZipInfo(name);info.external_attr=(mode|0o600)<<16;z.writestr(info,raw)
   with self.assertRaises(ValueError):self.install()
 def test_outer_compression_comments_encryption_and_flags(self):
  self.signer.write(self.path,self.members,compression=zipfile.ZIP_DEFLATED)
  with self.assertRaises(ValueError):self.install()
  self.signer.write(self.path,self.members)
  with zipfile.ZipFile(self.path,'a') as z:z.comment=b'forbidden'
  with self.assertRaises(ValueError):self.install()
  for flag in (1,8,2048):
   self.signer.write(self.path,self.members);raw=bytearray(self.path.read_bytes());at=raw.index(b'PK\x01\x02');struct.pack_into('<H',raw,at+8,flag);self.path.write_bytes(raw)
   with self.assertRaises(ValueError):self.install()
 def test_directory_bound_precedes_member_reads(self):
  for field,value in ((-12,50000),(-10,50000),(-6,0xffffffff)):
   self.signer.write(self.path,self.members);raw=bytearray(self.path.read_bytes())
   if field==-6:struct.pack_into('<I',raw,len(raw)+field,value)
   else:struct.pack_into('<H',raw,len(raw)+field,value)
   self.path.write_bytes(raw)
   with patch.object(archive,'StoredMember',side_effect=AssertionError('Payload read before bounds')):
    with self.assertRaises(ValueError):self.install()
 def test_headers_cannot_be_reparsed_after_preflight(self):
  original=archive.preflight
  def mutate(fd):
   members=original(fd)
   raw=bytearray(self.path.read_bytes())
   # A concurrent writer changes the directory request AFTER bounded parsing.
   struct.pack_into('<I',raw,len(raw)-12,archive.CD_LIMIT+1)
   self.path.write_bytes(raw)
   return members
  with patch.object(archive,'preflight',side_effect=mutate),patch.object(archive.zipfile,'ZipFile',side_effect=AssertionError('Mutable headers reparsed')):
   self.assertEqual(bundle.validate_bundle(self.path,_catalog=self.catalog)['result'],'valid')
 def test_duplicate_retry_requires_parent_sync(self):
  self.install();real=os.fsync;parents=[]
  def fail(fd):
   name=os.readlink('/proc/self/fd/'+str(fd))
   if name==str(self.home/'images'):
    parents.append(name);raise OSError(errno.ENOSPC,'retry directory sync failure')
   return real(fd)
  with patch.object(bundle.os,'fsync',side_effect=fail):
   with self.assertRaisesRegex(OSError,'retry directory'):self.install()
  self.assertTrue(parents);self.assertTrue((self.target()/'receipt.json').exists())
 def test_local_header_ranges_and_truncation(self):
  self.signer.write(self.path,self.members);original=self.path.read_bytes();central=original.index(b'PK\x01\x02')
  for offset,value in ((30,ord('x')),(14,255),(22,255),(central+42,255)):
   raw=bytearray(original);raw[offset]=value;self.path.write_bytes(raw)
   with self.assertRaises(ValueError):self.install()
  for raw in (original[:-1],b'prefix'+original,original+b'trailer'):
   self.path.write_bytes(raw)
   with self.assertRaises(ValueError):self.install()
 def test_zip64_central_sizes_offsets_and_bounds(self):
  original=self.path.read_bytes();end=list(struct.unpack('<4s4H2IH',original[-22:]));cd_at=end[6]
  central=original[cd_at:-22];position=0;rebuilt=bytearray()
  for _ in range(6):
   row=list(struct.unpack_from('<4s6H3I5H2I',central,position));length=46+row[10]+row[11]+row[12]
   name=central[position+46:position+46+row[10]]
   extra=struct.pack('<HHQQQ',1,24,row[9],row[8],row[16])
   row[2]=45;row[8]=row[9]=row[16]=0xffffffff;row[11]=len(extra)
   rebuilt.extend(struct.pack('<4s6H3I5H2I',*row)+name+extra);position+=length
  payload=bytearray(original[:cd_at]);position=0
  while position<cd_at:
   row=struct.unpack_from('<4s5H3I2H',payload,position)
   struct.pack_into('<H',payload,position+4,45)
   position+=30+row[9]+row[10]+row[7]
  end[5]=len(rebuilt);valid=payload+rebuilt+struct.pack('<4s4H2IH',*end)
  self.path.write_bytes(valid);self.assertEqual(self.install()['result'],'installed')
  for field in (4,12,20):
   bad=bytearray(valid);nlen=struct.unpack_from('<H',bad,cd_at+28)[0]
   struct.pack_into('<Q',bad,cd_at+46+nlen+field,2**63)
   self.path.write_bytes(bad)
   with self.assertRaises(ValueError):bundle.validate_bundle(self.path,_catalog=self.catalog)
 def test_multiple_output_chunks_preserve_exact_raw_bytes(self):
  raw=b'nonbootable synthetic bytes\n'*100000
  self.catalog,self.manifest,self.members=self.signer.bundle(self.path,raw=raw)
  self.assertEqual(self.install()['result'],'installed')
  self.assertEqual((self.target()/'base.raw').read_bytes(),raw)
 def test_required_zip64_local_extra_accepted(self):
  self.signer.write(self.path,self.members,zip64=True)
  self.assertEqual(self.install()['result'],'installed')
 def test_unsupported_zip_extras_rejected(self):
  with zipfile.ZipFile(self.path,'w') as z:
   for name,raw in self.members.items():
    i=zipfile.ZipInfo(name);i.extra=b'\x55\x54\x01\x00\x00';z.writestr(i,raw)
  with self.assertRaises(ValueError):self.install()
 def test_cancel_before_and_after_payload(self):
  with self.assertRaisesRegex(Refused,'cancelled'):self.install(_cancel=lambda:True)
  self.assertFalse(self.home.exists())
  event=threading.Event()
  with self.assertRaisesRegex(Refused,'cancelled'):self.install(_cancel=event.is_set,_checkpoint=lambda n:event.set() if n=='prepared' else None)
  self.assertFalse(self.target().exists());self.assertTrue(list((self.home/'staging').iterdir()))
 def test_crash_boundaries_and_retry(self):
  for point in ('compressed-verified','prepared','before-publication','published','durable'):
   self.home=self.root/point
   def hook(name):
    if name==point:raise OSError(errno.EIO,'injected crash')
   with self.assertRaises(OSError):self.install(_checkpoint=hook)
   published=point in ('published','durable');self.assertEqual(self.target().exists(),published)
   result=self.install();self.assertEqual(result['result'],'already-installed' if published else 'installed')
 def test_disk_admission_enospc_and_short_writes(self):
  with patch.object(bundle,'enough_space',side_effect=Refused('Insufficient space')):
   with self.assertRaises(Refused):self.install()
  with patch.object(bundle,'write_all',side_effect=OSError(errno.ENOSPC,'Full')):
   with self.assertRaises(OSError):self.install()
  self.assertFalse(self.target().exists())
  real=os.write
  with patch.object(bundle.os,'write',side_effect=lambda fd,b:real(fd,b[:max(1,len(b)//2)])):
   self.assertEqual(self.install()['result'],'installed')
 def test_concurrent_imports_and_operation_lock(self):
  with Directory.absolute(self.home,create=True) as root,bundle.import_lock(root):
   with self.assertRaisesRegex(ValueError,'import is in progress'):self.install()
  with bundle.publication_lock(self.gate):
   with self.assertRaisesRegex(ValueError,'VM operation'):self.install()
  self.assertFalse(self.target().exists());self.assertEqual(self.install()['result'],'installed')
 def test_source_symlink_hardlink_fifo_rejected(self):
  original=self.path;link=self.root/'link';link.symlink_to(original)
  for path in (link,):
   with self.assertRaises(OSError):bundle.validate_bundle(path,_catalog=self.catalog)
  link.unlink();os.link(original,link)
  with self.assertRaises(ValueError):self.install()
  link.unlink();fifo=self.root/'fifo';os.mkfifo(fifo)
  with self.assertRaises(ValueError):bundle.validate_bundle(fifo,_catalog=self.catalog)
 def test_source_substitution_uses_open_descriptor(self):
  real=bundle.header
  def replace(a,c):
   result=real(a,c);self.path.rename(self.root/'retained-input');self.path.symlink_to('/etc/passwd');return result
  with patch.object(bundle,'header',side_effect=replace):self.assertEqual(self.install()['result'],'installed')
 def test_destination_symlink_and_stage_substitution(self):
  self.home.mkdir(mode=0o700);(self.home/'images').symlink_to(self.root)
  with self.assertRaises(OSError):self.install()
  (self.home/'images').unlink()
  def swap(name):
   if name=='before-publication':
    p=next((self.home/'staging').iterdir());p.rename(p.with_name('retained'));p.symlink_to(self.root)
  with self.assertRaisesRegex(ValueError,'substituted'):self.install(_checkpoint=swap)
  self.assertFalse(self.target().exists())
 def test_no_network_shell_mount_or_qemu(self):
  real=subprocess.Popen;calls=[]
  def allowed(args,*a,**kw):
   self.assertEqual(args[0],'/usr/bin/gpgv');self.assertFalse(kw.get('shell',False));calls.append(args);return real(args,*a,**kw)
  with patch('subprocess.Popen',side_effect=allowed),patch('os.system',side_effect=AssertionError('shell')),patch('socket.socket',side_effect=AssertionError('network')):
   self.assertEqual(self.install()['result'],'installed')
  self.assertEqual(len(calls),1)
 def test_legacy_local_transaction_and_duplicate(self):
  raw=self.root/'local.raw';raw.write_bytes(b'local fixture');spec=copy.deepcopy(self.manifest['descriptor']);spec.update(bytes=raw.stat().st_size,sha256=hash_(raw.read_bytes()))
  with patch('learning_lab.vm_preview.policy.image_spec',return_value=spec):
   self.assertEqual(bundle.register_local_image(raw,self.home,_gate_root=self.gate),'installed')
   self.assertEqual(bundle.register_local_image(raw,self.home,_gate_root=self.gate),'already-installed')
  self.assertEqual(set((self.home/'images'/spec['sha256']).iterdir()),{self.home/'images'/spec['sha256']/n for n in ('base.raw','provenance.json')})

 def test_staged_payload_substitution_refused(self):
  def replace(name):
   if name=='prepared':
    stage=next((self.home/'staging').iterdir());p=stage/'base.raw';p.chmod(0o600);p.write_bytes(b'changed')
  with self.assertRaisesRegex(Refused,'changed after validation'):self.install(_checkpoint=replace)
  self.assertFalse(self.target().exists())
 def test_lifetime_lock_does_not_stop_or_block_independent_image_registration(self):
  # This fake gate represents an unrelated running VM; no QMP operation occurs.
  with Directory.absolute(self.gate,create=True) as gate:
   lock=gate.open('running.lock',True,True)
   import fcntl
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   try:
    with patch('learning_lab.vm_preview.process.Qmp',side_effect=AssertionError('guest control')):
     self.assertEqual(self.install()['result'],'installed')
   finally:os.close(lock)
 def test_concurrent_process_import_lock(self):
  with Directory.absolute(self.home,create=True) as root,bundle.import_lock(root):
   script="from learning_lab.vm_preview.files import Directory; from learning_lab.vm_preview.image_bundle import import_lock; import sys; d=Directory.absolute(sys.argv[1]); lock=import_lock(d); lock.__enter__()"
   result=subprocess.run([__import__('sys').executable,'-B','-c',script,str(self.home)],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('Another image import',result.stderr)
 def test_two_import_threads_publish_only_once(self):
  entered=threading.Event();release=threading.Event();results=[]
  def hook(name):
   if name=='prepared':entered.set();assert release.wait(5)
  def work():
   try:results.append(self.install(_checkpoint=hook))
   except BaseException as exc:results.append(exc)
  t=threading.Thread(target=work);t.start()
  try:
   self.assertTrue(entered.wait(5))
   with self.assertRaisesRegex(ValueError,'Another image import'):self.install()
  finally:release.set();t.join(5)
  self.assertEqual(results[0]['result'],'installed');self.assertEqual(self.install()['result'],'already-installed')
 def test_end_fsync_failure_has_complete_receipt_and_retry(self):
  original=os.fsync;armed=False
  def hook(name):
   nonlocal armed
   if name=='published':armed=True
  def fail(fd):
   if armed:raise OSError(errno.ENOSPC,'directory sync full')
   return original(fd)
  with patch.object(bundle.os,'fsync',side_effect=fail):
   with self.assertRaises(OSError):self.install(_checkpoint=hook)
  self.assertTrue((self.target()/'receipt.json').is_file());self.assertEqual(self.install()['result'],'already-installed')
 def test_registration_collision_at_commit_never_overwrites(self):
  def hook(name):
   if name=='before-publication':
    target=self.target();target.mkdir(mode=0o700);(target/'sentinel').write_bytes(b'preserve')
  with self.assertRaises(OSError):self.install(_checkpoint=hook)
  self.assertEqual((self.target()/'sentinel').read_bytes(),b'preserve')
 def test_zip64_directory_end_and_overlap(self):
  original=self.path.read_bytes();end=list(struct.unpack('<4s4H2IH',original[-22:]));at=len(original)-22
  z=struct.pack('<4sQ2H2I4Q',b'PK\x06\x06',44,45,45,0,0,6,6,end[5],end[6])
  loc=struct.pack('<4sIQI',b'PK\x06\x07',0,at,1)
  classic=struct.pack('<4s4H2IH',b'PK\x05\x06',0,0,65535,65535,0xffffffff,0xffffffff,0)
  self.path.write_bytes(original[:-22]+z+loc+classic)
  self.assertEqual(self.install()['result'],'installed')
  # Real member overlap is rejected before opening the archive reader.
  raw=bytearray(original);first=raw.index(b'PK\x01\x02');second=raw.index(b'PK\x01\x02',first+4);struct.pack_into('<I',raw,second+42,0);self.path.write_bytes(raw)
  with self.assertRaises(ValueError):self.install()

 def test_large_hashing_never_holds_vm_operation_lock(self):
  real=bundle.sha256
  def hash_outside_lock(fd):
   with bundle.publication_lock(self.gate):pass
   return real(fd)
  with patch.object(bundle,'sha256',side_effect=hash_outside_lock):
   self.assertEqual(self.install()['result'],'installed')
   self.assertEqual(self.install()['result'],'already-installed')
 def test_abrupt_process_exit_before_and_after_publication(self):
  import multiprocessing
  for point in ('prepared','published'):
   self.home=self.root/('process-crash-'+point)
   def child():
    self.install(_checkpoint=lambda name:os._exit(73) if name==point else None)
   process=multiprocessing.get_context('fork').Process(target=child);process.start();process.join(10)
   if process.is_alive():process.kill();process.join();self.fail('Crash fixture timed out')
   self.assertEqual(process.exitcode,73)
   self.assertEqual(self.target().exists(),point=='published')
   self.assertEqual(self.install()['result'],'already-installed' if point=='published' else 'installed')

class SignatureStatusTests(unittest.TestCase):
 def test_ambiguous_wrong_signer_bad_exit_expiry_and_digest(self):
  fp='A'*40;valid=f'[GNUPG:] NEWSIG\n[GNUPG:] GOODSIG {fp[-16:]} Test\n[GNUPG:] VALIDSIG {fp} 2026-01-01 1 0 4 0 22 8 00 {fp}\n'.encode()
  signature.check_status(0,valid,fp)
  for code,raw,signer in ((1,valid,fp),(0,valid+valid,fp),(0,valid,'B'*40),(0,valid+b'[GNUPG:] BADSIG bad\n',fp),(0,valid.replace(b'1 0 4',b'1 9 4'),fp),(0,valid.replace(b'22 8',b'22 2'),fp),(0,b'garbage',fp)):
   with self.assertRaises(ValueError):signature.check_status(code,raw,signer)
 def test_status_order_and_duplicate_id_rejected(self):
  fp='A'*40;n='[GNUPG:] NEWSIG\n';g=f'[GNUPG:] GOODSIG {fp[-16:]} Test\n';v=f'[GNUPG:] VALIDSIG {fp} 2026-01-01 1 0 4 0 22 8 00 {fp}\n';i='[GNUPG:] SIG_ID abc 2026-01-01 1\n'
  for raw in (n+v+g,g+n+v,n+i+i+g+v,n+g+v+i):
   with self.assertRaises(ValueError):signature.check_status(0,raw.encode(),fp)
 def test_optional_verifier_absent(self):
  with patch.object(signature.os,'access',return_value=False),self.assertRaisesRegex(Refused,'unavailable'):signature.verify(b'{}',b'sig',b'key','A'*40)

 def test_verifier_timeout_and_output_bound_real_children(self):
  with tempfile.TemporaryDirectory() as temp:
   script=Path(temp)/'verifier'
   for body,setting,message in (("import time; time.sleep(10)",{'TIMEOUT':.05},'timed out'),("import os; os.write(1,b'x'*70000)",{'OUTPUT_LIMIT':1000},'exceeds limit')):
    script.write_text('#!/usr/bin/python3\n'+body+'\n');script.chmod(0o700)
    with patch.object(signature,'VERIFIER',str(script)),patch.multiple(signature,**setting):
     with self.assertRaisesRegex(Refused,message):signature.verify(b'{}',b'sig',b'key','A'*40)
