"""Navigation evidence, safety and lifecycle tests. All writes use fixtures."""
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
from learning_lab.linux_navigation.engine import guide
from learning_lab.portable import load_portable, PackRepository
from learning_lab.pinned_storage import PinnedStore

APP = QCoreApplication.instance() or QCoreApplication([])
ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT/'examples/linux-file-navigation.lab.json'
SCENARIO = load_portable(EXAMPLE.read_bytes())
HOME = '/home/learner'
DOCUMENTS = HOME+'/Documents'
PROJECTS = HOME+'/Projects'
WELCOME = DOCUMENTS+'/welcome.txt'
COMMANDS = ('pwd', 'ls', 'cd Documents', 'cat welcome.txt', 'cd /home/learner/Projects')


def session(mode='Learn'): return SCENARIO.domain().session(mode=mode)
def finish(s, commands=COMMANDS):
    for command in commands: s.execute(command)


class NavigationTests(unittest.TestCase):
    def test_initial_state_and_guided_progression(self):
        s=session(); initial=deepcopy(s.attempt['applied'])
        self.assertEqual(set(initial), {'filesystem','cwd','activity'})
        self.assertEqual(initial['cwd'],HOME);self.assertEqual(s.engine.grade()['score'],0)
        for i,command in enumerate(COMMANDS):
            g=guide(s.pack,s.attempt['applied'])
            self.assertEqual(g['index'],i);self.assertEqual(g['command'],command)
            self.assertTrue(g['explanation']);self.assertTrue(g['expected']);self.assertFalse(g['verified'])
            s.execute(command)
        self.assertTrue(guide(s.pack,s.attempt['applied'])['verified'])
        self.assertEqual(s.submit()['score'],100)
        self.assertEqual(s.attempt['applied']['filesystem'],initial['filesystem'])

    def test_equivalent_paths_and_different_order_in_challenge(self):
        for commands in (
            ('cat Documents/./welcome.txt','cd Documents/../Documents','ls ..','cd ..','pwd','cd ./Projects/'),
            ('ls -l /home//learner/.','cat '+WELCOME,'pwd','cd '+DOCUMENTS,'cd ../Downloads/../Projects'),
        ):
            s=session('Challenge');finish(s,commands)
            self.assertEqual(s.submit()['score'],100)
            self.assertEqual(s.domain.view_state(s,None,0)['guide'],{})
            with self.assertRaises(ValidationError):s.hint()

    def test_activity_is_distinct_from_final_state(self):
        s=session();s.execute('cd '+PROJECTS)
        self.assertEqual(s.submit()['score'],25)
        s.execute('cd');finish(s);self.assertEqual(s.submit()['score'],100)
        facts=deepcopy(s.attempt['applied']['activity']);s.execute('cd /')
        self.assertEqual(s.submit()['score'],75)
        for op in ('pwd','ls','cat'):self.assertEqual(s.attempt['applied']['activity'][op],facts[op])
        rows=s.engine.grade()['objectives']
        self.assertTrue(all(r['evidence'].startswith('Action evidence:') for r in rows[:4]))
        self.assertTrue(rows[-1]['evidence'].startswith('Final state:'))

    def test_diagnostics_and_wrong_targets_do_not_complete_actions(self):
        s=session();s.test();s.execute('help');s.execute('cat /etc/motd');s.execute('ls Documents')
        s.execute('cd Downloads');s.execute('pwd')
        self.assertEqual(s.engine.grade()['score'],0)
        self.assertEqual(guide(s.pack,s.attempt['applied'])['command'],'cd '+HOME)
        s.execute('cd '+HOME);self.assertEqual(guide(s.pack,s.attempt['applied'])['command'],'pwd')
        s.execute('pwd');s.execute('ls');s.execute('cd /')
        self.assertEqual(guide(s.pack,s.attempt['applied'])['command'],'cd home/learner/Documents')

    def test_evidence_survives_transcript_eviction_and_duplicate_submissions(self):
        s=session();finish(s);first=s.submit();revision=s.attempt['revision']
        facts=deepcopy(s.attempt['applied']['activity'])
        for _ in range(110):s.execute('help')
        self.assertEqual(len(s.attempt['commands']),100);self.assertLessEqual(len(s.attempt['console']),500)
        self.assertEqual(s.attempt['applied']['activity'],facts)
        self.assertEqual(s.attempt['revision'],revision);self.assertEqual(s.submit(),first)
        s.execute('cat '+WELCOME);self.assertEqual(s.attempt['revision'],revision)
        self.assertEqual(s.submit(),first)

    def test_path_errors_permissions_and_root_boundary(self):
        s=session()
        for command,reason in (
            ('cd absent','No such'),('cat missing.txt','No such'),('ls missing','No such'),
            ('cd Documents/welcome.txt','Not a virtual directory'),('cat Documents','Is a virtual directory'),
            ('cat Documents/welcome.txt/..','Not a virtual directory'),
            ('cd /root','Permission denied'),('ls /root','Permission denied'),
            ('cat /root/private.txt','Permission denied'),('cd /root/../home','Permission denied'),
            ('cd /missing/../home','No such'),('cd /../../home','escape'),
        ):
            before=deepcopy(s.attempt['applied']);state,out=s.engine.command(command)
            self.assertEqual(state,before,command);self.assertIn(reason,out,command)
        s.execute('ls Documents/welcome.txt');self.assertEqual(s.engine.grade()['score'],0)
        s.execute('cd /');s.execute('cd .');self.assertEqual(s.attempt['applied']['cwd'],'/')
        before=deepcopy(s.attempt['applied']);state,out=s.engine.command('cd ..')
        self.assertEqual(state,before);self.assertIn('escape',out)
        s.execute('cd');self.assertEqual(s.attempt['applied']['cwd'],HOME)
        # Separate read permission failure, with searchable parents, in pack data.
        p=SCENARIO.value();p['domain']['filesystem']['/etc/motd']['mode']='0600'
        t=load_portable(json.dumps(p).encode()).domain().session()
        state,out=t.engine.command('cat /etc/motd');self.assertIn('Permission denied (read)',out)
        self.assertEqual(state,t.attempt['applied'])

    def test_unsupported_and_hostile_commands_are_noops(self):
        s=session()
        for cmd in ('',' ','pwd extra','ls -a','cat','cat welcome.txt extra','cd -','ls ~',
                    'mkdir foo','systemctl start lab-web','journalctl','nano file','clear','sudo pwd',
                    'pwd; ls','pwd && ls','ls | sh','cat /etc/passwd > /tmp/out','$(pwd)','`pwd`',
                    'cat $HOME/.ssh/id_rsa','ls *','cd "Documents"','pwd\nls','pwd\x00','ls \\tmp','x'*513):
            state,out=s.engine.command(cmd)
            self.assertEqual(state,s.attempt['applied'],cmd);self.assertTrue(out.startswith('Simulation:'),(cmd,out))
        with self.assertRaises(ValidationError):s.edit(WELCOME,'bad')
        with self.assertRaises(ValidationError):s.apply()

    def test_no_host_io_processes_or_network(self):
        with tempfile.TemporaryDirectory() as temp:
            canary=Path(temp)/'private';canary.write_text('host-canary-never-in-output')
            s=session()
            with ExitStack() as stack:
                for api in ('builtins.open','io.open','os.open','os.system','os.popen','os.listdir','os.scandir',
                            'subprocess.Popen','subprocess.run','socket.socket','socket.create_connection',
                            'pathlib.Path.read_bytes','pathlib.Path.read_text','pathlib.Path.write_text',
                            'os.mkdir','os.makedirs','os.execve','os.spawnv'):
                    stack.enter_context(patch(api,side_effect=AssertionError('Forbidden host API: '+api)))
                finish(s);s.execute('help');s.execute('cat '+str(canary));s.execute('ls '+temp)
                self.assertEqual(s.submit()['score'],100)
                self.assertNotIn('host-canary-never-in-output','\n'.join(s.attempt['console']))
            self.assertEqual(canary.read_text(),'host-canary-never-in-output')
        tree=ast.parse((ROOT/'learning_lab/linux_navigation/engine.py').read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):self.assertTrue(all(n.name=='re' for n in node.names))
            if isinstance(node,ast.ImportFrom):self.assertIn(node.module,('copy','domain.validation','linux_service.vfs','linux_service.engine'))
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):self.assertNotIn(node.func.id,('eval','exec','open','__import__','compile'))


class NavigationPackTests(unittest.TestCase):
    def test_data_only_import_and_exact_export_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=PackRepository(Path(temp)/'packs')
            s,added=repo.import_file(EXAMPLE);self.assertTrue(added);self.assertEqual(s.pin,SCENARIO.pin)
            self.assertFalse(repo.import_file(EXAMPLE)[1])
            p=SCENARIO.value();p['identity']['content_version']='1.0.1'
            p['domain']['filesystem'][WELCOME]['content']='__import__("os").system("touch /tmp/never")\n<script>bad()</script>'
            with ExitStack() as stack:
                for api in ('os.system','os.popen','subprocess.Popen','socket.socket','builtins.eval','builtins.exec'):
                    stack.enter_context(patch(api,side_effect=AssertionError('Pack attempted execution: '+api)))
                imported,_=repo.install(json.dumps(p).encode());t=imported.domain().session()
                t.execute('cat '+WELCOME);self.assertIn('__import__','\n'.join(t.attempt['console']))
            self.assertNotEqual(imported.identity.content_digest,s.identity.content_digest)
            self.assertEqual(s.original_bytes,EXAMPLE.read_bytes())
            for field in ('script','module','on_load'):
                bad=SCENARIO.value();bad['domain'][field]='os.system'
                with self.assertRaises(ValidationError):repo.install(json.dumps(bad).encode())
            self.assertEqual(len(repo.scan()[0]),2)

    def test_versions_targets_limits_and_invalid_packs(self):
        for mutate in (
            lambda p:p.update(schema_version=2),lambda p:p['engine'].update(contract_version=2),
            lambda p:p['engine'].update(supported_behavior_versions=['future']),
            lambda p:p['engine'].update(required_capabilities=['host-execution']),
            lambda p:p['domain'].update(schema_version=2),lambda p:p['domain'].update(cwd='/../../etc'),
            lambda p:p['domain']['filesystem'][HOME].update(kind='symlink'),
            lambda p:p['domain']['filesystem'][HOME].update(mode='4777'),
            lambda p:p['domain']['filesystem'][WELCOME].update(content='x'*8193),
            lambda p:p['objectives'][0].update(predicate='eval'),
            lambda p:p['objectives'][0]['params'].update(path='/root'),
            lambda p:p['objectives'][3]['params'].update(path=DOCUMENTS),
            lambda p:p['domain']['lesson']['steps'][0].update(objective='missing'),
            lambda p:p.update(assets=['file:///etc/passwd']),
        ):
            p=SCENARIO.value();mutate(p)
            with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        for raw in (b'PKzip', b'{broken', b'x'*262145):
            with self.assertRaises(ValidationError):load_portable(raw)
        p=SCENARIO.value()
        for i in range(65):p['domain']['filesystem'][HOME+'/extra'+str(i)]=deepcopy(p['domain']['filesystem'][HOME])
        with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        for count in (0,1,5):
            p=SCENARIO.value();p['hints']=['Reasoning hint']*count;t=load_portable(json.dumps(p).encode()).domain().session()
            for _ in range(8):t.hint()
            self.assertEqual(t.attempt['hints'],count)

    def test_structural_fuzz_rejects_cleanly(self):
        original=SCENARIO.value()
        def paths(value,prefix=()):
            if isinstance(value,dict):
                for key,child in value.items():yield prefix+(key,);yield from paths(child,prefix+(key,))
            elif isinstance(value,list):
                for index,child in enumerate(value):yield prefix+(index,);yield from paths(child,prefix+(index,))
        for path in paths(original):
            for wrong in (None,True,[],{}):
                p=deepcopy(original);node=p
                for key in path[:-1]:node=node[key]
                node[path[-1]]=wrong
                try:load_portable(json.dumps(p).encode())
                except ValidationError:pass
                except Exception as exc:self.fail(f'Unbounded failure for {path}: {type(exc).__name__}')

    def test_pack_paths_and_objectives_are_not_hard_coded(self):
        p=SCENARIO.value();p['identity']['id']='different-navigation-fixture'
        # Change every virtual home path, including objective targets and cwd.
        raw=json.dumps(p).replace('/home/learner','/home/visitor')
        lab=load_portable(raw.encode());s=lab.domain().session()
        for _ in range(5):s.execute(guide(s.pack,s.attempt['applied'])['command'])
        self.assertEqual(s.submit()['score'],100);self.assertEqual(s.attempt['applied']['cwd'],'/home/visitor/Projects')

    def test_state_validation_corruption_recovery_and_future_preservation(self):
        s=session();finish(s);s.submit()
        with tempfile.TemporaryDirectory() as temp:
            store=PinnedStore(temp,SCENARIO)
            for mutate in (
                lambda a:a['applied']['activity']['cat'].append('/etc/shadow'),
                lambda a:a['applied']['activity']['pwd'].append(HOME),
                lambda a:a['applied']['activity'].update(pwd='pwd'),
                lambda a:a['applied'].update(cwd='/root'),
                lambda a:a['applied']['filesystem'][WELCOME].update(content='tampered'),
                lambda a:a['draft'].update({WELCOME:'bad'}),
                lambda a:a['assessments'][str(a['revision'])].update(score=0),
            ):
                a=deepcopy(s.attempt);mutate(a)
                with self.assertRaises(ValidationError):store.validate_record(store.encode_record(a))
            for field in s.attempt['applied']:
                for wrong in (None,[],{},True):
                    a=deepcopy(s.attempt);a['applied'][field]=wrong
                    with self.assertRaises(ValidationError):store.validate_record(store.encode_record(a))
            store.save(s.attempt);raw=store.current.read_bytes();store.current.write_bytes(b'{broken')
            self.assertEqual(store.load(),s.attempt);self.assertTrue(list(Path(temp).glob('current.corrupt-*')))
            future=json.loads(raw);future['pin']['engine']['behavior_version']='future'
            raw=json.dumps(future).encode();store.current.write_bytes(raw)
            self.assertIsNone(store.load());self.assertTrue(store.read_only);self.assertEqual(store.current.read_bytes(),raw)

    def test_catalog_restart_modes_reset_history_and_exports(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'config').mkdir();catalogs=[]
            def build():
                b=CatalogBridge(load_bundled_scenarios()[0],root/'data',root/'config');catalogs.append(b);return b
            try:
                b=build()
                for filename in ('linux-web-document-root','linux-service-basics'):
                    self.assertTrue(b.importPack(str(ROOT/'examples'/(filename+'.lab.json'))))
                original={str(p.relative_to(root/'data')):p.read_bytes() for p in (root/'data').rglob('current*.json')}
                self.assertTrue(b.importPack(str(EXAMPLE)));b.selectLab(SCENARIO.key,True)
                self.assertFalse(b.view['canEditVirtualFile']);self.assertFalse(b.view['dirty'])
                b.hint();b.execute('pwd');b.execute('ls');b.setCommandDraft('cd Documents');b.test();b.flush()
                old=b.view['attemptId'];state=deepcopy(b.session.attempt)
                for lab in b.labs.values():lab.timer.stop()
                b=build();self.assertEqual(b.session.attempt,state);self.assertEqual(b.view['guide']['index'],2)
                self.assertEqual(b.view['commandDraft'],'cd Documents')
                for command in COMMANDS[2:]:b.execute(command)
                b.submit();raw=b.store.current.read_bytes();b.submit();self.assertEqual(b.store.current.read_bytes(),raw)
                self.assertEqual(b.view['grade']['score'],100);self.assertEqual(b.view['hintCount'],1)
                b.restart('Challenge');self.assertEqual(b.session.engine.grade()['score'],0)
                self.assertEqual(b.view['guide'],{});b.hint();self.assertEqual(b.view['hintCount'],0)
                self.assertEqual(b.store.history(b.view['attemptId'])[1],1)
                for command in ('cat '+WELCOME,'cd '+DOCUMENTS,'ls ..','cd ..','pwd','cd Projects'):b.execute(command)
                b.submit();self.assertEqual(b.view['grade']['score'],100)
                history=root/'personal.attempt.json';self.assertTrue(b.exportAttempt(str(history),old))
                self.assertIn(old,history.read_text());self.assertIn('activity',history.read_text())
                exported=root/'scenario.lab.json';self.assertTrue(b.exportScenario(str(exported)))
                self.assertEqual(exported.read_bytes(),SCENARIO.original_bytes);self.assertNotIn(old,exported.read_text())
                repo=PackRepository(root/'reimport');reimported,added=repo.import_file(exported)
                self.assertTrue(added);self.assertEqual(reimported.pin,SCENARIO.pin)
                fresh=reimported.domain().session();finish(fresh);self.assertEqual(fresh.submit()['score'],100)
                with self.assertRaises(ValidationError):repo.import_file(history)
                b.restart('Challenge');self.assertEqual(b.store.history(b.view['attemptId'])[1],2)
                self.assertEqual(b.session.attempt['applied']['activity'],{op:[] for op in ('pwd','ls','cd','cat')})
                self.assertEqual(b.view['commandDraft'],'');self.assertEqual(b.view['console'],'')
                b.restart('Learn');self.assertEqual(b.store.history(b.view['attemptId'])[1],3)
                for key in list(b.labs):b.selectLab(key,True)
                b.selectLab(SCENARIO.key,True);self.assertEqual(b.view['guide']['index'],0)
                for name,raw in original.items():self.assertEqual((root/'data'/name).read_bytes(),raw,name)
            finally:
                for b in catalogs:
                    for lab in b.labs.values():lab.timer.stop()
