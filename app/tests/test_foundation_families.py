"""Bounds and compatibility only; live outcomes have separate native evidence."""
import copy,hashlib,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from learning_lab.vm_preview import registry
from learning_lab.vm_preview.image_catalog import Catalog,digest,production_catalog,resource,read_json
from learning_lab.vm_preview.sessions import Sessions
from foundation_preservation import projection,NEW_IDS
from text_archive_guest_fixtures import DATA as TEXT

BASE=json.loads(Path(__file__).with_name('foundation_baseline.json').read_text())
ROOT=registry.ROOT.parents[2]
class FoundationTests(unittest.TestCase):
 def tearDown(self):registry._bundle.cache_clear()
 def data(self):
  return TEXT
 def malformed(self,change,pattern):
  original=registry._read
  def read(name):v=copy.deepcopy(original(name));change(name,v);return v
  registry._bundle.cache_clear()
  with patch.object(registry,'_read',side_effect=read),self.assertRaisesRegex(ValueError,pattern):registry.units()
 def test_exact_bounds_and_parser_sizes(self):
  self.assertEqual((registry.MAX_UNITS,registry.MAX_TOTAL_LESSONS,registry.MAX_LESSONS_PER_UNIT),(11,94,16))
  self.assertEqual(len(registry.units()),11);self.assertEqual(len(registry.entries()),94)
  c=production_catalog();self.assertEqual((len(c.lessons),len(c.default_images),len(c._data['default_lessons'])),(94,94,94));self.assertFalse(c.keys or c.releases)
  for name in ('image-catalog.json','text-archive-unit.json'):self.assertLessEqual(len(resource(name)),65536);read_json(resource(name))
  self.assertTrue(all(len(i['lessons'])<=64 for i in c.images.values()))
 def test_immediate_total_overflow(self):
  self.malformed(lambda n,v:v['entries'].append(copy.deepcopy(v['entries'][0])) if n=='text-archive-unit.json' else None,'94')
 def test_immediate_unit_overflow(self):
  self.malformed(lambda n,v:v['units'].append(copy.deepcopy(v['units'][0])) if n=='units.json' else None,'1–11')
 def test_seventeenth_lesson_rejected(self):
  self.malformed(lambda n,v:v['entries'].extend([copy.deepcopy(v['entries'][0])]*9) if n=='text-archive-unit.json' else None,'1–16')
 def test_sixteenth_lesson_accepted(self):
  original=registry._read;first=copy.deepcopy(original('unit.json'));last=copy.deepcopy(original('text-archive-unit.json'));second=copy.deepcopy(original('resource-unit.json'))
  last['entries']+=first['entries'][1:]+second['entries'][:1];first['entries']=first['entries'][:1];second['entries']=second['entries'][1:]
  registry._bundle.cache_clear();values={'unit.json':first,'text-archive-unit.json':last,'resource-unit.json':second}
  with patch.object(registry,'_read',side_effect=lambda n:copy.deepcopy(values.get(n,original(n)))):self.assertEqual(len(registry.entries()),94)
 def test_default_retained_and_unrelated_limits(self):
  original=json.loads(resource('image-catalog.json'))
  for field in ('lessons','default_images','default_lessons'):
   bad=copy.deepcopy(original)
   if field=='lessons':bad[field].append(copy.deepcopy(bad[field][0]))
   else:bad[field]['extra']='0'*64
   with self.assertRaisesRegex(ValueError,{'lessons':'Catalog count exceeds limit','default_images':'Incomplete per-lesson image defaults','default_lessons':'Missing default lesson'}[field]):Catalog(bad)
  for field in ('images','keys','releases'):
   bad=copy.deepcopy(original);bad[field]=[{}]*65
   with self.assertRaisesRegex(ValueError,'Catalog count exceeds limit'):Catalog(bad)
  bad=copy.deepcopy(original);bad['images'][0]['lessons']=[bad['images'][0]['lessons'][0]]*65
  with self.assertRaisesRegex(ValueError,'compatibility'):Catalog(bad)
 def test_original_bytes_and_exact_authorized_code_delta(self):
  for name,h in BASE['protected'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),h,name)
  for name,key in [('registry.py','registry_sha256'),('image_catalog.py','image_catalog_code_sha256')]:self.assertEqual(hashlib.sha256(projection(name,(registry.ROOT/name).read_bytes())).hexdigest(),BASE[key])
  self.assertEqual(hashlib.sha256(projection('Main.qml',(ROOT/'app/learning_lab/qml/Main.qml').read_bytes())).hexdigest(),BASE['main_sha256'])
 def test_exact_original_catalog_and_unit_pins(self):
  for name,key in [('image-catalog.json','catalog_digest'),('units.json','units_digest')]:self.assertEqual(hashlib.sha256(projection(name,resource(name))).hexdigest(),BASE[key])
 def test_display_only_resources_and_no_host_effects(self):
  with patch('subprocess.Popen',side_effect=AssertionError('host execution')),patch('socket.socket',side_effect=AssertionError('network')):
   for x in self.data():
    l=registry.load_lesson(x['id']);self.assertEqual(l,x['content']);self.assertEqual(registry.entry(x['id']),x['entry']);self.assertIn('Self-reviewed',l['coverage']);self.assertNotIn('score',l)
    self.assertIn('here()',x['commands'][0]);self.assertIn('fresh()',x['commands'][0]);self.assertNotIn('rm -rf',x['cleanup_command'])
 def test_exact_routes_and_missing_image_no_fallback(self):
  for x in self.data():
   c=production_catalog();s,l=c.defaults(x['id']);self.assertEqual(s['image_id'],'debian13-admin-local-v1' if x['admin'] else 'debian13-jobs-local-v1')
   for image in c.images.values():
    if image['descriptor']!=s:
     with self.assertRaises(ValueError):c.resolve({'backend':'offline-qemu-preview-1','image':image['descriptor'],'lesson_sha256':digest(l)},x['id'])
   del c.images[digest(s)]
   with self.assertRaises(ValueError):c.defaults(x['id'])
 def test_unavailable_withdrawn_and_stop_resolution(self):
  for x in self.data():
   for state in ('resume-only','withdrawn'):
    c=production_catalog();s,l=c.defaults(x['id']);pin={'backend':'offline-qemu-preview-1','image':s,'lesson_sha256':digest(l)};c.images[digest(s)]['state']=state
    for operation in ('new','reset'):
     with self.assertRaises(ValueError):c.allow(pin,x['id'],operation)
    if state=='withdrawn':
     with self.assertRaises(ValueError):c.allow(pin,x['id'],'resume')
    # Stop uses the unchanged manager/process route, not boot admission.
    self.assertEqual(c.resolve(pin,x['id'])[0]['descriptor'],s)
 def test_modes_retained_reset_and_reopening(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);fake=root/'fake';fake.write_bytes(b'fixture');s=Sessions(root/'vm','b'*64,root/'gate');old={}
   def reset(m,mode):
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda _:os.open(fake,os.O_RDONLY)):return m.reset(mode,True)
   for e in registry.entries()[:86]:
    m=s.manager(e['id']);reset(m,'Learn');m.progress('hint');p=root/'vm/profiles'/m.profile/'current.json';old[p]=p.read_bytes()
   for x in self.data():
    m=s.manager(x['id']);one=reset(m,'Learn');m.progress('next');m.progress('hint');m.progress('complete');record=m.status()['session'];self.assertEqual(record,Sessions(root/'vm','b'*64,root/'gate').manager(x['id']).status()['session']);self.assertEqual(record['completion']['kind'],'self-reviewed')
    disk=root/'vm/profiles'/m.profile/'generations'/one['generation']/'disk.qcow2';raw=disk.read_bytes();two=reset(m,'Challenge');self.assertEqual(one['pin'],two['pin']);self.assertNotEqual(one['generation'],two['generation']);self.assertEqual(disk.read_bytes(),raw)
    for op in ('next','hint'):
     with self.assertRaises(ValueError):m.progress(op)
   for p,raw in old.items():self.assertEqual(p.read_bytes(),raw)

 def test_cleanup_type_refusal_isolated_from_enumeration(self):
  # Static developer fixture: every executor is a stub and PATH is empty.
  # No learner input or real deletion/query reaches the host.
  from foundation_guest_fixtures import quote
  for x in self.data():
   leaf=x['files'][0];definition=x['cleanup_command'].removesuffix('; clean_family')
   stubs='here() { return 0; }; find() { return 0; }; test() { if builtin test "$1" = -f && builtin test "$2" = '+quote(leaf)+'; then return 1; fi; return 0; }; rm() { echo REMOVE_CALLED; }; rmdir() { echo REMOVE_CALLED; }; cd() { echo CHANGED_DIRECTORY; }; umask() { echo CHANGED_UMASK; }'
   with tempfile.TemporaryDirectory() as td:
    v=subprocess.run(['/usr/bin/bash','--noprofile','--norc','-c',stubs+'; '+definition+'; clean_family; rc=$?; printf "STATUS=%s\\n" "$rc"'],cwd=td,env={'PATH':'/nonexistent','LC_ALL':'C'},capture_output=True,text=True,timeout=5)
    self.assertEqual(v.stdout,'STATUS=19\n',x['id']+v.stderr);self.assertEqual(list(Path(td).iterdir()),[])
