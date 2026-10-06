"""Explicit guest-image routing, registry bounds and old-record preservation."""
import copy,hashlib,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from learning_lab.vm_preview import registry
from learning_lab.vm_preview.image_catalog import Catalog,production_catalog,digest,resource
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.policy import image_spec
from admin_guest_fixtures import COMMANDS
UNIT='linux-administration-services-logs-recovery'
OLD_IDS=[e['id'] for u in registry.units()[:2] for e in u['entries']]
class AdminProvenanceTests(unittest.TestCase):
 def setUp(self):
  self.docs=Path(__file__).resolve().parents[1]/'docs/vm-preview'
  self.p=json.loads((self.docs/'admin-finalized-provenance.json').read_text())
 def test_final_inventory_is_exact_superset_without_rewriting_history(self):
  early=(self.docs/'admin-packages.tsv').read_bytes();final=(self.docs/'admin-finalized-packages.tsv').read_bytes()
  self.assertEqual(hashlib.sha256(early).hexdigest(),'22c40a10a16f763fd74749bd36da66547f8619fd6970172cc25da474b43f462b')
  self.assertEqual(hashlib.sha256(final).hexdigest(),'2271bd8b719e7d51c40810d5f08f10ce9feb80ae1ae9d8962a08d68a52520cd8')
  before=set(early.decode().splitlines());after=set(final.decode().splitlines())
  self.assertEqual((len(before),len(after)),(204,216));self.assertLessEqual(before,after)
  self.assertEqual(after-before,{'\t'.join(p[k] for k in ('binary','version','source','source_version')) for p in self.p['additional_packages']})
  for name,count in [('historical_inventory',204),('finalized_inventory',216)]:
   rec=self.p[name];self.assertEqual(rec['binary_count'],count);self.assertEqual(hashlib.sha256((self.docs/rec['resource']).read_bytes()).hexdigest(),rec['sha256'])
 def test_supplement_does_not_change_exact_descriptor_or_pinned_resolution(self):
  spec=json.loads(resource('admin-image.json'));c=production_catalog()
  self.assertEqual(digest(spec),'dcbdec81fc5aab2b775168cde1a350364ec8e017e67d1c25e1035f74cc8fb25d')
  self.assertEqual(spec['sha256'],self.p['image_sha256']);self.assertEqual(digest(spec),self.p['legacy_descriptor_sha256'])
  self.assertEqual(spec['packages_sha256'],self.p['historical_inventory']['sha256']);self.assertNotEqual(spec['packages_sha256'],self.p['finalized_inventory']['sha256'])
  for id in COMMANDS:
   old,lesson=c.defaults(id);self.assertEqual(old,spec)
   pinned={'backend':'offline-qemu-preview-1','image':old,'lesson_sha256':digest(lesson)}
   self.assertEqual(c.resolve(pinned,id)[0]['descriptor'],spec)
   altered=copy.deepcopy(pinned);altered['image']['packages_sha256']=self.p['finalized_inventory']['sha256']
   with self.assertRaisesRegex(ValueError,'descriptor unavailable'):c.resolve(altered,id)
  self.assertFalse(c.keys or c.releases)
 def test_additional_source_and_notice_mapping(self):
  p=self.p;self.assertEqual((p['source_version_count'],p['source_file_count'],p['additional_source_version_count']),(204,635,10))
  sources={(s['source'],s['version']) for s in p['additional_sources']}
  self.assertEqual(len(sources),10);self.assertEqual(sum(len(s['files']) for s in p['additional_sources']),32)
  self.assertEqual(sum(f['bytes'] for s in p['additional_sources'] for f in s['files']),p['additional_source_bytes'])
  for b in p['additional_packages']:
   self.assertFalse(b['built_using'] or b['static_built_using'])
   self.assertTrue((b['source'],b['source_version']) in sources or (b['source'],b['source_version'])==('gcc-14','14.2.0-19'))
   self.assertRegex(b['notice_sha256'],r'^[a-f0-9]{64}$');self.assertRegex(b['binary_sha256'],r'^[a-f0-9]{64}$')
  atomic=next(b for b in p['additional_packages'] if b['binary']=='libatomic1:amd64')
  self.assertEqual(atomic['notice_member'],'usr/share/doc/gcc-14-base/copyright')
  microcode=next(b for b in p['additional_packages'] if b['binary']=='intel-microcode')
  self.assertEqual(microcode['notice_sha256'],p['intel_microcode']['notice_sha256'])
  self.assertTrue(p['unresolved']);self.assertEqual(len(p['material_manifest']['sha256']),64)
class AdminCatalogTests(unittest.TestCase):
 def setUp(self):self.data=json.loads(resource('image-catalog.json'))
 def test_exact_explicit_routes_and_no_production_admission(self):
  c=production_catalog();self.assertEqual((len(c.images),len(c.lessons)),(4,68));self.assertFalse(c.keys or c.releases)
  for id in OLD_IDS:self.assertEqual(c.defaults(id)[0],image_spec())
  for id in COMMANDS:
   spec,lesson=c.defaults(id);self.assertEqual(spec['image_id'],'debian13-admin-local-v1');self.assertNotEqual(spec,image_spec());self.assertEqual(lesson['id'],id);self.assertEqual(spec,json.loads(resource('admin-image.json')))
   with self.assertRaisesRegex(ValueError,'combination'):c.resolve({'backend':'offline-qemu-preview-1','image':image_spec(),'lesson_sha256':digest(lesson)},id)
 def test_missing_map_entry_and_null_never_fall_back(self):
  for value in (None,{},[],{k:v for k,v in self.data['default_images'].items() if k!=next(iter(COMMANDS))}):
   d=copy.deepcopy(self.data);d['default_images']=value
   with self.assertRaisesRegex(ValueError,'Incomplete'):Catalog(d)
 def test_bad_mapping_identity_and_incompatible_privileged_substitution(self):
  for target in ('0'*64,[],digest(Catalog(self.data).defaults(next(iter(COMMANDS)))[0])):
   d=copy.deepcopy(self.data);d['default_images'][registry.LEGACY_ID]=target
   with self.assertRaises(ValueError):Catalog(d)
 def test_external_mapping_mutation_cannot_change_catalog(self):
  c=Catalog(self.data);self.data['default_images'][registry.LEGACY_ID]='0'*64
  self.assertEqual(c.defaults(registry.LEGACY_ID)[0],image_spec())
 def test_unavailable_exact_image_refuses_no_substitute(self):
  c=production_catalog();id=next(iter(COMMANDS));spec,_=c.defaults(id);c.images.pop(digest(spec))
  with self.assertRaisesRegex(ValueError,'no substitute'):c.defaults(id)
  self.assertEqual(c.defaults(registry.LEGACY_ID)[0],image_spec())
 def test_legacy_catalog_without_mapping_retains_old_semantics(self):
  d=copy.deepcopy(self.data);d.pop('default_images');d['images']=d['images'][:1];d['lessons']=[l for l in d['lessons'] if l['id'] in OLD_IDS];d['default_lessons']={k:v for k,v in d['default_lessons'].items() if k in OLD_IDS}
  d['images'][0]['lessons']=[x for x in d['images'][0]['lessons'] if x['id'] in OLD_IDS]
  c=Catalog(d)
  for id in OLD_IDS:self.assertEqual(c.defaults(id)[0],image_spec())
  self.assertEqual(digest(d),'76879cfcf51769fc451ee7f48105071bc29c2058c6cc393237d2106559dbe205')
 def test_old_pair_cannot_boot_privileged_image(self):
  c=production_catalog();admin=c.defaults(next(iter(COMMANDS)))[0]
  for id in OLD_IDS:
   with self.assertRaisesRegex(ValueError,'combination'):c.resolve({'backend':'offline-qemu-preview-1','image':admin,'lesson_sha256':digest(c.defaults(id)[1])},id)
 def test_both_modes_and_old_saved_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);s=Sessions(root/'vm','a'*64,root/'gate');fake=root/'fixture';fake.write_bytes(b'fixture')
   def reset(m,mode):
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda r:os.open(fake,os.O_RDONLY)):return m.reset(mode,True)
   originals={}
   for id in OLD_IDS:
    m=s.manager(id);reset(m,'Learn');m.progress('next');m.progress('complete');p=root/'vm/profiles'/m.profile/'current.json';originals[p]=p.read_bytes()
   for id in COMMANDS:
    m=s.manager(id);first=reset(m,'Learn');m.progress('hint');m.progress('complete');before=m.status()['session'];self.assertEqual(Sessions(root/'vm','a'*64,root/'gate').manager(id).status()['session'],before)
    disk=root/'vm/profiles'/m.profile/'generations'/first['generation']/'disk.qcow2';raw=disk.read_bytes();reset(m,'Challenge');self.assertIsNone(m.status()['session']['completion']);self.assertEqual(disk.read_bytes(),raw)
    with self.assertRaises(ValueError):m.progress('hint')
    m.progress('complete');self.assertNotIn('score',m.status()['session'])
   for p,raw in originals.items():self.assertEqual(p.read_bytes(),raw)
class AdminRegistryTests(unittest.TestCase):
 def fixture(self,change,valid=False):
  original=registry._read;reads=[]
  def read(name):
   reads.append(name)
   if name=='fourth-unit.json':v=copy.deepcopy(original('admin-unit.json'));v.update(id='fourth-unit',entries=v['entries'][4:]);return v
   v=original(name);change(name,v);return v
  registry._bundle.cache_clear()
  try:
   with patch.object(registry,'_read',side_effect=read):
    if valid:self.assertEqual(len(registry.entries()),24)
    else:
     with self.assertRaises(ValueError):registry.units()
  finally:registry._bundle.cache_clear()
  return reads
 def test_68_lessons_and_eight_units_are_valid(self):
  self.assertEqual((registry.MAX_UNITS,registry.MAX_LESSONS_PER_UNIT,registry.MAX_TOTAL_LESSONS),(8,16,68));self.assertEqual(len(registry.entries()),68);self.assertEqual([len(u['entries']) for u in registry.units()],[8,8,8,12,8,8,8,8])
 def test_four_units_can_fit_total_bound(self):
  def change(n,v):
   if n=='units.json':v['units']=v['units'][:3]+[{'id':'fourth-unit','resource':'fourth-unit.json'}]
   if n=='admin-unit.json':v['entries']=v['entries'][:4]
  self.fixture(change,True)
 def test_sixth_unit_empty_index_and_wrong_version_rejected(self):
  self.fixture(lambda n,v:v['units'].extend(v['units'][:2]) if n=='units.json' else None)
  self.fixture(lambda n,v:v.update(units=[]) if n=='units.json' else None)
  self.fixture(lambda n,v:v.update(schema_version=True) if n=='units.json' else None)
 def test_17_per_unit_and_cross_unit_duplicate_rejected(self):
  self.fixture(lambda n,v:v['entries'].extend(copy.deepcopy(v['entries'])+copy.deepcopy(v['entries'][:1])) if n=='admin-unit.json' else None)
  reads=self.fixture(lambda n,v:v['entries'].append(copy.deepcopy(v['entries'][0])) if n=='admin-unit.json' else None)
  self.assertNotIn('real-linux-bash-files.json',reads)
 def test_empty_unit_and_support_limits_rejected(self):
  self.fixture(lambda n,v:v.update(entries=[]) if n=='admin-unit.json' else None)
  self.fixture(lambda n,v:v['entries'][0].update(materials=['x']*17) if n=='admin-unit.json' else None)
  self.fixture(lambda n,v:v['entries'][0].update(materials=['x'*4097]) if n=='admin-unit.json' else None)
 def test_sixteen_entries_in_one_unit_are_supported(self):
  other=registry.catalog('lpic-resource-diagnosis-capacity')['entries']
  def change(n,v):
   if n=='units.json':v['units']=[v['units'][0],v['units'][2]]
   if n=='unit.json':v['entries'].extend(copy.deepcopy(other))
  self.fixture(change,True)
 def test_display_only_lessons_and_static_fixture_parity(self):
  self.assertEqual(list(COMMANDS),[e['id'] for e in registry.catalog(UNIT)['entries']])
  for id,commands in COMMANDS.items():
   lesson=registry.load_lesson(id);self.assertEqual(commands,[s['command'] for s in lesson['steps']]);self.assertTrue(all(c.isascii() for c in commands));self.assertIn('self-review',lesson['coverage']);self.assertIn('No score',lesson['coverage'])
   self.assertLessEqual(len((registry.ROOT/(id+'.json')).read_bytes()),65536)
  self.fixture(lambda n,v:v['entries'][0].update(execute='sudo id') if n=='admin-unit.json' else None)
 def test_legacy_lesson_files_unchanged(self):
  for name,h in json.loads(PROTECTED_JSON).items():self.assertEqual(hashlib.sha256((registry.ROOT/name).read_bytes()).hexdigest(),h,name)
PROTECTED_JSON = '{"unit.json": "6de3c33587271f923ae230a99d9fbec013a005fb818fde07533ab3fe781b7ad1", "resource-unit.json": "e6d3c0e6e8d6e47fccfe383a02f455b14f60168b3971ec88d426afe3ee2c9879", "image.json": "1499ad6e7f5cced795f5f0ff97348fbaa321a60aba3c8a810f074a846410a417", "lesson.json": "246f12b80f72fff3fae2a6484de185706c90dedf6ecd68f92417aea2ff6881da", "manager.py": "10c9c248ef11bbb221c37054a47c4096b569ceff0fe9231cdf24d0fbe02fe236", "policy.py": "0fc31036904c975950ed5902a910cfe2a3a02a8aa60e421aa460cdcbcc104031", "files.py": "548868ac623bb1a4796884a140c959fa2b2d5bbb539f3fa16d642c93b5f361c0", "runner.py": "dfc173564c073c0ac0d80c6a717a0b7a203d53194c466122a391ba932a2b5c48", "process.py": "b01bcf16fa10daa001f75c04e6054fcda610eb59db8c3737506e12bc2f9ba4c6", "catalog_manager.py": "8de739b4dfaebffb74aa5671a5be878b2fb9365984e208d20dd65ba536cd1aa2", "image_bundle.py": "7699e9544080028448a7742d212c267a93a82e4f82d239885e5876869067a470", "bundle_archive.py": "e474cbbc8ba9a3638b8fc9baee92faeb64f5566bc3ac399ee03718c2d5e629cd", "bundle_signature.py": "48c73f464e1a8c9259bf2f81042f089e13c10d0b346bfd5f586b0af3bf210068", "real-linux-process-inspection.json": "b954c498e5b3cb415d5e04091c7886c08cb632e3dc960e785362020d91e9feed", "real-linux-foreground-jobs.json": "d5b4794811e15969a8d0b81a82581648d72fcc0389e5fe2add0783f6b0217ee2", "real-linux-targeted-signals.json": "3be3c2d2f4fab885c7ca1d8eafe6833b2bc7c6fac58912dbde5a7de31c8cd2aa", "real-linux-live-monitoring.json": "24b4d79d57e31835559bde8a8212b6135df3311a17c48d7b616a2c1414ed40c2", "real-linux-logout-persistence.json": "7f5a32defd10c1a645b832df6359f53951e4ce8ca9ab23ca6b653f0559555d0d", "real-linux-process-priorities.json": "f81821b9d040be954a406f8c168e064a8d258504c9f13af9c4eb4bfd66f57fed", "real-linux-process-handover.json": "eab59839bc70e8c4acb05e184d5d11531f94b3fc524ee234eb61d3f36f29f32c", "real-linux-capacity-baseline.json": "89b3d63e1576524a31fcdbd70551c2fdb6137000c7a1a6b71172485066fdc4f1", "real-linux-capacity-cpu.json": "dfe1958e0d51f4c14393527e276f337d46516d8d4e00fbada1f71e8b17111bae", "real-linux-capacity-memory.json": "3c760586d55a1442bff0ec010576e653ba43c926ace2daad32c127cc671b9368", "real-linux-capacity-io.json": "f26c8148b9dacb9b5c4fb65b7130a569e43b8fc3eb2b7c4a54a72b3b604c653c", "real-linux-capacity-space-inodes.json": "506eb05d32b549e8da04870b54a98f77ba7902d87844c417567a7e9bc65cf2f7", "real-linux-capacity-trends.json": "e12aabc6ea190d3a435f619b228c01c3c2a61705e425f87145a697ded6781692", "real-linux-capacity-forecast.json": "c5c1ae68c7477b16380be8e41c6d84510e75ddaa6c2d6233c13f3ff0aa672c6f", "real-linux-capacity-recommendation.json": "31c38667c6bf87958b2dc9861876ad87e79fdd8444e68abd9e3b52a83608de32"}'
