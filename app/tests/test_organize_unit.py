"""Six-pack learning, compatibility and lifecycle proof in disposable profiles."""
from copy import deepcopy
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
from learning_lab import profile_backup as pb
from learning_lab.linux_navigation.file_management import guide as management_guide
from learning_lab.linux_navigation.engine import guide as navigation_guide
from learning_lab.domain.validation import ValidationError

APP=QCoreApplication.instance() or QCoreApplication([])
ROOT=Path(__file__).resolve().parents[1]
ENTRIES=load_collections()[2]['entries']
IDS=['linux-file-locations','linux-prepare-workspace','linux-copy-reference','linux-organize-report','linux-find-handover','linux-deliver-workspace']
H='/home/learner'
ALTERNATIVES=[
 ['cat todo.txt','cat /var/log/web.log','ls /var/log/.','cat /etc/./web.conf'],
 ['mkdir -p ./Workshop/drafts','cd ./Workshop'],
 ['cp -n /opt/reference/worksheet.txt .','cat ./worksheet.txt'],
 ['cp -n inbox/draft.txt Reports/report.txt','rm inbox/draft.txt','cat Reports/./report.txt'],
 ['cd Projects/site','find . -name handover.txt -type f','cat docs/../docs/handover.txt'],
 ['mkdir Delivery','cp -n incoming/brief.txt Delivery','mv -n Delivery/brief.txt Delivery/intermediate.txt','mv -n Delivery/intermediate.txt Delivery/brief.txt',
  'rm scratch/temporary.txt','rmdir scratch','find ./Delivery -type f','cat Delivery/brief.txt','cd Delivery']]


def finish(session):
    g=navigation_guide if session.domain.pack['domain']['schema_version']==1 else management_guide
    for _ in range(64):
        if session.engine.grade()['complete']:return
        session.execute(g(session.pack,session.attempt['applied'])['command'])
    raise AssertionError('Guided route did not complete.')


class OrganizeUnitTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.bridges=[];self.locks=[]
    def tearDown(self):
        for b in self.bridges:
            for lab in b.labs.values():lab.timer.stop()
        for lock in self.locks:lock.unlock()
        self.temp.cleanup()
    def build(self,name='profile'):
        data=self.root/name/'data';config=self.root/name/'config';config.mkdir(parents=True,exist_ok=True)
        b=CatalogBridge(load_bundled_scenarios()[0],data,config);self.bridges.append(b);return b

    def test_order_resources_titles_contracts_and_fresh_lazy_profile(self):
        self.assertEqual([e['scenario'].identity.scenario_id for e in ENTRIES],IDS)
        self.assertEqual([e['scenario'].pin['engine']['contract_version'] for e in ENTRIES],[1,4,4,4,4,4])
        b=self.build();self.assertEqual(len(b.view['collections']),4);self.assertEqual(len(b.labs),3)
        self.assertFalse(b.repository.root.exists());rows=b.view['collections'][2]['rows']
        self.assertEqual([r['action'] for r in rows],['Start']*6);self.assertEqual(b.view['collections'][2]['completed'],{'Learn':0,'Challenge':0})

    def test_all_learn_steps_hints_and_challenge_equivalent_solutions(self):
        for i,entry in enumerate(ENTRIES):
            lab=entry['scenario'];s=lab.domain().session();s.hint();self.assertEqual(s.attempt['hints'],1);finish(s)
            self.assertEqual(s.submit()['score'],100);self.assertEqual(s.attempt['hints'],1)
            challenge=lab.domain().session(mode='Challenge')
            self.assertEqual(challenge.domain.view_state(challenge,None,0)['guide'],{})
            with self.assertRaises(ValidationError):challenge.hint()
            for command in ALTERNATIVES[i]:challenge.execute(command)
            self.assertEqual(challenge.submit()['score'],100,(i,challenge.attempt['console']))

    def test_location_outcome_requires_inspection_at_each_correct_path(self):
        s=ENTRIES[0]['scenario'].domain().session();self.assertEqual(s.submit()['score'],10)
        s.execute('help');s.test();s.execute('cat /home/learner/todo.txt');self.assertEqual(s.submit()['score'],35)
        s.execute('ls /etc');self.assertEqual(s.submit()['score'],35)
        s.execute('cat /etc/web.conf');s.execute('cat /var/log/web.log');self.assertEqual(s.submit()['score'],85)
        s.execute('ls /var/log');self.assertEqual(s.submit()['score'],100)
        s.execute('cd /');self.assertEqual(s.submit()['score'],90)

    def test_wrong_repairs_and_missing_verification(self):
        s=ENTRIES[1]['scenario'].domain().session();s.execute('mkdir Wrong');self.assertEqual(s.submit()['score'],0)
        s=ENTRIES[2]['scenario'].domain().session();s.execute('cat /opt/reference/worksheet.txt');self.assertEqual(s.submit()['score'],20)
        s.execute('cp -n /opt/reference/worksheet.txt worksheet.txt');self.assertEqual(s.submit()['score'],80)
        s=ENTRIES[3]['scenario'].domain().session();s.execute('cp -n inbox/draft.txt Reports/report.txt');s.execute('cat Reports/report.txt');self.assertEqual(s.submit()['score'],65)
        s=ENTRIES[4]['scenario'].domain().session();s.execute('cat Projects/site/docs/handover.txt');self.assertEqual(s.submit()['score'],50)
        s.execute('find Projects -name absent');self.assertEqual(s.submit()['score'],50)
        s=ENTRIES[5]['scenario'].domain().session();s.execute('rmdir scratch');self.assertIn('not empty','\n'.join(s.attempt['console']))
        s.execute('rm -rf scratch');self.assertIn('Unsupported','\n'.join(s.attempt['console']))

    def test_final_assessment_evidence_invalidated_and_final_state_independent_of_route(self):
        s=ENTRIES[5]['scenario'].domain().session();finish(s);self.assertEqual(s.submit()['score'],100)
        s.execute('mkdir extra');self.assertEqual(s.submit()['score'],65)
        s.execute('cat brief.txt');s.execute('find . -type f -name brief.txt');self.assertEqual(s.submit()['score'],100)
        s.execute('mv -n brief.txt wrong.txt');self.assertLess(s.submit()['score'],100)
        s.execute('mv -n wrong.txt brief.txt');self.assertEqual(s.submit()['score'],65)
        s.execute('find .');s.execute('cat ./brief.txt');self.assertEqual(s.submit()['score'],100)

    def test_reset_mode_history_and_same_profile_restart_all_six(self):
        b=self.build()
        for entry in ENTRIES:
            key=entry['scenario'].key;self.assertTrue(b.selectLab(key,True));initial=deepcopy(b.session.attempt['applied'])
            finish(b.session);b.submit();first=b.session.attempt['id'];b.restart('Challenge')
            self.assertEqual(b.session.attempt['applied'],initial);self.assertIn(first,[r['id'] for r in b.store.history(b.session.attempt['id'])[0]])
            for command in ALTERNATIVES[IDS.index(entry['scenario'].identity.scenario_id)]:b.execute(command)
            b.submit();b.setCommandDraft('help');b.flush()
        expected={k:deepcopy(l.session.attempt) for k,l in b.labs.items()};counts=b.view['collections'][2]['completed']
        self.assertEqual(counts,{'Learn':6,'Challenge':6});new=self.build()
        self.assertEqual({k:l.session.attempt for k,l in new.labs.items()},expected);self.assertEqual(new.view['commandDraft'],'help')
        self.assertEqual(new.view['collections'][2]['completed'],counts)

    def test_scenario_export_reimport_history_export_and_pin_independence(self):
        b=self.build()
        for entry in ENTRIES:
            s=entry['scenario'];b.selectLab(s.key,True);finish(b.session);b.submit();b.flush();before=deepcopy(b.session.attempt)
            path=self.root/(s.identity.scenario_id+'.lab.json');self.assertTrue(b.exportScenario(str(path)))
            self.assertEqual(path.read_bytes(),s.original_bytes);self.assertTrue(b.importPack(str(path)));self.assertEqual(b.session.attempt,before)
            history=self.root/(s.identity.scenario_id+'.history.json');self.assertTrue(b.exportAttempt(str(history),before['id']))
            self.assertEqual(json.loads(history.read_text())['provenance'],'Pinned in record')
            other=self.build('reimport-'+s.identity.scenario_id);self.assertTrue(other.importPack(str(path)));other.selectLab(s.key,True)
            self.assertEqual(other.session.attempt['applied'],s.domain().session().attempt['applied'])
            self.assertNotEqual(other.session.attempt['id'],before['id'])
        s=ENTRIES[-1]['scenario'];value=s.value();value['identity']['content_version']='0.9.0'
        old,_=b.repository.install(json.dumps(value).encode());b._add_portable(old);b.selectLab(old.key,True);b.execute('pwd');b.flush();prior=deepcopy(b.session.attempt)
        b.selectLab(s.key,True);new=self.build();self.assertEqual(new.labs[old.key].session.attempt,prior);self.assertNotEqual(old.pin,s.pin)

    def test_backup_restore_preserves_all_states_pins_workspace_and_visibility(self):
        b=self.build();lock=ProfileLocks(b.data_root,b.config_root);self.locks.append(lock);b.profile_locks=lock
        for entry in ENTRIES:
            b.selectLab(entry['scenario'].key,True);finish(b.session);b.submit();b.setCommandDraft('help');b.flush()
        hidden=ENTRIES[1]['scenario'].key;b.setLibraryState(hidden,'hidden')
        before={k:deepcopy(l.session.attempt) for k,l in b.labs.items()}
        archive=self.root/'profile.llbackup';self.assertTrue(b.backupProfile(str(archive)),b.transfer_message)
        backup=pb.read_backup(archive);self.assertEqual(backup.manifest['schema_version'],2)
        pb.restore(backup,self.root/'restored',confirmed=True);restored=self.build('restored')
        self.assertEqual({k:l.session.attempt for k,l in restored.labs.items()},before)
        self.assertEqual(restored.visibility.entries,b.visibility.entries);self.assertEqual(restored.view['commandDraft'],'help')
        self.assertEqual(restored.view['collections'][2]['completed'],{'Learn':6,'Challenge':0})

    def test_validation_does_not_install_and_script_text_is_inert_data(self):
        b=self.build();value=ENTRIES[2]['scenario'].value();value['identity']['id']='authored-copy-proof'
        value['domain']['filesystem']['/opt/reference/worksheet.txt']['content']='__import__("os").system("bad")\n'
        path=self.root/'authored.lab.json';path.write_text(json.dumps(value))
        before={str(p):p.read_bytes() for folder in (b.data_root,b.config_root) for p in folder.rglob('*') if p.is_file()}
        self.assertTrue(b.authoring.validateLab(str(path)),b.authoring.message)
        self.assertEqual(before,{str(p):p.read_bytes() for folder in (b.data_root,b.config_root) for p in folder.rglob('*') if p.is_file()})
        self.assertTrue(b.authoring.importValidated());s=load_portable(path.read_bytes());b.selectLab(s.key,True);finish(b.session)
        b.submit();self.assertEqual(b.view['grade']['score'],100);self.assertIn('__import__','\n'.join(b.session.attempt['console']))

    def previous_source(self):
        destination=self.root/'baseline/app';baseline='c46ad12f36d554ab79d8f45b0077ef0c638d43cb'
        names=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline,'app/learning_lab'],cwd=ROOT.parent).decode().splitlines()
        for name in names:
            path=self.root/'baseline'/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(subprocess.check_output(['git','show',baseline+':'+name],cwd=ROOT.parent))
        return destination

    def test_actual_baseline_pinned_records_reopen_byte_unchanged(self):
        previous=self.previous_source();profile=self.root/'profile'
        probe='''
import json,sys
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.portable import load_portable
app=QCoreApplication([]);root=Path(sys.argv[1]);config=root/'config';config.mkdir(parents=True)
b=CatalogBridge(load_bundled_scenarios()[0],root/'data',config)
for name in ('linux-file-navigation','linux-file-permissions','linux-directory-permissions'):
 source=Path('learning_lab/collections/packs')/(name+'.lab.json');scenario=load_portable(source.read_bytes())
 assert b.importPack(str(source.resolve()));assert b.selectLab(scenario.key,True)
 b.execute('pwd');b.restart('Challenge');b.execute('pwd');b.setCommandDraft('help');b.flush()
(root/'expected.json').write_text(json.dumps({k:l.session.attempt for k,l in b.labs.items()}))
for l in b.labs.values():l.timer.stop()
'''
        result=subprocess.run(['python3','-B','-c',probe,str(profile)],cwd=previous,env={**os.environ,'PYTHONPATH':str(previous)},capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        before={p:p.read_bytes() for folder in (profile/'data',profile/'config') for p in folder.rglob('*.json')}
        new=self.build();expected=json.loads((profile/'expected.json').read_text())
        self.assertEqual({k:l.session.attempt for k,l in new.labs.items()},expected)
        for path,raw in before.items():self.assertEqual(path.read_bytes(),raw)
        self.assertEqual(new.view['commandDraft'],'help')

    def test_previous_reader_rejects_new_contract_backup_before_activation(self):
        previous=self.previous_source();b=self.build();lock=ProfileLocks(b.data_root,b.config_root);self.locks.append(lock);b.profile_locks=lock
        b.selectLab(ENTRIES[-1]['scenario'].key,True);finish(b.session);b.submit();b.flush()
        archive=self.root/'new-contract.llbackup';self.assertTrue(b.backupProfile(str(archive)))
        probe='''
import sys
from pathlib import Path
from learning_lab import profile_backup as pb
archive=Path(sys.argv[1]);destination=Path(sys.argv[2])
try:pb.restore(pb.read_backup(archive),destination,confirmed=True)
except ValueError as exc:
 assert 'contract' in str(exc),str(exc)
else:raise AssertionError('Previous app accepted new contract')
assert not destination.exists()
print('Previous reader safely rejects unavailable contract; no partial restore.')
'''
        result=subprocess.run(['python3','-B','-c',probe,str(archive),str(self.root/'old-restore')],cwd=previous,env={**os.environ,'PYTHONPATH':str(previous)},capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
