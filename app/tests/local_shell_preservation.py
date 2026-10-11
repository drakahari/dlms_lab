"""Project only this authorized unit out of historical preservation fixtures.
Other application bytes and every old lesson/descriptor/default remain exact.
"""
import json

def projection(name, raw):
    if name.endswith('image_catalog.py'):
        return raw.replace(b'MAX_RETAINED_LESSONS = 86', b'MAX_RETAINED_LESSONS = 76').replace(b'MAX_DEFAULT_LESSONS = 86', b'MAX_DEFAULT_LESSONS = 76')
    if name.endswith('registry.py'):
        return raw.replace(b'MAX_UNITS = 10', b'MAX_UNITS = 9').replace(b'MAX_TOTAL_LESSONS = 86', b'MAX_TOTAL_LESSONS = 76').replace('1–10 bundled'.encode(), '1–9 bundled'.encode()).replace(b'at most 86 total', b'at most 76 total')
    if name.endswith(('image-catalog.json','units.json')):
        data=json.loads(raw)
        if name.endswith('units.json'):
            data['units']=[u for u in data['units'] if u['id']!='lpic-local-shell-filesystem']
        else:
            new={l['id'] for l in data['lessons'] if l['id'].startswith('real-linux-local-')}
            data['lessons']=[l for l in data['lessons'] if l['id'] not in new]
            for image in data['images']:
                image['lessons']=[l for l in image['lessons'] if l['id'] not in new]
            for field in ('default_images','default_lessons'):
                data[field]={k:v for k,v in data[field].items() if k not in new}
        return json.dumps(data,sort_keys=True,separators=(',',':')).encode()
    return raw
