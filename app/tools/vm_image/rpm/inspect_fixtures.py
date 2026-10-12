"""Read-only developer admission of the three original teaching RPMs.

No RPM installation, script execution, host extraction or signature exception.
These unsigned local fixtures are admitted by reviewed source/payload identity.
"""
import hashlib
import io
import os
import stat
import struct
import zlib
from pathlib import Path

EPOCH = 1767225600
NAMES = ('ll-rpm-data-1.0-1.noarch.rpm', 'll-rpm-data-2.0-1.noarch.rpm',
         'll-rpm-report-1.0-1.noarch.rpm')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def header(stream, offset):
    stream.seek(offset)
    head = stream.read(16)
    require(head[:8] == b'\x8e\xad\xe8\x01\0\0\0\0' and len(head) == 16,
            'Invalid RPM header')
    count, size = struct.unpack('>II', head[8:])
    require(0 < count <= 1024 and 0 < size <= 65536, 'RPM header bounds')
    indexes, data = stream.read(count * 16), stream.read(size)
    require(len(indexes) == count * 16 and len(data) == size, 'Truncated header')
    values = {}
    for n in range(count):
        tag, kind, start, length = struct.unpack('>IIII', indexes[n*16:(n+1)*16])
        require(tag not in values and start < size
                and length <= (65536 if kind == 7 else 1024),
                'Invalid or duplicate header entry')
        if kind in (6, 8, 9):
            require(kind != 6 or length == 1, 'Invalid scalar string')
            parts, at = [], start
            for _ in range(length):
                end = data.find(b'\0', at)
                require(end >= at, 'Unterminated header string')
                parts.append(data[at:end].decode('utf-8')); at = end + 1
            value = parts[0] if kind == 6 else parts
        elif kind in (2, 3, 4, 5):
            width = {2: 1, 3: 2, 4: 4, 5: 8}[kind]
            require(start + width * length <= size, 'Integer header bounds')
            value = [int.from_bytes(data[start+i*width:start+(i+1)*width], 'big')
                     for i in range(length)]
        elif kind == 7:
            require(start + length <= size, 'Binary header bounds')
            value = data[start:start+length]
        else:
            raise ValueError('Unsupported fixture header type')
        values[tag] = value
    return values, offset + 16 + count * 16 + size


def inspect(path, sources):
    path, sources = Path(path), Path(sources)
    require(path.name in NAMES, 'Unexpected archive identity')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        require(stat.S_ISREG(before.st_mode) and 96 < before.st_size <= 131072,
                'Archive type/size')
        payload = stream.read(131073)
        after = os.fstat(stream.fileno())
        def identity(info):
            return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
                    info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        require(identity(before) == identity(after) and len(payload) == before.st_size,
                'Archive changed')
    stream = io.BytesIO(payload)
    require(payload[:6] == b'\xed\xab\xee\xdb\x03\0', 'Invalid RPM lead')
    _, end = header(stream, 96)
    h, end = header(stream, (end + 7) // 8 * 8)
    # Exact bounded metadata vocabulary emitted by the frozen RPM4 builder.
    # Unknown tags cannot smuggle a new script/trigger family past a denylist.
    allowed = {63, 100, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007,
               1009, 1014, 1016, 1021, 1022, 1028, 1030, 1033, 1034,
               1035, 1036, 1037, 1039, 1040, 1044, 1045, 1047, 1048,
               1049, 1050, 1064, 1080, 1081, 1082, 1095, 1096, 1097,
               1112, 1113, 1116, 1117, 1118, 1122, 1124, 1125, 1126,
               1132, 1140, 1141, 1142, 1143, 1144, 1145, 5011, 5062,
               5092, 5093, 5097}
    require(set(h) <= allowed, 'Unknown fixture metadata or executable tag')
    name, version = h[1000], h[1001]
    require(path.name == f'{name}-{version}-1.noarch.rpm' and h[1002] == '1'
            and h.get(1003, [0]) == [0] and h[1022] == 'noarch', 'Wrong NEVRA')
    require(h[1006] == [EPOCH] and all(v == EPOCH for v in h[1034]),
            'Build/file timestamps are not reproducibly pinned')
    # All scriptlet/trigger families in the pinned RPM4 tag definitions.
    forbidden = (1023, 1024, 1025, 1026, 1065, 1066, 1067, 1068, 1069,
                 1085, 1086, 1087, 1088, 1091, 1092, 1151, 1152,
                 1153, 1154, 5009, 5066, 5067, 5071, 5072, 5073,
                 5074, 5075, 5076, 5077, 5078, 5079, 5080, 5081,
                 5082, 5083, 5084, 5085, 5086)
    require(not any(tag in h for tag in forbidden), 'Scripts or triggers present')
    require(not any(h.get(5010, [])) and not any(h[1036]), 'Capabilities or links')
    license_bytes = (sources / 'LICENSE').read_bytes()
    expected = {}
    if name == 'll-rpm-data':
        require(version in ('1.0', '2.0'), 'Unsupported data version')
        expected = {
            '/etc/learning-lab-rpm': (stat.S_IFDIR | 0o755, 0, b''),
            '/etc/learning-lab-rpm/report.conf': (stat.S_IFREG | 0o644, 17,
                (sources / f'data-{version}/report.conf').read_bytes()),
            '/usr/share/learning-lab-rpm': (stat.S_IFDIR | 0o755, 0, b''),
            '/usr/share/learning-lab-rpm/data.txt': (stat.S_IFREG | 0o644, 0,
                (sources / f'data-{version}/data.txt').read_bytes()),
            '/usr/share/licenses/ll-rpm-data/LICENSE': (stat.S_IFREG | 0o644, 128, license_bytes),
        }
        extra = [('config(ll-rpm-data)', 268435464, version + '-1')]
    else:
        require(name == 'll-rpm-report' and version == '1.0', 'Unsupported report')
        # The authenticated Alma brp-mangle-shebangs changes only this prefix.
        script = (sources / 'report-1.0/ll-rpm-report').read_bytes()
        require(script.startswith(b'#!/bin/sh\n'), 'Unexpected report source')
        script = b'#!/usr/bin/sh\n' + script[len(b'#!/bin/sh\n'):]
        expected = {
            '/usr/bin/ll-rpm-report': (stat.S_IFREG | 0o755, 0, script),
            '/usr/share/licenses/ll-rpm-report/LICENSE': (stat.S_IFREG | 0o644, 128, license_bytes),
        }
        extra = [('/usr/bin/sh', 16384, ''), ('ll-rpm-data', 8, '2.0-1')]
    require(len(h[1049]) == len(h[1048]) == len(h[1050]),
            'Dependency arrays differ in length')
    requirements = list(zip(h[1049], h[1048], h[1050]))
    require(requirements == extra + [
        ('rpmlib(CompressedFileNames)', 16777226, '3.0.4-1'),
        ('rpmlib(FileDigests)', 16777226, '4.6.0-1'),
        ('rpmlib(PayloadFilesHavePrefix)', 16777226, '4.0-1')], 'Unexpected dependencies')
    require(all(len(h[tag]) == len(expected) for tag in
                (1028, 1030, 1033, 1034, 1035, 1036, 1037, 1039, 1040, 1116, 1117))
            and all(0 <= index < len(h[1118]) for index in h[1116]),
            'File metadata arrays differ in length or invalid directory index')
    require(h[5011] == [8], 'Expected SHA256 file digests')
    paths = [h[1118][index] + base for index, base in zip(h[1116], h[1117])]
    require(len(paths) == len(set(paths)) == len(expected) and set(paths) == set(expected),
            'Unexpected declared paths')
    require(h[1039] == h[1040] == ['root'] * len(paths), 'Wrong declared owners')
    for n, path_name in enumerate(paths):
        mode, flags, content = expected[path_name]
        require(h[1030][n] == mode and h[1037][n] == flags, 'Wrong mode/config flags')
        require(h[1028][n] == len(content) and h[1033][n] == 0,
                'Wrong declared file size or device')
        require(h[1035][n] == (hashlib.sha256(content).hexdigest()
                if stat.S_ISREG(mode) else ''), 'Wrong declared content')
    require(h[1124] == 'cpio' and h[1125] == 'gzip', 'Unsupported payload encoding')
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    raw = decoder.decompress(payload[end:], 262145)
    require(len(raw) <= 262144 and decoder.eof and not decoder.unused_data
            and not decoder.unconsumed_tail, 'Payload decompression bound/format')
    seen, at = set(), 0
    while True:
        require(raw[at:at+6] == b'070701' and len(raw) >= at + 110, 'Invalid newc member')
        fields = [int(raw[at+6+i*8:at+14+i*8], 16) for i in range(13)]
        _, mode, uid, gid, links, mtime, size, _, _, rdevmajor, rdevminor, namelen, check = fields
        require(0 < namelen <= 256 and at+110+namelen <= len(raw), 'Member name bounds')
        name_bytes = raw[at+110:at+110+namelen]
        require(name_bytes[-1:] == b'\0', 'Member name terminator')
        member = name_bytes[:-1].decode('utf-8')
        data_start = (at + 110 + namelen + 3) // 4 * 4
        require(data_start + size <= len(raw), 'Truncated member')
        content = raw[data_start:data_start+size]; at = (data_start+size+3)//4*4
        if member == 'TRAILER!!!':
            require(size == 0 and not any(raw[at:]), 'Unexpected payload tail'); break
        require(member.startswith('./') and member[1:] in expected and member not in seen,
                'Unexpected, duplicate or escaping member')
        seen.add(member); wanted_mode, _, wanted_content = expected[member[1:]]
        require(mode == wanted_mode and uid == gid == rdevmajor == rdevminor == check == 0
                and links == 1 and mtime == EPOCH and content == wanted_content,
                'Unexpected payload metadata/content')
    require({member[1:] for member in seen} == set(expected), 'Incomplete payload')
    return {'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload),
            'paths': paths, 'requires': requirements, 'fixed_epoch': EPOCH}
