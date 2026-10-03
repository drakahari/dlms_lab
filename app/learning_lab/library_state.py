"""Reversible Library presentation choices, independent of attempts and engines."""
import json
from pathlib import Path
from .domain.validation import decode, keys, require
from .storage import atomic_write

LIMIT = 65536
MAX_ENTRIES = 512


def validate(value, builtins, imported):
    keys(value, {'schema_version', 'entries'}, 'Library settings')
    require(type(value['schema_version']) is int and value['schema_version'] == 1,
            'Unsupported Library settings version; original preserved.')
    entries = value['entries']
    require(isinstance(entries, dict) and len(entries) <= MAX_ENTRIES, 'Too many Library choices.')
    for key, state in entries.items():
        require(isinstance(key, str) and len(key) <= 80, 'Invalid Library identity.')
        if key in builtins:
            # A previously removed import may now be bundled. Preserve its exact
            # stored choice without rewriting settings or reactivating the lab.
            require(state == 'hidden' or (state == 'removed' and key in imported),
                    'Removed bundled entry needs its exact previously installed pack.')
        else:
            require(key in imported and state == 'removed', 'Removed Library entry needs its exact installed pack.')
    return dict(entries)


class LibraryState:
    def __init__(self, path, builtins, imported):
        self.path = Path(path)
        self.builtins, self.imported = set(builtins), set(imported)
        self.entries = {}; self.read_only = False; self.notice = ''
        try:
            if self.path.exists() or self.path.is_symlink():
                require(self.path.is_file() and not self.path.is_symlink(), 'Library settings must be a regular file.')
                with self.path.open('rb') as stream: raw = stream.read(LIMIT+1)
                self.entries = validate(decode(raw, LIMIT), self.builtins, self.imported)
        except (OSError, ValueError) as exc:
            self.read_only = True
            self.notice = 'Library settings need recovery; choices are read-only and original files are preserved. '+str(exc)

    def save(self, entries):
        require(not self.read_only, 'Library settings are read-only; resolve recovery first.')
        value = {'schema_version': 1, 'entries': entries}
        validated = validate(value, self.builtins, self.imported)
        raw = json.dumps(value, sort_keys=True, indent=2).encode()
        require(len(raw) <= LIMIT, 'Library choices exceed size limit.')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(self.path, raw)
        self.entries = validated  # Failed writes never change the displayed choice.

    def state(self, key): return self.entries.get(key, 'active')
