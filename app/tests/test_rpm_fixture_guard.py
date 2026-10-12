"""Pure declared-transaction tests, separate from required real DNF evidence."""
import importlib.util
from pathlib import Path
import unittest
import tempfile
import os
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    'rpm_fixture_guard', Path(__file__).parents[1] / 'tools/vm_image/rpm/transaction-helper.py')
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
# Distinct test tokens; native tests must use actual DNF constants and transactions.
ACTIONS = (1, 2, 3, 4, 5, 6)
DATA1 = ('ll-rpm-data', 'noarch', '0', '1.0', '1')
DATA2 = ('ll-rpm-data', 'noarch', '0', '2.0', '1')
REPORT = ('ll-rpm-report', 'noarch', '0', '1.0', '1')


class FixtureGuardTests(unittest.TestCase):
    def test_directory_repeated_enumeration_uses_independent_cursor(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / 'operation.lock').write_bytes(b'lock')
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.listdir(fd)  # Exercise prior enumeration on the original FD.
                for _ in range(4): self.assertEqual(GUARD.directory_names(fd), ['operation.lock'])
                (Path(root) / 'unexpected').write_bytes(b'retained')
                self.assertEqual(set(GUARD.directory_names(fd)), {'operation.lock', 'unexpected'})
            finally: os.close(fd)

    def test_directory_mutation_during_enumeration_refused(self):
        with tempfile.TemporaryDirectory() as root:
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            original = os.listdir
            def mutated(target):
                result = original(target)
                (Path(root) / 'substitution').write_bytes(b'changed')
                return result
            try:
                with patch.object(GUARD.os, 'listdir', side_effect=mutated), self.assertRaisesRegex(GUARD.Refused, 'during enumeration'):
                    GUARD.directory_names(fd)
            finally: os.close(fd)

    def test_exact_supported_operations_and_final_states(self):
        cases = (
            ('data1', {}, {'ll-rpm-data': DATA1}),
            ('pair', {}, {'ll-rpm-data': DATA2, 'll-rpm-report': REPORT}),
            ('upgrade', {'ll-rpm-data': DATA1}, {'ll-rpm-data': DATA2}),
            ('reinstall', {'ll-rpm-data': DATA2, 'll-rpm-report': REPORT},
             {'ll-rpm-data': DATA2, 'll-rpm-report': REPORT}),
            ('remove-report', {'ll-rpm-data': DATA2, 'll-rpm-report': REPORT},
             {'ll-rpm-data': DATA2}),
            ('remove-data', {'ll-rpm-data': DATA2}, {}),
        )
        for operation, before, after in cases:
            with self.subTest(operation=operation):
                original = dict(before)
                _, expected, _ = GUARD.expected_operation(operation, before, ACTIONS)
                GUARD.validate_plan(list(reversed(expected)), expected)
                self.assertEqual(GUARD.expected_final(before, expected, ACTIONS), after)
                self.assertEqual(before, original)

    def test_resolved_plan_rejects_extra_identity_or_action(self):
        _, expected, _ = GUARD.expected_operation('pair', {}, ACTIONS)
        for extra in (
            ('bash', 'x86_64', '0', '1', '1', 6),
            ('ll-rpm-data', 'x86_64', '0', '2.0', '1', 1),
            ('ll-rpm-report', 'noarch', '1', '1.0', '1', 1),
            DATA1 + (1,),
            DATA2 + (6,),
        ):
            with self.subTest(extra=extra), self.assertRaises(GUARD.Refused):
                GUARD.validate_plan(expected + [extra], expected)

    def test_outgoing_halves_are_not_ignored(self):
        for operation in ('upgrade', 'reinstall'):
            before = {'ll-rpm-data': DATA1 if operation == 'upgrade' else DATA2}
            _, expected, _ = GUARD.expected_operation(operation, before, ACTIONS)
            with self.subTest(operation=operation), self.assertRaises(GUARD.Refused):
                GUARD.validate_plan(expected[:1], expected)

    def test_empty_duplicate_or_excessive_plan_refused(self):
        expected = [DATA1 + (1,)]
        for rows in ([], expected * 2, expected * 5):
            with self.subTest(rows=rows), self.assertRaises(GUARD.Refused):
                GUARD.validate_plan(rows, expected)

    def test_wrong_state_and_implicit_dependent_removal_refused(self):
        cases = (
            ('data1', {'ll-rpm-data': DATA1}),
            ('pair', {'ll-rpm-data': DATA2}),
            ('upgrade', {'ll-rpm-data': DATA2}),
            ('upgrade', {'ll-rpm-data': DATA1, 'll-rpm-report': REPORT}),
            ('reinstall', {}),
            ('remove-data', {'ll-rpm-data': DATA2, 'll-rpm-report': REPORT}),
            ('remove-report', {}),
            ('arbitrary', {}),
        )
        for operation, before in cases:
            with self.subTest(operation=operation, before=before), self.assertRaises(GUARD.Refused):
                GUARD.expected_operation(operation, before, ACTIONS)
