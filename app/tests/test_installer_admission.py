"""Synthetic preparation-plan tests; native Anaconda admission is separate."""
import importlib.util
import hashlib
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace as Object
import unittest

ROOT = Path(__file__).parents[1] / 'tools/vm_image/rpm'
spec = importlib.util.spec_from_file_location('installer_admission', ROOT / 'installer_admission.py')
gate = importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
spec = importlib.util.spec_from_file_location('patch_installer', ROOT / 'patch_installer.py')
patcher = importlib.util.module_from_spec(spec); spec.loader.exec_module(patcher)


class InstallerAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{'name': 'fixture' + str(i), 'arch': 'x86_64', 'epoch': '0',
                      'version': '1', 'release': '1'} for i in range(190)]
        self.items = [Object(pkg=Object(**row), action=1) for row in self.rows]

    def test_exact_multiset_and_equivalent_order(self):
        self.assertEqual(len(gate.admit_plan(self.items, self.rows, 1)), 190)
        self.assertEqual(len(gate.admit_plan(reversed(self.items), self.rows, 1)), 190)

    def test_count_duplicate_identity_and_action_refusals(self):
        for name, change in (
                ('missing', lambda xs: xs.pop()),
                ('duplicate', lambda xs: xs.__setitem__(0, xs[1])),
                ('upgrade', lambda xs: setattr(xs[0], 'action', 2)),
                ('unknown', lambda xs: setattr(xs[0].pkg, 'name', 'kexec-tools')),
                ('version', lambda xs: setattr(xs[0].pkg, 'version', '2'))):
            with self.subTest(name=name):
                items = [Object(pkg=Object(**row), action=1) for row in self.rows]
                change(items)
                with self.assertRaises(ValueError): gate.admit_plan(items, self.rows, 1)
        with self.assertRaises(ValueError): gate.admit_plan(self.items, self.rows[:-1], 1)
        duplicate = self.rows.copy(); duplicate[0] = duplicate[1]
        with self.assertRaises(ValueError): gate.admit_plan(self.items, duplicate, 1)

    def test_iteration_stops_at_first_overflow(self):
        visited = []
        def infinite():
            while True:
                visited.append(True)
                yield self.items[0]
        with self.assertRaisesRegex(ValueError, 'exceeds bound'):
            gate.admit_plan(infinite(), self.rows, 1)
        self.assertEqual(len(visited), 191)

    def test_manifest_bounds_and_leaf_symlink_refusal(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'input'; path.write_bytes(b'known')
            self.assertEqual(gate.read_bounded(path, 5), b'known')
            with self.assertRaises(ValueError): gate.read_bounded(path, 4)
            link = Path(root) / 'link'; link.symlink_to(path)
            with self.assertRaises(OSError): gate.read_bounded(link, 5)

    def test_unrecognized_installer_source_refused(self):
        with self.assertRaisesRegex(ValueError, 'verified Alma RPM'):
            patcher.patched(b'        base.do_transaction(display=display)\n')
        with self.assertRaises(ValueError): patcher.patched(b'')

    def test_payload_path_exact_member_and_traversal_refusal(self):
        prefix = '/run/install/sources/mount-0000-cdrom/Minimal/Packages/'
        self.assertEqual(gate.payload_path(prefix + 'known.rpm', {'file': 'known.rpm'}), prefix + 'known.rpm')
        for filename in ('../known.rpm', '/known.rpm', 'a/b.rpm', 'a\\b.rpm', 'bad\0.rpm'):
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                gate.payload_path(prefix + filename, {'file': filename})
        for path in ('/tmp/known.rpm', '/run/install/repo/Minimal/Packages/known.rpm',
                     prefix + 'other.rpm', prefix + '../Packages/known.rpm'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                gate.payload_path(path, {'file': 'known.rpm'})

    def test_real_payload_hash_size_and_type_refusals(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'known'; path.write_bytes(b'known')
            row = {'bytes': 5, 'sha256': hashlib.sha256(b'known').hexdigest()}
            with path.open('rb') as stream: gate.verify_payload(stream, row)
            for bad in ({**row, 'bytes': 4}, {**row, 'sha256': '0' * 64},
                        {**row, 'bytes': 0}, {**row, 'bytes': 256 * 1024**2 + 1}):
                with self.subTest(row=bad), path.open('rb') as stream, self.assertRaises(ValueError):
                    gate.verify_payload(stream, bad)
            fd = os.open(root, os.O_RDONLY)
            try:
                class DirectoryStream:
                    def fileno(self): return fd
                with self.assertRaises(ValueError): gate.verify_payload(DirectoryStream(), row)
            finally: os.close(fd)

    def test_actual_descriptor_mutation_refused_even_when_bytes_match(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'known'; path.write_bytes(b'known')
            row = {'bytes': 5, 'sha256': hashlib.sha256(b'known').hexdigest()}
            with path.open('rb') as source:
                class MutatingStream:
                    changed = False
                    def fileno(self): return source.fileno()
                    def read(self, size):
                        data = source.read(size)
                        if not self.changed:
                            os.utime(path, ns=(1, 1)); self.changed = True
                        return data
                with self.assertRaisesRegex(ValueError, 'changed during admission'):
                    gate.verify_payload(MutatingStream(), row)
