"""Bounded static developer Bash/GNU reference fixtures, not learner execution."""
import os,subprocess,tempfile,unittest
from pathlib import Path
from bash_guest_fixtures import SCRIPT_ROWS
class BashReferenceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  for name,rows in SCRIPT_ROWS.items():
   p=self.root/(name+'.sh');p.write_text('\n'.join(rows)+'\n');p.chmod(0o700)
 def run_script(self,name,*args):
  return subprocess.run(['/usr/bin/timeout','-k','2s','5s','/bin/bash',str(self.root/(name+'.sh')),*args],cwd=self.root,capture_output=True,timeout=8)
 def put(self,name,data):
  p=self.root/name;p.write_bytes(data);return str(p)
 def test_all_syntax_valid_does_not_mean_correct_behavior(self):
  for name in SCRIPT_ROWS:self.assertEqual(subprocess.run(['/bin/bash','-n',str(self.root/(name+'.sh'))],capture_output=True,timeout=5).returncode,0)
  r=self.run_script('script','two words');self.assertEqual((r.returncode,r.stdout,r.stderr),(0,b'target=<two words>\n',b''))
  r=self.run_script('script');self.assertEqual(r.returncode,2);self.assertIn(b'usage:',r.stderr);self.assertEqual(r.stdout,b'')
  wrong=self.root/'wrong.sh';wrong.write_text('printf wrong\n');self.assertEqual(subprocess.run(['/bin/bash','-n',str(wrong)],timeout=5).returncode,0)
  self.assertNotEqual(subprocess.run(['/bin/bash',str(wrong)],capture_output=True,timeout=5).stdout,b'target=<two words>\n')
 def test_guards_success_and_distinct_errors(self):
  p=self.put('ready note.txt',b'READY\n');r=self.run_script('guards',p);self.assertEqual((r.returncode,r.stdout),(0,('ready: '+p+'\n').encode()))
  for args,status in [((),2),(('missing',),3),((str(self.root),),3),((self.put('empty',b''),),4),((self.put('wrong',b'WAIT\n'),),5)]:
   r=self.run_script('guards',*args);self.assertEqual(r.returncode,status);self.assertTrue(r.stderr);self.assertEqual(r.stdout,b'')
 def test_guard_option_like_and_dash_filenames_are_data(self):
  for name in ('--help','-q','-'):
   self.put(name,b'READY\n');r=self.run_script('guards',name);self.assertEqual(r.returncode,0);self.assertEqual(r.stdout,('ready: '+name+'\n').encode())
  self.put('-q',b'WAIT\n');self.assertEqual(self.run_script('guards','-q').returncode,5)
 def test_records_bytes_empty_and_unterminated_line(self):
  p=self.put('records',b' two words \nback\\slash\n\ntail');r=self.run_script('records',p)
  self.assertEqual((r.returncode,r.stdout),(0,b'< two words >\n<back\\slash>\n<>\n<tail>\nrecords=4\n'))
  r=self.run_script('records',self.put('empty',b''));self.assertEqual(r.stdout,b'records=0\n')
 def test_record_and_byte_limits_partial_output(self):
  for n in (20,21):
   r=self.run_script('records',self.put('many',b'x\n'*n));self.assertEqual(r.returncode,0 if n==20 else 4)
   if n==21:self.assertEqual(r.stdout,b'<x>\n'*20);self.assertIn(b'too many',r.stderr)
  self.assertEqual(self.run_script('records',self.put('large',b'x'*2049)).returncode,3)
 def test_handover_exact_output_empty_and_malformed(self):
  r=self.run_script('handover',self.put('rows',b'app one|ok\nstore\\east|fail\ncache|fail\n'))
  self.assertEqual((r.returncode,r.stdout),(0,b'FAIL store\\east\nFAIL cache\nok=1 fail=2\n'))
  self.assertEqual(self.run_script('handover',self.put('empty',b'')).stdout,b'ok=0 fail=0\n')
  for b in (b'ok\n',b'stray\n',b'|ok\n',b'a|b|ok\n',b'x|unknown\n'):
   r=self.run_script('handover',self.put('bad',b));self.assertEqual(r.returncode,3);self.assertTrue(r.stderr)
 def test_handover_bounds_and_partial_error(self):
  r=self.run_script('handover',self.put('partial',b'x|fail\nbad\n'));self.assertEqual((r.returncode,r.stdout),(3,b'FAIL x\n'))
  self.assertEqual(self.run_script('handover',self.put('many',b'x|ok\n'*21)).returncode,4)
  self.assertEqual(self.run_script('handover',self.put('large',b'x'*2049)).returncode,2)
 def test_redirection_pipeline_status_and_publication(self):
  # Static developer syntax in a temporary directory, never learner supplied.
  script="printf retained > report; cat missing > candidate 2> errors; rc=$?; if [ \"$rc\" -eq 0 ]; then cp candidate report; fi; cat missing 2> pipe-errors | wc -l > count; printf '%s\\n' \"$?\" > default; set -o pipefail; cat missing 2>> pipe-errors | wc -l > count; printf '%s\\n' \"$?\" > pipefail"
  r=subprocess.run(['/bin/bash','-c',script],cwd=self.root,capture_output=True,timeout=5);self.assertEqual(r.returncode,0)
  self.assertEqual((self.root/'report').read_bytes(),b'retained');self.assertEqual((self.root/'candidate').read_bytes(),b'');self.assertTrue((self.root/'errors').read_bytes())
  self.assertEqual((self.root/'default').read_bytes(),b'0\n');self.assertEqual((self.root/'pipefail').read_bytes(),b'1\n')
 def test_static_timeout_guards_runaway_test_script(self):
  p=self.root/'loop.sh';p.write_text('while :; do :; done\n')
  r=subprocess.run(['/usr/bin/timeout','-k','1s','0.2s','/bin/bash',str(p)],capture_output=True,timeout=3);self.assertEqual(r.returncode,124)
