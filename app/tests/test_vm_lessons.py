"""Trusted content and selection fixtures. All mutation uses temporary VM stores."""
import hashlib,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from learning_lab.vm_preview import registry
from learning_lab.vm_preview.registry import LEGACY_ID,catalog,load_lesson,session_binding
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.manager import Manager
from learning_lab.vm_preview.files import Refused

class RegistryTests(unittest.TestCase):
 def test_order_and_original_bytes_and_pin(self):
  ids=[e['id'] for e in catalog()['entries']]
  self.assertEqual(len(ids),8);self.assertEqual(ids[2],LEGACY_ID)
  raw=Path(registry.ROOT/'lesson.json').read_bytes()
  self.assertEqual(hashlib.sha256(raw).hexdigest(),'246f12b80f72fff3fae2a6484de185706c90dedf6ecd68f92417aea2ff6881da')
  a=Manager('/tmp/not-created','a'*64);b=Manager('/tmp/not-created','a'*64,lesson_id=LEGACY_ID)
  self.assertEqual(a.lesson,b.lesson);self.assertEqual(a.pin,b.pin)
  self.assertEqual(b.pin['lesson_sha256'],'cc71a87e9cc21224b84803a4175dffdfd83da793700402e20ffe3515eeb59180')
 def test_bindings_stable_distinct_legacy_unchanged(self):
  keys=[session_binding('a'*64,e['id']) for e in catalog()['entries']]
  self.assertEqual(keys[2],'a'*64);self.assertEqual(len(set(keys)),8)
  self.assertEqual(keys,[session_binding('a'*64,e['id']) for e in catalog()['entries']])
  self.assertNotEqual(keys[0],session_binding('b'*64,catalog()['entries'][0]['id']))
 def test_unknown_ids_no_paths_or_execution(self):
  with patch('subprocess.Popen',side_effect=AssertionError('Host execution')):
   for id in ('../lesson.json','$(touch /tmp/host)',LEGACY_ID+';id',None):
    with self.assertRaises(ValueError):load_lesson(id)
    with self.assertRaises(ValueError):session_binding('a'*64,id)
 def test_returned_content_cannot_mutate_registry_or_pins(self):
  lesson=load_lesson();lesson['steps'].clear();c=catalog();c['entries'].clear()
  self.assertEqual(len(load_lesson()['steps']),6);self.assertEqual(len(catalog()['entries']),8)
 def malformed(self,mutate):
  source=registry._read
  def read(name):
   value=source(name);mutate(name,value);return value
  registry._bundle.cache_clear()
  try:
   with patch.object(registry,'_read',side_effect=read),self.assertRaises((ValueError,TypeError)):catalog()
  finally:registry._bundle.cache_clear()
 def test_duplicate_identity_rejected(self):
  self.malformed(lambda name,v:v['entries'].append(v['entries'][0]) if name=='unit.json' else None)
 def test_unsupported_registry_version(self):
  self.malformed(lambda name,v:v.update(schema_version=2) if name=='unit.json' else None)
 def test_resource_path_rejected(self):
  self.malformed(lambda name,v:v['entries'][0].update(resource='../image.json') if name=='unit.json' else None)
 def test_executable_fields_rejected(self):
  self.malformed(lambda name,v:v.update(script='id') if name=='lesson.json' else None)
 def test_steps_and_text_bounded(self):
  self.malformed(lambda name,v:v.update(steps=v['steps']*32) if name=='lesson.json' else None)
  self.malformed(lambda name,v:v.update(goal='x'*4097) if name=='lesson.json' else None)
 def test_security_controller_and_image_unchanged(self):
  # policy.py has the reviewed display-only revision; test_vm_display verifies
  # exact legacy/new argv and isolation. Lifecycle method hashes remain frozen.
  import ast
  root=registry.ROOT
  expected={'policy.py':'0fc31036904c975950ed5902a910cfe2a3a02a8aa60e421aa460cdcbcc104031',
            'files.py':'8e8ab7789daf65be7d5374b4548c452b1faebc813673ca8da390201e88112594',
            'process.py':'b01bcf16fa10daa001f75c04e6054fcda610eb59db8c3737506e12bc2f9ba4c6',
            'runner.py':'dfc173564c073c0ac0d80c6a717a0b7a203d53194c466122a391ba932a2b5c48',
            'image.json':'1499ad6e7f5cced795f5f0ff97348fbaa321a60aba3c8a810f074a846410a417'}
  for name,digest in expected.items():self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),digest)
  tree=ast.parse((root/'manager.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Manager')
  # Approved catalog hooks only; the remaining lifecycle/security AST must still
  # match the accepted controller. Stop, QMP and process operations are untouched.
  hooks=[]
  class StripCatalogHooks(ast.NodeTransformer):
   def visit_Expr(self,node):
    if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='_authorize':
     hooks.append(ast.unparse(node));return None
    return self.generic_visit(node)
  cls=StripCatalogHooks().visit(cls)
  self.assertEqual(hooks,["self._authorize('new', None)","self._authorize('reset', old)","self._authorize('resume' if s else 'new', s)"])
  methods='\n'.join(ast.dump(n,include_attributes=False) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name not in ('__init__','_authorize'))
  self.assertEqual(hashlib.sha256(methods.encode()).hexdigest(),'8be8f31148f2cfd0020a86cdd19b3c40645093f48345342f05062715fc69e9bf')
 def test_help_and_coverage_honest(self):
  text=json.dumps(catalog())+' '.join(json.dumps(load_lesson(e['id'])) for e in catalog()['entries'])
  for word in ('self-review','103.5','103.6','huponexit','Permission denied','normally 0','Resume','screen/tmux'):
   self.assertIn(word,text)
  for e in catalog()['entries']:
   l=load_lesson(e['id']);self.assertTrue(l['challenge']);self.assertTrue(l['review'])
   self.assertTrue(e['cleanup']);self.assertTrue(e['troubleshooting'])

@unittest.skipUnless(Path('/usr/bin/qemu-img').exists(),'Optional QEMU tooling absent')
class SelectionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.sessions=Sessions(self.root/'vm','a'*64,self.root/'gate');self.ids=[e['id'] for e in catalog()['entries']]
  self.fake=self.root/'fake';self.fake.write_bytes(b'fixture');self.patches=[]
 def tearDown(self):
  for p in self.patches:p.stop()
  self.temp.cleanup()
 def prepared(self,id,mode='Learn'):
  m=self.sessions.manager(id)
  for p in (patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda root:os.open(self.fake,os.O_RDONLY))):p.start();self.patches.append(p)
  return m,m.reset(mode,True)
 def test_lazy_default_without_storage(self):
  self.assertEqual(self.sessions.selected(),LEGACY_ID);self.assertFalse((self.root/'vm').exists())
 def test_selection_restart_preserves_all_records(self):
  legacy,s=self.prepared(LEGACY_ID);legacy.progress('hint');legacy.progress('complete')
  path=self.root/'vm/profiles'/('a'*64)/'current.json';before=path.read_bytes()
  self.sessions.select(self.ids[0]);m,new=self.prepared(self.ids[0],'Challenge')
  m.progress('complete');self.sessions.select(LEGACY_ID)
  self.assertEqual(path.read_bytes(),before)
  self.assertEqual(self.sessions.view(LEGACY_ID)['session']['mode'],'Learn')
  self.assertEqual(self.sessions.view(self.ids[0])['session']['mode'],'Challenge')
  reopened=Sessions(self.root/'vm','a'*64,self.root/'gate');self.assertEqual(reopened.selected(),LEGACY_ID)
  self.assertEqual(reopened.manager(self.ids[0]).status()['session'],m.status()['session'])
 def test_modes_and_hints_lesson_scoped(self):
  a,first=self.prepared(self.ids[0]);b,second=self.prepared(self.ids[1],'Challenge')
  a.progress('hint');a.progress('next');a.progress('complete')
  self.assertEqual(b.status()['session'],second)
  with self.assertRaises(Refused):b.progress('hint')
  old=self.root/'vm/profiles'/a.profile/'generations'/first['generation']/'disk.qcow2';raw=old.read_bytes()
  a.reset('Challenge',True);self.assertEqual(old.read_bytes(),raw);self.assertEqual(b.status()['session'],second)
 def test_missing_session_record_not_fresh_start(self):
  m,s=self.prepared(self.ids[0]);p=self.root/'vm/profiles'/m.profile
  (p/'current.json').rename(p/'retained-current.json')
  self.assertEqual(self.sessions.view(self.ids[0])['state'],'session-unavailable')
  with self.assertRaisesRegex(Refused,'record is missing'):self.sessions.require_record(m)
  old=p/'generations'/s['generation']/'disk.qcow2';raw=old.read_bytes()
  new=m.reset(confirmed=True);self.assertNotEqual(new['generation'],s['generation']);self.assertEqual(old.read_bytes(),raw)
 def test_corrupt_record_not_replaced(self):
  m,s=self.prepared(self.ids[0]);p=self.root/'vm/profiles'/m.profile/'current.json';p.write_bytes(b'{broken')
  self.assertEqual(self.sessions.view(self.ids[0])['state'],'session-unavailable')
  with self.assertRaises(ValueError):m.reset(confirmed=True)
  self.assertEqual(p.read_bytes(),b'{broken')
 def test_missing_disk_and_journal_still_block(self):
  m,s=self.prepared(self.ids[0]);p=self.root/'vm/profiles'/m.profile/'generations'/s['generation'];(p/'disk.qcow2').rename(p/'kept.qcow2')
  self.assertEqual(self.sessions.view(self.ids[0])['state'],'disk-missing')
  (p/'kept.qcow2').rename(p/'disk.qcow2');(p/'lifecycle.json').rename(p/'kept-journal.json')
  self.assertEqual(self.sessions.view(self.ids[0])['state'],'session-unavailable')
 def test_newer_selection_preserved(self):
  self.sessions.select(self.ids[0]);p=self.root/'vm/selections'/('a'*64+'.json');raw=b'{"schema_version":2,"lesson_id":"future"}';p.write_bytes(raw)
  with self.assertRaisesRegex(Refused,'Unsupported'):self.sessions.selected()
  with self.assertRaisesRegex(Refused,'Unsupported'):self.sessions.select(LEGACY_ID)
  self.assertEqual(p.read_bytes(),raw)
 def test_unknown_choice_does_not_create_store(self):
  with self.assertRaises(ValueError):self.sessions.select('../escape')
  self.assertFalse((self.root/'vm').exists())
 def test_symlink_choice_rejected_without_modifying_target(self):
  self.sessions.select(self.ids[0]);p=self.root/'vm/selections'/('a'*64+'.json');p.rename(p.with_name('retained.json'));p.symlink_to(self.fake)
  with self.assertRaises(OSError):self.sessions.select(LEGACY_ID)
  self.assertEqual(self.fake.read_bytes(),b'fixture')
 def test_live_global_lock_blocks_other_lessons_and_profiles(self):
  a,s=self.prepared(self.ids[0]);b,t=self.prepared(self.ids[1]);other=Sessions(self.root/'vm','b'*64,self.root/'gate')
  with a.access() as (_,g,p):fd=a.gate(g)
  try:
   for m in (b,other.manager(self.ids[0])):
    with self.assertRaisesRegex(Refused,'already running'):m.start()
    with self.assertRaisesRegex(Refused,'already running'):m.reset(confirmed=True)
  finally:os.close(fd)
 def test_running_selected_elsewhere_routes_stop_to_owner_only(self):
  a,s=self.prepared(self.ids[0]);b,t=self.prepared(self.ids[1])
  r={'state':'running','store':a.binding,'profile':a.profile}
  with patch.object(b,'reconcile',return_value=r),patch.object(a,'status',return_value={'state':'running','session':s}),patch.object(b,'status',return_value={'state':'stopped','session':t}),patch.object(a,'stop',return_value='Cleanly stopped') as stop:
   view=self.sessions.view(self.ids[1]);self.assertEqual(view['running_lesson_id'],self.ids[0])
   self.sessions.running_manager(self.ids[1]).stop();stop.assert_called_once()
   self.assertEqual(view['session']['session'],t['session'])
 def test_other_profile_not_adopted_for_controls(self):
  b,t=self.prepared(self.ids[1]);r={'state':'running','store':b.binding,'profile':'f'*64}
  with patch.object(b,'reconcile',return_value=r),patch.object(b,'status',return_value={'state':'stopped','session':t}):
   self.assertTrue(self.sessions.view(self.ids[1])['other_profile_running'])
   with self.assertRaisesRegex(Refused,'No verified'):self.sessions.running_manager(self.ids[1])
 def test_lost_running_progress_does_not_hide_stop(self):
  m,s=self.prepared(self.ids[0]);r={'state':'running','store':m.binding,'profile':m.profile}
  with patch.object(m,'reconcile',return_value=r),patch.object(m,'status',side_effect=Refused('missing journal')):
   view=self.sessions.view(self.ids[0]);self.assertEqual(view['running_lesson_id'],self.ids[0]);self.assertEqual(view['running_state'],'control-only')
   self.assertIs(self.sessions.running_manager(self.ids[0]),m)
 def test_lost_active_record_keeps_control_only(self):
  m,s=self.prepared(self.ids[0]);path=self.root/'vm/profiles'/m.profile/'current.json';path.rename(path.with_name('retained-current.json'))
  record={'state':'running','store':m.binding,'profile':m.profile}
  with patch.object(m,'reconcile',return_value=record):
   view=self.sessions.view(self.ids[0]);self.assertEqual(view['running_state'],'control-only');self.assertIn('record is missing',view['running_error'])
   self.assertIs(self.sessions.running_manager(self.ids[0]),m)
 def test_updated_pin_refused_without_migration(self):
  m,s=self.prepared(self.ids[0]);path=self.root/'vm/profiles'/m.profile/'current.json';before=path.read_bytes()
  # A revision absent from the trusted catalog must not be silently substituted.
  m.catalog.lessons.pop((m.lesson_id,m.pin['lesson_sha256']))
  self.assertEqual(self.sessions.view(self.ids[0])['state'],'session-unavailable');self.assertEqual(path.read_bytes(),before)
