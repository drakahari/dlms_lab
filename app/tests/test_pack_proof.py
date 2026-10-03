"""Frozen-application proof fixtures; these tests never use the owner's profile."""
import hashlib,json
from pathlib import Path
import tempfile
import unittest
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.portable import load_portable,PackRepository
from learning_lab.session import Session

APP=QCoreApplication.instance() or QCoreApplication([])
ROOT=Path(__file__).resolve().parents[1]

class PackProofTests(unittest.TestCase):
    def test_networking_core_and_original_packs_match_historical_freeze(self):
        # The complete application freeze proves the earlier data-only authoring
        # milestone. A new trusted engine changes the application intentionally;
        # keep the manifest as historical evidence, without rewriting its hashes.
        manifest=json.loads((ROOT/'evidence/proof-code-freeze.json').read_bytes())
        protected={name:digest for name,digest in manifest['files'].items() if name.startswith(('learning_lab/domain/','learning_lab/packs/'))}
        self.assertTrue(protected)
        for name,digest in protected.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        self.assertNotIn('resolver-misdirection', ''.join(p.read_text() for p in (ROOT/'learning_lab').rglob('*.py')))

    def test_data_only_proof_end_to_end(self):
        scenarios=[load_portable((ROOT/'examples'/name).read_bytes()) for name in ('gateway-dns.lab.json','resolver-misdirection.lab.json')]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);data=root/'data';config=root/'config';config.mkdir()
            b=CatalogBridge(load_bundled_scenarios()[0],data,config);catalogs=[b]
            try:
                original={str(p.relative_to(data)):p.read_bytes() for p in data.rglob('*.json')}
                for scenario in scenarios:
                    name=scenario.identity.scenario_id;incoming=root/(name+'.lab.json');incoming.write_bytes(scenario.original_bytes)
                    self.assertTrue(b.importPack(str(incoming)));self.assertTrue(b.selectLab(scenario.key,True))
                    baseline=b.session.engine.grade()['score'];b.test();b.hint();b.hint();b.submit()
                    if name=='gateway-dns':fix={'gateway':'192.168.50.1','dns':'10.20.0.10'}
                    else:
                        fix={'dns':'172.22.20.10'}
                        self.assertEqual(baseline,40)
                        for ip in ('172.22.8.1','172.22.20.10','172.22.20.20'):self.assertTrue(b.session.engine.reach(ip).ok)
                        for name in ('inventory.lab.test','orders.lab.test'):
                            self.assertTrue(b.session.engine.resolve(name)[0].ok);self.assertFalse(b.session.engine.portal(name).ok)
                        self.assertEqual(b.view['sourceDevice'],'CLIENT-7');self.assertEqual(len(b.view['topologyNodes']),4)
                    old=b.session.attempt['id']
                    for field,value in fix.items():b.edit(field,value)
                    self.assertEqual(b.session.engine.grade()['score'],baseline)
                    b.apply();b.test();b.submit();self.assertEqual(b.view['grade']['score'],100)
                    raw=b.store.current.read_bytes();b.submit();self.assertEqual(b.store.current.read_bytes(),raw)
                    b.restart('Challenge');b.hint();self.assertEqual(b.view['hintCount'],0)
                    rows,_,_=b.store.history(b.session.attempt['id']);self.assertEqual(rows[0]['id'],old);self.assertEqual(rows[0]['hints'],2)
                    for field,value in fix.items():b.edit(field,value)
                    b.apply();b.submit();self.assertEqual(b.view['grade']['score'],100)
                    challenge=b.session.attempt['id'];b.edit('dns','pending invalid draft');b.setCommandDraft('help');b.flush()
                    for lab in b.labs.values():lab.timer.stop()
                    fresh=CatalogBridge(load_bundled_scenarios()[0],data,config);catalogs.append(fresh);b=fresh
                    self.assertEqual(fresh.view['labKey'],scenario.key);self.assertEqual(fresh.session.attempt['id'],challenge)
                    self.assertEqual(fresh.view['mode'],'Challenge');self.assertEqual(fresh.view['inputs']['dns'],'pending invalid draft');self.assertEqual(fresh.view['commandDraft'],'help')
                    self.assertEqual(fresh.store.scenario.pin,scenario.pin)
                    export=root/(scenario.identity.scenario_id+'-export.lab.json');self.assertTrue(fresh.exportScenario(str(export)))
                    self.assertEqual(export.read_bytes(),scenario.original_bytes);self.assertNotIn(challenge,export.read_text())
                    imported,added=PackRepository(root/('reimport-'+scenario.identity.scenario_id)).import_file(export)
                    self.assertTrue(added);self.assertEqual(imported.identity,scenario.identity)
                    self.assertEqual(Session(imported.legacy_pack(),domain=imported.domain()).engine.grade()['score'],baseline)
                    fresh.restart('Challenge');self.assertEqual(fresh.view['inputs']['dns'],str(next(iter(scenario.legacy_pack()['initial_state'].values()))['dns']))
                    self.assertEqual(fresh.store.history(fresh.session.attempt['id'])[1],2)
                    for lab in fresh.labs.values():lab.timer.stop()
                for name,raw in original.items():self.assertEqual((data/name).read_bytes(),raw)
                bad=root/'invalid.lab.json';p=scenarios[-1].value();p['engine']['contract_version']=99;bad.write_text(json.dumps(p))
                before={str(p.relative_to(data)):p.read_bytes() for p in data.rglob('*.json')}
                self.assertFalse(b.importPack(str(bad)))
                self.assertEqual(before,{str(p.relative_to(data)):p.read_bytes() for p in data.rglob('*.json')})
                self.assertEqual(len(b.labs),5)
            finally:
                for catalog in catalogs:
                    for lab in catalog.labs.values():lab.timer.stop()

    def test_other_portable_examples_match_originals(self):
        for original in load_bundled_scenarios()[0]:
            scenario=load_portable((ROOT/'examples'/(original['lab_id']+'.lab.json')).read_bytes())
            self.assertEqual(scenario.legacy_pack(),original)
            self.assertEqual(Session(scenario.legacy_pack()).engine.grade(),Session(original).engine.grade())
