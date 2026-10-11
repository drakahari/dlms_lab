"""Bounded trusted registry, independent arithmetic and isolated session fixtures."""
import copy, hashlib, json, os, tempfile, unittest
from fractions import Fraction
from pathlib import Path
from local_shell_preservation import projection
from unittest.mock import patch
from learning_lab.vm_preview import registry
from learning_lab.vm_preview.registry import units, entries, catalog, load_lesson, session_binding, LEGACY_ID
from learning_lab.vm_preview.image_catalog import production_catalog, digest
from learning_lab.vm_preview.sessions import Sessions
from capacity_guest_fixtures import COMMANDS
PROTECTED = {'unit.json': '6de3c33587271f923ae230a99d9fbec013a005fb818fde07533ab3fe781b7ad1', 'lesson.json': '246f12b80f72fff3fae2a6484de185706c90dedf6ecd68f92417aea2ff6881da', 'image.json': '1499ad6e7f5cced795f5f0ff97348fbaa321a60aba3c8a810f074a846410a417', 'manager.py': '10c9c248ef11bbb221c37054a47c4096b569ceff0fe9231cdf24d0fbe02fe236', 'policy.py': '0fc31036904c975950ed5902a910cfe2a3a02a8aa60e421aa460cdcbcc104031', 'process.py': 'b01bcf16fa10daa001f75c04e6054fcda610eb59db8c3737506e12bc2f9ba4c6', 'runner.py': 'dfc173564c073c0ac0d80c6a717a0b7a203d53194c466122a391ba932a2b5c48', 'files.py': '548868ac623bb1a4796884a140c959fa2b2d5bbb539f3fa16d642c93b5f361c0', 'catalog_manager.py': '8de739b4dfaebffb74aa5671a5be878b2fb9365984e208d20dd65ba536cd1aa2', 'image_catalog.py': '3f72b04b3ea97c4d96b1049d3ba4960ed1d9218e6967777a0cd0e045f278f46a', 'bundle_archive.py': 'e474cbbc8ba9a3638b8fc9baee92faeb64f5566bc3ac399ee03718c2d5e629cd', 'bundle_signature.py': '48c73f464e1a8c9259bf2f81042f089e13c10d0b346bfd5f586b0af3bf210068', 'image_bundle.py': '7699e9544080028448a7742d212c267a93a82e4f82d239885e5876869067a470', 'real-linux-process-inspection.json': 'b954c498e5b3cb415d5e04091c7886c08cb632e3dc960e785362020d91e9feed', 'real-linux-foreground-jobs.json': 'd5b4794811e15969a8d0b81a82581648d72fcc0389e5fe2add0783f6b0217ee2', 'real-linux-targeted-signals.json': '3be3c2d2f4fab885c7ca1d8eafe6833b2bc7c6fac58912dbde5a7de31c8cd2aa', 'real-linux-live-monitoring.json': '24b4d79d57e31835559bde8a8212b6135df3311a17c48d7b616a2c1414ed40c2', 'real-linux-logout-persistence.json': '7f5a32defd10c1a645b832df6359f53951e4ce8ca9ab23ca6b653f0559555d0d', 'real-linux-process-priorities.json': 'f81821b9d040be954a406f8c168e064a8d258504c9f13af9c4eb4bfd66f57fed', 'real-linux-process-handover.json': 'eab59839bc70e8c4acb05e184d5d11531f94b3fc524ee234eb61d3f36f29f32c'}
UNIT = 'lpic-resource-diagnosis-capacity'

class CapacityRegistryTests(unittest.TestCase):
 def malformed(self, change):
  original=registry._read
  def read(name):
   value=original(name);change(name,value);return value
  registry._bundle.cache_clear()
  try:
   with patch.object(registry,'_read',side_effect=read),self.assertRaises((ValueError,TypeError)):units()
  finally:registry._bundle.cache_clear()
 def test_exact_legacy_bytes_and_controller_unchanged(self):
  for name,h in PROTECTED.items():self.assertEqual(hashlib.sha256(projection(name,(registry.ROOT/name).read_bytes())).hexdigest(),h,name)
 def test_order_bounds_and_global_identity(self):
  self.assertEqual([u['id'] for u in units()[:2]],[registry.LEGACY_UNIT,UNIT])
  self.assertEqual([len(u['entries']) for u in units()[:2]],[8,8])
  self.assertEqual(len(entries()),86);self.assertEqual(len({e['id'] for e in entries()}),86)
  self.assertEqual((registry.MAX_UNITS,registry.MAX_LESSONS_PER_UNIT,registry.MAX_TOTAL_LESSONS),(10,16,86))
  self.assertEqual(list(COMMANDS),[e['id'] for e in catalog(UNIT)['entries']])
 def test_unit_count_version_duplicates_and_paths_rejected(self):
  self.malformed(lambda n,v:v.update(schema_version=2) if n=='units.json' else None)
  self.malformed(lambda n,v:v['units'].extend(v['units']*3) if n=='units.json' else None)
  self.malformed(lambda n,v:v['units'].append(v['units'][0]) if n=='units.json' else None)
  self.malformed(lambda n,v:v['units'][1].update(resource='../image.json') if n=='units.json' else None)
  self.malformed(lambda n,v:v['units'][1].update(resource=['bad']) if n=='units.json' else None)
 def test_cross_unit_duplicate_and_total_limit_fail_before_lesson_reads(self):
  self.malformed(lambda n,v:v['entries'][0].update(id=LEGACY_ID) if n=='resource-unit.json' else None)
  self.malformed(lambda n,v:v['entries'].extend(copy.deepcopy(v['entries'])+copy.deepcopy(v['entries'][:1])) if n=='resource-unit.json' else None)
  self.malformed(lambda n,v:v['entries'].extend(v['entries']*2) if n=='resource-unit.json' else None)
 def test_support_fields_cannot_execute_or_exceed_bounds(self):
  self.malformed(lambda n,v:v['entries'][0].update(script='id') if n=='resource-unit.json' else None)
  self.malformed(lambda n,v:v['entries'][0].update(materials=['x'*4097]) if n=='resource-unit.json' else None)
  self.malformed(lambda n,v:v['entries'][0].update(questions=['q']*17) if n=='resource-unit.json' else None)
 def test_no_external_registry_or_host_execution_on_content_read(self):
  with patch('subprocess.Popen',side_effect=AssertionError('host execution')),patch('socket.socket',side_effect=AssertionError('network')):
   for e in catalog(UNIT)['entries']:
    self.assertTrue(load_lesson(e['id'])['challenge'])
   for bad in ('../outside','https://example.org/units.json',None):
    with self.assertRaises(ValueError):registry._read(bad)
 def test_all_new_pairs_exact_and_production_trust_empty(self):
  c=production_catalog();self.assertEqual(c.keys,{});self.assertEqual(c.releases,{})
  self.assertEqual(len(c.lessons),86);self.assertEqual(len(c.images),4)
  for e in entries():
   spec,l=c.defaults(e['id']);self.assertEqual(l,load_lesson(e['id']))
   self.assertEqual(digest(l),c._data['default_lessons'][e['id']])
   self.assertEqual(spec,json.loads((registry.ROOT/('package-image.json' if e['id'].startswith('real-linux-discovery-') else 'admin-image.json' if e['id'].startswith(('real-linux-admin-','real-linux-users-','real-linux-schedule-','real-linux-backup-','real-linux-discovery-','real-linux-storage-','real-linux-local-sticky','real-linux-local-priority')) else 'image.json')).read_text()))
 def test_original_catalog_projection_exact(self):
  # Remove only the authorized new lesson entries. Every remaining descriptor,
  # availability state, compatibility pair, default, key and release is exact.
  c=json.loads((registry.ROOT/'image-catalog.json').read_text())
  c['images']=[i for i in c['images'] if i['descriptor']['image_id']!='debian13-package-admin-local-v1']
  new={e['id'] for e in entries() if e['id'].startswith(('real-linux-capacity-','real-linux-admin-','real-linux-bash-','real-linux-users-','real-linux-schedule-','real-linux-backup-','real-linux-discovery-','real-linux-storage-','real-linux-local-'))}
  c.pop('default_images',None);c['images']=c['images'][:1]
  c['lessons']=[x for x in c['lessons'] if x['id'] not in new]
  for image in c['images']:image['lessons']=[x for x in image['lessons'] if x['id'] not in new]
  for name in ('default_lessons',):
   c[name]={k:v for k,v in c[name].items() if k not in new}
  self.assertEqual(digest(c),'4b51ab22989965c2363859f8961faa03bd644b9a07a270da5e7e31a02f2e0928')
 def test_guidance_matches_static_developer_fixtures_and_is_ascii(self):
  for e in catalog(UNIT)['entries']:
   l=load_lesson(e['id']);self.assertEqual([s['command'] for s in l['steps']],COMMANDS[e['id']])
   self.assertTrue(all(c.isascii() for c in COMMANDS[e['id']]))
   for k in ('materials','observations','questions','limitations','cleanup','troubleshooting'):self.assertTrue(e[k])
   for k in ('challenge','hints','review','coverage'):self.assertTrue(l[k])
   self.assertIn('self-review',l['coverage']);self.assertNotIn('score',l.keys())
 def test_datasets_are_available_without_guided_solutions(self):
  for e in catalog(UNIT)['entries']:
   source=' '.join(e['materials']);l=load_lesson(e['id'])
   for c in COMMANDS[e['id']]:
    if c.startswith("printf '%s\\n'") and any(n in c for n in ('history.txt','memory-example.txt','shortages.txt','irregular.txt')):self.assertIn(c,source)
   self.assertNotIn('49 days', ' '.join(l['review']))
 def test_forecast_independent_exact_arithmetic_and_chart(self):
  samples=[(0,200),(7,270),(14,340),(21,410)]
  rates=[Fraction(b[1]-a[1],b[0]-a[0]) for a,b in zip(samples,samples[1:])]
  self.assertEqual(rates,[10,10,10]);headroom=1000-100-samples[-1][1]
  self.assertEqual(headroom,490);days=Fraction(headroom,rates[-1]);self.assertEqual(days,49)
  self.assertEqual(samples[-1][0]+days,70);self.assertEqual(Fraction(1000-410,10)+21,80)
  self.assertEqual([used//50 for day,used in samples],[4,5,6,8])
  self.assertGreater(540672-16384,0);self.assertEqual(540672-16384,512*1024)
 def test_irregular_data_not_a_reliable_positive_growth_model(self):
  values=[200,190,300,210];changes=[b-a for a,b in zip(values,values[1:])]
  self.assertEqual(changes,[-10,110,-90]);self.assertGreater(Fraction(values[-1]-values[0],21),0)
  self.assertFalse(all(x>0 for x in changes));self.assertEqual(len(set(changes)),3)

@unittest.skipUnless(Path('/usr/bin/qemu-img').exists(),'Optional tooling absent')
class CapacitySessionTests(unittest.TestCase):
 def test_both_modes_hints_reset_restart_and_old_record_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);s=Sessions(root/'vm','a'*64,root/'gate');fake=root/'fixture';fake.write_bytes(b'fixture')
   def reset(m,mode):
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda r:os.open(fake,os.O_RDONLY)):return m.reset(mode,True)
   legacy=s.manager(LEGACY_ID);reset(legacy,'Learn');legacy.progress('next');legacy.progress('hint');legacy.progress('complete')
   old=root/'vm/profiles'/legacy.profile/'current.json';original=old.read_bytes()
   for e in catalog(UNIT)['entries']:
    m=s.manager(e['id']);first=reset(m,'Learn');m.progress('hint');m.progress('next');m.progress('complete')
    s.select(e['id']);reopened=Sessions(root/'vm','a'*64,root/'gate')
    self.assertEqual(reopened.selected(),e['id']);self.assertEqual(reopened.manager(e['id']).status()['session'],m.status()['session'])
    disk=root/'vm/profiles'/m.profile/'generations'/first['generation']/'disk.qcow2';before=disk.read_bytes()
    new=reset(m,'Challenge');self.assertIsNone(new['completion']);self.assertEqual(new['hints'],0)
    with self.assertRaises(ValueError):m.progress('hint')
    m.progress('complete');self.assertEqual(disk.read_bytes(),before)
    self.assertEqual(m.status()['session']['completion']['kind'],'self-reviewed')
    self.assertEqual(old.read_bytes(),original)
 def test_cross_unit_running_controls_and_exclusion(self):
  with tempfile.TemporaryDirectory() as td:
   s=Sessions(Path(td)/'vm','a'*64,Path(td)/'gate');a=s.manager(LEGACY_ID);id=catalog(UNIT)['entries'][0]['id'];b=s.manager(id)
   r={'state':'running','store':a.binding,'profile':a.profile}
   with patch.object(b,'reconcile',return_value=r),patch.object(a,'status',return_value={'state':'running','session':None}),patch.object(b,'status',return_value={'state':'stopped','session':None}),patch.object(s,'require_record'):
    self.assertEqual(s.view(id)['running_lesson_id'],LEGACY_ID);self.assertIs(s.running_manager(id),a)
   with a.access() as (_,g,p):fd=a.gate(g)
   try:
    with self.assertRaisesRegex(ValueError,'already running'):b.start()
    with self.assertRaisesRegex(ValueError,'already running'):b.reset(confirmed=True)
   finally:os.close(fd)
