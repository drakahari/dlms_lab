#!/usr/bin/python3 -I
"""Guest-only fixed fixture transaction helper; never called by Learning Lab.

No arbitrary package names/paths/options. Guest root can modify or bypass this
teaching guard. This helper is not a host security boundary or generic DNF wrapper.
"""
import fcntl, hashlib, json, os, resource, signal, stat, sys, tempfile
from pathlib import Path

FIXTURE_ROOT = '/opt/learning-lab/rpm-fixtures'
STATE_ROOT = '/var/lib/learning-lab-rpm'
# Filled by the reviewed fixture build, before the learner image is prepared.
MANIFEST_SHA256 = 'FIXTURE_MANIFEST_SHA256'
NAMES = {'ll-rpm-data', 'll-rpm-report'}
PAYLOADS = {
    'll-rpm-data': ('/usr/share/learning-lab-rpm/data.txt','/etc/learning-lab-rpm/report.conf',
                    '/usr/share/licenses/ll-rpm-data/LICENSE'),
    'll-rpm-report': ('/usr/bin/ll-rpm-report','/usr/share/licenses/ll-rpm-report/LICENSE'),
}
MAX_ARCHIVE_BYTES = 131072
MAX_TRANSACTIONS = 32
MAX_RETAINED_BYTES = 256 * 1024**2
MAX_FILE_BYTES = 32 * 1024**2
WORK = None

class Refused(Exception): pass

def require(ok, message):
    if not ok: raise Refused(message)

def validate_plan(rows, expected):
    """Exact multiset including outgoing upgrade/reinstall halves; no hidden rows."""
    require(0 < len(rows) <= 4, 'Empty or excessive transaction')
    require(len(rows) == len(set(rows)), 'Duplicate transaction row')
    require(all(row[0] in NAMES and row[1] == 'noarch' and row[2] == '0' for row in rows),
            'Unexpected package identity, architecture or epoch')
    require(set(rows) == set(expected), 'Resolved transaction differs from the declared fixture operation')

def owned_directory(path):
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in Path(path).parts[1:]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = child
            metadata = os.fstat(fd)
            require(metadata.st_uid == 0 and metadata.st_mode & 0o022 == 0,
                    'Untrusted fixture/state directory')
        return fd
    except BaseException:
        os.close(fd); raise

def read_regular(parent, name, limit):
    require('/' not in name and name not in ('.', '..'), 'Invalid fixed member')
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_uid == 0 and before.st_nlink == 1
                and before.st_mode & 0o022 == 0 and before.st_size <= limit,
                'Unexpected member type, ownership, permissions, links or size')
        data = bytearray()
        while chunk := os.read(fd, min(65536, limit + 1 - len(data))):
            data.extend(chunk); require(len(data) <= limit, 'Member exceeds bound')
        after = os.fstat(fd)
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns) ==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
                and len(data) == before.st_size, 'Member changed during admission')
        return bytes(data)
    finally: os.close(fd)

def directory_names(parent):
    """Fresh open-file description, tied to the verified directory descriptor."""
    def state(fd):
        info = os.fstat(fd)
        require(stat.S_ISDIR(info.st_mode), 'Expected retained directory')
        return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
                info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    before = state(parent)
    child = os.open('.', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
    try:
        require(state(child) == before, 'Retained directory changed before enumeration')
        names = os.listdir(child)
        require(state(child) == before and state(parent) == before,
                'Retained directory changed during enumeration')
        require(len(names) == len(set(names)), 'Duplicate retained members')
        return names
    finally: os.close(child)

def installed_state():
    import rpm
    rows = []; fixtures = {}
    for header in rpm.TransactionSet().dbMatch():
        row = (header['name'],header['arch'],str(header['epoch'] or 0),header['version'],header['release'])
        if row[0] in NAMES:
            require(row[0] not in fixtures and row[1] == 'noarch' and row[2] == '0',
                    'Ambiguous or unexpected installed fixture')
            require((row[0] == 'll-rpm-data' and row[3:] in [('1.0','1'),('2.0','1')]) or
                    (row[0] == 'll-rpm-report' and row[3:] == ('1.0','1')),
                    'Unsupported installed fixture version')
            fixtures[row[0]] = row
        else: rows.append(row)
    return sorted(rows), fixtures

def policy_snapshot():
    hashes = {}
    for path in ('/etc/passwd','/etc/shadow','/etc/sudoers'):
        parent = owned_directory(str(Path(path).parent))
        try: data = read_regular(parent,Path(path).name,65536)
        finally: os.close(parent)
        if path.endswith(('passwd','shadow')):
            data = b'\n'.join(row for row in data.splitlines() if row.split(b':',1)[0] in (b'root',b'learner'))
            require(len(data.splitlines()) == 2, 'Missing or duplicate learner/root account record')
        metadata = os.stat(path,follow_symlinks=False)
        hashes[path] = (hashlib.sha256(data).hexdigest(),stat.S_IMODE(metadata.st_mode),metadata.st_uid,metadata.st_gid,metadata.st_nlink)
    directory = owned_directory('/etc/sudoers.d')
    try:
        names = sorted(directory_names(directory))
        require(len(names) <= 32, 'Excessive sudo drop-ins')
        for name in names:
            payload = read_regular(directory,name,8192)
            metadata = os.stat(name,dir_fd=directory,follow_symlinks=False)
            hashes['sudoers.d/'+name] = (hashlib.sha256(payload).hexdigest(),stat.S_IMODE(metadata.st_mode),metadata.st_uid,metadata.st_gid,metadata.st_nlink)
    finally: os.close(directory)
    import pwd, grp
    user = pwd.getpwnam('learner')
    groups = sorted(g.gr_gid for g in grp.getgrall() if 'learner' in g.gr_mem)
    return (hashes,user.pw_uid,user.pw_gid,user.pw_dir,user.pw_shell,groups)

def retained_size(fd, depth=0):
    require(depth <= 8, 'Retained state is too deeply nested')
    total = 0
    names = directory_names(fd)
    require(len(names) <= 4096, 'Excessive retained state members')
    for name in names:
        metadata = os.stat(name,dir_fd=fd,follow_symlinks=False)
        require(metadata.st_uid == 0 and metadata.st_mode & 0o022 == 0,
                'Untrusted retained state member')
        if stat.S_ISDIR(metadata.st_mode):
            child = os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            try: total += retained_size(child,depth+1)
            finally: os.close(child)
        else:
            require(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1
                    and metadata.st_size <= MAX_FILE_BYTES, 'Unexpected retained file')
            total += metadata.st_size
        require(total <= MAX_RETAINED_BYTES, 'Retained evidence limit reached; no automatic pruning')
    return total

def evidence(name, record):
    require(WORK is not None and name in ('plan.json','result.json','failure.json'), 'Invalid evidence destination')
    payload = (json.dumps(record,sort_keys=True,indent=2)+'\n').encode()
    require(len(payload) <= 16384, 'Evidence exceeds bound')
    with (WORK/name).open('xb') as output:
        output.write(payload); output.flush(); os.fsync(output.fileno())

def expected_final(fixtures, expected, actions):
    incoming = set(actions[:2]) | {actions[3]}
    outgoing = {actions[2],actions[4],actions[5]}
    final = dict(fixtures)
    for row in expected:
        if row[5] in outgoing: final.pop(row[0],None)
    for row in expected:
        if row[5] in incoming: final[row[0]] = row[:5]
    return final

def validate_payload_targets(expected, fixtures):
    """Refuse unowned/unrelated collisions and symlink parents before RPM writes.

    Guest root can race or bypass this helper. No claim of protection against
    root; the fixed images and exercises use only the declared teaching paths.
    """
    import rpm
    wanted = {path for name in NAMES for path in PAYLOADS[name]}
    providers = {path: [] for path in wanted}
    for header in rpm.TransactionSet().dbMatch():
        for path in header['filenames']:
            if path in providers: providers[path].append(header['name'])
    for name in {row[0] for row in expected}:
        for path in PAYLOADS[name]:
            parent = Path(path).parent
            try: directory = owned_directory(str(parent))
            except FileNotFoundError:
                require(parent.as_posix() in ('/usr/share/learning-lab-rpm','/etc/learning-lab-rpm',
                                            '/usr/share/licenses/ll-rpm-data','/usr/share/licenses/ll-rpm-report'),
                        'Unexpected missing payload ancestor')
                directory = owned_directory(str(parent.parent)); os.close(directory)
                require(not providers[path], 'Installed payload parent missing; inspect manually')
                continue
            try:
                expected_provider = [name] if name in fixtures else []
                require(providers[path] == expected_provider, 'Unrelated or ambiguous payload ownership')
                try: metadata = os.stat(Path(path).name,dir_fd=directory,follow_symlinks=False)
                except FileNotFoundError: metadata = None
                if metadata is not None:
                    require(name in fixtures and stat.S_ISREG(metadata.st_mode)
                            and metadata.st_uid == 0 and metadata.st_nlink == 1
                            and metadata.st_mode & 0o022 == 0, 'Payload collision or unexpected type/permissions')
                if path.endswith('report.conf'):
                    for suffix in ('.rpmnew','.rpmsave'):
                        try: os.stat(Path(path).name+suffix,dir_fd=directory,follow_symlinks=False)
                        except FileNotFoundError: continue
                        raise Refused('Retained configuration candidate already exists; inspect and preserve it first')
            finally: os.close(directory)

def expected_operation(operation, fixtures, actions):
    I,U,UD,R,RD,E = actions
    data = fixtures.get('ll-rpm-data'); report = fixtures.get('ll-rpm-report')
    def row(name, version, action): return (name,'noarch','0',version,'1',action)
    if operation == 'data1':
        require(not fixtures, 'data1 requires both fixtures absent')
        return ['ll-rpm-data-1.0-1.noarch.rpm'], [row('ll-rpm-data','1.0',I)], 'install'
    if operation == 'pair':
        require(not fixtures, 'pair requires both fixtures absent')
        return ['ll-rpm-data-2.0-1.noarch.rpm','ll-rpm-report-1.0-1.noarch.rpm'], [row('ll-rpm-data','2.0',I),row('ll-rpm-report','1.0',I)], 'install'
    if operation == 'upgrade':
        require(data is not None and data[3:] == ('1.0','1') and report is None,
                'upgrade requires data1 only')
        return ['ll-rpm-data-2.0-1.noarch.rpm'], [row('ll-rpm-data','2.0',U),row('ll-rpm-data','1.0',UD)], 'upgrade'
    if operation == 'reinstall':
        require(data is not None and data[3:] == ('2.0','1'), 'reinstall requires data2')
        return ['ll-rpm-data-2.0-1.noarch.rpm'], [row('ll-rpm-data','2.0',R),row('ll-rpm-data','2.0',RD)], 'reinstall'
    if operation == 'remove-report':
        require(report is not None, 'report is not installed')
        return [], [row('ll-rpm-report','1.0',E)], 'remove'
    if operation == 'remove-data':
        require(data is not None and report is None, 'Remove report first; no implicit dependent removal')
        return [], [row('ll-rpm-data',data[3],E)], 'remove'
    raise Refused('Supported operations: data1, pair, upgrade, reinstall, remove-report, remove-data')

def main():
    global WORK
    require(os.geteuid() == 0, 'Run this guest-only helper with sudo')
    require(not sys.flags.optimize and sys.flags.isolated, 'Isolated Python required')
    require(len(sys.argv) in (2,3) and sys.argv[1] in ('status','preview','apply'),
            'Syntax: ll-rpm-fixture status | preview OPERATION | apply OPERATION')
    mode = sys.argv[1]
    require((mode == 'status' and len(sys.argv) == 2) or (mode != 'status' and len(sys.argv) == 3),
            'Unsupported arguments')
    os.environ['LC_ALL'] = 'C'; os.environ['LANG'] = 'C'; os.environ['HOME'] = '/root'
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Refused('60-second deadline; inspect retained state before retry')))
    signal.alarm(60)
    resource.setrlimit(resource.RLIMIT_FSIZE,(MAX_FILE_BYTES,MAX_FILE_BYTES))
    root = owned_directory(STATE_ROOT); source = owned_directory(FIXTURE_ROOT)
    lock = os.open('operation.lock',os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW,0o600,dir_fd=root)
    metadata=os.fstat(lock)
    require(stat.S_ISREG(metadata.st_mode) and metadata.st_uid == 0 and metadata.st_nlink == 1
            and metadata.st_mode & 0o077 == 0, 'Unexpected operation lock')
    fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
    before, fixtures = installed_state(); policy = policy_snapshot()
    if mode == 'status':
        print(json.dumps({'fixtures':fixtures,'unrelated_count':len(before),'unrelated_sha256':hashlib.sha256(json.dumps(before).encode()).hexdigest()},sort_keys=True));return
    members = directory_names(root)
    require(all(name == 'operation.lock' or name.startswith('transaction-') for name in members),
            'Unexpected state directory member')
    require(len([name for name in members if name.startswith('transaction-')]) < MAX_TRANSACTIONS,
            'Retained transaction limit reached; no automatic pruning')
    # Admission and post-operation accounting, not an aggregate quota. The
    # kernel per-file limit also applies to RPMDB writes; native tests verify
    # sufficient DB headroom before this helper is admitted to an image.
    require(retained_size(root) <= MAX_RETAINED_BYTES - MAX_FILE_BYTES,
            'Insufficient retained-evidence allowance')
    require(os.statvfs(STATE_ROOT).f_bavail * os.statvfs(STATE_ROOT).f_frsize >= 1024**3, 'At least1GiB guest free required')
    manifest_bytes = read_regular(source,'manifest.json',8192)
    require(hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA256, 'Fixture manifest changed')
    manifest = json.loads(manifest_bytes)
    require(set(manifest)=={'schema_version','archives'} and manifest['schema_version']==1
            and set(manifest['archives']) == {'ll-rpm-data-1.0-1.noarch.rpm','ll-rpm-data-2.0-1.noarch.rpm','ll-rpm-report-1.0-1.noarch.rpm'}, 'Unsupported fixture manifest')
    import dnf
    import dnf.transaction as t
    actions = (int(t.PKG_INSTALL),int(t.PKG_UPGRADE),int(t.PKG_UPGRADED),int(t.PKG_REINSTALL),int(t.PKG_REINSTALLED),int(t.PKG_REMOVE))
    filenames, expected, verb = expected_operation(sys.argv[2],fixtures,actions)
    # Retain admitted copies and any failure evidence, never overwrite a prior transaction.
    work = Path(tempfile.mkdtemp(prefix='transaction-',dir=STATE_ROOT)); os.chmod(work,0o700)
    WORK = work
    files = []
    for name in filenames:
        data = read_regular(source,name,MAX_ARCHIVE_BYTES); spec = manifest['archives'][name]
        require(set(spec)=={'bytes','sha256'} and len(data)==spec['bytes'] and hashlib.sha256(data).hexdigest()==spec['sha256'], 'Archive hash/size mismatch')
        path = work/name
        with path.open('xb') as output: output.write(data); output.flush(); os.fsync(output.fileno())
        path.chmod(0o400); files.append(str(path))
    with dnf.Base() as base:
        # No config.read/read_all_repos: ambient repositories/plugins are never loaded.
        base.conf.plugins=False; base.conf.install_weak_deps=False; base.conf.history_record=False
        base.conf.clean_requirements_on_remove=False; base.conf.obsoletes=False
        base.conf.localpkg_gpgcheck=False  # Only fixed, independently SHA-pinned unsigned project archives.
        base.conf.gpgcheck=True; base.conf.exit_on_lock=True; base.conf.debuglevel=0
        base.conf.cachedir=str(work/'cache');base.conf.persistdir=str(work/'state');base.conf.logdir=str(work/'log')
        for path in ('cache','state','log'): (work/path).mkdir(mode=0o700)
        base.conf.substitutions['releasever']='9.8';base.conf.substitutions['basearch']='x86_64'
        base.fill_sack(load_system_repo=True,load_available_repos=False)
        require(not list(base.repos.iter_enabled()), 'Unexpected enabled repository')
        packages=base.add_remote_rpms(files,strict=True) if files else []
        for package in packages:
            require(package.name in NAMES and package.arch=='noarch' and str(package.epoch)=='0', 'Unexpected local package')
            getattr(base,'package_'+verb)(package)
        if verb == 'remove':
            name=expected[0][0];matches=list(base.sack.query().installed().filter(name=name))
            require(len(matches)==1,'Ambiguous installed fixture');base.package_remove(matches[0])
        base.resolve(allow_erasing=False)
        def rows():
            return [(i.pkg.name,i.pkg.arch,str(i.pkg.epoch),i.pkg.version,i.pkg.release,int(i.action)) for i in base.transaction]
        planned=rows();validate_plan(planned,expected)
        validate_payload_targets(expected,fixtures)
        plan={'operation':sys.argv[2],'transaction':planned,'same_resolved_object':id(base.transaction),'repositories':[],'weak_dependencies':False,'automatic_removal':False}
        evidence('plan.json',plan)
        print(json.dumps(plan,sort_keys=True),flush=True)
        if mode == 'preview': print('Preview only: nothing installed or removed.'); return
        require(input('Apply exactly this resolved fixture transaction? Type APPLY: ')=='APPLY', 'Cancelled; no transaction applied')
        require(installed_state()==(before,fixtures) and policy_snapshot()==policy, 'State changed after resolution; refuse execution')
        validate_plan(rows(),expected)
        validate_payload_targets(expected,fixtures)
        transaction=base.transaction
        base.do_transaction()
        require(base.transaction is transaction, 'Unexpected transaction-object replacement')
    after,final=installed_state();require(after==before and policy_snapshot()==policy,'Unrelated package/learner/sudo state changed; retain evidence and stop')
    require(final == expected_final(fixtures,expected,actions), 'Intended final fixture state not achieved; retain evidence and stop')
    retained_size(root)
    evidence('result.json',{'fixtures':final,'unrelated_unchanged':True,'checked_guest_policy_unchanged':True})
    print('Applied exact fixture transaction; unrelated packages and learner/sudo policy unchanged.')
    signal.alarm(0)

if __name__=='__main__':
    try: main()
    except (Exception,KeyboardInterrupt) as error:
        if WORK is not None:
            try: evidence('failure.json',{'status':'incomplete','type':type(error).__name__,'message':str(error)[:2048],
                                         'instruction':'Inspect retained package state; do not assume rollback or retry blindly.'})
            except Exception as recording_error:
                print('Failure record unavailable: '+type(recording_error).__name__,file=sys.stderr)
        print('REFUSED: '+str(error),file=sys.stderr);sys.exit(1)
