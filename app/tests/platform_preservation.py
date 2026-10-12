"""Remove only this approved platform delta for historical baseline comparisons."""
import json
from pathlib import Path

BASE = json.loads(Path(__file__).with_name('platform_baseline.json').read_text())
NEW_IDS = set(BASE['new_ids'])
NEW_UNITS = set(BASE['new_units'])
NEW_IMAGES = set(BASE['new_images'])


def projection(name, raw):
    if name.endswith('registry.py'):
        return raw.replace(b'MAX_UNITS = 14', b'MAX_UNITS = 12').replace(
            b'MAX_TOTAL_LESSONS = 120', b'MAX_TOTAL_LESSONS = 102').replace(
            '1–14 bundled'.encode(), '1–12 bundled'.encode()).replace(
            b'at most 120 total', b'at most 102 total')
    if name.endswith('image_catalog.py'):
        return raw.replace(b'MAX_RETAINED_LESSONS = 120', b'MAX_RETAINED_LESSONS = 102').replace(
            b'MAX_DEFAULT_LESSONS = 120', b'MAX_DEFAULT_LESSONS = 102')
    if name.endswith('Main.qml'):
        return raw.replace(b'fourteen units / 120 lessons', b'twelve units / 102 lessons')
    if name.endswith(('units.json', 'image-catalog.json')):
        value = json.loads(raw)
        if name.endswith('units.json'):
            value['units'] = [u for u in value['units'] if u['id'] not in NEW_UNITS]
        else:
            value['images'] = [i for i in value['images']
                               if i['descriptor']['image_id'] not in NEW_IMAGES]
            value['lessons'] = [l for l in value['lessons'] if l['id'] not in NEW_IDS]
            for field in ('default_lessons', 'default_images'):
                value[field] = {k: v for k, v in value[field].items() if k not in NEW_IDS}
        return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return raw
