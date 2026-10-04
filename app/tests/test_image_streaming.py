"""Streaming test builder checks; no production trust or guest launch."""
import copy, hashlib, os, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from offline_image_fixtures import SigningFixture, stream_bundle, file_hash
from learning_lab.vm_preview.image_bundle import validate_bundle, import_bundle
from learning_lab.vm_preview.policy import image_spec


@unittest.skipUnless(shutil.which('gpg') and shutil.which('gpgv'), 'GnuPG test tools unavailable')
class StreamingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.signer=SigningFixture()
    @classmethod
    def tearDownClass(cls): cls.signer.close()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.source=self.root/'source.raw';self.source.write_bytes(os.urandom(2*1024**2+31));self.source.chmod(0o444)
        self.spec=copy.deepcopy(image_spec());self.spec.update(image_id='streaming-test-only',bytes=self.source.stat().st_size,sha256=file_hash(self.source))
        self.path=self.root/'bundle.llvmimage'
    def tearDown(self):self.temp.cleanup()
    def test_bounded_stream_round_trip_and_noop(self):
        counts=[];catalog,manifest,compressed=stream_bundle(self.signer,self.path,self.source,self.spec,progress=counts.append)
        self.assertEqual(manifest['descriptor'],self.spec);self.assertEqual(counts[-1],self.spec['bytes']);self.assertGreater(len(counts),2)
        self.assertEqual(validate_bundle(self.path,_catalog=catalog)['result'],'valid')
        home=self.root/'vm';kwargs={'_catalog':catalog,'_gate_root':self.root/'gate'}
        self.assertEqual(import_bundle(self.path,home,**kwargs)['result'],'installed')
        target=home/'images'/self.spec['sha256']/'base.raw'
        self.assertEqual(file_hash(target),self.spec['sha256']);identity=target.stat().st_ino
        self.assertEqual(import_bundle(self.path,home,**kwargs)['result'],'already-installed')
        self.assertEqual(target.stat().st_ino,identity);self.assertEqual(file_hash(self.source),self.spec['sha256'])
        with self.assertRaisesRegex(ValueError,'allowlist'):validate_bundle(self.path)
    def test_exact_pin_and_readonly_required(self):
        self.source.chmod(0o600)
        with self.assertRaisesRegex(ValueError,'read-only'):stream_bundle(self.signer,self.path,self.source,self.spec)
        self.source.chmod(0o444);self.spec['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'exact pin'):stream_bundle(self.signer,self.path,self.source,self.spec)
        self.assertFalse(self.path.exists());self.assertTrue(self.path.with_suffix('.raw.gz').exists())
    def test_existing_outputs_preserved(self):
        self.path.write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):stream_bundle(self.signer,self.path,self.source,self.spec)
        self.assertEqual(self.path.read_bytes(),b'preserve')
    def test_compressed_limit_enforced_during_write(self):
        with patch('offline_image_fixtures.STREAM_GZIP_LIMIT',128):
            with self.assertRaisesRegex(ValueError,'compressed-size'):stream_bundle(self.signer,self.path,self.source,self.spec)
        self.assertLessEqual(self.path.with_suffix('.raw.gz').stat().st_size,128)
        self.assertFalse(self.path.exists())
