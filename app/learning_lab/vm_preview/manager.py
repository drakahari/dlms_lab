"""Separate optional VM sessions. No simulation records or profile backup changes."""
from contextlib import contextmanager, ExitStack
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from .files import Directory, Refused, require, sha256
from .policy import image_spec, lesson, inspect_overlay, launch_arguments, QEMU, QEMU_IMG, VIRTUAL_BYTES, FILE_CEILING, RESERVE, BACKEND
from .process import process_identity, same_process, verify_launch, Qmp


def now():
    from datetime import datetime,timezone
    return datetime.now(timezone.utc).isoformat()

def uuid_text(value):
    require(isinstance(value,str) and str(uuid.UUID(value))==value,'Invalid VM identity');return value

class Manager:
    def __init__(self,home,profile_key,gate_root=None,*,spec=None,lesson_id=None):
        self.home=Path(home).absolute();self.profile=profile_key
        self.binding=hashlib.sha256(str(self.home).encode()).hexdigest()
        require(len(profile_key)==64 and all(c in '0123456789abcdef' for c in profile_key),'Invalid profile binding')
        self.gate_root=Path(gate_root or f'/run/user/{os.getuid()}/oll-vm-preview')
        self.spec=spec or image_spec()
        if lesson_id is None:self.lesson=lesson()
        else:
            from .registry import load_lesson
            self.lesson=load_lesson(lesson_id)
        self.pin={'backend':BACKEND,'image':self.spec,'lesson_sha256':hashlib.sha256(json.dumps(self.lesson,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
    def _authorize(self,operation,session):
        # Catalog adapter checks availability inside the existing operation lock.
        # Legacy direct construction retains the approved local-only behavior.
        pass
    @contextmanager
    def access(self):
        require(os.getuid()!=0,'Run the VM preview as an ordinary user, never root')
        with ExitStack() as stack:
            root=stack.enter_context(Directory.absolute(self.home,create=True))
            gate=stack.enter_context(Directory.absolute(self.gate_root,create=True))
            lock=gate.open('operations.lock',write=True,new=not gate.exists('operations.lock'));stack.callback(os.close,lock)
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise Refused('Another VM operation is in progress')
            profiles=stack.enter_context(root.child('profiles',create=True));profile=stack.enter_context(profiles.child(self.profile,create=True))
            yield root,gate,profile
    def gate(self,gate):
        fd=gate.open('running.lock',write=True,new=not gate.exists('running.lock'))
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:os.close(fd);raise Refused('A preview VM is already running, possibly in another profile')
        return fd
    def current(self,profile):
        if not profile.exists('current.json'):return None
        s=profile.json('current.json')
        require(set(s)=={'schema_version','session','generation','mode','pin','started','step','hints','completion'},'Unsupported VM session record')
        require(s['schema_version']==1 and s['mode'] in ('Learn','Challenge'),'Unsupported VM session')
        uuid_text(s['session']);uuid_text(s['generation'])
        require(s['pin']==self.pin,'Session requires its exact older lesson/image/backend; preserved without upgrading')
        require(type(s['step']) is int and 0<=s['step']<=len(self.lesson['steps']) and type(s['hints']) is int and 0<=s['hints']<=len(self.lesson['hints']),'Invalid VM guidance record')
        require(s['completion'] is None or isinstance(s['completion'],dict) and set(s['completion'])=={'kind','at'} and s['completion']['kind']=='self-reviewed','Invalid completion record')
        return s
    def record(self,gate):
        if not gate.exists('running.json'):return None
        r=gate.json('running.json')
        require(set(r)=={'schema_version','run','store','profile','session','generation','state','process'},'Invalid VM runtime record')
        require(r['schema_version']==1 and r['state'] in ('intent','running','stopped','unclean'),'Invalid VM lifecycle state')
        uuid_text(r['run']);uuid_text(r['session']);uuid_text(r['generation'])
        require(all(isinstance(r[k],str) and len(r[k])==64 and all(c in '0123456789abcdef' for c in r[k]) for k in ('store','profile')),'Invalid runtime binding')
        require(r['state']!='running' or isinstance(r['process'],dict),'Missing running process identity')
        if r['process'] is not None:require(set(r['process'])=={'pid','start','boot','argv_sha256'},'Invalid process identity')
        return r
    def reconcile(self,gate,stopped_verified=False):
        r=self.record(gate)
        if not r:
            if not stopped_verified:
                fd=self.gate(gate);os.close(fd)
            return None
        if r['state']=='intent':
            found=[]
            for entry in Path('/proc').iterdir():
                if not entry.name.isdigit():continue
                try:
                    if entry.stat().st_uid!=os.getuid():continue
                    args=(entry/'cmdline').read_bytes().split(b'\0')
                except (FileNotFoundError,ProcessLookupError):continue
                except PermissionError:raise Refused('Cannot reconcile process inventory safely')
                if b'-uuid' in args:
                    index=args.index(b'-uuid')
                    if index+1<len(args) and args[index+1]==r['run'].encode():found.append(int(entry.name))
            require(len(found)<=1,'Multiple processes match the launch intent; no action taken')
            if found:
                pid=found[0];r['process']=process_identity(pid)
                require(r['process'] is not None,'Interrupted launch process exited; retry under the lifetime lock')
                verify_launch(r,str(self.gate_root/r['run']/'qmp'))
                with gate.child(r['run']) as rd,Qmp(rd,r) as q:
                    require(len(q.call('query-block'))==1,'Unexpected recovered disk graph')
                r['state']='running';gate.write('running.json',r,replace=True)
            else:
                require(stopped_verified,'Interrupted Start retained. Use Start/Resume to reconcile under the global lock.')
                r['state']='unclean';gate.write('running.json',r,replace=True)
        if r['state']=='running':
            if same_process(r):verify_launch(r,str(self.gate_root/r['run']/'qmp'))
            else:r['state']='unclean';gate.write('running.json',r,replace=True)
        elif not stopped_verified:
            # A terminal record (or a reused old PID) never proves the lifetime lock is free.
            fd=self.gate(gate);os.close(fd)
        return r
    def image(self,root):
        require(self.spec.get('prepared') is True,'Local preview image is not prepared; see the image recipe')
        digest=self.spec['sha256'];require(isinstance(digest,str) and len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'Invalid pinned image digest')
        try:
            with root.child('images') as images,images.child(digest) as image:
                fd=image.open('base.raw')
        except FileNotFoundError as exc:
            raise Refused('The pinned local image is not registered. Use the reviewed image preparation/registration recipe; no download or installation is automatic.') from exc
        try:
            s=os.fstat(fd);require(s.st_mode&0o222==0 and s.st_size==self.spec['bytes']==VIRTUAL_BYTES,'Base size/mode differs from pinned image')
            require(sha256(fd)==digest,'Base image hash differs; no launch/reset performed')
            return fd
        except BaseException:os.close(fd);raise
    def admission(self,root):
        disk=os.fstatvfs(root.fd)
        require(disk.f_bavail*disk.f_frsize>=FILE_CEILING+RESERVE,'Insufficient free space for one bounded overlay plus the safety margin. Existing disks retained.')
        mem={a:b.strip() for a,b in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())}
        require(int(mem['MemAvailable'].split()[0])*1024>=3*1024**3,'At least 3 GiB available RAM is required for this preview')
    def generation(self,profile,generation):
        with profile.child('generations') as generations:
            return generations.child(uuid_text(generation))
    def lifecycle(self,profile,generation):
        with self.generation(profile,generation) as gen:
            require(gen.exists('lifecycle.json'),'Disk lifecycle journal is missing; Resume is blocked. Confirmed Reset retains the generation and starts fresh.')
            value=gen.json('lifecycle.json')
            require(set(value)=={'state','at'} and value['state'] in ('fresh','intent','running','stopped','unclean'),'Invalid disk lifecycle journal')
            return value['state']
    def journal(self,profile,generation,state):
        with self.generation(profile,generation) as gen:
            gen.write('lifecycle.json',{'state':state,'at':now()},replace=True)
    def prepare(self,root,profile,mode):
        self._authorize('new',None)
        self.admission(root);base=self.image(root);os.close(base)
        ident=str(uuid.uuid4())
        with profile.child('generations',create=True) as generations,generations.child(ident,create=True,exclusive=True) as gen:
            fd=gen.open('disk.qcow2',write=True,new=True)
            try:
                subprocess.run([QEMU_IMG,'create','-f','qcow2','-o','compat=1.1,cluster_size=65536,refcount_bits=16,lazy_refcounts=off,extended_l2=off',f'/proc/self/fd/{fd}',str(VIRTUAL_BYTES)],pass_fds=(fd,),check=True,capture_output=True,timeout=15)
                inspect_overlay(fd);os.fsync(fd)
            finally:os.close(fd)
            s={'schema_version':1,'session':str(uuid.uuid4()),'generation':ident,'mode':mode,'pin':self.pin,'started':now(),'step':0,'hints':0,'completion':None}
            gen.write('origin.json',s)
            gen.write('lifecycle.json',{'state':'fresh','at':now()});os.fsync(gen.fd)
        # Publication is the only active-generation switch. Old generations never move.
        profile.write('current.json',s,replace=True);return s
    def reset(self,mode='Learn',confirmed=False):
        require(confirmed is True and mode in ('Learn','Challenge'),'Reset needs explicit confirmation and a valid mode')
        with self.access() as (root,gate,profile):
            fd=self.gate(gate)
            try:
                self.reconcile(gate,stopped_verified=True);old=self.current(profile)
                self._authorize('reset',old)
                if old:
                    profile.write('retained-'+uuid.uuid4().hex+'.json',old)
                return self.prepare(root,profile,mode)
            finally:os.close(fd)
    def start(self,mode='Learn',*,display='gtk'):
        require(mode in ('Learn','Challenge'),'Invalid mode')
        with self.access() as (root,gate,profile):
            gatefd=self.gate(gate);base=disk=None
            try:
                r=self.reconcile(gate,stopped_verified=True);s=self.current(profile)
                self._authorize('resume' if s else 'new',s)
                if s is None:s=self.prepare(root,profile,mode)
                require(not (r and r['state']=='unclean' and r['store']==self.binding and r['profile']==self.profile and r['generation']==s['generation']),'Unclean runtime record conflicts with this disk; Resume refused')
                require(s['mode']==mode,'Changing mode requires a confirmed reset into a new session')
                require(self.lifecycle(profile,s['generation']) in ('fresh','stopped'),'Unclean or interrupted disk retained unchanged. Use confirmed Reset for a fresh session; automatic repair/resume is unavailable.')
                self.admission(root);base=self.image(root)
                with self.generation(profile,s['generation']) as gen:
                    origin=gen.json('origin.json')
                    require(all(origin.get(k)==s[k] for k in ('schema_version','session','generation','mode','pin','started')),'Disk generation provenance differs from the session')
                    disk=gen.open('disk.qcow2',write=True)
                require(os.fstat(disk).st_size<FILE_CEILING,'Overlay reached its file ceiling; preserved for recovery')
                inspect_overlay(disk)
                # Read-only consistency check; no automatic repair, rebase or commit.
                subprocess.run([QEMU_IMG,'check','-f','qcow2',f'/proc/self/fd/{disk}'],pass_fds=(disk,),capture_output=True,check=True,timeout=20)
                run=str(uuid.uuid4());runtime={'schema_version':1,'run':run,'store':self.binding,'profile':self.profile,'session':s['session'],'generation':s['generation'],'state':'intent','process':None}
                with gate.child(run,create=True,exclusive=True) as rd:
                    socket_path=str(self.gate_root/run/'qmp');require(len(socket_path.encode())<104,'Runtime socket path is too long')
                    self.journal(profile,s['generation'],'intent')
                    gate.write('running.json',runtime,replace=True)
                    args=launch_arguments(base,disk,gatefd,run,socket_path,display=display)
                    log=rd.open('qemu.log',write=True,new=True)
                    try:
                        child=subprocess.Popen([sys.executable,'-I','-B',str(Path(__file__).with_name('runner.py')),str(FILE_CEILING),*args],pass_fds=(base,disk,gatefd),stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
                    finally:os.close(log)
                    for _ in range(100):
                        if child.poll() is not None:
                            runtime['state']='unclean';gate.write('running.json',runtime,replace=True);raise Refused('QEMU failed to start; disk and launch log retained')
                        if rd.exists('qmp'):
                            runtime['process']=process_identity(child.pid)
                            if runtime['process']:
                                with Qmp(rd,runtime) as q:
                                    require(q.call('query-kvm')['enabled'],'KVM did not activate')
                                    require(len(q.call('query-block'))==1,'Unexpected runtime disk graph')
                                runtime['state']='running';gate.write('running.json',runtime,replace=True)
                                self.journal(profile,s['generation'],'running');return s
                        time.sleep(.05)
                    raise Refused('Start is incomplete. Process/disk evidence retained; recovery inspection required.')
            finally:
                for fd in (base,disk,gatefd):
                    if fd is not None:os.close(fd) # QEMU retains gate fdset for its whole lifetime.
    def stop(self,force=False,confirmed=False):
        require(not force or confirmed is True,'Force stop requires explicit confirmation')
        with self.access() as (root,gate,profile):
            r=self.reconcile(gate)
            if not r or r['state']!='running':
                fd=self.gate(gate);os.close(fd)
                return 'Already stopped; lifetime lock is free and retained disks are unchanged'
            require(r['profile']==self.profile and r['store']==self.binding,'Another profile owns the running VM')
            with gate.child(r['run']) as rd,Qmp(rd,r) as q:
                if force:
                    try:q.call('quit')
                    except EOFError:pass
                    deadline=time.monotonic()+5
                    while time.monotonic()<deadline and same_process(r):time.sleep(.05)
                    require(not same_process(r),'QEMU exit not confirmed; reset remains blocked');clean=False
                else:clean=q.powerdown(r)
            r['state']='stopped' if clean else 'unclean';gate.write('running.json',r,replace=True)
            self.journal(profile,r['generation'],r['state'])
            return 'Cleanly stopped' if clean else 'Stopped uncleanly; disk retained, no repair performed'
    def status(self):
        with self.access() as (root,gate,profile):
            r=self.reconcile(gate);s=self.current(profile);state='not-started' if not s else 'stopped';message=''
            if r and r['profile']==self.profile and r['store']==self.binding and s and r['generation']==s['generation']:
                state=r['state']
                if state=='running':
                    try:
                        with gate.child(r['run']) as rd,Qmp(rd,r) as q:
                            state=q.call('query-status')['status']
                            if state=='io-error':message='Guest I/O stopped after a disk error. Disk retained; no repair performed. An explicitly confirmed force stop may be needed.'
                            available=os.fstatvfs(root.fd);low=available.f_bavail*available.f_frsize<RESERVE
                            with self.generation(profile,s['generation']) as gen:
                                f=gen.open('disk.qcow2');near=os.fstat(f).st_size>=FILE_CEILING-64*1024**2;os.close(f)
                            if state=='running' and (low or near):q.call('stop');state='paused';message='Storage safeguard paused the VM. Disk retained. Stop may require explicit force stop.'
                    except (FileNotFoundError,ConnectionError,EOFError) as exc:
                        raise Refused('QEMU process exists but control is unavailable; no reset or second launch permitted') from exc
            if s:
                try:
                    lifecycle=self.lifecycle(profile,s['generation'])
                    if state=='stopped' and lifecycle not in ('fresh','stopped'):
                        fd=self.gate(gate);os.close(fd)
                        state='unclean';message='Disk from an interrupted or unclean run is retained. Resume is blocked to preserve evidence; use confirmed Reset for a new session.'
                    with self.generation(profile,s['generation']) as gen:f=gen.open('disk.qcow2');os.close(f)
                except FileNotFoundError:state='disk-missing';message='Guest disk unavailable. Resume is disabled; Reset creates a new session.'
            return {'state':state,'session':s,'message':message,'other_profile_running':bool(r and r['state']=='running' and (r['profile']!=self.profile or r['store']!=self.binding))}
    def progress(self,kind):
        require(kind in ('next','back','hint','complete'),'Unknown VM guidance action')
        with self.access() as (root,gate,profile):
            s=self.current(profile);require(s is not None,'Start a session first')
            if kind=='hint':require(s['mode']=='Learn','Hints are hidden in Challenge');s['hints']=min(len(self.lesson['hints']),s['hints']+1)
            elif kind=='next':require(s['mode']=='Learn','Guidance is hidden in Challenge');s['step']=min(len(self.lesson['steps'])-1,s['step']+1)
            elif kind=='back':s['step']=max(0,s['step']-1)
            else:s['completion']={'kind':'self-reviewed','at':now()}
            profile.write('current.json',s,replace=True);return s
