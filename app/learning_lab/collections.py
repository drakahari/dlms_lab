"""Trusted Library curation; scenario bytes still pass the portable validator."""
from importlib.resources import files
from .portable import load_portable
from .domain.validation import decode, keys, text, require


def linux_fundamentals():
    root = files('learning_lab').joinpath('collections')
    manifest = decode(root.joinpath('linux-fundamentals.json').read_bytes())
    keys(manifest, {'title', 'items'}, 'collection')
    require(manifest['title'] == 'Linux Fundamentals', 'Unknown collection.')
    require(isinstance(manifest['items'], list) and len(manifest['items']) == 6,
            'Expected six curated labs.')
    entries = []
    for item in manifest['items']:
        keys(item, {'file', 'skill'}, 'collection item')
        name = item['file']
        require(isinstance(name, str) and '/' not in name and '\\' not in name
                and name.endswith('.lab.json') and '..' not in name, 'Invalid collection resource.')
        text(item['skill'], 'skill', 240)
        scenario = load_portable(root.joinpath('packs', name).read_bytes())
        require(scenario.key not in {e['scenario'].key for e in entries}, 'Duplicate collection lab.')
        entries.append({'scenario': scenario, 'skill': item['skill']})
    return entries
