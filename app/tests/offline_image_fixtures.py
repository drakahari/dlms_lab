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
                  'lessons':[{'id':l['id'],'sha256':l['sha256']} for l in data['lessons']],
                  'members':{k:{'bytes':len(v),'sha256':hash_(v)} for k,v in members.items()}}
        if manifest_edit:manifest_edit(manifest)
        encoded=canonical(manifest)+b'\n';signature=self.sign(encoded)
        data['images'].append({'descriptor':spec,'state':state,'legacy':False,'lessons':[{'id':l['id'],'sha256':l['sha256']} for l in data['lessons']]})
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
