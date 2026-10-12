"""Developer-only gate on Anaconda's actual resolved transaction in the guest.

No package execution here. The caller preserves Anaconda's existing error/quit
protocol and invokes this immediately before the same Base.do_transaction.
"""
import hashlib
import json
import os
import signal
import stat


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identity(value):
    return (value.name, value.arch, str(value.epoch), value.version, value.release)


def admit_plan(items, rows, install_action):
    require(len(rows) == 190, 'Frozen learner input count differs')
    expected = {(p['name'], p['arch'], p['epoch'], p['version'], p['release']): p for p in rows}
    require(len(expected) == 190, 'Duplicate frozen learner identity')
    actual = []
    for item in items:
        require(len(actual) < 190, 'Actual installer transaction exceeds bound')
        actual.append(item)
    require(len(actual) == 190, 'Actual installer transaction count differs')
    seen = set()
    for item in actual:
        key = identity(item.pkg)
        require(item.action == install_action, 'Unexpected installer transaction action')
        require(key in expected and key not in seen, 'Unexpected or duplicate installer package')
        seen.add(key)
    require(seen == set(expected), 'Actual installer package set differs')
    return [(item.pkg, expected[identity(item.pkg)]) for item in actual]


def read_bounded(path, maximum):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_size <= maximum,
                'Unexpected preparation manifest type/size')
        value = stream.read(maximum + 1)
        require(len(value) <= maximum, 'Preparation manifest grew')
        return value


def payload_path(path, row):
    name = row['file']
    require(isinstance(name, str) and name.endswith('.rpm') and
            name not in ('.', '..') and '/' not in name and '\\' not in name
            and '\0' not in name, 'Invalid frozen ISO member name')
    # Observed on the pinned installer: DNF resolves the read-only CD source
    # directly, not its /run/install/repo alias. Keep one exact permitted root.
    require(path == '/run/install/sources/mount-0000-cdrom/Minimal/Packages/' + name,
            'Installer payload is not the declared ISO member: ' +
            repr(path)[:384] + '; declared ' + repr(name)[:192])
    return path


def verify_payload(stream, row):
    before = os.fstat(stream.fileno())
    require(type(row['bytes']) is int and 0 < row['bytes'] <= 256 * 1024**2
            and stat.S_ISREG(before.st_mode) and before.st_size == row['bytes'],
            'Installer payload type/size mismatch')
    digest = hashlib.sha256(); count = 0
    while chunk := stream.read(65536):
        count += len(chunk)
        require(count <= row['bytes'], 'Installer payload grew')
        digest.update(chunk)
    after = os.fstat(stream.fileno())
    require(count == row['bytes'] and digest.hexdigest() == row['sha256'],
            'Actual installer payload hash mismatch')
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
            'Actual installer payload changed during admission')


def guard(base):
    import dnf.transaction as transaction
    require(os.geteuid() == 0, 'Installer admission requires guest root')
    frozen = json.loads(read_bounded('/ll-inputs/learner-manifest.json', 262144))
    require(frozen['format_version'] == 1, 'Unsupported installer manifest')
    original = base.transaction
    pairs = admit_plan(original, frozen['packages'], transaction.PKG_INSTALL)
    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_alarm = signal.alarm(0)
    if previous_alarm:
        signal.alarm(previous_alarm)
        raise ValueError('Unexpected pre-existing admission alarm')
    def expired(*_):
        raise TimeoutError('Actual installer admission exceeded120s')
    signal.signal(signal.SIGALRM, expired)
    signal.alarm(120)
    evidence = []
    try:
        for package, row in pairs:
            # The exact immutable media package, not a second solver or a name.
            path = payload_path(package.localPkg(), row)
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, 'rb') as stream:
                verify_payload(stream, row)
            evidence.append({'identity': list(identity(package)), 'sha256': row['sha256']})
        require(base.transaction is original, 'Actual installer transaction replaced')
        with open('/dev/ttyS0', 'w') as serial:
            serial.write('LL_ACTUAL_INSTALLER_ADMISSION=' + json.dumps(evidence, separators=(',', ':')) + '\n')
            serial.write('LL_ACTUAL_INSTALLER_ADMISSION_PASS\n'); serial.flush()
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, previous_handler)
