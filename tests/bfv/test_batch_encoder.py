"""Tests for batch_encoder.py."""
import os
import unittest

from bfv.batch_encoder import BatchEncoder
from bfv.bfv_parameters import BFVParameters
from util.plaintext import Plaintext
from util.random_sample import sample_uniform

TEST_DIRECTORY = os.path.dirname(__file__)


class TestBatchEncoder(unittest.TestCase):
    def setUp(self):
        self.degree = 8
        self.plain_modulus = 17
        self.ciph_modulus = 0x3fffffff000001
        params = BFVParameters(poly_degree=self.degree,
                               plain_modulus=self.plain_modulus,
                               ciph_modulus=self.ciph_modulus)
        self.encoder = BatchEncoder(params)

    def run_test_encode_decode(self, inp):
        plain = self.encoder.encode(inp)
        value = self.encoder.decode(plain)
        self.assertEqual(len(value), len(inp))
        self.assertEqual(value, inp)

    def run_test_encode_multiply(self, inp1, inp2):
        prod = [(inp1[i] * inp2[i]) % self.plain_modulus for i in range(len(inp1))]
        plain1 = self.encoder.encode(inp1)
        plain2 = self.encoder.encode(inp2)
        plain_prod = Plaintext(plain1.poly.multiply(plain2.poly, self.plain_modulus))
        decoded_prod = self.encoder.decode(plain_prod)
        self.assertEqual(prod, decoded_prod)

    def test_encode_decode_01(self):
        vec = sample_uniform(0, self.plain_modulus, self.degree)
        self.run_test_encode_decode(vec)

    def test_encode_decode_02(self):
        self.run_test_encode_decode([0] * self.degree)

    def test_encode_multiply_01(self):
        vec1 = sample_uniform(0, self.plain_modulus, self.degree)
        vec2 = sample_uniform(0, self.plain_modulus, self.degree)
        self.run_test_encode_multiply(vec1, vec2)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
