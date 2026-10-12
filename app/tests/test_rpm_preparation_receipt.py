"""Actual host-side receipt branch, not image admission or hostile-RPM coverage."""
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest


class LearnerReceiptTests(unittest.TestCase):
    def execute_branch(self, root, reviewed):
        source = Path(__file__).parents[1] / 'tools/vm_image/rpm/prepare.py'
        tree = ast.parse(source.read_text())
        branches = [node for node in ast.walk(tree) if isinstance(node, ast.If)
                    and any(isinstance(item, ast.Assign) and any(
                        isinstance(target, ast.Name) and target.id == 'found'
                        for target in item.targets) for item in node.body)
                    and 'Retained learner fixture receipt differs' in ast.unparse(node)]
        self.assertEqual(len(branches), 1)
        payloads = {name: ('synthetic receipt bytes ' + name).encode()
                    for name in ('ll-rpm-data-1.0-1.noarch.rpm',
                                 'll-rpm-data-2.0-1.noarch.rpm',
                                 'll-rpm-report-1.0-1.noarch.rpm')}
        expected = {name: {'sha256': hashlib.sha256(value).hexdigest(), 'bytes': len(value)}
                    for name, value in payloads.items()}
        manifest = json.dumps({'schema_version': 1, 'archives': expected}).encode()
        def require(condition, message):
            if not condition: raise ValueError(message)
        scope = dict(a=SimpleNamespace(kind='learner'), fixture_bytes=payloads,
                     fixture_manifest=manifest, archive_dir=root, found={},
                     reviewed=expected if reviewed is None else reviewed,
                     hashlib=hashlib, require=require)
        # Execute only the exact reviewed trusted-source receipt branch. No
        # argparse, subprocess, VM boot, signature/RPM validation is substituted.
        module = ast.fix_missing_locations(ast.Module(body=[branches[0]], type_ignores=[]))
        exec(compile(module, str(source), 'exec'), scope)
        return scope, expected, manifest

    def test_all_three_admitted_archives_and_exact_manifest_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope, expected, manifest = self.execute_branch(root, None)
            self.assertEqual(scope['found'], expected)
            self.assertEqual((root / 'manifest.json').read_bytes(), manifest)
            self.assertEqual(set(p.name for p in root.iterdir()), set(expected) | {'manifest.json'})
            for name, spec in expected.items():
                data = (root / name).read_bytes()
                self.assertEqual(len(data), spec['bytes'])
                self.assertEqual(hashlib.sha256(data).hexdigest(), spec['sha256'])

    def test_mismatch_fails_without_publication_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, 'receipt differs'):
                self.execute_branch(root, {})
            self.assertFalse((root / 'manifest.json').exists())
            self.assertFalse((root / 'image-result.json').exists())
