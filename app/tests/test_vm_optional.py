"""Prove QEMU capability absence does not prevent the core Qt app from starting."""
import os,subprocess,sys,unittest

class OptionalVmTests(unittest.TestCase):
 def test_core_without_qemu_capabilities_or_subprocess(self):
  script=r'''
import tempfile
from pathlib import Path
from unittest.mock import patch
from learning_lab.__main__ import build_application
with tempfile.TemporaryDirectory() as d:
 p=Path(d)
 with patch('learning_lab.vm_preview.bridge.os.access',return_value=False), patch('subprocess.Popen',side_effect=AssertionError('Core launched a process')):
  app,engine,b,lock=build_application(p/'data',p/'config',p/'vm')
  assert engine.rootObjects()
  assert not b.vm_preview.view['prerequisites']
  assert not (p/'vm').exists()
  b.execute('help');b.flush();assert b.session.attempt['console']
  engine.rootObjects()[0].close();app.processEvents();lock.unlock()
'''
  env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='',QT_QUICK_BACKEND='software')
  result=subprocess.run([sys.executable,'-B','-c',script],env=env,capture_output=True,text=True,timeout=25)
  self.assertEqual(result.returncode,0,result.stderr)
