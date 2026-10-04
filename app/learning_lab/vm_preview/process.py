"""Bounded QMP and process identity. No HMP, guest-exec or host-path messages."""
import hashlib
import json
import os
import socket
import stat
import struct
import time
from pathlib import Path
from .files import require, Refused
from .policy import QEMU, verify_arguments

COMMANDS=frozenset(('query-status','query-uuid','query-block','query-kvm','query-cpus-fast','query-memory-size-summary','system_powerdown','stop','quit'))

def process_identity(pid):
    require(type(pid) is int and pid>1,'Invalid QEMU PID')
    root=Path('/proc')/str(pid)
    try:
        uid=root.stat().st_uid
        fields=(root/'stat').read_text().rsplit(')',1)[1].split()
        if fields[0]=='Z':return None
        args=(root/'cmdline').read_bytes()
        exe=os.stat(root/'exe');trusted=os.stat(QEMU)
    except (FileNotFoundError,ProcessLookupError):return None
    except PermissionError as exc:raise Refused('Cannot verify QEMU ownership; no control action taken') from exc
    require(uid==os.getuid() and (exe.st_dev,exe.st_ino)==(trusted.st_dev,trusted.st_ino),'Process is not this user’s trusted QEMU')
    return {'pid':pid,'start':fields[19],'boot':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'argv_sha256':hashlib.sha256(args).hexdigest()}

def same_process(record):
    actual=process_identity(record['process']['pid'])
    if actual is None:return False
    require(actual==record['process'],'Stale or forged QEMU process record; no action taken')
    return True

def verify_launch(record,socket_path):
    require(same_process(record),'QEMU is no longer running')
    try:
        raw=Path('/proc')/str(record['process']['pid'])/'cmdline'
        args=[part.decode() for part in raw.read_bytes().split(b'\0') if part]
        verify_arguments(args,record['run'],socket_path)
    except (OSError,UnicodeError) as exc:
        raise Refused('Cannot verify QEMU launch policy; no control action taken') from exc
    require(same_process(record),'QEMU changed during policy verification')


class Qmp:
    def __init__(self,directory,record):
        require(same_process(record),'QEMU is no longer running')
        info=os.stat('qmp',dir_fd=directory.fd,follow_symlinks=False)
        require(stat.S_ISSOCK(info.st_mode) and info.st_uid==os.getuid(),'Unsafe QMP endpoint')
        self.sock=socket.socket(socket.AF_UNIX);self.sock.settimeout(2);self.buf=b'';self.events=[];self.seq=0
        try:
            self.sock.connect(f'/proc/self/fd/{directory.fd}/qmp')
            pid,uid,gid=struct.unpack('3i',self.sock.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
            require(pid==record['process']['pid'] and uid==os.getuid(),'QMP peer identity mismatch')
            require('QMP' in self.read(),'Invalid QMP greeting')
            self._call('qmp_capabilities')
            require(self.call('query-uuid')['UUID']==record['run'],'QMP VM UUID mismatch')
        except BaseException:self.sock.close();raise
    def close(self):self.sock.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def read(self):
        while b'\n' not in self.buf:
            chunk=self.sock.recv(8192)
            if not chunk:raise EOFError('QEMU control disconnected')
            self.buf+=chunk;require(len(self.buf)<=65536,'QMP response exceeds limit')
        line,self.buf=self.buf.split(b'\n',1);value=json.loads(line)
        require(isinstance(value,dict),'Invalid QMP message');return value
    def _call(self,command):
        self.seq+=1;self.sock.sendall((json.dumps({'execute':command,'id':self.seq})+'\n').encode())
        for _ in range(128):
            value=self.read()
            if 'event' in value:self.events.append(value);continue
            require(value.get('id')==self.seq,'Unexpected QMP response')
            require('error' not in value,'QMP refused trusted operation')
            return value.get('return')
        raise Refused('Too many QMP messages')
    def call(self,command):
        require(command in COMMANDS,'Unsupported QMP operation')
        return self._call(command)
    def powerdown(self,record,timeout=35):
        self.call('system_powerdown');deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            try:
                msg=self.read()
                if 'event' in msg:self.events.append(msg)
                require(len(self.events)<=128,'Too many QMP events')
            except socket.timeout:pass
            except EOFError:break
            if not same_process(record):break
        clean=any(e.get('event')=='SHUTDOWN' and e.get('data',{}).get('guest') is True for e in self.events)
        while time.monotonic()<deadline and same_process(record):time.sleep(.05)
        require(not same_process(record),'Guest did not shut down. Disk retained; force stop needs explicit confirmation.')
        return clean
