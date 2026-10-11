"""Content-only factual reports; no assessment of free-form reasoning."""
from copy import deepcopy
import hashlib,json,subprocess,sys,tempfile,unittest,shutil
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios,ProfileLocks
from learning_lab.catalog import CatalogBridge
from learning_lab.collections import load_collections
from learning_lab.domain.validation import ValidationError
from learning_lab.linux_text.engine import guide
from learning_lab import profile_backup as pb
APP=QCoreApplication.instance() or QCoreApplication([])
ROOT=Path(__file__).resolve().parents[1]
UNITS=[c for c in load_collections() if c['id'] in ('lpic-network-evidence','lpic-dns-evidence','lpic-web-evidence')]
ENTRIES=[e for c in UNITS for e in c['entries']]
def alternative(s):
 command=s.pack['domain']['lesson']['steps'][0]['command']
 return 'cat ./evidence.txt | '+command.replace(' evidence.txt','').replace('> report.txt','> /home/learner/report.txt')
def finish(s):
 for _ in range(64):
  if s.engine.grade()['complete']:return
  s.execute(guide(s.pack,s.attempt['applied'])['command'])
 raise AssertionError(s.attempt['console'])
class OfflineEvidenceTests(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.bridges=[];self.locks=[]
 def tearDown(self):
  for b in self.bridges:
   for lab in b.labs.values():lab.timer.stop()
  for lock in self.locks:lock.unlock()
  self.temp.cleanup()
 def build(self,name='profile'):
  p=self.root/name;(p/'config').mkdir(parents=True,exist_ok=True)
  b=CatalogBridge(load_bundled_scenarios()[0],p/'data',p/'config');self.bridges.append(b);return b
 def test_registration_checker_ceiling_and_unchanged_vm_bounds(self):
  self.assertTrue(UNITS);self.assertEqual(len(load_collections()),5+len(UNITS));b=self.build();self.assertEqual(len(b.curated),26+4*len(UNITS));self.assertFalse(b.repository.root.exists())
  from learning_lab.vm_preview.registry import units,entries
  self.assertEqual((len(units()),len(entries())),(11,94));ids=[]
  for unit in UNITS:
   self.assertEqual(len(unit['entries']),4)
   for e in unit['entries']:
    s=e['scenario'];v=s.value();ids.append(s.identity.scenario_id)
    self.assertEqual(v['engine']['contract_version'],5);self.assertEqual(v['domain']['output_files'],['/home/learner/report.txt'])
    self.assertEqual([(o['predicate'],o['points']) for o in v['objectives']],[('file_content',80),('stream_observed',20)])
    self.assertEqual(v['objectives'][1]['params']['source'],'/home/learner/report.txt')
    self.assertIn('Self-review',v['mission']['brief']);h=v['domain']['filesystem']['/home/learner/HELP.txt']['content']
    for text in ('SIMULATOR / OFFLINE SNAPSHOTS','Model interpretation:','Common mistakes:','not keyword graded','not normalized','not your computer'):self.assertIn(text,h)
    self.assertGreater(len(v['objectives'][0]['params']['content'].splitlines()),2)
  self.assertEqual(len(ids),len(set(ids)))
 def test_both_modes_alternatives_hints_and_no_rote_source_reading(self):
  for e in ENTRIES:
   with self.subTest(lab=e['scenario'].identity.scenario_id):
    s=e['scenario'].domain().session();s.hint();finish(s);self.assertEqual(s.submit()['score'],100);self.assertEqual(s.attempt['hints'],1)
    s=e['scenario'].domain().session(mode='Challenge');self.assertEqual(s.domain.view_state(s,None,0)['guide'],{})
    with self.assertRaises(ValidationError):s.hint()
    s.execute(alternative(s));self.assertEqual(s.submit()['score'],80)
    s.execute('cat ./report.txt');self.assertEqual(s.submit()['score'],100)
 def test_wrong_incomplete_empty_retry_and_last_write_reading(self):
  for e in ENTRIES:
   s=e['scenario'].domain().session(mode='Challenge');self.assertEqual(s.submit()['score'],0)
   for command in ['head -n 1 evidence.txt > report.txt','tail -n 1 evidence.txt > report.txt',"grep -F 'NO SUCH RECORD' evidence.txt > report.txt"]:
    s.execute(command);s.execute('cat report.txt');self.assertEqual(s.submit()['score'],0)
   finish(s);self.assertEqual(s.submit()['score'],100);s.execute(alternative(s));self.assertEqual(s.submit()['score'],80)
   s.execute('head -n 99 report.txt');self.assertEqual(s.submit()['score'],80);s.execute('cat report.txt');self.assertEqual(s.submit()['score'],100)
 def test_source_and_output_isolation_no_host_effects(self):
  for e in ENTRIES:
   s=e['scenario'].domain().session();initial=deepcopy(s.attempt['applied']['filesystem'])
   with patch('subprocess.Popen',side_effect=AssertionError('host execution')),patch('socket.socket',side_effect=AssertionError('network')):
    for c in ['ip address','dig example.test','curl http://192.0.2.1','cat /etc/passwd','cat evidence.txt > ../report.txt','cat evidence.txt > reference.txt','cat evidence.txt > /tmp/escape','cat evidence.txt | sh','cat evidence.txt; id','cat evidence.txt > HELP.txt']:s.execute(c)
    self.assertEqual(s.attempt['applied']['filesystem'],initial);finish(s)
   for path,node in initial.items():self.assertEqual(s.attempt['applied']['filesystem'][path],node)
 def test_reset_modes_history_and_profile_isolation(self):
  b=self.build();other=self.build('other')
  for e in ENTRIES:
   b.selectLab(e['scenario'].key,True);initial=deepcopy(b.session.attempt['applied']);finish(b.session);b.submit();old=b.session.attempt['id'];b.restart('Challenge')
   self.assertEqual(b.session.attempt['applied'],initial);self.assertIn(old,[x['id'] for x in b.store.history(b.session.attempt['id'])[0]])
   finish(b.session);b.submit();done=b.session.attempt['id'];b.restart('Challenge');self.assertEqual(b.session.attempt['applied'],initial);self.assertIn(done,[x['id'] for x in b.store.history(b.session.attempt['id'])[0]])
   other.selectLab(e['scenario'].key,True);self.assertEqual(other.session.attempt['applied'],initial)
 def test_separate_process_resume_exact_incomplete_challenge_drafts_and_bytes(self):
  b=self.build()
  for e in ENTRIES:
   b.selectLab(e['scenario'].key,True);finish(b.session);b.submit();b.restart('Challenge');b.execute(alternative(b.session));b.submit();b.setCommandDraft('cat report.txt');b.flush()
  (self.root/'expected.json').write_text(json.dumps({k:l.session.attempt for k,l in b.labs.items()}));before={p:p.read_bytes() for p in (self.root/'profile').rglob('*.json')}
  code='''import json,sys
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
app=QCoreApplication([]);r=Path(sys.argv[1]);b=CatalogBridge(load_bundled_scenarios()[0],r/'profile/data',r/'profile/config')
assert {k:l.session.attempt for k,l in b.labs.items()}==json.loads((r/'expected.json').read_text())
assert b.view['commandDraft']=='cat report.txt' and b.view['grade']['score']==80
for l in b.labs.values():l.timer.stop()
print('Exact pinned incomplete Challenge resume PASS')
'''
  r=subprocess.run([sys.executable,'-B','-c',code,str(self.root)],cwd=ROOT,capture_output=True,text=True,timeout=30);self.assertEqual(r.returncode,0,r.stderr)
  for p,data in before.items():self.assertEqual(p.read_bytes(),data)
 def test_export_reimport_backup_visibility_and_older_pin(self):
  b=self.build();lock=ProfileLocks(b.data_root,b.config_root);b.profile_locks=lock;self.locks.append(lock)
  for e in ENTRIES:
   lab=e['scenario'];b.selectLab(lab.key,True);finish(b.session);b.submit();b.flush();before=deepcopy(b.session.attempt)
   p=self.root/(lab.identity.scenario_id+'.lab.json');self.assertTrue(b.exportScenario(str(p)));self.assertEqual(p.read_bytes(),lab.original_bytes);self.assertTrue(b.importPack(str(p)));self.assertEqual(b.session.attempt,before)
   other=self.build(lab.identity.scenario_id);self.assertTrue(other.importPack(str(p)));other.selectLab(lab.key,True);finish(other.session);other.submit();self.assertEqual(other.view['grade']['score'],100)
  v=ENTRIES[0]['scenario'].value();v['identity']['content_version']='0.9.0';old,_=b.repository.install(json.dumps(v).encode());b._add_portable(old);b.selectLab(old.key,True);b.execute('pwd');b.flush()
  b.setLibraryState(ENTRIES[-1]['scenario'].key,'hidden');expected={k:deepcopy(l.session.attempt) for k,l in b.labs.items()};p=self.root/'profile.llbackup';self.assertTrue(b.backupProfile(str(p)),b.transfer_message)
  pb.restore(pb.read_backup(p),self.root/'restored',confirmed=True);restored=self.build('restored');self.assertEqual({k:l.session.attempt for k,l in restored.labs.items()},expected);self.assertEqual(restored.visibility.entries,b.visibility.entries)
 def test_prior_application_bytes_or_exact_authorized_presentation(self):
  from local_shell_preservation import projection
  base='1201aaa69d409f765d54e81cf8ce0b42e35560ca'
  for name in subprocess.check_output(['git','ls-tree','-r','--name-only',base,'app/learning_lab'],cwd=ROOT.parent).decode().splitlines():
   if name=='app/learning_lab/qml/Main.qml':
    from presentation_revision import MAIN_SHA256
    self.assertEqual(hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest(),MAIN_SHA256,name)
   elif name!='app/learning_lab/collections/index.json':self.assertEqual(projection(name,(ROOT.parent/name).read_bytes()),projection(name,subprocess.check_output(['git','show',base+':'+name],cwd=ROOT.parent)),name)

 def test_exact_approved_registration_bounds_and_reserved_evidence(self):
  expected=['linux-network-interface-evidence','linux-network-route-evidence','linux-network-name-evidence','linux-network-incident-evidence','linux-dns-response-evidence','linux-dns-zone-evidence','linux-dns-consistency-evidence','linux-dns-handover-evidence','linux-web-listener-evidence','linux-web-vhost-evidence','linux-web-tls-evidence','linux-web-proxy-evidence']
  self.assertEqual([e['scenario'].identity.scenario_id for e in ENTRIES],expected)
  self.assertEqual(len(load_collections()),8)
  resources=self.root/'resources';shutil.copytree(ROOT/'learning_lab/collections',resources/'collections');p=resources/'collections/index.json';value=json.loads(p.read_text());self.assertLess(len(p.read_bytes()),65536)
  extra=deepcopy(value['collections'][-1]);extra['id']='overflow';value['collections'].append(extra);p.write_text(json.dumps(value))
  with patch('learning_lab.collections.files',return_value=resources),self.assertRaises(ValidationError):load_collections()
  for e in ENTRIES:
   v=e['scenario'].value()
   for node in v['domain']['filesystem'].values():
    self.assertLessEqual(len(node['content'].encode()),8192)
    self.assertNotIn('BEGIN PRIVATE KEY',node['content'])
   self.assertIn('synthetic',v['objectives'][0]['params']['content'] if e['scenario'].identity.scenario_id.endswith(('interface-evidence','route-evidence','name-evidence','response-evidence','zone-evidence','consistency-evidence','listener-evidence','vhost-evidence','tls-evidence')) else v['domain']['filesystem']['/home/learner/reference.txt']['content'].lower())
 def test_factual_semantics_and_no_causal_grading(self):
  packs={e['scenario'].identity.scenario_id:e['scenario'].value() for e in ENTRIES}
  route=packs['linux-network-route-evidence']['objectives'][0]['params']['content'];self.assertIn('not attempted after failed lookup',route);self.assertIn('HTTP=503|curl without --fail exit=0',route)
  dns=packs['linux-dns-response-evidence']['objectives'][0]['params']['content'];self.assertIn('NOERROR|flags=qr aa|ANSWER=0|authority=example.test SOA',dns);self.assertIn('no response|RCODE=unavailable',dns)
  cache=packs['linux-dns-handover-evidence']['objectives'][0]['params']['content'];self.assertIn('09:30:00Z',cache);self.assertIn('09:33:00Z',cache);self.assertEqual(300-180,120);self.assertIn('remaining TTL=120 seconds',cache)
  tls=packs['linux-web-tls-evidence'];self.assertIn('-verify_return_error',tls['domain']['filesystem']['/home/learner/reference.txt']['content']);self.assertIn('portal name=absent',tls['objectives'][0]['params']['content'])
  proxy=packs['linux-web-proxy-evidence']['objectives'][0]['params']['content'];self.assertEqual(proxy,''.join(sorted(proxy.splitlines(keepends=True))))
  for v in packs.values():self.assertEqual(len(v['objectives']),2);self.assertEqual(v['objectives'][1]['params']['tool'],'cat')
