"""Application-owned exact image/lesson revisions. Bundles cannot extend trust."""
import copy
import hashlib
import json
import re
from pathlib import Path
from .files import require
from .policy import BACKEND, VIRTUAL_BYTES
from . import registry

STATES = {'active', 'resume-only', 'withdrawn'}
HEX = re.compile(r'[0-9a-f]{64}')
ROOT = Path(__file__).parent
MAX_RETAINED_LESSONS = 86
MAX_DEFAULT_LESSONS = 86


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(raw, limit=65536):
    require(len(raw) <= limit, 'JSON exceeds size limit')
    def pairs(items):
        result = {}
        for k, v in items:
            require(k not in result, 'Duplicate JSON field: '+k)
            result[k] = v
        return result
    def invalid(value):
        raise ValueError('Non-integer JSON number is unsupported')
    try:
        value=json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                         parse_float=invalid, parse_constant=invalid)
        pending=[(value,0)];nodes=0
        while pending:
            current,depth=pending.pop();nodes+=1
            require(depth<=32 and nodes<=8192,'JSON nesting/count exceeds limit')
            if isinstance(current,dict):pending.extend((v,depth+1) for v in current.values())
            elif isinstance(current,list):pending.extend((v,depth+1) for v in current)
        return value
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('Invalid or excessively nested JSON') from exc


def resource(name):
    require(isinstance(name, str) and re.fullmatch(r'[a-z0-9-]+\.(json|gpg)', name), 'Invalid trusted resource name')
    with (ROOT/name).open('rb') as stream:
        return stream.read(65537)


class Catalog:
    """Internal dependency injection supports isolated tests, never CLI/profile input."""
    def __init__(self, data, read_resource=resource):
        self._data = copy.deepcopy(data)
        self._read = read_resource
        fields={'schema_version','images','lessons','default_image','default_lessons','releases','keys'}
        require(set(data) in (fields,fields|{'default_images'}) and
                type(data['schema_version']) is int and data['schema_version'] == 1, 'Unsupported image catalog')
        self.images = {}; self.lessons = {}; self.releases = {}; self.keys = {}
        for field in ('images','lessons','releases','keys'):
            require(isinstance(data[field],list) and len(data[field]) <= (MAX_RETAINED_LESSONS if field == 'lessons' else 64), 'Catalog count exceeds limit')
        for item in data['images']:
            require(set(item)=={'descriptor','state','legacy','lessons'} and item['state'] in STATES and type(item['legacy']) is bool,
                    'Invalid catalog image')
            spec=item['descriptor']
            require(isinstance(spec,dict) and HEX.fullmatch(spec.get('sha256','')) and type(spec.get('bytes')) is int and
                    0 < spec['bytes'] <= VIRTUAL_BYTES and spec.get('format')=='raw', 'Invalid image descriptor')
            require(isinstance(item['lessons'],list) and 0<len(item['lessons'])<=64,'Invalid image lesson compatibility')
            pairs=[]
            for pair in item['lessons']:
                require(isinstance(pair,dict) and set(pair)=={'id','sha256'} and isinstance(pair['id'],str) and isinstance(pair['sha256'],str) and HEX.fullmatch(pair['sha256']),'Invalid compatible lesson revision')
                pairs.append((pair['id'],pair['sha256']))
            require(len(set(pairs))==len(pairs),'Duplicate image lesson compatibility')
            key=digest(spec); require(key not in self.images,'Duplicate image descriptor')
            self.images[key]=copy.deepcopy(item)
        for item in data['lessons']:
            require(set(item)=={'id','sha256','resource','state'} and item['state'] in STATES and
                    isinstance(item['id'],str) and re.fullmatch(r'[a-z0-9-]{1,80}',item['id']) and
                    isinstance(item['sha256'],str) and HEX.fullmatch(item['sha256']), 'Invalid retained lesson')
            key=(item['id'],item['sha256']);require(key not in self.lessons,'Duplicate lesson revision')
            require(isinstance(item['resource'],str) and re.fullmatch(r'[a-z0-9-]+\.json',item['resource']),'Invalid retained lesson resource')
            self.lessons[key]=(copy.deepcopy(item),None)
        require(data['default_image'] in self.images,'Missing default image')
        require(isinstance(data['default_lessons'],dict) and data['default_lessons'] and
                len(data['default_lessons']) <= MAX_DEFAULT_LESSONS and
                all((k,v) in self.lessons for k,v in data['default_lessons'].items()),'Missing default lesson')
        # Old trusted catalogs retain their one-image behavior. An explicit map
        # must cover EVERY default; missing entries never fall back to a different
        # image (especially one with guest-root privileges). Saved pins bypass
        # defaults and still resolve exact retained descriptors and lesson bytes.
        self.default_images=copy.deepcopy(data.get('default_images'))
        if 'default_images' in data:
            require(isinstance(self.default_images,dict) and
                    set(self.default_images)==set(data['default_lessons']) and
                    len(self.default_images)<=MAX_DEFAULT_LESSONS,'Incomplete per-lesson image defaults')
            for lesson_id,image_id in self.default_images.items():
                require(isinstance(image_id,str) and image_id in self.images,
                        'Unavailable per-lesson image descriptor')
                require({'id':lesson_id,'sha256':data['default_lessons'][lesson_id]} in self.images[image_id]['lessons'],
                        'Default image/lesson pair unsupported')
        for item in data['keys']:
            require(set(item)=={'fingerprint','resource'} and re.fullmatch(r'[0-9A-F]{40}',item['fingerprint']), 'Invalid signer')
            require(item['fingerprint'] not in self.keys,'Duplicate signer')
            raw=self._read(item['resource']);require(0<len(raw)<=65536,'Keyring exceeds limit')
            self.keys[item['fingerprint']]=raw
        for item in data['releases']:
            require(set(item)=={'manifest_sha256','descriptor_sha256','signer','state'} and item['state'] in STATES and
                    HEX.fullmatch(item['manifest_sha256']) and item['descriptor_sha256'] in self.images and
                    item['signer'] in self.keys, 'Invalid authorized release')
            require(item['state']==self.images[item['descriptor_sha256']]['state'],'Release/image availability differs')
            require(item['manifest_sha256'] not in self.releases,'Duplicate release manifest')
            self.releases[item['manifest_sha256']]=copy.deepcopy(item)

    def defaults(self, lesson_id):
        require(lesson_id in self._data['default_lessons'],'Unavailable lesson default')
        image_id=self.default_images[lesson_id] if self.default_images is not None else self._data['default_image']
        require(image_id in self.images,'Unavailable exact default image; no substitute selected')
        image=self.images[image_id]
        spec=image['descriptor']
        require({'id':lesson_id,'sha256':self._data['default_lessons'][lesson_id]} in image['lessons'],'Default image/lesson pair unsupported')
        lesson=self._lesson((lesson_id,self._data['default_lessons'][lesson_id]))[1]
        return copy.deepcopy(spec),copy.deepcopy(lesson)

    def _lesson(self,key):
        item,value=self.lessons[key]
        try:
            value=read_json(self._read(item['resource']))
        except OSError as exc:
            raise ValueError('Pinned lesson resource unavailable; records preserved and verified Stop remains available') from exc
        require(isinstance(value,dict) and value.get('id')==item['id'] and digest(value)==item['sha256'],'Retained lesson digest differs')
        registry.validate_lesson(value,item['id'])
        return copy.deepcopy(item),value

    def resolve(self, pin, lesson_id):
        require(isinstance(pin,dict) and set(pin)=={'backend','image','lesson_sha256'} and pin['backend']==BACKEND,
                'Session requires an unavailable backend; preserved without migration')
        image=self.images.get(digest(pin['image']))
        lesson=self.lessons.get((lesson_id,pin['lesson_sha256']))
        require(image is not None and image['descriptor']==pin['image'],'Pinned image descriptor unavailable; session preserved')
        require(lesson is not None,'Pinned lesson revision unavailable; session preserved')
        require({'id':lesson_id,'sha256':pin['lesson_sha256']} in image['lessons'],'Pinned image/lesson combination unavailable; session preserved')
        return copy.deepcopy(image),self._lesson((lesson_id,pin['lesson_sha256']))

    def allow(self,pin,lesson_id,operation):
        image,lesson=self.resolve(pin,lesson_id)
        states=(image['state'],lesson[0]['state'])
        require('withdrawn' not in states,'Pinned image or lesson is withdrawn; boot and Reset are blocked. Records retained; Stop remains available.')
        require(operation=='resume' or all(s=='active' for s in states),
                'Pinned release is resume-only: existing sessions may Resume; new sessions and Reset are blocked. No image substituted.')


def production_catalog():
    data=read_json(resource('image-catalog.json'))
    catalog=Catalog(data)
    require(all(i['descriptor']['bytes']==VIRTUAL_BYTES for i in catalog.images.values()),'Unsupported production image size')
    return catalog
