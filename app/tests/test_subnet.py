from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication
from learning_lab.catalog import CatalogBridge
from learning_lab.domain.engine import Engine, load_pack, load_catalog
from learning_lab.domain.validation import ValidationError
from learning_lab.session import Session
from learning_lab.storage import Store, encode, validate_record, NewerSchema
from test_lab import PACK, RAW, FIXED

APP = QCoreApplication.instance() or QCoreApplication([])
SUB_RAW = (Path(__file__).resolve().parents[1] / 'learning_lab/packs/subnet-boundary.json').read_bytes()
SUB = load_pack(SUB_RAW)


class SubnetTests(unittest.TestCase):
    def test_initial_peer_gateway_server(self):
        e = Engine(SUB)
        self.assertTrue(e.reach('192.168.50.21').ok)
        for target in ('192.168.50.1', '10.20.0.10'):
            self.assertFalse(e.reach(target).ok)
            self.assertIn('outside', e.reach(target).message)
        self.assertFalse(e.resolve('portal.lab.test')[0].ok)
        self.assertEqual(e.grade()['score'], 40)
        self.assertIn('192.168.50.16/28', e.command('ip route'))

    def test_exact_prefix_and_assigned_address(self):
        for changes, score in (({'prefix':24},100), ({'prefix':16},70), ({'prefix':24,'address':'192.168.50.22'},80)):
            with self.subTest(changes=changes):
                e = Engine(SUB, {**SUB['initial_state']['WS-01'], **changes})
                for target in ('192.168.50.21','192.168.50.1','10.20.0.10'):
                    self.assertTrue(e.reach(target).ok)
                self.assertTrue(e.portal().ok)
                self.assertEqual(e.grade()['score'], score)
                self.assertEqual(e.grade()['complete'], score == 100)

    def test_mask_alternatives_and_atomic_validation(self):
        for value in ('24','/24','255.255.255.0'):
            s=Session(SUB);s.edit('prefix',value)
            self.assertEqual(s.submit()['score'],40)
            s.apply();self.assertEqual(s.submit()['score'],100)
        for value in ('255.0.255.0','0.0.0.255','33','/32','bad'):
            s=Session(SUB);s.edit('prefix',value);before=deepcopy(s.attempt)
            with self.assertRaises(ValidationError):s.apply()
            self.assertEqual(s.attempt,before)
        for address in ('192.168.50.16','192.168.50.31','192.168.50.21'):
            s=Session(SUB);s.edit('address',address)
            with self.assertRaises(ValidationError):s.apply()

    def test_fixed_fields_and_unsolvable_packs(self):
        for field in ('gateway','dns'):
            s=Session(SUB)
            with self.assertRaises(ValidationError):s.edit(field,'10.20.0.99')
            s.attempt['draft'][field]='10.20.0.99'
            with self.assertRaises(ValidationError):s.apply()
            with self.assertRaises(ValidationError):validate_record(encode(s.attempt),SUB)
        for fields in ([],['prefix','prefix'],['shell'],['address']):
            p=deepcopy(SUB);p['editable_fields']['WS-01']=fields
            with self.assertRaises(ValidationError):load_pack(json.dumps(p))
        p=deepcopy(SUB);p['initial_state']['WS-01']['gateway']='192.168.50.254';p['topology']['devices'][0]['gateway']='192.168.50.254'
        with self.assertRaises(ValidationError):load_pack(json.dumps(p))
        self.assertEqual(len(load_catalog([RAW,SUB_RAW])),2)
        with self.assertRaises(ValidationError):load_catalog([SUB_RAW,SUB_RAW])

    def test_diagnostics_and_bounded_console(self):
        s=Session(SUB);s.test();text='\n'.join(s.attempt['console'])
        self.assertIn('PASS · Retain local peer',text)
        self.assertIn('FAIL · Reach the assigned gateway',text)
        self.assertIn('FAIL · Restore remote server',text)
        for command in ('ping 192.168.50.1; touch /tmp/evil','$(id)','ping 8.8.8.8','connect portal.lab.test 443','x'*1000):
            result=s.engine.command(command);self.assertLess(len(result),2048)
        s.edit('prefix','24');s.test();self.assertIn('Warning: drafts exist','\n'.join(s.attempt['console']))
        s.apply();s.test();self.assertIn('PASS · Restore remote server','\n'.join(s.attempt['console']))


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.data=self.root/'data';self.config=self.root/'config';self.config.mkdir()

    def catalog(self):
        c=CatalogBridge([PACK,SUB],self.data,self.config)
        self.addCleanup(lambda: [lab.timer.stop() for lab in c.labs.values()])
        return c

    def test_legacy_gateway_location_and_dirty_switch(self):
        store=Store(self.data,PACK);s=Session(PACK);s.edit('gateway','192.168.50.1');store.save(s.attempt)
        c=self.catalog();original=deepcopy(c.session.attempt)
        self.assertFalse(c.selectLab('subnet-boundary',False))
        self.assertEqual(c.pack['lab_id'],'gateway-dns')
        self.assertTrue(c.selectLab('subnet-boundary',True));c.hint();c.edit('prefix','24')
        subnet=deepcopy(c.session.attempt)
        self.assertTrue(c.selectLab('gateway-dns',True));self.assertEqual(c.session.attempt,original)
        self.assertEqual(Store(self.data,PACK).load(),original)
        self.assertEqual(Store(self.data/'labs/subnet-boundary',SUB).load(),subnet)
        self.assertFalse(c.selectLab('../../evil',True))
        c.selectLab('subnet-boundary',True);c.flush();restored=self.catalog()
        self.assertEqual(restored.session.attempt,subnet)
        restored.selectLab('gateway-dns',True);self.assertEqual(restored.session.attempt,original)

    def test_hints_grades_reset_modes_and_restart_both(self):
        c=self.catalog()
        for pack,fix in ((PACK,FIXED),(SUB,{'prefix':24})):
            with self.subTest(lab=pack['lab_id']):
                c.selectLab(pack['lab_id'],True)
                for _ in range(4):c.hint()
                self.assertEqual(c.session.attempt['hints'],3)
                for field,value in fix.items():c.edit(field,str(value))
                c.apply();c.submit();first=deepcopy(c.session.attempt);c.submit()
                self.assertEqual(c.session.attempt['assessments'],first['assessments'])
                self.assertEqual(c.session.engine.grade()['score'],100)
                c.edit('address','draft retained');c.restart('Challenge')
                rows,count,_=c.store.history(c.session.attempt['id'])
                self.assertEqual(count,1);self.assertEqual(rows[0]['hints'],3)
                self.assertEqual(rows[0]['draft']['address'],'draft retained')
                self.assertEqual(rows[0]['assessments']['1']['score'],100)
                self.assertEqual(c.view['hints'],[]);c.hint();self.assertEqual(c.session.attempt['hints'],0)
                c.execute('help');old=c.session.attempt['id'];c.restart('Challenge')
                self.assertNotEqual(c.session.attempt['id'],old)
                self.assertEqual(c.session.attempt['applied'],pack['initial_state']['WS-01'])
                self.assertFalse(c.session.attempt['draft']);self.assertFalse(c.session.attempt['console'])
                self.assertEqual(c.store.history(c.session.attempt['id'])[1],2)
                self.assertEqual(c.view['libraryBest'],'100/100')
        c.flush();r=self.catalog()
        self.assertEqual(r.pack['lab_id'],'subnet-boundary')
        for lab in r.labs.values():
            self.assertEqual(lab.view['libraryStatus'],'Completed')
            self.assertEqual(lab.view['historyCount'],2)
            self.assertEqual(lab.session.attempt['mode'],'Challenge')

    def test_switch_blocked_on_save_failure(self):
        c=self.catalog();c.edit('prefix','24')
        with patch.object(c.store,'save',side_effect=OSError('disk full')):
            self.assertFalse(c.selectLab('subnet-boundary',True))
        self.assertEqual(c.pack['lab_id'],'gateway-dns');self.assertTrue(c.view['canRetry'])
        c.retrySave();self.assertTrue(c.selectLab('subnet-boundary',True))

    def test_unknown_selection_preserved(self):
        for raw in ('{"schema_version":2,"future":true}','{','{"schema_version":1,"lab_id":[]}'):
            p=self.config/'selection.json';p.write_text(raw);c=self.catalog()
            self.assertIn('preserved',c.view['message']);c.selectLab('subnet-boundary',True)
            self.assertEqual(p.read_text(),raw)

    def test_corruption_and_newer_schema_both(self):
        for pack in (PACK,SUB):
            root=self.root/pack['lab_id'];s=Session(pack);store=Store(root,pack)
            store.save(s.attempt);s.hint();store.save(s.attempt)
            store.current.write_text('{broken')
            recovered=Store(root,pack);a=recovered.load()
            self.assertEqual(a['id'],s.attempt['id']);self.assertEqual(a['hints'],0)
            self.assertTrue(any(root.glob('current.corrupt-*')))
            newer=b'{"schema_version":99,"future":"keep"}';recovered.current.write_bytes(newer)
            future=Store(root,pack);self.assertIsNone(future.load());self.assertTrue(future.read_only)
            self.assertEqual(future.current.read_bytes(),newer)
