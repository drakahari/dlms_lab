"""Developer-only preparation console. Not part of the app's VM controller.

Exact same-user QEMU identity, inherited private directory, peer credentials and
UUID are checked before every operation. Only status and ACPI guest powerdown
are exposed. A request alone never proves clean shutdown.
"""
import json
import hashlib
import os
import socket
import stat
import struct
import subprocess
import time
import uuid as uuid_module
from pathlib import Path
from learning_lab.vm_preview.files import require
from learning_lab.vm_preview.process import process_identity
OPERATIONS = frozenset(('qmp_capabilities', 'query-uuid', 'query-status', 'system_powerdown'))


class PreparationConsole:
    def __init__(self, directory, process, args, uuid, expected_identity=None):
        self.directory, self.process, self.uuid = directory, process, uuid
        self.identity = process_identity(process.pid)
        require(self.identity is not None, 'Preparation QEMU exited before control readiness')
        require(expected_identity is None or self.identity == expected_identity,
                'Preparation identity differs from original binding; no connection permitted')
        expected_raw = b'\0'.join(os.fsencode(arg) for arg in args) + b'\0'
        initial_raw = (Path('/proc') / str(process.pid) / 'cmdline').read_bytes()
        require(len(expected_raw) <= 16384 and len(initial_raw) <= 16384,
                'Preparation argv exceeds fixed-input bound')
        initial_identity = dict(self.identity)
        self.sock = None
        self.buf, self.events, self.sequence = b'', [], 0
        deadline = time.monotonic() + 10
        while True:
            # Poll a concrete readiness condition, not until an argv mismatch
            # disappears. No connection/command is permitted during this phase.
            actual = process_identity(process.pid)
            require(actual is not None and all(actual[key] == initial_identity[key]
                    for key in ('pid', 'start', 'boot')),
                    'Preparation process exited or immutable identity changed')
            try:
                info = os.stat('qmp', dir_fd=directory.fd, follow_symlinks=False)
                require(stat.S_ISSOCK(info.st_mode) and info.st_uid == os.getuid(),
                        'Unsafe preparation QMP socket')
                break
            except FileNotFoundError:
                require(time.monotonic() < deadline, 'Preparation QMP socket not ready')
                time.sleep(.05)
        raw = (Path('/proc') / str(process.pid) / 'cmdline').read_bytes()
        require(len(raw) <= 16384, 'Preparation argv exceeds fixed-input bound')
        directory.write('startup-observation-' + uuid_module.uuid4().hex + '.json', {
            'initial_identity': initial_identity, 'initial_raw_hex': initial_raw.hex(),
            'ready_raw_hex': raw.hex(), 'expected_raw_hex': expected_raw.hex()})
        require(raw == expected_raw, 'Ready preparation launch differs from recorded arguments')
        self.identity = process_identity(process.pid)
        require(self.identity is not None and all(self.identity[key] == initial_identity[key]
                for key in ('pid', 'start', 'boot')) and
                self.identity['argv_sha256'] == hashlib.sha256(expected_raw).hexdigest(),
                'Preparation identity/argv changed at binding')
        require(expected_identity is None or self.identity == expected_identity,
                'Preparation final identity differs from original binding; no connection permitted')
        self.verify()
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.settimeout(max(.001, min(2, deadline - time.monotonic())))
        try:
            self.sock.connect(f'/proc/self/fd/{directory.fd}/qmp')
            pid, uid, gid = struct.unpack('3i', self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            require(pid == process.pid and uid == os.getuid(), 'Preparation control peer mismatch')
            require('QMP' in self.read(deadline), 'Invalid preparation greeting')
            self._call('qmp_capabilities', deadline)
            require(self._call('query-uuid', deadline)['UUID'] == uuid, 'Preparation UUID mismatch')
            self.verify()
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def verify(self):
        require(process_identity(self.process.pid) == self.identity,
                'Preparation process exited or identity changed; no control sent')

    def read(self, deadline):
        require(time.monotonic() < deadline, 'Preparation control deadline exceeded')
        while b'\n' not in self.buf:
            remaining = deadline - time.monotonic()
            require(remaining > 0, 'Preparation control deadline exceeded')
            self.sock.settimeout(min(2, remaining))
            chunk = self.sock.recv(8192)
            if not chunk:
                raise EOFError('Preparation QMP disconnected')
            self.buf += chunk
            require(len(self.buf) <= 65536, 'Oversized preparation QMP response')
        line, self.buf = self.buf.split(b'\n', 1)
        value = json.loads(line)
        require(isinstance(value, dict), 'Malformed preparation QMP response')
        return value

    def _call(self, operation, deadline=None):
        require(operation in OPERATIONS, 'Unsupported preparation control operation')
        deadline = time.monotonic() + 5 if deadline is None else deadline
        require(time.monotonic() < deadline, 'Preparation control deadline exceeded')
        self.verify()
        self.sequence += 1
        self.sock.settimeout(min(2, deadline - time.monotonic()))
        self.sock.sendall((json.dumps({'execute': operation, 'id': self.sequence}) + '\n').encode())
        for _ in range(128):
            value = self.read(deadline)
            if 'event' in value:
                self.events.append(value)
                require(len(self.events) <= 128, 'Excessive preparation QMP events')
                continue
            require(value.get('id') == self.sequence and 'error' not in value,
                    'Unexpected/refused preparation control response')
            return value.get('return')
        raise RuntimeError('Excessive preparation control responses')

    def status(self):
        return self._call('query-status')

    def powerdown(self, seconds=35):
        deadline = time.monotonic() + seconds
        self._call('system_powerdown', deadline)
        while time.monotonic() < deadline:
            try:
                value = self.read(deadline)
                if 'event' in value:
                    self.events.append(value)
                    require(len(self.events) <= 128, 'Excessive shutdown events')
            except socket.timeout:
                pass
            except EOFError:
                break
            if self.process.poll() is not None:
                break
        remaining = max(0, deadline - time.monotonic())
        try:
            self.process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            raise RuntimeError('Preparation guest remains active; no force stop authorized')
        require(process_identity(self.process.pid) is None, 'Preparation process still active')
        return any(event.get('event') == 'SHUTDOWN' and event.get('data', {}).get('guest') is True
                   for event in self.events)
