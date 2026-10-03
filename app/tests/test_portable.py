from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.domain.engine import Engine
from learning_lab.domain.validation import ValidationError
from learning_lab.portable import load_portable, portable_from_legacy, PackRepository
from learning_lab.pinned_storage import PinnedStore
from learning_lab.session import Session
from test_lab import PACK, FIXED

APP=QCoreApplication.instance() or QCoreApplication([])
SCENARIO=portable_from_legacy(PACK)


class PortableTests(unittest.TestCase):
    def test_conversion_preserves_each_original_scenario(self):
        for pack in load_bundled_scenarios()[0]:
            s=portable_from_legacy(pack)
            self.assertEqual(s.legacy_pack(), pack)
            self.assertEqual(Engine(s.legacy_pack()).grade(),Engine(pack).grade())

    def test_format_capability_paths_and_code_rejected(self):
        base=SCENARIO.value()
        changes=[('schema_version',99),('assets',['../../etc/passwd']),('format','other')]
        for key,value in changes:
            p=deepcopy(base);p[key]=value
            with self.subTest(key=key),self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        for field,value in [('id','python:evil'),('contract_version',True),('contract_version',2),
                            ('supported_behavior_versions',['future']),('required_capabilities',['shell'])]:
            p=deepcopy(base);p['engine'][field]=value
            with self.subTest(field=field),self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        for raw in (b'PK\x03\x04',b'\x1f\x8b',b'x'*262145,b'[]',b'{',b'\xff',b'\xef\xbb\xbf'+SCENARIO.original_bytes):
            with self.assertRaises(ValidationError):load_portable(raw)
        p=deepcopy(base);p['script']='eval("x")'
        with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        p=deepcopy(base);p['objectives'][0]['predicate']='eval'
        with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        raw=SCENARIO.original_bytes.replace(b'"format":',b'"format":"duplicate", "format":',1)
        with self.assertRaises(ValidationError):load_portable(raw)

    def test_resource_limits_and_nonregular_files(self):
        for mutate in (
            lambda p:p['metadata'].update(title='x'*121),
            lambda p:p['domain']['diagnostics'][0].update(label='x'*513),
            lambda p:p.update(hints=['hint']*33),
            lambda p:p['domain']['topology'].update(devices=p['domain']['topology']['devices']*11),
        ):
            p=SCENARIO.value();mutate(p)
            with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        with tempfile.TemporaryDirectory() as tmp:
            import os
            root=Path(tmp);fifo=root/'pipe.lab.json';os.mkfifo(fifo)
            with self.assertRaises(ValidationError):PackRepository(root/'packs').import_file(fifo)
            repo=PackRepository(root/'packs');repo.root.mkdir()
            for i in range(256):(repo.root/(str(i)+'.json')).write_bytes(b'{}')
            with self.assertRaises(ValidationError):repo.install(SCENARIO.original_bytes)
            self.assertEqual(len(list(repo.root.iterdir())),256)

    def test_diagnostic_validation(self):
        for change in ({'operation':'shell'},{'target':'8.8.8.8'},{'id':'../bad'}):
            p=SCENARIO.value();p['domain']['diagnostics'][0].update(change)
            with self.subTest(change=change),self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        p=SCENARIO.value();p['domain']['diagnostics']*=2
        with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        p=SCENARIO.value();p['domain']['source_device']='unknown'
        with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())

    def test_hints_are_variable_for_portable_only(self):
        for count in (0,1,5):
            p=SCENARIO.value();p['hints']=['A progressive hint']*count
            scenario=load_portable(json.dumps(p).encode())
            s=Session(scenario.legacy_pack(),domain=scenario.domain())
            for _ in range(8):s.hint()
            self.assertEqual(s.attempt['hints'],count)
            with tempfile.TemporaryDirectory() as tmp:
                store=PinnedStore(tmp,scenario);store.save(s.attempt)
                self.assertEqual(store.load(),s.attempt)

    def test_import_duplicate_conflict_and_parallel_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=PackRepository(Path(tmp)/'packs')
            first,added=repo.install(SCENARIO.original_bytes);self.assertTrue(added)
            same,added=repo.install(json.dumps(SCENARIO.value(),sort_keys=True).encode())
            self.assertFalse(added);self.assertEqual(same.key,first.key)
            p=SCENARIO.value();p['metadata']['title']+=' changed'
            with self.assertRaises(ValidationError):repo.install(json.dumps(p).encode())
            p['identity']['content_version']='1.1.0'
            later,added=repo.install(json.dumps(p).encode());self.assertTrue(added)
            self.assertNotEqual(first.key,later.key)
            self.assertEqual(len(repo.scan()[0]),2)
            self.assertEqual(first.original_bytes,SCENARIO.original_bytes)

    def test_invalid_import_and_interrupted_write_do_not_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=PackRepository(Path(tmp)/'packs')
            with self.assertRaises(ValidationError):repo.install(b'{}')
            self.assertFalse(repo.root.exists())
            with patch('learning_lab.storage.os.replace',side_effect=OSError('disk full')):
                with self.assertRaises(OSError):repo.install(SCENARIO.original_bytes)
            self.assertEqual(list(repo.root.iterdir()),[])

    def test_bad_repository_entries_are_preserved_and_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=PackRepository(tmp);repo.install(SCENARIO.original_bytes)
            bad=Path(tmp)/'bad.json';bad.write_bytes(b'{}')
            scenarios,warnings=repo.scan()
            self.assertEqual(len(scenarios),1);self.assertTrue(warnings);self.assertEqual(bad.read_bytes(),b'{}')
            link=Path(tmp)/'link.json';link.symlink_to(bad)
            self.assertEqual(len(repo.scan()[1]),2)

    def test_pins_prevent_backup_downgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=PinnedStore(tmp,SCENARIO);s=Session(SCENARIO.legacy_pack());store.save(s.attempt)
            p=json.loads(store.current.read_bytes());p['pin']['engine']['behavior_version']='future'
            raw=json.dumps(p).encode();store.current.write_bytes(raw)
            self.assertIsNone(store.load());self.assertTrue(store.read_only)
            self.assertEqual(store.current.read_bytes(),raw)
            self.assertIn('engine',store.notice)

    def test_corruption_and_newer_records_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=PinnedStore(tmp,SCENARIO);s=Session(SCENARIO.legacy_pack());store.save(s.attempt)
            store.current.write_bytes(b'{broken')
            self.assertEqual(store.load()['id'],s.attempt['id'])
            self.assertEqual(len(list(Path(tmp).glob('current.corrupt-*'))),1)
            p=json.loads(store.current.read_bytes());p['schema_version']=99
            raw=json.dumps(p).encode();store.current.write_bytes(raw)
            self.assertIsNone(store.load());self.assertEqual(store.current.read_bytes(),raw)

    def test_catalog_import_export_modes_and_restart_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=root/'data';config=root/'config';config.mkdir()
            bundled=load_bundled_scenarios()[0]
            catalog=CatalogBridge(bundled,data,config)
            try:
                legacy={str(p.relative_to(data)):p.read_bytes() for p in data.rglob('*.json')}
                imported=root/'in.lab.json';imported.write_bytes(SCENARIO.original_bytes)
                self.assertTrue(catalog.importPack(str(imported)))
                self.assertEqual(len(catalog.labs),4)
                self.assertTrue(catalog.selectLab(SCENARIO.key,True))
                for key,value in FIXED.items():catalog.edit(key,str(value))
                catalog.apply();catalog.hint();catalog.submit()
                self.assertEqual(catalog.view['grade']['score'],100)
                old=catalog.session.attempt['id'];catalog.restart('Challenge')
                self.assertEqual(catalog.session.attempt['hints'],0)
                rows,_,_=catalog.store.history(catalog.session.attempt['id'])
                self.assertEqual(rows[0]['id'],old);self.assertEqual(rows[0]['hints'],1)
                catalog.edit('dns','unfinished text');attempt=catalog.session.attempt['id'];catalog.flush()
                out=root/'out.lab.json';self.assertTrue(catalog.exportScenario(str(out)))
                self.assertEqual(load_portable(out.read_bytes()).identity,SCENARIO.identity)
                self.assertNotIn(attempt,out.read_text())
                self.assertTrue(catalog.importPack(str(out)))
                self.assertEqual(len(catalog.labs),4)
                for name,raw in legacy.items():self.assertEqual((data/name).read_bytes(),raw)
                fresh=CatalogBridge(bundled,data,config)
                try:
                    self.assertEqual(fresh.session.attempt['id'],attempt)
                    self.assertEqual(fresh.session.attempt['draft']['dns'],'unfinished text')
                    self.assertEqual(fresh.session.attempt['mode'],'Challenge')
                    self.assertEqual(fresh.store.scenario.pin,SCENARIO.pin)
                finally:
                    for lab in fresh.labs.values():lab.timer.stop()
            finally:
                for lab in catalog.labs.values():lab.timer.stop()
