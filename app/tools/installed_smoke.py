"""Run with an installed venv's python -I; writes only a disposable profile.

This standalone harness can be copied away from the source tree. It deliberately
does not add the checkout to sys.path or use the examples directory.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from importlib.metadata import distribution, version


def phase(root, resume, require_icon):
    import learning_lab
    from PySide6.QtTest import QTest
    from learning_lab.__main__ import build_application
    from learning_lab.collections import linux_fundamentals
    package = Path(learning_lab.__file__).resolve().parent
    if sys.prefix == sys.base_prefix or not package.is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError('Smoke test requires an installed package inside this venv.')
    dist = distribution('omarchy-learning-lab')
    if not dist.read_text('WHEEL') or '"editable": true' in (dist.read_text('direct_url.json') or ''):
        raise RuntimeError('Expected a wheel installation, not an editable source tree.')
    assert (package/'qml/Main.qml').is_file()
    assert (package/'qml/AuthoringDialog.qml').is_file()
    from learning_lab.authoring import resource
    from learning_lab.portable import load_portable
    load_portable(resource('permissions.lab.json').encode())
    assert 'disposable profile' in resource('guide.txt')
    assert 'untrusted' in resource('guide.txt')
    assert 'contract 3' in resource('prompt.txt')
    if require_icon:assert (package/'icons/omarchy-learning-lab.svg').is_file()
    entries = linux_fundamentals(); assert len(entries) == 6
    app, engine, bridge, lock = build_application(root/'data', root/'config')
    window = engine.rootObjects()[0]
    try:
        assert QTest.qWaitForWindowExposed(window, 5000)
        assert not window.grabWindow().isNull()
        if resume:
            expected = json.loads((root/'expected.json').read_text())
            assert {k: lab.session.attempt for k, lab in bridge.labs.items()} == expected['attempts']
            assert bridge.view['labKey'] == expected['selected']
            assert bridge.view['commandDraft'] == 'help'
        else:
            assert len(bridge.labs) == 3
            for entry in entries:
                assert bridge.selectLab(entry['scenario'].key, True)
                bridge.execute('pwd')
                assert bridge.session.attempt['console']
                bridge.setCommandDraft('help'); bridge.flush()
            assert len(bridge.labs) == 9
            source=root/'authored.lab.json';author=bridge.authoring
            assert author.prepareStarter(str(source)) and author.confirmStarter(True)
            value=json.loads(source.read_text());value['metadata']['title']='Installed authoring proof'
            value['domain']['filesystem']['/home/learner/notes.txt']['content']='Original disposable authored note.\n'
            source.write_text(json.dumps(value))
            before={str(p):p.read_bytes() for folder in (root/'data',root/'config') for p in folder.rglob('*') if p.is_file()}
            assert author.validateLab(str(source)) and len(bridge.labs)==9
            assert before=={str(p):p.read_bytes() for folder in (root/'data',root/'config') for p in folder.rglob('*') if p.is_file()}
            assert author.importValidated()
            scenario=load_portable(source.read_bytes());assert bridge.selectLab(scenario.key)
            for _ in range(4):bridge.execute(bridge.view['guide']['command'])
            bridge.submit();assert bridge.view['grade']['score']==100
            bridge.restart('Challenge');assert bridge.view['guide']=={}
            bridge.execute('chmod 600 notes.txt');bridge.execute('cat notes.txt');bridge.submit()
            assert bridge.view['grade']['score']==100
            bridge.setCommandDraft('help');bridge.flush()
            (root/'expected.json').write_text(json.dumps({
                'selected': bridge.view['labKey'],
                'attempts': {k: lab.session.attempt for k, lab in bridge.labs.items()}}))
        return {'phase': 'resume' if resume else 'start', 'result': 'PASS',
                'package': str(package), 'platform': app.platformName(),
                'collection_packs': len(entries), 'authoring_resources':True, 'authored_learn_challenge_resume':True, 'pyside': version('PySide6')}
    finally:
        window.close(); app.processEvents(); lock.unlock()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-icon', action='store_true')
    parser.add_argument('--profile', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--resume', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.profile:
        print(json.dumps(phase(args.profile, args.resume, args.require_icon)))
        return
    # All subprocesses use a new profile and cwd, independent of the checkout.
    with tempfile.TemporaryDirectory(prefix='learning-lab-installed-smoke-') as temp:
        root = Path(temp); results = []
        env = {**os.environ, 'QT_QPA_PLATFORM': 'offscreen', 'QT_QPA_PLATFORMTHEME': '',
               'QT_QUICK_BACKEND': 'software', 'PYTHONDONTWRITEBYTECODE': '1'}
        env.pop('PYTHONPATH', None); env.pop('PYTHONHOME', None)
        for resume in (False, True):
            cmd = [sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--profile', str(root)]
            if resume: cmd.append('--resume')
            if args.require_icon: cmd.append('--require-icon')
            result = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True, timeout=45)
            if result.returncode:raise RuntimeError(result.stdout + result.stderr)
            results.append(json.loads(result.stdout))
        print(json.dumps({'result': 'PASS', 'phases': results,
                          'scope': 'Offscreen resource/start/resume smoke; not complete lab or native-dialog acceptance.'}, indent=2))


if __name__ == '__main__':main()
