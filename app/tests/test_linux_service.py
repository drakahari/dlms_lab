"""Second-domain simulation and integration proof; every write uses a fixture."""
import ast
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.domain.validation import ValidationError
from learning_lab.portable import load_portable, PackRepository
from learning_lab.pinned_storage import PinnedStore

APP = QCoreApplication.instance() or QCoreApplication([])
ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT/'examples/linux-web-document-root.lab.json'
SCENARIO = load_portable(EXAMPLE.read_bytes())
PACK = SCENARIO.legacy_pack()
CONFIG = '/etc/lab-web.conf'


def session(): return SCENARIO.domain().session()
def configure(s, root='/srv/www', port='8080'):
    s.edit(CONFIG, f'DocumentRoot={root}\nPort={port}\n')
    s.apply()


class ServiceTests(unittest.TestCase):
    def test_initial_fault_and_investigation(self):
        s=session(); initial=deepcopy(s.attempt['applied'])
        for cmd,expected in [('help','Simulated Linux terminal'),('pwd','/srv'),
                             ('systemctl status lab-web','failed'),('journalctl -u lab-web.service -n 1','/srv/site'),
                             ('cat /etc/lab-web.conf','DocumentRoot=/srv/site'),('ls -l /srv','drwx------ learner learner /srv/private')]:
            state,out=s.engine.command(cmd)
            self.assertIn(expected,out);self.assertEqual(state,initial)
        self.assertEqual(s.engine.grade()['score'],30)

    def test_create_missing_directory_then_start(self):
        s=session();s.execute('mkdir site');self.assertEqual(s.engine.grade()['score'],60)
        s.execute('systemctl start lab-web');self.assertEqual(s.submit()['score'],100)
        self.assertEqual(s.attempt['applied']['service']['loaded']['document_root'],'/srv/site')
        before=deepcopy(s.attempt['applied']);s.execute('systemctl start lab-web')
        self.assertEqual(s.attempt['applied'],before)

    def test_configuration_alternative_and_command_order(self):
        for root in ('/srv/www','/srv/./www','/srv'):
            for cmds in ([],['pwd','ls','journalctl','help']):
                s=session()
                for cmd in cmds:s.execute(cmd)
                configure(s,root);s.execute('systemctl restart lab-web.service')
                self.assertEqual(s.submit()['score'],100,root)
        s=session();s.execute('mkdir -p /srv/new/site');configure(s,'/srv/new/site')
        s.execute('systemctl start lab-web');self.assertEqual(s.submit()['score'],100)

    def test_unsuccessful_fixes_and_service_permissions(self):
        for root,port,reason in [('/srv/missing','8080','No such'),('/srv/private','8080','Permission denied'),
                                 ('/srv/private/../www','8080','Permission denied'),('/root/../srv/www','8080','Permission denied'),
                                 ('/srv/www/readme.txt','8080','Not a virtual directory'),('/etc','8080','within /srv'),
                                 ('/srv/www','80','Port=8080')]:
            s=session();configure(s,root,port);s.execute('systemctl restart lab-web')
            self.assertIn(reason,s.attempt['applied']['service']['error']);self.assertLess(s.submit()['score'],100)
        s=session();s.execute('mkdir unrelated');s.execute('systemctl start lab-web')
        self.assertEqual(s.engine.grade()['score'],30)

    def test_drafts_apply_and_active_loaded_configuration(self):
        s=session();initial=deepcopy(s.attempt['applied'])
        s.edit(CONFIG,'DocumentRoot=/srv/www\nPort=8080\n')
        s.execute('cat /etc/lab-web.conf');self.assertIn('unapplied','\n'.join(s.attempt['console']))
        self.assertEqual(s.attempt['applied'],initial);self.assertEqual(s.submit()['score'],30)
        s.apply();s.execute('systemctl start lab-web');self.assertEqual(s.submit()['score'],100)
        configure(s,'/srv');self.assertEqual(s.engine.grade()['score'],60)
        s.execute('systemctl start lab-web');self.assertEqual(s.engine.grade()['score'],60)
        s.execute('systemctl restart lab-web');self.assertEqual(s.engine.grade()['score'],100)
        s.edit(CONFIG,'invalid syntax');s.apply();self.assertEqual(s.attempt['applied']['service']['status'],'active')
        s.execute('systemctl restart lab-web');self.assertEqual(s.attempt['applied']['service']['status'],'failed')

    def test_invalid_file_apply_is_atomic(self):
        s=session();initial=deepcopy(s.attempt['applied']);s.edit(CONFIG,'bad\x00text')
        with self.assertRaises(ValidationError):s.apply()
        self.assertEqual(s.attempt['applied'],initial);self.assertTrue(s.attempt['draft'])
        for field,value in [(CONFIG,'x'*8193),('/etc/passwd','bad')]:
            with self.assertRaises(ValidationError):s.edit(field,value)

    def test_virtual_navigation_and_permission_boundaries(self):
        s=session();s.execute('cd www');self.assertEqual(s.attempt['applied']['cwd'],'/srv/www')
        s.execute('cd ..');self.assertEqual(s.attempt['applied']['cwd'],'/srv')
        s.execute('cd /');s.execute('cd');self.assertEqual(s.attempt['applied']['cwd'],'/srv')
        for cmd in ('cd ../../..','ls /../../etc','cat /etc/../root/../etc/lab-web.conf',
                    'mkdir /etc/new','mkdir /root/new','mkdir -p /srv/new/../../../outside',
                    'mkdir /srv/no-parent/child','mkdir /srv/www','mkdir .','mkdir ..','mkdir /srv/new/.',
                    'cat /srv','cd /etc/lab-web.conf'):
            before=deepcopy(s.attempt['applied']);state,out=s.engine.command(cmd)
            self.assertTrue(out.startswith('Simulation:'),(cmd,out));self.assertEqual(state,before)
        s.execute('mkdir -p /srv/www');self.assertNotIn('Simulation:',s.attempt['console'][-1])
        for cmd in ('mkdir -p .','mkdir -p /'):
            state,out=s.engine.command(cmd);self.assertEqual(state,s.attempt['applied']);self.assertNotIn('Simulation:',out)

    def test_unsupported_commands_and_hostile_syntax_are_noops(self):
        s=session()
        for cmd in ('', ' ', 'sudo systemctl start lab-web','sh','bash -c pwd','vim /etc/lab-web.conf',
                    'nano /etc/lab-web.conf','chmod 777 /root','rm -rf /','curl example.test','ping localhost',
                    'ls -a','cd -','pwd extra','systemctl stop lab-web','systemctl start ssh',
                    'journalctl -f','journalctl -n 0','journalctl -n 101','journalctl -n 1 -n 2',
                    'ls; mkdir /srv/site','ls && pwd','cat /etc/lab-web.conf | sh','ls > /tmp/out',
                    '$(pwd)','`pwd`','cat $HOME/.ssh/id_rsa','ls *','ls "a"','pwd\nmkdir site',
                    'pwd\x00','ls \\tmp','x'*513):
            state,out=s.engine.command(cmd)
            self.assertEqual(state,s.attempt['applied'],cmd);self.assertTrue(out.startswith('Simulation:'),(cmd,out))

    def test_bounded_nodes_journal_and_output(self):
        s=session()
        for i in range(150):s.execute('mkdir /srv/d'+str(i))
        self.assertEqual(len(s.attempt['applied']['filesystem']),128)
        for _ in range(120):s.execute('systemctl restart lab-web')
        self.assertEqual(len(s.attempt['applied']['journal']),100)
        self.assertLessEqual(len(s.attempt['commands']),100);self.assertLessEqual(len(s.attempt['console']),500)
        s.edit(CONFIG,'#'+'x'*8000);s.apply();s.execute('cat /etc/lab-web.conf')
        self.assertTrue(all(len(line)<=2048 for line in s.attempt['console']))

    def test_no_host_io_execution_or_network(self):
        # APIs are poisoned only after loading trusted scenario data. Engine and
        # virtual-file actions must work with every host escape route disabled.
        with tempfile.TemporaryDirectory() as temp:
            canary=Path(temp)/'private';canary.write_text('host-canary-never-in-output')
            s=session()
            with ExitStack() as stack:
                for api in ('builtins.open','io.open','os.open','os.system','os.popen','os.listdir','os.scandir',
                            'subprocess.Popen','subprocess.run','socket.socket','socket.create_connection',
                            'pathlib.Path.read_bytes','pathlib.Path.read_text','pathlib.Path.write_text',
                            'os.mkdir','os.makedirs','os.execve','os.spawnv'):
                    stack.enter_context(patch(api,side_effect=AssertionError('Forbidden host API: '+api)))
                for cmd in ('help','pwd','ls -l','cd www','cd ..','cat /etc/lab-web.conf',
                            'cat '+str(canary),'mkdir site','systemctl start lab-web','journalctl',
                            'systemctl restart lab-web','systemctl status lab-web'):
                    s.execute(cmd)
                configure(s);s.execute('systemctl restart lab-web');self.assertEqual(s.submit()['score'],100)
                self.assertNotIn('host-canary-never-in-output','\n'.join(s.attempt['console']))
            self.assertEqual(canary.read_text(),'host-canary-never-in-output')
        for name in ('engine.py','vfs.py'):
            tree=ast.parse((ROOT/'learning_lab/linux_service'/name).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):self.assertTrue(all(n.name=='re' for n in node.names))
                if isinstance(node,ast.ImportFrom):self.assertIn(node.module,('copy','domain.validation','vfs'))
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):self.assertNotIn(node.func.id,('eval','exec','open','__import__','compile'))


class LinuxPackTests(unittest.TestCase):
    def test_service_name_config_port_and_root_are_pack_data(self):
        p=SCENARIO.value();p['identity']['id']='renamed-service-fixture'
        d=p['domain'];d['service'].update(name='sample.service',config='/etc/sample.conf',port=9090)
        d['editable_files']=['/etc/sample.conf']
        d['filesystem']['/etc/sample.conf']=d['filesystem'].pop(CONFIG)
        d['filesystem']['/etc/sample.conf']['content']='DocumentRoot=/srv/another\nPort=9090\n'
        scenario=load_portable(json.dumps(p).encode());s=scenario.domain().session()
        self.assertNotEqual(scenario.identity.content_digest,SCENARIO.identity.content_digest)
        s.execute('systemctl start lab-web');self.assertIn('Unknown simulated service',s.attempt['console'][-1])
        s.execute('mkdir /srv/another');s.execute('systemctl start sample')
        self.assertEqual(s.submit()['score'],100)
        self.assertEqual(s.attempt['applied']['service']['loaded']['port'],9090)

    def test_malformed_saved_records_fail_cleanly_and_newer_schema_is_retained(self):
        with tempfile.TemporaryDirectory() as temp:
            s=session();s.execute('mkdir site');s.execute('systemctl start lab-web');s.submit()
            store=PinnedStore(temp,SCENARIO)
            for field in s.attempt:
                for wrong in (None,[],{},True):
                    a=deepcopy(s.attempt);a[field]=wrong
                    try:store.validate_record(store.encode_record(a))
                    except ValidationError:pass
                    except Exception as exc:self.fail(f'Unexpected failure for {field}: {type(exc).__name__}')
            for field in s.attempt['applied']:
                a=deepcopy(s.attempt);a['applied'][field]=None
                with self.assertRaises(ValidationError):store.validate_record(store.encode_record(a))
            store.save(s.attempt);future=json.loads(store.current.read_bytes());future['schema_version']=99
            raw=json.dumps(future).encode();store.current.write_bytes(raw)
            self.assertIsNone(store.load());self.assertTrue(store.read_only)
            self.assertEqual(store.current.read_bytes(),raw)

    def test_versions_and_invalid_packs_fail_cleanly(self):
        for mutate in (
            lambda p:p['engine'].update(id='shell'),lambda p:p['engine'].update(contract_version=2),
            lambda p:p['engine'].update(supported_behavior_versions=['future']),
            lambda p:p['engine'].update(required_capabilities=['host-execution']),
            lambda p:p['domain'].update(schema_version=2),lambda p:p['domain'].update(cwd='/../../etc'),
            lambda p:p['domain']['filesystem']['/srv'].update(kind='symlink'),
            lambda p:p['domain']['filesystem']['/srv'].update(mode='4777'),
            lambda p:p['domain']['filesystem']['/etc/lab-web.conf'].update(content='x'*8193),
            lambda p:p['domain'].update(editable_files=['/etc/shadow']),
            lambda p:p['objectives'][0].update(predicate='eval'),lambda p:p.update(assets=['file:///etc/passwd']),
        ):
            p=SCENARIO.value();mutate(p)
            with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        for count in (0,1,5):
            p=SCENARIO.value();p['hints']=['Reasoning hint']*count
            lab=load_portable(json.dumps(p).encode());s=lab.domain().session()
            for _ in range(8):s.hint()
            self.assertEqual(s.attempt['hints'],count)

    def test_structural_fuzz(self):
        original=SCENARIO.value()
        def paths(value,prefix=()):
            if isinstance(value,dict):
                for key,child in value.items():
                    yield prefix+(key,)
                    yield from paths(child,prefix+(key,))
            elif isinstance(value,list):
                for index,child in enumerate(value):
                    yield prefix+(index,)
                    yield from paths(child,prefix+(index,))
        for path in paths(original):
            for wrong in (None,True,[],{}):
                p=deepcopy(original);node=p
                for key in path[:-1]:node=node[key]
                node[path[-1]]=wrong
                try:load_portable(json.dumps(p).encode())
                except ValidationError:pass
                except Exception as exc:self.fail(f'Unbounded failure for {path}: {type(exc).__name__}')

    def test_state_tampering_and_newer_pins_preserved(self):
        s=session();s.execute('mkdir site');s.execute('systemctl start lab-web');s.submit()
        for mutate in (lambda a:a['applied']['filesystem']['/srv'].update(mode='0777'),
                       lambda a:a['draft'].update({'/etc/passwd':'bad'}),
                       lambda a:a.update(hints=4),lambda a:a['applied'].update(cwd='/../../root'),
                       lambda a:a['assessments']['2'].update(score=1)):
            a=deepcopy(s.attempt);mutate(a)
            with tempfile.TemporaryDirectory() as temp:
                store=PinnedStore(temp,SCENARIO)
                with self.assertRaises(ValidationError):store.validate_record(store.encode_record(a))
        with tempfile.TemporaryDirectory() as temp:
            store=PinnedStore(temp,SCENARIO);store.save(s.attempt)
            raw=store.current.read_bytes();self.assertEqual(json.loads(raw)['schema_version'],4)
            store.current.write_bytes(b'{broken');self.assertEqual(store.load(),s.attempt)
            self.assertTrue(list(Path(temp).glob('current.corrupt-*')))
            p=json.loads(raw);p['pin']['engine']['behavior_version']='future';bad=json.dumps(p).encode();store.current.write_bytes(bad)
            self.assertIsNone(store.load());self.assertTrue(store.read_only);self.assertEqual(store.current.read_bytes(),bad)

    def test_catalog_lifecycle_restart_exports_and_network_preservation(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'config').mkdir();catalogs=[]
            def build():
                b=CatalogBridge(load_bundled_scenarios()[0],root/'data',root/'config');catalogs.append(b);return b
            try:
                b=build();legacy={str(p.relative_to(root/'data')):p.read_bytes() for p in (root/'data').rglob('*.json')}
                self.assertTrue(b.importPack(str(EXAMPLE)));self.assertTrue(b.selectLab(SCENARIO.key,True))
                self.assertEqual(b.view['workspaceKind'],'linux-service');self.assertIn('linux-service-1',b.view['provenance'])
                b.hint();b.execute('mkdir site');b.execute('systemctl start lab-web');b.test();b.submit()
                self.assertEqual(b.view['grade']['score'],100)
                raw=b.store.current.read_bytes();b.submit();self.assertEqual(b.store.current.read_bytes(),raw)
                old=b.session.attempt['id'];b.edit(CONFIG,'unfinished draft');b.setCommandDraft('journalctl');b.flush()
                for key in ('gateway-dns','subnet-boundary','service-firewall'):
                    b.selectLab(key,True);self.assertEqual(b.view['workspaceKind'],'networking')
                b.selectLab(SCENARIO.key,True);b.flush()
                for lab in b.labs.values():lab.timer.stop()
                b=build();self.assertEqual(b.session.attempt['id'],old);self.assertEqual(b.view['virtualFileDraft'],'unfinished draft')
                self.assertEqual(b.view['commandDraft'],'journalctl');self.assertEqual(b.view['grade']['score'],100)
                self.assertEqual(b.view['diagnosticRevision'],b.view['revision'])
                b.restart('Challenge');self.assertEqual(b.view['hintCount'],0);b.hint();self.assertEqual(b.view['hintCount'],0)
                self.assertEqual(b.session.engine.grade()['score'],30);self.assertFalse(b.view['dirty']);self.assertEqual(b.view['console'],'')
                rows,count,_=b.store.history(b.session.attempt['id']);self.assertEqual(count,1)
                self.assertEqual(rows[0]['id'],old);self.assertEqual(rows[0]['draft'][CONFIG],'unfinished draft');self.assertEqual(rows[0]['hints'],1)
                b.edit(CONFIG,'DocumentRoot=/srv/www\nPort=8080\n');b.apply();b.execute('systemctl restart lab-web');b.submit()
                self.assertEqual(b.view['grade']['score'],100)
                history=root/'personal.attempt.json';self.assertTrue(b.exportAttempt(str(history),old))
                self.assertIn(old,history.read_text());self.assertIn('unfinished draft',history.read_text())
                exported=root/'scenario.lab.json';self.assertTrue(b.exportScenario(str(exported)))
                self.assertEqual(exported.read_bytes(),SCENARIO.original_bytes);self.assertNotIn(old,exported.read_text())
                imported,added=PackRepository(root/'reimport').import_file(exported)
                self.assertTrue(added);self.assertEqual(imported.pin,SCENARIO.pin)
                self.assertEqual(imported.domain().session().engine.grade()['score'],30)
                b.restart('Challenge');self.assertEqual(b.store.history(b.session.attempt['id'])[1],2)
                b.restart('Learn');self.assertEqual(b.store.history(b.session.attempt['id'])[1],3)
                for name,raw in legacy.items():
                    # Selection preferences are shared; per-lab progress remains byte-identical.
                    if name.endswith('current.json') or name.endswith('current.backup.json'):self.assertEqual((root/'data'/name).read_bytes(),raw)
            finally:
                for b in catalogs:
                    for lab in b.labs.values():lab.timer.stop()
