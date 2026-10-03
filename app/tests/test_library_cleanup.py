"""Reversible Library choices in disposable profiles only."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios, ProfileLocks
from learning_lab.catalog import CatalogBridge
from learning_lab.collections import linux_fundamentals
from learning_lab.portable import load_portable
from learning_lab import profile_backup as pb
from learning_lab.library_state import validate

APP=QCoreApplication.instance() or QCoreApplication([])
ROOT=Path(__file__).resolve().parents[1]


class LibraryCleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='library-cleanup-tests-');self.root=Path(self.temp.name)
        self.data=self.root/'data';self.config=self.root/'config'
        self.data.mkdir();self.config.mkdir();self.bridges=[];self.locks=ProfileLocks(self.data,self.config)
        self.b=self.build()

    def build(self):
        b=CatalogBridge(load_bundled_scenarios()[0],self.data,self.config);b.profile_locks=self.locks
        self.bridges.append(b);return b

    def tearDown(self):
        for b in self.bridges:
            for lab in b.labs.values():lab.timer.stop()
        self.locks.unlock();self.temp.cleanup()

    def imported(self, version='1.0.0', identity='cleanup-service'):
        value=linux_fundamentals()[-1]['scenario'].value()
        value['identity']={'id':identity,'content_version':version}
        source=self.root/(identity+'-'+version+'.lab.json');source.write_text(json.dumps(value))
        self.assertTrue(self.b.importPack(str(source)),self.b.transfer_message)
        return load_portable(source.read_bytes()),source

    def data_bytes(self):return {str(p.relative_to(self.data)):p.read_bytes() for p in self.data.rglob('*.json')}

    def test_builtin_hide_show_and_restore_visibility_preserve_progress(self):
        b=self.b;b.edit('dns','unapplied');b.setCommandDraft('ping 10.20.0.10');b.hint();b.flush()
        before=self.data_bytes();key=b.view['fundamentals'][0]['labKey']
        self.assertTrue(b.setLibraryState('gateway-dns','hidden'))
        self.assertTrue(b.setLibraryState(key,'hidden'))
        self.assertEqual(len(b.view['visibleFundamentals']),5)
        self.assertEqual(len(b.view['fundamentals']),6)
        self.assertNotIn('gateway-dns',[r['labKey'] for r in b.view['otherLabs']])
        self.assertEqual(b.view['hiddenCount'],2);self.assertEqual(b.view['inactiveLabs'][0]['status'],'Learn: Not started · Challenge: Not started')
        self.assertEqual(self.data_bytes(),before)
        self.assertFalse(b.selectLab('gateway-dns'));self.assertEqual(b.session.attempt['draft'],{'dns':'unapplied'})
        self.assertTrue(b.restoreVisibility());self.assertEqual(b.view['hiddenCount'],0)
        self.assertFalse(b.repository.root.exists());self.assertEqual(self.data_bytes(),before)

    def test_remove_requires_confirmation_restore_and_completed_attempt(self):
        s,_=self.imported();b=self.b;b.selectLab(s.key)
        b.execute('mkdir /srv/site');b.execute('systemctl restart lab-web');b.submit();b.setCommandDraft('help');b.flush()
        self.assertEqual(b.view['grade']['score'],100)
        before=self.data_bytes();attempt=deepcopy(b.session.attempt)
        self.assertFalse(b.setLibraryState(s.key,'removed',False));self.assertEqual(b.view['removedCount'],0)
        self.assertTrue(b.setLibraryState(s.key,'removed',True))
        self.assertEqual(self.data_bytes(),before);self.assertNotIn(s.key,[r['labKey'] for r in b.view['otherLabs']])
        self.assertFalse(b.selectLab(s.key));self.assertEqual(b.session.attempt,attempt)
        self.assertFalse(b.view['canStartAttempt']);b.restart('Challenge');b.restart('Learn')
        self.assertEqual(b.session.attempt,attempt)
        self.assertEqual(b.view['commandDraft'],'help')
        self.assertTrue(any(r['labKey']==s.key for r in b.view['allHistory']))
        self.assertTrue(b.setLibraryState(s.key,'active'));self.assertTrue(b.view['canStartAttempt'])
        self.assertEqual(len([r for r in b.view['otherLabs'] if r['labKey']==s.key]),1)
        self.assertEqual(self.data_bytes(),before)
        b.restart('Challenge');self.assertNotEqual(b.session.attempt['id'],attempt['id'])
        self.assertTrue((b.store.archives/(attempt['id']+'.json')).exists())

    def test_reimport_removed_version_never_restores_or_duplicates(self):
        s,path=self.imported();b=self.b;b.selectLab(s.key);b.execute('pwd');b.flush()
        self.assertTrue(b.setLibraryState(s.key,'removed',True));before=self.data_bytes()
        for _ in range(3):self.assertTrue(b.importPack(str(path)))
        self.assertIn('Still removed',b.transfer_message);self.assertEqual(self.data_bytes(),before)
        self.assertEqual(len(b.portables),1);self.assertEqual(len(b.view['inactiveLabs']),1)
        for _ in range(3):self.assertTrue(b.setLibraryState(s.key,'active'))
        self.assertEqual(len(b.portables),1)

    def test_versions_and_builtin_import_overlap_are_independent(self):
        first,_=self.imported();second,_=self.imported('2.0.0');b=self.b
        self.assertTrue(b.setLibraryState(first.key,'removed',True))
        self.assertIn(second.key,[r['labKey'] for r in b.view['otherLabs']])
        entry=b.collection[0]['scenario'];source=self.root/'exact-builtin.lab.json';source.write_bytes(entry.original_bytes)
        self.assertTrue(b.setLibraryState(entry.key,'hidden'))
        self.assertTrue(b.importPack(str(source)))
        self.assertEqual(b.visibility.state(entry.key),'hidden')
        self.assertNotIn(entry.key,b.labs)  # Reimport must not create an inactive attempt.
        self.assertFalse(b.setLibraryState(entry.key,'removed',True))
        self.assertNotIn(entry.key,[r['labKey'] for r in b.view['otherLabs']])
        self.assertTrue(b.restoreVisibility());self.assertEqual(b.visibility.state(first.key),'removed')
        self.assertEqual(len([r for r in b.view['fundamentals'] if r['labKey']==entry.key]),1)

    def test_legacy_id_overlap_and_removed_builtin_version_conflict(self):
        from learning_lab.portable import portable_from_legacy
        b=self.b
        converted=portable_from_legacy(b.labs['gateway-dns'].pack)
        source=self.root/'gateway-copy.lab.json';source.write_bytes(converted.original_bytes)
        self.assertTrue(b.importPack(str(source)))
        self.assertTrue(b.setLibraryState('gateway-dns','hidden'))
        self.assertEqual(b.visibility.state(converted.key),'active')
        self.assertTrue(b.setLibraryState(converted.key,'removed',True))
        self.assertTrue(b.restoreVisibility())
        self.assertEqual(b.visibility.state('gateway-dns'),'active')
        self.assertEqual(b.visibility.state(converted.key),'removed')
        # Removing a conflicting import does not permit silent replacement by a
        # same-ID/version bundled pack; retained pinned content still owns it.
        builtin=b.collection[1]['scenario'];value=builtin.value();value['metadata']['title']='Reviewed custom title'
        source=self.root/'conflict.lab.json';source.write_text(json.dumps(value))
        custom=load_portable(source.read_bytes());self.assertTrue(b.importPack(str(source)))
        self.assertTrue(b.setLibraryState(custom.key,'removed',True))
        self.assertFalse(b.view['fundamentals'][1]['available'])
        self.assertFalse(b.selectLab(builtin.key));self.assertIn(custom.key,b.portables)

    def test_removed_completion_keeps_archived_history_and_draft_before_switch(self):
        s,_=self.imported();b=self.b;b.selectLab(s.key)
        b.execute('mkdir /srv/site');b.execute('systemctl restart lab-web');b.submit()
        old=b.session.attempt['id'];self.assertEqual(b.view['grade']['score'],100)
        b.restart('Challenge');b.edit('/etc/lab-web.conf','pending virtual-file draft');b.setCommandDraft('help');b.flush()
        before=self.data_bytes();b.setLibraryState(s.key,'removed',True)
        row=next(r for r in b.view['inactiveLabs'] if r['labKey']==s.key)
        self.assertEqual(row['status'],'Learn: Completed · Challenge: In progress')
        self.assertFalse(b.selectLab('gateway-dns'))
        self.assertTrue(b.selectLab('gateway-dns',True))
        self.assertFalse(b.selectLab(s.key));self.assertTrue(b.viewHistory(s.key))
        self.assertEqual(b.view['dirty'],True);self.assertEqual(b.view['commandDraft'],'help')
        self.assertTrue(any(r['id']==old and r['complete'] for r in b.view['history']))
        b.setLibraryState(s.key,'active')
        after=self.data_bytes()
        for name,raw in before.items():
            if not name.endswith('current.backup.json'):self.assertEqual(after[name],raw)

    def test_removed_same_version_conflicts_remain_rejected(self):
        s,path=self.imported();self.b.setLibraryState(s.key,'removed',True)
        before=self.data_bytes();value=s.value();value['metadata']['title']='Conflicting content'
        path.write_text(json.dumps(value));self.assertFalse(self.b.importPack(str(path)))
        self.assertEqual(self.data_bytes(),before);self.assertEqual(self.b.visibility.state(s.key),'removed')

    def test_collection_completion_remains_truthful_when_hidden(self):
        b=self.b;key=b.view['fundamentals'][2]['labKey'];b.selectLab(key)
        b.execute('chmod 600 notes.txt');b.execute('cat notes.txt');b.submit();b.restart('Challenge')
        expected=b.view['fundamentals'][2]['status']
        self.assertEqual(expected,'Learn: Completed · Challenge: Not started')
        self.assertTrue(b.setLibraryState(key,'hidden'))
        self.assertEqual(b.view['inactiveLabs'][0]['status'],expected)
        self.assertTrue(b.setLibraryState(key,'active'));self.assertEqual(b.view['fundamentals'][2]['status'],expected)

    def test_restart_preserves_removed_selection_drafts_and_history(self):
        s,_=self.imported();b=self.b;b.selectLab(s.key);b.execute('pwd');b.restart('Challenge')
        b.edit('/etc/lab-web.conf','draft text');b.setCommandDraft('ls');b.flush();b.setLibraryState(s.key,'removed',True)
        expected=deepcopy(b.session.attempt);history={p.name:p.read_bytes() for p in b.store.archives.glob('*.json')}
        fresh=self.build();self.assertEqual(fresh.view['labKey'],s.key)
        self.assertEqual(fresh.session.attempt,expected);self.assertEqual(fresh.view['commandDraft'],'ls')
        self.assertEqual(fresh.view['activeLibraryState'],'removed');self.assertFalse(fresh.view['canStartAttempt'])
        self.assertFalse(fresh.navigate(1));fresh.execute('help');self.assertEqual(fresh.session.attempt,expected)
        self.assertTrue(fresh.restoreAndResume(s.key,expected['id']));self.assertEqual(fresh.session.attempt,expected)
        self.assertEqual({p.name:p.read_bytes() for p in fresh.store.archives.glob('*.json')},history)

    def test_missing_current_removed_entry_does_not_create_attempt_until_restored(self):
        s,_=self.imported();b=self.b;b.setLibraryState(s.key,'removed',True)
        store=b.labs[s.key].store
        store.current.unlink();store.backup.unlink()  # Disposable damaged fixture only.
        fresh=self.build();self.assertNotIn(s.key,fresh.labs)
        self.assertFalse(fresh.selectLab(s.key));self.assertFalse(store.current.exists())
        self.assertTrue(fresh.setLibraryState(s.key,'active'));self.assertTrue(fresh.selectLab(s.key))
        self.assertTrue(store.current.exists())

    def test_failed_settings_write_and_bad_actions_preserve_files(self):
        s,_=self.imported();before=self.data_bytes()
        with patch('learning_lab.library_state.atomic_write',side_effect=OSError('fixture disk failure')):
            self.assertFalse(self.b.setLibraryState(s.key,'removed',True))
        self.assertEqual(self.b.visibility.state(s.key),'active');self.assertEqual(self.data_bytes(),before)
        for key,state in (('unknown','hidden'),('gateway-dns','removed'),(s.key,'hidden'),(s.key,'delete')):
            self.assertFalse(self.b.setLibraryState(key,state,True))
        self.assertEqual(self.data_bytes(),before)

    def test_unsupported_settings_preserved_and_backup_blocked(self):
        path=self.config/'library-state.json';raw=b'{"schema_version":999,"entries":{}}';path.write_bytes(raw)
        fresh=self.build();self.assertTrue(fresh.view['libraryChoicesReadOnly'])
        self.assertFalse(fresh.restoreVisibility());self.assertFalse(fresh.setLibraryState('gateway-dns','hidden'))
        self.assertFalse(fresh.backupProfile(str(self.root/'bad.llbackup')))
        self.assertEqual(path.read_bytes(),raw)

    def test_old_backup_v1_and_new_backup_v2_reopen_with_exact_choices(self):
        old=self.root/'old.llbackup';self.assertTrue(self.b.backupProfile(str(old)))
        self.assertEqual(pb.read_backup(old).manifest['schema_version'],1)
        pb.restore(pb.read_backup(old),self.root/'old-restored',confirmed=True)
        self.assertFalse((self.root/'old-restored/config/library-state.json').exists())
        s,_=self.imported();b=self.b;b.selectLab(s.key);b.execute('pwd');b.submit();b.restart('Challenge')
        b.edit('/etc/lab-web.conf','saved unapplied draft');b.setCommandDraft('help');b.flush()
        b.setLibraryState(s.key,'removed',True);b.setLibraryState(b.collection[0]['scenario'].key,'hidden')
        path=self.root/'new.llbackup';self.assertTrue(b.backupProfile(str(path)),b.transfer_message)
        backup=pb.read_backup(path);self.assertEqual(backup.manifest['schema_version'],2)
        restored=self.root/'new-restored';pb.restore(backup,restored,confirmed=True)
        self.assertEqual((restored/'config/library-state.json').read_bytes(),b.visibility.path.read_bytes())
        for name,raw in backup.files.items():self.assertEqual((restored/name).read_bytes(),raw)
        expected={'entries':b.visibility.entries,'attempt':b.session.attempt,'key':s.key}
        (self.root/'expected.json').write_text(json.dumps(expected))
        probe='''
import sys,json
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
app=QCoreApplication([]);r=Path(sys.argv[1]);e=json.loads(Path(sys.argv[2]).read_text())
b=CatalogBridge(load_bundled_scenarios()[0],r/'data',r/'config')
assert b.visibility.entries==e['entries']
assert b.session.attempt==e['attempt'] and b.view['labKey']==e['key']
assert b.view['commandDraft']=='help' and not b.view['canStartAttempt']
assert not b.selectLab(e['key'])
assert not b.navigate(1)
b.restart('Challenge');assert b.session.attempt==e['attempt']
assert b.restoreAndResume(e['key'],e['attempt']['id'])
assert b.session.attempt==e['attempt'] and b.view['canStartAttempt']
print('restored choices and pinned attempt resume PASS')
'''
        result=subprocess.run([sys.executable,'-B','-c',probe,str(restored),str(self.root/'expected.json')],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_inactive_backend_routes_blocked_for_hidden_and_removed(self):
        s,_=self.imported();b=self.b
        for key,state in (('gateway-dns','hidden'),(s.key,'removed')):
            self.assertTrue(b.selectLab(key,True))
            b.setCommandDraft('pending');b.flush();expected=deepcopy(b.session.attempt)
            self.assertTrue(b.setLibraryState(key,state,True));before=self.data_bytes()
            self.assertEqual(b.page,0);self.assertFalse(b.selectLab(key,True));self.assertFalse(b.navigate(1))
            for action in (lambda:b.execute('help'),lambda:b.setCommandDraft('lost'),lambda:b.edit('dns','lost'),b.apply,b.test,b.hint,b.submit,
                           lambda:b.restart('Challenge'),b.addRule,b.removeRule,lambda:b.moveRule(1),lambda:b.editDefault('allow'),lambda:b.editRule('action','allow')):
                action()
            self.assertEqual(b.session.attempt,expected);self.assertEqual(b.view['commandDraft'],'pending')
            self.assertEqual(self.data_bytes(),before)
            self.assertTrue(b.viewHistory(key));self.assertEqual(b.page,2);self.assertEqual(b.visibility.state(key),state)
            self.assertTrue(b.setLibraryState(key,'active'));self.assertEqual(b.page,2)
            self.assertEqual(b.session.attempt,expected);self.assertTrue(b.selectLab(key));self.assertTrue(b.view['canStartAttempt'])

    def test_restore_resume_exact_current_among_multiple_history_records_and_versions(self):
        first,_=self.imported();second,_=self.imported('2.0.0');b=self.b
        for key,state in ((first.key,'removed'),('gateway-dns','hidden')):
            b.selectLab(key,True);ended=[]
            for mode in ('Challenge','Learn','Challenge'):
                ended.append(b.session.attempt['id']);b.restart(mode)
            b.setCommandDraft('pending');b.hint();b.flush();expected=deepcopy(b.session.attempt)
            b.setLibraryState(key,state,True);before=self.data_bytes()
            choices=b.resumableAttempts(key)
            self.assertEqual([r['id'] for r in choices],[expected['id']])
            self.assertEqual(choices[0]['mode'],'Challenge')
            for attempt_id in ended+['stale-selection']:
                self.assertFalse(b.restoreAndResume(key,attempt_id,True));self.assertEqual(b.visibility.state(key),state)
            self.assertTrue(b.restoreAndResume(key,expected['id'],True))
            self.assertEqual(b.page,1);self.assertEqual(b.session.attempt,expected);self.assertEqual(b.view['commandDraft'],'pending')
            self.assertEqual(self.data_bytes(),before);self.assertTrue(b.view['canStartAttempt'])
            self.assertEqual(b.visibility.state(second.key),'active')
            self.assertTrue(b.restoreAndResume(key,expected['id'],True))  # Already restored/open is safe.
            self.assertEqual(b.session.attempt,expected)

    def test_restore_without_launch_and_restart_preserve_inactive_other_version(self):
        first,_=self.imported();second,_=self.imported('2.0.0');b=self.b
        b.selectLab(first.key);b.execute('pwd');b.setCommandDraft('help');b.flush();expected=deepcopy(b.session.attempt)
        b.setLibraryState(first.key,'removed',True);b.setLibraryState(second.key,'removed',True)
        b.selectLab('gateway-dns');b.navigate(0)
        self.assertTrue(b.setLibraryState(first.key,'active'))
        self.assertEqual(b.view['labKey'],'gateway-dns');self.assertEqual(b.page,0)
        fresh=self.build();self.assertEqual(fresh.view['labKey'],'gateway-dns')
        self.assertEqual(fresh.visibility.state(first.key),'active');self.assertEqual(fresh.visibility.state(second.key),'removed')
        self.assertTrue(fresh.selectLab(first.key));self.assertEqual(fresh.session.attempt,expected);self.assertEqual(fresh.view['commandDraft'],'help')

    def test_stale_resume_after_reset_and_restore_write_failure(self):
        s,_=self.imported();b=self.b;b.selectLab(s.key);old=b.session.attempt['id']
        b.restart('Learn');current=deepcopy(b.session.attempt);b.setLibraryState(s.key,'removed',True)
        self.assertFalse(b.restoreAndResume(s.key,old));self.assertEqual(b.visibility.state(s.key),'removed')
        with patch('learning_lab.library_state.atomic_write',side_effect=OSError('fixture write failure')):
            self.assertFalse(b.restoreAndResume(s.key,current['id']))
        self.assertEqual(b.session.attempt,current);self.assertEqual(b.visibility.state(s.key),'removed');self.assertEqual(b.page,0)

    def test_restore_resume_saves_other_lab_drafts_only_with_confirmation(self):
        s,_=self.imported();b=self.b;current=deepcopy(b.labs[s.key].session.attempt)
        b.setLibraryState(s.key,'removed',True);b.edit('dns','keep me')
        self.assertFalse(b.restoreAndResume(s.key,current['id']));self.assertEqual(b.visibility.state(s.key),'removed')
        self.assertTrue(b.restoreAndResume(s.key,current['id'],True));self.assertEqual(b.session.attempt,current)
        self.assertEqual(b.labs['gateway-dns'].session.attempt['draft'],{'dns':'keep me'})

    def test_backup_schema_and_settings_reference_rejection(self):
        self.b.setLibraryState('gateway-dns','hidden');path=self.root/'new.llbackup'
        self.assertTrue(self.b.backupProfile(str(path)))
        with ZipFile(path) as z:files={n:z.read(n) for n in z.namelist()}
        manifest=json.loads(files['manifest.json']);manifest['schema_version']=1;files['manifest.json']=json.dumps(manifest).encode()
        with ZipFile(path,'w') as z:
            for name,raw in files.items():z.writestr(name,raw)
        with self.assertRaises(ValueError):pb.read_backup(path)
        for value in ({'schema_version':1,'entries':{'pack:'+'a'*64:'removed'}},
                      {'schema_version':1,'entries':{'gateway-dns':'removed'}},
                      {'schema_version':True,'entries':{}}):
            with self.assertRaises(ValueError):validate(value,{'gateway-dns'},set())
