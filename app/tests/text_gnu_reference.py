"""Static developer fixtures ONLY. Never accepts a pack or learner command.
GNU execution is intentionally isolated from learning_lab's runtime.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from test_text_streams import fixture, engine, H

# Static shell snippets, not supplied by packs or users. Inputs are inert bytes.
CASES=[
 ('', 'head input'),('', 'tail input'),('', 'wc -l input'),('', 'sort input'),('', 'uniq -c input'),
 ('a\nb', 'head -n 1 input'),('a\nb', 'tail -n 1 input'),('a\nb','wc -l input'),
 ('é\t猫\nlast','wc -c input'),('é\t猫\nlast','wc -w input'),('a\u00a0b','wc -w input'),
 ('é\nb\nb\na\nb','sort input'),('é\nb\nb\na\nb','uniq -c input'),('é\nb\nb\na\nb','sort input | uniq -c'),
 ('a|b|c\nx|y\nplain\na||z','cut -d "|" -f 3 input'),('a|b|c\nx|y\nplain\na||z',"cut -d '|' -f 2 input"),
 ('a.b\naXb\na.b','grep -F -n "a.b" input'),('a.b\naXb\na.b','grep -F nope input'),
 ('a\nb\na\n','grep -F a input | wc -l'),('a\n','grep -F nope input | wc -l'),
 ('a\n','head missing | wc -l'),('a\n','cat input | sort missing | wc -l'),
 ('a\n','cat missing > report'),('a\n','cat missing > new'),('a\n','cat missing >> report'),
 ('a\n','head missing | wc -l > report'),('a\n','cat report > report'),('a\n','cat report >> report'),
 ('a\n','head input > denied'),('a\n','head input > report'),('a\n','head input >> report'),
 ('a\nb','cut -d : -f 2 input'),('a\nb','grep -F b input'),('a\nb','uniq input'),
 ('\n\n','head -n 0 input'),('x\n','head input | wc -l input'),('x\n','tail -n 0 input'),
 ('a b\n','grep -F "a b" input'),('a*b\nother\n','grep -F "a*b" input'),('a b c\nplain','cut -d " " -f 2 input'),('a\n','cat input | head missing > report'),('a\n','cat input | grep -F nope > report'),('a\n','grep -F a missing | wc -l > report'),('a\n','cat missing | sort > new')]

def error_categories(messages):
    categories=[]
    for message in messages:
        lowered=message.lower()
        if not lowered.strip():continue
        if 'no such' in lowered:category='missing-path'
        elif 'permission denied' in lowered:category='permission-denied'
        elif 'input file is output file' in lowered:category='input-output-alias'
        else:raise AssertionError('Unclassified reference diagnostic: '+message)
        categories.append(category)
    return sorted(set(categories))


def main():
    results=[]
    with tempfile.TemporaryDirectory(prefix='text-gnu-static-') as folder:
        root=Path(folder)
        for data,command in CASES:
            for p in root.iterdir():p.chmod(0o600);p.unlink()
            (root/'input').write_bytes(data.encode());(root/'report').write_text('Old report\n');(root/'denied').write_text('Private\n');(root/'denied').chmod(0o400)
            ref=subprocess.run(['bash','--noprofile','--norc','-c',command],cwd=root,
                env={**os.environ,'LC_ALL':'C','LANG':'C','POSIXLY_CORRECT':'1'},capture_output=True,timeout=5)
            e=engine(fixture(data));state,r=e.run(command)
            assert r.stdout==ref.stdout,(command,r.stdout,ref.stdout)
            assert r.status==ref.returncode,(command,r.status,ref.returncode)
            assert bool(r.errors)==bool(ref.stderr),(command,r.errors,ref.stderr)
            expected_errors=error_categories(ref.stderr.decode('utf-8',errors='replace').splitlines())
            actual_errors=error_categories(r.errors)
            assert expected_errors==actual_errors,(command,expected_errors,actual_errors)
            expected_files={};actual_files={}
            for name in ('input','report','new','denied'):
                virtual=state['filesystem'].get(H+'/'+name)
                assert (root/name).exists()==(virtual is not None),(command,name)
                expected_files[H+'/'+name]=(root/name).read_bytes().hex() if (root/name).exists() else None
                actual_files[H+'/'+name]=virtual['content'].encode().hex() if virtual is not None else None
                assert expected_files[H+'/'+name]==actual_files[H+'/'+name],(command,name)
            results.append({'command':command,'utf8_bytes':len(data.encode()),'passed':True,
                'expected_stdout_hex':ref.stdout.hex(),'actual_stdout_hex':r.stdout.hex(),
                'expected_status':ref.returncode,'actual_status':r.status,
                'expected_stderr_present':bool(ref.stderr),'actual_stderr_present':bool(r.errors),
                'gnu_stderr':ref.stderr.decode('utf-8',errors='replace'),'simulated_errors':list(r.errors),
                'expected_error_categories':expected_errors,'actual_error_categories':actual_errors,
                'expected_file_bytes_hex':expected_files,'actual_virtual_file_bytes_hex':actual_files})
    print(json.dumps({'result':'PASS','fixtures':results,'locale':'C','POSIXLY_CORRECT':'1','scope':'Static developer verification only'},indent=2))
if __name__=='__main__':main()
