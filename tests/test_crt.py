"""Tests for crt.py."""
import os
import unittest
from util.crt import CRTContext

TEST_DIRECTORY = os.path.dirname(__file__)


class TestCRT(unittest.TestCase):
    def setUp(self):
        self.crt = CRTContext(primes=[2, 3, 5, 7])

    def test_transform(self):
        ans = self.crt.transform([1, 2, 4, 4])
        self.assertEqual(179, ans)

    def test_inverse_transform(self):
        vals = self.crt.inverse_transform(90)
        self.assertEqual(vals, [0, 0, 0, 6])

    def test_inverse(self):
        original = 178
        vals = self.crt.inverse_transform(original)
        reverse = self.crt.transform(vals)
        self.assertEqual(original, reverse)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
