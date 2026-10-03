"""Curated resources and profile-safe Library integration."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch
import zipfile
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.collections import linux_fundamentals
from learning_lab.portable import PackRepository, load_portable

APP=QCoreApplication.instance() or QCoreApplication([])
ROOT=Path(__file__).resolve().parents[1]


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.data=self.root/'data';self.config=self.root/'config';self.config.mkdir()
        self.catalogs=[]

    def tearDown(self):
        for b in self.catalogs:
            for lab in b.labs.values():lab.timer.stop()
        self.temp.cleanup()

    def build(self):
        b=CatalogBridge(load_bundled_scenarios()[0],self.data,self.config)
        self.catalogs.append(b);return b

    def test_approved_bytes_titles_order_and_fresh_profile(self):
        entries=linux_fundamentals()
        expected=['Find your way around Linux','Start your first service','Restore access to your file',
                  'Why can’t I enter this directory?','Read the fieldwork handover','Recover a failed web service']
        for e in entries:
            s=e['scenario'];self.assertEqual(s.original_bytes,(ROOT/'examples'/(s.identity.scenario_id+'.lab.json')).read_bytes())
        b=self.build();self.assertEqual([r['title'] for r in b.view['fundamentals']],expected)
        self.assertEqual(len(b.labs),3);self.assertFalse(b.repository.root.exists())
        for row in b.view['fundamentals']:
            self.assertTrue(row['available']);self.assertEqual(row['action'],'Start')
            self.assertEqual(row['status'],'Learn: Not started · Challenge: Not started')
        self.assertEqual(len(b.view['otherLabs']),3)

    def test_any_lab_starts_lazily_and_repeated_start_does_not_reset(self):
        b=self.build();row=b.view['fundamentals'][-1]
        self.assertTrue(b.selectLab(row['labKey']))
        first=deepcopy(b.session.attempt);self.assertEqual(len(b.portables),1)
        self.assertTrue(b.selectLab(row['labKey']));self.assertEqual(b.session.attempt,first)
        self.assertEqual(b.view['fundamentals'][-1]['action'],'Continue')
        self.assertEqual(len(b.view['otherLabs']),3)
        self.assertTrue(b.importPack(str(ROOT/'examples/linux-web-document-root.lab.json')))
        self.assertEqual(len(b.labs),4)

    def test_existing_import_progress_modes_reset_and_restart(self):
        b=self.build();s=linux_fundamentals()[2]['scenario'];b.repository.install(s.original_bytes);b._add_portable(s)
        b.selectLab(s.key);b.hint();b.execute('chmod 600 notes.txt');b.execute('cat notes.txt');b.submit()
        original=b.store.current.read_bytes();attempt=b.session.attempt['id']
        self.assertEqual(b.view['fundamentals'][2]['status'],'Learn: Completed · Challenge: Not started')
        self.assertTrue(b.selectLab(s.key));self.assertEqual(b.store.current.read_bytes(),original)
        b.restart('Challenge');self.assertEqual(b.view['fundamentals'][2]['status'],'Learn: Completed · Challenge: Not started')
        b.execute('cat notes.txt');self.assertEqual(b.view['fundamentals'][2]['status'],'Learn: Completed · Challenge: In progress')
        b.execute('chmod u+r notes.txt');b.execute('cat notes.txt');b.submit();b.restart('Challenge')
        self.assertEqual(b.view['fundamentals'][2]['status'],'Learn: Completed · Challenge: Completed')
        b.setCommandDraft('pwd');b.flush();saved=deepcopy(b.session.attempt)
        snapshot={p.relative_to(self.data):p.read_bytes() for p in self.data.rglob('*.json')}
        fresh=self.build();self.assertEqual(fresh.session.attempt,saved);self.assertEqual(fresh.view['commandDraft'],'pwd')
        for p,raw in snapshot.items():self.assertEqual((self.data/p).read_bytes(),raw)
        self.assertEqual(fresh.view['historyCount'],2)
        self.assertTrue((fresh.store.archives/(attempt+'.json')).exists())
        self.assertEqual(len(fresh.labs),4)

    def test_conflicting_same_version_preserved_and_not_started(self):
        s=linux_fundamentals()[3]['scenario'];value=s.value();value['metadata']['title']='Custom directory exercise'
        repo=PackRepository(self.data/'portable/packs');custom,_=repo.install(json.dumps(value).encode())
        b=self.build();b.selectLab(custom.key);b.execute('pwd');b.flush()
        snapshot={p.relative_to(self.data):p.read_bytes() for p in self.data.rglob('*.json')}
        row=b.view['fundamentals'][3];self.assertFalse(row['available']);self.assertEqual(row['status'],'')
        self.assertIn(custom.key,[r['labKey'] for r in b.view['otherLabs']])
        self.assertFalse(b.selectLab(s.key,True));self.assertNotIn(s.key,b.labs)
        for p,raw in snapshot.items():self.assertEqual((self.data/p).read_bytes(),raw)

    def test_other_versions_and_custom_imports_remain_separate(self):
        s=linux_fundamentals()[0]['scenario'];value=s.value();value['identity']['content_version']='2.0.0'
        repo=PackRepository(self.data/'portable/packs');newer,_=repo.install(json.dumps(value).encode())
        value['identity']['id']='my-navigation';custom,_=repo.install(json.dumps(value).encode())
        b=self.build();self.assertTrue(b.selectLab(s.key))
        self.assertEqual(set(b.portables),{s.key,newer.key,custom.key})
        self.assertEqual({r['labKey'] for r in b.view['otherLabs']},set(b.labs)-{s.key})
        self.assertEqual(b.portables[newer.key].original_bytes,newer.original_bytes)

    def test_drafts_block_install_until_existing_confirmation(self):
        b=self.build();b.edit('dns','draft');key=b.view['fundamentals'][0]['labKey']
        self.assertFalse(b.selectLab(key));self.assertFalse(b.repository.root.exists())
        previous=deepcopy(b.session.attempt)
        self.assertTrue(b.selectLab(key,True));self.assertEqual(b.labs['gateway-dns'].session.attempt,previous)

    def test_unreliable_records_omit_status(self):
        b=self.build();s=linux_fundamentals()[4]['scenario'];b.selectLab(s.key)
        b.store.current.write_bytes(b'{"schema_version":999}')
        fresh=self.build();self.assertTrue(fresh.labs[s.key].store.read_only)
        self.assertEqual(fresh.view['fundamentals'][4]['status'],'')
        self.assertEqual(fresh.labs[s.key].store.current.read_bytes(),b'{"schema_version":999}')
        b=self.build();lab=b.labs[s.key];lab.store.read_only=False;lab.store.notice='';lab.history_reliable=False
        self.assertEqual(b.view['fundamentals'][4]['status'],'')

    def test_history_pages_do_not_merge_learning_modes(self):
        b=self.build();b.selectLab(b.view['fundamentals'][2]['labKey'])
        b.execute('chmod 600 notes.txt');b.execute('cat notes.txt');b.submit()
        b.restart('Challenge')
        for _ in range(26):b.restart('Challenge')
        fresh=self.build();self.assertEqual(fresh.view['fundamentals'][2]['status'],'Learn: Completed · Challenge: In progress')
        (fresh.store.archives/'unreadable.json').write_bytes(b'{bad')
        again=self.build();self.assertEqual(again.view['fundamentals'][2]['status'],'')

    def test_unavailable_collection_or_install_error_preserves_library(self):
        with patch('learning_lab.catalog.load_collections',side_effect=ValueError('invalid resource')):
            b=self.build();self.assertEqual(b.view['fundamentals'],[]);self.assertEqual(len(b.view['otherLabs']),3)
            self.assertIn('unavailable',b.notice)
        b=self.build();key=b.view['fundamentals'][0]['labKey']
        with patch.object(b.repository,'install',side_effect=OSError('read-only profile')):
            self.assertFalse(b.selectLab(key));self.assertEqual(len(b.labs),3)
            self.assertIn('preserved',b.view['transferMessage'])

    def test_missing_pack_with_existing_attempt_omits_status_until_resume(self):
        b=self.build();row=b.view['fundamentals'][0];b.selectLab(row['labKey']);b.execute('pwd');b.flush()
        attempt=deepcopy(b.session.attempt)
        # Remove only a disposable fixture's installed pack, leaving its pinned record.
        path=b.repository.root/(row['labKey'][5:]+'.json');path.unlink()
        fresh=self.build();row=fresh.view['fundamentals'][0]
        self.assertEqual(row['status'],'');self.assertEqual(row['action'],'Continue')
        self.assertTrue(fresh.selectLab(row['labKey']));self.assertEqual(fresh.session.attempt,attempt)
        self.assertEqual(fresh.view['fundamentals'][0]['status'],'Learn: In progress · Challenge: Not started')

    def test_packaged_resources_and_source_launch_from_unrelated_directory(self):
        # Stage the declared package layout, without setuptools/network/system install.
        config=tomllib.loads((ROOT/'pyproject.toml').read_text())
        patterns=config['tool']['setuptools']['package-data']['learning_lab']
        staged=self.root/'installed';package=staged/'learning_lab';package.mkdir(parents=True)
        source=ROOT/'learning_lab'
        for path in list(source.rglob('*.py'))+[p for pattern in patterns for p in source.glob(pattern)]:
            target=package/path.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        self.assertFalse((staged/'examples').exists())
        archive=self.root/'resources.zip'
        with zipfile.ZipFile(archive,'w') as z:
            for p in package.rglob('*'):
                if p.is_file():z.write(p,p.relative_to(staged))
        probe="from learning_lab.collections import linux_fundamentals; assert len(linux_fundamentals()) == 6; print('resources PASS')"
        for location in (ROOT,staged,archive):
            result=subprocess.run([sys.executable,'-B','-c',probe],cwd=self.root,
                                  env={**os.environ,'PYTHONPATH':str(location)},capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
        gui="""
from pathlib import Path
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
app,e,b,lock=build_application(Path('staged-data'),Path('staged-config'))
w=e.rootObjects()[0]
assert QTest.qWaitForWindowExposed(w,5000)
assert len(b.view['fundamentals'])==6
assert b.selectLab(b.view['fundamentals'][5]['labKey'])
assert b.view['labId']=='linux-web-document-root'
assert not w.grabWindow().isNull()
w.close();app.processEvents();lock.unlock()
"""
        result=subprocess.run([sys.executable,'-B','-c',gui],cwd=self.root,
                              env={**os.environ,'PYTHONPATH':str(staged),'QT_QPA_PLATFORM':'offscreen',
                                   'QT_QPA_PLATFORMTHEME':'','QT_QUICK_BACKEND':'software'},capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
