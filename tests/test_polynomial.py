"""Tests for polynomial.py."""

from math import ceil, floor, log, sqrt
import os
import unittest
from util.crt import CRTContext
from util.polynomial import Polynomial
from util.random_sample import sample_uniform

TEST_DIRECTORY = os.path.dirname(__file__)


class TestPolynomial(unittest.TestCase):
    def setUp(self):
        self.degree = 5
        self.coeff_modulus = 60
        self.poly1 = Polynomial(self.degree, [0, 1, 4, 5, 59])
        self.poly2 = Polynomial(self.degree, [1, 2, 4, 3, 2])

    def test_add(self):
        poly_sum = self.poly1.add(self.poly2, self.coeff_modulus)
        poly_sum2 = self.poly2.add(self.poly1, self.coeff_modulus)
        self.assertEqual(poly_sum.coeffs, [1, 3, 8, 8, 1])
        self.assertEqual(poly_sum.coeffs, poly_sum2.coeffs)

    def test_subtract(self):
        poly_diff = self.poly1.subtract(self.poly2, self.coeff_modulus)
        self.assertEqual(poly_diff.coeffs, [59, 59, 0, 2, 57])

    def test_multiply(self):
        poly1 = Polynomial(4, [0, 1, 4, 5])
        poly2 = Polynomial(4, [1, 2, 4, 3])
        poly_prod = poly1.multiply(poly2, 73)
        poly_prod2 = poly2.multiply(poly1, 73)
        self.assertEqual(poly_prod.coeffs, [44, 42, 64, 17])
        self.assertEqual(poly_prod.coeffs, poly_prod2.coeffs)

    def test_multiply_crt(self):
        log_modulus = 10
        modulus = 1 << log_modulus
        prime_size = 59
        log_poly_degree = 2
        poly_degree = 1 << log_poly_degree
        num_primes = (2 + log_poly_degree + 4 * log_modulus + prime_size - 1) // prime_size
        crt = CRTContext(num_primes, prime_size, poly_degree)
        poly1 = Polynomial(poly_degree, [0, 1, 4, 5])
        poly2 = Polynomial(poly_degree, [1, 2, 4, 3])
        poly_prod = poly1.multiply_crt(poly2, crt)
        poly_prod = poly_prod.mod_small(modulus)
        poly_prod2 = poly2.multiply_crt(poly1, crt)
        poly_prod2 = poly_prod2.mod_small(modulus)
        actual = poly1.multiply_naive(poly2, modulus)
        actual = actual.mod_small(modulus)
        self.assertEqual(poly_prod.coeffs, actual.coeffs)
        self.assertEqual(poly_prod.coeffs, poly_prod2.coeffs)

    def test_multiply_fft(self):
        poly1 = Polynomial(4, [0, 1, 4, 5])
        poly2 = Polynomial(4, [1, 2, 4, 3])

        poly_prod = poly1.multiply_fft(poly2)
        actual_coeffs = [-29, -31, -9, 17]

        self.assertEqual(poly_prod.coeffs, actual_coeffs)

    def test_multiply_naive(self):
        poly_prod = self.poly1.multiply_naive(self.poly2, self.coeff_modulus)
        poly_prod2 = self.poly2.multiply_naive(self.poly1, self.coeff_modulus)
        self.assertEqual(poly_prod.coeffs, [28, 42, 59, 19, 28])
        self.assertEqual(poly_prod.coeffs, poly_prod2.coeffs)

    def test_multiply_01(self):
        poly1 = Polynomial(4, sample_uniform(0, 30, 4))
        poly2 = Polynomial(4, sample_uniform(0, 30, 4))

        poly_prod = poly1.multiply_fft(poly2)
        poly_prod2 = poly1.multiply_naive(poly2)

        self.assertEqual(poly_prod.coeffs, poly_prod2.coeffs)

    def test_scalar_multiply(self):
        poly_prod = self.poly1.scalar_multiply(-1, self.coeff_modulus)
        self.assertEqual(poly_prod.coeffs, [0, 59, 56, 55, 1])

    def test_rotate(self):
        poly1 = Polynomial(4, [0, 1, 4, 59])
        poly_rot = poly1.rotate(3)
        self.assertEqual(poly_rot.coeffs, [0, -1, 4, -59])

    def test_round(self):
        poly = Polynomial(self.degree, [0.51, -3.2, 54.666, 39.01, 0])
        poly_rounded = poly.round()
        self.assertEqual(poly_rounded.coeffs, [1, -3, 55, 39, 0])

    def test_mod(self):
        poly = Polynomial(self.degree, [57, -34, 100, 1000, -7999])
        poly_rounded = poly.mod(self.coeff_modulus)
        self.assertEqual(poly_rounded.coeffs, [57, 26, 40, 40, 41])

    def test_base_decompose(self):
        base = ceil(sqrt(self.coeff_modulus))
        num_levels = floor(log(self.coeff_modulus, base)) + 1
        poly_decomposed = self.poly1.base_decompose(base, num_levels)
        self.assertEqual(poly_decomposed[0].coeffs, [0, 1, 4, 5, 3])
        self.assertEqual(poly_decomposed[1].coeffs, [0, 0, 0, 0, 7])

    def test_evaluate(self):
        poly = Polynomial(self.degree, [0, 1, 2, 3, 4])
        result = poly.evaluate(3)
        self.assertEqual(result, 426)

    def test_str(self):
        string1 = str(self.poly1)
        string2 = str(self.poly2)
        self.assertEqual(string1, '59x^4 + 5x^3 + 4x^2 + x')
        self.assertEqual(string2, '2x^4 + 3x^3 + 4x^2 + 2x + 1')

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
