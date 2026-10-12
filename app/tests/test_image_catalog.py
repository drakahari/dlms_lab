from foundation_preservation import NEW_IDS
"""Pinned revision/availability fixtures; never launch a guest."""
import copy,hashlib,json,os,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from learning_lab.vm_preview.image_catalog import Catalog,canonical,digest,resource,production_catalog
from learning_lab.vm_preview.catalog_manager import CatalogManager
from learning_lab.vm_preview.manager import Manager,now
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.policy import BACKEND,image_spec
from learning_lab.vm_preview.registry import LEGACY_ID,load_lesson,session_binding
from learning_lab.vm_preview.files import Refused

class CatalogTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.data=json.loads(resource('image-catalog.json'));self.resources={}
 def tearDown(self):self.tmp.cleanup()
 def catalog(self):return Catalog(self.data,lambda n:self.resources[n] if n in self.resources else resource(n))
 def manager(self,catalog=None,id=LEGACY_ID,profile='a'*64):
  return CatalogManager(self.root/'vm',session_binding(profile,id),self.root/'gate',lesson_id=id,catalog=catalog or self.catalog())
 def record(self,m,mode='Learn'):
  record={'schema_version':1,'session':str(uuid.uuid4()),'generation':str(uuid.uuid4()),'mode':mode,'pin':copy.deepcopy(m.pin),'started':now(),'step':1,'hints':1 if mode=='Learn' else 0,'completion':{'kind':'self-reviewed','at':now()}}
  with m.access() as (_,g,p):
   with p.child('generations',create=True) as gens,gens.child(record['generation'],create=True) as gen:
    gen.write('origin.json',record);gen.write('lifecycle.json',{'state':'stopped','at':now()});fd=gen.open('disk.qcow2',True,True);os.write(fd,b'NEVER BOOT THIS FIXTURE');os.close(fd)
   p.write('current.json',record)
  return record
 def inventory(self):return {str(p.relative_to(self.root)):p.read_bytes() for p in (self.root/'vm').rglob('*') if p.is_file()}
 def add_revision(self):
  # Smaller isolated rollback catalog leaves room for an added retained revision.
  gone={l['id'] for l in self.data['lessons'] if l['id'] in NEW_IDS or l['id'].startswith(('real-linux-discovery-','real-linux-storage-','real-linux-local-'))}
  self.data['lessons']=[l for l in self.data['lessons'] if l['id'] not in gone]
  self.data['images']=[i for i in self.data['images'] if i['descriptor']['image_id']!='debian13-package-admin-local-v1']
  for image in self.data['images']:image['lessons']=[l for l in image['lessons'] if l['id'] not in gone]
  for field in ('default_images','default_lessons'):self.data[field]={k:v for k,v in self.data[field].items() if k not in gone}
  lesson=load_lesson();lesson.update(title='Updated fixture title',content_version='1.0.1');self.resources['fixture-revision.json']=canonical(lesson)
  self.data['lessons'].append({'id':LEGACY_ID,'sha256':digest(lesson),'resource':'fixture-revision.json','state':'active'})
  self.data['default_lessons'][LEGACY_ID]=digest(lesson)
  image=copy.deepcopy(image_spec());image.update(image_id='new-fixture-image',sha256='b'*64,version=2)
  self.data['images'].append({'descriptor':image,'state':'active','legacy':False,'lessons':[{'id':l['id'],'sha256':l['sha256']} for l in self.data['lessons']]});self.data['default_image']=digest(image);self.data.pop('default_images',None)
 def test_legacy_catalog_exact_and_active(self):
  cat=production_catalog();old=Manager(self.root/'unused','a'*64);m=self.manager(cat)
  self.assertEqual(old.pin,m.pin);self.assertEqual(m.profile,'a'*64);self.assertFalse(self.root.joinpath('unused').exists())
  cat.allow(m.pin,LEGACY_ID,'new');cat.allow(m.pin,LEGACY_ID,'reset');cat.allow(m.pin,LEGACY_ID,'resume')
  self.assertEqual(len(cat.lessons),102);self.assertEqual(len(cat.images),4);self.assertEqual(cat.keys,{});self.assertEqual(cat.releases,{})
 def test_catalog_edit_reopen_preserves_exact_learn_challenge_bytes(self):
  for mode,profile in (('Learn','a'*64),('Challenge','b'*64)):
   old=self.manager(profile=profile);self.record(old,mode)
  before=self.inventory();self.add_revision()
  for profile in ('a'*64,'b'*64):
   m=self.manager(profile=profile);self.assertEqual(m.lesson['title'],'Updated fixture title')
   self.assertEqual(m.status()['session']['pin'],Manager(self.root/'unused',profile).pin)
   self.assertEqual(m.lesson,load_lesson());self.assertEqual(m.spec,image_spec())
  self.assertEqual(self.inventory(),before)
 def test_resume_only_blocks_reset_and_new_without_writes(self):
  m=self.manager();self.record(m);self.data['images'][0]['state']='resume-only';m=self.manager();before=self.inventory()
  m.status();m._authorize('resume',m.status()['session'])
  with self.assertRaisesRegex(Refused,'resume-only'):m.reset(confirmed=True)
  self.assertEqual(before,self.inventory())
  new=self.manager(profile='b'*64)
  with patch.object(new,'prepare',side_effect=AssertionError('created disk')):
   with self.assertRaisesRegex(Refused,'resume-only'):new.start()
 def test_withdrawn_blocks_boot_reset_but_does_not_touch_session(self):
  m=self.manager();self.record(m);self.data['images'][0]['state']='withdrawn';m=self.manager();before=self.inventory()
  self.assertEqual(m.status()['state'],'stopped')
  with patch('subprocess.Popen',side_effect=AssertionError('spawn')):
   for action in (lambda:m.start(),lambda:m.reset(confirmed=True)):
    with self.assertRaisesRegex(Refused,'withdrawn'):action()
  self.assertEqual(self.inventory(),before)
 def test_withdrawn_lesson_blocks_boot(self):
  m=self.manager();self.record(m)
  next(v for v in self.data['lessons'] if v['id']==LEGACY_ID)['state']='withdrawn'
  with self.assertRaisesRegex(Refused,'withdrawn'):self.manager().start()
 def test_missing_image_or_lesson_retained_stop_routes(self):
  old=self.manager();saved=self.record(old);self.add_revision();before=self.inventory()
  for missing in ('image','lesson','resource'):
   cat=self.catalog()
   if missing=='image':cat.images.pop(digest(saved['pin']['image']))
   elif missing=='lesson':cat.lessons.pop((LEGACY_ID,saved['pin']['lesson_sha256']))
   else:
    original=cat._read
    def fail(name):
     if name=='lesson.json':raise FileNotFoundError(name)
     return original(name)
    cat._read=fail
   m=self.manager(cat);sessions=Sessions(self.root/'vm','a'*64,self.root/'gate');sessions.managers[LEGACY_ID]=m
   running={'state':'running','store':m.binding,'profile':m.profile}
   with patch.object(m,'reconcile',return_value=running),patch.object(m,'stop',return_value='verified stop') as stop:
    view=sessions.view(LEGACY_ID);self.assertEqual(view['running_state'],'control-only');self.assertEqual(view['running_lesson_id'],LEGACY_ID)
    sessions.running_manager(LEGACY_ID).stop();stop.assert_called_once()
   with patch('subprocess.Popen',side_effect=AssertionError('unavailable content spawned a process')):
    for action in (m.start,lambda:m.reset(confirmed=True)):
     with self.assertRaises(ValueError):action()
   self.assertEqual(self.inventory(),before)
 def test_actual_inherited_stop_does_not_require_content(self):
  m=self.manager();saved=self.record(m);m.catalog.images.clear()
  record={'state':'running','store':m.binding,'profile':m.profile,'generation':saved['generation'],'run':str(uuid.uuid4())}
  with m.access() as (_,gate,p):
   with gate.child(record['run'],create=True):pass
   fd=m.gate(gate);os.close(fd) # Actual running sessions always have a lifetime lock.
  from unittest.mock import MagicMock
  q=MagicMock();q.__enter__.return_value.powerdown.return_value=True
  with patch.object(m,'reconcile',return_value=record),patch('learning_lab.vm_preview.manager.Qmp',return_value=q):
   self.assertEqual(m.stop(),'Cleanly stopped');q.__enter__.return_value.powerdown.assert_called_once_with(record)
  self.assertEqual(m.stop.__func__,Manager.stop)
 def test_rollback_known_legacy_and_unknown_new_pin(self):
  m=self.manager();old=self.record(m);before=self.inventory();self.add_revision()
  self.assertEqual(self.manager().status()['session'],old);self.assertEqual(self.inventory(),before)
  # Unchanged baseline controller still reads old records exactly.
  self.assertEqual(Manager(self.root/'vm','a'*64,self.root/'gate').status()['session'],old)
  new=self.manager(profile='b'*64);self.record(new);before=self.inventory()
  with self.assertRaisesRegex(Refused,'older'):Manager(self.root/'vm','b'*64,self.root/'gate').status()
  with self.assertRaisesRegex(Refused,'unavailable'):self.manager(production_catalog(),profile='b'*64).status()
  self.assertEqual(self.inventory(),before)
 def test_retained_digest_and_duplicate_rejection(self):
  self.add_revision();self.resources['fixture-revision.json']=canonical(load_lesson())
  with self.assertRaisesRegex(Refused,'digest'):self.catalog().defaults(LEGACY_ID)
  self.data['images'].append(copy.deepcopy(self.data['images'][0]))
  with self.assertRaisesRegex(Refused,'Duplicate'):self.catalog()
 def test_catalog_copies_cannot_change_saved_pins(self):
  cat=self.catalog();spec,lesson=cat.defaults(LEGACY_ID);spec['sha256']='0'*64;lesson['steps'].clear()
  self.assertEqual(cat.defaults(LEGACY_ID),(image_spec(),load_lesson()))

 def test_image_lesson_pair_must_be_explicit(self):
  m=self.manager();saved=self.record(m);before=self.inventory()
  image=self.data['images'][0];image['lessons']=[p for p in image['lessons'] if p['id']!=LEGACY_ID]
  with self.assertRaisesRegex(Refused,'pair'):self.catalog()
  self.data.pop('default_images')  # Legacy catalog still refuses at pin resolution.
  cat=self.catalog()
  with self.assertRaisesRegex(Refused,'combination'):cat.resolve(saved['pin'],LEGACY_ID)
  self.assertEqual(self.inventory(),before)

 def test_all_accepted_revisions_remain_available(self):
  expected={'real-linux-process-inspection': '74d4890547d9b0fe8781c8381a2054e07584f5897ea7ae6812f351a602bf981b', 'real-linux-foreground-jobs': '4b557cebe81d0139bc4f7a20358e19b111e633eef0e9a1a32ef3dffc57392995', 'real-linux-background-job': 'cc71a87e9cc21224b84803a4175dffdfd83da793700402e20ffe3515eeb59180', 'real-linux-targeted-signals': '74313980280ec7d3c051eebb4f990b52beb985c0d49c900879c17ef94c3878bc', 'real-linux-live-monitoring': '09418373ac0317e45a6a7e54bf4b5e277b1964cec29b69b3321bd0986cb87270', 'real-linux-logout-persistence': 'f61fe25369e916aa928397dde2f670d83f9f55c5f8b7c945a383c7356f076ae1', 'real-linux-process-priorities': '41e60137f469672450ebc59b91003b63864821edd002f608e9c1e032efbc8f7c', 'real-linux-process-handover': '1cb7c3424c060c1657e61d695d4bbf14a9e529df4e48bd3d92a614e477f8a7b7'}
  cat=production_catalog()
  for id,sha in expected.items():
   image,lesson=cat.resolve({'backend':BACKEND,'image':image_spec(),'lesson_sha256':sha},id)
   self.assertEqual(digest(lesson[1]),sha)

 def test_withdrawal_never_bypasses_real_process_identity(self):
  # Real /proc verification, no mocked reconcile/process identity/QMP. A forged
  # record names this Python process: neither unavailable nor withdrawn content
  # may convert it into permission to signal/connect to an arbitrary process.
  m=self.manager();saved=self.record(m)
  self.data['images'][0]['state']='withdrawn';m=self.manager()
  forged={'schema_version':1,'state':'running','store':m.binding,'profile':m.profile,
          'generation':saved['generation'],'session':saved['session'],'run':str(uuid.uuid4()),
          'process':{'pid':os.getpid(),'start':'0','boot':'forged','argv_sha256':'0'*64}}
  with m.access() as (_,gate,p):gate.write('running.json',forged)
  for missing in (False,True):
   if missing:m.catalog.images.clear()
   with self.assertRaisesRegex(Refused,'trusted QEMU'):m.stop()
  self.assertEqual(os.getpid(),forged['process']['pid'])

 def test_every_explicit_route_availability_and_preserved_records(self):
  # All 44 routes, both image and lesson availability; no image/disk mock can
  # hide an accidental boot. Authorization must reject before process creation.
  for id in self.data['default_lessons']:
   m=self.manager(id=id);saved=self.record(m);before=self.inventory()
   for field in ('image','lesson'):
    for state in ('resume-only','withdrawn'):
     cat=self.catalog()
     if field=='image':cat.images[digest(saved['pin']['image'])]['state']=state
     else:cat.lessons[(id,saved['pin']['lesson_sha256'])][0]['state']=state
     m=self.manager(cat,id=id)
     self.assertEqual(m.status()['session'],saved)
     with patch('subprocess.Popen',side_effect=AssertionError('unauthorized spawn')):
      with self.assertRaisesRegex(Refused,state):m.reset(confirmed=True)
      fresh=self.manager(cat,id=id,profile='b'*64)
      with self.assertRaisesRegex(Refused,state):fresh.start()
      if state=='withdrawn':
       with self.assertRaisesRegex(Refused,'withdrawn'):m.start()
      else:m._authorize('resume',saved)
     self.assertEqual(m.pin,saved['pin'])
   # Access may create empty lock directories; saved evidence must not change.
   after=self.inventory()
   for path,raw in before.items():self.assertEqual(after[path],raw)

 def test_every_route_missing_mismatched_or_unavailable_pin_refuses_boot(self):
  for id in self.data['default_lessons']:
   m=self.manager(id=id);saved=self.record(m);before=self.inventory()
   for fault in ('missing-image','missing-lesson','mismatched-descriptor','mismatched-resource'):
    m=self.manager(id=id);cat=m.catalog
    if fault=='missing-image':cat.images.pop(digest(saved['pin']['image']))
    elif fault=='missing-lesson':cat.lessons.pop((id,saved['pin']['lesson_sha256']))
    elif fault=='mismatched-descriptor':cat.images[digest(saved['pin']['image'])]['descriptor']['version']+=1
    else:cat._read=lambda name:canonical({'id':id,'title':'substituted'})
    with patch('subprocess.Popen',side_effect=AssertionError('invalid pin spawned')):
     for action in (m.start,lambda:m.reset(confirmed=True)):
      with self.assertRaises(ValueError):action()
    self.assertEqual(m.pin,saved['pin'])
   self.assertEqual(before,self.inventory())

 def test_old_route_missing_base_never_uses_installed_admin_base(self):
  # Real descriptor-contained file lookup, not a mocked image() implementation.
  m=self.manager();admin=self.catalog().defaults('real-linux-admin-change')[0]
  with m.access() as (root,g,p):
   with root.child('images',create=True) as images,images.child(admin['sha256'],create=True) as image:
    fd=image.open('base.raw',True,True);os.write(fd,b'ADMIN MUST NOT BE USED');os.close(fd)
   with self.assertRaisesRegex(Refused,'pinned local image is not registered'):m.image(root)
  self.assertEqual(m.spec,image_spec())
