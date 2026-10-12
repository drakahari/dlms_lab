"""Exact authorized projections for the two foundation families only."""
import json
from platform_preservation import projection as platform_projection

NEW_UNITS={'lpic-text-archive-tools','lpic-accounts-logging-recovery'}
NEW_IDS={'real-linux-textarchive-'+s for s in ('streams','tee','xargs','join','find','cpio','composition','handover')}
NEW_IDS|={'real-linux-operations-'+s for s in ('accountfiles','cronaccess','timerresult','journalcursor','journalfields','rotationfd','notices','handover')}

def projection(name,raw):
    raw=platform_projection(name,raw)
    if name.endswith('registry.py'):
        for new in (94,102):raw=raw.replace(('MAX_TOTAL_LESSONS = '+str(new)).encode(),b'MAX_TOTAL_LESSONS = 86').replace(('at most '+str(new)+' total').encode(),b'at most 86 total')
        for new in (11,12):raw=raw.replace(('MAX_UNITS = '+str(new)).encode(),b'MAX_UNITS = 10').replace(('1–'+str(new)+' bundled').encode(),'1–10 bundled'.encode())
    elif name.endswith('image_catalog.py'):
        for new in (94,102):
            for key in ('MAX_RETAINED_LESSONS','MAX_DEFAULT_LESSONS'):raw=raw.replace((key+' = '+str(new)).encode(),(key+' = 86').encode())
    elif name.endswith('Main.qml'):
        for words in ('eleven units / 94 lessons','twelve units / 102 lessons'):raw=raw.replace(words.encode(),b'ten units / 86 lessons')
    elif name.endswith(('image-catalog.json','units.json')):
        data=json.loads(raw)
        if name.endswith('units.json'):data['units']=[u for u in data['units'] if u['id'] not in NEW_UNITS]
        else:
            data['lessons']=[l for l in data['lessons'] if l['id'] not in NEW_IDS]
            for image in data['images']:image['lessons']=[l for l in image['lessons'] if l['id'] not in NEW_IDS]
            for key in ('default_lessons','default_images'):data[key]={k:v for k,v in data[key].items() if k not in NEW_IDS}
        raw=json.dumps(data,sort_keys=True,separators=(',',':')).encode()
    return raw
