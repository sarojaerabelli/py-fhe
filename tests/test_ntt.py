"""Tests for ntt.py."""
from math import pi, cos, sin
import os
import unittest
from util.ntt import NTTContext, FFTContext
from util.polynomial import Polynomial
from util.random_sample import sample_uniform
from tests.helper import check_complex_vector_approx_eq

TEST_DIRECTORY = os.path.dirname(__file__)


class TestNTT(unittest.TestCase):
    def setUp(self):
        self.ntt = NTTContext(poly_degree=4, coeff_modulus=73)
        self.num_slots = 8
        self.fft = FFTContext(fft_length=4*self.num_slots)

    def test_ntt(self):
        fwd = self.ntt.ntt(coeffs=[0, 1, 4, 5], rou=self.ntt.roots_of_unity)
        self.assertEqual(fwd, [10, 34, 71, 31])

    def test_intt(self):
        coeffs = [10, 34, 71, 31]
        coeffs = [(coeffs[i] * -18) % 73 for i in range(4)]
        inv = self.ntt.ntt(coeffs=coeffs, rou=self.ntt.roots_of_unity_inv)
        self.assertEqual(inv, [0, 1, 4, 5])

    def test_fft(self):
        fft_vec = self.fft.fft_fwd(coeffs=[0, 1, 4, 5])
        check_complex_vector_approx_eq(fft_vec, [10, -4-4j, -2, -4+4j])

    def test_fft_inverses(self):
        """Checks that fft_fwd and fft_inv are inverses.

        Performs the FFT on the input vector, performs the inverse FFT on the result,
        and checks that they match.

        Raises:
            ValueError: An error if test fails.
        """
        vec = sample_uniform(0, 7, self.num_slots)
        fft_vec = self.fft.fft_fwd(vec)
        to_check = self.fft.fft_inv(fft_vec)

        check_complex_vector_approx_eq(vec, to_check, 0.000001,
                                       "fft_inv is not the inverse of fft_fwd")

    def test_embedding(self):
        """Checks that canonical embedding is correct.

        Checks that the embedding matches the evaluations of the roots of unity at
        indices that are 1 (mod) 4.

        Raises:
            ValueError: An error if test fails.
        """
        coeffs = [10, 34, 71, 31, 1, 2, 3, 4]
        poly = Polynomial(self.num_slots, coeffs)
        fft_length = self.num_slots * 4
        embedding = self.fft.embedding(coeffs)
        evals = []
        power = 1
        for i in range(1, fft_length, 4):
            angle = 2 * pi * power / fft_length
            root_of_unity = complex(cos(angle), sin(angle))
            evals.append(poly.evaluate(root_of_unity))
            power = (power * 5) % fft_length

        check_complex_vector_approx_eq(embedding, evals, 0.00001)

    def test_embedding_inverses(self):
        """Checks that embedding and embedding_inv are inverses.

        Computes the canonical embedding on the input vector, performs the inverse embedding on the
        result, and checks that they match.

        Raises:
            ValueError: An error if test fails.
        """
        n = 1 << 5
        context = FFTContext(fft_length=4 * n)

        vec = sample_uniform(0, 7, n)
        fft_vec = context.embedding(vec)
        to_check = context.embedding_inv(fft_vec)

        check_complex_vector_approx_eq(vec, to_check, 0.000001,
                                       "embedding_inv is not the inverse of embedding")

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
