"""Content-only private-note lesson and isolated catalog lifecycle."""
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.domain.validation import ValidationError
from learning_lab.linux_navigation.permissions import guide
from learning_lab.portable import load_portable, PackRepository

APP = QCoreApplication.instance() or QCoreApplication([])
ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'examples/linux-private-note.lab.json'
TARGET = '/home/learner/notes.txt'


class PrivateNoteTests(unittest.TestCase):
    def setUp(self):
        self.lab = load_portable(PACK.read_bytes())

    def session(self, mode='Learn'):
        return self.lab.domain().session(mode=mode)

    def test_identity_contract_and_initial_read_does_not_prove_privacy(self):
        template = load_portable((ROOT / 'templates/linux-permissions.lab.json').read_bytes())
        self.assertEqual(self.lab.value()['engine'], template.value()['engine'])
        self.assertNotEqual(self.lab.value()['identity']['id'], template.value()['identity']['id'])
        for p in (ROOT / 'learning_lab/collections/packs').glob('*.json'):
            self.assertNotEqual(self.lab.value()['identity']['id'], load_portable(p.read_bytes()).value()['identity']['id'])
        s = self.session()
        self.assertEqual(s.attempt['applied']['filesystem'][TARGET]['mode'], '0777')
        s.execute('cat notes.txt')
        self.assertIn('Personal learning notes', '\n'.join(s.attempt['console']))
        self.assertEqual(s.submit()['score'], 30)
        self.assertFalse(s.engine.grade()['complete'])

    def test_learn_guidance_and_hints(self):
        s = self.session()
        for index, command in enumerate(('ls -l .', 'chmod 600 notes.txt', 'cat notes.txt')):
            g = guide(s.pack, s.attempt['applied'])
            self.assertEqual((g['index'], g['command']), (index, command))
            self.assertTrue(g['explanation'] and g['expected'])
            s.execute(command)
        s.hint()
        self.assertTrue(guide(s.pack, s.attempt['applied'])['verified'])
        self.assertEqual(s.submit()['score'], 100)  # no hidden hint penalty

    def test_challenge_equivalent_paths_and_no_required_inspection(self):
        for target in ('notes.txt', './notes.txt', TARGET, '../learner/./notes.txt'):
            with self.subTest(target=target):
                s = self.session('Challenge')
                self.assertEqual(s.domain.view_state(s, None, 0)['guide'], {})
                with self.assertRaises(ValidationError):
                    s.hint()
                s.execute('chmod 600 ' + target)
                s.execute('cat ' + target)
                self.assertEqual(s.submit()['score'], 100)
                self.assertEqual(s.attempt['applied']['activity']['inspected'], [])
        self.assertNotIn('chmod', json.dumps(self.lab.value()['mission']))

    def test_incorrect_modes_and_insufficient_symbolic_repairs(self):
        for modifier in ('777', '644', '700', '400', 'u+r', 'u+x'):
            with self.subTest(modifier=modifier):
                s = self.session('Challenge')
                s.execute('chmod ' + modifier + ' notes.txt')
                s.execute('cat notes.txt')
                self.assertEqual(s.submit()['score'], 30)
                self.assertFalse(s.engine.grade()['complete'])
        s = self.session()
        s.execute('chmod 000 notes.txt'); s.execute('cat notes.txt')
        self.assertEqual(s.submit()['score'], 0)

    def test_missing_verification_wrong_file_and_later_change(self):
        s = self.session()
        s.execute('cat notes.txt')  # successful early reading cannot verify repair
        s.execute('chmod 600 notes.txt')
        self.assertEqual(s.submit()['score'], 70)
        s.execute('cat /etc/motd'); s.test()
        self.assertEqual(s.submit()['score'], 70)
        s.execute('cat notes.txt'); self.assertEqual(s.submit()['score'], 100)
        s.execute('chmod 644 notes.txt'); s.execute('chmod 600 notes.txt')
        self.assertEqual(s.submit()['score'], 70)
        s.execute('cat notes.txt'); first = s.submit()
        s.execute('chmod 600 notes.txt')  # no actual change: preserve evidence
        self.assertEqual(s.submit(), first)

    def test_unsupported_commands_and_inert_imported_text(self):
        p = self.lab.value()
        p['domain']['filesystem'][TARGET]['content'] = '__import__("os").system("false")\n$(false)'
        s = load_portable(json.dumps(p).encode()).domain().session()
        with ExitStack() as stack:
            for api in ('builtins.open', 'builtins.eval', 'builtins.exec', 'io.open', 'os.open',
                        'os.chmod', 'os.system', 'subprocess.Popen', 'socket.socket'):
                stack.enter_context(patch(api, side_effect=AssertionError('host access: ' + api)))
            for cmd in ('chmod 0600 notes.txt', 'chmod go-rwx notes.txt', 'chmod 600 *',
                        'chmod 600 notes.txt; cat notes.txt', 'cat /etc/passwd', 'sh'):
                before = deepcopy(s.attempt['applied'])
                state, output = s.engine.command(cmd)
                self.assertEqual(state, before)
                self.assertTrue(output.startswith('Simulation:'))
            s.execute('chmod 600 notes.txt'); s.execute('cat notes.txt')
            self.assertEqual(s.submit()['score'], 100)

    def test_reset_reopen_exports_and_pinned_versions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); catalogs = []
            def build(name):
                config = root / name / 'config'; config.mkdir(parents=True, exist_ok=True)
                b = CatalogBridge(load_bundled_scenarios()[0], root / name / 'data', config)
                catalogs.append(b)
                return b
            try:
                b = build('first')
                old = ROOT / 'examples/linux-file-permissions.lab.json'
                self.assertTrue(b.importPack(str(old)))
                old_key = load_portable(old.read_bytes()).key
                b.selectLab(old_key, True); b.execute('chmod u+r notes.txt')
                b.setCommandDraft('cat notes.txt'); b.flush()
                old_attempt = deepcopy(b.session.attempt)
                self.assertTrue(b.importPack(str(PACK)))
                b.selectLab(self.lab.key, True)
                for cmd in ('chmod 600 notes.txt', 'cat notes.txt'): b.execute(cmd)
                b.submit(); completed = b.session.attempt['id']
                b.restart('Challenge')
                self.assertEqual(b.session.attempt['applied']['filesystem'][TARGET]['mode'], '0777')
                self.assertEqual(b.session.engine.grade()['score'], 0)
                self.assertEqual(b.view['guide'], {})
                b.execute('chmod 600 notes.txt'); b.setCommandDraft('cat notes.txt'); b.flush()
                expected = deepcopy(b.session.attempt)
                for entry in b.labs.values(): entry.timer.stop()
                b = build('first')
                self.assertEqual(b.session.attempt, expected)
                self.assertEqual(b.portables[self.lab.key].pin, self.lab.pin)
                self.assertEqual(b.labs[old_key].session.attempt, old_attempt)
                self.assertEqual(b.view['historyCount'], 1)
                b.execute('cat notes.txt'); b.submit()
                self.assertEqual(b.view['grade']['score'], 100)
                b.flush(); pinned = deepcopy(b.session.attempt)
                updated = self.lab.value()
                updated['identity']['content_version'] = '1.0.1'
                updated['metadata']['title'] = 'Private note revision fixture'
                update = root / 'update.lab.json'; update.write_text(json.dumps(updated))
                self.assertTrue(b.importPack(str(update)))
                self.assertTrue(b.importPack(str(PACK)))
                b.selectLab(self.lab.key, True)
                self.assertEqual(b.session.attempt, pinned)
                self.assertEqual(b.portables[self.lab.key].pin, self.lab.pin)
                export = root / 'export.lab.json'; self.assertTrue(b.exportScenario(str(export)))
                self.assertEqual(export.read_bytes(), PACK.read_bytes())
                other = build('second'); self.assertTrue(other.importPack(str(export)))
                other.selectLab(self.lab.key, True)
                self.assertEqual(other.view['historyCount'], 0)
                self.assertEqual(other.session.engine.grade()['score'], 0)
                for _ in range(3): other.execute(other.view['guide']['command'])
                other.submit(); self.assertEqual(other.view['grade']['score'], 100)
                history = root / 'personal.attempt.json'
                self.assertTrue(b.exportAttempt(str(history), completed))
                with self.assertRaises(ValidationError): load_portable(history.read_bytes())
                b.restart('Learn')
                self.assertEqual(b.view['historyCount'], 2)
                self.assertEqual(b.view['commandDraft'], '')
                self.assertEqual(b.view['console'], '')
            finally:
                for b in catalogs:
                    for entry in b.labs.values(): entry.timer.stop()

    def test_conflicting_import_preserves_repository_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = PackRepository(Path(temp) / 'packs'); repo.install(PACK.read_bytes())
            before = {p.name: p.read_bytes() for p in repo.root.iterdir()}
            conflict = self.lab.value(); conflict['metadata']['title'] = 'Conflicting content'
            with self.assertRaises(ValidationError): repo.install(json.dumps(conflict).encode())
            self.assertEqual({p.name: p.read_bytes() for p in repo.root.iterdir()}, before)
