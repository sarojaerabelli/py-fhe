"""Tests for batch_encoder.py."""
import os
import unittest

from bfv.batch_encoder import BatchEncoder
from bfv.bfv_parameters import BFVParameters
from util.random_sample import sample_uniform

TEST_DIRECTORY = os.path.dirname(__file__)


class TestBatchEncoder(unittest.TestCase):
    def setUp(self):
        self.degree = 2048
        self.plain_modulus = 256
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

    def test_encode_decode_01(self):
        self.run_test_encode_decode(sample_uniform(0, self.plain_modulus, self.degree))

    def test_encode_decode_02(self):
        self.run_test_encode_decode([0] * self.degree)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
