"""Bounded bundled lesson content only. Never an import or execution endpoint."""
import copy
from functools import lru_cache
import hashlib
import json
import re
from pathlib import Path
from .files import require

LEGACY_ID = 'real-linux-background-job'
ROOT = Path(__file__).parent
MAX_UNITS = 4
MAX_LESSONS_PER_UNIT = 16
MAX_TOTAL_LESSONS = 36
LEGACY_UNIT = 'lpic-processes-jobs-priorities'

def _read(name):
    require(isinstance(name, str) and re.fullmatch(r'[a-z0-9-]+\.json', name) is not None, 'Invalid bundled resource name')
    with (ROOT / name).open('rb') as stream: raw = stream.read(65537)
    require(len(raw) <= 65536, 'Bundled VM content exceeds limit')
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate bundled field: '+key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)

def _text(value, label, limit=4096):
    require(isinstance(value, str) and 0 < len(value) <= limit and '\x00' not in value,
            'Invalid bundled '+label)

def _texts(value, label, minimum=1, maximum=16):
    require(isinstance(value, list) and minimum <= len(value) <= maximum, 'Invalid '+label+' count')
    for text in value: _text(text, label)

def validate_lesson(content,lesson_id):
    require(set(content) == {'id', 'content_version', 'title', 'goal', 'challenge', 'steps', 'hints', 'review', 'coverage'},
            'Unsupported lesson fields; no executable actions permitted')
    require(content['id'] == lesson_id, 'Bundled lesson identity differs')
    require(isinstance(content['content_version'],str) and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', content['content_version']),
            'Invalid lesson content version')
    for key in ('title', 'goal', 'challenge', 'coverage'): _text(content[key], key)
    require(isinstance(content['steps'], list) and 1 <= len(content['steps']) <= 32, 'Invalid step count')
    for step in content['steps']:
        require(set(step) == {'command', 'explanation', 'expected'}, 'Unsupported step fields')
        for key in step: _text(step[key], key)
    _texts(content['hints'], 'hints', 0); _texts(content['review'], 'review')

@lru_cache(maxsize=1)
def _bundle():
    index = _read('units.json')
    require(isinstance(index, dict) and set(index) == {'schema_version', 'units'} and
            type(index['schema_version']) is int and index['schema_version'] == 1,
            'Unsupported bundled VM unit index')
    require(isinstance(index['units'], list) and 1 <= len(index['units']) <= MAX_UNITS,
            'Expected 1–4 bundled VM units')
    units = []; lessons = {}; seen = set(); unit_ids = set(); resources = set()
    for item in index['units']:
        require(isinstance(item, dict) and set(item) == {'id', 'resource'} and
                isinstance(item['id'], str) and re.fullmatch(r'[a-z0-9-]{1,80}', item['id']) and
                isinstance(item['resource'], str) and re.fullmatch(r'[a-z0-9-]+\.json', item['resource']),
                'Invalid bundled VM unit identity')
        require(item['id'] not in unit_ids and item['resource'] not in resources,
                'Duplicate bundled VM unit identity/resource')
        unit_ids.add(item['id']); resources.add(item['resource'])
        value = _read(item['resource'])
        require(isinstance(value, dict) and value.get('id') == item['id'], 'Bundled VM unit identity differs')
        _validate_unit(value, seen, lessons)
        units.append(value)
    require(len(lessons) <= MAX_TOTAL_LESSONS, 'Expected at most 36 total bundled VM lessons')
    require(LEGACY_UNIT in unit_ids and LEGACY_ID in seen, 'Accepted unit/lesson missing')
    return units, lessons

def _validate_unit(value, seen, lessons):
    require(set(value) == {'schema_version', 'id', 'title', 'purpose', 'prerequisites', 'coverage', 'entries'},
            'Unsupported bundled unit fields')
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'Unsupported VM unit version')
    for key in ('id', 'title', 'purpose', 'prerequisites', 'coverage'): _text(value[key], key)
    require(isinstance(value['entries'], list) and 1 <= len(value['entries']) <= MAX_LESSONS_PER_UNIT, 'Expected 1–16 bundled unit entries')
    require(len(seen) + len(value['entries']) <= MAX_TOTAL_LESSONS, 'Expected at most 36 total bundled VM lessons')
    for entry in value['entries']:
        base = {'id', 'resource', 'description', 'objectives', 'troubleshooting', 'cleanup'}
        require(isinstance(entry, dict) and set(entry) in (base, base | {'observations', 'questions', 'limitations', 'materials'}),
                'Unsupported bundled entry fields')
        require(isinstance(entry['id'], str) and re.fullmatch(r'[a-z0-9-]{1,80}', entry['id']) is not None,
                'Invalid bundled lesson identity')
        require(entry['id'] not in seen, 'Duplicate bundled lesson identity'); seen.add(entry['id'])
        _text(entry['description'], 'description')
        _texts(entry['objectives'], 'objectives'); _texts(entry['troubleshooting'], 'troubleshooting')
        _texts(entry['cleanup'], 'cleanup')
        for key in ('observations', 'questions', 'limitations', 'materials'):
            if key in entry: _texts(entry[key], key)
        content = _read(entry['resource'])
        validate_lesson(content,entry['id'])
        lessons[entry['id']] = content

def units():
    return copy.deepcopy(_bundle()[0])

def catalog(unit_id=LEGACY_UNIT):
    for value in units():
        if value['id'] == unit_id: return value
    raise ValueError('Unknown bundled VM unit')

def entries():
    return [item for value in units() for item in value['entries']]

def unit_for_lesson(lesson_id):
    for value in units():
        if any(item['id'] == lesson_id for item in value['entries']): return value
    raise ValueError('Unknown bundled VM lesson')

def entry(lesson_id):
    require(isinstance(lesson_id, str), 'Choose a bundled VM lesson')
    for item in entries():
        if item['id'] == lesson_id: return item
    raise ValueError('Unknown bundled VM lesson; imported VM lessons are unsupported')

def load_lesson(lesson_id=LEGACY_ID):
    entry(lesson_id)
    return copy.deepcopy(_bundle()[1][lesson_id])

def session_binding(profile, lesson_id):
    entry(lesson_id)
    require(isinstance(profile,str) and re.fullmatch(r'[0-9a-f]{64}',profile), 'Invalid application profile binding')
    # Accepted v1 location and all canonical pins remain byte-for-byte unchanged.
    if lesson_id == LEGACY_ID: return profile
    return hashlib.sha256(('vm-lesson-session-v1\0'+profile+'\0'+lesson_id).encode()).hexdigest()
