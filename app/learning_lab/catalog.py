"""Bundled lab selection; independent attempt stores under one writer lock."""
import json
from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl
from pathlib import Path
from .bridge import Bridge
from .storage import Store, atomic_write
from .domain.validation import decode, ValidationError
from .portable import PackRepository, portable_from_legacy
from .pinned_storage import PinnedStore
from .collections import linux_fundamentals


class CatalogBridge(QObject):
    changed = Signal()

    def __init__(self, packs, data_root, config_root):
        super().__init__()
        self.data_root, self.config_root = Path(data_root), Path(config_root)
        self.repository = PackRepository(self.data_root / 'portable' / 'packs')
        self.portables = {}
        try:
            self.collection = linux_fundamentals()
            collection_warning = ''
        except (OSError, ValueError) as exc:
            self.collection = []
            collection_warning = 'Linux Fundamentals unavailable: ' + str(exc)
        # Gateway's original root is a compatibility exception. IDs have already
        # passed the strict pack validator; packs never supply filesystem paths.
        roots = {p['lab_id']: data_root if p['lab_id'] == 'gateway-dns' else data_root / 'labs' / p['lab_id'] for p in packs}
        self.labs = {p['lab_id']: Bridge(p, Store(roots[p['lab_id']], p), config_root / 'preferences.json', self) for p in packs}
        scenarios, pack_warnings = self.repository.scan()
        for scenario in scenarios: self._add_portable(scenario, connect=False)
        self.active = self.labs.get('gateway-dns', next(iter(self.labs.values())))
        self.selection_path = config_root / 'selection.json'
        self.selection_readonly = False
        self.notice = '\n'.join(pack_warnings + ([collection_warning] if collection_warning else []))
        self.transfer_message = ''
        self.profile_locks = None
        self.restore_pending = None
        self.profile_preview = ''
        self.profile_preview_details = {}
        self.profile_result_details = {}
        self.layout_notice = ''
        self.workspace_layout = {}
        self.layout_path = self.config_root/'workspace-layout.json'
        self.layout_readonly = False
        try:
            if self.layout_path.exists():
                saved=decode(self.layout_path.read_bytes(),4096)
                if not isinstance(saved,dict) or set(saved)!={'schema_version','sizes'} or type(saved['schema_version']) is not int or saved['schema_version']!=1:
                    raise ValueError('Unsupported layout file')
                self._validate_layout(saved['sizes'])
                self.workspace_layout=saved['sizes']
        except (OSError,ValueError):
            self.layout_readonly=True
            self.notice+=' Unsupported layout preferences preserved; layout changes are temporary.'
        self.linux_layout = {}
        self.linux_layout_path = self.config_root/'linux-workspace-layout.json'
        self.linux_layout_readonly = False
        try:
            if self.linux_layout_path.exists():
                saved=decode(self.linux_layout_path.read_bytes(),4096)
                if not isinstance(saved,dict) or set(saved)!={'schema_version','sizes'} or type(saved['schema_version']) is not int or saved['schema_version']!=1:
                    raise ValueError('Unsupported Linux layout file')
                self._validate_layout(saved['sizes'])
                self.linux_layout=saved['sizes']
        except (OSError,ValueError):
            self.linux_layout_readonly=True
            self.notice+=' Unsupported Linux layout preferences preserved; Linux layout changes are temporary.'
        try:
            if self.selection_path.exists():
                selection = decode(self.selection_path.read_bytes(), 4096)
                if not isinstance(selection, dict) or set(selection) != {'schema_version', 'lab_id'} or type(selection['schema_version']) is not int or selection['schema_version'] != 1 or selection['lab_id'] not in self.labs:
                    raise ValueError('Unsupported selection')
                self.active = self.labs[selection['lab_id']]
        except (OSError, ValueError, TypeError):
            self.selection_readonly = True
            self.notice += ' Invalid or unsupported library selection preserved; selection is temporary.'
        for lab in self.labs.values():
            lab.changed.connect(self.changed)

    @Property('QVariantMap', notify=changed)
    def view(self):
        result = self.active.view
        active_key = next(key for key, lab in self.labs.items() if lab is self.active)
        result['labKey'] = active_key
        result['labs'] = []
        result['allHistory'] = []
        for key, lab in self.labs.items():
            view=lab.view
            result['allHistory'] += [{**row,'labTitle':lab.pack['metadata']['title'],'labKey':key} for row in view['history']]
            result['labs'].append({**{k:view[k] for k in ('labId','metadata','libraryBest','libraryStatus','historyCount')},
                                   'labKey':key,'version':lab.pack['content_version'],
                                   'origin':'Portable pack' if key in self.portables else 'Bundled legacy'})
        result['scenarioVersion'] = self.pack['content_version']
        result['fundamentals'] = self.collection_rows()
        curated = {row['labKey'] for row in result['fundamentals']}
        result['otherLabs'] = [row for row in result['labs'] if row['labKey'] not in curated]
        result['provenance'] = ('Pinned content ' + self.portables[active_key].identity.content_digest + ' · engine ' + self.portables[active_key].pin['engine']['behavior_version']
                                if active_key in self.portables else 'Legacy attempt: original content digest and engine provenance were not recorded.')
        result['profilePreviewDetails'] = self.profile_preview_details
        result['profileResultDetails'] = self.profile_result_details
        result['profilePreview'] = self.profile_preview
        result['restoreReady'] = self.restore_pending is not None
        result['transferMessage'] = self.transfer_message
        result['catalogNotice'] = self.notice
        result['workspaceLayout'] = dict(self.linux_layout if self.active.domain.workspace=='linux-service' else self.workspace_layout)
        result['canRetry'] = any(lab.save_failed for lab in self.labs.values())
        if any(lab.save_failed for lab in self.labs.values() if lab is not self.active):
            result['message'] += ' Another lab has unsaved progress. Retry save before closing.'
        result['message'] += self.notice + self.layout_notice
        return result

    def collection_rows(self):
        rows = []
        for entry in self.collection:
            scenario = entry['scenario']; key = scenario.key
            conflict = any((s.identity.scenario_id, s.identity.content_version) ==
                           (scenario.identity.scenario_id, scenario.identity.content_version)
                           and s.key != key for s in self.portables.values())
            lab = self.labs.get(key)
            progress = lab.library_progress() if lab else None
            prior = (self.data_root/'portable'/'attempts'/key[5:]).exists()
            if not lab and not prior and not conflict:
                progress = {'Learn': 'Not started', 'Challenge': 'Not started'}
            status = ' · '.join(mode + ': ' + state for mode, state in progress.items()) if progress else ''
            started = prior or (progress and any(v != 'Not started' for v in progress.values()))
            rows.append({'labKey': key, 'title': scenario.value()['metadata']['title'],
                         'skill': entry['skill'], 'status': status,
                         'action': 'Continue' if started else 'Start', 'available': not conflict,
                         'problem': 'A different pack with this ID/version is installed. It is preserved below; this collection version cannot replace it.' if conflict else '',
                         'version': scenario.identity.content_version})
        return rows

    def _add_portable(self, scenario, connect=True):
        if scenario.key in self.labs: return
        store = PinnedStore(self.data_root/'portable'/'attempts'/scenario.key[5:], scenario)
        lab = Bridge(scenario.legacy_pack(), store, self.config_root/'preferences.json', self, domain=scenario.domain())
        self.labs[scenario.key] = lab
        self.portables[scenario.key] = scenario
        if connect: lab.changed.connect(self.changed)

    @staticmethod
    def _local_path(value):
        url=QUrl(value)
        path=Path(url.toLocalFile()) if url.isLocalFile() else Path(value)
        if not path.is_absolute() or (url.scheme() and not url.isLocalFile()):
            raise ValidationError('Choose a local file; network URLs are not supported.')
        return path

    @staticmethod
    def _validate_layout(value):
        if not isinstance(value,dict) or not set(value)<={'mission_width','mission_height','dock_height'} or not all(type(v) is int and 60<=v<=1800 for v in value.values()):
            raise ValidationError('Invalid workspace layout sizes.')

    @Slot('QVariantMap')
    def saveLayout(self, sizes):
        try:
            # QML JavaScript numbers arrive as doubles even after Math.round().
            # Normalize the UI boundary only; disk validation stays strict.
            if isinstance(sizes,dict):
                sizes={k:int(v) if type(v) is float and v.is_integer() and 60<=v<=1800 else v for k,v in sizes.items()}
            self._validate_layout(sizes)
            linux=self.active.domain.workspace=='linux-service'
            readonly=self.linux_layout_readonly if linux else self.layout_readonly
            path=self.linux_layout_path if linux else self.layout_path
            # Keep a valid user's choice in memory even if disk persistence fails.
            if linux:self.linux_layout=dict(sizes)
            else:self.workspace_layout=dict(sizes)
            if not readonly:
                self.config_root.mkdir(parents=True,exist_ok=True)
                atomic_write(path,json.dumps({'schema_version':1,'sizes':sizes}).encode())
            self.layout_notice=''
            self.changed.emit()
        except (OSError,ValueError) as exc:
            self.transfer_message='Layout could not be saved: '+str(exc)
            self.layout_notice=' '+self.transfer_message+' Current sizing is temporary.'
            self.changed.emit()

    @Slot(str, result=bool)
    def importPack(self, value):
        try:
            scenario, added = self.repository.import_file(self._local_path(value))
            self._add_portable(scenario)
            self.transfer_message = ('Imported ' if added else 'Already installed: ') + scenario.identity.scenario_id + ' · ' + scenario.identity.content_version
            self.changed.emit()
            return True
        except (OSError, ValueError) as exc:
            self.transfer_message = str(exc) + ' Existing labs and attempts are preserved.'
            self.changed.emit()
            return False

    @Slot(str, result=bool)
    def exportScenario(self, value):
        try:
            key=next(key for key,lab in self.labs.items() if lab is self.active)
            scenario=self.portables[key] if key in self.portables else portable_from_legacy(self.pack)
            atomic_write(self._local_path(value), scenario.original_bytes)
            self.transfer_message='Scenario exported. No personal attempts, commands, or hint usage were included.'
            self.changed.emit(); return True
        except (OSError,ValueError) as exc:
            self.transfer_message='Export failed: '+str(exc)
            self.changed.emit(); return False

    @Slot(str)
    def setCommandDraft(self, value):
        if isinstance(value,str) and len(value)<=512:
            self.active.edit_command(value)

    @Slot(str)
    def execute(self, command):
        self.active.command_draft=''
        self.active.execute(command)

    @Slot(str, str, result=bool)
    def exportAttempt(self, value, attempt_id):
        try:
            from uuid import UUID
            from .workspace_state import load_workspace
            if str(UUID(attempt_id)) != attempt_id: raise ValidationError('Invalid attempt ID.')
            if attempt_id == self.session.attempt['id']:
                if self.store.read_only: raise ValidationError('Current attempt is in recovery mode; preserve its original files before exporting.')
                self.active.flush()
                if self.active.save_failed: raise ValidationError('Save the current attempt before exporting it.')
                raw=self.store.encode_record(self.session.attempt)
            else:
                raw,_=self.store.read(self.store.archives/(attempt_id+'.json'))
            document={'format':'learning-lab.attempt-history','schema_version':1,
                      'record_json':raw.decode('utf-8'),'workspace':load_workspace(self.store,attempt_id),
                      'provenance':'Pinned in record' if self.store.__class__ is PinnedStore else 'Legacy record: exact content/engine provenance unknown'}
            atomic_write(self._local_path(value),json.dumps(document,ensure_ascii=False,indent=2).encode())
            self.transfer_message='Personal attempt exported separately from scenario content.'
            self.changed.emit();return True
        except (OSError,ValueError) as exc:
            self.transfer_message='Attempt export failed: '+str(exc)
            self.changed.emit();return False

    @staticmethod
    def _profile_error(summary, error):
        # OS errors can embed arbitrarily long paths; keep those selectable and
        # horizontally scrollable instead of splitting words in the prose.
        return {'summary': summary, 'paths': [{'label': 'Error details', 'value': str(error)}]}

    @Slot(str, result=bool)
    def backupProfile(self, value):
        try:
            from .profile_backup import snapshot, write_backup
            path = self._local_path(value)
            if any(path.resolve().is_relative_to(root.resolve()) for root in (self.data_root, self.config_root)):
                raise ValidationError('Save the backup outside the active profile folders.')
            if self.profile_locks is None or not self.profile_locks.isLocked():
                raise ValidationError('Backup needs the running app’s profile writer locks.')
            if any(lab.store.read_only or lab.config_readonly for lab in self.labs.values()) or self.selection_readonly or self.layout_readonly or self.linux_layout_readonly:
                raise ValidationError('Resolve profile recovery or unsupported settings before creating a restorable backup.')
            # Preflight before save: do not silently replace damaged files or links.
            snapshot(self.data_root, self.config_root, self.profile_locks.locks)
            # Synchronous GUI slot: actions/timers remain paused until this returns.
            self.flush()
            if any(lab.save_failed for lab in self.labs.values()):
                raise ValidationError('Progress could not be saved. Retry save before backing up.')
            backup = snapshot(self.data_root, self.config_root, self.profile_locks.locks)
            write_backup(backup, path)
            self.transfer_message = 'Profile backup saved and verified: '+str(path)+'. It includes personal progress; keep it private.'
            self.profile_result_details = {'summary': 'Profile backup saved and verified.',
                'paths': [{'label': 'Backup file', 'value': str(path)}],
                'warning': 'This backup includes personal progress. Keep it private.'}
            self.changed.emit(); return True
        except (OSError, ValueError) as exc:
            self.transfer_message = 'Backup failed: '+str(exc)
            self.profile_result_details = self._profile_error('Backup failed.', exc)
            self.changed.emit(); return False

    @Slot(str, str, result=bool)
    def previewRestore(self, archive, parent):
        self.restore_pending = None
        self.profile_preview = ''
        self.profile_preview_details = {}
        try:
            from datetime import datetime, timezone
            from uuid import uuid4
            from .profile_backup import read_backup, validate_destination
            backup = read_backup(self._local_path(archive))
            name = 'Learning-Lab-restored-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid4().hex[:6]
            destination = validate_destination(self._local_path(parent)/name)
            if any(destination.resolve().is_relative_to(root.resolve()) for root in (self.data_root, self.config_root)):
                raise ValidationError('Choose a destination outside the active profile folders.')
            self.restore_pending = (backup, destination)
            summary = backup.summary
            self.profile_preview_details = {
                'summary': 'Restore this backup into a new, separate profile. Your open profile will not change.',
                'created': 'Created: '+backup.manifest['created_utc'],
                'counts': (f"{summary['profiles']} lab profiles · {summary['packs']} installed packs\n"
                           f"{summary['history_records']} archived attempts\n"
                           f"{summary['learn_records']} Learn / {summary['challenge_records']} Challenge records\n"
                           f"{summary['files']} files · {summary['bytes']} bytes, including drafts, workspace state and saved settings."),
                'labs': '; '.join(summary['lab_titles']),
                'paths': [{'label': 'New profile folder', 'value': str(destination)},
                          {'label': 'Progress and packs', 'value': str(destination/'data')},
                          {'label': 'Settings', 'value': str(destination/'config')}],
                'warning': 'Nothing is merged or overwritten. Hashes detect corruption, but do not authenticate an untrusted backup. Restore only backups you trust.'}
            self.profile_preview = (f"Created: {backup.manifest['created_utc']}\n"
                f"{summary['profiles']} lab profiles · {summary['packs']} installed scenario packs\n"
                f"{summary['history_records']} archived attempts · {summary['learn_records']} Learn / {summary['challenge_records']} Challenge records\n"
                f"{summary['files']} files · {summary['bytes']} bytes, including drafts, workspace state and saved settings.\n\n"
                "Included labs: "+"; ".join(summary['lab_titles'])+"\n\n"
                f"New destination: {destination}\nData: {destination/'data'}\nSettings: {destination/'config'}\n\n"
                "The open profile will not change. Nothing is merged or overwritten. Hashes detect corruption, but do not authenticate an untrusted backup. Restore only backups you trust.")
            self.changed.emit(); return True
        except (OSError, ValueError) as exc:
            self.transfer_message = 'Restore validation failed: '+str(exc)
            self.profile_result_details = self._profile_error('Restore validation failed.', exc)
            self.changed.emit(); return False

    @Slot()
    def cancelRestore(self):
        self.restore_pending = None; self.profile_preview = ''; self.profile_preview_details = {}; self.changed.emit()

    @Slot(bool, result=bool)
    def confirmRestore(self, confirmed):
        try:
            import shlex
            from .profile_backup import restore
            if confirmed is not True or self.restore_pending is None:
                raise ValidationError('Preview the backup and explicitly confirm the new destination first.')
            backup, destination = self.restore_pending
            restore(backup, destination, confirmed=True)
            self.transfer_message = ('Profile restored to '+str(destination)+'. Your open profile is unchanged. '
                'Reopen using Learning Lab with --data-dir '+shlex.quote(str(destination/'data'))+
                ' --config-dir '+shlex.quote(str(destination/'config')))
            self.profile_result_details = {'summary': 'Profile restored. Your open profile is unchanged.',
                'paths': [{'label': 'Restored profile folder', 'value': str(destination)},
                          {'label': 'Launch arguments', 'value': '--data-dir '+shlex.quote(str(destination/'data'))+' --config-dir '+shlex.quote(str(destination/'config'))}],
                'warning': 'Close the app normally, then use these arguments when launching Learning Lab to open the restored copy.'}
            self.profile_preview = self.transfer_message
            self.restore_pending = None
            self.changed.emit(); return True
        except (OSError, ValueError) as exc:
            self.transfer_message = 'Restore failed: '+str(exc)+' The open profile is unchanged.'
            self.profile_result_details = self._profile_error('Restore failed. Your open profile is unchanged.', exc)
            self.restore_pending = None
            self.profile_preview = self.transfer_message
            self.changed.emit(); return False

    # Python access for native acceptance and diagnostics; QML uses view/slots.
    @property
    def session(self): return self.active.session
    @property
    def pack(self): return self.active.pack
    @property
    def store(self): return self.active.store
    @property
    def page(self): return self.active.page
    @property
    def selected(self): return self.active.selected
    @property
    def force_fallback(self): return self.active.force_fallback
    @property
    def theme_name(self): return self.active.theme_name

    @Slot(str, bool, result=bool)
    def selectLab(self, lab_id, confirmed=False):
        if lab_id not in self.labs:
            entry = next((e for e in self.collection if e['scenario'].key == lab_id), None)
            if entry is None or (self.session.attempt['draft'] and not confirmed):
                return False
            try:
                scenario, _ = self.repository.install(entry['scenario'].original_bytes)
                self._add_portable(scenario)
            except (OSError, ValueError) as exc:
                self.transfer_message = 'Collection could not open: ' + str(exc) + ' Existing files are preserved.'
                self.changed.emit()
                return False
        if self.active is not self.labs[lab_id]:
            if self.session.attempt['draft'] and not confirmed:
                return False
            self.active.flush()
            if self.active.save_failed:
                return False
            self.active = self.labs[lab_id]
            if not self.selection_readonly:
                try:
                    atomic_write(self.selection_path, json.dumps({'schema_version': 1, 'lab_id': lab_id}).encode())
                except OSError as exc:
                    self.notice = f' Selection is temporary; could not save library selection: {exc}'
        self.active.navigate(1)
        return True

    @Slot()
    def flush(self):
        for lab in self.labs.values(): lab.flush()
    @Slot()
    def retrySave(self):
        for lab in self.labs.values(): lab.retrySave()
    @Slot(str, str)
    def edit(self, field, value): self.active.edit(field, value)
    @Slot()
    def apply(self): self.active.apply()
    @Slot(int)
    def selectRule(self, index): self.active.selectRule(index)
    @Slot(str, str)
    def editRule(self, field, value): self.active.editRule(field, value)
    @Slot(str)
    def editDefault(self, value): self.active.editDefault(value)
    @Slot()
    def addRule(self): self.active.addRule()
    @Slot()
    def removeRule(self): self.active.removeRule()
    @Slot(int)
    def moveRule(self, offset): self.active.moveRule(offset)
    @Slot()
    def test(self): self.active.test()
    @Slot()
    def hint(self): self.active.hint()
    @Slot()
    def submit(self): self.active.submit()
    @Slot(str)
    def restart(self, mode): self.active.restart(mode)
    @Slot(int)
    def navigate(self, page): self.active.navigate(page)
    @Slot(str)
    def selectDevice(self, device): self.active.selectDevice(device)
    @Slot(int, result=str)
    def commandHistory(self, distance): return self.active.commandHistory(distance)
    @Slot(int)
    def historyPage(self, offset): self.active.historyPage(offset)
    @Slot()
    def refreshTheme(self):
        for lab in self.labs.values(): lab.refreshTheme()
    @Slot(bool)
    def fallbackTheme(self, enabled):
        self.active.fallbackTheme(enabled)
        for lab in self.labs.values():
            if lab is not self.active:
                lab.force_fallback = enabled
                lab.refreshTheme()
