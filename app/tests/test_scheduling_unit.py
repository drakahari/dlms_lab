from foundation_preservation import NEW_IDS
"""Bounded scheduling unit, exact administrator routes and legacy compatibility.
Metadata mocks here are not substitutes for the separate real guest access proof.
"""
import copy,hashlib,json,os,subprocess,tempfile,unittest
from pathlib import Path
from local_shell_preservation import projection
from unittest.mock import patch
from learning_lab.vm_preview import registry
from learning_lab.vm_preview.image_catalog import production_catalog,Catalog,digest,resource
from learning_lab.vm_preview.sessions import Sessions
from scheduling_guest_fixtures import COMMANDS,UNIT

class SchedulingUnitTests(unittest.TestCase):
 def test_exact_limits_nine_units_and_76_lessons(self):
  self.assertEqual((registry.MAX_UNITS,registry.MAX_LESSONS_PER_UNIT,registry.MAX_TOTAL_LESSONS),(12,16,102))
  self.assertEqual([len(u['entries']) for u in registry.units()],[8,8,8,12,8,8,8,8,8,10,8,8])
  self.assertEqual(len(registry.entries()),102)
  self.assertEqual([e['id'] for e in registry.catalog(UNIT)['entries']],list(COMMANDS))
 def malformed(self,mutate,pattern):
  original=registry._read;reads=[]
  def read(name):
   reads.append(name);v=original(name);mutate(name,v);return v
  registry._bundle.cache_clear()
  try:
   with patch.object(registry,'_read',side_effect=read),self.assertRaisesRegex(ValueError,pattern):registry.units()
  finally:registry._bundle.cache_clear()
  return reads
 def test_reject_77_before_last_unit_lesson_read(self):
  reads=self.malformed(lambda n,v:v['entries'].append(copy.deepcopy(v['entries'][0])) if n=='operations-unit.json' else None,'102')
  self.assertNotIn('real-linux-operations-accountfiles.json',reads)
 def test_reject_tenth_unit_before_resource_reads(self):
  reads=self.malformed(lambda n,v:v['units'].append({'id':'seventh','resource':'seventh.json'}) if n=='units.json' else None,'1–12')
  self.assertEqual(reads,['units.json'])
 def test_reject_17_per_unit_and_oversized_guidance(self):
  self.malformed(lambda n,v:v['entries'].extend(v['entries']+[v['entries'][0]]) if n=='scheduling-unit.json' else None,'1–16')
  self.malformed(lambda n,v:v['entries'][0].update(materials=['x'*4097]) if n=='scheduling-unit.json' else None,'materials')
 def test_sixteen_per_unit_remains_accepted(self):
  original=registry._read
  # Use another eight unique accepted lesson identities as static entries.
  other=registry.catalog('linux-administration-services-logs-recovery')['entries']
  def read(n):
   v=original(n)
   if n=='units.json':v['units']=v['units'][:1]+[next(x for x in v['units'] if x['resource']=='scheduling-unit.json')]
   if n=='scheduling-unit.json':v['entries'].extend(copy.deepcopy(other))
   return v
  registry._bundle.cache_clear()
  try:
   with patch.object(registry,'_read',side_effect=read):self.assertEqual([len(u['entries']) for u in registry.units()],[8,16])
  finally:registry._bundle.cache_clear()
 def test_original_44_lesson_controller_image_bytes(self):
  for name,h in PROTECTED.items():self.assertEqual(hashlib.sha256(projection(name,(registry.ROOT/name).read_bytes())).hexdigest(),h,name)
 def test_exact_catalog_projection(self):
  c=json.loads(resource('image-catalog.json'));c['images']=[i for i in c['images'] if i['descriptor']['image_id']!='debian13-package-admin-local-v1'];new=set(COMMANDS)
  new |= {e['id'] for e in registry.catalog('linux-backup-safe-recovery')['entries']}
  new |= {e['id'] for e in registry.catalog('linux-system-discovery-package-fundamentals')['entries']}
  new |= {e['id'] for e in registry.catalog('linux-storage-filesystems-mounts-safe-maintenance')['entries']}
  new |= {e['id'] for e in registry.catalog('lpic-local-shell-filesystem')['entries']}
  new |= NEW_IDS
  c['lessons']=[l for l in c['lessons'] if l['id'] not in new]
  for i in c['images']:i['lessons']=[l for l in i['lessons'] if l['id'] not in new]
  for name in ('default_lessons','default_images'):c[name]={k:v for k,v in c[name].items() if k not in new}
  self.assertEqual(digest(c),BASELINE_CATALOG)
 def test_new_routes_exact_admin_without_fallback(self):
  c=production_catalog();admin=json.loads(resource('admin-image.json'));plain=json.loads(resource('image.json'))
  self.assertFalse(c.keys or c.releases)
  for id in COMMANDS:
   spec,l=c.defaults(id);self.assertEqual(spec,admin);self.assertEqual(l,registry.load_lesson(id))
   with self.assertRaisesRegex(ValueError,'combination'):c.resolve({'backend':'offline-qemu-preview-1','image':plain,'lesson_sha256':digest(l)},id)
  c.images.pop(digest(admin))
  for id in COMMANDS:
   with self.assertRaisesRegex(ValueError,'no substitute'):c.defaults(id)
 def test_unavailable_withdrawn_missing_and_mismatched_content_refused(self):
  # Existing test_image_catalog exercises every route's Stop ownership and
  # missing/forged pins. This tests authorization without substituting images.
  for id in COMMANDS:
   for state in ('resume-only','withdrawn'):
    c=production_catalog();spec,l=c.defaults(id);c.images[digest(spec)]['state']=state
    with self.assertRaisesRegex(ValueError,state):c.allow({'backend':'offline-qemu-preview-1','image':spec,'lesson_sha256':digest(l)},id,'new')
   c=production_catalog();c.lessons[(id,c._data['default_lessons'][id])][0]['state']='withdrawn'
   spec,l=c.defaults(id)
   with self.assertRaisesRegex(ValueError,'withdrawn'):c.allow({'backend':'offline-qemu-preview-1','image':spec,'lesson_sha256':digest(l)},id,'resume')
 def test_static_fixture_parity_display_only_and_limits(self):
  with patch('subprocess.Popen',side_effect=AssertionError('host execution')),patch('socket.socket',side_effect=AssertionError('network')):
   for e in registry.catalog(UNIT)['entries']:
    l=registry.load_lesson(e['id']);self.assertEqual([s['command'] for s in l['steps']],COMMANDS[e['id']])
    self.assertIn('self-review',l['coverage']);self.assertNotIn('score',l)
    for key in ('cleanup','materials','observations','questions','limitations','troubleshooting'):self.assertTrue(e[key])
    self.assertLessEqual(len((registry.ROOT/e['resource']).read_bytes()),65536)
    self.assertTrue(all(c.isascii() for c in COMMANDS[e['id']]))
    for repair in ('sudo chmod','sudo chown','sudo sed','systemd-run'):
     self.assertNotIn(repair,l['challenge'])
 def test_challenge_fault_setup_matches_real_guest_static_fixtures(self):
  unit=registry.catalog(UNIT)
  for index,count in ((3,4),(7,3)):
   entry=unit['entries'][index]
   self.assertEqual(entry['materials'][-1].split('\n',1)[1], '\n'.join(COMMANDS[entry['id']][:count]))
 def test_crontab_collision_guards_use_guest_root_visibility(self):
  # The real guest proves mode1730 root:crontab blocks learner's lookup.
  # An unprivileged ! -e cannot establish absence inside that spool.
  for slug,n in (('cron',3),('diagnose',4),('assessment',8)):
   commands=COMMANDS['real-linux-schedule-'+slug]
   guarded=[c for c in commands if '/var/spool/cron/crontabs/' in c]
   self.assertEqual(len(guarded),1)
   self.assertTrue(guarded[0].startswith('sudo test ! -e /var/spool/cron/crontabs/ll-s'+str(n)+' && '))
 def test_tool_check_and_explicit_user_service_types(self):
  self.assertNotIn('--no-pager',COMMANDS['real-linux-schedule-inspect'][2])
  lesson=registry.load_lesson('real-linux-schedule-monotonic')
  for index in (2,4):self.assertIn('--property=Type=exec',lesson['steps'][index]['command'])
  self.assertIn('otherwise defaults to Type=simple',lesson['hints'][2])
 def test_gnu_directory_setgid_fault_fixture_is_explicit(self):
  # Static developer reference only: owned temporary fixture, no learner input.
  with tempfile.TemporaryDirectory() as td:
   directory=Path(td)/'shared';directory.mkdir();directory.chmod(0o2770)
   subprocess.run(['/usr/bin/chmod','0770',str(directory)],check=True)
   self.assertEqual(directory.stat().st_mode & 0o7777,0o2770)
   subprocess.run(['/usr/bin/chmod','g-s',str(directory)],check=True)
   self.assertEqual(directory.stat().st_mode & 0o7777,0o770)
 def test_both_modes_restart_reset_and_older_saved_record_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);s=Sessions(root/'vm','a'*64,root/'gate');base=root/'fake';base.write_bytes(b'metadata fixture only')
   def reset(m,mode):
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda r:os.open(base,os.O_RDONLY)):return m.reset(mode,True)
   old={}
   for e in registry.entries()[:44]:
    m=s.manager(e['id']);reset(m,'Learn');m.progress('next');m.progress('complete');p=root/'vm/profiles'/m.profile/'current.json';old[p]=p.read_bytes()
   for id in COMMANDS:
    m=s.manager(id);first=reset(m,'Learn');m.progress('next');m.progress('hint');m.progress('complete');record=m.status()['session']
    self.assertEqual(record['completion']['kind'],'self-reviewed');self.assertNotIn('score',record)
    self.assertEqual(Sessions(root/'vm','a'*64,root/'gate').manager(id).status()['session'],record)
    disk=root/'vm/profiles'/m.profile/'generations'/first['generation']/'disk.qcow2';before=disk.read_bytes();second=reset(m,'Challenge')
    self.assertEqual(first['pin'],second['pin']);self.assertNotEqual(first['generation'],second['generation']);self.assertEqual(disk.read_bytes(),before)
    for op in ('hint','next'):
     with self.assertRaises(ValueError):m.progress(op)
    m.progress('complete');self.assertEqual(m.status()['session']['mode'],'Challenge')
   for p,raw in old.items():self.assertEqual(p.read_bytes(),raw)

PROTECTED = {'__init__.py': '1e2f17daefc011e021e1c5eb273f11eddce55c305b2a79fa2a376837c59ffeb9', 'admin-image.json': '6adaf2d5d4b885221e190fcefc7cfeb25bc3901dc7b645721e237ae785ce85fd', 'admin-unit.json': '7e0a1f116d25d261946f381bdf86f06c1adb99cf33f48b2af202690c9467eb55', 'bash-unit.json': '539a468b60d73529a0ac97dde1694ee0ba5523f9dae1ec98daacfe553636a9f2', 'bridge.py': '825f3c42660f084f993a7be62e24a5a0844bd36eadcd63261aa762d6da24b73f', 'bundle_archive.py': 'e474cbbc8ba9a3638b8fc9baee92faeb64f5566bc3ac399ee03718c2d5e629cd', 'bundle_signature.py': '48c73f464e1a8c9259bf2f81042f089e13c10d0b346bfd5f586b0af3bf210068', 'catalog_manager.py': '8de739b4dfaebffb74aa5671a5be878b2fb9365984e208d20dd65ba536cd1aa2', 'files.py': '548868ac623bb1a4796884a140c959fa2b2d5bbb539f3fa16d642c93b5f361c0', 'image.json': '1499ad6e7f5cced795f5f0ff97348fbaa321a60aba3c8a810f074a846410a417', 'image_bundle.py': '7699e9544080028448a7742d212c267a93a82e4f82d239885e5876869067a470', 'image_catalog.py': '3f72b04b3ea97c4d96b1049d3ba4960ed1d9218e6967777a0cd0e045f278f46a', 'lesson.json': '246f12b80f72fff3fae2a6484de185706c90dedf6ecd68f92417aea2ff6881da', 'manager.py': '10c9c248ef11bbb221c37054a47c4096b569ceff0fe9231cdf24d0fbe02fe236', 'policy.py': '0fc31036904c975950ed5902a910cfe2a3a02a8aa60e421aa460cdcbcc104031', 'process.py': 'b01bcf16fa10daa001f75c04e6054fcda610eb59db8c3737506e12bc2f9ba4c6', 'real-linux-admin-access.json': '028a9c82e801a7fc75a3d4d54009a09feb3bb5eb2d85aefdc0242054498ccd17', 'real-linux-admin-boot.json': '6c0b4f2900ff942121c11324c0f50a85350b451a3f0e6a7b554add8af886e8bc', 'real-linux-admin-change.json': '02277b4f40be2eec8a77832ce8e89e7663a09f06a3189b3e0146263b43ad9062', 'real-linux-admin-incident.json': '2b20aa5b0e9a54669a6edeb86211b2929ef263b5c773ac24c507e151cc0aee43', 'real-linux-admin-lifecycle.json': 'e70399c1cac835825e09d502e840861ff62ba2cd2f3d025bc7ff7b58c24c307a', 'real-linux-admin-logs.json': '2ce60f3d5868d6f82af76f49a7212d7819a2c729c749e40811ae65844686a87b', 'real-linux-admin-override.json': 'deb90abd551eaa539a4d9d9e02f5e88f2d0558c8b788094aa35df9d5f1729a52', 'real-linux-admin-rotation.json': '5596a103d689a84de21136dbfdf849d01cac810e49f9f2ff5dd48019ace572cb', 'real-linux-bash-environment.json': '975a5dade292d60e621884f1d318cdd208df23fcc42bf4a13c6035c5ff27608e', 'real-linux-bash-files.json': '748d64684a4f0d92b8288cb2c556d1a61e2fe43105a98e130e236dc50832616e', 'real-linux-bash-guards.json': 'b8e0ed564b7450a51ebc8d3131a8441ef384cec989a65f34ed70b24b4b637fb7', 'real-linux-bash-handover.json': '157a824a4bd4c8ea33fded7244aaa8c63d777b20d95cf19c57953cad3d5055dc', 'real-linux-bash-quoting.json': 'ba60b71dfa3cec7b046489ed1d042b40cf1a9afb38d1146bf35e651c87837e55', 'real-linux-bash-records.json': '039584858810c38050db7fa3d3bfd6893d63005132bd055aae95a1a01e4860e6', 'real-linux-bash-regex.json': 'd1924bf55ffeb5f8e431be670c8e46553375f3d589f5c8cbf840d0ff76278686', 'real-linux-bash-rollback.json': '15f6bffe41ce2cf7daf6fd41c4a819cce395ae314f793495275ca95f2dd74186', 'real-linux-bash-script.json': '85b409f617b1f00da955d8cf48d5280db7b9d94432a3385b059fffc5cb16678c', 'real-linux-bash-streams.json': '78f2185a3776bab0c596820c79e9bb9cb72e8e65b49ceda704698bcc1c5f1162', 'real-linux-bash-transform.json': 'e4574f9c4bacd9f5a09158e3ec96ef347880ca76d1bcfdb560eef63b2cb0651d', 'real-linux-bash-vi.json': '9fac14c98be2390d884565f55a47715c5591a771fcc5c9a73d175783056e0a30', 'real-linux-capacity-baseline.json': '89b3d63e1576524a31fcdbd70551c2fdb6137000c7a1a6b71172485066fdc4f1', 'real-linux-capacity-cpu.json': 'dfe1958e0d51f4c14393527e276f337d46516d8d4e00fbada1f71e8b17111bae', 'real-linux-capacity-forecast.json': 'c5c1ae68c7477b16380be8e41c6d84510e75ddaa6c2d6233c13f3ff0aa672c6f', 'real-linux-capacity-io.json': 'f26c8148b9dacb9b5c4fb65b7130a569e43b8fc3eb2b7c4a54a72b3b604c653c', 'real-linux-capacity-memory.json': '3c760586d55a1442bff0ec010576e653ba43c926ace2daad32c127cc671b9368', 'real-linux-capacity-recommendation.json': '31c38667c6bf87958b2dc9861876ad87e79fdd8444e68abd9e3b52a83608de32', 'real-linux-capacity-space-inodes.json': '506eb05d32b549e8da04870b54a98f77ba7902d87844c417567a7e9bc65cf2f7', 'real-linux-capacity-trends.json': 'e12aabc6ea190d3a435f619b228c01c3c2a61705e425f87145a697ded6781692', 'real-linux-foreground-jobs.json': 'd5b4794811e15969a8d0b81a82581648d72fcc0389e5fe2add0783f6b0217ee2', 'real-linux-live-monitoring.json': '24b4d79d57e31835559bde8a8212b6135df3311a17c48d7b616a2c1414ed40c2', 'real-linux-logout-persistence.json': '7f5a32defd10c1a645b832df6359f53951e4ce8ca9ab23ca6b653f0559555d0d', 'real-linux-process-handover.json': 'eab59839bc70e8c4acb05e184d5d11531f94b3fc524ee234eb61d3f36f29f32c', 'real-linux-process-inspection.json': 'b954c498e5b3cb415d5e04091c7886c08cb632e3dc960e785362020d91e9feed', 'real-linux-process-priorities.json': 'f81821b9d040be954a406f8c168e064a8d258504c9f13af9c4eb4bfd66f57fed', 'real-linux-targeted-signals.json': '3be3c2d2f4fab885c7ca1d8eafe6833b2bc7c6fac58912dbde5a7de31c8cd2aa', 'real-linux-users-create.json': 'f8942ff0a9448dbae3427ca06279a88c3d4a67ca1b47c928121c0056e48cd762', 'real-linux-users-inspect.json': '2b0c7436de62339f24115699021e8a440db33b73f6bae022d1a133536c8b848f', 'real-linux-users-membership.json': 'a758c3af430648dd34f408597a13f647300b27d3013dbe61291e699dbe6476e4', 'real-linux-users-ownership.json': '7691c75e514ebe770db9b3b22b77eca59d57e97070e6883acf268d45b07c6bd9', 'real-linux-users-repair.json': '6e10129ca23817f7838f4a43a88e7a7284ab0cbd95fb8287b45fdbcdf5e44150', 'real-linux-users-restrictions.json': '8b41049e01b20f7a9c59b8b42181a13264c967ba6719db0c1470b4724e51c824', 'real-linux-users-shared.json': '8c89fa669d205e81bc5422e1c3087e9f1b9f2c4e161a02b8269356bbc78f534c', 'real-linux-users-umask.json': 'cd96c6b08a4cf6a940132382173739e3b8fed8f5764046f534156f0451027dd9', 'resource-unit.json': 'e6d3c0e6e8d6e47fccfe383a02f455b14f60168b3971ec88d426afe3ee2c9879', 'runner.py': 'dfc173564c073c0ac0d80c6a717a0b7a203d53194c466122a391ba932a2b5c48', 'sessions.py': '5879078e3b4221ee4fcf95a9ae8cd59b03b2d6a84945bc8be6655c1d53a3166a', 'unit.json': '6de3c33587271f923ae230a99d9fbec013a005fb818fde07533ab3fe781b7ad1', 'users-unit.json': 'da69c8ae6980682d6fdda1f92f2c553a953c5931781b28191a90efbdbdd43519'}
BASELINE_CATALOG = '1d54ca2e32cf77b72dd7758cd9cf2de4176d6ebf729af5f56858917c0c9d9c04'
