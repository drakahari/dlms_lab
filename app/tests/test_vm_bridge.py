"""Regression for a confirmed action racing the periodic Qt status refresh."""
import os,subprocess,sys,unittest

class BridgeRefreshTests(unittest.TestCase):
 def run_fixture(self,refresh):
  script=r'''
import tempfile,threading,time
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication
from learning_lab.vm_preview.bridge import VmBridge
from learning_lab.vm_preview.registry import LEGACY_ID
app=QCoreApplication([])
with tempfile.TemporaryDirectory() as d:
 root=Path(d);vm=VmBridge(root/'data',root/'config',root/'vm',gate_root=root/'gate')
 entered=threading.Event();release=threading.Event();calls=[]
 def view(id):
  calls.append(id)
  if len(calls)==1:entered.set();assert release.wait(4)
  return {'state':'not-started','session':None,'message':'','other_profile_running':False,'running_lesson_id':''}
 with patch.object(vm.sessions,'view',side_effect=view),patch.object(vm.manager,'reset',return_value=None) as reset:
  if REFRESH:vm.refresh()
  else:vm._work(lambda manager:None)
  assert entered.wait(2);assert vm.view['busy']
  vm.reset('Challenge',True)
  # Queue is bounded: a second confirmation cannot create a second reset.
  vm.reset('Learn',True);release.set()
  deadline=time.monotonic()+5
  while (vm.view['busy'] or vm._pending) and time.monotonic()<deadline:app.processEvents();time.sleep(.005)
  assert not vm.view['busy'];assert vm._pending is None
  if REFRESH:reset.assert_called_once_with('Challenge',True);assert calls==[LEGACY_ID,LEGACY_ID]
  else:reset.assert_not_called();assert calls==[LEGACY_ID]
 assert not (root/'vm').exists()
'''.replace('REFRESH','True' if refresh else 'False')
  result=subprocess.run([sys.executable,'-B','-c',script],capture_output=True,text=True,timeout=12,env={**os.environ,'QT_QPA_PLATFORM':'offscreen'})
  self.assertEqual(result.returncode,0,result.stdout+result.stderr)
 def test_confirmed_reset_waits_for_refresh_once(self):self.run_fixture(True)
 def test_mutation_busy_does_not_queue_duplicate_work(self):self.run_fixture(False)
