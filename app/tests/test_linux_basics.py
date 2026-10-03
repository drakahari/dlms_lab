"""Beginner service and UI preference regressions; fixture writes only."""
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
from learning_lab.portable import load_portable, PackRepository
from learning_lab.pinned_storage import PinnedStore

APP=QCoreApplication.instance() or QCoreApplication([])
ROOT=Path(__file__).resolve().parents[1]
INTRO_FILE=ROOT/'examples/linux-service-basics.lab.json'
FAULT_FILE=ROOT/'examples/linux-web-document-root.lab.json'
INTRO=load_portable(INTRO_FILE.read_bytes())
FAULT=load_portable(FAULT_FILE.read_bytes())


class BeginnerServiceTests(unittest.TestCase):
    def test_stopped_service_has_no_configuration_fault(self):
        s=INTRO.domain().session();state=deepcopy(s.attempt['applied'])
        self.assertEqual(state['service']['status'],'inactive')
        self.assertIsNone(state['service']['loaded']);self.assertEqual(state['service']['error'],'')
        checks=s.engine.checks();self.assertTrue(checks['configuration_valid'][0]);self.assertTrue(checks['document_root_accessible'][0])
        self.assertEqual(s.submit()['score'],0)
        s.execute('systemctl status lab-web');self.assertEqual(s.attempt['applied'],state)
        self.assertIn('healthy configuration','\n'.join(s.attempt['console']))
        with self.assertRaises(ValidationError):s.edit('/etc/lab-web.conf','bad')

    def test_guidance_advances_one_command_at_a_time(self):
        domain=INTRO.domain();s=domain.session()
        def guide():return domain.view_state(s,'',0)['guide']
        self.assertEqual(guide()['index'],0);self.assertIn('changes nothing',guide()['explanation'])
        s.execute('systemctl status unknown');self.assertEqual(guide()['index'],0)
        s.execute('systemctl\nstatus lab-web');self.assertEqual(guide()['index'],0)
        s.execute('systemctl status lab-web.service');self.assertEqual(guide()['index'],1)
        s.execute('systemctl start lab-web');self.assertEqual(guide()['index'],2);self.assertFalse(guide()['verified'])
        s.execute('systemctl\nstatus lab-web');self.assertFalse(guide()['verified'])
        s.execute('systemctl status lab-web');self.assertTrue(guide()['verified'])
        self.assertEqual(s.submit()['score'],100)
        challenge=domain.session(mode='Challenge');self.assertEqual(domain.view_state(challenge,'',0)['guide'],{})
        with self.assertRaises(ValidationError):challenge.hint()

    def test_grading_is_state_based_and_unsupported_commands_are_safe(self):
        for mode in ('Learn','Challenge'):
            for action in ('start','restart'):
                s=INTRO.domain().session(mode=mode)
                with patch('builtins.open',side_effect=AssertionError('host file')),patch('subprocess.Popen',side_effect=AssertionError('host process')),patch('socket.socket',side_effect=AssertionError('network')):
                    for command in ('systemctl start lab-web; id','cat /../../etc/passwd','sudo systemctl start lab-web'):
                        state,out=s.engine.command(command);self.assertEqual(state,s.attempt['applied']);self.assertTrue(out.startswith('Simulation:'))
                    s.execute('systemctl '+action+' lab-web');self.assertEqual(s.submit()['score'],100)
                before=deepcopy(s.attempt['assessments']);s.submit();self.assertEqual(s.attempt['assessments'],before)

    def test_original_content_pin_and_behavior_preserved(self):
        self.assertEqual(FAULT.identity.content_digest,'sha256:d918833e91e24908262751a8d3501b057e3ba319d637e99e68cfda8e82b79edd')
        self.assertEqual(FAULT.pin['engine'],{'engine_id':'linux-service','contract_version':1,'behavior_version':'linux-service-1'})
        self.assertEqual(FAULT.domain().session().attempt['applied']['service']['status'],'failed')
        self.assertEqual(INTRO.pin['engine']['contract_version'],2)
        self.assertEqual(INTRO.pin['engine']['behavior_version'],'linux-service-2')
        with tempfile.TemporaryDirectory() as tmp:
            store=PinnedStore(tmp,FAULT);s=FAULT.domain().session();s.execute('mkdir site');s.execute('systemctl start lab-web');s.submit()
            store.save(s.attempt);raw=store.current.read_bytes()
            fresh=PinnedStore(tmp,FAULT);self.assertEqual(fresh.load(),s.attempt);self.assertEqual(fresh.current.read_bytes(),raw)

    def test_invalid_intro_contract_and_unhealthy_config_rejected(self):
        for change in (
            lambda p:p['engine'].update(contract_version=3),
            lambda p:p['engine'].update(supported_behavior_versions=['linux-service-1']),
            lambda p:p['domain'].update(initial_service='failed'),
            lambda p:p['domain'].update(editable_files=['/etc/lab-web.conf']),
            lambda p:p['domain']['lesson']['steps'][0].update(action='shell'),
            lambda p:p['domain']['lesson'].update(steps=[]),
            lambda p:p['domain']['filesystem']['/etc/lab-web.conf'].update(content='DocumentRoot=/srv/missing\nPort=8080'),
        ):
            p=INTRO.value();change(p)
            with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())

    def test_reset_modes_resume_and_separate_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'config').mkdir();catalogs=[]
            def build():
                b=CatalogBridge(load_bundled_scenarios()[0],root/'data',root/'config');catalogs.append(b);return b
            try:
                b=build();b.importPack(str(INTRO_FILE));b.importPack(str(FAULT_FILE));b.selectLab(INTRO.key,True)
                b.execute('systemctl status lab-web');b.flush();attempt=b.view['attemptId']
                fresh=build();self.assertEqual(fresh.view['attemptId'],attempt);self.assertEqual(fresh.view['guide']['index'],1)
                fresh.execute('systemctl start lab-web');fresh.execute('systemctl status lab-web');fresh.hint();fresh.submit()
                raw=fresh.store.current.read_bytes();fresh.submit();self.assertEqual(fresh.store.current.read_bytes(),raw)
                for key in ('gateway-dns','subnet-boundary','service-firewall',FAULT.key,INTRO.key):fresh.selectLab(key,True)
                self.assertEqual(fresh.view['grade']['score'],100);self.assertTrue(fresh.view['guide']['verified'])
                export=root/'intro.lab.json';personal=root/'personal.attempt.json'
                self.assertTrue(fresh.exportScenario(str(export)));self.assertEqual(export.read_bytes(),INTRO.original_bytes)
                self.assertTrue(fresh.exportAttempt(str(personal),attempt));self.assertIn(attempt,personal.read_text());self.assertNotIn(attempt,export.read_text())
                scenario,added=PackRepository(root/'imported').import_file(export);self.assertTrue(added);self.assertEqual(scenario.pin,INTRO.pin)
                fresh.restart('Challenge');self.assertEqual(fresh.view['guide'],{});self.assertEqual(fresh.session.engine.grade()['score'],0)
                self.assertEqual(fresh.store.history(fresh.view['attemptId'])[0][0]['hints'],1)
                fresh.execute('systemctl start lab-web');fresh.submit();fresh.restart('Learn')
                self.assertEqual(fresh.view['guide']['index'],0);self.assertEqual(fresh.view['hintCount'],0)
                self.assertEqual(fresh.store.history(fresh.view['attemptId'])[1],2)
            finally:
                for b in catalogs:
                    for lab in b.labs.values():lab.timer.stop()


class LinuxLayoutTests(unittest.TestCase):
    def test_layout_write_failure_keeps_choice_in_memory_and_previous_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);config=root/'config';config.mkdir()
            b=CatalogBridge(load_bundled_scenarios()[0],root/'data',config)
            try:
                b.importPack(str(FAULT_FILE));b.selectLab(FAULT.key,True);b.saveLayout({'dock_height':300.0})
                path=config/'linux-workspace-layout.json';raw=path.read_bytes()
                with patch('learning_lab.catalog.atomic_write',side_effect=OSError('fixture disk full')):
                    b.saveLayout({'dock_height':400.0})
                b.execute('help');b.refreshTheme()
                self.assertEqual(b.view['workspaceLayout']['dock_height'],400)
                self.assertEqual(path.read_bytes(),raw);self.assertIn('sizing is temporary',b.view['message'])
            finally:
                for lab in b.labs.values():lab.timer.stop()

    def test_qml_double_sizes_are_saved_without_changing_network_preferences(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);config=root/'config';config.mkdir();catalogs=[]
            def build():
                b=CatalogBridge(load_bundled_scenarios()[0],root/'data',config);catalogs.append(b);return b
            try:
                b=build();b.saveLayout({'mission_width':310.0,'dock_height':230.0});network=(config/'workspace-layout.json').read_bytes()
                b.importPack(str(FAULT_FILE));b.selectLab(FAULT.key,True)
                self.assertEqual(b.view['workspaceLayout'],{})
                b.saveLayout({'mission_width':280.0,'dock_height':420.0})
                for _ in range(5):b.execute('journalctl');b.refreshTheme()
                self.assertEqual(b.view['workspaceLayout'],{'mission_width':280,'dock_height':420})
                self.assertEqual((config/'workspace-layout.json').read_bytes(),network)
                fresh=build();self.assertEqual(fresh.view['workspaceLayout']['dock_height'],420)
                fresh.selectLab('gateway-dns',True);self.assertEqual(fresh.view['workspaceLayout']['dock_height'],230)
                fresh.selectLab(FAULT.key,True);path=config/'linux-workspace-layout.json';raw=path.read_bytes()
                for value in (True,420.5,float('nan'),float('inf'),4000,'420'):
                    fresh.saveLayout({'dock_height':value});self.assertEqual(path.read_bytes(),raw)
                path.write_bytes(b'{"schema_version":99,"sizes":{}}');newer=build();newer.saveLayout({'dock_height':500.0})
                self.assertEqual(path.read_bytes(),b'{"schema_version":99,"sizes":{}}')
                self.assertEqual((config/'workspace-layout.json').read_bytes(),network)
            finally:
                for b in catalogs:
                    for lab in b.labs.values():lab.timer.stop()
