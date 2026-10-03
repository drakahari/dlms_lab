"""Multiple collections organize exact scenarios; disposable profiles only."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios, ProfileLocks
from learning_lab.catalog import CatalogBridge
from learning_lab.collections import load_collections, linux_fundamentals
from learning_lab.portable import load_portable
from learning_lab import profile_backup as pb
from learning_lab.library_state import validate
from learning_lab.domain.validation import ValidationError

APP = QCoreApplication.instance() or QCoreApplication([])
ROOT = Path(__file__).resolve().parents[1]
IDS = ['linux-file-navigation', 'linux-file-permissions', 'linux-directory-permissions',
       'linux-private-note', 'linux-search-only-directory', 'linux-archive-access']


class LpicCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.catalogs = []; self.locks = []

    def tearDown(self):
        for b in self.catalogs:
            for lab in b.labs.values(): lab.timer.stop()
        for lock in self.locks: lock.unlock()
        self.temp.cleanup()

    def build(self, name='profile', old=False):
        data = self.root/name/'data'; config = self.root/name/'config'
        config.mkdir(parents=True, exist_ok=True)
        if old:
            with patch('learning_lab.catalog.load_collections', return_value=load_collections()[:1]):
                b = CatalogBridge(load_bundled_scenarios()[0], data, config)
        else: b = CatalogBridge(load_bundled_scenarios()[0], data, config)
        self.catalogs.append(b); return b

    def unit(self, b): return b.view['collections'][1]

    def test_exact_resources_order_digests_and_no_initial_install(self):
        collections = load_collections()
        self.assertEqual([c['id'] for c in collections], ['fundamentals','lpic-foundations'])
        unit = collections[1]
        self.assertEqual(unit['title'], 'LPIC-1 Foundations: Files & Permissions')
        self.assertEqual([e['scenario'].identity.scenario_id for e in unit['entries']], IDS)
        self.assertEqual(collections[0]['entries'], linux_fundamentals())
        for entry in unit['entries']:
            s = entry['scenario']; accepted = load_portable((ROOT/'examples'/(s.identity.scenario_id+'.lab.json')).read_bytes())
            self.assertEqual(s.original_bytes, accepted.original_bytes)
            self.assertEqual(s.pin, accepted.pin)
        b = self.build(); self.assertEqual(len(b.labs),3)
        self.assertFalse(b.repository.root.exists()); self.assertEqual(len(b.curated),8)
        for c in b.view['collections']:
            self.assertEqual(c['completed'], {'Learn':0,'Challenge':0})
            self.assertEqual(len(c['rows']),6); self.assertTrue(c['progressKnown'])

    def test_shared_progress_bidirectional_modes_and_reset(self):
        b = self.build(); key = b.view['fundamentals'][2]['labKey']
        self.assertEqual(key, self.unit(b)['rows'][1]['labKey'])
        b.selectLab(key); b.execute('chmod 600 notes.txt'); b.execute('cat notes.txt'); b.submit()
        attempt = deepcopy(b.session.attempt)
        b.selectLab(self.unit(b)['rows'][1]['labKey'])
        self.assertEqual(b.session.attempt,attempt)
        for c in b.view['collections']: self.assertEqual(c['completed']['Learn'],1)
        b.restart('Challenge'); b.execute('pwd')
        self.assertEqual(self.unit(b)['rows'][1]['status'],b.view['fundamentals'][2]['status'])
        b.execute('chmod u+r notes.txt'); b.execute('cat notes.txt'); b.submit()
        b.selectLab(b.view['fundamentals'][2]['labKey'])
        for c in b.view['collections']: self.assertEqual(c['completed'],{'Learn':1,'Challenge':1})
        self.assertEqual(len(b.labs),4); b.restart('Learn')
        self.assertEqual(b.view['historyCount'],2)
        self.assertEqual(self.unit(b)['completed']['Learn'],1)

    def test_collection_manifest_validation(self):
        resources=self.root/'resources'; shutil.copytree(ROOT/'learning_lab/collections',resources/'collections')
        index=resources/'collections/index.json'; original=json.loads(index.read_text())
        with patch('learning_lab.collections.files',return_value=resources):
            for change in ('duplicate','path','size','conflict'):
                value=deepcopy(original)
                if change=='duplicate':value['collections'][1]['id']=value['collections'][0]['id']
                if change=='path':value['collections'][1]['file']='../escape.json'
                if change=='size':value['collections'][1]['purpose']='x'*1025
                if change=='conflict':
                    pack=json.loads((resources/'collections/packs/linux-file-navigation.lab.json').read_text())
                    pack['metadata']['title']='Different same-version content'
                    (resources/'collections/packs/conflict.lab.json').write_text(json.dumps(pack))
                    manifest=resources/'collections/lpic-foundations.json'
                    content=json.loads(manifest.read_text());content['items'][0]['file']='conflict.lab.json'
                    manifest.write_text(json.dumps(content))
                index.write_text(json.dumps(value))
                with self.subTest(change=change),self.assertRaises(ValidationError):load_collections()

    def test_hidden_shared_rows_counts_and_unique_inactive_list(self):
        b=self.build(); key=self.unit(b)['rows'][1]['labKey']; b.selectLab(key)
        b.execute('chmod 600 notes.txt'); b.execute('cat notes.txt'); b.submit(); b.flush()
        saved=b.store.current.read_bytes()
        self.assertTrue(b.setLibraryState(key,'hidden'))
        for c in b.view['collections']:
            self.assertEqual(c['inactiveCount'],1); self.assertEqual(c['total'],6)
            self.assertEqual(c['completed']['Learn'],1)
            self.assertNotIn(key,[r['labKey'] for r in c['visibleRows']])
        self.assertEqual(len(b.view['inactiveLabs']),1)
        self.assertFalse(b.selectLab(key)); self.assertTrue(b.viewHistory(key,True))
        self.assertEqual(b.store.current.read_bytes(),saved)
        b.restoreVisibility(); self.assertTrue(b.selectLab(key))
        unstarted=self.unit(b)['rows'][4]['labKey']; b.setLibraryState(unstarted,'hidden')
        self.assertEqual(self.unit(b)['completed']['Learn'],1)

    def test_previously_removed_import_stays_removed_and_byte_identical(self):
        old=self.build(old=True); source=ROOT/'examples/linux-private-note.lab.json'
        scenario=load_portable(source.read_bytes()); old.importPack(str(source)); old.selectLab(scenario.key)
        old.execute('chmod 600 notes.txt'); old.setCommandDraft('cat notes.txt'); old.flush()
        self.assertTrue(old.setLibraryState(scenario.key,'removed',True))
        saved=deepcopy(old.session.attempt)
        before={p:p.read_bytes() for folder in (old.data_root,old.config_root) for p in folder.rglob('*.json')}
        new=self.build()
        self.assertFalse(new.visibility.read_only); self.assertEqual(new.visibility.state(scenario.key),'removed')
        for p,raw in before.items(): self.assertEqual(p.read_bytes(),raw)
        self.assertEqual(new.session.attempt,saved); self.assertFalse(new.selectLab(scenario.key))
        self.assertTrue(new.importPack(str(source))); self.assertEqual(new.visibility.state(scenario.key),'removed')
        self.assertEqual(len(new.view['inactiveLabs']),1); self.assertEqual(len(new.portables),1)
        new.restoreVisibility(); self.assertEqual(new.visibility.state(scenario.key),'removed')
        self.assertTrue(new.restoreAndResume(scenario.key,saved['id']))
        self.assertEqual(new.session.attempt,saved); self.assertEqual(new.view['commandDraft'],'cat notes.txt')
        self.assertFalse(new.setLibraryState(scenario.key,'removed',True))
        self.assertTrue(new.setLibraryState(scenario.key,'hidden'))

    def test_old_version_conflict_custom_import_and_restart(self):
        b=self.build(); s=load_collections()[1]['entries'][3]['scenario']
        value=s.value(); value['identity']['content_version']='0.9.0'
        old,_=b.repository.install(json.dumps(value).encode()); b._add_portable(old); b.selectLab(old.key)
        b.execute('pwd'); b.setCommandDraft('help'); b.flush(); prior=deepcopy(b.session.attempt)
        b.setLibraryState(old.key,'removed',True)
        b.selectLab(s.key,True); b.execute('chmod 600 notes.txt'); b.execute('cat notes.txt'); b.submit(); b.flush()
        new=self.build(); self.assertEqual(new.labs[old.key].session.attempt,prior)
        self.assertEqual(new.visibility.state(old.key),'removed')
        self.assertEqual(self.unit(new)['rows'][3]['progress']['Learn'],'Completed')
        self.assertIn(old.key,[r['labKey'] for r in new.view['inactiveLabs']])
        # Same ID/version with different content cannot replace a bundled scenario.
        other=self.build('conflict'); value=s.value(); value['metadata']['title']='Custom variant'
        custom,_=other.repository.install(json.dumps(value).encode()); other._add_portable(custom)
        row=self.unit(other)['rows'][3]; self.assertFalse(row['available']); self.assertEqual(row['status'],'')
        self.assertFalse(other.selectLab(s.key)); self.assertIn(custom.key,[r['labKey'] for r in other.view['otherLabs']])

    def test_backup_restore_removed_promoted_import_and_hidden_shared_lab(self):
        old=self.build(old=True); source=ROOT/'examples/linux-search-only-directory.lab.json'
        scenario=load_portable(source.read_bytes()); old.importPack(str(source)); old.selectLab(scenario.key)
        old.execute('chmod 100 Lookup'); old.execute('cd Lookup'); old.setCommandDraft('cat message.txt'); old.flush()
        old.setLibraryState(scenario.key,'removed',True)
        key=old.collection[0]['scenario'].key; old.setLibraryState(key,'hidden')
        b=self.build(); lock=ProfileLocks(b.data_root,b.config_root); self.locks.append(lock); b.profile_locks=lock
        unstarted=self.unit(b)['rows'][3]['labKey']
        self.assertTrue(b.setLibraryState(unstarted,'hidden'))
        self.assertNotIn(unstarted,b.portables)
        archive=self.root/'backup.llbackup'; self.assertTrue(b.backupProfile(str(archive)),b.transfer_message)
        backup=pb.read_backup(archive); self.assertEqual(backup.manifest['schema_version'],2)
        dest=self.root/'restored'; pb.restore(backup,dest,confirmed=True)
        for name,raw in backup.files.items(): self.assertEqual((dest/name).read_bytes(),raw)
        restored=self.build('restored')
        self.assertEqual(restored.session.attempt,b.session.attempt)
        self.assertEqual(restored.visibility.entries,b.visibility.entries)
        self.assertEqual(restored.view['commandDraft'],'cat message.txt')
        self.assertTrue(restored.restoreAndResume(scenario.key,restored.session.attempt['id']))
        restored.execute('cat message.txt'); restored.submit(); self.assertEqual(restored.view['grade']['score'],100)
        self.assertEqual([c['inactiveCount'] for c in restored.view['collections']],[1,2])

    def test_corrupt_progress_omits_totals_and_visibility_validation(self):
        b=self.build(); key=self.unit(b)['rows'][0]['labKey']; b.selectLab(key)
        b.store.current.write_bytes(b'{"schema_version":999}')
        new=self.build()
        for c in new.view['collections']: self.assertFalse(c['progressKnown'])
        with self.assertRaises(ValidationError):
            validate({'schema_version':1,'entries':{key:'removed'}},{key},set())
        self.assertEqual(validate({'schema_version':1,'entries':{key:'removed'}},{key},{key}),{key:'removed'})

    def test_all_unit_entries_launch_without_import_and_reimport_is_idempotent(self):
        b=self.build()
        for row in reversed(self.unit(b)['rows']):
            self.assertTrue(b.selectLab(row['labKey'],True))
            self.assertEqual(b.view['metadata']['title'],row['title'])
            before=deepcopy(b.session.attempt)
            source=ROOT/'examples'/(b.view['labId']+'.lab.json')
            self.assertTrue(b.importPack(str(source)))
            self.assertEqual(b.session.attempt,before)
        self.assertEqual(len(b.portables),6); self.assertEqual(len(b.view['otherLabs']),3)
        b.flush(); before={k:deepcopy(l.session.attempt) for k,l in b.labs.items()}
        new=self.build(); self.assertEqual({k:l.session.attempt for k,l in new.labs.items()},before)
