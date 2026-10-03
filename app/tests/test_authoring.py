"""Authoring changes only explicitly selected files or explicitly imported packs."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.authoring import resource
from learning_lab.portable import LIMIT, load_portable

APP = QCoreApplication.instance() or QCoreApplication([])


class AuthoringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='lab-authoring-')
        self.root = Path(self.temp.name)
        self.data = self.root/'data'; self.config = self.root/'config'
        self.config.mkdir()
        self.b = CatalogBridge(load_bundled_scenarios()[0], self.data, self.config)
        self.a = self.b.authoring
        self.source = self.root/'my-notes.lab.json'

    def tearDown(self):
        for lab in self.b.labs.values(): lab.timer.stop()
        self.temp.cleanup()

    def profile(self):
        return {str(p.relative_to(self.root)):p.read_bytes() for folder in (self.data,self.config)
                for p in folder.rglob('*') if p.is_file()}

    def starter(self):
        self.assertTrue(self.a.prepareStarter(str(self.source)),self.a.message)
        self.assertTrue(self.a.confirmStarter(True),self.a.message)
        return load_portable(self.source.read_bytes())

    def test_resources_and_starter_unique_identity_without_profile_writes(self):
        before = self.profile(); first = self.starter()
        self.assertEqual(self.profile(),before)
        example = load_portable(resource('permissions.lab.json').encode())
        self.assertNotEqual(first.identity.scenario_id,example.identity.scenario_id)
        self.assertIn('complete',resource('guide.txt'))
        self.assertIn('learning-lab.scenario',self.a.view['prompt'])
        self.assertTrue(self.a.prepareStarter(str(self.source)))
        self.assertTrue(self.a.view['replacing']); self.assertTrue(self.a.confirmStarter(True))
        second = load_portable(self.source.read_bytes())
        self.assertNotEqual(first.identity.scenario_id,second.identity.scenario_id)
        self.assertEqual(self.profile(),before)

    def test_cancellation_explicit_confirmation_and_existing_file(self):
        self.assertFalse(self.a.confirmStarter(True))
        self.assertTrue(self.a.prepareStarter(str(self.source)))
        self.assertFalse(self.source.exists());self.assertFalse(self.a.confirmStarter(False))
        self.assertFalse(self.source.exists())
        self.source.write_bytes(b'original owner-selected file')
        self.assertTrue(self.a.prepareStarter(str(self.source)))
        self.assertEqual(self.source.read_bytes(),b'original owner-selected file')
        self.assertFalse(self.a.confirmStarter(False))
        self.assertEqual(self.source.read_bytes(),b'original owner-selected file')

    def test_save_races_symlinks_and_profile_paths_fail_safely(self):
        self.assertTrue(self.a.prepareStarter(str(self.source)))
        self.source.write_bytes(b'appeared after preview')
        self.assertFalse(self.a.confirmStarter(True));self.assertEqual(self.source.read_bytes(),b'appeared after preview')
        self.assertTrue(self.a.prepareStarter(str(self.source)));self.source.write_bytes(b'changed')
        self.assertFalse(self.a.confirmStarter(True));self.assertEqual(self.source.read_bytes(),b'changed')
        link=self.root/'link.lab.json';link.symlink_to(self.source)
        self.assertFalse(self.a.prepareStarter(str(link)));self.assertFalse(self.a.validateLab(str(link)))
        before=self.profile()
        for path in (self.data/'bad.lab.json', self.config/'bad.lab.json',self.root/'bad.txt'):
            self.assertFalse(self.a.prepareStarter(str(path)))
        self.assertEqual(self.profile(),before);self.assertFalse(list(self.root.glob('.lab-starter-*')))

    def test_validate_summary_is_readonly_and_import_is_explicit(self):
        pack=self.starter();before=self.profile();lab_key=self.b.view['labKey']
        self.assertTrue(self.a.validateLab(str(self.source)),self.a.message)
        self.assertEqual(self.profile(),before);self.assertNotIn(pack.key,self.b.portables)
        for text in (pack.identity.scenario_id,'linux-navigation','1.0.0','Final state','not a gameplay test'):
            self.assertIn(text,self.a.summary)
        self.assertTrue(self.a.importValidated(),self.a.message)
        self.assertIn(pack.key,self.b.portables);self.assertEqual(self.b.view['labKey'],lab_key)
        self.assertFalse(self.a.importValidated())
        self.b.setLibraryState(pack.key,'removed',True)
        before=self.profile();self.assertTrue(self.a.validateLab(str(self.source)))
        self.assertEqual(self.profile(),before);self.assertTrue(self.a.importValidated())
        self.assertEqual(self.b.visibility.state(pack.key),'removed');self.assertEqual(len(self.b.portables),1)

    def test_identity_conflict_and_changed_source_require_revalidation(self):
        pack=self.starter();self.assertTrue(self.a.validateLab(str(self.source)))
        value=pack.value();value['metadata']['title']='Edited title';self.source.write_text(json.dumps(value))
        self.assertFalse(self.a.importValidated());self.assertFalse(self.b.portables)
        self.assertTrue(self.a.validateLab(str(self.source)));self.assertTrue(self.a.importValidated())
        value['metadata']['title']='Conflicting title';self.source.write_text(json.dumps(value));before=self.profile()
        self.assertFalse(self.a.validateLab(str(self.source)));self.assertIn('Same ID/version',self.a.message)
        self.assertEqual(self.profile(),before)
        value['identity']['content_version']='1.0.1';self.source.write_text(json.dumps(value))
        self.assertTrue(self.a.validateLab(str(self.source)));self.assertEqual(self.profile(),before)

    def test_invalid_files_unsupported_contracts_and_infeasible_goals(self):
        base=self.starter().value();before=self.profile()
        bad=[b'{\n "format": }',b' '* (LIMIT+1),b'PKarchive',b'{"x":1,"x":2}']
        for change in (
            lambda p:p['engine'].update(contract_version=999),
            lambda p:p['engine']['required_capabilities'].append('host-shell'),
            lambda p:p['identity'].update(id='Bad ID'),
            lambda p:p['objectives'][0]['params'].update(mode='0200'),
            lambda p:p['domain']['lesson']['steps'][0].update(action='execute'),
            lambda p:p.update(assets=['file:///etc/passwd']),
        ):
            value=deepcopy(base);change(value);bad.append(json.dumps(value).encode())
        for raw in bad:
            self.source.write_bytes(raw);self.assertFalse(self.a.validateLab(str(self.source)),raw[:30])
            self.assertFalse(self.a.view['canImport']);self.assertFalse(self.a.importValidated())
            self.assertEqual(self.profile(),before)
        self.source.write_bytes(b'{\n "format": }');self.a.validateLab(str(self.source))
        self.assertIn('line 2 column',self.a.message)

    def test_derived_scenario_learn_challenge_and_export(self):
        value=self.starter().value()
        # Meaningful user edits: renamed target, new learning content and title.
        old='/home/learner/notes.txt';new='/home/learner/project.txt'
        value=json.loads(json.dumps(value).replace(old,new).replace('notes.txt','project.txt'))
        value['metadata']['title']='Read my project plan'
        value['domain']['filesystem'][new]['content']='Project plan: rehearse the demo.\n'
        value['domain']['lesson']['steps'][-1]['expected']='The project plan says to rehearse the demo. Submit when ready.'
        self.source.write_text(json.dumps(value));self.assertTrue(self.a.validateLab(str(self.source)))
        self.assertTrue(self.a.importValidated());pack=load_portable(self.source.read_bytes())
        self.assertTrue(self.b.selectLab(pack.key))
        for _ in range(4):self.b.execute(self.b.view['guide']['command'])
        self.b.submit();self.assertEqual(self.b.view['grade']['score'],100)
        learned=self.b.session.attempt['id'];self.b.restart('Challenge');self.assertEqual(self.b.view['guide'],{})
        self.b.execute('chmod 600 ./project.txt');self.b.execute('cat '+new);self.b.submit()
        self.assertEqual(self.b.view['grade']['score'],100)
        self.assertTrue(any(row['id']==learned for row in self.b.view['history']))
        export=self.root/'export.lab.json';self.assertTrue(self.b.exportScenario(str(export)))
        self.assertEqual(load_portable(export.read_bytes()).key,pack.key)
        self.b.restart('Learn');self.assertEqual(self.b.session.engine.grade()['score'],0)

    def test_import_rechecks_repository_conflicts_after_preview(self):
        value=self.starter().value();self.assertTrue(self.a.validateLab(str(self.source)))
        value['metadata']['title']='Another source imported meanwhile'
        other=self.root/'other.lab.json';other.write_text(json.dumps(value));self.assertTrue(self.b.importPack(str(other)))
        before=self.profile();self.assertFalse(self.a.importValidated());self.assertEqual(self.profile(),before)

    def test_authored_attempt_reopens_with_same_pin_mode_draft_and_history(self):
        scenario=self.starter();self.a.validateLab(str(self.source));self.a.importValidated()
        self.b.selectLab(scenario.key)
        self.b.execute('chmod u+r notes.txt');self.b.execute('cat notes.txt');self.b.submit()
        self.b.restart('Challenge');self.b.execute('pwd');self.b.setCommandDraft('cat notes.txt');self.b.flush()
        expected=deepcopy(self.b.session.attempt)
        for lab in self.b.labs.values():lab.timer.stop()
        fresh=CatalogBridge(load_bundled_scenarios()[0],self.data,self.config)
        try:
            self.assertEqual(fresh.session.attempt,expected)
            self.assertEqual(fresh.view['commandDraft'],'cat notes.txt')
            self.assertEqual(fresh.portables[scenario.key].pin,scenario.pin)
            self.assertEqual(fresh.view['historyCount'],1)
        finally:
            for lab in fresh.labs.values():lab.timer.stop()

    def test_imported_file_content_is_data_not_executable(self):
        from unittest.mock import patch
        value=self.starter().value();marker=self.root/'never-created'
        content='__import__("pathlib").Path('+repr(str(marker))+').touch()\n$(touch '+str(marker)+')'
        value['domain']['filesystem']['/home/learner/notes.txt']['content']=content
        self.source.write_text(json.dumps(value))
        with patch('os.system',side_effect=AssertionError('host execution')), patch('subprocess.Popen',side_effect=AssertionError('subprocess')), patch('socket.socket',side_effect=AssertionError('network')):
            self.assertTrue(self.a.validateLab(str(self.source)));self.assertTrue(self.a.importValidated())
            key=load_portable(self.source.read_bytes()).key;self.b.selectLab(key)
            self.b.execute('chmod 600 notes.txt');self.b.execute('cat notes.txt')
        self.assertFalse(marker.exists())

    def test_new_starter_discards_old_validation_preview_only(self):
        self.starter();self.assertTrue(self.a.validateLab(str(self.source)));before=self.profile()
        self.assertTrue(self.a.prepareStarter(str(self.root/'second.lab.json')))
        self.assertFalse(self.a.view['canImport']);self.assertEqual(self.a.summary,'')
        self.assertFalse(self.a.confirmStarter(False));self.assertEqual(self.profile(),before)
