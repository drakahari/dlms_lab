"""Offline-only bundle validation and durable, non-overwriting registration.

CLI trust is always packaged trust. No key/catalog/size override exists in CLI,
profiles, environment variables, lessons or the graphical application.
"""
import argparse
from contextlib import contextmanager
import ctypes
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import uuid
import zipfile
import zlib
from .files import Directory, require, component, sha256
from .image_catalog import production_catalog, canonical, digest, read_json, HEX
from .bundle_archive import Archive, LIMITS
from .bundle_signature import verify
from .policy import BACKEND, RESERVE

CHUNK=1024**2
MEMBERS=set(LIMITS)-{'manifest.json','manifest.sig'}


@contextmanager
def source_file(path):
    path=Path(path).absolute();parts=path.parts[1:];require(parts,'Choose a bundle file')
    directory=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
    fd=None
    try:
        for name in parts[:-1]:
            component(name);new=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory)
            os.close(directory);directory=new
        component(parts[-1]);fd=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
        info=os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and info.st_nlink==1 and info.st_mode&0o022==0,
                'Bundle must be an owned regular file without links or shared writes')
        yield fd
    finally:
        if fd is not None:os.close(fd)
        os.close(directory)


def cancelled(callback):
    require(callback is None or not callback(),'Import cancelled before publication; existing images preserved')


def checkpoint(callback,name):
    if callback:callback(name)


def write_all(fd,raw):
    view=memoryview(raw)
    while view:
        n=os.write(fd,view);require(n>0,'Image write stopped early');view=view[n:]


def bytes_file(directory,name,raw,readonly=False):
    fd=directory.open(name,True,True)
    try:
        write_all(fd,raw)
        if readonly:os.fchmod(fd,0o444)
        os.fsync(fd)
    finally:os.close(fd)


def header(archive,catalog):
    raw=archive.read('manifest.json');signature=archive.read('manifest.sig')
    value=read_json(raw)
    require(isinstance(value,dict) and set(value)=={'schema_version','release_id','descriptor','backend','lessons','members'} and
            type(value['schema_version']) is int and value['schema_version']==1,'Unsupported bundle manifest')
    require(raw==canonical(value)+b'\n','Manifest must use the canonical byte encoding')
    key=hashlib.sha256(raw).hexdigest();release=catalog.releases.get(key)
    require(release is not None,'Manifest is not in this application\'s trusted release allowlist')
    require(digest(value['descriptor'])==release['descriptor_sha256'],'Release image descriptor differs')
    image=catalog.images[release['descriptor_sha256']]
    require(image['descriptor']==value['descriptor'],'Image descriptor differs')
    require(release['state']!='withdrawn' and image['state']!='withdrawn','Release is withdrawn; installation refused')
    require(isinstance(value['release_id'],str) and 0<len(value['release_id'])<=80 and
            all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-.' for c in value['release_id']),'Invalid release ID')
    require(value['backend']==BACKEND,'Unsupported image backend')
    require(isinstance(value['lessons'],list) and value['lessons']==image['lessons'],'Manifest lesson compatibility differs from trusted catalog')
    seen=set()
    for item in value['lessons']:
        require(isinstance(item,dict) and set(item)=={'id','sha256'},'Invalid lesson compatibility')
        require(isinstance(item['id'],str) and isinstance(item['sha256'],str),'Invalid lesson identity types')
        pair=(item['id'],item['sha256']);require(pair in catalog.lessons and pair not in seen,'Unsupported or duplicate lesson revision');seen.add(pair)
        require(catalog.lessons[pair][0]['state']!='withdrawn','Compatible lesson is withdrawn')
    require(isinstance(value['members'],dict) and set(value['members'])==MEMBERS,'Unsupported payload members')
    for name,details in value['members'].items():
        require(isinstance(details,dict) and set(details)=={'bytes','sha256'} and type(details['bytes']) is int and
                0<=details['bytes']<=LIMITS[name] and isinstance(details['sha256'],str) and HEX.fullmatch(details['sha256']), 'Invalid payload size/hash: '+name)
        require(archive.size(name)==details['bytes'],'Payload length differs: '+name)
    verify(raw,signature,catalog.keys[release['signer']],release['signer'])
    return value,raw,signature,key


def enough_space(directory,needed):
    space=os.fstatvfs(directory.fd)
    require(space.f_bavail*space.f_frsize>=needed+RESERVE,'Insufficient space for staging and safety margin; no space is reserved')


def process_payload(archive,stage,manifest,raw,signature,key,cancel=None,hook=None):
    spec=manifest['descriptor'];receipt={'schema_version':1,'kind':'bundle','manifest_sha256':key,
        'descriptor_sha256':digest(spec),'signature_sha256':hashlib.sha256(signature).hexdigest()}
    enough_space(stage,spec['bytes']+manifest['members']['image.raw.gz']['bytes']+16*1024**2)
    for name in ('packages.json','provenance.json','notices.txt'):
        cancelled(cancel);content=archive.read(name);info=manifest['members'][name]
        require(len(content)==info['bytes'] and hashlib.sha256(content).hexdigest()==info['sha256'],'Metadata hash differs: '+name)
        if name.endswith('.json'):read_json(content,LIMITS[name])
        else:
            text=content.decode('utf-8');require('\x00' not in text,'NUL in notices')
        bytes_file(stage,'release-provenance.json' if name=='provenance.json' else name,content,True)
    compressed=stage.open('image.raw.gz',True,True)
    try:
        count=0;hash_=hashlib.sha256()
        with archive.open('image.raw.gz') as stream:
            while True:
                cancelled(cancel);block=stream.read(CHUNK)
                if not block:break
                count+=len(block);require(count<=manifest['members']['image.raw.gz']['bytes'],'Compressed size exceeds declared limit')
                hash_.update(block);write_all(compressed,block)
        require(count==manifest['members']['image.raw.gz']['bytes'] and hash_.hexdigest()==manifest['members']['image.raw.gz']['sha256'], 'Compressed payload size/hash differs')
        os.fsync(compressed);checkpoint(hook,'compressed-verified');cancelled(cancel)
        os.lseek(compressed,0,os.SEEK_SET);decoder=zlib.decompressobj(31);count=0;hash_=hashlib.sha256()
        out=stage.open('base.raw',True,True)
        try:
            while True:
                block=os.read(compressed,CHUNK)
                if not block:break
                require(not decoder.eof,'Concatenated gzip or trailing data forbidden')
                while block:
                    cancelled(cancel)
                    decoded=decoder.decompress(block,min(CHUNK,spec['bytes']-count+1))
                    count+=len(decoded);require(count<=spec['bytes'],'Raw payload exceeds exact size')
                    hash_.update(decoded);write_all(out,decoded)
                    require(not decoder.unused_data,'Concatenated gzip or trailing data forbidden')
                    block=decoder.unconsumed_tail
                enough_space(stage,max(0,spec['bytes']-count))
            require(decoder.eof and count==spec['bytes'] and hash_.hexdigest()==spec['sha256'],'Raw payload size/hash or gzip end differs')
            os.fchmod(out,0o444);os.fsync(out)
            require(sha256(out)==spec['sha256'],'Staged raw image readback differs')
        finally:os.close(out)
    finally:os.close(compressed)
    # Only own transient compressed copy is removed, never an input or old image.
    os.unlink('image.raw.gz',dir_fd=stage.fd)
    for name,content in (('manifest.json',raw),('manifest.sig',signature),('provenance.json',canonical(spec)+b'\n'),('receipt.json',canonical(receipt)+b'\n')):
        bytes_file(stage,name,content,True)
    os.fsync(stage.fd);seal=seal_directory(stage);checkpoint(hook,'prepared');return seal


def file_identity(fd):
    st=os.fstat(fd)
    return (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns,stat.S_IMODE(st.st_mode))


def seal_directory(directory):
    result={}
    for name in directory.names():
        fd=directory.open(name)
        try:
            identity=file_identity(fd);hash_=sha256(fd)
            require(file_identity(fd)==identity,'Staged member changed during hashing')
            result[name]=(identity,hash_)
        finally:os.close(fd)
    return result


def verify_identity(directory,seal):
    require(set(directory.names())==set(seal),'Staged image members changed after validation; publication refused')
    for name,(identity,hash_) in seal.items():
        fd=directory.open(name)
        try:require(file_identity(fd)==identity,'Staged image member changed after validation; publication refused')
        finally:os.close(fd)


def same_installation(existing,seal):
    # Hash the existing directory OUTSIDE the VM operation lock. Exact existing
    # bytes are authoritative; a second manifest/receipt never replaces them.
    require(set(existing.names())==set(seal),'Image registration conflict: members/legacy receipt differ; existing directory preserved')
    found=seal_directory(existing)
    for name,(identity,hash_) in seal.items():
        current,current_hash=found[name]
        require(current[2]==identity[2] and current_hash==hash_,
                'Image registration conflict: manifest, receipt or content differs; existing directory preserved')
        if name=='base.raw':require(current[5]&0o222==0,'Existing image is writable; preserved without changes')
    return found


def publish(staging,stage_name,stage,images,digest_,seal,existing_seal,hook=None):
    verify_identity(stage,seal)
    if images.exists(digest_):
        require(existing_seal is not None,'Image appeared during publication; preserved, retry import')
        with images.child(digest_) as existing:
            verify_identity(existing,existing_seal)
            # A previous rename may have succeeded before its parent sync failed.
            os.fsync(existing.fd)
        os.fsync(images.fd);os.fsync(staging.fd)
        return 'already-installed'
    require(existing_seal is None,'Existing image disappeared during publication; no replacement performed')
    checkpoint(hook,'before-publication');verify_identity(stage,seal)
    original=os.fstat(stage.fd);entry=os.stat(stage_name,dir_fd=staging.fd,follow_symlinks=False)
    require((entry.st_dev,entry.st_ino)==(original.st_dev,original.st_ino) and stat.S_ISDIR(entry.st_mode), 'Staging directory substituted; publication refused')
    libc=ctypes.CDLL(None,use_errno=True)
    result=libc.renameat2(staging.fd,os.fsencode(stage_name),images.fd,os.fsencode(digest_),1)
    if result:raise OSError(ctypes.get_errno(),'Image publication refused; staging and existing images retained')
    entry=os.stat(digest_,dir_fd=images.fd,follow_symlinks=False)
    require((entry.st_dev,entry.st_ino)==(original.st_dev,original.st_ino),'Published directory identity differs; operation refused')
    with images.child(digest_) as published:verify_identity(published,seal)
    checkpoint(hook,'published')
    os.fsync(images.fd);os.fsync(staging.fd)
    checkpoint(hook,'durable')
    return 'installed'


def commit_image(staging,name,stage,images,digest_,gate_root,seal,hook=None):
    verify_identity(stage,seal)
    existing_seal=None
    if images.exists(digest_):
        with images.child(digest_) as existing:existing_seal=same_installation(existing,seal)
    # No full-image hashing or decompression while Stop needs this lock.
    with publication_lock(gate_root):
        return publish(staging,name,stage,images,digest_,seal,existing_seal,hook)


@contextmanager
def import_lock(root):
    fd=root.open('imports.lock',True,not root.exists('imports.lock'))
    try:
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('Another image import is in progress; retry after it finishes')
        yield
    finally:os.close(fd)


@contextmanager
def publication_lock(gate_root):
    with Directory.absolute(gate_root,create=True) as gate:
        fd=gate.open('operations.lock',True,not gate.exists('operations.lock'))
        try:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise ValueError('Another VM operation is in progress; prepared image retained, retry import')
            yield
        finally:os.close(fd)


def validate_bundle(path,*,_catalog=None):
    catalog=_catalog if _catalog is not None else production_catalog()
    with source_file(path) as fd,Archive(fd) as archive:
        manifest,raw,signature,key=header(archive,catalog)
        with tempfile.TemporaryDirectory(prefix='oll-image-validation-') as temp,Directory.absolute(temp) as stage:
            process_payload(archive,stage,manifest,raw,signature,key)
        return {'result':'valid','manifest_sha256':key,'release_id':manifest['release_id'],'raw_sha256':manifest['descriptor']['sha256'],
                'message':'Integrity and compatibility validated; no installation or guest playtest performed.'}


def import_bundle(path,vm_home,*,_catalog=None,_cancel=None,_checkpoint=None,_gate_root=None):
    catalog=_catalog if _catalog is not None else production_catalog()
    with source_file(path) as fd,Archive(fd) as archive:
        manifest,raw,signature,key=header(archive,catalog);cancelled(_cancel)
        with Directory.absolute(Path(vm_home).absolute(),create=True) as root,import_lock(root),root.child('staging',create=True) as staging,root.child('images',create=True) as images:
            name=uuid.uuid4().hex
            with staging.child(name,create=True,exclusive=True) as stage:
                seal=process_payload(archive,stage,manifest,raw,signature,key,_cancel,_checkpoint)
                cancelled(_cancel)
                result=commit_image(staging,name,stage,images,manifest['descriptor']['sha256'],
                                    _gate_root or f'/run/user/{os.getuid()}/oll-vm-preview',seal,_checkpoint)
                return {'result':result,'manifest_sha256':key,'raw_sha256':manifest['descriptor']['sha256']}


def register_local_image(path,vm_home,*,_gate_root=None):
    """Preserve legacy exact-hash registration, now using atomic directory publication."""
    from .policy import image_spec
    spec=image_spec()
    with source_file(path) as fd:
        require(os.fstat(fd).st_size==spec['bytes'] and sha256(fd)==spec['sha256'],'Image differs from the reviewed local build')
        with Directory.absolute(Path(vm_home).absolute(),create=True) as root,import_lock(root),root.child('staging',create=True) as staging,root.child('images',create=True) as images:
            name=uuid.uuid4().hex
            with staging.child(name,create=True,exclusive=True) as stage:
                enough_space(stage,spec['bytes'])
                out=stage.open('base.raw',True,True)
                try:
                    os.ftruncate(out,spec['bytes']);position=0
                    while position<spec['bytes']:
                        try:start=os.lseek(fd,position,os.SEEK_DATA)
                        except OSError as exc:
                            if exc.errno==errno.ENXIO:break
                            raise
                        end=min(os.lseek(fd,start,os.SEEK_HOLE),spec['bytes'])
                        os.lseek(fd,start,os.SEEK_SET);os.lseek(out,start,os.SEEK_SET)
                        while start<end:
                            block=os.read(fd,min(CHUNK,end-start));require(block,'Source image stopped early')
                            write_all(out,block);start+=len(block)
                        position=end
                    require(sha256(out)==spec['sha256'],'Local image copy hash differs')
                    os.fchmod(out,0o444);os.fsync(out)
                finally:os.close(out)
                # Exact historical format; no fabricated bundle/signature receipt.
                stage.write('provenance.json',spec);os.fsync(stage.fd)
                seal=seal_directory(stage)
                return commit_image(staging,name,stage,images,spec['sha256'],
                                    _gate_root or f'/run/user/{os.getuid()}/oll-vm-preview',seal)


def main(argv=None):
    parser=argparse.ArgumentParser(description='Validate or register an explicitly trusted offline VM image. Never boots an image.')
    sub=parser.add_subparsers(dest='command',required=True)
    for command in ('validate','import'):
        child=sub.add_parser(command);child.add_argument('bundle',type=Path)
        if command=='import':child.add_argument('--vm-home',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        result=validate_bundle(args.bundle) if args.command=='validate' else import_bundle(args.bundle,args.vm_home)
        print(json.dumps(result));return 0
    except (ValueError,OSError,zipfile.BadZipFile,zlib.error,EOFError) as exc:
        print('Image operation refused: '+str(exc));return 1
    except KeyboardInterrupt:
        print('Image operation interrupted. Inspect/retry: pre-publication staging is inactive; a completed publication is retained.');return 130


if __name__=='__main__':raise SystemExit(main())
