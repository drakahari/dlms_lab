"""Prevent legal-file drift or omission in the isolated installer build source."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import user_install

APP=Path(__file__).resolve().parents[1]

class LicensingTests(unittest.TestCase):
    def test_canonical_license_and_standalone_project_copy_match(self):
        raw=(APP.parent/'LICENSE').read_bytes()
        self.assertEqual(raw,(APP/'LICENSE').read_bytes())
        self.assertIn(b'Copyright (c) 2026 Mike Buchanan',raw)
        # Reviewed standard MIT text; changing clauses needs explicit review.
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'c9edc682b985b87e20a83ade37677f0cb86acaf0cf8e40fa1779662678aa5cb2')
    def test_isolated_builder_carries_legal_inputs(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);workspace=root/'work';workspace.mkdir();output=root/'wheels'
            def run(command,cwd,log):
                copied=workspace/'source'
                for name in ('LICENSE','THIRD_PARTY_NOTICES.md','MANIFEST.in','docs/distribution-licensing.md'):
                    self.assertEqual((copied/name).read_bytes(),(APP/name).read_bytes())
                if 'wheel' in command:(output/'omarchy_learning_lab-test.whl').write_bytes(b'fixture only')
            with patch.object(user_install,'run',side_effect=run):
                self.assertTrue(user_install.build_wheel(APP,output,workspace,root/'log').is_file())
    def test_missing_legal_file_refuses_build_before_dependency_or_install_actions(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source=root/'source';source.mkdir();work=root/'work';work.mkdir()
            for name in ('pyproject.toml','README.md'):(source/name).write_bytes((APP/name).read_bytes())
            with patch.object(user_install,'run') as run:
                with self.assertRaises(FileNotFoundError):user_install.build_wheel(source,root/'dist',work,root/'log')
                run.assert_not_called()
