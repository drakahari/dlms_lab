"""User install transactions under a disposable staging root; no real home writes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch
from zipfile import ZipFile
from tools import user_install as installer


class UserInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='install-tests-')
        self.stage = Path(self.temp.name)/'stage with spaces'
        self.target = installer.Installation(self.stage)
        self.wheel = Path(self.temp.name)/'omarchy_learning_lab-0.1.0-py3-none-any.whl'
        with ZipFile(self.wheel, 'w') as z:
            z.writestr('learning_lab/icons/omarchy-learning-lab.svg', '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.commands = []

    def tearDown(self):self.temp.cleanup()

    def runner(self, command, cwd, log):
        # A transaction fixture, not proof of pip or a working installed wheel.
        command = [str(v) for v in command]; self.commands.append(command)
        if 'venv' in command:
            path = Path(command[-1]);(path/'bin').mkdir(parents=True)
            (path/'bin/python').write_text('fixture interpreter')
        log.write_text('Preparation fixture passed\n')

    def prepared(self):
        with patch.object(installer, 'run', side_effect=self.runner):
            return installer.install(self.target, wheel=self.wheel)

    def test_stage_paths_and_desktop_validate(self):
        release = self.prepared()
        self.assertTrue(self.target.root.is_relative_to(self.stage))
        self.assertTrue(self.target.desktop.is_relative_to(self.stage))
        self.assertEqual(self.target.selected('current'), release)
        self.assertIn(str(self.target.launch), self.target.desktop.read_text())
        self.assertIn('Terminal=false', self.target.desktop.read_text())
        self.assertIn('-I -m learning_lab', self.target.launch.read_text())
        self.assertEqual(self.target.launch.stat().st_mode & 0o777, 0o755)
        validator = shutil.which('desktop-file-validate')
        if validator:
            result = subprocess.run([validator,str(self.target.desktop)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_preparation_gate_update_and_rollback(self):
        with self.assertRaises(installer.InstallError):self.target.rollback()
        self.assertFalse(self.target.root.exists())
        first = self.prepared()
        def preparing(command,cwd,log):
            self.assertEqual(self.target.selected('current'),first)
            self.runner(command,cwd,log)
        with patch.object(installer,'run',side_effect=preparing):
            second=installer.install(self.target,wheel=self.wheel)
        self.assertEqual(self.target.selected('current'),second)
        self.assertEqual(self.target.selected('previous'),first)
        self.target.rollback()
        self.assertEqual(self.target.selected('current'),first)
        self.assertEqual(self.target.selected('previous'),second)
        self.assertTrue(first.exists() and second.exists())

    def test_failure_at_each_preparation_stage_preserves_current(self):
        first=self.prepared();desktop=self.target.desktop.read_bytes()
        for fail_index in range(4):  # venv, pip install, pip check, smoke
            calls=[]
            def failing(command,cwd,log):
                if len(calls)==fail_index:raise installer.InstallError('expected fixture failure')
                calls.append(command);self.runner(command,cwd,log)
            with patch.object(installer,'run',side_effect=failing):
                with self.assertRaises(installer.InstallError):installer.install(self.target,wheel=self.wheel)
            self.assertEqual(self.target.selected('current'),first)
            self.assertEqual(self.target.desktop.read_bytes(),desktop)
            self.assertFalse((self.target.root/'.install-lock').exists())

    def test_failed_first_install_publishes_no_launcher(self):
        with patch.object(installer,'run',side_effect=installer.InstallError('blocked dependency')):
            with self.assertRaises(installer.InstallError):installer.install(self.target,wheel=self.wheel)
        self.assertIsNone(self.target.selected('current'))
        self.assertFalse(self.target.desktop.exists());self.assertFalse(self.target.launch.exists())

    def test_missing_icon_or_unprepared_release_cannot_activate(self):
        first=self.prepared()
        bad=Path(self.temp.name)/'bad.whl'
        with ZipFile(bad,'w') as z:z.writestr('unexpected','data')
        with self.assertRaises(KeyError):installer.install(self.target,wheel=bad)
        release=self.target.releases/'unprepared';release.mkdir()
        with self.assertRaises(OSError):self.target.activate(release)
        self.assertEqual(self.target.selected('current'),first)

    def test_unmanaged_application_or_modified_desktop_is_preserved(self):
        self.target.root.mkdir(parents=True);original=self.target.root/'existing.txt';original.write_text('keep')
        with self.assertRaises(installer.InstallError):self.prepared()
        self.assertEqual(original.read_text(),'keep')
        other=installer.Installation(Path(self.temp.name)/'second-stage')
        other.desktop.parent.mkdir(parents=True);other.desktop.write_text('existing desktop entry')
        with self.assertRaises(installer.InstallError):installer.install(other,wheel=self.wheel)
        self.assertEqual(other.desktop.read_text(),'existing desktop entry')

    def test_symlink_escape_and_unsafe_desktop_paths_rejected(self):
        outside=Path(self.temp.name)/'outside';outside.mkdir()
        self.stage.mkdir();(self.stage/'home').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(installer.InstallError):installer.Installation(self.stage)
        for suffix in ('bad%path','bad\npath','bad"path','bad$path'):
            with self.assertRaises(installer.InstallError):installer.Installation(Path(self.temp.name)/suffix)

    def test_lock_and_unsafe_current_are_not_removed(self):
        first=self.prepared();lock=self.target.root/'.install-lock';lock.mkdir()
        with self.assertRaises(installer.InstallError):self.target.rollback()
        self.assertTrue(lock.is_dir());lock.rmdir()
        (self.target.root/'current').unlink();(self.target.root/'current').symlink_to('/tmp')
        with self.assertRaises(installer.InstallError):self.target.check_owned()
        self.assertEqual(os.readlink(self.target.root/'current'),'/tmp')
        self.assertTrue(first.exists())

    def test_launcher_resolves_fixed_release_and_forwards_arguments(self):
        release=self.prepared();python=release/'venv/bin/python'
        # Executable fixture records arguments: no host shell receives learner input.
        python.write_text('#!/bin/sh\nprintf "%s\\n" "$0" "$@"\n');python.chmod(0o755)
        result=subprocess.run([str(self.target.launch),'--data-dir','a path with spaces'],cwd='/',capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.splitlines(),[str(python),'-I','-m','learning_lab','--data-dir','a path with spaces'])

    def test_uninstall_preserves_data_and_unknown_files(self):
        self.prepared()
        personal=self.stage/'data/omarchy-learning-lab/current.json';personal.parent.mkdir(parents=True);personal.write_text('personal fixture')
        config=self.stage/'home/.config/omarchy-learning-lab/preferences.json';config.parent.mkdir(parents=True);config.write_text('config fixture')
        unknown=self.target.root/'keep.txt';unknown.write_text('unknown')
        with self.assertRaises(installer.InstallError):self.target.uninstall()
        self.assertEqual(unknown.read_text(),'unknown');unknown.unlink()
        self.target.uninstall()
        self.assertFalse(self.target.root.exists());self.assertFalse(self.target.desktop.exists())
        self.assertEqual(personal.read_text(),'personal fixture');self.assertEqual(config.read_text(),'config fixture')

    def test_offline_dependency_flags_and_pip_check_before_smoke(self):
        wheelhouse=Path(self.temp.name)/'wheels';wheelhouse.mkdir()
        with patch.object(installer,'run',side_effect=self.runner):
            installer.install(self.target,wheel=self.wheel,wheelhouse=wheelhouse)
        commands=self.commands
        self.assertIn('--no-index',commands[1]);self.assertIn('--only-binary=:all:',commands[1])
        self.assertEqual(commands[2][-2:],['pip','check'])
        self.assertEqual(commands[3][-1],'--require-icon')

    def test_generated_files_do_not_name_personal_data_or_config(self):
        self.prepared()
        text=self.target.launch.read_text()+self.target.desktop.read_text()
        for forbidden in ('--data-dir','--config-dir','XDG_DATA_HOME=','XDG_CONFIG_HOME='):
            self.assertNotIn(forbidden,text)
        self.assertIn('current/icon.svg',text)

    def test_changed_desktop_destination_is_not_silently_adopted(self):
        self.prepared();original=self.target.desktop
        self.target.desktop=self.stage/'other-data/applications/omarchy-learning-lab.desktop'
        with self.assertRaises(installer.InstallError):self.target.check_owned()
        self.assertTrue(original.exists());self.assertFalse(self.target.desktop.exists())

    def test_original_icon_is_valid_and_declared_as_package_data(self):
        from PySide6.QtSvg import QSvgRenderer
        raw=(installer.APP/'learning_lab/icons/omarchy-learning-lab.svg').read_bytes()
        self.assertTrue(QSvgRenderer(raw).isValid())
        config=tomllib.loads((installer.APP/'pyproject.toml').read_text())
        self.assertIn('icons/*.svg',config['tool']['setuptools']['package-data']['learning_lab'])
