"""Trusted Bash unit bounds, explicit image routing and pinned-record preservation."""
import copy,hashlib,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from learning_lab.vm_preview import registry
from learning_lab.vm_preview.image_catalog import production_catalog,digest,resource
from learning_lab.vm_preview.policy import image_spec
from learning_lab.vm_preview.sessions import Sessions
from bash_guest_fixtures import COMMANDS,SCRIPT_ROWS,UNIT
class BashUnitTests(unittest.TestCase):
 def test_exact_bounds_and_all_76_lessons(self):
  self.assertEqual((registry.MAX_UNITS,registry.MAX_LESSONS_PER_UNIT,registry.MAX_TOTAL_LESSONS),(9,16,76))
  self.assertEqual([len(u['entries']) for u in registry.units()],[8,8,8,12,8,8,8,8,8]);self.assertEqual(len(registry.entries()),76)
 def test_reject_77_before_reading_eighth_unit_lessons(self):
  original=registry._read;reads=[]
  def read(name):
   reads.append(name);d=original(name)
   if name=='storage-unit.json':d['entries'].append(copy.deepcopy(d['entries'][0]))
   return d
  registry._bundle.cache_clear()
  try:
   with patch.object(registry,'_read',side_effect=read):
    with self.assertRaisesRegex(ValueError,'76'):registry.units()
   self.assertNotIn('real-linux-storage-identify.json',reads)
  finally:registry._bundle.cache_clear()
 def test_reject_tenth_unit_before_resources(self):
  original=registry._read;reads=[]
  def read(name):
   reads.append(name);d=original(name)
   if name=='units.json':d['units'].append({'id':'sixth','resource':'sixth.json'})
   return d
  registry._bundle.cache_clear()
  try:
   with patch.object(registry,'_read',side_effect=read):
    with self.assertRaisesRegex(ValueError,'unit'):registry.units()
   self.assertEqual(reads,['units.json'])
  finally:registry._bundle.cache_clear()
 def test_existing_controller_images_and_24_lessons_exact_bytes(self):
  for name,h in PROTECTED.items():self.assertEqual(hashlib.sha256((registry.ROOT/name).read_bytes()).hexdigest(),h,name)
 def test_exact_old_catalog_projection(self):
  c=json.loads(resource('image-catalog.json'));c['images']=[i for i in c['images'] if i['descriptor']['image_id']!='debian13-package-admin-local-v1'];new=set(COMMANDS)|{e['id'] for e in registry.catalog('linux-users-groups-access')['entries']}|{e['id'] for e in registry.catalog('linux-scheduling-automation')['entries']}
  new |= {e['id'] for e in registry.catalog('linux-backup-safe-recovery')['entries']}
  new |= {e['id'] for e in registry.catalog('linux-system-discovery-package-fundamentals')['entries']}
  new |= {e['id'] for e in registry.catalog('linux-storage-filesystems-mounts-safe-maintenance')['entries']}
  c['lessons']=[l for l in c['lessons'] if l['id'] not in new]
  for i in c['images']:i['lessons']=[l for l in i['lessons'] if l['id'] not in new]
  for name in ('default_images','default_lessons'):c[name]={k:v for k,v in c[name].items() if k not in new}
  self.assertEqual(digest(c),OLD_CATALOG_DIGEST)
 def test_new_routes_explicit_unprivileged_no_fallback(self):
  c=production_catalog();self.assertFalse(c.keys or c.releases)
  admin=c.defaults('real-linux-admin-change')[0]
  for id in COMMANDS:
   image,l=c.defaults(id);self.assertEqual(image,image_spec());self.assertEqual(l,registry.load_lesson(id))
   with self.assertRaises(ValueError):c.resolve({'backend':'offline-qemu-preview-1','image':admin,'lesson_sha256':digest(l)},id)
  c.images.pop(digest(image_spec()))
  for id in COMMANDS:
   with self.assertRaisesRegex(ValueError,'no substitute'):c.defaults(id)
 def test_both_modes_retained_reset_and_same_profile_restart(self):
  # Isolated metadata fixture: native tests separately verify actual QEMU disks.
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);s=Sessions(r/'vm','a'*64,r/'gate');base=r/'fake';base.write_bytes(b'fixture')
   def reset(m,mode):
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda root:os.open(base,os.O_RDONLY)):return m.reset(mode,True)
   old={}
   for e in registry.entries()[:24]:
    m=s.manager(e['id']);reset(m,'Learn');m.progress('next');m.progress('complete');p=r/'vm/profiles'/m.profile/'current.json';old[p]=p.read_bytes()
   for id in COMMANDS:
    m=s.manager(id);learn=reset(m,'Learn');m.progress('next');m.progress('hint');m.progress('complete');saved=m.status()['session']
    self.assertEqual(saved['completion']['kind'],'self-reviewed');self.assertNotIn('score',saved)
    self.assertEqual(Sessions(r/'vm','a'*64,r/'gate').manager(id).status()['session'],saved)
    disk=r/'vm/profiles'/m.profile/'generations'/learn['generation']/'disk.qcow2';before=disk.read_bytes();challenge=reset(m,'Challenge')
    self.assertNotEqual(challenge['generation'],learn['generation']);self.assertEqual(challenge['pin'],learn['pin']);self.assertEqual(disk.read_bytes(),before)
    self.assertIsNone(m.status()['session']['completion'])
    with self.assertRaises(ValueError):m.progress('hint')
    m.progress('complete');self.assertEqual(m.status()['session']['mode'],'Challenge')
   for p,b in old.items():self.assertEqual(p.read_bytes(),b)
 def test_display_only_content_static_fixture_parity_and_limits(self):
  u=registry.catalog(UNIT);self.assertEqual([e['id'] for e in u['entries']],list(COMMANDS))
  for e in u['entries']:
   l=registry.load_lesson(e['id']);self.assertEqual([s['command'] for s in l['steps']],COMMANDS[e['id']]);self.assertIn('self-review',l['coverage']);self.assertNotIn('score',l)
   for k in ('materials','observations','questions','limitations','cleanup'):self.assertTrue(e[k])
   self.assertLessEqual(len((registry.ROOT/e['resource']).read_bytes()),65536)
   self.assertTrue(all(c.isascii() for c in COMMANDS[e['id']]))
  self.assertEqual(registry.load_lesson('real-linux-bash-guards')['goal'],'Guard script inputs and report failures predictably before declaring success.')
  self.assertNotIn('set -e', '\n'.join(SCRIPT_ROWS['guards']))

PROTECTED = {'__init__.py': '1e2f17daefc011e021e1c5eb273f11eddce55c305b2a79fa2a376837c59ffeb9', 'admin-image.json': '6adaf2d5d4b885221e190fcefc7cfeb25bc3901dc7b645721e237ae785ce85fd', 'admin-unit.json': '7e0a1f116d25d261946f381bdf86f06c1adb99cf33f48b2af202690c9467eb55', 'bridge.py': '9a92918586de3d06a7a938ffe6c768579d8f0d33471f585520deee2cff5ee80d', 'bundle_archive.py': 'e474cbbc8ba9a3638b8fc9baee92faeb64f5566bc3ac399ee03718c2d5e629cd', 'bundle_signature.py': '48c73f464e1a8c9259bf2f81042f089e13c10d0b346bfd5f586b0af3bf210068', 'catalog_manager.py': '8de739b4dfaebffb74aa5671a5be878b2fb9365984e208d20dd65ba536cd1aa2', 'files.py': '548868ac623bb1a4796884a140c959fa2b2d5bbb539f3fa16d642c93b5f361c0', 'image.json': '1499ad6e7f5cced795f5f0ff97348fbaa321a60aba3c8a810f074a846410a417', 'image_bundle.py': '7699e9544080028448a7742d212c267a93a82e4f82d239885e5876869067a470', 'image_catalog.py': '3f72b04b3ea97c4d96b1049d3ba4960ed1d9218e6967777a0cd0e045f278f46a', 'lesson.json': '246f12b80f72fff3fae2a6484de185706c90dedf6ecd68f92417aea2ff6881da', 'manager.py': '10c9c248ef11bbb221c37054a47c4096b569ceff0fe9231cdf24d0fbe02fe236', 'policy.py': '0fc31036904c975950ed5902a910cfe2a3a02a8aa60e421aa460cdcbcc104031', 'process.py': 'b01bcf16fa10daa001f75c04e6054fcda610eb59db8c3737506e12bc2f9ba4c6', 'real-linux-admin-access.json': '028a9c82e801a7fc75a3d4d54009a09feb3bb5eb2d85aefdc0242054498ccd17', 'real-linux-admin-boot.json': '6c0b4f2900ff942121c11324c0f50a85350b451a3f0e6a7b554add8af886e8bc', 'real-linux-admin-change.json': '02277b4f40be2eec8a77832ce8e89e7663a09f06a3189b3e0146263b43ad9062', 'real-linux-admin-incident.json': '2b20aa5b0e9a54669a6edeb86211b2929ef263b5c773ac24c507e151cc0aee43', 'real-linux-admin-lifecycle.json': 'e70399c1cac835825e09d502e840861ff62ba2cd2f3d025bc7ff7b58c24c307a', 'real-linux-admin-logs.json': '2ce60f3d5868d6f82af76f49a7212d7819a2c729c749e40811ae65844686a87b', 'real-linux-admin-override.json': 'deb90abd551eaa539a4d9d9e02f5e88f2d0558c8b788094aa35df9d5f1729a52', 'real-linux-admin-rotation.json': '5596a103d689a84de21136dbfdf849d01cac810e49f9f2ff5dd48019ace572cb', 'real-linux-capacity-baseline.json': '89b3d63e1576524a31fcdbd70551c2fdb6137000c7a1a6b71172485066fdc4f1', 'real-linux-capacity-cpu.json': 'dfe1958e0d51f4c14393527e276f337d46516d8d4e00fbada1f71e8b17111bae', 'real-linux-capacity-forecast.json': 'c5c1ae68c7477b16380be8e41c6d84510e75ddaa6c2d6233c13f3ff0aa672c6f', 'real-linux-capacity-io.json': 'f26c8148b9dacb9b5c4fb65b7130a569e43b8fc3eb2b7c4a54a72b3b604c653c', 'real-linux-capacity-memory.json': '3c760586d55a1442bff0ec010576e653ba43c926ace2daad32c127cc671b9368', 'real-linux-capacity-recommendation.json': '31c38667c6bf87958b2dc9861876ad87e79fdd8444e68abd9e3b52a83608de32', 'real-linux-capacity-space-inodes.json': '506eb05d32b549e8da04870b54a98f77ba7902d87844c417567a7e9bc65cf2f7', 'real-linux-capacity-trends.json': 'e12aabc6ea190d3a435f619b228c01c3c2a61705e425f87145a697ded6781692', 'real-linux-foreground-jobs.json': 'd5b4794811e15969a8d0b81a82581648d72fcc0389e5fe2add0783f6b0217ee2', 'real-linux-live-monitoring.json': '24b4d79d57e31835559bde8a8212b6135df3311a17c48d7b616a2c1414ed40c2', 'real-linux-logout-persistence.json': '7f5a32defd10c1a645b832df6359f53951e4ce8ca9ab23ca6b653f0559555d0d', 'real-linux-process-handover.json': 'eab59839bc70e8c4acb05e184d5d11531f94b3fc524ee234eb61d3f36f29f32c', 'real-linux-process-inspection.json': 'b954c498e5b3cb415d5e04091c7886c08cb632e3dc960e785362020d91e9feed', 'real-linux-process-priorities.json': 'f81821b9d040be954a406f8c168e064a8d258504c9f13af9c4eb4bfd66f57fed', 'real-linux-targeted-signals.json': '3be3c2d2f4fab885c7ca1d8eafe6833b2bc7c6fac58912dbde5a7de31c8cd2aa', 'resource-unit.json': 'e6d3c0e6e8d6e47fccfe383a02f455b14f60168b3971ec88d426afe3ee2c9879', 'runner.py': 'dfc173564c073c0ac0d80c6a717a0b7a203d53194c466122a391ba932a2b5c48', 'sessions.py': '5879078e3b4221ee4fcf95a9ae8cd59b03b2d6a84945bc8be6655c1d53a3166a', 'unit.json': '6de3c33587271f923ae230a99d9fbec013a005fb818fde07533ab3fe781b7ad1'}
OLD_CATALOG_DIGEST = '485e67a9001875a3bac942ecf9b362472f153881c717f22af6cbeb50d16c539c'
