"""Profile transfer never touches the owner's XDG roots or installation."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios, ProfileLocks
from learning_lab.catalog import CatalogBridge
from learning_lab import profile_backup as pb
from learning_lab.domain.validation import ValidationError

APP = QCoreApplication.instance() or QCoreApplication([])
ROOT = Path(__file__).resolve().parents[1]


class ProfileBackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='profile-backup-tests-')
        self.root = Path(self.temp.name)
        self.data = self.root/'source/data'; self.config = self.root/'source/config'
        self.data.mkdir(parents=True); self.config.mkdir()
        self.locks = ProfileLocks(self.data, self.config)
        self.b = CatalogBridge(load_bundled_scenarios()[0], self.data, self.config)
        self.b.profile_locks = self.locks
        self.archive = self.root/'profile.llbackup'

    def tearDown(self):
        for lab in self.b.labs.values(): lab.timer.stop()
        self.locks.unlock(); self.temp.cleanup()

    def populate(self):
        b = self.b
        b.edit('gateway', '192.168.50.1'); b.edit('dns', '10.20.0.10'); b.apply(); b.submit(); b.restart('Challenge')
        for row in b.view['fundamentals']: b.selectLab(row['labKey'], True)
        # Real custom import, not just a collection pack.
        value = b.collection[0]['scenario'].value(); value['identity']['id'] = 'custom-backup-navigation'
        source = self.root/'custom.lab.json'; source.write_text(json.dumps(value))
        self.assertTrue(b.importPack(str(source)))
        scenario = next(s for s in b.portables.values() if s.identity.scenario_id == 'custom-backup-navigation')
        b.selectLab(scenario.key); b.execute('pwd'); b.hint(); b.submit(); b.restart('Challenge'); b.execute('ls')
        b.setCommandDraft('cat notes.txt'); b.saveLayout({'mission_width': 310, 'dock_height': 280})
        b.fallbackTheme(True); b.flush()

    def make_backup(self):
        self.assertTrue(self.b.backupProfile(str(self.archive)), self.b.transfer_message)
        return pb.read_backup(self.archive)

    def rewrite(self, *, mutate_manifest=None, change_files=None, extra=None):
        with ZipFile(self.archive) as z: entries = {n: z.read(n) for n in z.namelist()}
        manifest = json.loads(entries.pop('manifest.json'))
        if change_files:
            change_files(entries)
            manifest['files'] = {n: {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'mtime_ns': 1} for n, raw in entries.items()}
        if mutate_manifest: mutate_manifest(manifest)
        with ZipFile(self.archive, 'w') as z:
            z.writestr('manifest.json', json.dumps(manifest))
            for n, raw in entries.items(): z.writestr(n, raw)
            if extra: z.writestr(*extra)

    def test_complete_round_trip_exact_bytes_and_fresh_process_reopen(self):
        self.populate(); backup = self.make_backup()
        before = {k: deepcopy(l.session.attempt) for k, l in self.b.labs.items()}
        self.assertEqual(backup.summary['packs'], 7)
        destination = self.root/'restored'
        pb.restore(backup, destination, confirmed=True)
        for name, raw in backup.files.items():
            self.assertEqual((destination/name).read_bytes(), raw)
            self.assertEqual((destination/name).stat().st_mtime_ns, backup.manifest['files'][name]['mtime_ns'])
        expected = self.root/'expected.json'
        expected.write_text(json.dumps({'attempts': before, 'selected': self.b.view['labKey'], 'layout': self.b.view['workspaceLayout']}))
        probe = '''
import json, sys
from pathlib import Path
from learning_lab.__main__ import build_application
root=Path(sys.argv[1]); expected=json.loads(Path(sys.argv[2]).read_text())
app,e,b,lock=build_application(root/'data',root/'config')
assert {k:l.session.attempt for k,l in b.labs.items()}==expected['attempts']
assert b.view['labKey']==expected['selected']
assert b.view['commandDraft']=='cat notes.txt'
assert b.view['workspaceLayout']==expected['layout']
assert b.force_fallback
assert len(b.portables)==7
assert b.view['mode']=='Challenge'
e.rootObjects()[0].close();app.processEvents();lock.unlock()
print('fresh process resume PASS')
'''
        result = subprocess.run([sys.executable, '-B', '-c', probe, str(destination), str(expected)], cwd=ROOT,
                                env={**os.environ, 'QT_QPA_PLATFORM':'offscreen', 'QT_QPA_PLATFORMTHEME':'', 'QT_QUICK_BACKEND':'software'}, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual({k:l.session.attempt for k,l in self.b.labs.items()}, before)

    def test_exclusions_and_no_overwrite_backup(self):
        for root in (self.data, self.config):
            (root/'credentials.json').write_text('private fixture')
            (root/'cache').mkdir(); (root/'cache/secret.txt').write_text('cache fixture')
            (root/'recovery').mkdir(); (root/'recovery/current.json').write_text('recovery fixture')
        backup = self.make_backup()
        self.assertFalse(any('credentials' in n or 'writer.lock' in n or 'recovery' in n or 'cache' in n for n in backup.files))
        original = self.archive.read_bytes()
        self.assertFalse(self.b.backupProfile(str(self.archive)))
        self.assertEqual(self.archive.read_bytes(), original)

    def test_locked_snapshot_and_pending_draft_flush(self):
        self.b.edit('dns', 'unsaved draft'); self.b.setCommandDraft('ping 10.20.0.10')
        backup = self.make_backup()
        current = json.loads(backup.files['data/current.json'])['attempt']
        self.assertEqual(current['draft']['dns'], 'unsaved draft')
        self.assertTrue(any(json.loads(raw).get('command') == 'ping 10.20.0.10' for n,raw in backup.files.items() if '/workspace/' in n))
        self.locks.unlock()
        with self.assertRaises(ValidationError): pb.snapshot(self.data, self.config, self.locks.locks)
        self.assertFalse(self.b.backupProfile(str(self.root/'unlocked.llbackup')))

    def test_shared_settings_writer_lock_and_released_locks(self):
        other = self.root/'other-data'; other.mkdir()
        with self.assertRaises(RuntimeError): ProfileLocks(other, self.config)
        independent = self.root/'other-config'; independent.mkdir()
        new = ProfileLocks(other, independent); self.assertTrue(new.isLocked()); new.unlock()

    def test_failed_save_stops_backup(self):
        with patch.object(self.b.active.store, 'save', side_effect=OSError('fixture full disk')):
            self.assertFalse(self.b.backupProfile(str(self.archive)))
        self.assertFalse(self.archive.exists())

    def test_readonly_profile_rejected(self):
        self.b.active.store.read_only = True
        self.assertFalse(self.b.backupProfile(str(self.archive)))
        self.assertFalse(self.archive.exists())

    def test_explicit_preview_confirmation_and_cancel(self):
        self.make_backup()
        self.assertFalse(self.b.confirmRestore(True))
        self.assertTrue(self.b.previewRestore(str(self.archive), str(self.root)))
        backup, destination = self.b.restore_pending
        self.assertIn(str(destination), self.b.profile_preview)
        self.assertIn('do not authenticate', self.b.profile_preview)
        self.assertFalse(destination.exists())
        self.b.cancelRestore(); self.assertFalse(destination.exists())
        self.assertTrue(self.b.previewRestore(str(self.archive), str(self.root)))
        self.assertFalse(self.b.confirmRestore(False))
        self.assertTrue(self.b.previewRestore(str(self.archive), str(self.root)))
        destination = self.b.restore_pending[1]
        self.assertTrue(self.b.confirmRestore(True)); self.assertTrue((destination/'data/current.json').exists())
        self.assertEqual(self.b.data_root, self.data)

    def test_transfer_sections_keep_exact_paths_out_of_prose(self):
        import shlex
        self.make_backup()
        result=self.b.view['profileResultDetails']
        self.assertEqual(result['paths'][0]['value'],str(self.archive))
        self.assertNotIn(str(self.archive),result['summary'])
        parent=self.root/('folder with spaces '+ 'a'*80);parent.mkdir()
        self.assertTrue(self.b.previewRestore(str(self.archive),str(parent)))
        destination=self.b.restore_pending[1];view=self.b.view['profilePreviewDetails']
        self.assertEqual([p['value'] for p in view['paths']],list(map(str,(destination,destination/'data',destination/'config'))))
        self.assertNotIn(str(destination),view['summary'])
        self.assertIn('Learn',view['counts']);self.assertIn('Challenge',view['counts'])
        self.assertIn('do not authenticate',view['warning'])
        self.assertTrue(self.b.confirmRestore(True))
        args=self.b.view['profileResultDetails']['paths'][1]['value']
        self.assertEqual(shlex.split(args),['--data-dir',str(destination/'data'),'--config-dir',str(destination/'config')])
        self.assertFalse(self.b.previewRestore(str(self.root/'missing.llbackup'),str(parent)))
        self.assertEqual(self.b.view['profileResultDetails']['summary'],'Restore validation failed.')
        self.assertEqual(self.b.view['profileResultDetails']['paths'][0]['label'],'Error details')

    def test_confirmation_uses_validated_bytes_not_replaced_archive(self):
        self.make_backup(); self.assertTrue(self.b.previewRestore(str(self.archive), str(self.root)))
        expected, destination = self.b.restore_pending
        self.archive.write_bytes(b'changed after preview')
        self.assertTrue(self.b.confirmRestore(True))
        self.assertEqual((destination/'data/current.json').read_bytes(), expected.files['data/current.json'])

    def test_existing_empty_nonempty_and_symlink_destinations_rejected(self):
        backup = self.make_backup()
        for name in ('empty', 'nonempty', 'symlink'):
            path = self.root/name
            if name == 'symlink': path.symlink_to(self.data)
            else: path.mkdir()
            if name == 'nonempty': (path/'keep').write_text('retain')
            with self.assertRaises(ValidationError): pb.restore(backup, path, confirmed=True)
        self.assertEqual((self.root/'nonempty/keep').read_text(), 'retain')
        with self.assertRaises(ValidationError): pb.restore(backup, self.root/'no-confirm')

    def test_destination_created_after_preview_is_preserved(self):
        self.make_backup(); self.b.previewRestore(str(self.archive), str(self.root))
        destination = self.b.restore_pending[1]; destination.mkdir(); (destination/'keep').write_text('untouched')
        self.assertFalse(self.b.confirmRestore(True)); self.assertEqual((destination/'keep').read_text(), 'untouched')

    def test_atomic_publication_never_replaces_a_late_empty_directory(self):
        backup = self.make_backup(); destination = self.root/'late-conflict'
        real_cdll = pb.ctypes.CDLL
        class LateConflict:
            def __init__(self):
                native = real_cdll(None, use_errno=True).renameat2
                def conflict(*args):
                    destination.mkdir()
                    return native(*args)
                self.renameat2 = conflict
        with patch.object(pb.ctypes, 'CDLL', return_value=LateConflict()):
            with self.assertRaises(OSError): pb.restore(backup, destination, confirmed=True)
        self.assertTrue(destination.is_dir()); self.assertEqual(list(destination.iterdir()), [])
        self.assertFalse(list(self.root.glob('.learning-lab-restore-*')))

    def test_failed_write_has_no_usable_partial_restore(self):
        backup = self.make_backup(); destination = self.root/'failed'
        with patch('learning_lab.profile_backup.os.fsync', side_effect=OSError('fixture disk failure')):
            with self.assertRaises(OSError): pb.restore(backup, destination, confirmed=True)
        self.assertFalse(destination.exists()); self.assertFalse(list(self.root.glob('.learning-lab-restore-*')))
        self.assertTrue(self.data.joinpath('current.json').exists())

    def test_corrupt_truncated_and_integrity_mismatch(self):
        self.make_backup(); raw = self.archive.read_bytes()
        for corrupt in (b'not zip', raw[:50], raw[:-20]):
            self.archive.write_bytes(corrupt)
            with self.assertRaises(ValueError): pb.read_backup(self.archive)
        self.archive.write_bytes(raw)
        self.rewrite(mutate_manifest=lambda m: m['files']['data/current.json'].update(sha256='0'*64))
        with self.assertRaisesRegex(ValueError, 'integrity'): pb.read_backup(self.archive)

    def test_unsupported_manifest_and_legacy_resource_versions(self):
        self.make_backup(); raw = self.archive.read_bytes()
        for change in (lambda m:m.update(schema_version=99), lambda m:m['legacy_resources'].update({'gateway-dns':'0'*64})):
            self.archive.write_bytes(raw); self.rewrite(mutate_manifest=change)
            with self.assertRaises(ValueError): pb.read_backup(self.archive)

    def test_oversize_file_total_archive_and_entry_count(self):
        self.make_backup()
        for key,value in (('MAX_ARCHIVE',20), ('MAX_TOTAL',20), ('MAX_FILES',1)):
            with patch.object(pb,key,value):
                with self.assertRaises(ValueError): pb.read_backup(self.archive)
        self.rewrite(extra=('config/preferences.json',b' '*4097))
        with self.assertRaises(ValueError): pb.read_backup(self.archive)

    def test_paths_duplicates_and_nonregular_archive_entries(self):
        self.make_backup(); raw = self.archive.read_bytes()
        for name in ('../escape', '/absolute', 'data/../escape', 'data\\current.json', 'data//current.json', 'manifest.json'):
            self.archive.write_bytes(raw); self.rewrite(extra=(name,b'bad'))
            with self.assertRaises(ValueError): pb.read_backup(self.archive)
        for kind in (stat.S_IFLNK, stat.S_IFIFO, stat.S_IFDIR, stat.S_IFREG | 0o111):
            self.archive.write_bytes(raw)
            info=ZipInfo('config/preferences.json');info.external_attr=(kind|0o600)<<16
            self.rewrite(extra=(info,b'target'))
            with self.assertRaises(ValueError): pb.read_backup(self.archive)
        self.assertFalse((self.root/'escape').exists())

    def test_source_symlink_and_fifo_rejected_without_blocking(self):
        self.make_backup(); self.archive.unlink()
        current=self.data/'current.backup.json'; current.unlink(); current.symlink_to(self.data/'current.json')
        self.assertFalse(self.b.backupProfile(str(self.archive)))
        # The save itself replaces the backup, so test snapshot boundaries directly.
        current.unlink(); current.symlink_to(self.data/'current.json')
        with self.assertRaises((OSError,ValueError)): pb.snapshot(self.data,self.config,self.locks.locks)
        current.unlink(); os.mkfifo(current)
        with self.assertRaises(ValueError): pb.snapshot(self.data,self.config,self.locks.locks)

    def test_missing_pack_and_changed_pin_rejected_even_with_valid_hashes(self):
        self.populate(); self.make_backup(); raw=self.archive.read_bytes()
        self.rewrite(change_files=lambda files: files.pop(next(n for n in files if pb.PACK.fullmatch(n))))
        with self.assertRaises(ValueError): pb.read_backup(self.archive)
        self.archive.write_bytes(raw)
        def change(files):
            name=next(n for n in files if '/portable/attempts/' in n and n.endswith('/current.json'))
            value=json.loads(files[name]); value['pin']['engine']['behavior_version']='unknown'
            files[name]=json.dumps(value).encode()
        self.rewrite(change_files=change)
        with self.assertRaises(ValueError): pb.read_backup(self.archive)

    def test_bad_record_workspace_selection_and_settings(self):
        self.b.setCommandDraft('pwd'); self.b.flush(); self.make_backup(); raw=self.archive.read_bytes()
        changes=[lambda f:f.update({'config/selection.json':b'{"schema_version":1,"lab_id":"missing"}'}),
                 lambda f:f.update({'config/preferences.json':b'{"schema_version":2,"fallback_theme":true}'}),
                 lambda f:f.update({'data/current.json':b'{"schema_version":900}'}),
                 lambda f:f.update({'data/workspace/00000000-0000-0000-0000-000000000000.json':b'{"schema_version":1,"command":"","diagnostic_revision":-1,"diagnostics":[]}'})]
        for change in changes:
            self.archive.write_bytes(raw);self.rewrite(change_files=change)
            with self.assertRaises(ValueError):pb.read_backup(self.archive)

    def test_imported_content_cannot_supply_code_or_host_paths(self):
        self.populate();self.make_backup()
        def change(files):
            name=next(n for n in files if pb.PACK.fullmatch(n)); value=json.loads(files[name])
            value['script']='__import__("os").system("false")';files[name]=json.dumps(value).encode()
        self.rewrite(change_files=change)
        with patch('subprocess.Popen',side_effect=AssertionError('no execution')), patch('socket.socket',side_effect=AssertionError('no networking')):
            with self.assertRaises(ValueError):pb.read_backup(self.archive)

    def test_backup_and_restore_refuse_active_profile_destinations(self):
        self.assertFalse(self.b.backupProfile(str(self.data/'backup.llbackup')))
        self.make_backup()
        self.assertFalse(self.b.previewRestore(str(self.archive),str(self.data)))
