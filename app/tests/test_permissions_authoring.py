"""Directory permissions and data-only authoring against the versioned engine."""
from contextlib import ExitStack
from copy import deepcopy
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.domain.validation import ValidationError
from learning_lab.linux_navigation.permissions import guide
from learning_lab.portable import load_portable, PackRepository
from learning_lab.pinned_storage import PinnedStore

APP=QCoreApplication.instance() or QCoreApplication([])
ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/'examples/linux-directory-permissions.lab.json'
TEMPLATE=ROOT/'templates/linux-permissions.lab.json'
LAB=load_portable(EXAMPLE.read_bytes())
DIRECTORY='/home/learner/Research';NOTE=DIRECTORY+'/welcome.txt'


def session(mode='Learn'):return LAB.domain().session(mode=mode)
def fix(s,mode='u+x'):
    for c in ('chmod '+mode+' '+DIRECTORY,'cd '+DIRECTORY,'cat '+NOTE):s.execute(c)


class DirectoryTests(unittest.TestCase):
    def test_baseline_read_lists_names_but_search_fails(self):
        s=session();s.execute('ls Research');self.assertEqual(s.attempt['console'][-1],'welcome.txt')
        self.assertEqual(s.engine.grade()['score'],0)
        for c in ('cd Research','cat Research/welcome.txt','ls -l Research'):
            s.execute(c);self.assertIn('Permission denied',s.attempt['console'][-1]);self.assertEqual(s.attempt['applied']['cwd'],'/home/learner')
        s.execute('ls -l .');self.assertTrue(any('dr-------- learner learner '+DIRECTORY in line for line in s.attempt['console']))
        self.assertEqual(s.engine.grade()['score'],0)

    def test_guided_steps_and_symbolic_repair(self):
        s=session();commands=('ls -l .','ls Research','cd Research','chmod u+x Research','cd Research','cat welcome.txt')
        for i,cmd in enumerate(commands):
            g=guide(s.pack,s.attempt['applied']);self.assertEqual(g['index'],i);self.assertEqual(g['command'],cmd)
            s.execute(cmd)
        self.assertTrue(guide(s.pack,s.attempt['applied'])['verified']);self.assertEqual(s.submit()['score'],100)

    def test_challenge_equivalence_and_no_initial_mistake(self):
        for mode in ('u+x','500'):
            s=session('Challenge');s.execute('chmod '+mode+' ./Research')
            s.execute('cat Research/./welcome.txt');self.assertEqual(s.engine.grade()['score'],85)
            s.execute('cd /home/learner/../learner/Research');self.assertEqual(s.submit()['score'],100)
            self.assertEqual(s.attempt['applied']['activity']['denied'],[])
            self.assertEqual(s.domain.view_state(s,None,0)['guide'],{})
            with self.assertRaises(ValidationError):s.hint()

    def test_incorrect_modes_search_only_and_reverification(self):
        for mode,score in [('400',0),('600',0),('000',0),('100',30),('700',30),('777',30),('500',100)]:
            s=session();fix(s,mode);self.assertEqual(s.engine.grade()['score'],score,mode)
            if mode=='100':
                s.execute('ls '+DIRECTORY);self.assertIn('Permission denied (list names)',s.attempt['console'][-1])
                s.execute('cat '+NOTE);self.assertIn('file also needs','\n'.join(s.attempt['console']))
        s=session();fix(s);old=s.submit();revision=s.attempt['revision']
        s.execute('chmod 500 '+DIRECTORY);self.assertEqual(s.attempt['revision'],revision);self.assertEqual(s.submit(),old)
        s.execute('chmod 700 '+DIRECTORY);s.execute('chmod 500 '+DIRECTORY)
        self.assertEqual(s.engine.grade()['score'],70)
        s.test();self.assertEqual(s.engine.grade()['score'],70)
        s.execute('cd .');s.execute('cat welcome.txt');self.assertEqual(s.engine.grade()['score'],100)

    def test_remove_search_while_inside_remains_persistable_and_recoverable(self):
        s=session();fix(s);s.execute('chmod 400 '+DIRECTORY)
        self.assertEqual(s.attempt['applied']['cwd'],DIRECTORY);s.execute('pwd');self.assertEqual(s.attempt['console'][-1],DIRECTORY)
        s.execute('cat welcome.txt');self.assertIn('Permission denied',s.attempt['console'][-1])
        s.execute('cd ..');self.assertEqual(s.attempt['applied']['cwd'],DIRECTORY)
        with tempfile.TemporaryDirectory() as t:
            store=PinnedStore(t,LAB);store.save(s.attempt);self.assertEqual(store.load(),s.attempt)
        s.execute('cd /');s.execute('chmod u+x '+DIRECTORY);s.execute('cd '+DIRECTORY);s.execute('cat welcome.txt')
        self.assertEqual(s.submit()['score'],100)

    def test_ownership_fixed_nodes_and_unsupported_forms(self):
        s=session()
        for cmd in ('chmod 777 /home/learner','chmod u+x /etc/motd','chmod 777 Research/welcome.txt',
                    'chmod 777 /root/../home/learner/Research','chmod 0500 Research','chmod u+rx Research',
                    'chmod -R 500 Research','chmod a+x Research','chmod 500 Research; cd Research',
                    'ls Research | sh','cat $(pwd)','chmod 500 ../../../../tmp/x','ls *'):
            state,out=s.engine.command(cmd);self.assertEqual(state,s.attempt['applied'],cmd);self.assertTrue(out.startswith('Simulation:'),out)
        fix(s);before=deepcopy(s.attempt['applied']);s.execute('chmod 777 welcome.txt')
        self.assertEqual(s.attempt['applied'],before);self.assertIn('not enabled',s.attempt['console'][-1])

    def test_names_only_listing_selects_one_permission_class(self):
        for owner,group,mode,allowed in [('learner','learner','0004',False),('root','learner','0040',True),('root','learner','0004',False),('root','root','0004',True)]:
            p=LAB.value();p['domain']['filesystem']['/shared']={'kind':'directory','owner':owner,'group':group,'mode':mode,'content':''}
            p['domain']['filesystem']['/shared/name.txt']={'kind':'file','owner':'root','group':'root','mode':'0000','content':'inaccessible'}
            s=load_portable(json.dumps(p).encode()).domain().session();s.execute('ls /shared')
            self.assertEqual(s.attempt['console'][-1]=='name.txt',allowed)
            s.execute('cat /shared/name.txt');self.assertIn('Permission denied',s.attempt['console'][-1])

    def test_contract_two_is_unchanged_and_cannot_accept_directory_pack(self):
        old=load_portable((ROOT/'examples/linux-file-permissions.lab.json').read_bytes());s=old.domain().session()
        for cmd in ('chmod u+x /home/learner','chmod 500 /home/learner'):
            state,out=s.engine.command(cmd);self.assertEqual(state,s.attempt['applied']);self.assertTrue(out.startswith('Simulation:'))
        self.assertEqual(old.pin['engine']['behavior_version'],'linux-permissions-1')
        p=LAB.value();p['engine'].update(contract_version=2,supported_behavior_versions=['linux-permissions-1'])
        with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())

    def test_simulation_safety_and_code_like_imported_text(self):
        p=LAB.value();p['domain']['filesystem'][NOTE]['content']='__import__("os").system("touch /tmp/never")\n<script>bad()</script>'
        s=load_portable(json.dumps(p).encode()).domain().session()
        with ExitStack() as stack:
            for api in ('builtins.open','builtins.eval','builtins.exec','io.open','os.open','os.chmod','os.system','os.popen','os.listdir','os.scandir','os.mkdir','subprocess.Popen','socket.socket','socket.create_connection'):
                stack.enter_context(patch(api,side_effect=AssertionError('Host API: '+api)))
            s.execute('ls Research');fix(s);self.assertEqual(s.submit()['score'],100)
            self.assertIn('__import__','\n'.join(s.attempt['console']))
        tree=ast.parse((ROOT/'learning_lab/linux_navigation/permissions_lesson.py').read_text())
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):self.fail('Unexpected module import')
            if isinstance(n,ast.ImportFrom):self.assertIn(n.module,('domain.validation','linux_service.vfs','engine','permissions'))
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Name):self.assertNotIn(n.func.id,('open','eval','exec','__import__','compile'))


class AuthoringTests(unittest.TestCase):
    def test_template_customization_without_scenario_specific_code(self):
        p=load_portable(TEMPLATE.read_bytes()).value();p['identity']['id']='authored-logbook'
        p['metadata']['title']='Recover my logbook'
        raw=json.dumps(p).replace('/home/learner/notes.txt','/home/learner/logbook.txt').encode()
        authored=load_portable(raw)
        with tempfile.TemporaryDirectory() as temp:
            repo=PackRepository(Path(temp)/'packs');repo.install(raw)
            for lab in (authored,LAB):
                for mode in ('Learn','Challenge'):
                    s=lab.domain().session(mode=mode)
                    for _ in range(16):
                        g=guide(s.pack,s.attempt['applied'])
                        if g['verified']:break
                        s.execute(g['command'])
                    self.assertEqual(s.submit()['score'],100)
        code=''.join(p.read_text() for p in (ROOT/'learning_lab').rglob('*.py'))
        self.assertNotIn('Research',code);self.assertNotIn('linux-directory-permissions',code)

    def test_read_only_validation_cli_and_invalid_pack(self):
        with tempfile.TemporaryDirectory() as temp:
            bad=Path(temp)/'bad.json';bad.write_bytes(b'{bad');before=bad.read_bytes()
            tool=ROOT/'tools/validate_scenario.py'
            good=subprocess.run([sys.executable,'-B',str(tool),str(TEMPLATE),str(EXAMPLE)],capture_output=True,text=True)
            self.assertEqual(good.returncode,0,good.stderr);self.assertEqual(good.stdout.count('VALID '),2)
            invalid=subprocess.run([sys.executable,'-B',str(tool),str(bad)],capture_output=True,text=True)
            self.assertEqual(invalid.returncode,1);self.assertEqual(bad.read_bytes(),before)
            self.assertEqual(list(Path(temp).iterdir()),[bad])

    def test_invalid_capabilities_paths_lessons_and_unsolvable_goals(self):
        for mutate in (
            lambda p:p['engine'].update(contract_version=4),lambda p:p['engine'].update(supported_behavior_versions=['future']),
            lambda p:p['engine'].update(required_capabilities=['directory-permissions']),lambda p:p['domain'].update(schema_version=2),
            lambda p:p['domain']['filesystem'][DIRECTORY].update(owner='root'),lambda p:p['domain'].update(permission_targets=['/']),
            lambda p:p['objectives'][0]['params'].update(mode='0400'),lambda p:p['objectives'][2]['params'].update(path=DIRECTORY),
            lambda p:p['domain']['lesson']['steps'][0].update(action='exec'),lambda p:p['domain']['lesson']['steps'][0].update(path='/etc/motd'),
            lambda p:p['domain']['lesson']['steps'][3].update(path='/etc/motd'),lambda p:p['domain'].update(script='print(1)'),
            lambda p:p.update(assets=['file:///tmp/x']),
        ):
            p=LAB.value();mutate(p)
            with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())

    def test_structural_fuzz_and_state_validation(self):
        def paths(v,p=()):
            if isinstance(v,dict):
                for k,c in v.items():yield p+(k,);yield from paths(c,p+(k,))
            elif isinstance(v,list):
                for i,c in enumerate(v):yield p+(i,);yield from paths(c,p+(i,))
        original=LAB.value()
        for path in paths(original):
            for wrong in (None,True,[],{}):
                p=deepcopy(original);node=p
                for k in path[:-1]:node=node[k]
                node[path[-1]]=wrong
                try:load_portable(json.dumps(p).encode())
                except ValidationError:pass
                except Exception as exc:self.fail(f'{path}: {type(exc).__name__}')
        s=session();fix(s)
        for mutate in (lambda a:a['activity']['traversed'].append(NOTE),lambda a:a['activity']['verified'].append('/etc/shadow'),
                       lambda a:a['filesystem'][NOTE].update(mode='0777'),lambda a:a['filesystem'][DIRECTORY].update(owner='root')):
            state=deepcopy(s.attempt['applied']);mutate(state)
            with self.assertRaises(ValidationError):s.domain.validate_state(state)

    def test_lifecycle_restart_pins_exports_and_preserved_existing_records(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'config').mkdir();catalogs=[]
            def build():
                b=CatalogBridge(load_bundled_scenarios()[0],root/'data',root/'config');catalogs.append(b);return b
            try:
                b=build()
                for name in ('linux-web-document-root','linux-service-basics','linux-file-navigation','linux-file-permissions'):
                    b.importPack(str(ROOT/'examples'/(name+'.lab.json')))
                old={str(p.relative_to(root/'data')):p.read_bytes() for p in (root/'data').rglob('current*.json')}
                b.importPack(str(EXAMPLE));b.selectLab(LAB.key,True);b.hint();b.execute('chmod u+x Research');b.execute('cd Research')
                b.setCommandDraft('cat welcome.txt');b.flush();attempt=deepcopy(b.session.attempt)
                for lab in b.labs.values():lab.timer.stop()
                b=build();self.assertEqual(b.session.attempt,attempt);self.assertEqual(b.view['commandDraft'],'cat welcome.txt')
                b.execute('cat welcome.txt');b.submit();self.assertEqual(b.view['grade']['score'],100)
                raw=b.store.current.read_bytes();b.submit();self.assertEqual(b.store.current.read_bytes(),raw)
                b.restart('Challenge');self.assertEqual(b.session.engine.grade()['score'],0);self.assertEqual(b.view['guide'],{})
                for c in ('chmod 500 Research','cat Research/welcome.txt','cd Research'):b.execute(c)
                b.submit();self.assertEqual(b.view['grade']['score'],100)
                exported=root/'directory.lab.json';b.exportScenario(str(exported));self.assertEqual(exported.read_bytes(),LAB.original_bytes)
                fresh,_=PackRepository(root/'new').import_file(exported);self.assertEqual(fresh.pin,LAB.pin)
                s=fresh.domain().session();fix(s);self.assertEqual(s.submit()['score'],100)
                personal=root/'personal.attempt.json';b.exportAttempt(str(personal),attempt['id']);self.assertIn(attempt['id'],personal.read_text())
                with self.assertRaises(ValidationError):load_portable(personal.read_bytes())
                b.restart('Challenge');b.restart('Learn');self.assertEqual(b.view['historyCount'],3)
                self.assertEqual(b.session.attempt['applied']['filesystem'][DIRECTORY]['mode'],'0400')
                for key in list(b.labs):b.selectLab(key,True)
                for path,raw in old.items():self.assertEqual((root/'data'/path).read_bytes(),raw)
            finally:
                for b in catalogs:
                    for lab in b.labs.values():lab.timer.stop()
