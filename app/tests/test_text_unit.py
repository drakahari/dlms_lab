"""Eight text packs, lifecycle and compatibility; all profiles disposable."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios, ProfileLocks
from learning_lab.catalog import CatalogBridge
from learning_lab.collections import load_collections
from learning_lab.portable import load_portable
from learning_lab.domain.validation import ValidationError
from learning_lab.linux_text.engine import guide
from learning_lab import profile_backup as pb

APP=QCoreApplication.instance() or QCoreApplication([]);ROOT=Path(__file__).resolve().parents[1];H='/home/learner'
ENTRIES=load_collections()[3]['entries']
IDS=['linux-log-slices','linux-text-events','linux-text-counts','linux-text-deduplicate','linux-text-fields','linux-text-pipeline','linux-text-report','linux-text-handover']
ALTERNATIVES=[
 ['tail -n 2 ./events.log','head -n 2 /home/learner/events.log'],
 ["grep -F 'a.b' ./events.log","grep -F 'ERROR' /home/learner/events.log"],
 ['cat note.txt | wc -c','wc -w ./note.txt','wc -l /home/learner/note.txt'],
 ['uniq ./names.txt','cat names.txt | sort | uniq -c'],
 ["cut -d '|' -f 3 ./people.txt",'cut -d "|" -f 2 /home/learner/people.txt'],
 ['cut -d "|" -f 1 checks.txt | sort | uniq','grep -F "|ok" ./checks.txt | cut -d "|" -f 1 | uniq | sort'],
 ['cat part1.txt > append.txt','cat part2.txt >> append.txt','cat part1.txt > overwrite.txt','cat append.txt','cat overwrite.txt'],
 ['grep -F "|fail" checks.txt | sort | cut -d "|" -f 1 | uniq > failed-sites.txt','cat failed-sites.txt | wc -l > count.txt',
  'grep -F "|fail" ./checks.txt | sort | cut -d "|" -f 1 | uniq','cat count.txt','cat failed-sites.txt']]
# Sorting complete selected records also groups the repeated beta entries.

def finish(s):
    for _ in range(64):
        if s.engine.grade()['complete']:return
        s.execute(guide(s.pack,s.attempt['applied'])['command'])
    raise AssertionError('Learn route failed.')

class TextUnitTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory(prefix='text-unit-');self.root=Path(self.temp.name);self.bridges=[];self.locks=[]
    def tearDown(self):
        for b in self.bridges:
            for l in b.labs.values():l.timer.stop()
        for lock in self.locks:lock.unlock()
        self.temp.cleanup()
    def build(self,name='profile'):
        root=self.root/name;(root/'config').mkdir(parents=True,exist_ok=True)
        b=CatalogBridge(load_bundled_scenarios()[0],root/'data',root/'config');self.bridges.append(b);return b
    def test_order_identity_lazy_profile_and_contract(self):
        b=self.build();self.assertFalse(b.repository.root.exists());self.assertEqual(len(b.curated),38)
        self.assertEqual([e['scenario'].identity.scenario_id for e in ENTRIES],IDS)
        self.assertEqual(b.view['collections'][3]['total'],8);self.assertEqual(b.view['collections'][3]['completed'],{'Learn':0,'Challenge':0})
        for e in ENTRIES:self.assertEqual(e['scenario'].pin['engine']['contract_version'],5)
    def test_all_learn_steps_hints_and_equivalent_challenge(self):
        for i,e in enumerate(ENTRIES):
            with self.subTest(lab=IDS[i]):
                s=e['scenario'].domain().session();s.hint();finish(s);self.assertEqual(s.submit()['score'],100)
                self.assertEqual(s.attempt['hints'],1);s=e['scenario'].domain().session(mode='Challenge')
                self.assertEqual(s.domain.view_state(s,None,0)['guide'],{})
                with self.assertRaises(ValidationError):s.hint()
                for cmd in ALTERNATIVES[i]:s.execute(cmd)
                self.assertEqual(s.submit()['score'],100,s.attempt['console'])
    def test_wrong_results_tool_evidence_not_merely_reading_or_lessons(self):
        for i in range(6):
            s=ENTRIES[i]['scenario'].domain().session();source=next(p for p,n in s.attempt['applied']['filesystem'].items() if n['kind']=='file')
            s.execute('help');s.test();s.execute('cat '+source);self.assertEqual(s.submit()['score'],0)
        s=ENTRIES[2]['scenario'].domain().session();s.execute('wc -w note.txt');self.assertEqual(s.submit()['score'],30)
        s=ENTRIES[3]['scenario'].domain().session();s.execute('sort names.txt');self.assertEqual(s.submit()['score'],0)
        s=ENTRIES[5]['scenario'].domain().session();s.execute('cut -d "|" -f 1 checks.txt | sort | uniq');self.assertEqual(s.submit()['score'],0)
    def test_report_wrong_append_and_nontransactional_failure(self):
        s=ENTRIES[6]['scenario'].domain().session();finish(s);self.assertEqual(s.submit()['score'],100)
        s.execute('cat part2.txt >> append.txt');self.assertEqual(s.submit()['score'],30)
        s.execute('cat missing > overwrite.txt');self.assertEqual(s.attempt['applied']['filesystem'][H+'/overwrite.txt']['content'],'')
        self.assertEqual(s.submit()['score'],0)
    def test_capstone_final_state_and_fresh_verification(self):
        s=ENTRIES[7]['scenario'].domain().session();finish(s);self.assertEqual(s.submit()['score'],100)
        s.execute('cat failed-sites.txt > count.txt');self.assertEqual(s.submit()['score'],35)
        s.execute('cat failed-sites.txt | wc -l > count.txt');self.assertEqual(s.submit()['score'],50)
        for cmd in ALTERNATIVES[7][2:]:s.execute(cmd)
        self.assertEqual(s.submit()['score'],100)
        s.execute('cat missing > failed-sites.txt');self.assertEqual(s.submit()['score'],25)
    def test_reset_modes_restart_and_command_drafts_all_eight(self):
        b=self.build()
        for i,e in enumerate(ENTRIES):
            b.selectLab(e['scenario'].key,True);initial=deepcopy(b.session.attempt['applied']);finish(b.session);b.submit();first=b.session.attempt['id']
            b.restart('Challenge');self.assertEqual(b.session.attempt['applied'],initial)
            self.assertIn(first,[a['id'] for a in b.store.history(b.session.attempt['id'])[0]])
            for cmd in ALTERNATIVES[i]:b.execute(cmd)
            b.submit();b.setCommandDraft('help');b.flush()
        before={k:deepcopy(l.session.attempt) for k,l in b.labs.items()};new=self.build()
        self.assertEqual({k:l.session.attempt for k,l in new.labs.items()},before)
        self.assertEqual(new.view['collections'][3]['completed'],{'Learn':8,'Challenge':8});self.assertEqual(new.view['commandDraft'],'help')
    def test_scenario_history_export_reimport_and_old_version_pins(self):
        b=self.build()
        for e in ENTRIES:
            lab=e['scenario'];b.selectLab(lab.key,True);finish(b.session);b.submit();b.flush();prior=deepcopy(b.session.attempt)
            path=self.root/(lab.identity.scenario_id+'.json');self.assertTrue(b.exportScenario(str(path)));self.assertEqual(path.read_bytes(),lab.original_bytes)
            self.assertTrue(b.importPack(str(path)));self.assertEqual(b.session.attempt,prior)
            history=self.root/(lab.identity.scenario_id+'.history.json');self.assertTrue(b.exportAttempt(str(history),prior['id']))
            self.assertEqual(json.loads(history.read_text())['provenance'],'Pinned in record')
            other=self.build(lab.identity.scenario_id);self.assertTrue(other.importPack(str(path)));other.selectLab(lab.key,True);finish(other.session);other.submit()
            self.assertEqual(other.view['grade']['score'],100)
        lab=ENTRIES[-1]['scenario'];v=lab.value();v['identity']['content_version']='0.9.0';old,_=b.repository.install(json.dumps(v).encode());b._add_portable(old)
        b.selectLab(old.key,True);b.execute('pwd');b.flush();prior=deepcopy(b.session.attempt);b.selectLab(lab.key,True)
        self.assertEqual(self.build().labs[old.key].session.attempt,prior)
    def test_backup_visibility_and_restart_preserve_all_state(self):
        b=self.build();lock=ProfileLocks(b.data_root,b.config_root);b.profile_locks=lock;self.locks.append(lock)
        for e in ENTRIES:b.selectLab(e['scenario'].key,True);finish(b.session);b.submit();b.setCommandDraft('wc -l');b.flush()
        b.setLibraryState(ENTRIES[0]['scenario'].key,'hidden');before={k:deepcopy(l.session.attempt) for k,l in b.labs.items()}
        path=self.root/'snapshot.llbackup';self.assertTrue(b.backupProfile(str(path)),b.transfer_message)
        pb.restore(pb.read_backup(path),self.root/'restored',confirmed=True);new=self.build('restored')
        self.assertEqual({k:l.session.attempt for k,l in new.labs.items()},before);self.assertEqual(new.visibility.entries,b.visibility.entries)
        self.assertEqual(new.view['commandDraft'],'wc -l');self.assertEqual(new.view['collections'][3]['completed'],{'Learn':8,'Challenge':0})
    def test_imported_text_inert_validation_has_no_profile_writes(self):
        b=self.build();v=ENTRIES[0]['scenario'].value();v['identity']['id']='authored-text-proof';v['metadata']['title']='__import__("os").system("bad")'
        path=self.root/'authored.json';path.write_text(json.dumps(v));before={p:p.read_bytes() for p in (self.root/'profile').rglob('*') if p.is_file()}
        self.assertTrue(b.authoring.validateLab(str(path)),b.authoring.message);self.assertEqual(before,{p:p.read_bytes() for p in (self.root/'profile').rglob('*') if p.is_file()})
        self.assertTrue(b.authoring.importValidated());s=load_portable(path.read_bytes());b.selectLab(s.key,True);finish(b.session);b.submit();self.assertEqual(b.view['grade']['score'],100)
    def baseline_source(self):
        old=self.root/'baseline';baseline='f9bbb91e65f0701ee7021093d9946d5aa53201ba'
        for name in subprocess.check_output(['git','ls-tree','-r','--name-only',baseline,'app/learning_lab'],cwd=ROOT.parent).decode().splitlines():
            p=old/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(subprocess.check_output(['git','show',baseline+':'+name],cwd=ROOT.parent))
        return old/'app'
    def test_baseline_contracts_1_to_4_resume_byte_unchanged(self):
        old=self.baseline_source();profile=self.root/'profile';probe='''
import json,sys
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.portable import load_portable
app=QCoreApplication([]);p=Path(sys.argv[1]);(p/'config').mkdir(parents=True)
b=CatalogBridge(load_bundled_scenarios()[0],p/'data',p/'config')
for name in ('linux-file-navigation','linux-file-permissions','linux-directory-permissions','linux-deliver-workspace'):
 source=Path('learning_lab/collections/packs')/(name+'.lab.json');s=load_portable(source.read_bytes());assert b.importPack(str(source.resolve()));b.selectLab(s.key,True);b.execute('pwd');b.restart('Challenge');b.execute('pwd');b.setCommandDraft('help');b.flush()
(p/'expected.json').write_text(json.dumps({k:l.session.attempt for k,l in b.labs.items()}))
for l in b.labs.values():l.timer.stop()
'''
        r=subprocess.run(['python3','-B','-c',probe,str(profile)],cwd=old,env={**os.environ,'PYTHONPATH':str(old)},capture_output=True,text=True,timeout=30);self.assertEqual(r.returncode,0,r.stderr)
        before={p:p.read_bytes() for d in (profile/'data',profile/'config') for p in d.rglob('*.json')};b=self.build()
        self.assertEqual({k:l.session.attempt for k,l in b.labs.items()},json.loads((profile/'expected.json').read_text()))
        for p,data in before.items():self.assertEqual(p.read_bytes(),data)
    def test_baseline_backup_reader_rejects_contract5_before_activation(self):
        old=self.baseline_source();b=self.build();lock=ProfileLocks(b.data_root,b.config_root);b.profile_locks=lock;self.locks.append(lock)
        b.selectLab(ENTRIES[-1]['scenario'].key,True);finish(b.session);b.submit();path=self.root/'new.llbackup';self.assertTrue(b.backupProfile(str(path)))
        probe='''
import sys
from pathlib import Path
from learning_lab import profile_backup as pb
try:pb.restore(pb.read_backup(Path(sys.argv[1])),Path(sys.argv[2]),confirmed=True)
except ValueError as e:assert 'contract' in str(e),str(e)
else:raise AssertionError('Old app accepted unknown contract')
assert not Path(sys.argv[2]).exists()
'''
        r=subprocess.run(['python3','-B','-c',probe,str(path),str(self.root/'reject')],cwd=old,env={**os.environ,'PYTHONPATH':str(old)},capture_output=True,text=True,timeout=30);self.assertEqual(r.returncode,0,r.stderr)
