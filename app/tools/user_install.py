"""Reviewed user-local wheel installer. No sudo, system Python changes or data migration."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from uuid import uuid4
from zipfile import ZipFile

APP = Path(__file__).resolve().parents[1]
MARKER = {'format': 'omarchy-learning-lab.user-install', 'version': 1}


class InstallError(RuntimeError):pass


def atomic_bytes(path, raw, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.'+path.name+'-'+uuid4().hex)
    try:
        with tmp.open('xb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        tmp.chmod(mode); os.replace(tmp, path)
    finally:
        if tmp.exists():tmp.unlink()


class Installation:
    def __init__(self, staging_root=None):
        self.stage = Path(staging_root).resolve() if staging_root else None
        home = self.stage/'home' if self.stage else Path.home()
        data = self.stage/'data' if self.stage else Path(os.environ.get('XDG_DATA_HOME') or home/'.local/share')
        self.root = home/'.local/opt/omarchy-learning-lab'
        self.desktop = data/'applications/omarchy-learning-lab.desktop'
        for path in (self.root, self.desktop):
            if not path.is_absolute() or any(c in str(path) for c in '\n\r\t\\"`$%'):
                raise InstallError('Installation paths must be absolute and contain no control characters, backslashes, quotes, $, ` or %.')
            if self.stage and not path.resolve().is_relative_to(self.stage):
                raise InstallError('Staging destination escapes its root through a symlink.')
        self.releases = self.root/'releases'
        self.launch = self.root/'launch'
        self.marker = self.root/'managed.json'

    def launcher_bytes(self):
        return ('#!/bin/sh\n# Managed Learning Lab launcher; resolve the release before starting Python.\n'
                'release=$(/usr/bin/readlink -f -- '+shlex.quote(str(self.root/'current'))+') || exit 1\n'
                'exec "$release/venv/bin/python" -I -m learning_lab "$@"\n').encode()

    def desktop_bytes(self):
        return ('[Desktop Entry]\nType=Application\nName=Learning Lab\n'
                'Comment=Offline Linux and networking troubleshooting simulations\n'
                f'Exec="{self.launch}"\nIcon={self.root}/current/icon.svg\n'
                'Terminal=false\nCategories=Education;Science;\nKeywords=Linux;Networking;Learning;\n'
                'StartupWMClass=omarchy-learning-lab\n').encode()

    def check_owned(self):
        if self.root.is_symlink():raise InstallError('Application root cannot be a symlink.')
        if self.root.exists():
            if not self.marker.is_file() or self.marker.is_symlink() or json.loads(self.marker.read_bytes()) != {**MARKER, 'desktop': str(self.desktop)}:
                raise InstallError('Existing application directory is not managed by this installer; preserve it.')
            if self.releases.is_symlink():raise InstallError('Release directory cannot be a symlink.')
        for path, raw in ((self.launch, self.launcher_bytes()), (self.desktop, self.desktop_bytes())):
            if path.is_symlink() or (path.exists() and (not path.is_file() or path.read_bytes() != raw)):
                raise InstallError('Existing launcher/desktop file is not the expected managed file: '+str(path))
        for name in ('current', 'previous'):
            path = self.root/name
            if path.exists() or path.is_symlink():self.selected(name)

    @contextmanager
    def locked(self):
        self.check_owned()
        if not self.root.exists():
            self.root.mkdir(parents=True)
            atomic_bytes(self.marker, (json.dumps({**MARKER, 'desktop': str(self.desktop)})+'\n').encode())
        lock = self.root/'.install-lock'
        try:lock.mkdir()
        except FileExistsError:raise InstallError('Another install operation is active. Lock retained; do not remove it automatically.')
        try:yield
        finally:lock.rmdir()

    def selected(self, name):
        link = self.root/name
        if not link.exists() and not link.is_symlink():return None
        if not link.is_symlink():raise InstallError(name+' is not a managed symlink.')
        target = os.readlink(link)
        if not re.fullmatch(r'releases/[A-Za-z0-9-]+', target):raise InstallError('Unsafe release link.')
        release = self.root/target
        if release.is_symlink() or not release.is_dir():raise InstallError('Missing or unsafe release.')
        return release

    def point(self, name, release):
        tmp = self.root/('.'+name+'-'+uuid4().hex)
        try:
            tmp.symlink_to(str(release.relative_to(self.root))); os.replace(tmp, self.root/name)
        finally:
            if tmp.is_symlink():tmp.unlink()

    def activate(self, release):
        self.check_owned()
        if release.parent != self.releases or release.is_symlink():raise InstallError('Unmanaged release.')
        ready = json.loads((release/'ready.json').read_bytes())
        if ready.get('result') != 'PASS' or not (release/'venv/bin/python').exists():
            raise InstallError('Release is not prepared and verified.')
        old = self.selected('current')
        atomic_bytes(self.launch, self.launcher_bytes(), 0o755)
        atomic_bytes(self.desktop, self.desktop_bytes())
        if old and old != release:self.point('previous', old)
        self.point('current', release)  # The working installation changes only here.

    def rollback(self):
        if not self.root.exists():raise InstallError('No managed installation; nothing changed.')
        with self.locked():
            previous = self.selected('previous')
            if previous is None:raise InstallError('No previous release; nothing changed.')
            self.activate(previous)

    def uninstall(self):
        self.check_owned()
        if not self.root.exists():raise InstallError('No managed installation.')
        with self.locked():
            # No real data/config path is enumerated or deleted. Refuse extra files.
            allowed = {'managed.json', 'launch', 'current', 'previous', 'releases', '.install-lock'}
            if set(p.name for p in self.root.iterdir()) - allowed:
                raise InstallError('Unknown files in installation root; preserve and inspect them first.')
            if self.desktop.exists():self.desktop.unlink()
            for name in ('current', 'previous'):
                path = self.root/name
                if path.is_symlink():path.unlink()
            if self.releases.exists():shutil.rmtree(self.releases)
            if self.launch.exists():self.launch.unlink()
        self.marker.unlink(); self.root.rmdir()


def run(command, cwd, log):
    env = dict(os.environ)
    env.pop('PYTHONPATH', None); env.pop('PYTHONHOME', None)
    env.update(HOME=str(cwd/'build-home'), XDG_CACHE_HOME=str(cwd/'cache'),
               PIP_DISABLE_PIP_VERSION_CHECK='1', PIP_NO_CACHE_DIR='1', PYTHONDONTWRITEBYTECODE='1')
    with log.open('ab') as stream:
        result = subprocess.run([str(c) for c in command], cwd=cwd, env=env,
                                stdout=stream, stderr=subprocess.STDOUT, timeout=300)
    if result.returncode:raise InstallError('Preparation failed; active installation unchanged. See '+str(log))


def pip(python, *args):
    return [python, '-I', '-m', 'pip', '--isolated', *args, '--no-cache-dir', '--disable-pip-version-check', '--no-input']


def index_args(wheelhouse):
    return ['--no-index', '--find-links', str(Path(wheelhouse).resolve())] if wheelhouse else []


def build_wheel(source, destination, workspace, log, wheelhouse=None):
    source = Path(source).resolve(); destination.mkdir(parents=True, exist_ok=True)
    copied = workspace/'source'; copied.mkdir()
    for name in ('pyproject.toml', 'README.md'):shutil.copyfile(source/name, copied/name)
    shutil.copytree(source/'learning_lab', copied/'learning_lab', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    build_env = workspace/'build-env'
    run([sys.executable, '-I', '-m', 'venv', build_env], workspace, log)
    run(pip(build_env/'bin/python', 'wheel', '--use-pep517', '--no-deps',
            '--wheel-dir', destination, *index_args(wheelhouse), copied), workspace, log)
    wheels = list(destination.glob('omarchy_learning_lab-*.whl'))
    if len(wheels) != 1:raise InstallError('Expected exactly one Learning Lab wheel.')
    return wheels[0]


def install(target, source=APP, wheel=None, wheelhouse=None):
    with target.locked():
        tag = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid4().hex[:8]
        release = target.releases/tag; release.mkdir(parents=True)
        log = release/'install.log'
        # Venv is created at its final release path: never relocate venv scripts.
        with tempfile.TemporaryDirectory(prefix='learning-lab-build-') as temp:
            workspace = Path(temp)
            if wheel:
                artifact = release/Path(wheel).name
                if artifact.suffix != '.whl':raise InstallError('Expected a local .whl file.')
                shutil.copyfile(wheel, artifact)
            else:artifact = build_wheel(source, release, workspace, log, wheelhouse)
            with ZipFile(artifact) as archive:
                # Read one known asset; never extract arbitrary archive paths.
                icon = archive.read('learning_lab/icons/omarchy-learning-lab.svg')
                if len(icon) > 65536:raise InstallError('Icon resource too large.')
            (release/'icon.svg').write_bytes(icon)
            python = release/'venv/bin/python'
            run([sys.executable, '-I', '-m', 'venv', release/'venv'], workspace, log)
            run(pip(python, 'install', '--only-binary=:all:', *index_args(wheelhouse), artifact), workspace, log)
            run([python, '-I', '-m', 'pip', 'check'], workspace, log)
            shutil.copyfile(APP/'tools/installed_smoke.py', release/'installed_smoke.py')
            run([python, '-I', '-B', release/'installed_smoke.py', '--require-icon'], workspace, log)
        atomic_bytes(release/'ready.json', json.dumps({'result': 'PASS', 'wheel': artifact.name,
                     'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
                     'verification': 'pip check and isolated offscreen start/resume smoke'}).encode())
        target.activate(release)
        return release


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('build', 'install', 'rollback', 'uninstall'))
    parser.add_argument('--staging-root', type=Path, help='Redirect installation and desktop entry to an isolated test tree.')
    parser.add_argument('--source', type=Path, default=APP)
    parser.add_argument('--wheel', type=Path, help='Install a trusted local Learning Lab wheel instead of building.')
    parser.add_argument('--wheelhouse', type=Path, help='Use only local dependency wheels; no index access.')
    parser.add_argument('--output', type=Path, help='Required build output directory; must be empty.')
    args = parser.parse_args()
    try:
        if args.action == 'build':
            if not args.output:raise InstallError('build requires --output.')
            output = args.output.resolve()
            if output.exists() and any(output.iterdir()):raise InstallError('Build output must be empty.')
            output.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='learning-lab-build-') as temp:
                wheel = build_wheel(args.source, output, Path(temp), output/'build.log', args.wheelhouse)
            print(wheel);return
        target = Installation(args.staging_root)
        if args.action == 'install':print('Activated:', install(target, args.source, args.wheel, args.wheelhouse))
        elif args.action == 'rollback':target.rollback();print('Rolled back to:', target.selected('current'))
        else:target.uninstall();print('Application files removed. Personal progress/configuration retained.')
    except (InstallError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, 'Learning Lab installer: '+str(exc)+'\n')


if __name__ == '__main__':main()
