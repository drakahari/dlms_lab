import ast
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from learning_lab.domain.engine import Engine, load_pack, load_catalog
from learning_lab.domain.validation import ValidationError, prefix, settings
from learning_lab.session import Session, new_attempt
from learning_lab.storage import Store, encode, validate_record, atomic_write
from learning_lab.theme import FALLBACK, read_theme, contrast

PACK_PATH = Path(__file__).resolve().parents[1] / 'learning_lab/packs/gateway-dns.json'
RAW = PACK_PATH.read_bytes()
PACK = load_pack(RAW)
FIXED = {**PACK['initial_state']['WS-01'], 'gateway': '192.168.50.1', 'dns': '10.20.0.10'}

class NetworkTests(unittest.TestCase):
    def test_fault_matrix(self):
        for change, score, ip_ok, dns_ok in (({},40,False,False), ({'gateway':'192.168.50.1'},70,True,False), ({'dns':'10.20.0.10'},40,False,False), (FIXED,100,True,True)):
            with self.subTest(change=change):
                e = Engine(PACK, {**PACK['initial_state']['WS-01'], **change})
                self.assertEqual(e.reach('10.20.0.10').ok, ip_ok)
                self.assertEqual(e.resolve('portal.lab.test')[0].ok, dns_ok)
                self.assertEqual(e.grade()['score'], score)
                self.assertEqual(e.portal().ok, dns_ok)

    def test_local_router_and_unknown(self):
        e = Engine(PACK)
        self.assertTrue(e.reach('192.168.50.1').ok)
        self.assertFalse(e.reach('192.168.50.254').ok)
        self.assertIn('simulation', e.command('ping example.org'))
        self.assertIn('No known', e.command('ping 8.8.8.8'))

    def test_forward_and_return_paths(self):
        for mutation, word in ((lambda p: p['topology']['devices'][1].update(forwarding=False), 'forward'), (lambda p: p['topology']['devices'][2].update(gateway='10.20.0.99'), 'Return')):
            p = deepcopy(PACK); mutation(p)
            result = Engine(p,FIXED).reach('10.20.0.10')
            self.assertFalse(result.ok); self.assertIn(word,result.message)

    def test_constraints_allow_functional_but_wrong_state(self):
        for change in ({'address':'192.168.50.21'}, {'prefix':16}):
            e = Engine(PACK,{**FIXED,**change})
            self.assertTrue(e.portal().ok)
            self.assertEqual(e.grade()['score'],80)
            self.assertFalse(e.grade()['complete'])

    def test_alternative_dns_when_pack_permits(self):
        p = deepcopy(PACK)
        server = deepcopy(p['topology']['devices'][2])
        server['id'] = 'DNS-02'; server['interfaces'][0]['address'] = '10.20.0.11'
        server['endpoints'] = []; p['topology']['devices'].append(server)
        p = load_pack(json.dumps(p))
        self.assertEqual(Engine(p,{**FIXED,'dns':'10.20.0.11'}).grade()['score'],100)

    def test_ip_hostname_and_service_boundary(self):
        e = Engine(PACK,FIXED)
        self.assertIn('reply',e.command('ping portal.lab.test'))
        self.assertIn('resolves',e.command('nslookup PORTAL.LAB.TEST.'))
        self.assertIn('RTR-01',e.command('traceroute 10.20.0.10'))
        self.assertIn('not validated',e.portal().message)
        self.assertIn('unsupported',e.command('connect portal.lab.test 443'))

class ValidationTests(unittest.TestCase):
    def test_mask_formats(self):
        for value in (24,'24','/24','255.255.255.0'):
            self.assertEqual(prefix(value),24)
        for value in ('255.0.255.0','0.0.0.255','255.255.255.255','/33',True,24.5,'NaN','0'):
            with self.subTest(value=value), self.assertRaises(ValidationError): prefix(value)

    def test_invalid_host_addresses(self):
        for ip in ('192.168.50.0','192.168.50.255','999.1.2.3','224.0.0.1','127.0.0.1','0.0.0.0'):
            with self.subTest(ip=ip),self.assertRaises(ValidationError): settings({**FIXED,'address':ip})

    def test_bad_packs(self):
        mutations = [lambda p:p.update(schema_version=2), lambda p:p.update(required_capabilities=['shell']),
          lambda p:p.update(hints=['one']), lambda p:p.update(extra='evil'),
          lambda p:p['topology']['devices'][0]['interfaces'][0].update(segment='missing'),
          lambda p:p['topology']['devices'][0]['interfaces'][0].update(prefix=33),
          lambda p:p['topology']['devices'][1].update(id='WS-01'),
          lambda p:p['objectives'][0].update(predicate='eval'),
          lambda p:p['objectives'][2]['params'].update(target='8.8.8.8'),
          lambda p:p['objectives'][0].update(points=99),
          lambda p:p['topology']['devices'][1].update(forwarding=False),
          lambda p:p['metadata'].update(brief='x'*16385)]
        for change in mutations:
            p=deepcopy(PACK); change(p)
            with self.subTest(change=change),self.assertRaises(ValidationError): load_pack(json.dumps(p))
        for raw in ('{','{"a":1,"a":2}','[]','{"a":NaN}', ' '*262145):
            with self.subTest(raw=raw[:30]),self.assertRaises(ValidationError): load_pack(raw)
        with self.assertRaises(ValidationError): load_catalog([RAW,RAW])

    def test_structural_fuzz(self):
        for field in PACK:
            for value in (None, [], {}, 123, True):
                p=deepcopy(PACK); p[field]=value
                with self.subTest(field=field,value=value),self.assertRaises(ValidationError): load_pack(json.dumps(p))

    def test_nested_structural_fuzz(self):
        for location in ('device','interface','objective','parameters'):
            for value in (None, [], {}, True, 12):
                p=deepcopy(PACK)
                if location=='device':p['topology']['devices'][0]['id']=value
                elif location=='interface':p['topology']['devices'][0]['interfaces'][0]['segment']=value
                elif location=='objective':p['objectives'][0]['predicate']=value
                else:p['objectives'][2]['params']['target']=value
                with self.subTest(location=location,value=value),self.assertRaises(ValidationError):load_pack(json.dumps(p))

class SafetyTests(unittest.TestCase):
    def test_hostile_commands_and_bounded_output(self):
        e=Engine(PACK,FIXED)
        commands=['ping 10.20.0.10; touch /tmp/pwn', '$(id)', '`id`', 'ping x | sh', 'ping x\nsh', 'rm -rf /', 'python -c x', 'curl https://x', 'ping -c 1 10.20.0.10', '../../etc/passwd','a'*513]
        for command in commands:
            with self.subTest(command=command):
                result=e.command(command)
                self.assertLess(len(result),1000)
                self.assertTrue('simulation' in result.lower() or 'limit' in result.lower())

    def test_engine_cannot_call_host_executors_or_network(self):
        import socket, subprocess, os
        with patch.object(socket,'socket',side_effect=AssertionError('network')), patch.object(subprocess,'Popen',side_effect=AssertionError('process')), patch.object(os,'system',side_effect=AssertionError('shell')):
            e=Engine(PACK,FIXED)
            for command in ('help','ipconfig','ip addr','ip route','ping 10.20.0.10','ping portal.lab.test','nslookup portal.lab.test','traceroute 10.20.0.10','$(id)'):
                e.command(command)
            e.grade()
        allowed={'copy','dataclasses','ipaddress','re','json','validation','firewall'}
        for path in (PACK_PATH.parent.parent/'domain').glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node,ast.Import): self.assertTrue(all(n.name.split('.')[0] in allowed for n in node.names))
                if isinstance(node,ast.ImportFrom): self.assertIn(node.module.split('.')[0],allowed)
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name): self.assertNotIn(node.func.id, {'eval','exec','compile','__import__','open'})

class SessionTests(unittest.TestCase):
    def test_apply_atomicity_and_draft_grading(self):
        s=Session(PACK); baseline=deepcopy(s.attempt['applied'])
        s.edit('gateway','192.168.50.1'); s.edit('prefix','255.0.255.0')
        with self.assertRaises(ValidationError):s.apply()
        self.assertEqual(s.attempt['applied'],baseline); self.assertEqual(s.attempt['revision'],0)
        self.assertEqual(s.submit()['score'],40)
        s.test(); self.assertIn('drafts', '\n'.join(s.attempt['console']))
        s.edit('prefix','255.255.255.0'); s.apply()
        self.assertEqual(s.attempt['revision'],1); self.assertEqual(s.submit()['score'],70)
        self.assertEqual(s.attempt['draft'],{})

    def test_duplicate_submission_and_hints(self):
        s=Session(PACK); s.hint(); s.hint(); s.hint(); s.hint()
        self.assertEqual(s.attempt['hints'],3)
        for k,v in FIXED.items():s.edit(k,str(v))
        s.apply(); first=s.submit(); self.assertEqual(first,s.submit())
        self.assertEqual(first['score'],100); self.assertEqual(first['hints_at_submission'],3)
        self.assertEqual(len(s.attempt['assessments']),1)
        s.apply(); self.assertEqual(s.attempt['revision'],1)
        s.edit('dns','10.20.0.99'); s.apply(); s.submit()
        self.assertEqual(len(s.attempt['assessments']),2)

    def test_archive_and_fresh_mode(self):
        s=Session(PACK); s.hint(); s.edit('dns','10.20.0.10'); s.execute('help'); s.submit()
        archived=s.archived('mode-change'); fresh=new_attempt(PACK,'Challenge')
        self.assertNotEqual(archived['id'],fresh['id']); self.assertEqual(archived['hints'],1)
        self.assertTrue(archived['draft']); self.assertTrue(archived['console']); self.assertTrue(archived['assessments'])
        self.assertEqual((fresh['hints'],fresh['draft'],fresh['console']),(0,{},[]))
        with self.assertRaises(ValidationError):Session(PACK,fresh).hint()

    def test_console_limits(self):
        s=Session(PACK)
        for _ in range(260):s.execute('ipconfig')
        self.assertLessEqual(len(s.attempt['console']),500);self.assertEqual(len(s.attempt['commands']),100)
        s.execute('clear');self.assertEqual(s.attempt['console'],[])

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store=Store(self.tmp.name,PACK);self.a=new_attempt(PACK)

    def test_roundtrip_drafts_and_submission(self):
        s=Session(PACK);s.hint();s.edit('dns','bad draft');s.submit()
        self.store.save(s.attempt); self.assertEqual(self.store.load(),s.attempt)

    def test_backup_corruption_recovery(self):
        self.store.save(self.a); old=deepcopy(self.a);self.a['hints']=1;self.store.save(self.a)
        self.store.current.write_text('{broken')
        self.assertEqual(self.store.load(),old)
        self.assertIn('Recovered',self.store.notice)
        self.assertEqual(len(list(self.store.root.glob('current.corrupt-*'))),1)
        self.assertEqual(next(self.store.root.glob('current.corrupt-*')).read_text(),'{broken')

    def test_both_corrupt_readonly(self):
        self.store.current.write_text('bad');self.store.backup.write_text('also bad')
        self.assertIsNone(self.store.load());self.assertTrue(self.store.read_only)
        self.assertEqual(self.store.current.read_text(),'bad')
        with self.assertRaises(ValidationError):self.store.save(self.a)

    def test_newer_schema_preserved_even_with_good_backup(self):
        self.store.save(self.a);self.store.save(self.a)
        raw=json.dumps({'schema_version':2,'future':'keep me'})
        self.store.current.write_text(raw)
        self.assertIsNone(self.store.load());self.assertTrue(self.store.read_only)
        self.assertEqual(self.store.current.read_text(),raw)

    def test_unsupported_schema_and_pack_version(self):
        for field,value in (('schema_version',0),('content_version','9.0.0')):
            data=json.loads(encode(self.a))
            if field=='schema_version':data[field]=value
            else:data['attempt'][field]=value
            self.store.current.write_text(json.dumps(data))
            store=Store(self.tmp.name,PACK);self.assertIsNone(store.load());self.assertTrue(store.read_only)

    def test_archive_no_pruning_and_paging(self):
        for _ in range(32):
            a=Session(PACK).archived('reset');self.store.archive(a)
        rows,count,warnings=self.store.history(self.a['id'],0)
        self.assertEqual((len(rows),count,warnings),(25,32,[]))
        self.assertEqual(len(self.store.history(self.a['id'],1)[0]),7)
        self.store.save(self.a);self.assertEqual(len(list(self.store.archives.glob('*.json'))),32)

    def test_atomic_replace_failure_preserves_previous(self):
        self.store.save(self.a);before=self.store.current.read_bytes()
        with patch('learning_lab.storage.os.replace',side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):atomic_write(self.store.current,b'broken')
        self.assertEqual(self.store.current.read_bytes(),before)
        self.assertFalse(list(self.store.root.glob('.current.json.*')))

    def test_tampered_score_rejected(self):
        s=Session(PACK);s.submit();s.attempt['assessments']['0']['score']=100
        with self.assertRaises(ValidationError):validate_record(encode(s.attempt),PACK)

    def test_missing_current_recovers_backup(self):
        self.store.save(self.a);self.store.current.unlink()
        self.assertEqual(self.store.load(),self.a)
        self.assertIn('missing',self.store.notice)

    def test_malformed_record_structures(self):
        for field in self.a:
            for value in ([], {}, 1):
                a=deepcopy(self.a);a[field]=value
                if a==self.a or (field=='revision' and value==1) or (field=='hints' and value==1):continue
                with self.subTest(field=field,value=value),self.assertRaises(ValidationError):validate_record(encode(a),PACK)

class ThemeTests(unittest.TestCase):
    def test_fallbacks_and_contrast(self):
        self.assertEqual(read_theme('/does/not/exist')[0],FALLBACK)
        self.assertEqual(read_theme(force_fallback=True)[0],FALLBACK)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'colors.toml'
            for raw in ('bad toml','background="javascript:evil"','x'*65537):
                p.write_text(raw);self.assertEqual(read_theme(p)[0],FALLBACK)
        for role in ('foreground','muted','accent','success','danger'):
            for bg in ('background','surface'):self.assertGreaterEqual(contrast(FALLBACK[role],FALLBACK[bg]),4.5)

if __name__=='__main__':unittest.main()
