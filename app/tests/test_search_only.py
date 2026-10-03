"""Content-only search-without-listing scenario; temporary profiles only."""
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios, ProfileLocks
from learning_lab.catalog import CatalogBridge
from learning_lab.domain.validation import ValidationError
from learning_lab.linux_navigation.permissions import guide
from learning_lab.portable import load_portable, PackRepository
from learning_lab import profile_backup as pb

APP = QCoreApplication.instance() or QCoreApplication([])
ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'examples/linux-search-only-directory.lab.json'
DIRECTORY = '/home/learner/Lookup'
NOTE = DIRECTORY + '/message.txt'


class SearchOnlyTests(unittest.TestCase):
    def setUp(self):
        self.lab = load_portable(PACK.read_bytes())

    def session(self, mode='Learn'):
        return self.lab.domain().session(mode=mode)

    def fix(self, s, modifier='u+x'):
        for cmd in ('chmod ' + modifier + ' ' + DIRECTORY, 'cd ' + DIRECTORY, 'cat message.txt'):
            s.execute(cmd)

    def test_contract_identity_and_initial_denials(self):
        template = load_portable((ROOT / 'templates/linux-permissions.lab.json').read_bytes())
        self.assertEqual(self.lab.value()['engine'], template.value()['engine'])
        for p in (ROOT / 'examples').glob('*.lab.json'):
            if p != PACK:
                self.assertNotEqual(load_portable(p.read_bytes()).identity.scenario_id, self.lab.identity.scenario_id)
        s = self.session()
        self.assertEqual(s.attempt['applied']['filesystem'][DIRECTORY]['mode'], '0000')
        self.assertEqual(s.attempt['applied']['filesystem'][NOTE]['mode'], '0600')
        for cmd in ('ls Lookup', 'cd Lookup', 'cat Lookup/message.txt'):
            s.execute(cmd)
            self.assertIn('Permission denied', s.attempt['console'][-1])
            self.assertEqual(s.engine.grade()['score'], 0)
        self.assertEqual(s.attempt['applied']['cwd'], '/home/learner')

    def test_learn_progression_and_optional_denied_listing(self):
        s = self.session()
        for index, cmd in enumerate(('ls -l .', 'chmod u+x Lookup', 'cd Lookup', 'cat message.txt')):
            g = guide(s.pack, s.attempt['applied'])
            self.assertEqual((g['index'], g['command']), (index, cmd))
            if index == 3:
                before = deepcopy(s.attempt['applied'])
                s.execute('ls .')
                self.assertIn('Permission denied (list names)', s.attempt['console'][-1])
                self.assertEqual(s.attempt['applied'], before)
                self.assertEqual(guide(s.pack, s.attempt['applied'])['index'], 3)
            s.execute(cmd)
        s.hint()
        self.assertEqual(s.submit()['score'], 100)
        self.assertTrue(guide(s.pack, s.attempt['applied'])['verified'])

    def test_challenge_equivalent_repairs_paths_and_orders(self):
        for modifier in ('u+x', '100'):
            for read_first in (False, True):
                with self.subTest(modifier=modifier, read_first=read_first):
                    s = self.session('Challenge')
                    self.assertEqual(s.domain.view_state(s, None, 0)['guide'], {})
                    with self.assertRaises(ValidationError): s.hint()
                    s.execute('chmod ' + modifier + ' ./Lookup')
                    cmds = ['cd /home/learner/../learner/Lookup', 'cat ' + DIRECTORY + '/./message.txt']
                    for cmd in reversed(cmds) if read_first else cmds: s.execute(cmd)
                    self.assertEqual(s.submit()['score'], 100)
                    self.assertEqual(s.attempt['applied']['activity']['denied'], [])
                    self.assertEqual(s.attempt['applied']['activity']['listed'], [])
        self.assertNotIn('chmod', json.dumps(self.lab.value()['mission']))

    def test_wrong_modes_and_read_search_distinction(self):
        for modifier, score, lists in [('400', 0, True), ('500', 30, True), ('777', 30, True),
                                      ('u+r', 0, True), ('000', 0, False), ('100', 100, False)]:
            with self.subTest(modifier=modifier):
                s = self.session(); self.fix(s, modifier)
                self.assertEqual(s.submit()['score'], score)
                s.execute('ls ' + DIRECTORY)
                self.assertEqual(s.attempt['console'][-1] == 'message.txt', lists)
                if not lists: self.assertIn('Permission denied (list names)', s.attempt['console'][-1])

    def test_listing_denial_is_behavior_not_a_graded_action(self):
        s = self.session(); self.fix(s)
        grade = s.submit(); before = deepcopy(s.attempt['applied'])
        for cmd in ('ls', 'ls .', 'ls ' + DIRECTORY, 'ls -l .'):
            s.execute(cmd)
            self.assertIn('Permission denied (list names)', s.attempt['console'][-1])
            self.assertEqual(s.attempt['applied'], before)
            self.assertEqual(s.submit(), grade)
        self.assertEqual({o['predicate'] for o in self.lab.value()['objectives']},
                         {'mode_equals', 'traversal_verified', 'read_verified'})

    def test_missing_and_invalidated_evidence(self):
        s = self.session(); s.execute('chmod 100 Lookup')
        self.assertEqual(s.submit()['score'], 70)
        s.execute('cat Lookup/message.txt'); self.assertEqual(s.submit()['score'], 85)
        s.execute('cd Lookup'); self.assertEqual(s.submit()['score'], 100)
        s.execute('chmod 500 ' + DIRECTORY); s.execute('chmod 100 ' + DIRECTORY)
        s.test(); self.assertEqual(s.submit()['score'], 70)
        s.execute('cd .'); self.assertEqual(s.submit()['score'], 85)
        s.execute('cat message.txt'); complete = s.submit()
        s.execute('chmod u+x ' + DIRECTORY); self.assertEqual(s.submit(), complete)

    def test_safety_limits_and_inert_imported_content(self):
        value = self.lab.value(); value['domain']['filesystem'][NOTE]['content'] = '$(false)\n__import__("os").system("false")'
        s = load_portable(json.dumps(value).encode()).domain().session()
        with ExitStack() as stack:
            for api in ('builtins.open', 'builtins.eval', 'builtins.exec', 'io.open', 'os.open',
                        'os.chmod', 'os.system', 'subprocess.Popen', 'socket.socket'):
                stack.enter_context(patch(api, side_effect=AssertionError('host API: ' + api)))
            for cmd in ('chmod 0100 Lookup', 'chmod a+x Lookup', 'chmod -R 100 Lookup',
                        'chmod 100 Lookup; cat Lookup/message.txt', 'ls *', 'cd ../../../../',
                        'chmod 100 /root/../home/learner/Lookup'):
                state, output = s.engine.command(cmd)
                self.assertEqual(state, s.attempt['applied'])
                self.assertTrue(output.startswith('Simulation:'))
            self.fix(s); self.assertEqual(s.submit()['score'], 100)

    def test_invalid_goals_and_conflicting_import(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = PackRepository(Path(temp) / 'packs'); repo.install(PACK.read_bytes())
            before = {p.name: p.read_bytes() for p in repo.root.iterdir()}
            for mutate in (lambda p: p['objectives'][0]['params'].update(mode='0400'),
                           lambda p: p['engine'].update(contract_version=4),
                           lambda p: p['domain'].update(script='execute me'),
                           lambda p: p['metadata'].update(title='Conflicting same version')):
                p = self.lab.value(); mutate(p)
                with self.assertRaises(ValidationError): repo.install(json.dumps(p).encode())
                self.assertEqual({p.name: p.read_bytes() for p in repo.root.iterdir()}, before)

    def test_reset_restart_exports_backup_and_pinned_versions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); catalogs = []; locks = []
            def build(name):
                data = root / name / 'data'; config = root / name / 'config'
                data.mkdir(parents=True, exist_ok=True); config.mkdir(parents=True, exist_ok=True)
                lock = ProfileLocks(data, config); locks.append(lock)
                b = CatalogBridge(load_bundled_scenarios()[0], data, config)
                b.profile_locks = lock; catalogs.append(b)
                return b
            def close(b):
                b.flush()
                for entry in b.labs.values(): entry.timer.stop()
                b.profile_locks.unlock()
            try:
                b = build('source')
                old = ROOT / 'examples/linux-private-note.lab.json'; old_lab = load_portable(old.read_bytes())
                self.assertTrue(b.importPack(str(old))); b.selectLab(old_lab.key, True)
                b.execute('chmod 600 notes.txt'); b.setCommandDraft('cat notes.txt'); b.flush()
                old_attempt = deepcopy(b.session.attempt)
                self.assertTrue(b.importPack(str(PACK))); b.selectLab(self.lab.key, True)
                for _ in range(4): b.execute(b.view['guide']['command'])
                b.submit(); self.assertEqual(b.view['grade']['score'], 100)
                completed = b.session.attempt['id']; b.restart('Challenge')
                self.assertEqual(b.view['historyCount'], 1)
                self.assertEqual(b.session.attempt['applied']['filesystem'][DIRECTORY]['mode'], '0000')
                self.assertEqual(b.session.attempt['applied']['activity'],
                                 {'inspected': [], 'denied': [], 'verified': [], 'traversed': [], 'listed': []})
                b.execute('chmod 100 Lookup'); b.execute('cd Lookup')
                b.setCommandDraft('cat message.txt'); b.flush()
                expected = deepcopy(b.session.attempt); close(b); b = build('source')
                self.assertEqual(b.session.attempt, expected)
                self.assertEqual(b.view['commandDraft'], 'cat message.txt')
                self.assertEqual(b.labs[old_lab.key].session.attempt, old_attempt)
                updated = self.lab.value(); updated['identity']['content_version'] = '1.0.1'
                updated['metadata']['title'] = 'Version fixture'
                update = root / 'update.lab.json'; update.write_text(json.dumps(updated))
                self.assertTrue(b.importPack(str(update))); self.assertTrue(b.importPack(str(PACK)))
                b.selectLab(self.lab.key, True)
                self.assertEqual(b.session.attempt, expected)
                self.assertEqual(b.portables[self.lab.key].pin, self.lab.pin)
                archive = root / 'profile.llbackup'
                self.assertTrue(b.backupProfile(str(archive)), b.transfer_message)
                backup = pb.read_backup(archive); dest = root / 'restored'
                pb.restore(backup, dest, confirmed=True)
                for name, raw in backup.files.items(): self.assertEqual((dest / name).read_bytes(), raw)
                restored = build('restored')
                self.assertEqual(restored.session.attempt, expected)
                self.assertEqual(restored.view['commandDraft'], 'cat message.txt')
                self.assertEqual(restored.portables[self.lab.key].pin, self.lab.pin)
                self.assertEqual(restored.labs[old_lab.key].session.attempt, old_attempt)
                self.assertEqual(restored.view['historyCount'], 1)
                restored.execute('cat message.txt'); restored.submit()
                self.assertEqual(restored.view['grade']['score'], 100)
                export = root / 'export.lab.json'; self.assertTrue(restored.exportScenario(str(export)))
                self.assertEqual(export.read_bytes(), PACK.read_bytes())
                other = build('reimport'); self.assertTrue(other.importPack(str(export)))
                other.selectLab(self.lab.key, True)
                self.assertEqual(other.view['historyCount'], 0)
                self.assertEqual(other.session.engine.grade()['score'], 0)
                for _ in range(4): other.execute(other.view['guide']['command'])
                other.submit(); self.assertEqual(other.view['grade']['score'], 100)
                history = root / 'history.json'; self.assertTrue(b.exportAttempt(str(history), completed))
                with self.assertRaises(ValidationError): load_portable(history.read_bytes())
                restored.restart('Learn')
                self.assertEqual(restored.view['historyCount'], 2)
                self.assertEqual(restored.view['console'], '')
                self.assertEqual(restored.view['commandDraft'], '')
                self.assertEqual(b.session.attempt, expected)  # restore never activates over source
            finally:
                for b in catalogs:
                    for entry in b.labs.values(): entry.timer.stop()
                for lock in locks: lock.unlock()
