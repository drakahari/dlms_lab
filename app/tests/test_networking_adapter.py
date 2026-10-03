import json
from pathlib import Path
import tempfile
import unittest
from PySide6.QtCore import QCoreApplication
from learning_lab.catalog import CatalogBridge
from learning_lab.domain.engine import load_pack
from learning_lab.networking import NetworkingDomain, TRUSTED_ENGINES
from learning_lab.session import Session
from test_lab import RAW, FIXED

APP = QCoreApplication.instance() or QCoreApplication([])


class NetworkingAdapterTests(unittest.TestCase):
    def pack(self):
        return load_pack(RAW.replace(b'gateway-dns', b'renamed-fixture').replace(b'WS-01', b'CLIENT-7').replace(b'portal.lab.test', b'inventory.lab.test'))

    def test_source_and_diagnostics_are_pack_driven(self):
        pack = self.pack(); domain = NetworkingDomain(pack)
        session = Session(pack, domain=domain)
        self.assertEqual(domain.source, 'CLIENT-7')
        self.assertIn('CLIENT-7', session.engine.command('help'))
        self.assertNotIn('WS-01', session.engine.command('ipconfig'))
        for key, value in FIXED.items(): session.edit(key, str(value))
        session.apply()
        rows = session.test()
        self.assertTrue(all(r['ok'] for r in rows))
        self.assertIn('inventory.lab.test', json.dumps(rows))
        self.assertNotIn('portal.lab.test', json.dumps(rows))
        self.assertEqual(session.submit()['score'], 100)

    def test_catalog_has_no_scenario_specific_root_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); pack = self.pack()
            catalog = CatalogBridge([pack], root/'data', root/'config')
            try:
                self.assertEqual(catalog.view['sourceDevice'], 'CLIENT-7')
                self.assertEqual(catalog.store.root, root/'data/labs/renamed-fixture')
                self.assertEqual(catalog.view['workspaceKind'], 'networking')
                self.assertEqual(catalog.view['hintTotal'], 3)
                self.assertEqual(catalog.view['topologyNodes'][0]['id'], 'CLIENT-7')
                self.assertNotIn('firewall', catalog.view['workspaceTools'])
            finally: catalog.active.timer.stop()

    def test_multiple_names_and_explicit_diagnostics(self):
        pack=self.pack()
        checks=[{'id':'name','label':'Check the name','operation':'resolve','hostname':'inventory.lab.test'},
                {'id':'route','label':'Check route','operation':'reach','target':'10.20.0.10'}]
        domain=NetworkingDomain(pack, diagnostics=checks, constraints=['Preserve the address'])
        rows=domain.diagnose(FIXED)
        self.assertEqual([r['id'] for r in rows], ['name','route'])
        self.assertTrue(all(r['ok'] for r in rows))
        self.assertEqual(domain.presentation(FIXED,'CLIENT-7')['constraints'], ['Preserve the address'])
        self.assertEqual(set(TRUSTED_ENGINES), {'networking'})
