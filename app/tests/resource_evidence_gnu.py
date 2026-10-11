"""Static developer fixtures ONLY; no learner/imported input reaches GNU."""
import json
from pathlib import Path
import subprocess
import tempfile
from learning_lab.collections import load_collections
from learning_lab.linux_text.engine import TextEngine
# Fixed developer commands. Arguments are not obtained from lesson/user input.
FIXTURES=[('snapshot.txt',[['head','-n','5']], 'baseline.txt'),
 ('memory.txt',[['tail','-n','8']], 'memory-report.txt'),
 ('space.txt',[['tail','-n','2']], 'space-report.txt'),
 ('inodes.txt',[['tail','-n','2']], 'inode-report.txt'),
 ('history.txt',[['grep','-F','2026-'],['sort']], 'handover.txt')]
checks=[]
entries=load_collections()[4]['entries'];packs=[e['scenario'].value() for e in entries]
with tempfile.TemporaryDirectory() as temp:
 for source,stages,dest in FIXTURES:
  pack=next(p for p in packs if '/home/learner/'+source in p['domain']['filesystem'])
  data=pack['domain']['filesystem']['/home/learner/'+source]['content'].encode();states=[]
  for args in stages:
   result=subprocess.run(args,input=data,capture_output=True,env={'PATH':'/usr/bin','LC_ALL':'C','POSIXLY_CORRECT':'1'},timeout=5)
   assert result.returncode==0 and not result.stderr,(args,result.stderr)
   states.append({'argv':args,'status':result.returncode,'stderr':result.stderr.decode()});data=result.stdout
  expected=next(o['params']['content'].encode() for o in pack['objectives'] if o['predicate']=='file_content' and o['params']['path'].endswith('/'+dest))
  assert data==expected,(source,data,expected)
  # The trusted fixed command also runs through the simulator. Compare final bytes.
  command=' | '.join(' '.join(args)+(' '+source if i==0 else '') for i,args in enumerate(stages))+' > '+dest
  state,r=TextEngine(pack).run(command);assert r.status==0 and not r.errors
  actual=state['filesystem']['/home/learner/'+dest]['content'].encode();assert actual==data
  checks.append({'source':source,'stages':states,'stdout':data.decode(),'virtual_report':actual.decode()})
print(json.dumps({'result':'PASS','fixtures':len(checks),'checks':checks},indent=2))
