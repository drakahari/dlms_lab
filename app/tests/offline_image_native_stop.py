"""Opt-in REAL guest Stop-routing acceptance; never mocks controller success.
Uses the normal shared gate. Each invocation reopens the same disposable profile.
Blocked ownership/visibility stops before application construction or guest launch.
"""
import argparse, copy, fcntl, hashlib, json, os, resource, subprocess, sys, time
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.vm_preview.files import Directory, Refused, component
from learning_lab.vm_preview.image_catalog import digest, production_catalog
from learning_lab.vm_preview.policy import image_spec, QEMU
from learning_lab.vm_preview.process import Qmp, same_process, verify_launch
from learning_lab.vm_preview.registry import LEGACY_ID
import learning_lab.vm_preview.manager as controller


def write(path,value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


def host_preflight(evidence):
    if Path('/proc/1/comm').read_text().strip()!='systemd' or Path('/proc/2/comm').read_text().strip()!='kthreadd':
        raise RuntimeError('BLOCKED: reliable initial host PID namespace visibility is unavailable')
    found=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            comm=(p/'comm').read_text().strip()
            if comm.startswith('qemu-system'):found.append({'pid':int(p.name),'comm':comm})
        except FileNotFoundError:pass
        except PermissionError:raise RuntimeError('BLOCKED: incomplete process inventory')
    if found:raise RuntimeError('BLOCKED: an existing QEMU guest is present; no control sent')
    gate=Path(f'/run/user/{os.getuid()}/oll-vm-preview')
    # Read-only opens: never create, truncate, repair or remove owner's gate files.
    with Directory.absolute(gate) as directory:
        op=directory.open('operations.lock');life=directory.open('running.lock')
        try:
            fcntl.flock(op,fcntl.LOCK_EX|fcntl.LOCK_NB)
            fcntl.flock(life,fcntl.LOCK_EX|fcntl.LOCK_NB)
            raw=directory.read('running.json') if directory.exists('running.json') else None
            prior=json.loads(raw) if raw else None
            if prior and prior.get('state') not in ('unclean','stopped'):
                raise RuntimeError('BLOCKED: existing coordination is not terminal; no repair or overwrite attempted')
            if prior and prior.get('process') and Path('/proc',str(prior['process']['pid'])).exists():
                raise RuntimeError('BLOCKED: prior recorded process still exists; ownership requires review')
            write(evidence/'preflight.json',{'pid_namespace':os.readlink('/proc/self/ns/pid'),
                  'host_init':'systemd','kernel_thread_2':'kthreadd','existing_qemu':found,
                  'shared_exclusion_acquired':True,'previous_coordination_sha256':hashlib.sha256(raw).hexdigest() if raw else None,
                  'previous_coordination':prior})
        finally:os.close(life);os.close(op)
    # The unmodified Start reacquires both normal locks and passes its lifetime
    # lock descriptor to QEMU. No private native gate or lock bypass is used.
    return gate


def run(root,case,label=''):
    report_path=root/'evidence/report.json'
    accepted=json.loads(report_path.read_text());assert accepted['result']=='PASS' and not accepted['guest_started']
    evidence=root/'evidence'/component('native-'+case+('-'+label if label else ''));evidence.mkdir(mode=0o700)
    report={'case':case,'result':'BLOCKED','checks':[]};app=window=locks=None;m=None
    def check(name,condition):
        if not condition:raise AssertionError(name)
        report['checks'].append(name)
    try:
        gate=host_preflight(evidence)
        check('KVM access',os.access('/dev/kvm',os.R_OK|os.W_OK))
        app,engine,b,locks=build_application(root/'profile/data',root/'profile/config',root/'vm')
        window=engine.rootObjects()[0];vm=b.vm_preview
        check('native Wayland',app.platformName()=='wayland')
        check('native Lab exposed',QTest.qWaitForWindowExposed(window,10000))
        def pause(seconds):
            # QTest.qWait holds the Python GIL between event deliveries on this
            # PySide runtime. Yield explicitly so the real hashing/QMP worker
            # can progress; do not replace it or fabricate operation completion.
            until=time.monotonic()+seconds
            while time.monotonic()<until:app.processEvents();time.sleep(.03)
        def wait(allow_error=False):
            until=time.monotonic()+90
            while vm.view['busy'] and time.monotonic()<until:pause(.03)
            check('operation completed',not vm.view['busy'])
            if not allow_error:check('operation has no error',not vm.view['error'])
        def item(name):
            def visit(x):
                if x.objectName()==name and x.isVisible():return x
                for child in x.childItems():
                    value=visit(child)
                    if value is not None:return value
            value=visit(window.contentItem());assert value is not None,name;return value
        def press(name):
            control=item(name);check(name+' enabled',control.isEnabled())
            control.forceActiveFocus(Qt.TabFocusReason);QTest.keyClick(window,Qt.Key_Return);pause(.1)
        press('vmPreviewButton');wait();vm.selectLesson(LEGACY_ID);wait()
        m=vm.manager;check('normal shared gate',m.gate_root==gate)
        record_path=root/'vm/profiles'/m.profile/'current.json'
        before=record_path.read_bytes() if record_path.exists() else None
        check('fresh or reopened as requested',(before is None)==(case=='active'))
        press('vmStart');wait()
        with m.access() as (_,gd,p):
            r=m.reconcile(gd);session=m.current(p)
        check('real QEMU process identity',same_process(r));verify_launch(r,str(gate/r['run']/'qmp'))
        check('exact image pin',session['pin']['image']==image_spec())
        check('self-review not completed',session['completion'] is None)
        if before:check('same record on disk Resume',record_path.read_bytes()==before)
        before=record_path.read_bytes()
        report['runtime_before_stop']=copy.deepcopy(r);report['session_pin']=session['pin']
        # Give the unchanged guest time to reach its native console and logind.
        pause(15)
        clients=json.loads(subprocess.check_output(['/usr/bin/hyprctl','-j','clients']))
        guest=[c for c in clients if c.get('pid')==r['process']['pid']]
        check('native GTK guest window',len(guest)==1)
        c=guest[0];x,y=c['at'];width,height=c['size']
        subprocess.run(['/usr/bin/grim','-g',f'{x},{y} {width}x{height}',str(evidence/'guest.png')],check=True,timeout=15)
        report['guest_window']={k:c.get(k) for k in ('pid','class','size','at','xwayland')}
        if case=='withdrawn':m.catalog.images[digest(m.spec)]['state']='withdrawn'
        elif case=='missing-image':m.catalog.images.pop(digest(m.spec))
        elif case=='missing-lesson':m.catalog.lessons.pop((LEGACY_ID,m.pin['lesson_sha256']))
        check('availability change did not stop guest',same_process(r))
        other='real-linux-process-inspection'
        vm.selectLesson(other);wait(allow_error=True)
        check('running lesson remains identified',vm.view['running_lesson_id']==LEGACY_ID)
        check('second Start disabled',not item('vmStart').isEnabled())
        if case.startswith('missing-'):check('unavailable pin exposes control-only Stop',vm.view['running_state']=='control-only')
        window.grabWindow().save(str(evidence/'lab-before-stop.png'))
        shutdown=[]
        class ObservedQmp(Qmp):
            # Observation only: real constructor, peer/UUID checks and original
            # powerdown implementation run. No result or guest event fabricated.
            def powerdown(self,record,timeout=35):
                result=super().powerdown(record,timeout)
                shutdown.append({'clean':result,'events':copy.deepcopy(self.events),'process_exited':not same_process(record)})
                return result
        original=controller.Qmp;controller.Qmp=ObservedQmp
        try:press('vmStop');wait(allow_error=True)
        finally:controller.Qmp=original
        check('real guest SHUTDOWN and exit',len(shutdown)==1 and shutdown[0]['clean'] is True and shutdown[0]['process_exited'] and any(e.get('event')=='SHUTDOWN' and e.get('data',{}).get('guest') is True for e in shutdown[0]['events']))
        check('no remaining QEMU process',not same_process(r))
        report['shutdown']=shutdown
        with m.access() as (_,gd,p):
            final=m.record(gd);lifecycle=m.lifecycle(p,session['generation'])
        check('clean runtime and generation journals',final['state']=='stopped' and lifecycle=='stopped')
        check('pinned attempt bytes unchanged',record_path.read_bytes()==before)
        report['runtime_after_stop']=final;report['final_guest_state']='stopped cleanly'
        if case!='active':
            for name,action in (('Start',m.start),('Reset',lambda:m.reset(confirmed=True))):
                try:action()
                except ValueError as exc:report['checks'].append(name+' refused: '+str(exc))
                else:raise AssertionError(name+' incorrectly allowed unavailable/withdrawn pin')
            check('refusals preserve attempt',record_path.read_bytes()==before)
        check('production trust empty',not production_catalog().keys and not production_catalog().releases)
        window.grabWindow().save(str(evidence/'lab-after-stop.png'))
        report['result']='PASS'
    except BaseException as exc:
        report.update(result='BLOCKED' if app is None else 'FAIL',error=type(exc).__name__+': '+str(exc))
        # Never force-stop, repair, erase evidence or guess ownership on failure.
        report.setdefault('final_guest_state','not launched' if m is None else 'inspect retained evidence; no automatic force stop')
        raise
    finally:
        report['max_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
        write(evidence/'result.json',report)
        print(json.dumps(report,indent=2),flush=True)
        if app is not None:
            b.flush();window.close();app.processEvents();locks.unlock()
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--case',choices=('active','withdrawn','missing-image','missing-lesson'),required=True)
    p.add_argument('--run-label',default='',help='Unique suffix to retain previous attempt evidence')
    args=p.parse_args();run(args.root.absolute(),args.case,args.run_label)
