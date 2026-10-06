"""Ephemeral TEST ONLY trust. Not a package resource or executable production switch."""
import copy,gzip,hashlib,io,json,os,subprocess,tempfile,zipfile
from pathlib import Path
from learning_lab.vm_preview.image_catalog import Catalog,canonical,digest,resource
from learning_lab.vm_preview.policy import BACKEND


def hash_(raw):return hashlib.sha256(raw).hexdigest()

class SigningFixture:
    def __init__(self):
        self.temp=tempfile.TemporaryDirectory(prefix='oll-TEST-TRUST-');self.root=Path(self.temp.name)
        self.env={'PATH':'/usr/bin','LC_ALL':'C','GNUPGHOME':str(self.root)}
        subprocess.run(['/usr/bin/gpg','--batch','--pinentry-mode','loopback','--passphrase','','--quick-generate-key',
                        'Learning Lab TEST ONLY <fixture@example.invalid>','ed25519','sign','0'],env=self.env,check=True,capture_output=True)
        keys=subprocess.check_output(['/usr/bin/gpg','--batch','--with-colons','--list-keys'],env=self.env,stderr=subprocess.DEVNULL).decode()
        self.fingerprint=next(line.split(':')[9] for line in keys.splitlines() if line.startswith('fpr:'))
        self.public=subprocess.check_output(['/usr/bin/gpg','--batch','--export',self.fingerprint],env=self.env)
    def sign(self,raw):
        return subprocess.check_output(['/usr/bin/gpg','--batch','--pinentry-mode','loopback','--passphrase','','--detach-sign','--output','-'],input=raw,env=self.env,stderr=subprocess.DEVNULL)
    def close(self):
        subprocess.run(['/usr/bin/gpgconf','--homedir',str(self.root),'--kill','all'],env=self.env,capture_output=True)
        self.temp.cleanup()
    def bundle(self,path,*,raw=b'SYNTHETIC NOT BOOTABLE\n'*128,compressed=None,manifest_edit=None,state='active',descriptor=None):
        data=json.loads(resource('image-catalog.json'));spec=copy.deepcopy(data['images'][0]['descriptor'])
        spec.update(image_id='synthetic-test-only',bytes=len(raw),sha256=hash_(raw))
        if descriptor:spec.update(descriptor)
        members={'image.raw.gz':gzip.compress(raw,mtime=0) if compressed is None else compressed,
                 'packages.json':b'[]\n','provenance.json':b'{"purpose":"TEST ONLY"}\n','notices.txt':b'Synthetic fixture; never a guest image.\n'}
        manifest={'schema_version':1,'release_id':'synthetic-test-only-1','descriptor':spec,'backend':BACKEND,
                  'lessons':copy.deepcopy(data['images'][0]['lessons']),
                  'members':{k:{'bytes':len(v),'sha256':hash_(v)} for k,v in members.items()}}
        if manifest_edit:manifest_edit(manifest)
        encoded=canonical(manifest)+b'\n';signature=self.sign(encoded)
        data['images'].append({'descriptor':spec,'state':state,'legacy':False,'lessons':copy.deepcopy(data['images'][0]['lessons'])})
        data['keys']=[{'fingerprint':self.fingerprint,'resource':'fixture.gpg'}]
        data['releases']=[{'manifest_sha256':hash_(encoded),'descriptor_sha256':digest(spec),'signer':self.fingerprint,'state':state}]
        catalog=Catalog(data,lambda name:self.public if name=='fixture.gpg' else resource(name))
        members={'manifest.json':encoded,'manifest.sig':signature,**members}
        self.write(path,members)
        return catalog,manifest,members
    @staticmethod
    def write(path,members,*,compression=zipfile.ZIP_STORED,zip64=False):
        with zipfile.ZipFile(path,'w',compression=compression,allowZip64=True) as z:
            for name,raw in members.items():
                info=zipfile.ZipInfo(name);info.external_attr=(0o100600)<<16;info.compress_type=compression
                if zip64:
                    with z.open(info,'w',force_zip64=True) as stream:stream.write(raw)
                else:z.writestr(info,raw)

# Test-only streaming builder. No runtime import depends on this module.
STREAM_CHUNK = 1024**2
STREAM_GZIP_LIMIT = 8*1024**3


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


class LimitedWriter:
    def __init__(self, stream, limit):
        self.stream, self.limit, self.count = stream, limit, 0
    def write(self, data):
        if self.count + len(data) > self.limit:
            raise ValueError('Test gzip exceeds the bundle compressed-size limit')
        result = self.stream.write(data)
        self.count += result
        return result
    def flush(self): self.stream.flush()


def stream_bundle(signer, path, source, descriptor, *, metadata=None, progress=None):
    """Build from a read-only file in bounded chunks; retain exact descriptor pins.

    Outputs use exclusive creation. Failures retain their partial test artifacts.
    The returned catalog is in-memory TEST trust, never production configuration.
    """
    from learning_lab.vm_preview.image_bundle import source_file, file_identity
    from learning_lab.vm_preview.bundle_archive import LIMITS
    path, source = Path(path), Path(source)
    compressed = path.with_suffix('.raw.gz')
    if path.exists() or compressed.exists():
        raise FileExistsError('Test output already exists; preserved')
    spec = copy.deepcopy(descriptor)
    members = metadata or {'packages.json': b'[]\n',
        'provenance.json': b'{"purpose":"isolated TEST ONLY"}\n',
        'notices.txt': b'Local test artifact. Not a distribution release.\n'}
    if set(members) != {'packages.json','provenance.json','notices.txt'}:
        raise ValueError('Expected exactly the three bounded metadata members')
    for name, raw in members.items():
        if not isinstance(raw, bytes) or len(raw) > LIMITS[name]:
            raise ValueError('Test metadata exceeds member limit')
    raw_hash = hashlib.sha256(); count = 0
    with source_file(source) as fd:
        initial = file_identity(fd)
        if initial[2] != spec['bytes'] or initial[5] & 0o222:
            raise ValueError('Test source must have the exact size and be read-only')
        with compressed.open('xb') as target:
            os.chmod(compressed, 0o600)
            bounded = LimitedWriter(target, STREAM_GZIP_LIMIT)
            with gzip.GzipFile(filename='', fileobj=bounded, mode='wb', mtime=0) as gz:
                while block := os.read(fd, STREAM_CHUNK):
                    count += len(block)
                    if count > spec['bytes']: raise ValueError('Test source grew')
                    raw_hash.update(block); gz.write(block)
                    if progress: progress(count)
            target.flush(); os.fsync(target.fileno())
        if count != spec['bytes'] or raw_hash.hexdigest() != spec['sha256'] or file_identity(fd) != initial:
            raise ValueError('Test source changed or differs from its exact pin')
    data = json.loads(resource('image-catalog.json'))
    descriptor_key = digest(spec)
    images = [i for i in data['images'] if digest(i['descriptor']) == descriptor_key]
    compatible = images[0]['lessons'] if images else copy.deepcopy(data['images'][0]['lessons'])
    if not images:
        data['images'].append({'descriptor':spec,'state':'active','legacy':False,'lessons':compatible})
    manifest = {'schema_version':1,'release_id':'isolated-full-size-test-only',
        'descriptor':spec,'backend':BACKEND,'lessons':compatible,
        'members':{name:{'bytes':len(raw),'sha256':hash_(raw)} for name,raw in members.items()}}
    manifest['members']['image.raw.gz'] = {'bytes':compressed.stat().st_size,'sha256':file_hash(compressed)}
    encoded = canonical(manifest)+b'\n'; signature = signer.sign(encoded)
    data['keys'] = [{'fingerprint':signer.fingerprint,'resource':'fixture.gpg'}]
    data['releases'] = [{'manifest_sha256':hash_(encoded),'descriptor_sha256':descriptor_key,
                         'signer':signer.fingerprint,'state':'active'}]
    catalog = Catalog(data, lambda name:signer.public if name=='fixture.gpg' else resource(name))
    with path.open('xb') as target:
        os.chmod(path, 0o600)
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
            for name, raw in {'manifest.json':encoded,'manifest.sig':signature,**members}.items():
                info=zipfile.ZipInfo(name);info.external_attr=0o100600<<16
                archive.writestr(info,raw)
            info=zipfile.ZipInfo('image.raw.gz');info.external_attr=0o100600<<16
            with archive.open(info,'w',force_zip64=True) as output, compressed.open('rb') as stream:
                while block := stream.read(STREAM_CHUNK): output.write(block)
        target.flush();os.fsync(target.fileno())
    return catalog, manifest, compressed
