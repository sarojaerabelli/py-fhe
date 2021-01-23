"""Tests for dcrt_polynomial.py."""

from math import ceil, floor, log, sqrt
import os
import unittest
from util.crt import CRTContext
from util.dcrt_polynomial import DCRTPolynomial
from util.polynomial import Polynomial
from util.random_sample import sample_uniform

TEST_DIRECTORY = os.path.dirname(__file__)


class TestDCRTPolynomial(unittest.TestCase):
    def setUp(self):
        self.degree = 8
        self.coeff_modulus = 1 << 1200
        prime_size = 59
        num_primes = 1 + int((1 + log(self.degree, 2) + 4 * log(self.coeff_modulus, 2) \
             / prime_size))
        self.crt_context = CRTContext(num_primes, prime_size, self.degree)
        coeffs1 = [0, 1, 4, 5, 59, 1, 1 << 1199, 3]
        coeffs2 = [1, 2, 4, 3, 2, 1, 1, (1 << 1200) - 1]
        self.dcrt_poly1 = DCRTPolynomial(self.degree, coeffs1, self.crt_context)
        self.dcrt_poly2 = DCRTPolynomial(self.degree, coeffs2, self.crt_context)
        self.poly1 = Polynomial(self.degree, coeffs1)
        self.poly2 = Polynomial(self.degree, coeffs2)

    def test_add(self):
        dcrt_poly_sum = self.dcrt_poly1.add(self.dcrt_poly2)
        dcrt_poly_sum2 = self.dcrt_poly2.add(self.dcrt_poly1)
        poly_sum = dcrt_poly_sum.reconstruct().mod_small(self.coeff_modulus)
        poly_sum2 = dcrt_poly_sum2.reconstruct().mod_small(self.coeff_modulus)
        expected_poly_sum = self.poly1.add(self.poly2).mod_small(self.coeff_modulus)
        self.assertEqual(poly_sum.coeffs, expected_poly_sum.coeffs)
        self.assertEqual(poly_sum.coeffs, poly_sum2.coeffs)

    def test_subtract(self):
        dcrt_poly_diff = self.dcrt_poly1.subtract(self.dcrt_poly2)
        poly_diff = dcrt_poly_diff.reconstruct().mod_small(self.coeff_modulus)
        expected_poly_diff = self.poly1.subtract(self.poly2).mod_small(self.coeff_modulus)
        self.assertEqual(poly_diff.coeffs, expected_poly_diff.coeffs)

    def test_multiply(self):
        dcrt_poly_prod = self.dcrt_poly1.multiply(self.dcrt_poly2)
        dcrt_poly_prod2 = self.dcrt_poly2.multiply(self.dcrt_poly1)
        poly_prod = dcrt_poly_prod.reconstruct().mod_small(self.coeff_modulus)
        poly_prod2 = dcrt_poly_prod2.reconstruct().mod_small(self.coeff_modulus)
        expected_poly_prod = self.poly1.multiply(self.poly2, self.coeff_modulus).mod_small(self.coeff_modulus)
        self.assertEqual(poly_prod.coeffs, expected_poly_prod.coeffs)
        self.assertEqual(poly_prod.coeffs, poly_prod2.coeffs)

    def test_scalar_multiply(self):
        scalar = -1
        dcrt_poly_prod = self.dcrt_poly1.scalar_multiply(scalar)
        poly_prod = dcrt_poly_prod.reconstruct().mod_small(self.coeff_modulus)
        expected_poly_prod = self.poly1.scalar_multiply(scalar, self.coeff_modulus).mod_small(self.coeff_modulus)
        self.assertEqual(poly_prod.coeffs, expected_poly_prod.coeffs)

    def test_scalar_integer_divide(self):
        # TODO: Check whether this introduces error??
        scalar = 10
        dcrt_poly_quotient = self.dcrt_poly1.scalar_integer_divide(scalar)
        poly_quotient = dcrt_poly_quotient.reconstruct().mod_small(self.coeff_modulus)
        expected_poly_quotient = self.poly1.scalar_integer_divide(scalar).mod_small(self.coeff_modulus)
        self.assertEqual(poly_quotient.coeffs, expected_poly_quotient.coeffs)

    def test_rotate(self):
        scalar = 3
        dcrt_poly_rot = self.dcrt_poly1.rotate(scalar)
        poly_rot = dcrt_poly_rot.reconstruct().mod_small(self.coeff_modulus)
        expected_poly_rot = self.poly1.rotate(scalar).mod_small(self.coeff_modulus)
        self.assertEqual(poly_rot.coeffs, expected_poly_rot.coeffs)

    def test_conjugate(self):
        dcrt_poly_conj = self.dcrt_poly1.conjugate()
        poly_conj = dcrt_poly_conj.reconstruct().mod_small(self.coeff_modulus)
        expected_poly_conj = self.poly1.conjugate().mod_small(self.coeff_modulus)
        self.assertEqual(poly_conj.coeffs, expected_poly_conj.coeffs)

    def test_round(self):
        # TODO: Check whether this introduces error??
        dcrt_poly = DCRTPolynomial(self.degree, [0.51, -3.2, 54.666, 39.01, 0, 0, 0, 0], self.crt_context)
        poly = Polynomial(self.degree, [0.51, -3.2, 54.666, 39.01, 0, 0, 0, 0])
        dcrt_poly_rounded = dcrt_poly.round()
        poly_rounded = dcrt_poly_rounded.reconstruct().mod_small(self.coeff_modulus)
        expected_poly_rounded = poly.round().mod_small(self.coeff_modulus)
        self.assertEqual(poly_rounded.coeffs, expected_poly_rounded.coeffs)

    def test_floor(self):
        # TODO: Check whether this introduces error??
        dcrt_poly = DCRTPolynomial(self.degree, [0.51, -3.2, 54.666, 39.01, 0, 0, 0, 0], self.crt_context)
        poly = Polynomial(self.degree, [0.51, -3.2, 54.666, 39.01, 0, 0, 0, 0])
        dcrt_poly_floor = dcrt_poly.floor()
        poly_floor = dcrt_poly_floor.reconstruct().mod_small(self.coeff_modulus)
        expected_poly_floor = poly.floor().mod_small(self.coeff_modulus)
        self.assertEqual(poly_floor.coeffs, expected_poly_floor.coeffs)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
