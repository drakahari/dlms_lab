"""Bounded, data-only profile snapshots. Never merges or activates over a profile."""
from dataclasses import dataclass
from datetime import datetime, timezone
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import zlib
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED, BadZipFile

from .domain.validation import decode, keys, require, ValidationError
from .storage import MAX_RECORD, validate_record
from .portable import load_portable, MAX_PACKS, LIMIT
from .pinned_storage import PinnedStore
from .workspace_state import validate as validate_workspace

FORMAT = 'learning-lab.profile-backup'
VERSION = 2
MAX_FILES = 10000
MAX_TOTAL = 128 * 1024 * 1024
MAX_ARCHIVE = MAX_TOTAL + 8 * 1024 * 1024
MAX_MANIFEST = 2 * 1024 * 1024
UUID = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
DIGEST = r'[0-9a-f]{64}'
STORE = r'data(?:/labs/(?:subnet-boundary|service-firewall)|/portable/attempts/' + DIGEST + r')?'
RECORD = re.compile('('+STORE+r')/(current(?:\.backup)?\.json|attempts/('+UUID+r')\.json)$')
WORKSPACE = re.compile('('+STORE+r')/workspace/('+UUID+r')\.json$')
PACK = re.compile(r'data/portable/packs/('+DIGEST+r')\.json$')
CONFIG = {'preferences.json', 'selection.json', 'workspace-layout.json', 'linux-workspace-layout.json', 'library-state.json'}


def file_limit(name):
    require(isinstance(name, str), 'Invalid backup path.')
    if RECORD.fullmatch(name): return MAX_RECORD
    if WORKSPACE.fullmatch(name): return 262144
    if PACK.fullmatch(name): return LIMIT
    if name == 'config/library-state.json': return 65536
    if name.startswith('config/') and name[7:] in CONFIG: return 4096
    raise ValidationError('Backup contains an unsupported path; only profile files are allowed.')


def bundled():
    from .__main__ import load_bundled_scenarios
    packs, _ = load_bundled_scenarios()
    return {p['lab_id']: p for p in packs}


def legacy_resources():
    root = Path(__file__).parent/'packs'
    return {name: hashlib.sha256((root/(name+'.json')).read_bytes()).hexdigest()
            for name in ('gateway-dns', 'subnet-boundary', 'service-firewall')}


def validate_contents(files):
    """Validate without constructing stores (constructors would create directories)."""
    scenarios = {}; versions = set()
    for name, raw in files.items():
        require(len(raw) <= file_limit(name), 'Profile file exceeds its size limit.')
        match = PACK.fullmatch(name)
        if match:
            scenario = load_portable(raw)
            require(match[1] == scenario.key[5:], 'Pack filename does not match content identity.')
            version = (scenario.identity.scenario_id, scenario.identity.content_version)
            require(version not in versions, 'Conflicting scenario ID/version in backup.')
            versions.add(version); scenarios[match[1]] = scenario
    require(len(scenarios) <= MAX_PACKS, 'Too many imported packs.')
    packs = bundled(); records = {}; ids = {}; modes = {'Learn': 0, 'Challenge': 0}
    for name, raw in files.items():
        match = RECORD.fullmatch(name)
        if not match: continue
        root, leaf, archived_id = match.groups()
        if '/portable/attempts/' in root:
            digest = root.rsplit('/', 1)[1]
            require(digest in scenarios, 'Pinned attempt is missing its exact scenario pack.')
            scenario = scenarios[digest]
            validator = object.__new__(PinnedStore)
            validator.scenario = scenario; validator.pack = scenario.legacy_pack()
            validator.version = 3 if scenario.pin['engine']['engine_id'] == 'networking' else 4
            attempt = validator.validate_record(raw)
        else:
            lab = 'gateway-dns' if root == 'data' else root.rsplit('/', 1)[1]
            attempt = validate_record(raw, packs[lab])
        require(archived_id is None or archived_id == attempt['id'], 'History filename/attempt identity mismatch.')
        require(attempt['id'] not in ids or ids[attempt['id']] == root, 'Attempt identity is reused across scenarios.')
        ids[attempt['id']] = root
        records.setdefault(root, {})[leaf] = attempt
        if leaf != 'current.backup.json': modes[attempt['mode']] += 1
    for root in ('data', 'data/labs/subnet-boundary', 'data/labs/service-firewall'):
        require(root in records, 'Backup is missing a bundled lab profile.')
    for root, group in records.items():
        require('current.json' in group, 'Profile is missing a current attempt; resolve recovery before backup.')
        require(group['current.json']['ended'] is None, 'Current attempt is already ended.')
    for name, raw in files.items():
        match = WORKSPACE.fullmatch(name)
        if match:
            root, attempt_id = match.groups()
            attempts = [a for a in records.get(root, {}).values() if a['id'] == attempt_id]
            require(bool(attempts), 'Workspace references a missing attempt.')
            state = validate_workspace(decode(raw))
            require(state['diagnostic_revision'] <= max(a['revision'] for a in attempts), 'Workspace diagnostics reference a future revision.')
    for name in CONFIG:
        if 'config/'+name not in files: continue
        value = decode(files['config/'+name], file_limit('config/'+name))
        require(isinstance(value, dict) and type(value.get('schema_version')) is int and value['schema_version'] == 1,
                'Unsupported profile settings version.')
        if name == 'library-state.json':
            from .library_state import validate as validate_library
            from .collections import linux_fundamentals
            builtin_keys = set(packs) | {e['scenario'].key for e in linux_fundamentals()}
            validate_library(value, builtin_keys, {'pack:'+digest for digest in scenarios})
        elif name == 'preferences.json':
            keys(value, {'schema_version', 'fallback_theme'}, 'preferences')
            require(type(value['fallback_theme']) is bool, 'Invalid theme preference.')
        elif name == 'selection.json':
            keys(value, {'schema_version', 'lab_id'}, 'selection')
            available = set(packs) | {'pack:'+digest for digest in scenarios}
            require(isinstance(value['lab_id'], str) and value['lab_id'] in available, 'Selected scenario is missing.')
        else:
            keys(value, {'schema_version', 'sizes'}, 'layout')
            sizes = value['sizes']
            require(isinstance(sizes, dict) and set(sizes) <= {'mission_width', 'mission_height', 'dock_height'}
                    and all(type(v) is int and 60 <= v <= 1800 for v in sizes.values()), 'Invalid workspace layout.')
    return {'files': len(files), 'profiles': len(records), 'packs': len(scenarios),
            'learn_records': modes['Learn'], 'challenge_records': modes['Challenge'],
            'lab_titles': [p['metadata']['title'] for p in packs.values()] +
                          [scenario.value()['metadata']['title'] for scenario in scenarios.values()],
            'history_records': sum(RECORD.fullmatch(name)[2].startswith('attempts/')
                                   for name in files if RECORD.fullmatch(name)),
            'bytes': sum(map(len, files.values()))}


def read_regular(path, limit):
    # O_NOFOLLOW/O_NONBLOCK reject symlinks/FIFOs without following or hanging.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_size <= limit, 'Expected a bounded regular profile file.')
        raw = stream.read(limit+1)
        require(len(raw) <= limit, 'File exceeds its size limit.')
        return raw, info.st_mtime_ns


def snapshot(data_root, config_root, locks):
    """GUI-thread call only, after flush, while both writer locks remain held.

    No event processing or callbacks occur during collection. Other app writers
    are excluded by QLockFile; timers/actions cannot run until the slot returns.
    """
    require(len(locks) == 2 and all(lock is not None and lock.isLocked() for lock in locks),
            'Backup requires the running app’s data and settings writer locks.')
    files = {}; times = {}
    def add(path, name):
        if not path.exists() and not path.is_symlink(): return
        raw, mtime = read_regular(path, file_limit(name))
        files[name] = raw; times[name] = mtime
        require(len(files) <= MAX_FILES and sum(map(len, files.values())) <= MAX_TOTAL, 'Profile exceeds backup limits.')
    def directory(path):
        require(not path.is_symlink() and path.is_dir(), 'Profile directory must not be a symlink.')
        return path
    def store(root, prefix):
        if not root.exists() and not root.is_symlink(): return
        directory(root)
        for name in ('current.json', 'current.backup.json'): add(root/name, prefix+'/'+name)
        for name in ('attempts', 'workspace'):
            folder = root/name
            if folder.exists() or folder.is_symlink():
                for path in directory(folder).iterdir():
                    if path.suffix == '.json': add(path, prefix+'/'+name+'/'+path.name)
    data_root, config_root = Path(data_root), Path(config_root)
    directory(data_root); directory(config_root)
    store(data_root, 'data')
    if (data_root/'labs').exists() or (data_root/'labs').is_symlink():
        directory(data_root/'labs')
        for name in ('subnet-boundary', 'service-firewall'): store(data_root/'labs'/name, 'data/labs/'+name)
    if (data_root/'portable').exists() or (data_root/'portable').is_symlink():
        directory(data_root/'portable')
        folder = data_root/'portable/packs'
        if folder.exists() or folder.is_symlink():
            for path in directory(folder).iterdir():
                if path.suffix == '.json': add(path, 'data/portable/packs/'+path.name)
        folder = data_root/'portable/attempts'
        if folder.exists() or folder.is_symlink():
            for path in directory(folder).iterdir(): store(path, 'data/portable/attempts/'+path.name)
    for name in CONFIG: add(config_root/name, 'config/'+name)
    validate_contents(files)
    manifest = {'format': FORMAT, 'schema_version': VERSION if 'config/library-state.json' in files else 1,
                'created_utc': datetime.now(timezone.utc).isoformat(),
                'legacy_resources': legacy_resources(),
                'files': {name: {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'mtime_ns': times[name]}
                          for name, raw in sorted(files.items())}}
    return Backup(manifest, files, validate_contents(files))


@dataclass
class Backup:
    manifest: dict
    files: dict
    summary: dict


def write_backup(backup, destination):
    destination = Path(destination)
    require(not destination.exists() and not destination.is_symlink(), 'Backup destination already exists; choose a new filename.')
    with tempfile.TemporaryDirectory(prefix='.learning-lab-backup-', dir=destination.parent) as temp:
        staged = Path(temp)/'backup.llbackup'
        with ZipFile(staged, 'w', compression=ZIP_STORED) as archive:
            archive.writestr('manifest.json', json.dumps(backup.manifest, sort_keys=True).encode())
            for name, raw in backup.files.items(): archive.writestr(name, raw)
        staged.chmod(0o600)
        read_backup(staged)  # Verify the exact artifact before publishing it.
        with staged.open('rb') as stream: os.fsync(stream.fileno())
        os.link(staged, destination)  # Atomic exclusive publication, never overwrite.


def read_backup(path):
    try:
        raw, _ = read_regular(path, MAX_ARCHIVE)
        from io import BytesIO
        with ZipFile(BytesIO(raw)) as archive:
            infos = archive.infolist()
            require(1 <= len(infos) <= MAX_FILES+1, 'Too many backup entries.')
            names = [info.filename for info in infos]
            require(len(set(names)) == len(names) and names.count('manifest.json') == 1, 'Duplicate or missing manifest/entry.')
            total = 0
            for info in infos:
                require(info.orig_filename == info.filename, 'Noncanonical archive path.')
                limit = MAX_MANIFEST if info.filename == 'manifest.json' else file_limit(info.filename)
                mode = info.external_attr >> 16
                require(not info.is_dir() and stat.S_IFMT(mode) in (0, stat.S_IFREG) and not mode & 0o7111, 'Archive entries must be regular files.')
                require(info.compress_type in (ZIP_STORED, ZIP_DEFLATED) and not info.flag_bits & 1, 'Unsupported archive compression or encryption.')
                require(0 <= info.file_size <= limit, 'Backup entry exceeds size limit.')
                total += info.file_size
            require(sum(info.file_size for info in infos if info.filename != 'manifest.json') <= MAX_TOTAL, 'Backup payload exceeds total size limit.')
            require(total <= MAX_TOTAL+MAX_MANIFEST, 'Backup exceeds total size limit.')
            manifest = decode(archive.read('manifest.json'), MAX_MANIFEST)
            keys(manifest, {'format', 'schema_version', 'created_utc', 'legacy_resources', 'files'}, 'backup manifest')
            require(manifest['format'] == FORMAT and type(manifest['schema_version']) is int and manifest['schema_version'] in (1, VERSION),
                    'Unsupported profile backup version; no migration will be performed.')
            require(isinstance(manifest['created_utc'], str) and len(manifest['created_utc']) <= 64
                    and datetime.fromisoformat(manifest['created_utc']).tzinfo is not None, 'Invalid backup timestamp.')
            require(manifest['legacy_resources'] == legacy_resources(), 'Bundled legacy scenarios differ; use the matching app version. No migration is available.')
            entries = manifest['files']
            require(isinstance(entries, dict) and set(entries) == set(names)-{'manifest.json'}, 'Manifest file inventory differs from archive.')
            require(('config/library-state.json' in entries) == (manifest['schema_version'] == 2),
                    'Library settings require backup version 2; version 1 remains unchanged.')
            files = {}
            for name, expected in entries.items():
                keys(expected, {'size', 'sha256', 'mtime_ns'}, 'file integrity record')
                require(type(expected['size']) is int and 0 <= expected['size'] <= file_limit(name), 'Invalid recorded size.')
                require(isinstance(expected['sha256'], str) and re.fullmatch(DIGEST, expected['sha256']), 'Invalid integrity hash.')
                require(type(expected['mtime_ns']) is int and 0 <= expected['mtime_ns'] < 2**63, 'Invalid file timestamp.')
                content = archive.read(name)
                require(len(content) == expected['size'] and hashlib.sha256(content).hexdigest() == expected['sha256'], 'Backup integrity check failed.')
                files[name] = content
            return Backup(manifest, files, validate_contents(files))
    except (BadZipFile, zlib.error, EOFError, UnicodeError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        raise ValidationError('Invalid or damaged profile backup.') from exc


def validate_destination(destination):
    destination = Path(destination)
    require(destination.is_absolute() and destination.name not in ('', '.', '..'), 'Choose an absolute new profile directory.')
    require(destination.parent.is_dir(), 'Choose an existing parent directory.')
    require(not destination.exists() and not destination.is_symlink(), 'Destination already exists. Restore requires a new directory; no files will be replaced or merged.')
    return destination


def restore(backup, destination, *, confirmed=False):
    require(confirmed is True, 'Explicit restore confirmation is required.')
    destination = validate_destination(destination)
    validate_contents(backup.files)
    # Linux renameat2 prevents replacing even an empty directory created during
    # validation. If unavailable, fail closed rather than using replacing rename.
    libc = ctypes.CDLL(None, use_errno=True)
    rename = getattr(libc, 'renameat2', None)
    require(rename is not None, 'Atomic no-replace restore is unavailable on this platform.')
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    with tempfile.TemporaryDirectory(prefix='.learning-lab-restore-', dir=destination.parent) as temp:
        staged = Path(temp)/'profile'; staged.mkdir(mode=0o700)
        for folder in ('data', 'config'): (staged/folder).mkdir(mode=0o700)
        for name, raw in backup.files.items():
            path = staged/name; path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with path.open('xb') as stream:
                os.fchmod(stream.fileno(), 0o600); stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            mtime = backup.manifest['files'][name]['mtime_ns']; os.utime(path, ns=(mtime, mtime))
        # Persist the complete directory tree before making its name visible.
        for folder in [p for p in staged.rglob('*') if p.is_dir()] + [staged]:
            fd = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
            try: os.fsync(fd)
            finally: os.close(fd)
        if rename(-100, os.fsencode(staged), -100, os.fsencode(destination), 1):
            error = ctypes.get_errno(); raise OSError(error, 'Restore could not publish the new profile; destination was not replaced.')
    return destination
