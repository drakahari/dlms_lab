"""Engine checkpoint: trusted contract 4, temporary/dictionary fixtures only."""
import ast
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from learning_lab.domain.validation import ValidationError
from learning_lab.portable import load_portable
from learning_lab.linux_navigation.file_management import CAPABILITIES, guide, validate_state

ROOT=Path(__file__).resolve().parents[1]
HOME='/home/learner'
REF='/opt/reference/note.txt'
OUT=HOME+'/note.txt'


def node(kind='directory',content='',mode='0755',owner='root',group='root'):
    return {'kind':kind,'content':content,'mode':mode,'owner':owner,'group':group}


def fixture():
    value=json.loads((ROOT/'examples/linux-file-navigation.lab.json').read_text())
    value['identity']={'id':'file-management-fixture','content_version':'1.0.0'}
    value['engine']={'id':'linux-navigation','contract_version':4,'supported_behavior_versions':['linux-file-management-1'],'required_capabilities':sorted(CAPABILITIES)}
    value['domain']={'schema_version':2,'cwd':HOME,'mutable_roots':[HOME],
        'filesystem':{'/':node(),'/home':node(),HOME:node(owner='learner',group='learner'),
            '/opt':node(),'/opt/reference':node(),REF:node('file','Reference note.\n','0644'),
            HOME+'/scratch':node(owner='learner',group='learner'),
            HOME+'/scratch/junk.txt':node('file','Disposable.\n','0200','learner','learner'),
            HOME+'/locked':node(mode='0500',owner='learner',group='learner'),
            HOME+'/secret':node(mode='0700'),HOME+'/secret/private.txt':node('file','Private.','0600')},
        'lesson':{'goal':'Copy the reference and read the final copy.','steps':[
            {'objective':'copy','command':'cp -n '+REF+' '+OUT,'explanation':'Copy without clobbering.','expected':'A copy.'},
            {'objective':'read','command':'cat '+OUT,'explanation':'Verify the final copy.','expected':'Reference note.'}]}}
    value['objectives']=[{'id':'copy','label':'Final copy matches','points':70,'predicate':'file_matches_initial','params':{'path':OUT,'source':REF}},
        {'id':'read','label':'Action: read final copy','points':30,'predicate':'activity_observed','params':{'path':OUT,'operation':'cat'}}]
    return value


def scenario(value=None):return load_portable(json.dumps(value or fixture()).encode())
def session(value=None,mode='Learn'):return scenario(value).domain().session(mode=mode)


class FileManagementEngineTests(unittest.TestCase):
    def test_contract_pin_guidance_both_modes(self):
        lab=scenario();self.assertEqual(lab.pin['engine']['contract_version'],4)
        for mode in ('Learn','Challenge'):
            s=lab.domain().session(mode=mode);self.assertEqual(s.domain.view_state(s,None,0)['guide']=={},mode=='Challenge')
            s.execute('cp -n '+REF+' ./note.txt');self.assertEqual(s.engine.grade()['score'],70)
            s.execute('cat '+OUT);self.assertEqual(s.submit()['score'],100)
        self.assertEqual(guide(s.pack,s.attempt['applied'])['verified'],True)

    def test_mkdir_parents_dot_paths_and_metadata(self):
        s=session();s.execute('mkdir -p work/drafts');s.execute('mkdir work/final/')
        for path in ('work','work/drafts','work/final'):
            self.assertEqual(s.attempt['applied']['filesystem'][HOME+'/'+path],node(owner='learner',group='learner'))
        before=deepcopy(s.attempt['applied']);s.execute('mkdir -p work/drafts');self.assertEqual(s.attempt['applied'],before)
        for cmd in ('mkdir work','mkdir absent/child','mkdir new/.','mkdir -p new2/../../../../escape','mkdir /etc/test'):
            self.assert_no_change(s,cmd)
        self.assertNotIn(HOME+'/new2',s.attempt['applied']['filesystem'])

    def assert_no_change(self,s,cmd,fragment='Simulation:'):
        before=deepcopy(s.attempt['applied']);state,out=s.engine.command(cmd)
        self.assertEqual(state,before,cmd);self.assertIn(fragment,out,cmd)

    def test_copy_directory_destination_mode_owner_and_no_clobber(self):
        s=session();s.execute('cp -n '+REF+' scratch');p=HOME+'/scratch/note.txt';n=s.attempt['applied']['filesystem'][p]
        self.assertEqual(n,node('file','Reference note.\n','0644','learner','learner'))
        before=deepcopy(s.attempt['applied']);s.execute('cp -n '+REF+' scratch');self.assertEqual(s.attempt['applied'],before)
        self.assertIn('Skipped existing','\n'.join(s.attempt['console']))
        for cmd in ('cp -n /opt/reference scratch','cp -n missing.txt scratch','cp -n '+REF+' absent/new.txt','cp -n '+REF+' locked/new.txt','cp -n '+REF+' /opt/new.txt','cp -n secret/private.txt scratch'):
            self.assert_no_change(s,cmd)

    def test_move_preserves_metadata_requires_parent_not_file_read(self):
        s=session();old=deepcopy(s.attempt['applied']['filesystem'][HOME+'/scratch/junk.txt'])
        s.execute('mv -n scratch/junk.txt renamed.txt')
        self.assertNotIn(HOME+'/scratch/junk.txt',s.attempt['applied']['filesystem'])
        self.assertEqual(s.attempt['applied']['filesystem'][HOME+'/renamed.txt'],old)
        s.execute('cp -n '+REF+' scratch');before=deepcopy(s.attempt['applied'])
        s.execute('mv -n renamed.txt scratch/note.txt');self.assertEqual(s.attempt['applied'],before)
        for cmd in ('mv -n scratch note-dir','mv -n '+REF+' note.txt','mv -n renamed.txt locked','mv -n renamed.txt /opt/renamed.txt'):
            self.assert_no_change(s,cmd)

    def test_remove_and_rmdir_boundaries(self):
        s=session();s.execute('rm scratch/junk.txt');s.execute('rmdir scratch')
        self.assertNotIn(HOME+'/scratch',s.attempt['applied']['filesystem'])
        s.execute('mkdir work');s.execute('cd work')
        for cmd in ('rmdir .','rmdir ..','rm .','rm /opt/reference/note.txt','rmdir /home/learner','rmdir /home/learner/secret'):
            self.assert_no_change(s,cmd)
        s.execute('cd ..');s.execute('rmdir work');self.assertNotIn(HOME+'/work',s.attempt['applied']['filesystem'])

    def test_search_matching_order_permissions_and_atomic_denial(self):
        s=session();s.execute('cp -n '+REF+' note.txt')
        for cmd in ('find /opt/reference -type f -name note.txt','find /opt/reference -name note.txt -type f','find '+OUT):
            s.execute(cmd);self.assertIn(REF if '/opt' in cmd else OUT,s.attempt['applied']['activity']['find'])
        state,out=s.engine.command('find /opt -type d');self.assertIn('/opt/reference',out);self.assertNotIn(REF,out)
        before=deepcopy(s.attempt['applied']);state,out=s.engine.command('find /home/learner -type f');self.assertEqual(state,before);self.assertIn('Permission denied',out)
        state,out=s.engine.command('find /opt -name absent');self.assertIn('no matching',out)

    def test_verification_invalidated_only_by_actual_mutation(self):
        s=session();s.execute('cp -n '+REF+' note.txt');s.execute('cat note.txt');s.execute('find note.txt')
        self.assertEqual(s.engine.grade()['score'],100);before=deepcopy(s.attempt['applied'])
        s.execute('cp -n '+REF+' note.txt');self.assertEqual(s.attempt['applied'],before)
        s.execute('mkdir work');self.assertEqual(s.attempt['applied']['activity']['cat'],[]);self.assertEqual(s.attempt['applied']['activity']['find'],[])
        self.assertEqual(s.engine.grade()['score'],70);s.execute('cat note.txt');self.assertEqual(s.submit()['score'],100)

    def test_path_walk_does_not_bypass_permissions_or_missing_parents(self):
        s=session()
        for cmd in ('mkdir secret/../work','cp -n '+REF+' secret/../out.txt','mv -n scratch/junk.txt absent/../renamed.txt','rm secret/../scratch/junk.txt','find /../../opt','cat /opt/reference/note.txt/../note.txt'):
            self.assert_no_change(s,cmd)

    def test_group_other_permissions_and_nonowner_removal(self):
        for mode,group in (('0030','learner'),('0003','root')):
            value=fixture();path=HOME+'/shared';value['domain']['filesystem'][path]=node(mode=mode,group=group)
            file=path+'/unreadable.txt';value['domain']['filesystem'][file]=node('file','Owned by root.','0000')
            s=session(value);s.execute('mkdir shared/new')
            self.assertIn(path+'/new',s.attempt['applied']['filesystem'])
            self.assert_no_change(s,'cat shared/unreadable.txt','Permission denied')
            self.assert_no_change(s,'cp -n shared/unreadable.txt copy.txt','Permission denied')
            s.execute('mv -n shared/unreadable.txt root-file.txt')
            self.assertEqual(s.attempt['applied']['filesystem'][HOME+'/root-file.txt']['owner'],'root')
            s.execute('rm root-file.txt');self.assertNotIn(HOME+'/root-file.txt',s.attempt['applied']['filesystem'])
        # Owner permissions win even if the matching group/other bits allow more.
        value=fixture();value['domain']['filesystem'][HOME+'/locked'].update(mode='0033')
        self.assert_no_change(session(value),'mkdir locked/new','Permission denied')

    def test_collision_wrong_kind_and_same_file_are_atomic(self):
        value=fixture();value['domain']['filesystem'][HOME+'/scratch/note.txt']=node(owner='learner',group='learner')
        s=session(value);self.assert_no_change(s,'cp -n '+REF+' scratch','Target is not')
        s.execute('cp -n '+REF+' note.txt');before=deepcopy(s.attempt['applied'])
        for cmd in ('cp -n note.txt ./note.txt','mv -n note.txt ./note.txt'):
            state,out=s.engine.command(cmd);self.assertEqual(state,before);self.assertIn('Skipped existing',out)

    def test_removed_directory_path_can_be_reused_with_supported_operations(self):
        s=session();s.execute('rm scratch/junk.txt');s.execute('rmdir scratch')
        s.execute('cp -n '+REF+' scratch')
        self.assertEqual(s.attempt['applied']['filesystem'][HOME+'/scratch']['kind'],'file')
        s.execute('rm scratch');s.execute('mkdir scratch')
        self.assertEqual(s.attempt['applied']['filesystem'][HOME+'/scratch'],node(owner='learner',group='learner'))

    def test_unsupported_syntax_hostile_strings_atomic(self):
        s=session()
        for cmd in ('cp '+REF+' note.txt','mv scratch/junk.txt note.txt','cp -r /opt work','mv -f a b','rm -rf scratch','rmdir -p scratch','find . -exec sh','find . -delete','find . -size 1','find . -name *.txt','find . -type f -type d','find . -name','find . extra','mkdir -m 777 work','touch file','chmod 600 file','ls -a','pwd; mkdir x','$(pwd)','cat $HOME/key','ls | sh','pwd\nls','x'*513):
            self.assert_no_change(s,cmd)

    def test_node_file_and_total_limits_are_atomic(self):
        s=session()
        for i in range(117):s.execute('mkdir d'+str(i))
        self.assertEqual(len(s.attempt['applied']['filesystem']),128)
        self.assert_no_change(s,'mkdir -p overflow/child');self.assert_no_change(s,'cp -n '+REF+' note.txt')
        value=fixture();value['domain']['filesystem'][REF]['content']='x'*8192
        t=session(value)
        for i in range(7):t.execute('cp -n '+REF+' copy'+str(i))
        self.assert_no_change(t,'cp -n '+REF+' overflow')
        bad=fixture();bad['domain']['filesystem'][REF]['content']='x'*8193
        with self.assertRaises(ValidationError):scenario(bad)

    def test_imported_pack_and_restored_state_validation(self):
        changes=[lambda p:p['engine'].update(contract_version=5),lambda p:p['engine'].update(supported_behavior_versions=['future']),
          lambda p:p['engine']['required_capabilities'].append('host-shell'),lambda p:p['domain'].update(mutable_roots=['/']),
          lambda p:p['domain'].update(mutable_roots=[HOME+'/secret']),lambda p:p['domain'].update(mutable_roots=[HOME,HOME+'/scratch']),
          lambda p:p['objectives'][0].update(predicate='eval'),lambda p:p['objectives'][0]['params'].update(source='/missing'),
          lambda p:p['domain']['lesson']['steps'][0].update(command='rm -rf /'),lambda p:p['domain']['lesson']['steps'][0].update(command='pwd'),
          lambda p:p['domain'].update(script='arbitrary'),lambda p:p.update(assets=['/etc/passwd'])]
        for change in changes:
            v=fixture();change(v)
            with self.subTest(change=change),self.assertRaises(ValidationError):scenario(v)
        s=session()
        for mutate in (lambda state:state['filesystem'][REF].update(content='changed'),lambda state:state['filesystem'][HOME].update(mode='0777'),
                       lambda state:state['filesystem'].update({'/escape':node()}),lambda state:state['activity']['find'].append('/absent')):
            state=deepcopy(s.attempt['applied']);mutate(state)
            with self.assertRaises(ValidationError):validate_state(s.pack,state)

    def test_no_host_apis_for_commands_or_pack_content(self):
        value=fixture();value['domain']['filesystem'][REF]['content']='__import__("os").system("bad")\n'
        s=session(value)
        with ExitStack() as stack:
            for api in ('builtins.open','io.open','os.open','os.system','os.popen','os.listdir','os.scandir','os.mkdir','os.remove','os.rename','os.chmod','subprocess.Popen','subprocess.run','socket.socket','socket.create_connection','pathlib.Path.read_bytes','pathlib.Path.write_text'):
                stack.enter_context(patch(api,side_effect=AssertionError('Forbidden host API: '+api)))
            for cmd in ('mkdir work','cp -n '+REF+' work','mv -n work/note.txt work/final.txt','find work -type f','cat work/final.txt','rm work/final.txt','rmdir work','cat /etc/passwd'):
                s.execute(cmd)
            self.assertIn('__import__','\n'.join(s.attempt['console']))
        tree=ast.parse((ROOT/'learning_lab/linux_navigation/file_management.py').read_text())
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):self.assertTrue(all(a.name=='re' for a in n.names))
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Name):self.assertNotIn(n.func.id,('open','eval','exec','compile','__import__'))

    def test_contracts_one_two_three_keep_pins_bytes_and_reject_mutation(self):
        for name,contract in (('linux-file-navigation',1),('linux-file-permissions',2),('linux-directory-permissions',3)):
            raw=(ROOT/'examples'/(name+'.lab.json')).read_bytes();lab=load_portable(raw);s=lab.domain().session()
            self.assertEqual(lab.original_bytes,raw);self.assertEqual(lab.pin['engine']['contract_version'],contract)
            for cmd in ('mkdir work','cp -n file other','mv -n file other','find .','rm file','rmdir work'):
                self.assert_no_change(s,cmd)
