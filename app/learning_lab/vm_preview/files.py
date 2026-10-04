"""Descriptor-relative private storage; no lesson-provided filesystem paths."""
import ctypes
import errno
import hashlib
import json
import os
import re
import stat
import uuid
from contextlib import contextmanager

class Refused(ValueError): pass

def require(ok, message):
    if not ok: raise Refused(message)

def component(name):
    require(isinstance(name,str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,128}',name) and name not in ('.','..'), 'Invalid storage component')
    return name

class Directory:
    def __init__(self, fd):
        self.fd=fd
        s=os.fstat(fd);self._identity=(s.st_dev,s.st_ino)
    @classmethod
    def absolute(cls,path,create=False):
        path=os.fspath(path)
        require(path.startswith('/') and '..' not in path.split('/'), 'Storage root must be absolute without traversal')
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
        try:
            parts=[p for p in path.split('/') if p]
            for i,name in enumerate(parts):
                component(name)
                try:nxt=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                except FileNotFoundError:
                    require(create,'VM storage is not prepared')
                    os.mkdir(name,0o700,dir_fd=fd);os.fsync(fd)
                    nxt=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                os.close(fd);fd=nxt
            s=os.fstat(fd)
            require(s.st_uid==os.getuid() and s.st_mode&0o077==0,'VM storage must be owned by you with mode 0700')
            return cls(fd)
        except BaseException:os.close(fd);raise
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def child(self,name,create=False,exclusive=False):
        component(name)
        if create:
            try:os.mkdir(name,0o700,dir_fd=self.fd);os.fsync(self.fd)
            except FileExistsError:
                if exclusive:raise Refused('Generation already exists; preserved without replacement')
        fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=self.fd)
        s=os.fstat(fd)
        if s.st_uid!=os.getuid() or s.st_mode&0o077:os.close(fd);raise Refused('Unsafe VM directory ownership/mode')
        return Directory(fd)
    def open(self,name,write=False,new=False):
        component(name)
        flags=(os.O_RDWR if write else os.O_RDONLY)|os.O_NOFOLLOW|os.O_NONBLOCK
        if new:flags|=os.O_CREAT|os.O_EXCL
        fd=os.open(name,flags,0o600,dir_fd=self.fd);s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_nlink!=1 or s.st_mode&0o022:
            os.close(fd);raise Refused('Expected owned regular VM file without links or shared writes')
        return fd
    def exists(self,name):
        try:os.stat(component(name),dir_fd=self.fd,follow_symlinks=False);return True
        except FileNotFoundError:return False
    def read(self,name,limit=65536):
        fd=self.open(name)
        try:
            require(os.fstat(fd).st_size<=limit,'VM record exceeds limit')
            data=os.read(fd,limit+1);require(len(data)<=limit,'VM record exceeds limit');return data
        finally:os.close(fd)
    def json(self,name):
        def pairs(items):
            out={}
            for k,v in items:require(k not in out,'Duplicate JSON field');out[k]=v
            return out
        return json.loads(self.read(name),object_pairs_hook=pairs)
    def write(self,name,value,replace=False):
        component(name);raw=json.dumps(value,sort_keys=True,indent=2).encode()+b'\n'
        require(len(raw)<=65536,'VM record exceeds limit')
        temp='staged-'+uuid.uuid4().hex+'.json';fd=self.open(temp,True,True)
        try:
            with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
            if replace:
                if self.exists(name):
                    old=self.open(name);os.close(old)
                os.replace(temp,name,src_dir_fd=self.fd,dst_dir_fd=self.fd)
            else:
                libc=ctypes.CDLL(None,use_errno=True)
                result=libc.renameat2(self.fd,os.fsencode(temp),self.fd,os.fsencode(name),1)
                if result:raise OSError(ctypes.get_errno(),'No-replace record publication failed')
            os.fsync(self.fd)
        except BaseException:
            # Retain staged evidence. It is never interpreted as an active record.
            raise
    def names(self):
        # dup/listdir(fd) shares the old open-file description, including its
        # directory cursor and filesystem enumeration state. Reopen only this
        # verified directory, never its pathname, for an independent snapshot.
        def state(fd):
            s=os.fstat(fd)
            require(stat.S_ISDIR(s.st_mode) and (s.st_dev,s.st_ino)==self._identity
                    and s.st_uid==os.getuid() and s.st_mode&0o077==0,
                    'Directory identity or ownership/mode changed')
            return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,
                    s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        require(self.fd is not None,'Directory is closed')
        before=state(self.fd)
        fd=os.open('.',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=self.fd)
        try:
            require(state(fd)==before,'Directory changed before enumeration')
            names=os.listdir(fd)
            require(state(fd)==before and state(self.fd)==before,
                    'Directory changed during enumeration')
            require(len(names)==len(set(names)),'Duplicate directory members')
            return names
        finally:os.close(fd)

def sha256(fd):
    os.lseek(fd,0,os.SEEK_SET)
    with os.fdopen(os.dup(fd),'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
