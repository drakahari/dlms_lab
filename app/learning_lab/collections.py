"""Trusted Library curation; scenario bytes still pass the portable validator."""
from importlib.resources import files
from .portable import load_portable
from .domain.validation import decode, keys, text, require


def resource_name(name):
    require(isinstance(name, str) and '/' not in name and '\\' not in name
            and name.endswith('.json') and '..' not in name, 'Invalid collection resource.')
    return name


def load_collection(name):
    root = files('learning_lab').joinpath('collections')
    manifest = decode(root.joinpath(resource_name(name)).read_bytes(), 65536)
    keys(manifest, {'title', 'items'}, 'collection')
    text(manifest['title'], 'collection title', 120)
    require(isinstance(manifest['items'], list) and 1 <= len(manifest['items']) <= 32,
            'Expected 1–32 curated labs.')
    entries = []
    for item in manifest['items']:
        keys(item, {'file', 'skill'}, 'collection item')
        name = item['file']
        resource_name(name)
        require(name.endswith('.lab.json'), 'Expected scenario resource.')
        text(item['skill'], 'skill', 240)
        scenario = load_portable(root.joinpath('packs', name).read_bytes())
        require(scenario.key not in {e['scenario'].key for e in entries}, 'Duplicate collection lab.')
        entries.append({'scenario': scenario, 'skill': item['skill']})
    return {'title': manifest['title'], 'entries': entries}


def load_collections():
    root = files('learning_lab').joinpath('collections')
    index = decode(root.joinpath('index.json').read_bytes(), 65536)
    keys(index, {'collections'}, 'collection index')
    require(isinstance(index['collections'], list) and 1 <= len(index['collections']) <= 8,
            'Expected 1–8 collections.')
    result = []; ids = set(); identities = {}
    import re
    for descriptor in index['collections']:
        keys(descriptor, {'id', 'file', 'purpose', 'sequence', 'prerequisites', 'coverage'}, 'collection description')
        identity = descriptor['id']
        require(isinstance(identity, str) and re.fullmatch('[a-z][a-z0-9-]{0,63}', identity)
                and identity not in ids, 'Invalid or duplicate collection ID.')
        ids.add(identity)
        for field in ('purpose', 'sequence', 'prerequisites', 'coverage'):
            text(descriptor[field], field, 1024)
        collection = {**descriptor, **load_collection(descriptor['file'])}
        for entry in collection['entries']:
            s = entry['scenario']; version = (s.identity.scenario_id, s.identity.content_version)
            require(version not in identities or identities[version] == s.key, 'Conflicting bundled scenario version.')
            identities[version] = s.key
        result.append(collection)
    return result


def linux_fundamentals():
    """Compatibility accessor for the original, unchanged six entries."""
    return load_collection('linux-fundamentals.json')['entries']
