"""Developer QMP wire-format tests, not a substitute for native identity proof."""
import importlib.util
import json
import hashlib
import os
from pathlib import Path
import socket
import threading
import time
import unittest
import stat
from unittest.mock import patch
from types import SimpleNamespace

SPEC = importlib.util.spec_from_file_location(
    'preparation_console', Path(__file__).parents[1] / 'tools/vm_image/foundation/preparation_console.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PreparationConsoleTests(unittest.TestCase):
    def test_final_reconnect_binding_refusal_before_socket(self):
        raw = b'fixture\0'
        identity = {'pid': 123, 'start': '10', 'boot': 'fixture',
                    'argv_sha256': hashlib.sha256(raw).hexdigest(), 'exe': 'original'}
        changed = dict(identity); changed['exe'] = 'substituted'
        directory = SimpleNamespace(fd=3, write=lambda *args: None)
        with patch.object(MODULE, 'process_identity', side_effect=[identity, identity, changed]), \
                patch.object(MODULE.Path, 'read_bytes', return_value=raw), \
                patch.object(MODULE.os, 'stat', return_value=SimpleNamespace(st_mode=stat.S_IFSOCK, st_uid=os.getuid())), \
                patch.object(MODULE.socket, 'socket', side_effect=AssertionError('socket reached')):
            with self.assertRaisesRegex(ValueError, 'final identity'):
                MODULE.PreparationConsole(directory, SimpleNamespace(pid=123), ['fixture'], 'fixture', expected_identity=identity)

    def test_reconnect_rejects_changed_original_identity_before_paths_or_socket(self):
        original = {'pid': 123, 'start': '10', 'boot': 'fixture', 'argv_sha256': 'a'}
        for key, replacement in (('start', '11'), ('boot', 'other'), ('argv_sha256', 'b')):
            changed = dict(original); changed[key] = replacement
            with self.subTest(key=key), patch.object(MODULE, 'process_identity', return_value=changed), \
                    patch.object(MODULE.socket, 'socket', side_effect=AssertionError('socket reached')):
                with self.assertRaisesRegex(ValueError, 'original binding'):
                    MODULE.PreparationConsole(None, SimpleNamespace(pid=123), [], 'fixture', expected_identity=original)

    def test_json_line_wire_protocol_and_events(self):
        left, right = socket.socketpair()
        control = MODULE.PreparationConsole.__new__(MODULE.PreparationConsole)
        control.sock = left; control.buf = b''; control.events = []; control.sequence = 0
        # This test verifies only wire format; native process/peer checks remain
        # mandatory and are exercised against the actual preparation QEMU.
        control.verify = lambda: None
        received = []
        def server():
            try:
                right.settimeout(1)
                wire = bytearray()
                while not wire.endswith(b'\n'):
                    chunk = right.recv(1)
                    if not chunk: return
                    wire.extend(chunk)
                received.append(bytes(wire))
                right.sendall(b'{"event":"STOP"}\n{"return":{"running":true},"id":1}\n')
            finally: right.close()
        worker = threading.Thread(target=server); worker.start()
        try:
            self.assertEqual(control.status(), {'running': True})
            self.assertEqual(json.loads(received[0]), {'execute': 'query-status', 'id': 1})
            self.assertTrue(received[0].endswith(b'\n'))
            self.assertEqual(control.events, [{'event': 'STOP'}])
        finally:
            left.close(); worker.join(2)
        self.assertFalse(worker.is_alive())

    def test_unapproved_operation_rejected_before_identity_or_socket_use(self):
        control = MODULE.PreparationConsole.__new__(MODULE.PreparationConsole)
        control.verify = lambda: self.fail('Unsupported command reached identity/socket use')
        for command in ('quit', 'stop', 'human-monitor-command', 'guest-exec'):
            with self.subTest(command=command), self.assertRaises(ValueError): control._call(command)

    def test_partial_line_absolute_deadline(self):
        left, right = socket.socketpair()
        control = MODULE.PreparationConsole.__new__(MODULE.PreparationConsole)
        control.sock = left; control.buf = b''
        start = time.monotonic()
        try:
            right.sendall(b'{"return":')
            with self.assertRaises((socket.timeout, ValueError)): control.read(start + .05)
            self.assertLess(time.monotonic() - start, .5)
        finally: left.close(); right.close()
