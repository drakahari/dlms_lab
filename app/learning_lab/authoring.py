"""Authoring files are untrusted data. Preview is memory-only; import is explicit."""
import hashlib
from importlib.resources import files
import json
import os
from pathlib import Path
import stat
import tempfile
from uuid import uuid4

from PySide6.QtCore import QObject, Property, Signal, Slot
from .domain.validation import require
from .portable import LIMIT


def resource(name):
    require(name in ('permissions.lab.json', 'guide.txt', 'prompt.txt'), 'Unknown authoring resource.')
    return files('learning_lab').joinpath('authoring_resources', name).read_text(encoding='utf-8')


def read_json_file(path):
    # O_NONBLOCK prevents a substituted FIFO from hanging validation. No links,
    # devices or directories, and never an unbounded read of imported content.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'Choose a regular JSON file, not a link, device or directory.')
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, 'File exceeds 256 KiB. Reduce virtual content before validating.')
    return raw


def fingerprint(path):
    info = path.lstat()
    raw = read_json_file(path)
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, hashlib.sha256(raw).hexdigest())


class AuthoringBridge(QObject):
    changed = Signal()

    def __init__(self, catalog):
        super().__init__(catalog)
        self.catalog = catalog
        self.message = ''; self.summary = ''; self.pending = None; self.saving = None

    @Property('QVariantMap', notify=changed)
    def view(self):
        # Fixed shipped names only; packs cannot supply resource paths.
        return {'guide':resource('guide.txt'), 'example':resource('permissions.lab.json'),
                'prompt':resource('prompt.txt')+'\n\n'+resource('permissions.lab.json'), 'message':self.message, 'summary':self.summary,
                'canImport':self.pending is not None, 'saveReady':self.saving is not None,
                'savePath':str(self.saving[0]) if self.saving else '',
                'replacing':self.saving is not None and self.saving[2] is not None}

    def protected(self, path):
        resolved = path.resolve()
        require(not any(resolved.is_relative_to(root.resolve()) for root in
                        (self.catalog.data_root, self.catalog.config_root, Path(__file__).parent)),
                'Save authoring files outside the active profile and application resources.')

    @Slot(str, result=bool)
    def prepareStarter(self, value):
        self.saving = None; self.pending = None; self.summary = ''
        try:
            path = self.catalog._local_path(value)
            self.protected(path)
            require(path.name.endswith('.lab.json'), 'Choose a filename ending in .lab.json.')
            require(path.parent.is_dir(), 'Choose an existing destination folder.')
            previous = fingerprint(path) if path.exists() or path.is_symlink() else None
            pack = json.loads(resource('permissions.lab.json'))
            pack['identity'] = {'id':'my-permissions-'+uuid4().hex, 'content_version':'1.0.0'}
            pack['metadata']['title'] = 'My private notes lab'
            raw = (json.dumps(pack, ensure_ascii=False, indent=2)+'\n').encode()
            _, added = self.catalog.repository.check(raw)
            require(added, 'Generated identity already exists; choose Save starter again.')
            self.saving = (path, raw, previous)
            self.message = 'Confirm the destination. The starter has a new scenario ID; no pack is installed.'
            self.changed.emit(); return True
        except (OSError, ValueError) as exc:
            self.message = 'Starter not saved: '+str(exc)
            self.changed.emit(); return False

    @Slot(bool, result=bool)
    def confirmStarter(self, confirmed):
        pending = self.saving; self.saving = None
        temporary = None
        try:
            if confirmed is not True:
                self.message = 'Save cancelled. No file was changed.'
                self.changed.emit(); return False
            require(pending is not None, 'Choose a destination and preview it first.')
            path, raw, previous = pending
            self.protected(path)
            if previous is not None:
                require(fingerprint(path) == previous, 'Destination changed since preview; choose it again before replacing.')
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.lab-starter-', delete=False) as stream:
                temporary = Path(stream.name); stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            if previous is None:
                # Atomic no-clobber publication even if a file appeared after preview.
                os.link(temporary, path)
            else:
                require(fingerprint(path) == previous, 'Destination changed; replacement cancelled.')
                os.replace(temporary, path)
            self.message = 'Starter saved to '+str(path)+'. Edit it in a text editor, then Validate lab. It is not installed.'
            self.changed.emit(); return True
        except (OSError, ValueError) as exc:
            self.message = 'Starter not saved: '+str(exc)
            self.changed.emit(); return False
        finally:
            if temporary is not None: temporary.unlink(missing_ok=True)

    @Slot(str, result=bool)
    def validateLab(self, value):
        self.pending = None; self.summary = ''
        try:
            path = self.catalog._local_path(value)
            raw = read_json_file(path)
            scenario, added = self.catalog.repository.check(raw)
            pack = scenario.value(); engine = pack['engine']
            self.summary = ('Title: '+pack['metadata']['title']+'\nEngine: '+engine['id']+
                ' · contract '+str(engine['contract_version'])+'\nScenario ID: '+pack['identity']['id']+
                '\nContent version: '+pack['identity']['content_version']+'\nBehavior: '+', '.join(engine['supported_behavior_versions'])+
                '\n\nGoals:\n'+'\n'.join('• '+o['label']+' ('+str(o['points'])+' points)' for o in pack['objectives'])+
                '\n\n'+('Ready for explicit import.' if added else 'Identical content already installed; import will not duplicate or restore an inactive entry.')+
                '\nValidation checks structure, supported contracts and the engine’s goal constraints. This summary is not a gameplay test or a teaching-quality review.')
            self.pending = (path, raw)
            self.message = 'Valid pack. No pack was installed and no profile file was changed.'
            self.changed.emit(); return True
        except (OSError, ValueError) as exc:
            self.message = ('Validation failed: '+str(exc)+'\nFix the reported field or JSON line/column, save, then validate again. '
                'Compare engine, identity, objectives and domain fields with the worked example. No pack was installed.')
            self.changed.emit(); return False

    @Slot(result=bool)
    def importValidated(self):
        pending = self.pending; self.pending = None
        try:
            require(pending is not None, 'Validate a file before importing.')
            path, raw = pending
            require(read_json_file(path) == raw, 'File changed since validation. Validate it again before importing.')
            # Install the reviewed bytes, not a second racing read of the source.
            ok = self.catalog._import_raw(raw)
            self.message = self.catalog.transfer_message
            self.changed.emit(); return ok
        except (OSError, ValueError) as exc:
            self.message = 'Import stopped: '+str(exc)
            self.changed.emit(); return False
