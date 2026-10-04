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

def _read(name):
    require(re.fullmatch(r'[a-z0-9-]+\.json', name) is not None, 'Invalid bundled resource name')
    raw = (ROOT / name).read_bytes()
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
    value = _read('unit.json')
    require(set(value) == {'schema_version', 'id', 'title', 'purpose', 'prerequisites', 'coverage', 'entries'},
            'Unsupported bundled unit fields')
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'Unsupported VM unit version')
    for key in ('id', 'title', 'purpose', 'prerequisites', 'coverage'): _text(value[key], key)
    require(isinstance(value['entries'], list) and 1 <= len(value['entries']) <= 16, 'Expected 1–16 bundled unit entries')
    seen = set(); lessons = {}
    for entry in value['entries']:
        require(set(entry) == {'id', 'resource', 'description', 'objectives', 'troubleshooting', 'cleanup'},
                'Unsupported bundled entry fields')
        require(isinstance(entry['id'], str) and re.fullmatch(r'[a-z0-9-]{1,80}', entry['id']) is not None,
                'Invalid bundled lesson identity')
        require(entry['id'] not in seen, 'Duplicate bundled lesson identity'); seen.add(entry['id'])
        _text(entry['description'], 'description')
        _texts(entry['objectives'], 'objectives'); _texts(entry['troubleshooting'], 'troubleshooting')
        _texts(entry['cleanup'], 'cleanup')
        content = _read(entry['resource'])
        validate_lesson(content,entry['id'])
        lessons[entry['id']] = content
    require(LEGACY_ID in seen, 'Accepted lesson missing from unit')
    return value, lessons

def catalog():
    return copy.deepcopy(_bundle()[0])

def entry(lesson_id):
    require(isinstance(lesson_id, str), 'Choose a bundled VM lesson')
    for item in catalog()['entries']:
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
