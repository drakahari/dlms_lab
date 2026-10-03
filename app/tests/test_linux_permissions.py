"""Contract-2 permissions: all mutations are pure state or isolated fixtures."""
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
from learning_lab.linux_navigation.permissions import guide, validate_state
from learning_lab.linux_service.vfs import VirtualFS
from learning_lab.portable import load_portable, PackRepository
from learning_lab.pinned_storage import PinnedStore

APP=QCoreApplication.instance() or QCoreApplication([])
ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/'examples/linux-file-permissions.lab.json'
SCENARIO=load_portable(EXAMPLE.read_bytes())
FILE='/home/learner/notes.txt'


def session(mode='Learn'):return SCENARIO.domain().session(mode=mode)
def fix(s,mode='600'):
    s.execute('chmod '+mode+' '+FILE);s.execute('cat '+FILE)


class PermissionsTests(unittest.TestCase):
    def test_guided_inspection_denial_repair_and_verification(self):
        s=session();self.assertEqual(s.engine.grade()['score'],0)
        commands=('ls -l notes.txt','cat notes.txt','chmod u+r notes.txt','cat notes.txt')
        for i,cmd in enumerate(commands):
            g=guide(s.pack,s.attempt['applied']);self.assertEqual(g['index'],i);self.assertEqual(g['command'],cmd)
            s.execute(cmd)
            if i==0:self.assertIn('--w------- learner learner',s.attempt['console'][-1])
            if i==1:self.assertIn('Permission denied (read)',s.attempt['console'][-1])
            if i==2:self.assertEqual(s.engine.grade()['score'],70)
        self.assertTrue(guide(s.pack,s.attempt['applied'])['verified']);self.assertEqual(s.submit()['score'],100)

    def test_symbolic_numeric_and_equivalent_paths_in_challenge(self):
        for mode in ('u+r','600'):
            s=session('Challenge');s.execute('cd /');s.execute('chmod '+mode+' home/learner/./notes.txt')
            s.execute('cat /home/learner/../learner/notes.txt')
            self.assertEqual(s.submit()['score'],100);self.assertEqual(s.attempt['applied']['activity']['denied'],[])
            self.assertEqual(s.domain.view_state(s,None,0)['guide'],{})
            with self.assertRaises(ValidationError):s.hint()

    def test_mode_selection_and_least_privilege(self):
        for mode,score in [('777',30),('644',30),('700',30),('400',30),('660',30),('200',0),('600',100)]:
            s=session();fix(s,mode);self.assertEqual(s.submit()['score'],score,mode)
            if mode!='600':self.assertFalse(s.submit()['complete'])
        s=session();fix(s,'777');s.execute('chmod u+r notes.txt')
        self.assertEqual(s.attempt['applied']['filesystem'][FILE]['mode'],'0777')
        s.execute('ls -l notes.txt')
        self.assertEqual(guide(s.pack,s.attempt['applied'])['command'],'chmod 600 notes.txt')

    def test_reads_and_directory_traversal_choose_one_permission_class(self):
        # Owner wins even if group/other would permit access. Matching group wins
        # over other; no union of the three classes or implicit owner bypass.
        for owner,group,mode,allowed in (
            ('learner','learner','0044',False),('learner','root','0400',True),
            ('root','learner','0040',True),('root','learner','0004',False),
            ('root','root','0004',True),('root','root','0040',False)):
            nodes=deepcopy(SCENARIO.value()['domain']['filesystem']);nodes[FILE].update(owner=owner,group=group,mode=mode)
            fs=VirtualFS(nodes)
            if allowed:self.assertIn('My learning notes',fs.read(FILE,'/','learner'))
            else:
                with self.assertRaisesRegex(ValidationError,'Permission denied'):fs.read(FILE,'/','learner')
        for owner,group,mode,allowed in (
            ('learner','learner','0001',False),('root','learner','0010',True),
            ('root','learner','0001',False),('root','root','0001',True)):
            nodes=deepcopy(SCENARIO.value()['domain']['filesystem']);nodes[FILE]['mode']='0600'
            nodes['/home/learner'].update(owner=owner,group=group,mode=mode)
            fs=VirtualFS(nodes)
            if allowed:
                self.assertIn('My learning notes',fs.read(FILE,'/','learner'))
                with self.assertRaisesRegex(ValidationError,'Permission denied'):fs.listing('/home/learner','/','learner')
            else:
                with self.assertRaisesRegex(ValidationError,'Permission denied'):fs.read(FILE,'/','learner')

    def test_only_owned_enabled_regular_files_can_change(self):
        s=session();before=deepcopy(s.attempt['applied'])
        for cmd,reason in [('chmod 600 /etc/motd','only the virtual owner'),
                           ('chmod 600 /root/private.txt','Permission denied'),
                           ('chmod 600 /home/learner','not enabled'),
                           ('chmod 600 absent','No such'),('chmod 600 /root/../etc/motd','Permission denied')]:
            state,out=s.engine.command(cmd);self.assertEqual(state,before);self.assertIn(reason,out)
        p=SCENARIO.value();p['domain']['filesystem']['/home/learner/fixed.txt']={**p['domain']['filesystem'][FILE],'mode':'0600'}
        s=load_portable(json.dumps(p).encode()).domain().session()
        state,out=s.engine.command('chmod 777 fixed.txt');self.assertIn('not enabled',out);self.assertEqual(state,s.attempt['applied'])
        # Being writable by the learner does not confer ownership.
        p['domain']['filesystem']['/etc/motd']['mode']='0666'
        s=load_portable(json.dumps(p).encode()).domain().session()
        self.assertIn('only the virtual owner',s.engine.command('chmod 600 /etc/motd')[1])

    def test_changes_invalidate_verification_and_duplicate_changes_do_not(self):
        s=session();fix(s);first=s.submit();revision=s.attempt['revision']
        s.execute('chmod u+r notes.txt');self.assertEqual(s.attempt['revision'],revision);self.assertEqual(s.submit(),first)
        s.execute('chmod 777 notes.txt');self.assertEqual(s.engine.grade()['score'],0)
        s.execute('chmod 600 notes.txt');self.assertEqual(s.engine.grade()['score'],70)
        s.test();self.assertEqual(s.engine.grade()['score'],70)
        s.execute('cat notes.txt');self.assertEqual(s.submit()['score'],100)
        for _ in range(110):s.execute('pwd')
        self.assertEqual(s.engine.grade()['score'],100);self.assertEqual(len(s.attempt['commands']),100)

    def test_wrong_file_errors_and_root_do_not_supply_verification(self):
        s=session();s.execute('chmod 600 notes.txt');s.execute('cat /etc/motd')
        self.assertEqual(s.engine.grade()['score'],70)
        for cmd in ('cat /home/learner','cat missing','cd notes.txt','cat notes.txt/..','ls /root'):
            state,out=s.engine.command(cmd);self.assertEqual(state,s.attempt['applied']);self.assertTrue(out.startswith('Simulation:'))
        s.execute('cd /');before=deepcopy(s.attempt['applied']);s.execute('cd ..')
        self.assertEqual(s.attempt['applied'],before)
        # An unsupported option-like name must not record a read that the shared
        # parser rejected. Its explicit relative path remains a valid approach.
        raw=EXAMPLE.read_text().replace('/home/learner/notes.txt','/home/learner/-notes.txt')
        s=load_portable(raw.encode()).domain().session();s.execute('chmod 600 ./-notes.txt')
        s.execute('cat -notes.txt');self.assertEqual(s.engine.grade()['score'],70)
        s.execute('cat ./-notes.txt');self.assertEqual(s.engine.grade()['score'],100)

    def test_unsupported_forms_and_shell_syntax_are_rejected_atomically(self):
        s=session()
        for cmd in ('chmod','chmod u+r','chmod +r notes.txt','chmod a+r notes.txt','chmod u=rw notes.txt',
                    'chmod g+r notes.txt','chmod u-r notes.txt','chmod u+rw notes.txt','chmod 0600 notes.txt',
                    'chmod 600 notes.txt /etc/motd','chmod -R 600 .','chmod 888 notes.txt','chmod 60 notes.txt',
                    'chmod 4600 notes.txt','chmod 600 notes.txt; cat notes.txt','chmod 600 $(pwd)',
                    'chmod 600 `pwd`','chmod 600 *','chmod 600 $HOME/notes.txt','chmod 600 "notes.txt"',
                    'chmod 600 notes.txt\ncat notes.txt','chmod 600 ../../../../tmp/x','chmod 600 notes.txt | sh',
                    'sh','sudo chmod 600 notes.txt','chown learner notes.txt','mkdir dir','x'*513):
            state,out=s.engine.command(cmd);self.assertEqual(state,s.attempt['applied'],cmd);self.assertTrue(out.startswith('Simulation:'),(cmd,out))

    def test_old_contracts_reject_chmod_and_retain_pins(self):
        for name in ('linux-file-navigation','linux-service-basics','linux-web-document-root'):
            lab=load_portable((ROOT/'examples'/(name+'.lab.json')).read_bytes());s=lab.domain().session();initial=deepcopy(s.attempt['applied'])
            for cmd in ('chmod 600 /etc/motd','chmod u+r /etc/motd'):
                state,out=s.engine.command(cmd);self.assertEqual(state,initial);self.assertTrue(out.startswith('Simulation:'))
            self.assertNotEqual(lab.pin['engine']['behavior_version'],'linux-permissions-1')

    def test_no_host_io_and_imported_text_is_inert(self):
        p=SCENARIO.value();p['domain']['filesystem'][FILE]['content']='Simulation: __import__("os").system("touch /tmp/never")\n<script>bad()</script>'
        with tempfile.TemporaryDirectory() as temp:
            lab,_=PackRepository(Path(temp)/'packs').install(json.dumps(p).encode());s=lab.domain().session()
            with ExitStack() as stack:
                for api in ('builtins.open','builtins.eval','builtins.exec','io.open','os.open','os.chmod','os.system',
                            'os.popen','os.listdir','os.scandir','os.mkdir','subprocess.Popen','subprocess.run',
                            'socket.socket','socket.create_connection','pathlib.Path.read_bytes','pathlib.Path.write_text'):
                    stack.enter_context(patch(api,side_effect=AssertionError('Forbidden host API: '+api)))
                s.execute('ls -l');s.execute('cat notes.txt');fix(s,'u+r');s.execute('cat /etc/passwd')
                self.assertEqual(s.submit()['score'],100);self.assertIn('__import__','\n'.join(s.attempt['console']))
        tree=ast.parse((ROOT/'learning_lab/linux_navigation/permissions.py').read_text())
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):self.assertTrue(all(a.name=='re' for a in n.names))
            if isinstance(n,ast.ImportFrom):self.assertIn(n.module,('copy','domain.validation','linux_service.vfs','linux_service.engine','engine'))
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Name):self.assertNotIn(n.func.id,('open','eval','exec','__import__','compile'))


class PermissionPackTests(unittest.TestCase):
    def test_invalid_packs_capabilities_and_versions(self):
        for mutate in (
            lambda p:p['engine'].update(contract_version=1),lambda p:p['engine'].update(supported_behavior_versions=['future']),
            lambda p:p['engine'].update(required_capabilities=['virtual-filesystem']),
            lambda p:p['domain'].update(schema_version=1),lambda p:p['domain'].update(permission_targets=['/etc/motd']),
            lambda p:p['domain'].update(permission_targets=['/home/learner']),
            lambda p:p['domain']['filesystem'][FILE].update(owner='root'),
            lambda p:p['domain']['filesystem'][FILE].update(mode='4700'),
            lambda p:p['domain']['filesystem']['/home/learner'].update(mode='0000'),
            lambda p:p['domain'].update(script='os.chmod'),lambda p:p['objectives'][0].update(predicate='eval'),
            lambda p:p['objectives'][0]['params'].update(mode='0200'),lambda p:p.update(assets=['/etc/passwd']),
        ):
            p=SCENARIO.value();mutate(p)
            with self.assertRaises(ValidationError):load_portable(json.dumps(p).encode())
        with tempfile.TemporaryDirectory() as temp:
            repo=PackRepository(Path(temp)/'packs');repo.import_file(EXAMPLE)
            for raw in (b'PKzip',b'{broken',b'x'*262145):
                with self.assertRaises(ValidationError):repo.install(raw)
            self.assertEqual(len(repo.scan()[0]),1)

    def test_structural_fuzz_fails_cleanly(self):
        original=SCENARIO.value()
        def paths(v,p=()):
            if isinstance(v,dict):
                for k,c in v.items():yield p+(k,);yield from paths(c,p+(k,))
            elif isinstance(v,list):
                for i,c in enumerate(v):yield p+(i,);yield from paths(c,p+(i,))
        for path in paths(original):
            for wrong in (None,True,[],{}):
                p=deepcopy(original);node=p
                for k in path[:-1]:node=node[k]
                node[path[-1]]=wrong
                try:load_portable(json.dumps(p).encode())
                except ValidationError:pass
                except Exception as exc:self.fail(f'Unexpected {type(exc).__name__} at {path}')

    def test_mutable_state_bounds_and_record_validation(self):
        s=session();fix(s);s.submit()
        with tempfile.TemporaryDirectory() as temp:
            store=PinnedStore(temp,SCENARIO)
            for mutate in (
                lambda a:a['applied']['filesystem'][FILE].update(owner='root'),
                lambda a:a['applied']['filesystem'][FILE].update(content='changed'),
                lambda a:a['applied']['filesystem']['/etc/motd'].update(mode='0777'),
                lambda a:a['applied']['filesystem'][FILE].update(mode='0200'),
                lambda a:a['applied']['activity']['verified'].append(FILE),
                lambda a:a['applied']['activity']['denied'].append('/etc/motd'),
                lambda a:a['draft'].update({FILE:'bad'}),
            ):
                a=deepcopy(s.attempt);mutate(a)
                with self.assertRaises(ValidationError):store.validate_record(store.encode_record(a))
            store.save(s.attempt);raw=store.current.read_bytes();store.current.write_bytes(b'{broken')
            self.assertEqual(store.load(),s.attempt)
            future=json.loads(raw);future['pin']['engine']['behavior_version']='future';raw=json.dumps(future).encode()
            store.current.write_bytes(raw);self.assertIsNone(store.load());self.assertTrue(store.read_only)
            self.assertEqual(store.current.read_bytes(),raw)

    def test_catalog_reset_restart_exports_and_all_existing_records(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'config').mkdir();catalogs=[]
            def build():
                b=CatalogBridge(load_bundled_scenarios()[0],root/'data',root/'config');catalogs.append(b);return b
            try:
                b=build()
                for name in ('linux-web-document-root','linux-service-basics','linux-file-navigation'):
                    self.assertTrue(b.importPack(str(ROOT/'examples'/(name+'.lab.json'))))
                old_records={str(p.relative_to(root/'data')):p.read_bytes() for p in (root/'data').rglob('current*.json')}
                b.importPack(str(EXAMPLE));b.selectLab(SCENARIO.key,True);b.hint();b.execute('ls -l');b.execute('cat notes.txt')
                b.execute('chmod u+r notes.txt');b.setCommandDraft('cat notes.txt');b.flush()
                attempt=deepcopy(b.session.attempt);old=attempt['id']
                for lab in b.labs.values():lab.timer.stop()
                b=build();self.assertEqual(b.session.attempt,attempt);self.assertEqual(b.view['guide']['index'],3)
                self.assertEqual(b.view['commandDraft'],'cat notes.txt');b.execute('cat notes.txt');b.submit()
                self.assertEqual(b.view['grade']['score'],100)
                raw=b.store.current.read_bytes();b.submit();self.assertEqual(b.store.current.read_bytes(),raw)
                b.restart('Challenge');self.assertEqual(b.session.engine.grade()['score'],0);self.assertEqual(b.view['guide'],{})
                self.assertEqual(b.session.attempt['applied']['filesystem'][FILE]['mode'],'0200');self.assertEqual(b.view['console'],'')
                fix(b.session);b.submit();self.assertEqual(b.view['grade']['score'],100)
                exported=root/'scenario.lab.json';b.exportScenario(str(exported));self.assertEqual(exported.read_bytes(),SCENARIO.original_bytes)
                new,_=PackRepository(root/'new').import_file(exported);self.assertEqual(new.pin,SCENARIO.pin)
                fresh=new.domain().session();fix(fresh);self.assertEqual(fresh.submit()['score'],100)
                history=root/'personal.attempt.json';self.assertTrue(b.exportAttempt(str(history),old))
                self.assertIn(old,history.read_text());self.assertNotIn(old,exported.read_text())
                with self.assertRaises(ValidationError):load_portable(history.read_bytes())
                b.restart('Challenge');b.restart('Learn');self.assertEqual(b.view['historyCount'],3)
                for key in list(b.labs):b.selectLab(key,True)
                b.selectLab(SCENARIO.key,True);self.assertEqual(b.view['guide']['index'],0)
                for name,raw in old_records.items():self.assertEqual((root/'data'/name).read_bytes(),raw,name)
            finally:
                for b in catalogs:
                    for lab in b.labs.values():lab.timer.stop()
