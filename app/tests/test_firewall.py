from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication
from learning_lab.domain.engine import Engine, load_pack, load_catalog
from learning_lab.domain.firewall import Policy, policy, MAX_RULES
from learning_lab.domain.validation import ValidationError, initial_applied
from learning_lab.session import Session
from learning_lab.storage import Store, encode, validate_record
from learning_lab.catalog import CatalogBridge
from test_lab import PACK, RAW, FIXED
from test_subnet import SUB, SUB_RAW

APP=QCoreApplication.instance() or QCoreApplication([])
FW_RAW=(Path(__file__).resolve().parents[1]/'learning_lab/packs/service-firewall.json').read_bytes()
FW=load_pack(FW_RAW)


def rule(name='narrow', action='allow', source='192.168.50.20/32', destination='10.20.0.10/32', port=443):
    return {'id':name,'action':action,'protocol':'tcp','source':source,'destination':destination,'port':port}


def state(rules=None, default='deny'):
    return {**initial_applied(FW),'firewall':{'default':default,'rules':[rule()] if rules is None else rules}}


class FirewallEngineTests(unittest.TestCase):
    def test_baseline_dns_ping_tcp_differ(self):
        e=Engine(FW)
        self.assertTrue(e.reach('10.20.0.10').ok);self.assertTrue(e.portal().ok)
        self.assertTrue(e.resolve('portal.lab.test')[0].ok)
        denied=e.connect('portal.lab.test',443)
        self.assertFalse(denied.ok);self.assertEqual(denied.kind,'policy-deny')
        self.assertIn('rule 1 [block-portal]',denied.message)
        self.assertIn('default policy deny',e.connect('10.20.0.10',22).message)
        self.assertEqual(e.grade()['score'],40)

    def test_first_match_order_and_named_evidence(self):
        deny=rule('deny-first','deny')
        for rules,allowed,identifier in (([deny,rule()],False,'deny-first'),([rule(),deny],True,'narrow')):
            with self.subTest(rules=rules):
                e=Engine(FW,state(rules));r=e.connect('portal.lab.test',443)
                self.assertEqual(r.ok,allowed);self.assertIn('rule 1 ['+identifier+']',r.message)

    def test_source_destination_port_matching(self):
        p=Policy({'default':'deny','rules':[rule(source='192.168.50.16/28',destination='10.20.0.0/24')]})
        for src,dst,port,expected in [('192.168.50.20','10.20.0.10',443,True),('192.168.50.16','10.20.0.0',443,True),('192.168.50.31','10.20.0.255',443,True),('192.168.50.15','10.20.0.10',443,False),('192.168.50.32','10.20.0.10',443,False),('192.168.50.20','10.20.1.10',443,False),('192.168.50.20','10.20.0.10',22,False)]:
            with self.subTest(src=src,dst=dst,port=port):self.assertEqual(p.decision(src,dst,port)[0],expected)
        wildcard=Policy({'default':'deny','rules':[rule(source='any',destination='any',port='any')]})
        self.assertTrue(wildcard.decision('192.0.2.1','203.0.113.1',65535)[0])

    def test_default_allow_and_deny(self):
        for default,ok in [('allow',True),('deny',False)]:
            p=Policy({'default':default,'rules':[]});allowed,why=p.decision('192.168.50.20','10.20.0.10',443)
            self.assertEqual(allowed,ok);self.assertIn('default policy '+default,why)
        e=Engine(FW,state([],default='allow'));self.assertTrue(e.connect('portal.lab.test',22).ok)
        self.assertEqual(e.grade()['score'],70)

    def test_narrow_success_hostname_and_ip(self):
        e=Engine(FW,state())
        for target in ('portal.lab.test','PORTAL.LAB.TEST.','10.20.0.10'):
            self.assertTrue(e.connect(target,443).ok)
        self.assertEqual(e.connect('portal.lab.test',22).kind,'policy-deny')
        self.assertEqual(e.grade()['score'],100)
        self.assertIn('CONNECT',e.command('connect portal.lab.test 443'))
        self.assertIn('connect <IPv4-or-hostname> <port>',e.command('help'))
        changed=state([rule(source='192.168.50.22/32')]);changed['address']='192.168.50.22'
        self.assertTrue(Engine(FW,changed).connect('portal.lab.test',443).ok)
        self.assertFalse(Engine(FW,changed).grade()['complete'])

    def test_broad_rules_do_not_earn_isolation(self):
        for r in (rule(source='any'),rule(source='192.168.50.0/24'),rule(destination='any'),rule(destination='10.20.0.0/24'),rule(port='any'),rule(source='any',destination='any',port='any')):
            e=Engine(FW,state([r]));g=e.grade()
            self.assertTrue(e.connect('portal.lab.test',443).ok)
            self.assertFalse(g['complete']);self.assertLess(g['score'],100)
            self.assertIn('Overly broad',g['objectives'][-1]['evidence'])
        # Keeping SSH blocked alone does not make an allow-all workaround narrow.
        rules=[rule('ssh-deny','deny',source='any',destination='any',port=22),rule(source='any',destination='any',port='any')]
        e=Engine(FW,state(rules));self.assertEqual(e.connect('portal.lab.test',22).kind,'policy-deny')
        self.assertEqual(e.grade()['score'],80)

    def test_semantic_alternatives_and_shadowed_rules(self):
        deny_all=rule('deny-rest','deny','any','any','any')
        alternatives=[[rule('different-id')],[rule(),deny_all,rule('shadowed-broad','allow','any','any','any')],[rule(),rule('unrelated-deny','deny','192.168.51.0/24','any','any')]]
        for rules in alternatives:
            self.assertEqual(Engine(FW,state(rules)).grade()['score'],100)
        carved=[rule('exclude-peer','deny','192.168.50.21/32'),rule('two-host-range','allow','192.168.50.20/31')]
        self.assertEqual(Engine(FW,state(carved)).grade()['score'],100)
        # Even an allow default is safe when an earlier deny covers every other flow.
        self.assertEqual(Engine(FW,state([rule(),deny_all],default='allow')).grade()['score'],100)

    def test_policy_denial_not_missing_listener_or_route(self):
        e=Engine(FW,state([],default='allow'));result=e.connect('10.20.0.10',444)
        self.assertEqual(result.kind,'no-listener');self.assertIn('default policy allow',result.message)
        p=deepcopy(FW);p['tcp_services'][0]['ports']=[443]
        g=Engine(p,state([],default='allow')).grade()
        self.assertFalse(g['objectives'][3]['ok'])
        e=Engine(FW,{**state(),'gateway':'192.168.50.254'})
        self.assertEqual(e.connect('10.20.0.10',443).kind,'routing-failure')
        self.assertFalse(e.grade()['complete'])
        p=deepcopy(FW);p['topology']['devices'][2]['gateway']='10.20.0.99'
        self.assertIn('Return path',Engine(p,state()).connect('10.20.0.10',443).message)

    def test_bounded_command_and_no_host_io(self):
        import socket,subprocess,os
        e=Engine(FW,state())
        with patch.object(socket,'socket',side_effect=AssertionError('network')),patch.object(subprocess,'Popen',side_effect=AssertionError('process')),patch.object(os,'system',side_effect=AssertionError('shell')):
            for command in ('connect portal.lab.test 443','connect 10.20.0.10 22','connect unknown.test 443','connect 8.8.8.8 443','connect portal.lab.test 0','connect portal.lab.test 65536','connect portal.lab.test -1','connect portal.lab.test 443; sh','$(id)','connect portal.lab.test 443 --force','connect portal.lab.test 443\nsh','x'*513):
                self.assertLess(len(e.command(command)),2048)
            self.assertEqual(e.grade()['score'],100)
        for port in (True,False,0,65536,-1,1.5,'abc','1;sh',None):self.assertFalse(e.connect('portal.lab.test',port).ok)
        self.assertEqual(Engine(PACK,FIXED).connect('portal.lab.test',443).kind,'unsupported')


class FirewallValidationTests(unittest.TestCase):
    def test_malformed_policy(self):
        mutations=[lambda p:p.update(default='accept'),lambda p:p.update(extra='code'),lambda p:p.update(rules='shell'),lambda p:p['rules'][0].update(source='192.168.50.20/24'),lambda p:p['rules'][0].update(destination='999.0.0.0/24'),lambda p:p['rules'][0].update(port=0),lambda p:p['rules'][0].update(port=True),lambda p:p['rules'][0].update(port=65536),lambda p:p['rules'][0].update(protocol='udp'),lambda p:p['rules'][0].update(action='eval'),lambda p:p['rules'][0].update(id='$(id)'),lambda p:p['rules'].append(deepcopy(p['rules'][0])),lambda p:p.update(rules=[rule(str(i)) for i in range(MAX_RULES+1)])]
        for mutation in mutations:
            p={'default':'deny','rules':[rule()]};mutation(p)
            with self.subTest(mutation=mutation),self.assertRaises(ValidationError):policy(p)
        self.assertEqual(policy({'default':'deny','rules':[rule(source='192.168.50.20',port='443') ]})['rules'][0]['source'],'192.168.50.20/32')

    def test_schema_capabilities_services_and_impossible_objectives(self):
        mutations=[lambda p:p.update(schema_version=3),lambda p:p.update(required_capabilities=['tcp-connect']),lambda p:p['firewall'].update(device='APP-01'),lambda p:p['firewall'].update(extra='eval'),lambda p:p['tcp_services'][0].update(ports=[443]),lambda p:p['tcp_services'][0].update(ports=[22,443,443]),lambda p:p['tcp_services'][0].update(device='missing'),lambda p:p['objectives'][2]['params'].update(port=0),lambda p:p['objectives'][3]['params'].update(port=443),lambda p:p['objectives'][4]['params'].update(target='192.168.50.1'),lambda p:p['objectives'][4].update(predicate='eval')]
        for mutation in mutations:
            p=deepcopy(FW);mutation(p)
            with self.subTest(mutation=mutation),self.assertRaises(ValidationError):load_pack(json.dumps(p))
        self.assertEqual(len(load_catalog([RAW,SUB_RAW,FW_RAW])),3)
        with self.assertRaises(ValidationError):load_catalog([FW_RAW,FW_RAW])

    def test_structural_fuzz_new_fields(self):
        for key in ('firewall','tcp_services'):
            for value in (None,[],{},True,123):
                p=deepcopy(FW);p[key]=value
                with self.subTest(key=key,value=value),self.assertRaises(ValidationError):load_pack(json.dumps(p))


class FirewallStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def catalog(self):
        (self.root/'config').mkdir(exist_ok=True)
        c=CatalogBridge([PACK,SUB,FW],self.root/'data',self.root/'config')
        self.addCleanup(lambda:[lab.timer.stop() for lab in c.labs.values()])
        return c

    def test_rule_drafts_apply_atomically_and_submit_idempotently(self):
        s=Session(FW);s.edit_rule(0,'action','allow');s.edit_rule(0,'source','192.168.50.20/32');s.edit_rule(0,'port','bad')
        before=deepcopy(s.attempt)
        with self.assertRaises(ValidationError):s.apply()
        self.assertEqual(s.attempt,before);self.assertEqual(s.submit()['score'],40)
        s.test();self.assertIn('Warning: drafts','\n'.join(s.attempt['console']))
        s.edit_rule(0,'port','443');s.apply();s.hint();s.hint();s.hint()
        self.assertEqual(s.attempt['revision'],1);self.assertFalse(s.attempt['draft'])
        r=s.submit();self.assertEqual(r['score'],100);self.assertEqual(r,s.submit())
        self.assertEqual(r['hints_at_submission'],3)
        self.assertEqual(s.engine.command('connect portal.lab.test 443'),Engine(FW,s.attempt['applied']).command('connect portal.lab.test 443'))
        s.edit_rule(0,'source','192.168.50.20');s.apply();self.assertEqual(s.attempt['revision'],1)

    def test_add_move_remove_and_default_drafts(self):
        s=Session(FW);index=s.add_rule();self.assertEqual(index,1);s.edit_rule(index,'action','allow');s.apply()
        self.assertFalse(s.engine.connect('portal.lab.test',443).ok)
        self.assertEqual(s.move_rule(1,-1),0);s.apply();self.assertEqual(s.submit()['score'],100)
        s.edit_default('allow');self.assertEqual(s.engine.applied['firewall']['default'],'deny')
        s.apply();self.assertLess(s.submit()['score'],100)
        s.edit_default('deny');s.remove_rule(1);s.apply();self.assertEqual(s.submit()['score'],100)
        with self.assertRaises(ValidationError):s.move_rule(0,-1)
        with self.assertRaises(ValidationError):s.edit_rule(0,'protocol','udp')
        with self.assertRaises(ValidationError):s.edit('gateway','192.168.50.254')

    def test_grading_independent_of_command_order(self):
        results=[]
        for commands in (['ping portal.lab.test','connect portal.lab.test 443','connect portal.lab.test 22'],['connect portal.lab.test 22','nslookup portal.lab.test','connect 10.20.0.10 443'],[]):
            s=Session(FW);s.edit_rule(0,'source','192.168.50.20/32');s.edit_rule(0,'action','allow');s.apply()
            for command in commands:s.execute(command)
            r=s.submit();results.append({k:r[k] for k in ('score','complete','objectives')})
        self.assertTrue(all(r==results[0] for r in results));self.assertEqual(results[0]['score'],100)

    def test_all_three_switch_reset_mode_history_and_restart(self):
        c=self.catalog();ids={}
        for pack in (PACK,SUB,FW):
            c.selectLab(pack['lab_id'],True)
            if pack is FW:
                c.editRule('source','192.168.50.20/32');c.editRule('action','allow')
            else:
                for k,v in (FIXED if pack is PACK else {'prefix':24}).items():c.edit(k,str(v))
            c.apply();c.hint();c.submit();self.assertEqual(c.session.engine.grade()['score'],100)
            c.restart('Challenge');c.execute('help');c.restart('Challenge')
            self.assertEqual(c.view['historyCount'],2);self.assertEqual(c.view['libraryBest'],'100/100')
            self.assertFalse(c.session.attempt['console']);self.assertEqual(c.session.attempt['hints'],0)
            if pack is FW:c.editRule('source','unfinished source')
            else:c.edit('address','unfinished address')
            ids[pack['lab_id']]=c.session.attempt['id']
            c.flush()
        self.assertFalse(c.selectLab('gateway-dns',False));self.assertTrue(c.selectLab('gateway-dns',True))
        self.assertEqual(c.session.attempt['id'],ids['gateway-dns'])
        c.selectLab('service-firewall',True);c.flush();restored=self.catalog()
        self.assertEqual(restored.pack['lab_id'],'service-firewall')
        for lab_id in ids:
            restored.selectLab(lab_id,True)
            self.assertEqual(restored.session.attempt['id'],ids[lab_id]);self.assertTrue(restored.session.attempt['draft'])
            rows,count,_=restored.store.history(restored.session.attempt['id'])
            self.assertEqual(count,2);self.assertTrue(any(a['hints']==1 and any(r['score']==100 for r in a['assessments'].values()) for a in rows))
        self.assertEqual(json.loads((self.root/'data/current.json').read_text())['schema_version'],1)
        self.assertEqual(json.loads((self.root/'data/labs/service-firewall/current.json').read_text())['schema_version'],2)

    def test_firewall_progress_corruption_backup_and_future_schema(self):
        store=Store(self.root/'firewall',FW);s=Session(FW);store.save(s.attempt);s.edit_rule(0,'port','invalid draft');store.save(s.attempt)
        self.assertEqual(store.load()['draft']['firewall']['rules'][0]['port'],'invalid draft')
        store.current.write_text('{corrupt');recovery=Store(store.root,FW);a=recovery.load()
        self.assertEqual(a['id'],s.attempt['id']);self.assertFalse(a['draft']);self.assertTrue(list(store.root.glob('current.corrupt-*')))
        raw=b'{"schema_version":3,"future":"keep"}';store.current.write_bytes(raw);future=Store(store.root,FW)
        self.assertIsNone(future.load());self.assertTrue(future.read_only);self.assertEqual(future.current.read_bytes(),raw)

    def test_saved_rule_tampering_and_malformed_drafts(self):
        s=Session(FW)
        for mutate in (lambda a:a['applied']['firewall'].update(default='eval'),lambda a:a['applied']['firewall']['rules'][0].update(port=True),lambda a:a['draft'].update(firewall={'default':'deny','rules':[rule()]}),lambda a:a['draft'].update(firewall={'default':'deny','rules':[{'id':'x'}]})):
            a=deepcopy(s.attempt);mutate(a)
            with self.assertRaises(ValidationError):validate_record(encode(a),FW)
        s.edit_rule(0,'action','allow');s.edit_rule(0,'source','192.168.50.20/32');s.apply();s.submit();a=deepcopy(s.attempt)
        a['assessments']['1']['applied']['firewall']['rules'][0]['source']='any'
        with self.assertRaises(ValidationError):validate_record(encode(a),FW)

if __name__=='__main__':unittest.main()
