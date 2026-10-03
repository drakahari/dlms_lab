"""Checkpoint 1 parity and identity tests; all writes use temporary fixtures."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.domain.engine import Engine, load_catalog, load_pack
from learning_lab.legacy_scenario import (
    CompatibilityError, NETWORK_ENGINE, adapt_gateway_dns,
)
from learning_lab.scenario_identity import (
    CANONICALIZATION, IdentityError, canonical_content, content_digest,
)
from learning_lab.session import Session
from learning_lab.storage import Store, encode, validate_record
from test_lab import RAW, PACK, FIXED


def raw_pack(pack):
    return json.dumps(pack, ensure_ascii=False).encode('utf-8')


class CanonicalIdentityTests(unittest.TestCase):
    def test_known_canonical_bytes_and_digest(self):
        value = {'z': [3, True, None], 'a': 'é'}
        self.assertEqual(canonical_content(value), '{"a":"é","z":[3,true,null]}'.encode())
        self.assertEqual(content_digest(value),
                         'sha256:0c53765a3f019f951678673b2530db5ed0903eca29f596c006f3a99777eac0e8')

    def test_whitespace_key_order_and_escape_spelling_are_irrelevant(self):
        base = deepcopy(PACK)
        base['metadata']['brief'] += ' Café / resolver'
        original = adapt_gateway_dns(raw_pack(base))
        variants = [json.dumps(base, indent=4, sort_keys=True, ensure_ascii=True),
                    json.dumps(base, separators=(',', ':'), ensure_ascii=False),
                    json.dumps(base).replace('/', '\\/').replace('\n', '\r\n')]
        for variant in variants:
            with self.subTest(variant=variant[:40]):
                self.assertEqual(adapt_gateway_dns(variant.encode()).identity, original.identity)
        self.assertNotEqual(original.original_bytes, variants[0].encode())

    def test_all_pack_fields_are_covered_without_a_projection(self):
        baseline = content_digest(PACK)
        for field in PACK:
            changed = deepcopy(PACK)
            changed[field] = {'changed': changed[field]}
            with self.subTest(field=field):
                self.assertNotEqual(content_digest(changed), baseline)

    def test_meaningful_valid_changes_change_identity(self):
        variants = []
        for field in ('title', 'brief', 'difficulty', 'topic'):
            p = deepcopy(PACK); p['metadata'][field] += ' revised'; variants.append(p)
        p = deepcopy(PACK); p['metadata']['minutes'] += 1; variants.append(p)
        p = deepcopy(PACK); p['hints'][0] += ' Additional guidance.'; variants.append(p)
        p = deepcopy(PACK); p['hints'].reverse(); variants.append(p)
        p = deepcopy(PACK); p['initial_state']['WS-01']['gateway'] = '192.168.50.253'; variants.append(p)
        p = deepcopy(PACK); p['editable_fields']['WS-01'].remove('address'); variants.append(p)
        p = deepcopy(PACK); p['objectives'][0]['points'] = 10; p['objectives'][1]['points'] = 30; variants.append(p)
        p = deepcopy(PACK); p['objectives'][2]['params']['target'] = '10.20.0.1'; variants.append(p)
        p = deepcopy(PACK); p['topology']['devices'][2]['records']['alias.lab.test'] = '10.20.0.10'; variants.append(p)
        baseline = adapt_gateway_dns(RAW).identity
        for index, changed in enumerate(variants):
            with self.subTest(index=index):
                identity = adapt_gateway_dns(raw_pack(changed)).identity
                self.assertEqual(identity.content_version, baseline.content_version)
                self.assertNotEqual(identity.content_digest, baseline.content_digest)

    def test_array_order_and_exact_unicode_are_preserved(self):
        self.assertNotEqual(content_digest(['a', 'b']), content_digest(['b', 'a']))
        self.assertNotEqual(content_digest('é'), content_digest('e\u0301'))
        self.assertNotEqual(content_digest('a\nb'), content_digest('a\r\nb'))

    def test_noncanonical_types_and_resource_limits_fail(self):
        values = [1.0, float('nan'), float('inf'), (1, 2), {1: 'key'}, '\ud800',
                  2 ** 63, -(2 ** 63) - 1, 'x' * 262145]
        nested = None
        for _ in range(33): nested = [nested]
        values.append(nested)
        for value in values:
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(IdentityError): canonical_content(value)

    def test_identity_contract_does_not_impose_hint_count(self):
        for count in (0, 1, 3, 7):
            value = {'hints': [f'Hint {i}' for i in range(count)]}
            self.assertEqual(json.loads(canonical_content(value)), value)
        # The untouched legacy format still requires its original three hints.
        p = deepcopy(PACK); p['hints'].pop()
        with self.assertRaises(CompatibilityError): adapt_gateway_dns(raw_pack(p))


class LegacyAdapterTests(unittest.TestCase):
    def test_versions_are_distinct_and_content_versions_are_not_engine_versions(self):
        scenario = adapt_gateway_dns(RAW)
        self.assertEqual(scenario.identity.format_version, 1)
        self.assertEqual(scenario.identity.content_version, '1.0.0')
        self.assertEqual(scenario.identity.canonicalization, CANONICALIZATION)
        self.assertEqual(scenario.runtime.contract_version, 1)
        self.assertEqual(scenario.runtime.behavior_version, 'legacy-1')
        p = deepcopy(PACK); p['content_version'] = '2.0.0'
        updated = adapt_gateway_dns(raw_pack(p))
        self.assertEqual(updated.runtime, scenario.runtime)
        self.assertEqual(updated.identity.format_version, 1)
        self.assertNotEqual(updated.identity.content_digest, scenario.identity.content_digest)

    def test_unsupported_format_contract_behavior_and_capabilities_rejected(self):
        for version in (0, 2, 99, True, '1'):
            p = deepcopy(PACK); p['schema_version'] = version
            with self.subTest(format=version), self.assertRaises(CompatibilityError):
                adapt_gateway_dns(raw_pack(p))
        for runtime in (replace(NETWORK_ENGINE, engine_id='unknown'),
                        replace(NETWORK_ENGINE, contract_version=2),
                        replace(NETWORK_ENGINE, contract_version=True),
                        replace(NETWORK_ENGINE, behavior_version='legacy-2'), None):
            with self.subTest(runtime=runtime), self.assertRaises(CompatibilityError):
                adapt_gateway_dns(RAW, runtime=runtime)
        p = deepcopy(PACK); p['required_capabilities'].append('arbitrary-code')
        with self.assertRaises(CompatibilityError): adapt_gateway_dns(raw_pack(p))

    def test_invalid_input_and_unsupported_scenarios_rejected(self):
        p = deepcopy(PACK); p['content_version'] = 'latest'
        wrong_id = deepcopy(PACK); wrong_id['lab_id'] = 'other-scenario'
        variants = [b'{', b'[]', RAW.decode(), RAW.decode().encode('utf-16'),
                    b'\xef\xbb\xbf' + RAW, b'x' * 262145, raw_pack(p), raw_pack(wrong_id),
                    RAW.replace(b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1'),
                    RAW.replace(b'"minutes": 15', b'"minutes": 15.0'),
                    RAW.replace(b'"minutes": 15', b'"minutes": NaN')]
        for index, raw in enumerate(variants):
            with self.subTest(index=index), self.assertRaises(CompatibilityError):
                adapt_gateway_dns(raw)

    def test_adapter_is_immutable_and_preserves_original_order_and_hints(self):
        s = adapt_gateway_dns(RAW)
        self.assertEqual(s.original_bytes, RAW)
        self.assertEqual(s.legacy_pack(), PACK)
        self.assertEqual(list(s.legacy_pack()), list(PACK))
        self.assertEqual(s.legacy_pack()['hints'], PACK['hints'])
        copy = s.legacy_pack(); copy['hints'].clear()
        self.assertEqual(s.legacy_pack()['hints'], PACK['hints'])
        with self.assertRaises(FrozenInstanceError): s.identity.content_version = '9.0.0'
        with self.assertRaises(FrozenInstanceError): s.original_bytes = b'{}'

    def test_gateway_engine_and_session_parity(self):
        adapted = adapt_gateway_dns(RAW).legacy_pack()
        for changes, expected in (({}, 40), ({'gateway': '192.168.50.1'}, 70),
                                  ({'dns': '10.20.0.10'}, 40), (FIXED, 100)):
            state = {**PACK['initial_state']['WS-01'], **changes}
            old, new = Engine(PACK, state), Engine(adapted, state)
            self.assertEqual(new.grade(), old.grade())
            self.assertEqual(new.grade()['score'], expected)
            for cmd in ('help', 'ipconfig', 'ip route', 'ping 10.20.0.10',
                        'nslookup portal.lab.test', 'traceroute portal.lab.test', '$(id)'):
                self.assertEqual(new.command(cmd), old.command(cmd))
        original = Session(PACK)
        a, b = Session(PACK, original.attempt), Session(adapted, original.attempt)
        for s in (a, b):
            s.edit('gateway', '192.168.50.1'); s.test(); s.hint()
        for field in ('applied', 'draft', 'console', 'hints', 'revision'):
            self.assertEqual(a.attempt[field], b.attempt[field])
        a.apply(); b.apply()
        self.assertEqual(a.engine.grade(), b.engine.grade())

    def test_bundled_loading_preserves_all_three_packs(self):
        packs, scenario = load_bundled_scenarios()
        folder = Path(__file__).resolve().parents[1] / 'learning_lab/packs'
        old = load_catalog([(folder / name).read_bytes() for name in
                            ('gateway-dns.json', 'subnet-boundary.json', 'service-firewall.json')])
        self.assertEqual(packs, old)
        self.assertEqual(scenario.identity.scenario_id, 'gateway-dns')
        for before, after in zip(old, packs):
            self.assertEqual(Engine(before).grade(), Engine(after).grade())

    def test_legacy_records_and_storage_paths_unchanged_in_isolated_fixture(self):
        # No personal progress is a test fixture. Generate legacy-format records.
        from test_bridge import APP
        packs, scenario = load_bundled_scenarios()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / 'data'; config = root / 'config'; config.mkdir()
            for pack in packs:
                folder = data if pack['lab_id'] == 'gateway-dns' else data / 'labs' / pack['lab_id']
                store = Store(folder, pack)
                session = Session(pack); session.hint(); session.submit()
                if pack['lab_id'] == 'gateway-dns': session.edit('gateway', 'unfinished draft')
                store.save(session.attempt)
                store.archive(session.archived('reset'))
            before = {str(p.relative_to(data)): p.read_bytes() for p in data.rglob('*.json')}
            catalog = CatalogBridge(packs, data, config)
            try:
                self.assertEqual(catalog.labs['gateway-dns'].store.root, data)
                for lab_id in ('subnet-boundary', 'service-firewall'):
                    self.assertEqual(catalog.labs[lab_id].store.root, data / 'labs' / lab_id)
                catalog.flush()
                after = {str(p.relative_to(data)): p.read_bytes() for p in data.rglob('*.json')}
                self.assertEqual(before, after)
                for name, raw in after.items():
                    record = json.loads(raw)
                    self.assertNotIn('content_digest', record['attempt'])
                    self.assertNotIn('engine_version', record['attempt'])
                    self.assertNotIn('runtime', record['attempt'])
                    pack = next(p for p in packs if p['lab_id'] == record['attempt']['lab_id'])
                    self.assertEqual(encode(validate_record(raw, pack)), raw)
            finally:
                for lab in catalog.labs.values(): lab.timer.stop()

    def test_adapter_and_record_validation_do_not_rewrite_noncanonical_json(self):
        session = Session(PACK); session.submit()
        raw = json.dumps(json.loads(encode(session.attempt)), sort_keys=True, indent=4).encode()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'current.json'; path.write_bytes(raw)
            pack = adapt_gateway_dns(RAW).legacy_pack()
            validate_record(path.read_bytes(), pack)
            self.assertEqual(path.read_bytes(), raw)

    def test_offscreen_startup_uses_adapter_with_isolated_data(self):
        # Separate process because controller tests already own QCoreApplication.
        import os
        with tempfile.TemporaryDirectory() as tmp:
            code = '''
import sys
from pathlib import Path
from learning_lab.__main__ import build_application
root = Path(sys.argv[1])
app, engine, bridge, lock = build_application(root/'data', root/'config')
assert app.platformName() == 'offscreen'
assert engine.rootObjects()
assert bridge.gateway_scenario.identity.scenario_id == 'gateway-dns'
assert len(bridge.labs) == 3
assert bridge.pack == bridge.gateway_scenario.legacy_pack()
engine.rootObjects()[0].close()
app.processEvents()
lock.unlock()
print('ISOLATED_STARTUP_PASS')
'''
            env = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QPA_PLATFORMTHEME='',
                       QT_QUICK_BACKEND='software', PYTHONDONTWRITEBYTECODE='1',
                       XDG_CACHE_HOME=str(Path(tmp) / 'cache'))
            result = subprocess.run([sys.executable, '-B', '-c', code, tmp],
                                    cwd=Path(__file__).resolve().parents[1], env=env,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('ISOLATED_STARTUP_PASS', result.stdout)


if __name__ == '__main__':
    unittest.main()
