"""Current documentation parity and immutable accepted teaching contracts."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

from learning_lab.collections import load_collections
from learning_lab.vm_preview.registry import units, entries

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'cee8d782a1694c5f6a4fa7527a75da90b0d9e945'


class CompletionTests(unittest.TestCase):
    def test_inventory_is_current_and_counts_unique_content(self):
        collections = load_collections()
        self.assertEqual(len(collections), 8)
        self.assertEqual(sum(len(c['entries']) for c in collections), 42)
        self.assertEqual(len({e['scenario'].key for c in collections for e in c['entries']}), 38)
        self.assertEqual((len(units()), len(entries())), (9, 76))
        guide = (ROOT / 'docs/learning-guide.md').read_text()
        self.assertIn('41 distinct simulator activities', guide)
        for c in collections:
            self.assertIn(c['title'].split(' — ')[0], guide)

    def test_objective_rows_and_evidence_match_markdown(self):
        inventory = json.loads((ROOT / 'docs/curriculum-coverage.json').read_text())
        machine = {(r['certification'], r['objective']): r for r in inventory['objectives']}
        self.assertEqual(len(machine), 84)
        self.assertFalse(inventory['full_objective_claims'])
        cert = None
        found = set()
        for line in (ROOT / 'docs/curriculum-coverage.md').read_text().splitlines():
            if line.startswith('## LPIC-1'): cert = 'LPIC-1'
            if line.startswith('## LPIC-2'): cert = 'LPIC-2'
            match = re.fullmatch(r'\| (\d+\.\d+) \| ([^|]+) \| (.*) \|', line)
            if not match: continue
            oid, status, explanation = match.groups()
            key = cert, oid
            self.assertNotIn(key, found)
            found.add(key)
            row = machine[key]
            self.assertEqual(row['status'], status.strip(), key)
            plain = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', explanation).removeprefix('—. ')
            self.assertEqual(row['implemented_and_missing'], plain, key)
            self.assertEqual(row['evidence'], re.findall(r'\]\(([^)]+)\)', explanation), key)
            for link in row['evidence']:
                self.assertTrue((ROOT / 'docs' / link).is_file(), (key, link))
        self.assertEqual(found, set(machine))
        for oid in ('205.3', '207.1', '207.2', '208.1', '208.2', '208.4'):
            self.assertEqual(machine['LPIC-2', oid]['status'], 'Reinforcement only')
            self.assertIn('offline-evidence', machine['LPIC-2', oid]['units'])
        for oid in ('200.1', '200.2'):
            self.assertIn('resource-simulator', machine['LPIC-2', oid]['units'])

    def test_current_user_documents_have_resolvable_local_links(self):
        for name in ('README.md', 'docs/learning-guide.md', 'docs/completion-checklist.md',
                     'docs/user-installation.md', 'docs/curriculum-coverage.md'):
            path = ROOT / name
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' in link or link.startswith(('/', '#')): continue
                self.assertTrue((path.parent / link.split('#')[0]).exists(), (name, link))

    def test_accepted_resources_engines_and_controller_remain_identical(self):
        # Developer-only Git reads. Learner commands are never forwarded here.
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE,
                                         'app/learning_lab'], cwd=ROOT.parent, text=True).splitlines()
        count = 0
        for path in paths:
            if path == 'app/learning_lab/qml/Main.qml':
                from presentation_revision import MAIN_SHA256
                self.assertEqual(hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest(), MAIN_SHA256)
                continue
            before = subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT.parent)
            self.assertEqual(hashlib.sha256(before).digest(),
                             hashlib.sha256((ROOT.parent / path).read_bytes()).digest(), path)
            count += 1
        self.assertGreater(count, 200)

    def test_help_and_scoring_language_matches_supported_boundaries(self):
        guide = (ROOT / 'docs/learning-guide.md').read_text()
        qml = (ROOT / 'learning_lab/qml/Main.qml').read_text()
        self.assertIn('different content under the same identity/version', guide)
        self.assertIn('Networking labs use tasks', guide)
        for message in ('diagnostic reasoning, forecasts', 'nine units / 76 lessons',
                        'VM disks and sessions are excluded', 'not restore RAM or shell jobs'):
            self.assertIn(message, qml)
        self.assertNotIn('Optional · Manage a background job', qml)


if __name__ == '__main__':
    unittest.main()
