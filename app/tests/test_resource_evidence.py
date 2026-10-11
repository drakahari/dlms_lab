"""Supplied facts, not reasoning: contract 5 only; disposable profiles."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios, ProfileLocks
from learning_lab.catalog import CatalogBridge
from learning_lab.collections import load_collections
from learning_lab.domain.validation import ValidationError
from learning_lab.portable import load_portable
from learning_lab.linux_text.engine import guide
from learning_lab import profile_backup as pb

APP=QCoreApplication.instance() or QCoreApplication([])
ROOT=Path(__file__).resolve().parents[1]
UNIT=load_collections()[4]
ENTRIES=UNIT['entries']
IDS=['linux-resource-baseline','linux-memory-evidence','linux-space-inodes','linux-trend-handover']
ALTERNATIVES=[['tail -n 6 ./snapshot.txt | head -n 5 > /home/learner/baseline.txt'],
 ['cat /home/learner/memory.txt | tail -n 8 > ./memory-report.txt'],
 ['cat space.txt | tail -n 2 > ./space-report.txt','tail -n 2 /home/learner/inodes.txt > /home/learner/inode-report.txt'],
 ['tail -n 4 ./history.txt | sort > handover.txt']]

def finish(s):
 for _ in range(64):
  if s.engine.grade()['complete']:return
  s.execute(guide(s.pack,s.attempt['applied'])['command'])
 raise AssertionError('Learn route failed')

def verify(s):
 for o in s.pack['objectives']:
  if o['predicate']=='stream_observed':s.execute('cat '+o['params']['source'])

class ResourceEvidenceTests(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name);self.bridges=[];self.locks=[]
 def tearDown(self):
  for b in self.bridges:
   for l in b.labs.values():l.timer.stop()
  for l in self.locks:l.unlock()
  self.t.cleanup()
 def build(self,name='profile'):
  r=self.root/name;(r/'config').mkdir(parents=True,exist_ok=True)
  b=CatalogBridge(load_bundled_scenarios()[0],r/'data',r/'config');self.bridges.append(b);return b
 def test_registration_separate_vm_bounds_and_truthful_labels(self):
  self.assertEqual(UNIT['id'],'lpic-resource-evidence');self.assertEqual([e['scenario'].identity.scenario_id for e in ENTRIES],IDS)
  self.assertEqual(len(load_collections()),5);b=self.build();self.assertEqual(len(b.curated),26)
  self.assertFalse(b.repository.root.exists());self.assertEqual(b.view['collections'][4]['completed'],{'Learn':0,'Challenge':0})
  from learning_lab.vm_preview.registry import units,entries
  self.assertEqual((len(units()),len(entries())),(9,76))
  for e in ENTRIES:
   v=e['scenario'].value();self.assertEqual(v['engine']['contract_version'],5)
   self.assertTrue(all(o['predicate'] in ('file_content','stream_observed','original_preserved') for o in v['objectives']))
   self.assertIn('Self-review',v['mission']['brief']);self.assertIn('not measurements',v['mission']['constraints'][0])
   self.assertIn('self-reviewed',v['domain']['filesystem']['/home/learner/HELP.txt']['content'].lower())
   self.assertIn('Model interpretation:',v['domain']['filesystem']['/home/learner/HELP.txt']['content'])
   self.assertIn('Common mistakes:',v['domain']['filesystem']['/home/learner/HELP.txt']['content'])
 def test_both_modes_hints_and_equivalent_approaches(self):
  for i,e in enumerate(ENTRIES):
   with self.subTest(lab=IDS[i]):
    s=e['scenario'].domain().session();s.hint();finish(s);self.assertEqual(s.submit()['score'],100)
    self.assertEqual(s.attempt['hints'],1)
    s=e['scenario'].domain().session(mode='Challenge');self.assertEqual(s.domain.view_state(s,None,0)['guide'],{})
    with self.assertRaises(ValidationError):s.hint()
    for c in ALTERNATIVES[i]:s.execute(c)
    verify(s);self.assertEqual(s.submit()['score'],100,s.attempt['console'])
 def test_incomplete_wrong_reports_retry_and_last_write_verification(self):
  for i,e in enumerate(ENTRIES):
   s=e['scenario'].domain().session();self.assertLess(s.submit()['score'],100)
   source=next(o['params']['source'] for o in s.pack['objectives'] if o['predicate']=='stream_observed')
   dest=s.pack['domain']['output_files'][0]
   s.execute('head -n 1 '+source+' > '+dest);verify(s);self.assertFalse(s.submit()['complete'])
   finish(s);self.assertEqual(s.submit()['score'],100)
   s.execute('cat '+source+' > '+dest);self.assertFalse(s.submit()['complete'])
   for c in ALTERNATIVES[i]:s.execute(c)
   self.assertLess(s.submit()['score'],100);verify(s);self.assertEqual(s.submit()['score'],100)
 def test_reading_tools_and_ungraded_reasoning_are_not_overclaimed(self):
  for i,e in enumerate(ENTRIES):
   s=e['scenario'].domain().session()
   for cmd in ALTERNATIVES[i]:s.execute(cmd)
   for o in s.pack['objectives']:
    if o['predicate']=='stream_observed':s.execute('head -n 99 '+o['params']['source'])
   s.execute('cat HELP.txt');self.assertEqual(s.submit()['score'],60)
   verify(s);self.assertEqual(s.submit()['score'],100)
   self.assertIn('Required reading',e['scenario'].value()['mission']['constraints'][-1])
 def test_gap_units_and_both_resources_retained(self):
  baseline=ENTRIES[0]['scenario'].value()['objectives'][0]['params']['content'];self.assertIn('1 second',baseline);self.assertIn('KiB/s',baseline)
  memory=ENTRIES[1]['scenario'].value()['objectives'][0]['params']['content'];self.assertIn('MemAvailable',memory);self.assertIn('si=0 KiB/s',memory)
  s=ENTRIES[2]['scenario'].domain().session();s.execute('tail -n 2 space.txt > space-report.txt');verify(s);self.assertLess(s.submit()['score'],100)
  s=ENTRIES[3]['scenario'].domain().session();s.execute('grep -F observed history.txt | sort > handover.txt');verify(s);self.assertLess(s.submit()['score'],100)
 def test_no_host_effects_or_other_virtual_outputs(self):
  for e in ENTRIES:
   s=e['scenario'].domain().session();initial=deepcopy(s.attempt['applied']['filesystem'])
   with patch('subprocess.Popen',side_effect=AssertionError('host process')),patch('socket.socket',side_effect=AssertionError('network')):
    for c in ['free','df -h','rm /','cat /etc/passwd','cat HELP.txt > /tmp/host-result','cat HELP.txt > /home/learner/../other.txt','cat HELP.txt > /home/learner/snapshot.txt','cat HELP.txt; touch x','cat HELP.txt | sh']:
     s.execute(c)
    self.assertEqual(s.attempt['applied']['filesystem'],initial)
    finish(s);self.assertEqual(s.submit()['score'],100)
 def test_reset_modes_history_and_lab_isolation(self):
  b=self.build();snap={}
  for e in ENTRIES:
   b.selectLab(e['scenario'].key,True);initial=deepcopy(b.session.attempt['applied']);finish(b.session);b.submit();old=b.session.attempt['id'];b.restart('Challenge')
   self.assertEqual(b.session.attempt['applied'],initial);self.assertIn(old,[r['id'] for r in b.store.history(b.session.attempt['id'])[0]])
   finish(b.session);b.submit();b.setCommandDraft('cat HELP.txt');b.flush();snap[e['scenario'].key]=deepcopy(b.session.attempt)
  for key,attempt in snap.items():self.assertEqual(b.labs[key].session.attempt,attempt)
  b.restart('Challenge');self.assertEqual(b.session.attempt['applied'],initial)
  self.assertIn(old,[r['id'] for r in b.store.history(b.session.attempt['id'])[0]])
 def test_separate_process_resume_exact_pins_modes_drafts_and_bytes(self):
  b=self.build()
  for e in ENTRIES:
   b.selectLab(e['scenario'].key,True);finish(b.session);b.submit();b.restart('Challenge');finish(b.session);b.submit();b.setCommandDraft('cat HELP.txt');b.flush()
  expected={k:l.session.attempt for k,l in b.labs.items()};(self.root/'expected.json').write_text(json.dumps(expected));before={p:p.read_bytes() for p in (self.root/'profile').rglob('*.json')}
  code='''import json,sys
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
app=QCoreApplication([]);r=Path(sys.argv[1]);b=CatalogBridge(load_bundled_scenarios()[0],r/'profile/data',r/'profile/config')
assert {k:l.session.attempt for k,l in b.labs.items()}==json.loads((r/'expected.json').read_text())
assert b.view['collections'][4]['completed']=={'Learn':4,'Challenge':4}
assert b.view['commandDraft']=='cat HELP.txt'
for l in b.labs.values():l.timer.stop()
print('Separate-process resume PASS')
'''
  r=subprocess.run([sys.executable,'-B','-c',code,str(self.root)],cwd=ROOT,capture_output=True,text=True,timeout=30);self.assertEqual(r.returncode,0,r.stderr)
  for p,data in before.items():self.assertEqual(p.read_bytes(),data)
 def test_export_reimport_backup_visibility_and_old_pinned_attempt(self):
  b=self.build();lock=ProfileLocks(b.data_root,b.config_root);b.profile_locks=lock;self.locks.append(lock)
  for e in ENTRIES:
   lab=e['scenario'];b.selectLab(lab.key,True);finish(b.session);b.submit();b.flush();prior=deepcopy(b.session.attempt)
   p=self.root/(lab.identity.scenario_id+'.lab.json');self.assertTrue(b.exportScenario(str(p)));self.assertEqual(p.read_bytes(),lab.original_bytes)
   self.assertTrue(b.importPack(str(p)));self.assertEqual(b.session.attempt,prior)
   other=self.build(lab.identity.scenario_id);self.assertTrue(other.importPack(str(p)));other.selectLab(lab.key,True);finish(other.session);other.submit();self.assertEqual(other.view['grade']['score'],100)
   self.assertTrue(b.exportAttempt(str(self.root/(lab.identity.scenario_id+'.history.json')),prior['id']))
  v=ENTRIES[0]['scenario'].value();v['identity']['content_version']='0.9.0';old,_=b.repository.install(json.dumps(v).encode());b._add_portable(old);b.selectLab(old.key,True);b.execute('pwd');b.flush()
  b.setLibraryState(ENTRIES[-1]['scenario'].key,'hidden');before={k:deepcopy(l.session.attempt) for k,l in b.labs.items()};path=self.root/'snapshot.llbackup';self.assertTrue(b.backupProfile(str(path)),b.transfer_message)
  pb.restore(pb.read_backup(path),self.root/'restored',confirmed=True);restored=self.build('restored');self.assertEqual({k:l.session.attempt for k,l in restored.labs.items()},before);self.assertEqual(restored.visibility.entries,b.visibility.entries)
 def test_collection_capacity_and_content_limits(self):
  resources=self.root/'resources';shutil.copytree(ROOT/'learning_lab/collections',resources/'collections');p=resources/'collections/index.json';base=json.loads(p.read_text())
  with patch('learning_lab.collections.files',return_value=resources):
   eight=deepcopy(base)
   for i in range(3):e=deepcopy(base['collections'][4]);e['id']='test-'+str(i);eight['collections'].append(e)
   p.write_text(json.dumps(eight));self.assertEqual(len(load_collections()),8)
   e=deepcopy(eight['collections'][-1]);e['id']='test-overflow';eight['collections'].append(e);p.write_text(json.dumps(eight))
   with self.assertRaises(ValidationError):load_collections()
  value=ENTRIES[0]['scenario'].value();value['domain']['filesystem']['/home/learner/snapshot.txt']['content']='x'*8193
  with self.assertRaises(ValidationError):load_portable(json.dumps(value).encode())
 def test_original_pack_engine_controller_and_vm_resources_byte_preservation(self):
  baseline='7638b284bd2f4cabb676f50d6da7d064ddae69c2'
  names=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline,'app/learning_lab'],cwd=ROOT.parent).decode().splitlines()
  for name in names:
   if name=='app/learning_lab/collections/index.json':continue
   old=subprocess.check_output(['git','show',baseline+':'+name],cwd=ROOT.parent)
   self.assertEqual((ROOT.parent/name).read_bytes(),old,name)
