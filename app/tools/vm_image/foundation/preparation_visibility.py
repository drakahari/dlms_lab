"""Developer preparation visibility only; never used by the application controller."""
import os,pathlib,subprocess

def require_no_guest():
 uid=os.getuid()
 # User systemd may retain CAP_SYS_RESOURCE and consequently be non-dumpable.
 # Read the authoritative system-manager record for that one known executable.
 result=subprocess.run(["/usr/bin/systemctl","show",f"user@{uid}.service","--property=MainPID","--property=ExecStart","--property=FragmentPath","--property=PAMName"],capture_output=True,text=True,check=True,timeout=5,env={"PATH":"/usr/bin:/bin","LC_ALL":"C"})
 if len(result.stdout)>16384:raise RuntimeError("Oversized manager identity response")
 values=dict(line.split("=",1) for line in result.stdout.splitlines() if "=" in line)
 manager=int(values.get("MainPID","0"))
 manager_start=None
 if manager:
  try:manager_start=(pathlib.Path(f"/proc/{manager}/stat").read_text().rsplit(")",1)[1].split())[19]
  except (FileNotFoundError,ProcessLookupError):pass
 trusted_manager=(values.get("FragmentPath")=="/usr/lib/systemd/system/user@.service" and values.get("PAMName")=="systemd-user" and values.get("ExecStart","").startswith("{ path=/usr/lib/systemd/systemd ; argv[]=/usr/lib/systemd/systemd --user ;"))
 classified=[]
 for p in pathlib.Path("/proc").iterdir():
  if not p.name.isdigit():continue
  try:
   owner=p.stat().st_uid
   comm=(p/"comm").read_text().strip()
   if owner==uid:
    try:exe=os.readlink(p/"exe")
    except PermissionError:
     group=(p/"cgroup").read_text()
     expected_group=f"0::/user.slice/user-{uid}.slice/user@{uid}.service/init.scope\n"
     before=(p/"stat").read_text().rsplit(")",1)[1].split()[19]
     status=dict(line.split(":",1) for line in (p/"status").read_text().splitlines() if ":" in line)
     is_manager=int(p.name)==manager and comm=="systemd" and before==manager_start
     is_pam=comm=="(sd-pam)" and int(status["PPid"].strip())==manager
     if trusted_manager and group==expected_group and (is_manager or is_pam):
      if (p/"stat").read_text().rsplit(")",1)[1].split()[19]!=before:raise RuntimeError("Protected service PID changed")
      classified.append((p,before,comm,status["PPid"].strip()))
      continue
     raise RuntimeError("Uncertain same-user process identity: "+p.name)
    if pathlib.Path(exe).name.startswith("qemu-system"):raise RuntimeError("Existing guest: leave untouched: "+p.name)
   elif comm.startswith("qemu-system"):
    raise RuntimeError("Other-user guest ownership uncertain: "+p.name)
  except (FileNotFoundError,ProcessLookupError):pass
 if classified:
  again=subprocess.run(["/usr/bin/systemctl","show",f"user@{uid}.service","--property=MainPID","--property=ExecStart","--property=FragmentPath","--property=PAMName"],capture_output=True,text=True,check=True,timeout=5,env={"PATH":"/usr/bin:/bin","LC_ALL":"C"})
  if again.stdout!=result.stdout or pathlib.Path(f"/proc/{manager}/stat").read_text().rsplit(")",1)[1].split()[19]!=manager_start:raise RuntimeError("User manager changed during visibility check")
  if sum(comm=="(sd-pam)" for _,_,comm,_ in classified)>1:raise RuntimeError("Ambiguous PAM helper identity")
  for p,start,comm,parent in classified:
   status=dict(line.split(":",1) for line in (p/"status").read_text().splitlines() if ":" in line)
   if p.stat().st_uid!=uid or (p/"stat").read_text().rsplit(")",1)[1].split()[19]!=start or (p/"comm").read_text().strip()!=comm or status["PPid"].strip()!=parent or (p/"cgroup").read_text()!=f"0::/user.slice/user-{uid}.slice/user@{uid}.service/init.scope\n":raise RuntimeError("Protected service identity changed")
 return {"nonclassified_same_user_executables_checked":True,"authoritative_user_manager_pid":manager,"corroborated_systemd_pam_classification":[int(p.name) for p,_,_,_ in classified]}
