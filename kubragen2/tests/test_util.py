import unittest

from kubragen2.exception import InvalidParamError
from kubragen2.kutil import unit_to_bytes


class TestUtil(unittest.TestCase):
    def test_unit_to_bytes(self):
        self.assertEqual(unit_to_bytes('10Mi'), 10 * 1024 * 1024)
        self.assertEqual(unit_to_bytes('92Pi'), 92 * 1024 * 1024 * 1024 * 1024 * 1024)
        self.assertEqual(unit_to_bytes('415P'), 415 * 1000 * 1000 * 1000 * 1000 * 1000)
        with self.assertRaises(InvalidParamError):
            unit_to_bytes('WrongValue')
