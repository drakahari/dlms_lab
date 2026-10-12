"""Static developer pipe fixtures; no learner input, guest or host mutations."""
import hashlib
import errno
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    'preparation_capture', Path(__file__).parents[1] / 'tools/vm_image/foundation/bounded_capture.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PreparationCaptureTests(unittest.TestCase):
    def test_short_writes_completed_and_no_progress_rejected(self):
        class ShortWriter:
            def __init__(self): self.data = bytearray()
            def write(self, data):
                count = min(3, len(data))
                self.data.extend(data[:count])
                return count
        writer = ShortWriter()
        MODULE.write_all(writer, b'complete console output')
        self.assertEqual(writer.data, b'complete console output')
        class NoProgress:
            def write(self, data): return 0
        with self.assertRaises(OSError): MODULE.write_all(NoProgress(), b'x')

    def test_partial_write_enospc_never_marked_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'console.log'
            read_fd, write_fd = os.pipe()
            os.write(write_fd, b'fixture output')
            os.close(write_fd)
            def injected_enospc(output, data):
                output.write(data[:3])
                raise OSError(errno.ENOSPC, 'injected storage failure')
            with os.fdopen(read_fd, 'rb') as stream, patch.object(MODULE, 'write_all', injected_enospc):
                state = {}
                MODULE.capture_stream(stream, destination, state, 64,
                                      Path(directory) / 'capture.json')
            self.assertEqual(destination.read_bytes(), b'fix')
            self.assertFalse(state['complete'])
            self.assertFalse(state['persisted'])
            self.assertIn('injected storage failure', state['error'])

    def test_summary_persistence_required_and_collision_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            for name, collision in (('success', False), ('collision', True)):
                record = directory / (name + '.json')
                if collision: record.write_bytes(b'original evidence')
                read_fd, write_fd = os.pipe()
                os.write(write_fd, b'static fixture')
                os.close(write_fd)
                with os.fdopen(read_fd, 'rb') as stream:
                    state = {}
                    MODULE.capture_stream(stream, directory / (name + '.log'), state, 64, record)
                self.assertEqual((directory / (name + '.log')).read_bytes(), b'static fixture')
                self.assertEqual(state['complete'], not collision)
                self.assertEqual(state['persisted'], not collision)
                if collision: self.assertEqual(record.read_bytes(), b'original evidence')
                else: self.assertEqual(json.loads(record.read_text()), state)

    def test_small_output_visible_before_eof(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'console.log'
            read_fd, write_fd = os.pipe()
            state = {}
            with os.fdopen(read_fd, 'rb') as stream:
                thread = threading.Thread(target=MODULE.capture_stream,
                                          args=(stream, destination, state, 64))
                thread.start()
                try:
                    os.write(write_fd, b'waiting for input\n')
                    deadline = time.monotonic() + 2
                    while time.monotonic() < deadline:
                        if destination.exists() and destination.read_bytes() == b'waiting for input\n':
                            break
                        threading.Event().wait(0.01)
                    self.assertEqual(destination.read_bytes(), b'waiting for input\n')
                    self.assertTrue(thread.is_alive())
                    self.assertFalse(state['complete'])
                finally:
                    os.close(write_fd)
                    thread.join(2)
                self.assertFalse(thread.is_alive())
                self.assertTrue(state['complete'])
                self.assertFalse(state['overflow'])

    def test_overflow_drained_and_hashed_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'console.log'
            read_fd, write_fd = os.pipe()
            payload = b'0123456789' * 100
            os.write(write_fd, payload)
            os.close(write_fd)
            with os.fdopen(read_fd, 'rb') as stream:
                state = {}
                MODULE.capture_stream(stream, destination, state, 37)
            self.assertEqual(destination.read_bytes(), payload[:37])
            self.assertEqual(state['bytes'], len(payload))
            self.assertEqual(state['sha256'], hashlib.sha256(payload).hexdigest())
            self.assertTrue(state['complete'])
            self.assertTrue(state['overflow'])
            with os.fdopen(os.open('/dev/null', os.O_RDONLY), 'rb') as stream:
                collision = {}
                MODULE.capture_stream(stream, destination, collision, 37)
            self.assertIsNotNone(collision['error'])
            self.assertFalse(collision['complete'])
            self.assertEqual(destination.read_bytes(), payload[:37])
