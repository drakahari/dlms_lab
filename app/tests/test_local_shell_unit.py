from foundation_preservation import projection as foundation_projection,NEW_IDS
"""Metadata/bounds preservation. Real command safety has separate guest evidence."""
import copy,hashlib,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from learning_lab.vm_preview import registry
from learning_lab.vm_preview.image_catalog import Catalog,production_catalog,resource,digest,read_json
from learning_lab.vm_preview.sessions import Sessions
from local_shell_guest_fixtures import DATA,COMMANDS,UNIT
BASE=json.loads(Path(__file__).with_name('local_shell_baseline.json').read_text())
class LocalShellTests(unittest.TestCase):
 def tearDown(self):registry._bundle.cache_clear()
 def test_exact_bounds_and_parser_capacity(self):
  self.assertEqual((registry.MAX_UNITS,registry.MAX_TOTAL_LESSONS,registry.MAX_LESSONS_PER_UNIT),(11,94,16))
  self.assertEqual([len(u['entries']) for u in registry.units()],[8,8,8,12,8,8,8,8,8,10,8])
  self.assertEqual(len(registry.entries()),94)
  c=production_catalog();self.assertEqual((len(c.lessons),len(c._data['default_lessons']),len(c.default_images)),(94,94,94))
  self.assertFalse(c.keys or c.releases)
  for name in ('image-catalog.json','local-shell-unit.json'):self.assertLessEqual(len(resource(name)),65536);read_json(resource(name))
 def changed(self,change,pattern):
  original=registry._read
  def read(name):
   value=copy.deepcopy(original(name));change(name,value);return value
  registry._bundle.cache_clear()
  with patch.object(registry,'_read',side_effect=read),self.assertRaisesRegex(ValueError,pattern):registry.units()
 def test_87th_lesson_rejected(self):
  self.changed(lambda n,v:v['entries'].append(copy.deepcopy(v['entries'][0])) if n=='text-archive-unit.json' else None,'94')
 def test_eleventh_unit_rejected(self):
  self.changed(lambda n,v:v['units'].append(copy.deepcopy(v['units'][0])) if n=='units.json' else None,'1–11')
 def test_seventeenth_per_unit_rejected(self):
  self.changed(lambda n,v:v['entries'].extend([copy.deepcopy(v['entries'][0])]*7) if n=='local-shell-unit.json' else None,'1–16')
 def test_exact_sixteenth_per_unit_acceptance(self):
  original=registry._read;first=copy.deepcopy(original('unit.json'));last=copy.deepcopy(original('local-shell-unit.json'))
  last['entries']+=first['entries'][2:];first['entries']=first['entries'][:2]
  registry._bundle.cache_clear()
  with patch.object(registry,'_read',side_effect=lambda n:copy.deepcopy(first if n=='unit.json' else last if n=='local-shell-unit.json' else original(n))):self.assertEqual(len(registry.entries()),94)
 def test_catalog_retained_and_default_overflow(self):
  original=json.loads(resource('image-catalog.json'))
  bad=copy.deepcopy(original);bad['lessons'].append(copy.deepcopy(bad['lessons'][0]))
  with self.assertRaisesRegex(ValueError,'count'):Catalog(bad)
  for field in ('default_lessons','default_images'):
   bad=copy.deepcopy(original);bad[field]['new']='0'*64
   with self.assertRaises(ValueError):Catalog(bad)
  for field in ('images','keys','releases'):
   bad=copy.deepcopy(original);bad[field]=[{}]*65
   with self.assertRaises(ValueError):Catalog(bad)
  bad=copy.deepcopy(original);bad['images'][0]['lessons']=[bad['images'][0]['lessons'][0]]*65
  with self.assertRaisesRegex(ValueError,'compatibility'):Catalog(bad)
 def test_original_application_bytes(self):
  for name,h in BASE['protected'].items():
   raw=foundation_projection(name,(registry.ROOT.parents[1]/name).read_bytes())
   if name=='learning_lab/qml/Main.qml':raw=raw.replace(b'ten units / 86 lessons',b'nine units / 76 lessons')
   self.assertEqual(hashlib.sha256(raw).hexdigest(),h,name)
 def test_only_authorized_code_bound_changes(self):
  for name,key,changes in [('registry.py','registry_sha256',{'MAX_UNITS = 10':'MAX_UNITS = 9','MAX_TOTAL_LESSONS = 86':'MAX_TOTAL_LESSONS = 76','1–10 bundled':'1–9 bundled','at most 86 total':'at most 76 total'}),('image_catalog.py','image_catalog_code_sha256',{'MAX_RETAINED_LESSONS = 86':'MAX_RETAINED_LESSONS = 76','MAX_DEFAULT_LESSONS = 86':'MAX_DEFAULT_LESSONS = 76'})]:
   text=foundation_projection(name,(registry.ROOT/name).read_bytes()).decode()
   for a,b in changes.items():text=text.replace(a,b)
   self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),BASE[key])
 def test_catalog_projection_preserves_original_pins(self):
  data=json.loads(foundation_projection('image-catalog.json',resource('image-catalog.json')));new=set(COMMANDS)
  new |= NEW_IDS
  data['lessons']=[l for l in data['lessons'] if l['id'] not in new]
  for image in data['images']:image['lessons']=[l for l in image['lessons'] if l['id'] not in new]
  for f in ('default_images','default_lessons'):data[f]={k:v for k,v in data[f].items() if k not in new}
  self.assertEqual(digest(data),BASE['catalog_digest'])
 def test_exact_routes_no_fallback(self):
  for x in DATA:
   c=production_catalog();s,l=c.defaults(x['id']);expected='debian13-admin-local-v1' if x['admin'] else 'debian13-jobs-local-v1';self.assertEqual(s['image_id'],expected)
   for image in c.images.values():
    if image['descriptor']!=s:
     with self.assertRaises(ValueError):c.resolve({'backend':'offline-qemu-preview-1','image':image['descriptor'],'lesson_sha256':digest(l)},x['id'])
   del c.images[digest(s)]
   with self.assertRaises(ValueError):c.defaults(x['id'])
 def test_display_only_and_exact_fixture_cleanup(self):
  with patch('subprocess.Popen',side_effect=AssertionError('host execution')),patch('socket.socket',side_effect=AssertionError('network')):
   for x in DATA:
    l=registry.load_lesson(x['id']);self.assertEqual([s['command'] for s in l['steps']],x['commands']);self.assertIn(x['cleanup_command'],registry.entry(x['id'])['cleanup']);self.assertIn('Self-reviewed',l['coverage'])
    self.assertNotIn('score',l);self.assertNotIn('rm -rf',str(l));self.assertIn('test "${w%/*}" = "$HOME"',x['commands'][0]);self.assertIn('fresh()',x['commands'][0])
 def test_isolated_modes_retention_reopen(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fake=root/'not-a-disk';fake.write_bytes(b'fixture');s=Sessions(root/'vm','a'*64,root/'gate');old={}
   def reset(m,mode):
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda _:os.open(fake,os.O_RDONLY)):return m.reset(mode,True)
   for entry in registry.entries()[:76]:
    m=s.manager(entry['id']);reset(m,'Learn');m.progress('hint');p=root/'vm/profiles'/m.profile/'current.json';old[p]=p.read_bytes()
   for x in DATA:
    m=s.manager(x['id']);one=reset(m,'Learn');m.progress('next');m.progress('hint');m.progress('complete');record=m.status()['session'];self.assertEqual(record,Sessions(root/'vm','a'*64,root/'gate').manager(x['id']).status()['session']);self.assertEqual(record['completion']['kind'],'self-reviewed')
    disk=root/'vm/profiles'/m.profile/'generations'/one['generation']/'disk.qcow2';raw=disk.read_bytes();two=reset(m,'Challenge');self.assertEqual(one['pin'],two['pin']);self.assertNotEqual(one['generation'],two['generation']);self.assertEqual(disk.read_bytes(),raw)
    for op in ('next','hint'):
     with self.assertRaises(ValueError):m.progress(op)
   for p,raw in old.items():self.assertEqual(p.read_bytes(),raw)
