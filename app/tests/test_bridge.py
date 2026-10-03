import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication, QLockFile
from learning_lab.bridge import Bridge
from learning_lab.storage import Store
from test_lab import PACK, FIXED

APP=QCoreApplication.instance() or QCoreApplication([])

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.store=Store(self.root/'data',PACK)
        self.bridge=Bridge(PACK,self.store,self.root/'preferences.json')
        self.addCleanup(self.bridge.timer.stop)

    def test_library_completion_survives_reset(self):
        b=self.bridge
        self.assertEqual(b.view['libraryStatus'],'Not started')
        for key,value in FIXED.items():b.edit(key,str(value))
        b.apply();b.submit();old=b.session.attempt['id'];b.restart('Learn')
        self.assertEqual(b.view['libraryStatus'],'Completed')
        self.assertEqual(b.view['libraryBest'],'100/100')
        self.assertEqual(b.view['historyCount'],1)
        self.assertNotEqual(b.session.attempt['id'],old)

    def test_modes_preserve_drafts_and_hint_usage(self):
        b=self.bridge;b.hint();b.edit('gateway','bad draft');b.execute('help');b.submit()
        old=b.session.attempt['id'];b.restart('Challenge')
        rows,_,_=self.store.history(b.session.attempt['id'])
        self.assertEqual(rows[0]['id'],old)
        self.assertEqual(rows[0]['draft']['gateway'],'bad draft')
        self.assertEqual(rows[0]['hints'],1)
        self.assertTrue(rows[0]['console']);self.assertTrue(rows[0]['assessments'])
        b.restart('Learn')
        self.assertEqual(self.store.history(b.session.attempt['id'])[1],2)

    def test_duplicate_submit_saved_once(self):
        self.bridge.submit();self.bridge.submit()
        saved=self.store.load()
        self.assertEqual(len(saved['assessments']),1)

    def test_newer_preferences_preserved(self):
        p=self.root/'preferences.json';raw='{"schema_version":2,"future":"keep"}';p.write_text(raw)
        b=Bridge(PACK,self.store,p);self.addCleanup(lambda b=b: b.timer.stop())
        b.fallbackTheme(True)
        self.assertEqual(p.read_text(),raw)
        self.assertEqual(b.theme_name,'Built-in palette')

    def test_newer_progress_cannot_be_reset(self):
        raw='{"schema_version":99,"future":"keep"}';self.store.current.write_text(raw)
        b=Bridge(PACK,Store(self.root/'data',PACK),self.root/'preferences.json');self.addCleanup(lambda b=b: b.timer.stop())
        b.restart('Challenge');b.apply();b.submit()
        self.assertEqual(self.store.current.read_text(),raw)
        self.assertTrue(b.view['readOnly'])

    def test_single_writer(self):
        path=str(self.root/'lock');first=QLockFile(path);second=QLockFile(path)
        first.setStaleLockTime(0);second.setStaleLockTime(0)
        self.assertTrue(first.tryLock(0));self.assertFalse(second.tryLock(0));first.unlock()
        self.assertTrue(second.tryLock(0));second.unlock()

    def test_retry_save_preserves_in_memory_draft(self):
        b=self.bridge;b.edit('gateway','192.168.50.1')
        with patch.object(self.store,'save',side_effect=OSError('disk unavailable')):
            b.flush()
        self.assertTrue(b.view['canRetry']);self.assertTrue(b.view['readOnly'])
        b.retrySave()
        self.assertFalse(b.view['canRetry']);self.assertFalse(b.view['readOnly'])
        self.assertEqual(self.store.load()['draft']['gateway'],'192.168.50.1')

if __name__=='__main__':unittest.main()
