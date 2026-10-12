"""Metadata, exact preservation and independent bounds; not native guest evidence."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from learning_lab.vm_preview import registry
from learning_lab.vm_preview.image_catalog import Catalog, digest, production_catalog, read_json, resource
from learning_lab.vm_preview.sessions import Sessions
from platform_preservation import BASE, NEW_IDS, NEW_IMAGES, NEW_UNITS, projection

ROOT = Path(__file__).parents[2]


class PlatformExpansionTests(unittest.TestCase):
    def tearDown(self): registry._bundle.cache_clear()

    def test_actual_capacity_and_serialized_headroom(self):
        self.assertEqual((registry.MAX_UNITS, registry.MAX_TOTAL_LESSONS,
                          registry.MAX_LESSONS_PER_UNIT), (14, 120, 16))
        self.assertEqual((len(registry.units()), len(registry.entries())), (14, 120))
        c = production_catalog()
        self.assertEqual((len(c.lessons), len(c.default_images),
                          len(c._data['default_lessons'])), (120, 120, 120))
        self.assertGreaterEqual(65536 - len(resource('image-catalog.json')), 2048)
        self.assertFalse(c.keys or c.releases)
        for name in ('rpm-unit.json', 'foundation-unit.json'):
            self.assertLessEqual(len(resource(name)), 65536)
            read_json(resource(name))

    def test_original_resources_and_all_catalog_pins_exact(self):
        for name, sha in BASE['protected'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), sha, name)
        self.assertEqual(json.loads(projection('image-catalog.json', resource('image-catalog.json'))),
                         BASE['catalog'])
        c = production_catalog()
        for lid, revision in BASE['catalog']['default_lessons'].items():
            self.assertEqual(c._data['default_lessons'][lid], revision)
            self.assertEqual(c.default_images[lid], BASE['catalog']['default_images'][lid])
        self.assertEqual(len(c._data['lessons']), 120)

    def test_new_explicit_image_routes_no_fallback_and_display_only(self):
        c = production_catalog()
        with patch('subprocess.Popen', side_effect=AssertionError('host command')):
            for lid in sorted(NEW_IDS):
                spec, lesson = c.defaults(lid)
                expected = 'debian13-foundation-admin-local-v1' if lid.startswith('real-linux-foundation-') else 'almalinux9-rpm-admin-local-v1'
                self.assertEqual(spec['image_id'], expected)
                self.assertEqual(lesson, registry.load_lesson(lid))
                self.assertNotIn('score', lesson)
                self.assertIn('self-review', str(lesson).lower())
                for other in c.images.values():
                    if other['descriptor'] != spec:
                        with self.assertRaises(ValueError):
                            c.resolve({'backend': 'offline-qemu-preview-1', 'image': other['descriptor'],
                                       'lesson_sha256': digest(lesson)}, lid)
                removed = Catalog(c._data)
                del removed.images[digest(spec)]
                with self.assertRaisesRegex(ValueError, 'no substitute'): removed.defaults(lid)

    def test_registry_exact_overflow_before_resources(self):
        original = registry._read
        reads = []
        def changed(name):
            reads.append(name)
            value = copy.deepcopy(original(name))
            if name == 'units.json':
                value['units'].append({'id': 'fifteenth', 'resource': 'fifteenth.json'})
            return value
        with patch.object(registry, '_read', side_effect=changed), self.assertRaisesRegex(ValueError, '1–14'):
            registry.units()
        self.assertEqual(reads, ['units.json'])
        registry._bundle.cache_clear(); reads.clear()
        def total(name):
            reads.append(name); value = copy.deepcopy(original(name))
            if name == 'rpm-unit.json':
                extra = copy.deepcopy(value['entries'][0]); extra['id'] = 'fresh-overflow-id'
                extra['resource'] = 'fresh-overflow-id.json'; value['entries'].append(extra)
            return value
        with patch.object(registry, '_read', side_effect=total), self.assertRaisesRegex(ValueError, '120'):
            registry.units()
        self.assertNotIn('fresh-overflow-id.json', reads)

    def test_per_unit_sixteen_and_seventeen_independently(self):
        original = registry._read
        first = copy.deepcopy(original('unit.json')); last = copy.deepcopy(original('rpm-unit.json'))
        # Move eight unique resources, preserving total120 and every identity.
        last['entries'] += first['entries']; first['entries'] = []
        # Unit cannot be empty: instead move seven from first and one from resource unit.
        first = copy.deepcopy(original('unit.json')); second = copy.deepcopy(original('resource-unit.json'))
        last = copy.deepcopy(original('rpm-unit.json'))
        last['entries'] += first['entries'][1:] + second['entries'][:1]
        first['entries'] = first['entries'][:1]; second['entries'] = second['entries'][1:]
        changes = {'unit.json': first, 'resource-unit.json': second, 'rpm-unit.json': last}
        with patch.object(registry, '_read', side_effect=lambda n: copy.deepcopy(changes.get(n, original(n)))):
            self.assertEqual(len(registry.entries()), 120)
            self.assertEqual(len(registry.catalog('linux-rpm-offline-administration')['entries']), 16)
        registry._bundle.cache_clear(); last['entries'].append(copy.deepcopy(last['entries'][0]))
        with patch.object(registry, '_read', side_effect=lambda n: copy.deepcopy(changes.get(n, original(n)))), self.assertRaisesRegex(ValueError, '1–16'):
            registry.units()

    def test_retained_default_and_per_image_bounds(self):
        data = json.loads(resource('image-catalog.json')); Catalog(data)
        for field in ('lessons', 'default_lessons', 'default_images'):
            bad = copy.deepcopy(data)
            if field == 'lessons': bad[field].append({'id': 'fresh-retained', 'sha256': 'f'*64, 'resource': 'fresh.json', 'state': 'active'})
            else: bad[field]['fresh'] = 'f'*64
            with self.assertRaises(ValueError): Catalog(bad)
        # Default-image count is also constrained by exact key equality to the
        # bounded default-lesson map; it is not an independent larger capacity.
        pairs = data['images'][0]['lessons'][:]
        for row in data['lessons']:
            pair = {'id': row['id'], 'sha256': row['sha256']}
            if pair not in pairs: pairs.append(pair)
            if len(pairs) == 64: break
        ok = copy.deepcopy(data); ok['images'][0]['lessons'] = pairs; Catalog(ok)
        row = next(row for row in data['lessons'] if {'id': row['id'], 'sha256': row['sha256']} not in pairs)
        ok['images'][0]['lessons'].append({'id': row['id'], 'sha256': row['sha256']})
        with self.assertRaisesRegex(ValueError, 'compatibility'): Catalog(ok)
        for field in ('images', 'keys', 'releases'):
            bad = copy.deepcopy(data); bad[field] = [{}] * 65
            with self.assertRaisesRegex(ValueError, 'Catalog count'): Catalog(bad)

    def test_catalog_sixty_four_metadata_bounds_independently(self):
        # Synthetic catalog-only metadata. No signer/admission claim, no
        # key resource in normal operation or distributed package.
        data = json.loads(resource('image-catalog.json'))
        ok = copy.deepcopy(data)
        while len(ok['images']) < 64:
            row = copy.deepcopy(ok['images'][0])
            row['descriptor']['sha256'] = f"{len(ok['images'])+1000:064x}"
            ok['images'].append(row)
        Catalog(ok)
        synthetic = copy.deepcopy(data)
        synthetic['keys'] = [{'fingerprint': f'{n+1:040X}', 'resource': 'test-only-key'} for n in range(64)]
        Catalog(synthetic, read_resource=lambda _: b'TEST METADATA ONLY')
        synthetic['releases'] = [{'manifest_sha256': f'{n+1:064x}',
                                  'descriptor_sha256': data['default_image'],
                                  'signer': synthetic['keys'][0]['fingerprint'],
                                  'state': 'active'} for n in range(64)]
        Catalog(synthetic, read_resource=lambda _: b'TEST METADATA ONLY')
        for field in ('images', 'keys', 'releases'):
            overflow = copy.deepcopy(ok if field == 'images' else synthetic)
            overflow[field].append(copy.deepcopy(overflow[field][0]))
            with self.assertRaisesRegex(ValueError, 'Catalog count'):
                Catalog(overflow, read_resource=lambda _: b'TEST METADATA ONLY')

    def test_parser_boundaries_are_independent(self):
        read_json(b'{}' + b' ' * 65534)
        with self.assertRaisesRegex(ValueError, 'size'): read_json(b'{}' + b' ' * 65535)
        read_json(('['*32 + '0' + ']'*32).encode())
        with self.assertRaisesRegex(ValueError, 'nesting'): read_json(('['*33 + '0' + ']'*33).encode())
        read_json(json.dumps([0]*8191).encode())
        with self.assertRaisesRegex(ValueError, 'count'): read_json(json.dumps([0]*8192).encode())

    def test_new_metadata_modes_reopen_retained_reset_and_old_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); fake = root / 'fake'; fake.write_bytes(b'NOT A DISK')
            sessions = Sessions(root/'vm', 'a'*64, root/'gate')
            def reset(manager, mode):
                with patch.object(manager, 'admission'), patch.object(manager, 'image', side_effect=lambda _: os.open(fake, os.O_RDONLY)):
                    return manager.reset(mode, True)
            old = {}
            for lid in BASE['catalog']['default_lessons']:
                manager = sessions.manager(lid); reset(manager, 'Learn'); manager.progress('hint')
                path = root/'vm/profiles'/manager.profile/'current.json'; old[path] = path.read_bytes()
            for lid in sorted(NEW_IDS):
                manager = sessions.manager(lid); first = reset(manager, 'Learn')
                manager.progress('next'); manager.progress('hint'); manager.progress('complete')
                state = manager.status()['session']; self.assertEqual(state['completion']['kind'], 'self-reviewed')
                self.assertEqual(state, Sessions(root/'vm', 'a'*64, root/'gate').manager(lid).status()['session'])
                disk = root/'vm/profiles'/manager.profile/'generations'/first['generation']/'disk.qcow2'; before = disk.read_bytes()
                second = reset(manager, 'Challenge'); self.assertNotEqual(first['generation'], second['generation'])
                self.assertEqual(first['pin'], second['pin']); self.assertEqual(disk.read_bytes(), before)
                for action in ('next', 'hint'):
                    with self.assertRaises(ValueError): manager.progress(action)
            for path, data in old.items(): self.assertEqual(path.read_bytes(), data)

    def test_provenance_inventories_and_common_cleanup_are_exact(self):
        from platform_guest_fixtures import DATA
        index = json.loads((ROOT/'app/docs/vm-preview/platform-image-provenance.json').read_text())
        for name, resource_name in [('debian13-foundation-admin-local-v1','foundation-image.json'),
                                    ('almalinux9-rpm-admin-local-v1','rpm-image.json')]:
            row = index['evidence'][name]; spec = json.loads(resource(resource_name))
            self.assertEqual((spec['sha256'],spec['packages_sha256']),
                             (row['raw_sha256'],row['inventory_sha256']))
            raw=(ROOT/row['inventory_source']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['inventory_sha256'])
            self.assertEqual(len(raw.splitlines()),row['package_count'])
        self.assertEqual(len({tuple(f['cleanup']) for f in DATA if f['family']=='rpm'}),1)
        for f in DATA:
            if f['family']=='rpm':
                self.assertIn('printf',f['cleanup'][1])
                self.assertIn('| sudo "$h" apply "$op"',f['cleanup'][1])
            for field in ('negative_after_setup','negative_after_job'):
                for command in f[field]:
                    result=subprocess.run(['/usr/bin/bash','-n'],input=command+'\n',
                                          text=True,capture_output=True,timeout=5)
                    self.assertEqual(result.returncode,0,(f['content']['id'],field,result.stderr))

    def test_static_visible_commands_bash_syntax_only(self):
        # No learner execution here: -n parses trusted static developer fixtures.
        for lid in sorted(NEW_IDS):
            for index, step in enumerate(registry.load_lesson(lid)['steps']):
                result = subprocess.run(['/usr/bin/bash', '-n'], input=step['command']+'\n',
                                        text=True, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, (lid, index, result.stderr))

    def test_native_fixture_records_bind_exact_resources_and_entries(self):
        # Parse only the static literal. Do not run developer guest commands.
        path = Path(__file__).with_name('platform_guest_fixtures.py')
        tree = ast.parse(path.read_text())
        self.assertEqual(len(tree.body), 2)
        assignment = tree.body[1]
        self.assertIsInstance(assignment, ast.Assign)
        self.assertEqual([target.id for target in assignment.targets], ['DATA'])
        fixtures = ast.literal_eval(assignment.value)
        self.assertEqual({f['content']['id'] for f in fixtures}, NEW_IDS)
        self.assertEqual(len(fixtures), len(NEW_IDS))
        for fixture in fixtures:
            lid = fixture['content']['id']
            raw = resource(lid + '.json')
            self.assertEqual(hashlib.sha256(raw).hexdigest(),
                             fixture['resource_sha256'], lid)
            self.assertEqual(registry.load_lesson(lid), fixture['content'], lid)
            self.assertEqual(registry.entry(lid), fixture['entry'], lid)
            self.assertEqual(digest(fixture['entry']), fixture['entry_sha256'], lid)
            image, lesson = production_catalog().defaults(lid)
            self.assertEqual(image['image_id'], fixture['image_id'], lid)
            self.assertEqual(lesson, fixture['content'], lid)
            for index, command in enumerate(fixture['challenge']):
                parsed = subprocess.run(['/usr/bin/bash', '-n'],
                                        input=command + '\n', text=True,
                                        capture_output=True, timeout=5)
                self.assertEqual(parsed.returncode, 0, (lid, index, parsed.stderr))
