"""Tests for crt.py."""
import os
import unittest
from util.crt import CRTContext

TEST_DIRECTORY = os.path.dirname(__file__)


class TestCRT(unittest.TestCase):
    def setUp(self):
        self.num_primes = 4
        self.prime_size = 9
        self.poly_degree = 256
        self.crt = CRTContext(self.num_primes, self.prime_size, self.poly_degree)

    def test_generate_primes(self):
        self.assertEqual(self.num_primes, len(self.crt.primes))
        for prime in self.crt.primes:
            self.assertTrue(prime > (1 << self.prime_size))
            self.assertEqual(prime % (2 * self.poly_degree), 1)

    def test_inverse(self):
        original = 178
        vals = self.crt.crt(original)
        reverse = self.crt.reconstruct(vals)
        self.assertEqual(original, reverse)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
