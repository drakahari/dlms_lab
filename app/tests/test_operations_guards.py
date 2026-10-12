"""Safe static developer shell stubs; no real guest command reaches the host."""
import subprocess,tempfile,unittest
from pathlib import Path
from operations_guest_fixtures import COMMANDS,DATA
class OperationGuards(unittest.TestCase):
 def run_stub(self,command,defs):
  with tempfile.TemporaryDirectory() as d:
   p=subprocess.run(['/usr/bin/bash','--noprofile','--norc','-c',defs+'; '+command+'; rc=$?; printf "STATUS=%s\\n" "$rc"'],cwd=d,env={'PATH':'/nonexistent','LC_ALL':'C'},capture_output=True,text=True,timeout=5)
   self.assertEqual(list(Path(d).iterdir()),[]);return p.stdout,p.stderr
 def test_cron_refused_workspace_cannot_install(self):
  c=COMMANDS['real-linux-operations-cronaccess']['commands'][2]
  for bad in ('here','fresh'):
   out,err=self.run_stub(c,'here() { return '+('19' if bad=='here' else '0')+'; }; fresh() { return '+('19' if bad=='fresh' else '0')+'; }; crontab() { echo INSTALLED; }; env() { echo "no crontab for learner"; return 1; }')
   self.assertEqual(out,'STATUS=19\n',err)
 def test_timer_refused_launch_cannot_use_old_wait(self):
  c=COMMANDS['real-linux-operations-timerresult']['commands'][2]
  for bad in ('here','launch'):
   out,err=self.run_stub(c,'here() { return '+('19' if bad=='here' else '0')+'; }; fresh() { return 0; }; sudo() { echo CALLED >&2; return 19; }; timer_wait() { echo OLD_WAIT; }')
   self.assertEqual(out,'STATUS=19\n',err);self.assertNotIn('OLD_WAIT',out)
 def test_account_repeat_refuses_before_writes(self):
  c=COMMANDS['real-linux-operations-accountfiles']['commands'][2]
  out,err=self.run_stub(c,'here() { return 0; }; fresh() { return 19; }')
  self.assertNotIn('WRITE_CALLED',out) # No redirected data file is opened.
  self.assertEqual(out,'STATUS=19\n',err)
 def test_private_job_edit_refuses_symlink(self):
  for c in COMMANDS['real-linux-operations-timerresult']['commands'][3:5]:
   out,err=self.run_stub(c,'here() { return 0; }; fresh() { return 0; }; test() { if builtin test "$1" = -f; then return 0; fi; if builtin test "$1" = "!" && builtin test "$2" = -L; then return 1; fi; return 19; }')
   self.assertEqual(out,'STATUS=1\n',err)
 def stop_stub(self,command,scenario):
  defs=r'''w=/home/learner/operations-timerresult.ABCDEF; unit=ll-ops-result-ABCDEF; here() { return 0; }; grep() { IFS= read -r line; test "$line" = "argv[]=/usr/bin/timeout -k 1s 6s /bin/sh $w/job.sh ;"; }; sudo() { shift; action=$1; shift; if test "$action" = stop; then echo STOP:$1; stopped=1; return 0; fi; name=$1; shift; prop=$2; case "$prop" in LoadState) if test "$SCENARIO" = queryerror; then echo loaded; return 19; elif test "${stopped:-0}" = 1; then echo not-found; elif test "$name" = "$unit.timer" && test "$SCENARIO" != wrongtimer && test "$SCENARIO" != loadedtimer; then echo not-found; else echo loaded; fi;; User) if test "$SCENARIO" = wronguser; then echo other; elif test "$SCENARIO" = userqueryerror; then echo learner; return 19; else echo learner; fi;; ExecStart) if test "$SCENARIO" = wrongargv; then echo "argv[]=/usr/bin/timeout -k 1s 6s /bin/sh $w/job.sh.other ;"; elif test "$SCENARIO" = wrongcmd; then echo 'argv[]=/bin/true ;'; else echo "argv[]=/usr/bin/timeout -k 1s 6s /bin/sh $w/job.sh ;"; fi;; Triggers) if test "$SCENARIO" = wrongtimer; then echo unrelated.service; else echo "$unit.service"; fi;; ActiveState) echo activating;; MainPID|ControlPID) echo 1;; *) return 19;; esac; }'''
  if scenario=='wrongname':defs+='; unit=unrelated'
  return self.run_stub(command,'SCENARIO='+scenario+'; '+defs)
 def test_collected_timer_does_not_block_owned_service_stop(self):
  command=COMMANDS['real-linux-operations-timerresult']['commands'][-1]
  out,err=self.stop_stub(command,'valid')
  self.assertEqual(out,'STOP:ll-ops-result-ABCDEF.service\nSTATUS=0\n',err)
 def test_unexpected_query_and_service_identity_refuse_stop(self):
  command=COMMANDS['real-linux-operations-timerresult']['commands'][-1]
  for case in ('queryerror','userqueryerror','wronguser','wrongargv','wrongcmd','wrongtimer','wrongname'):
   out,err=self.stop_stub(command,case);self.assertNotIn('STOP:',out);self.assertEqual(out,'STATUS=19\n',err)
 def test_loaded_timer_is_stopped_only_with_exact_association(self):
  c=COMMANDS['real-linux-operations-timerresult']['commands'][-1]
  out,err=self.stop_stub(c,'loadedtimer')
  self.assertEqual(out,'STOP:ll-ops-result-ABCDEF.timer\nSTOP:ll-ops-result-ABCDEF.service\nSTATUS=0\n',err)
 def test_cleanup_active_transition_or_remaining_pid_refuses_enumeration(self):
  c=COMMANDS['real-linux-operations-timerresult']['cleanup_command']
  for case in ('activating','deactivating','mainpid','controlpid','queryerror'):
   defs=r'''w=/home/learner/operations-timerresult.ABCDEF; unit=ll-ops-result-ABCDEF; here() { return 0; }; find() { echo ENUM_CALLED; }; rm() { echo DELETE_CALLED; }; rmdir() { echo DELETE_CALLED; }; sudo() { prop=$5; case "$prop" in LoadState) echo loaded; test "$SCENARIO" != queryerror;; ActiveState) case "$SCENARIO" in activating|deactivating) echo "$SCENARIO";; *) echo inactive;; esac;; MainPID) if test "$SCENARIO" = mainpid; then echo 1; else echo 0; fi;; ControlPID) if test "$SCENARIO" = controlpid; then echo 1; else echo 0; fi;; *) return 19;; esac; }'''
   out,err=self.run_stub(c,'SCENARIO='+case+'; '+defs)
   self.assertEqual(out,'STATUS=19\n',case+err)
 def test_rotation_retained_generation_blocks_repeat(self):
  c=COMMANDS['real-linux-operations-rotationfd']['commands'][2]
  out,err=self.run_stub(c,'here() { return 0; }; fresh() { return 19; }; timeout() { echo ROTATED; }')
  self.assertEqual(out,'STATUS=19\n',err)
 def test_displayed_cleanup_is_not_scheduler_mutation(self):
  cron=COMMANDS['real-linux-operations-cronaccess']['cleanup_command']
  self.assertNotIn('crontab -r',cron)
  timer=COMMANDS['real-linux-operations-timerresult']['cleanup_command']
  self.assertNotIn('systemctl stop',timer);self.assertIn('ControlPID',timer);self.assertIn('LoadState',timer)
 def test_notice_requires_actual_console_not_echoed_payload(self):
  x=COMMANDS['real-linux-operations-notices']
  self.assertNotIn('cat notice.txt',x['commands'][1]);self.assertIn("\\033[2J",x['commands'][2]);self.assertIn('sudo -n wall -n',x['commands'][2])

 def test_oversized_notice_refuses_before_sender_or_status_write(self):
  c=COMMANDS['real-linux-operations-notices']['commands'][2]
  defs="here() { return 0; }; test() { if builtin test \"$1\" = -f || { builtin test \"$1\" = '!' && builtin test \"$2\" = -L; }; then return 0; else builtin test \"$@\"; fi; }; stat() { case \"$2\" in %U:%a:%h) echo learner:600:1;; %s) echo 129;; *) return 19;; esac; }; timeout() { echo SENDER_CALLED; }"
  out,err=self.run_stub(c,defs)
  self.assertEqual(out,'STATUS=1\n',err)
  self.assertNotIn('SENDER_CALLED',out)

 def test_notice_status_symlink_refuses_before_sender_or_write(self):
  c=COMMANDS['real-linux-operations-notices']['commands'][2]
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);(d/'notice.txt').write_text('known\n');(d/'notice.txt').chmod(0o600)
   (d/'victim.txt').write_text('retained\n');(d/'sent.txt').symlink_to('victim.txt')
   defs='here() { return 0; }; stat() { case "$2" in %U:%a:%h) echo learner:600:1;; %s) echo 6;; *) return 19;; esac; }; wc() { echo 1; }; timeout() { echo SENDER_CALLED; }'
   v=subprocess.run(['/usr/bin/bash','--noprofile','--norc','-c',defs+'; '+c+'; rc=$?; printf "STATUS=%s\n" "$rc"'],cwd=d,env={'PATH':'/nonexistent','LC_ALL':'C'},capture_output=True,text=True,timeout=5)
   self.assertEqual(v.stdout,'STATUS=1\n',v.stderr);self.assertNotIn('SENDER_CALLED',v.stdout)
   self.assertTrue((d/'sent.txt').is_symlink());self.assertEqual((d/'victim.txt').read_text(),'retained\n');self.assertEqual((d/'notice.txt').read_text(),'known\n')

 def test_first_creation_guard_precedes_each_diagnostic_or_restore_write(self):
  cases={'timerresult':(2,3,4),'journalcursor':(2,3),'journalfields':(2,3),'rotationfd':(2,),'handover':(2,)}
  for slug,indices in cases.items():
   for i in indices:
    c=COMMANDS['real-linux-operations-'+slug]['commands'][i]
    out,err=self.run_stub(c,'here() { return 0; }; fresh() { return 19; }; sudo() { echo SIDE_EFFECT; }; logger() { echo SIDE_EFFECT; }; timeout() { echo SIDE_EFFECT; }')
    self.assertEqual(out,'STATUS=19\n',(slug,i,err));self.assertNotIn('SIDE_EFFECT',out)
