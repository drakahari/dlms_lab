#!/usr/bin/env python3
"""Developer-only registration of the exact bundled local administrator build.

No new bundle trust, arbitrary descriptor, receipt or app startup action. Uses the
existing descriptor containment, publication, collision and shared exclusion guards.
"""
import argparse, errno, os, sys, uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from learning_lab.vm_preview.image_catalog import production_catalog
from learning_lab.vm_preview.image_bundle import source_file, import_lock, enough_space, write_all, seal_directory, commit_image, CHUNK
from learning_lab.vm_preview.files import Directory, require, sha256

def register(image, home):
    spec,_=production_catalog().defaults('real-linux-discovery-lifecycle')
    require(spec['image_id']=='debian13-package-admin-local-v1','Unexpected administrator image identity')
    with source_file(image) as fd:
        require(os.fstat(fd).st_size==spec['bytes'] and sha256(fd)==spec['sha256'],'Image differs from the exact reviewed administrator build')
        with Directory.absolute(Path(home).absolute(),create=True) as root,import_lock(root),root.child('staging',create=True) as staging,root.child('images',create=True) as images:
            name=uuid.uuid4().hex
            with staging.child(name,create=True,exclusive=True) as stage:
                enough_space(stage,spec['bytes']);out=stage.open('base.raw',True,True)
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
                            block=os.read(fd,min(CHUNK,end-start));require(block,'Source ended early')
                            write_all(out,block);start+=len(block)
                        position=end
                    require(sha256(out)==spec['sha256'],'Copied administrator image hash differs')
                    os.fchmod(out,0o444);os.fsync(out)
                finally:os.close(out)
                stage.write('provenance.json',spec);os.fsync(stage.fd)
                return commit_image(staging,name,stage,images,spec['sha256'],f'/run/user/{os.getuid()}/oll-vm-preview',seal_directory(stage))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('image',type=Path);p.add_argument('--vm-home',type=Path,required=True);a=p.parse_args()
    print(register(a.image,a.vm_home))
