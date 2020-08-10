"""Tests for ckks_encoder.py."""
import os
import unittest

from ckks.ckks_encoder import CKKSEncoder
from ckks.ckks_parameters import CKKSParameters
from tests.helper import check_complex_vector_approx_eq
from util.random_sample import sample_random_complex_vector
from util.plaintext import Plaintext

TEST_DIRECTORY = os.path.dirname(__file__)


class TestCKKSEncoder(unittest.TestCase):
    def setUp(self):
        self.ciph_modulus = 1 << 40
        self.big_modulus = 1 << 1200
        self.scaling_factor = 1 << 30
        self.degree = 2048
        params = CKKSParameters(poly_degree=self.degree,
                                ciph_modulus=self.ciph_modulus,
                                big_modulus=self.big_modulus,
                                scaling_factor=self.scaling_factor)
        self.encoder = CKKSEncoder(params)

    def run_test_encode_decode(self, vec):
        """Checks that encode and decode are inverses.

        Encodes the input vector, decodes the result, and checks that
        they match.

        Args:
            vec (list (complex)): Vector of complex numbers to encode.

        Raises:
            ValueError: An error if test fails.
        """
        plain = self.encoder.encode(vec, self.scaling_factor)
        value = self.encoder.decode(plain)
        check_complex_vector_approx_eq(vec, value, error=0.1)

    def run_test_multiply(self, vec1, vec2):
        """Checks that encode satisfies homomorphic multiplication.

        Encodes two input vectors, and check that their product matches
        before and after encoding. Before encoding, the product is
        component-wise, and after encoding, the product is polynomial, since
        the encoding includes an inverse FFT operation.

        Args:
            vec1 (list (complex)): First vector.
            vec2 (list (complex)): Second vector.

        Raises:
            ValueError: An error if test fails.
        """
        orig_prod = [0] * (self.degree // 2)
        for i in range(self.degree // 2):
            orig_prod[i] = vec1[i] * vec2[i]

        plain1 = self.encoder.encode(vec1, self.scaling_factor)
        plain2 = self.encoder.encode(vec2, self.scaling_factor)
        plain_prod = Plaintext(plain1.poly.multiply_naive(plain2.poly),
                               scaling_factor=self.scaling_factor**2)
        expected = self.encoder.decode(plain_prod)

        check_complex_vector_approx_eq(expected, orig_prod, error=0.1)

    def test_encode_decode_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        self.run_test_encode_decode(vec)

    def test_multiply_01(self):
        vec1 = sample_random_complex_vector(self.degree // 2)
        vec2 = sample_random_complex_vector(self.degree // 2)
        self.run_test_multiply(vec1, vec2)


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
