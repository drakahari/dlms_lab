"""Real descriptor enumeration; optional OLL_ENUM_TEST_ROOT tests another filesystem.
All directories are new isolated fixtures. No existing VM/profile files are used.
"""
import os, tempfile, threading, unittest
from pathlib import Path
from unittest.mock import patch
from learning_lab.vm_preview.files import Directory, Refused
from learning_lab.vm_preview.image_bundle import seal_directory, verify_identity, same_installation


class DirectoryNamesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='enum-regression-',dir=os.environ.get('OLL_ENUM_TEST_ROOT'))
        self.root=Path(self.temp.name);self.d=Directory.absolute(self.root)
    def tearDown(self):self.d.close();self.temp.cleanup()
    def add(self,name):
        fd=self.d.open(name,True,True)
        try:os.write(fd,b'fixture');os.fsync(fd)
        finally:os.close(fd)
        os.fsync(self.d.fd)
    def test_first_and_repeated_after_population(self):
        # No lseek before first call: even SEEK_CUR can refresh FS enumeration state.
        for n in ('a','b','c'):self.add(n)
        for _ in range(3):self.assertEqual(set(self.d.names()),{'a','b','c'})
    def test_prior_empty_enumeration_and_later_mutations(self):
        self.assertEqual(self.d.names(),[]);self.add('a')
        self.assertEqual(self.d.names(),['a']);self.add('b')
        self.assertEqual(set(self.d.names()),{'a','b'})
        os.unlink('a',dir_fd=self.d.fd);self.assertEqual(self.d.names(),['b'])
    def test_independent_description_preserves_original_offset(self):
        self.add('a');os.lseek(self.d.fd,2,os.SEEK_SET)
        before=(Path('/proc/self/fdinfo')/str(self.d.fd)).read_text()
        self.assertEqual(self.d.names(),['a'])
        self.assertEqual((Path('/proc/self/fdinfo')/str(self.d.fd)).read_text(),before)
    def test_closed_descriptor_cannot_enumerate_cwd_or_reused_fd(self):
        self.d.close()
        with self.assertRaisesRegex(Refused,'closed'):self.d.names()
    def test_reused_descriptor_identity_rejected(self):
        other=self.root/'other';other.mkdir(mode=0o700)
        fd=os.open(other,os.O_RDONLY|os.O_DIRECTORY)
        try:
            os.dup2(fd,self.d.fd)
            with self.assertRaisesRegex(Refused,'identity'):self.d.names()
        finally:os.close(fd)
    def test_path_substitution_stays_with_original_directory(self):
        self.add('original');moved=self.root.with_name(self.root.name+'-moved')
        self.root.rename(moved)
        try:
            self.root.symlink_to('/tmp',target_is_directory=True)
            self.assertEqual(self.d.names(),['original'])
        finally:self.root.unlink();moved.rename(self.root)
    def test_reopen_substitution_rejected(self):
        other=self.root/'other';other.mkdir(mode=0o700);real_open=os.open
        def substitute(path,*args,**kwargs):
            if path=='.':return real_open(other,os.O_RDONLY|os.O_DIRECTORY)
            return real_open(path,*args,**kwargs)
        with patch('learning_lab.vm_preview.files.os.open',side_effect=substitute):
            with self.assertRaisesRegex(Refused,'identity'):self.d.names()
    def test_concurrent_mutation_rejected_without_retry(self):
        self.add('a');real_listdir=os.listdir;ready=threading.Event();done=threading.Event()
        def writer():
            ready.wait();self.add('unexpected');done.set()
        thread=threading.Thread(target=writer);thread.start()
        def listing(fd):
            result=real_listdir(fd);ready.set();self.assertTrue(done.wait(5));return result
        try:
            with patch('learning_lab.vm_preview.files.os.listdir',side_effect=listing) as call:
                with self.assertRaisesRegex(Refused,'changed during'):self.d.names()
                self.assertEqual(call.call_count,1)
        finally:ready.set();thread.join(5)
    def test_concurrent_enumerators_have_independent_offsets(self):
        for i in range(50):self.add(str(i))
        expected={str(i) for i in range(50)};results=[];errors=[]
        def reader():
            try:results.append(set(self.d.names()))
            except BaseException as e:errors.append(e)
        threads=[threading.Thread(target=reader) for _ in range(8)]
        for t in threads:t.start()
        for t in threads:t.join()
        self.assertFalse(errors);self.assertEqual(results,[expected]*8)
    def test_exact_member_guard_preserved(self):
        self.add('a');seal=seal_directory(self.d);self.assertEqual(set(seal),{'a'})
        verify_identity(self.d,seal);same_installation(self.d,seal)
        self.add('unexpected')
        with self.assertRaisesRegex(Refused,'members changed'):verify_identity(self.d,seal)
        with self.assertRaisesRegex(Refused,'members/legacy'):same_installation(self.d,seal)
        os.unlink('unexpected',dir_fd=self.d.fd);os.unlink('a',dir_fd=self.d.fd)
        with self.assertRaisesRegex(Refused,'members changed'):verify_identity(self.d,seal)
    def test_member_symlink_and_identity_substitution_rejected(self):
        self.add('a');seal=seal_directory(self.d)
        os.rename('a','old',src_dir_fd=self.d.fd,dst_dir_fd=self.d.fd);self.add('a');os.unlink('old',dir_fd=self.d.fd)
        with self.assertRaisesRegex(Refused,'member changed'):verify_identity(self.d,seal)
        os.unlink('a',dir_fd=self.d.fd);os.symlink('/etc/passwd','a',dir_fd=self.d.fd)
        with self.assertRaises(OSError):seal_directory(self.d)
    def test_ownership_mode_change_rejected(self):
        os.fchmod(self.d.fd,0o755)
        with self.assertRaisesRegex(Refused,'ownership/mode'):self.d.names()

if __name__=='__main__':unittest.main()
