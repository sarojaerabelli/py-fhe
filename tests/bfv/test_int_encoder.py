"""Tests for int_encoder.py."""
import os
import unittest
from bfv.int_encoder import IntegerEncoder
from bfv.bfv_parameters import BFVParameters
from util.plaintext import Plaintext
from util.polynomial import Polynomial

TEST_DIRECTORY = os.path.dirname(__file__)


class TestIntegerEncoder(unittest.TestCase):
    def setUp(self):
        self.degree = 2048
        self.plain_modulus = 256
        self.ciph_modulus = 0x3fffffff000001
        params = BFVParameters(poly_degree=self.degree,
                               plain_modulus=self.plain_modulus,
                               ciph_modulus=self.ciph_modulus)
        self.encoder = IntegerEncoder(params)

    def test_encode(self):
        plain = self.encoder.encode(21)
        self.assertEqual(plain.poly.coeffs, [1, 0, 1, 0, 1] + [0] * (self.degree - 5))

    def test_decode(self):
        plain = Plaintext(Polynomial(self.degree, [1, 0, 1, 0, 1] + [0] * (self.degree - 5)))
        value = self.encoder.decode(plain)
        self.assertEqual(value, 21)

    def run_test_encode_decode(self, inp):
        plain = self.encoder.encode(inp)
        value = self.encoder.decode(plain)
        self.assertEqual(value, inp)

    def test_encode_decode_01(self):
        self.run_test_encode_decode(21321)

    def test_encode_decode_02(self):
        self.run_test_encode_decode(839)

    def test_encode_decode_03(self):
        self.run_test_encode_decode(9000)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
