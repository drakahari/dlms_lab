"""Developer-only GNU fixtures. No shell; never a learner execution path.

Validates text selection/status/output only, NOT ip/dig/curl/HTTP/TLS behavior.
"""
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from learning_lab.collections import load_collections
CASES={
'linux-network-interface-evidence':[['head','-n','4']],
'linux-network-route-evidence':[['head','-n','5']],
'linux-network-name-evidence':[['head','-n','4']],
'linux-network-incident-evidence':[['grep','-F','incident=NET-7'],['sort']],
'linux-dns-response-evidence':[['head','-n','6']],
'linux-dns-zone-evidence':[['head','-n','7']],
'linux-dns-consistency-evidence':[['head','-n','6']],
'linux-dns-handover-evidence':[['grep','-F','incident=DNS-9'],['sort']],
'linux-web-listener-evidence':[['head','-n','5']],
'linux-web-vhost-evidence':[['head','-n','5']],
'linux-web-tls-evidence':[['head','-n','6']],
'linux-web-proxy-evidence':[['grep','-F','incident=WEB-4'],['sort']],
}
results=[]
for c in load_collections():
 for e in c['entries']:
  v=e['scenario'].value();name=v['identity']['id']
  if name not in CASES:continue
  data=v['domain']['filesystem']['/home/learner/evidence.txt']['content'].encode()
  stages=[]
  for argv in CASES[name]:
   p=subprocess.run(argv,input=data,capture_output=True,timeout=5,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'})
   assert p.returncode==0 and not p.stderr,(name,argv,p.returncode,p.stderr)
   data=p.stdout;stages.append({'argv':argv,'exit':p.returncode,'stderr':p.stderr.decode()})
  expected=v['objectives'][0]['params']['content'].encode();assert data==expected,name
  s=e['scenario'].domain().session();s.execute(v['domain']['lesson']['steps'][0]['command'])
  assert s.attempt['applied']['filesystem']['/home/learner/report.txt']['content'].encode()==data,name
  results.append({'id':name,'stages':stages,'output':data.decode(),'virtual_report_matches':True})
assert len(results)==12
print(json.dumps({'result':'PASS','cases':results,'scope':'GNU text fixtures only; network/DNS/HTTP/TLS excerpts reviewed against official manuals'},indent=2))
