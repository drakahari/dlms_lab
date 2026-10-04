"""Contract checkpoint. GNU references live in a separate static-fixture harness."""
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from learning_lab.portable import load_portable
from learning_lab.domain.validation import ValidationError
from learning_lab.linux_text.engine import CAPABILITIES, TextEngine, parse, validate_state

ROOT=Path(__file__).resolve().parents[1];H='/home/learner'

def node(kind='directory',content='',mode='0755',owner='root',group='root'):
    return dict(kind=kind,content=content,mode=mode,owner=owner,group=group)

def fixture(data='alpha\nbeta\nalpha\n'):
    p=json.loads((ROOT/'examples/linux-file-navigation.lab.json').read_text());p['identity']={'id':'text-fixture','content_version':'1.0.0'}
    p['engine']={'id':'linux-navigation','contract_version':5,'supported_behavior_versions':['linux-text-streams-1'],'required_capabilities':sorted(CAPABILITIES)}
    p['domain']={'schema_version':3,'cwd':H,'output_files':[H+'/report',H+'/new',H+'/denied'],
        'filesystem':{'/':node(),'/home':node(),H:node(owner='learner',group='learner'),H+'/input':node('file',data,'0644','learner','learner'),
                      H+'/report':node('file','Old report\n','0644','learner','learner'),H+'/denied':node('file','Private\n','0400'),
                      H+'/locked':node(mode='0700'),H+'/locked/file':node('file','Secret','0644')},
        'lesson':{'goal':'Inspect the text.','steps':[dict(objective='inspect',command='head -n 1 input',explanation='Inspect first record.',expected='alpha')]}}
    p['objectives']=[dict(id='inspect',label='Inspect first record',points=100,predicate='stream_observed',params={'tool':'head','source':H+'/input','output':(data.split('\n')[0]+ ('\n' if '\n' in data else '') if data else '')})]
    return p

def lab(value=None):return load_portable(json.dumps(value or fixture(),ensure_ascii=False).encode())
def engine(value=None):return lab(value).domain().engine(lab(value).domain().session().attempt['applied'])

class TextContractTests(unittest.TestCase):
    def test_filters_empty_newlines_bytes_and_words(self):
        cases=[('', 'wc -l input',b'0 input\n'),('é\t猫\nlast','wc -c input',b'11 input\n'),
               ('é\t猫\nlast','wc -w input',b'3 input\n'),('a\nb','wc -l input',b'1 input\n'),
               ('a\nb','tail -n 1 input',b'b'),('a\nb','head -n 1 input',b'a\n'),
               ('a\nb','head -n 0 input',b''),('','sort input',b''),('x','sort input',b'x\n')]
        for data,cmd,out in cases:
            with self.subTest(cmd=cmd,data=data):self.assertEqual(engine(fixture(data)).run(cmd)[1].stdout,out)
    def test_grep_no_matches_numbering_and_literal_text(self):
        e=engine(fixture('a.b\naXb\na.b'));self.assertEqual(e.run('grep -F -n "a.b" input')[1].stdout,b'1:a.b\n3:a.b\n')
        r=e.run('grep -F nope input')[1];self.assertEqual((r.stdout,r.errors,r.status),(b'',(),1))
    def test_sort_uniq_adjacent_and_separated(self):
        e=engine(fixture('é\nb\nb\na\nb'))
        self.assertEqual(e.run('uniq -c input')[1].stdout,'      1 é\n      2 b\n      1 a\n      1 b\n'.encode())
        self.assertEqual(e.run('sort input | uniq -c')[1].stdout,'      1 a\n      3 b\n      1 é\n'.encode())
    def test_cut_quotes_missing_fields_and_plain_records(self):
        e=engine(fixture('a|b|c\nx|y\nplain\na||z'))
        self.assertEqual(e.run('cut -d "|" -f 3 input')[1].stdout,b'c\n\nplain\nz\n')
        self.assertEqual(e.run("cut -d '|' -f 2 input")[1].stdout,b'b\ny\nplain\n\n')
    def test_pipeline_input_override_status_and_upstream_errors(self):
        e=engine();self.assertEqual(e.run('grep -F beta input | wc -l')[1].stdout,b'1\n')
        r=e.run('grep -F nope input | wc -l')[1];self.assertEqual((r.stdout,r.status,r.errors),(b'0\n',0,()))
        r=e.run('head missing | wc -l')[1];self.assertEqual((r.stdout,r.status),(b'0\n',0));self.assertTrue(r.errors)
        r=e.run('cat input | sort missing | wc -l')[1];self.assertEqual((r.stdout,r.status),(b'0\n',0));self.assertTrue(r.errors)
        self.assertEqual(e.run('head input | wc -l input')[1].stdout,b'3 input\n')
    def test_redirection_truncation_append_alias_and_error_side_effects(self):
        e=engine();s,r=e.run('cat missing > report');self.assertEqual(s['filesystem'][H+'/report']['content'],'');self.assertEqual(r.status,1)
        s,r=e.run('cat missing > new');self.assertEqual(s['filesystem'][H+'/new']['content'],'');self.assertEqual(r.status,1)
        s,r=e.run('head missing | wc -l > report');self.assertEqual(s['filesystem'][H+'/report']['content'],'0\n');self.assertEqual(r.status,0);self.assertTrue(r.errors)
        s,r=e.run('cat report > report');self.assertEqual(s['filesystem'][H+'/report']['content'],'');self.assertEqual(r.status,0)
        s,r=e.run('cat report >> report');self.assertEqual(s['filesystem'][H+'/report']['content'],'Old report\n');self.assertEqual(r.status,1)
        s,r=e.run('cat missing >> report');self.assertEqual(s['filesystem'][H+'/report']['content'],'Old report\n')
        for cmd in ('head input | cat report > report','head input > denied','head input > /etc/other','cat input > report | wc -l','head --bad input > report'):
            state,r=e.run(cmd);self.assertEqual(state,e.state,cmd);self.assertTrue(r.errors)
    def test_permissions_search_file_write_and_creation(self):
        p=fixture();p['domain']['filesystem'][H]['mode']='0555';e=engine(p)
        s,r=e.run('head input > report');self.assertEqual(r.status,0);self.assertEqual(s['filesystem'][H+'/report']['content'],'alpha\nbeta\nalpha\n')
        self.assertTrue(e.run('head input > new')[1].errors)
        self.assertTrue(e.run('cat locked/file > report')[1].errors)
        self.assertTrue(e.run('head locked/../input')[1].errors)
        for mode,group in (('0020','learner'),('0002','root')):
            p=fixture();p['domain']['filesystem'][H+'/report'].update(owner='root',group=group,mode=mode)
            self.assertEqual(engine(p).run('head input > report')[1].status,0)
        p=fixture();p['domain']['filesystem'][H+'/report'].update(mode='0022')
        self.assertTrue(engine(p).run('head input > report')[1].errors)
    def test_evidence_outcomes_and_invalidation(self):
        e=engine();s,r=e.run('head -n 1 ./input');self.assertEqual(s['observed'],['inspect'])
        e=TextEngine(e.pack,s);s,r=e.run('head input > report');self.assertEqual(s['observed'],[])
        self.assertEqual(TextEngine(e.pack,s).grade()['score'],0)
        s,r=e.run('head -n 1 input > report');self.assertEqual(s['observed'],[])
        s,r=e.run('head -n 2 input');self.assertEqual(s['observed'],['inspect']) # earlier retained exact successful observation
        fresh=engine();self.assertEqual(fresh.run('head -n 2 input')[0]['observed'],[])
    def test_hostile_syntax_and_options_before_open(self):
        e=engine()
        for cmd in ('grep -F ~ input > report','head input; id','cat $HOME','cat `pwd`','cat $(pwd)','head input && wc -l input','cat input\ncat report','cat input < report','cat input 2>report','cat input | sh','head -c 1 input','tail -f input','grep beta input','grep -E x input','sort -n input','uniq -d input','cut -c 1 input','wc -lc input','head input |','| head input',"grep -F 'abc input",'grep -F a"b" input','cat *.txt','cat input > report > new','cat input | sort | uniq | wc -l | cat input','cat input\\','grep -F \ud800 input','x'*513):
            with self.subTest(cmd=cmd):s,r=e.run(cmd);self.assertEqual(s,e.state);self.assertTrue(r.errors)
    def test_file_limit_is_partial_and_display_not_stream_truncation(self):
        p=fixture('x'*8192);e=engine(p);s,r=e.run('cat input >> report');self.assertEqual(len(s['filesystem'][H+'/report']['content'].encode()),8192);self.assertEqual(r.status,1)
        p=fixture(('x\n'+'y\n')*2048);e=engine(p)
        s,r=e.run('uniq -c input');self.assertEqual(len(r.stdout),32768);self.assertEqual(r.status,1)
        s,r=e.run('uniq -c input > report');self.assertEqual(len(s['filesystem'][H+'/report']['content']),8192);self.assertEqual(r.status,1)
        state,out=e.command('uniq -c input');self.assertIn('display truncated',out)
    def test_total_limit_prefix_and_utf8_boundary(self):
        p=fixture('é'*4096)
        for i in range(7):p['domain']['filesystem'][H+'/f'+str(i)]=node('file','x'*8192,'0644','learner','learner')
        p['domain']['filesystem'][H+'/report']['content']=''
        p['domain']['filesystem'][H+'/denied']['content']=''
        p['domain']['filesystem'][H+'/locked/file']['content']=''
        e=engine(p);s,r=e.run('cat input > report');self.assertEqual(s['filesystem'][H+'/report']['content'],'');self.assertEqual(r.status,1)
        p=fixture('é'*4096);p['domain']['filesystem'][H+'/report']['content']='x'
        s,r=engine(p).run('cat input >> report');self.assertEqual(len(s['filesystem'][H+'/report']['content'].encode()),8191);self.assertEqual(r.status,1)

    def test_quoted_literals_alias_rejection_and_empty_cat_alias(self):
        e=engine(fixture('a*b\nother\n'))
        self.assertEqual(e.run('grep -F "a*b" input')[1].stdout,b'a*b\n')
        s,r=e.run('head report >> report');self.assertEqual(s,e.state);self.assertTrue(r.errors)
        p=fixture();p['domain']['filesystem'][H+'/report']['content']='';e=engine(p)
        s,r=e.run('cat report >> report');self.assertEqual(r.status,0);self.assertEqual(s,e.state)

    def test_validation_feasibility_and_state_protection(self):
        for mutate in (lambda p:p['engine'].update(contract_version=6),lambda p:p['engine']['required_capabilities'].append('shell'),
          lambda p:p['domain'].update(script='bad'),lambda p:p['domain']['lesson']['steps'][0].update(command='cat missing > report'),
          lambda p:p['objectives'][0]['params'].update(tool='eval'),lambda p:p['domain'].update(output_files=[H])):
            p=fixture();mutate(p)
            with self.assertRaises(ValidationError):lab(p)
        e=engine();s=deepcopy(e.state);s['filesystem'][H+'/input']['content']='tampered'
        with self.assertRaises(ValidationError):validate_state(e.pack,s)
    def test_wc_evidence_requires_option_accepts_path_spellings_and_stdin(self):
        p=fixture();p['objectives'][0]['params']={'tool':'wc -l','source':H+'/input','output':'3\n'}
        p['domain']['lesson']['steps'][0]['command']='wc -l input'
        for cmd in ('wc -l ./input','wc -l /home/learner/input','cat input | wc -l'):
            self.assertEqual(engine(p).run(cmd)[0]['observed'],['inspect'])
        self.assertEqual(engine(p).run('wc -w input')[0]['observed'],[])
        self.assertEqual(engine(p).run('wc -l input | wc -c')[0]['observed'],[])

    def test_no_host_apis_and_legacy_contracts(self):
        e=engine();
        with ExitStack() as stack:
            for api in ('builtins.open','io.open','os.open','os.system','subprocess.Popen','subprocess.run','socket.socket','pathlib.Path.read_bytes','pathlib.Path.write_text'):
                stack.enter_context(patch(api,side_effect=AssertionError('Learner host API')))
            for cmd in ('head input','tail input','grep -F alpha input','wc -c input','sort input | uniq -c','cut -d a -f 1 input','cat input > report','cat report >> report'):
                e.run(cmd)
        for name in ('linux-file-navigation','linux-file-permissions','linux-directory-permissions','linux-deliver-workspace'):
            p=ROOT/'collections/packs'/name
            p=ROOT/'learning_lab/collections/packs'/(name+'.lab.json');s=load_portable(p.read_bytes()).domain().session();before=deepcopy(s.attempt['applied'])
            for cmd in ('head input','sort input | uniq','cat input > report'):s.execute(cmd);self.assertEqual(s.attempt['applied'],before)
