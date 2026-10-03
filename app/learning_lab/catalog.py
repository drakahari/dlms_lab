"""Bundled lab selection; independent attempt stores under one writer lock."""
import json
from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl
from pathlib import Path
from .bridge import Bridge
from .storage import Store, atomic_write
from .domain.validation import decode, ValidationError
from .portable import PackRepository, portable_from_legacy
from .pinned_storage import PinnedStore


class CatalogBridge(QObject):
    changed = Signal()

    def __init__(self, packs, data_root, config_root):
        super().__init__()
        self.data_root, self.config_root = Path(data_root), Path(config_root)
        self.repository = PackRepository(self.data_root / 'portable' / 'packs')
        self.portables = {}
        # Gateway's original root is a compatibility exception. IDs have already
        # passed the strict pack validator; packs never supply filesystem paths.
        roots = {p['lab_id']: data_root if p['lab_id'] == 'gateway-dns' else data_root / 'labs' / p['lab_id'] for p in packs}
        self.labs = {p['lab_id']: Bridge(p, Store(roots[p['lab_id']], p), config_root / 'preferences.json', self) for p in packs}
        scenarios, pack_warnings = self.repository.scan()
        for scenario in scenarios: self._add_portable(scenario, connect=False)
        self.active = self.labs.get('gateway-dns', next(iter(self.labs.values())))
        self.selection_path = config_root / 'selection.json'
        self.selection_readonly = False
        self.notice = '\n'.join(pack_warnings)
        self.transfer_message = ''
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
        result['provenance'] = ('Pinned content ' + self.portables[active_key].identity.content_digest + ' · engine networking-1'
                                if active_key in self.portables else 'Legacy attempt: original content digest and engine provenance were not recorded.')
        result['transferMessage'] = self.transfer_message
        result['catalogNotice'] = self.notice
        result['workspaceLayout'] = dict(self.workspace_layout)
        result['canRetry'] = any(lab.save_failed for lab in self.labs.values())
        if any(lab.save_failed for lab in self.labs.values() if lab is not self.active):
            result['message'] += ' Another lab has unsaved progress. Retry save before closing.'
        result['message'] += self.notice
        return result

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
            self._validate_layout(sizes)
            if not self.layout_readonly:
                self.config_root.mkdir(parents=True,exist_ok=True)
                atomic_write(self.layout_path,json.dumps({'schema_version':1,'sizes':sizes}).encode())
            self.workspace_layout=dict(sizes)
            self.changed.emit()
        except (OSError,ValueError) as exc:
            self.transfer_message='Layout could not be saved: '+str(exc)
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
