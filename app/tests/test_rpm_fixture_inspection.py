"""Small synthetic RPM fixtures; native builder output is checked separately."""
import gzip
import importlib.util
import io
import stat
import struct
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / 'tools/vm_image/rpm'
spec = importlib.util.spec_from_file_location('fixture_inspection', TOOL / 'inspect_fixtures.py')
guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)


def encoded_header(values):
    data = bytearray(); indexes = []
    for tag, value in values.items():
        start = len(data)
        if isinstance(value, str):
            kind, count = 6, 1; data.extend(value.encode() + b'\0')
        elif isinstance(value, bytes):
            kind, count = 7, len(value); data.extend(value)
        elif value and isinstance(value[0], str):
            kind, count = 8, len(value)
            for item in value: data.extend(item.encode() + b'\0')
        else:
            kind, count = 4, len(value)
            for item in value: data.extend(struct.pack('>I', item))
        indexes.append(struct.pack('>IIII', tag, kind, start, count))
    return b'\x8e\xad\xe8\x01\0\0\0\0' + struct.pack('>II', len(indexes), len(data)) + b''.join(indexes) + data


class FixtureInspectionTests(unittest.TestCase):
    def fixture(self, root, mutate=lambda h: None, trailer=b'', member_override=None):
        import hashlib
        sources = TOOL / 'fixtures'
        entries = [
            ('/etc/learning-lab-rpm', stat.S_IFDIR | 0o755, 0, b''),
            ('/etc/learning-lab-rpm/report.conf', stat.S_IFREG | 0o644, 17,
             (sources / 'data-1.0/report.conf').read_bytes()),
            ('/usr/share/learning-lab-rpm', stat.S_IFDIR | 0o755, 0, b''),
            ('/usr/share/learning-lab-rpm/data.txt', stat.S_IFREG | 0o644, 0,
             (sources / 'data-1.0/data.txt').read_bytes()),
            ('/usr/share/licenses/ll-rpm-data/LICENSE', stat.S_IFREG | 0o644, 128,
             (sources / 'LICENSE').read_bytes()),
        ]
        h = {1000: 'll-rpm-data', 1001: '1.0', 1002: '1', 1022: 'noarch',
             1006: [guard.EPOCH], 5011: [8], 1124: 'cpio', 1125: 'gzip',
             1028: [len(row[3]) for row in entries],
             1030: [row[1] for row in entries], 1033: [0]*5,
             1034: [guard.EPOCH]*5,
             1035: [hashlib.sha256(row[3]).hexdigest() if stat.S_ISREG(row[1]) else '' for row in entries],
             1036: ['']*5, 1037: [row[2] for row in entries],
             1039: ['root']*5, 1040: ['root']*5,
             1049: ['config(ll-rpm-data)', 'rpmlib(CompressedFileNames)', 'rpmlib(FileDigests)', 'rpmlib(PayloadFilesHavePrefix)'],
             1048: [268435464, 16777226, 16777226, 16777226],
             1050: ['1.0-1', '3.0.4-1', '4.6.0-1', '4.0-1'],
             1116: list(range(5)), 1117: [Path(row[0]).name for row in entries],
             1118: [str(Path(row[0]).parent)+'/' for row in entries]}
        mutate(h)
        raw = bytearray()
        def member(name, mode, content):
            encoded = name.encode()+b'\0'
            fields = [1, mode, 0, 0, 1, guard.EPOCH, len(content), 0, 0, 0, 0, len(encoded), 0]
            raw.extend(b'070701'+b''.join(f'{field:08x}'.encode() for field in fields)+encoded)
            raw.extend(b'\0'*(-len(raw)%4)); raw.extend(content);raw.extend(b'\0'*(-len(raw)%4))
        for n, (name, mode, _, content) in enumerate(entries):
            member(member_override if n==0 and member_override else '.'+name, mode, content)
        member('TRAILER!!!', 0, b''); raw.extend(trailer)
        lead=b'\xed\xab\xee\xdb\x03\0'+b'\0'*90
        signature=encoded_header({1000: b'\0'*4096})
        prefix=lead+signature;prefix+=b'\0'*(-len(prefix)%8)
        path=root/guard.NAMES[0]
        path.write_bytes(prefix+encoded_header(h)+gzip.compress(bytes(raw),mtime=0))
        return path

    def test_positive_bounded_payload_and_reserved_signature_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            record=guard.inspect(self.fixture(Path(tmp)),TOOL/'fixtures')
            self.assertEqual(record['fixed_epoch'],guard.EPOCH)
            self.assertEqual(len(record['paths']),5)

    def test_verify_script_and_unknown_tag_refused(self):
        for tag in (1079, 5089, 60000):
            with self.subTest(tag=tag), tempfile.TemporaryDirectory() as tmp:
                path=self.fixture(Path(tmp),lambda h:h.update({tag:'echo forbidden'}))
                with self.assertRaisesRegex(ValueError,'metadata or executable'):
                    guard.inspect(path,TOOL/'fixtures')

    def test_parallel_arrays_wrong_mode_and_unpinned_time_refused(self):
        for change in (lambda h:h[1048].pop(),lambda h:h[1030].pop(),
                       lambda h:h[1030].__setitem__(1,stat.S_IFREG|0o4755),
                       lambda h:h[1006].__setitem__(0,guard.EPOCH+1)):
            with tempfile.TemporaryDirectory() as tmp:
                path=self.fixture(Path(tmp),change)
                with self.assertRaises(ValueError):guard.inspect(path,TOOL/'fixtures')

    def test_escaping_member_and_payload_tail_refused(self):
        for kwargs in ({'member_override':'../escape'},{'trailer':b'x'}):
            with tempfile.TemporaryDirectory() as tmp:
                path=self.fixture(Path(tmp),**kwargs)
                with self.assertRaises(ValueError):guard.inspect(path,TOOL/'fixtures')

    def test_header_bounds_duplicate_and_truncation(self):
        value=encoded_header({1000:'value'})
        with self.assertRaises(ValueError):guard.header(io.BytesIO(value[:-1]),0)
        raw=b'\x8e\xad\xe8\x01\0\0\0\0'+struct.pack('>II',1025,1)
        with self.assertRaisesRegex(ValueError,'bounds'):guard.header(io.BytesIO(raw),0)

    def test_leaf_symlink_and_oversize_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/guard.NAMES[0];path.symlink_to(root/'missing')
            with self.assertRaises(OSError):guard.inspect(path,TOOL/'fixtures')
            path.unlink();path.write_bytes(b'x'*131073)
            with self.assertRaisesRegex(ValueError,'type/size'):guard.inspect(path,TOOL/'fixtures')
