"""Workspace lifecycle and transfer failures use isolated profiles only."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.workspace_state import load_workspace,path_for

APP=QCoreApplication.instance() or QCoreApplication([])

class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.data=self.root/'data';self.config=self.root/'config';self.config.mkdir()
        self.catalogs=[];self.b=self.open()
    def open(self):
        b=CatalogBridge(load_bundled_scenarios()[0],self.data,self.config);self.catalogs.append(b);return b
    def tearDown(self):
        for b in self.catalogs:
            for lab in b.labs.values():lab.timer.stop()
        self.tmp.cleanup()
    def test_pending_commands_diagnostics_reset_and_restart(self):
        b=self.b;old=b.session.attempt['id'];b.setCommandDraft('ping 10.20.0.10');b.test();b.flush()
        raw=b.store.current.read_bytes();side=load_workspace(b.store,old)
        self.assertEqual(side['command'],'ping 10.20.0.10');self.assertTrue(side['diagnostics'])
        self.assertNotIn('diagnostics',json.loads(raw)['attempt'])
        b.edit('dns','unfinished');b.restart('Challenge')
        self.assertEqual(load_workspace(b.store,old),side)
        rows,_,_=b.store.history(b.session.attempt['id']);self.assertEqual(rows[0]['draft']['dns'],'unfinished')
        self.assertEqual(b.view['commandDraft'],'');self.assertEqual(b.view['diagnostics'],[])
        b.setCommandDraft('help');b.flush();fresh=self.open()
        self.assertEqual(fresh.view['commandDraft'],'help');self.assertEqual(fresh.view['mode'],'Challenge')
        self.assertEqual(load_workspace(fresh.store,old),side)
    def test_future_and_corrupt_workspace_preserved(self):
        for raw in (b'{broken',b'{"schema_version":99,"command":"private","diagnostic_revision":-1,"diagnostics":[]}'):
            with self.subTest(raw=raw):
                b=self.b;p=path_for(b.store,b.session.attempt['id']);p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
                current=b.store.current.read_bytes();backup=b.store.backup.read_bytes()
                fresh=self.open();self.assertTrue(fresh.store.read_only)
                fresh.setCommandDraft('overwrite');fresh.flush()
                self.assertEqual(p.read_bytes(),raw);self.assertEqual(b.store.current.read_bytes(),current);self.assertEqual(b.store.backup.read_bytes(),backup)
                self.assertFalse(fresh.exportAttempt(str(self.root/'bad.attempt.json'),fresh.session.attempt['id']))
    def test_sidecar_write_failure_blocks_switch_until_retry(self):
        b=self.b;b.setCommandDraft('pending command');old=b.active
        with patch('learning_lab.bridge.save_workspace',side_effect=OSError('disk full')):
            self.assertFalse(b.selectLab('subnet-boundary',True))
        self.assertIs(b.active,old);self.assertTrue(b.view['canRetry']);self.assertEqual(b.view['commandDraft'],'pending command')
        b.retrySave();self.assertFalse(b.view['canRetry']);self.assertTrue(b.selectLab('subnet-boundary',True))
        b.selectLab('gateway-dns',True);self.assertEqual(b.view['commandDraft'],'pending command')
    def test_separate_attempt_export_preserves_history_and_scenario_privacy(self):
        b=self.b;old=b.session.attempt['id'];b.setCommandDraft('PRIVATE-DRAFT');b.edit('dns','PRIVATE-SETTING');b.hint();b.restart('Learn')
        archive=b.store.archives/(old+'.json');raw=archive.read_bytes()
        dest=self.root/'personal.attempt.json';self.assertTrue(b.exportAttempt(str(dest),old))
        doc=json.loads(dest.read_bytes());self.assertEqual(doc['format'],'learning-lab.attempt-history');self.assertEqual(doc['record_json'].encode(),raw)
        self.assertEqual(doc['workspace']['command'],'PRIVATE-DRAFT');self.assertIn('unknown',doc['provenance'])
        pack=self.root/'public.lab.json';self.assertTrue(b.exportScenario(str(pack)))
        self.assertNotIn('PRIVATE',pack.read_text());self.assertNotIn(old,pack.read_text())
        self.assertEqual(archive.read_bytes(),raw)
        self.assertFalse(b.importPack(str(dest)));self.assertFalse(b.exportAttempt(str(dest),'../../escape'))
    def test_layout_preferences_restart_and_unknown_preservation(self):
        self.b.saveLayout({'mission_width':310,'mission_height':120,'dock_height':240})
        self.assertEqual(self.open().view['workspaceLayout']['mission_width'],310)
        path=self.config/'workspace-layout.json';raw=b'{"schema_version":99,"sizes":{}}';path.write_bytes(raw)
        fresh=self.open();fresh.saveLayout({'mission_width':280})
        self.assertEqual(path.read_bytes(),raw);self.assertIn('preserved',fresh.view['catalogNotice'])
        fresh.saveLayout({'unexpected':4});self.assertIn('could not be saved',fresh.view['transferMessage'])
    def test_pack_warning_visible_in_library_and_retained_after_switch(self):
        root=self.data/'portable'/'packs';root.mkdir(parents=True);bad=root/'bad.json';bad.write_bytes(b'{}')
        fresh=self.open();self.assertIn('unavailable pack',fresh.view['catalogNotice'])
        fresh.selectLab('subnet-boundary',True);self.assertIn('unavailable pack',fresh.view['catalogNotice'])
        self.assertEqual(bad.read_bytes(),b'{}')
