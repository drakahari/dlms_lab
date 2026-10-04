#!/usr/bin/env python3
"""Explicit local registration of the exact reviewed image; no arbitrary VM import."""
import argparse, errno, os, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from learning_lab.vm_preview.files import Directory, require, sha256
from learning_lab.vm_preview.policy import image_spec
p=argparse.ArgumentParser();p.add_argument('image',type=Path);p.add_argument('--vm-home',type=Path,required=True);a=p.parse_args();spec=image_spec()
with Directory.absolute(a.image.absolute().parent) as source,Directory.absolute(a.vm_home.absolute(),create=True) as root:
 fd=source.open(a.image.name)
 try:
  require(os.fstat(fd).st_size==spec['bytes'] and sha256(fd)==spec['sha256'],'Image differs from the reviewed build')
  with root.child('images',create=True) as images,images.child(spec['sha256'],create=True,exclusive=True) as dest:
   out=dest.open('base.raw',write=True,new=True)
   try:
    os.ftruncate(out,spec['bytes']);position=0
    while position<spec['bytes']:
     try:start=os.lseek(fd,position,os.SEEK_DATA)
     except OSError as e:
      if e.errno==errno.ENXIO:break
      raise
     end=min(os.lseek(fd,start,os.SEEK_HOLE),spec['bytes']);os.lseek(fd,start,os.SEEK_SET);os.lseek(out,start,os.SEEK_SET)
     while start<end:
      copied=os.copy_file_range(fd,out,min(end-start,4*1024**2));require(copied>0,'Image copy stopped early');start+=copied
     position=end
    os.fsync(out);require(sha256(out)==spec['sha256'],'Registered image verification failed');os.fchmod(out,0o444)
   finally:os.close(out)
   dest.write('provenance.json',spec);os.fsync(dest.fd)
 finally:os.close(fd)
print('Registered exact local image:',a.vm_home/'images'/spec['sha256'])
