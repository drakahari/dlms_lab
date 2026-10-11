"""Exercise real controls and asynchronous polling, never guest processes."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import unittest


class VmNavigationTests(unittest.TestCase):
    def test_bridge_adds_only_read_only_refresh_status(self):
        from learning_lab.vm_preview import bridge
        data=Path(bridge.__file__).read_bytes()
        new=b"'busy':self._busy,'refreshing':self._refreshing"
        self.assertEqual(data.count(new),1)
        self.assertEqual(hashlib.sha256(data.replace(new,b"'busy':self._busy")).hexdigest(),
                         '9a92918586de3d06a7a938ffe6c768579d8f0d33471f585520deee2cff5ee80d')

    def test_navigation_survives_refresh_and_keeps_readable_exact_selection(self):
        result = subprocess.run(
            [sys.executable, '-B', str(Path(__file__).with_name('vm_navigation_acceptance.py')), '--quick'],
            env={**os.environ, 'QT_QPA_PLATFORM':'offscreen', 'QT_QPA_PLATFORMTHEME':'',
                 'QT_QUICK_BACKEND':'software', 'QT_SCALE_FACTOR':'1'},
            capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
