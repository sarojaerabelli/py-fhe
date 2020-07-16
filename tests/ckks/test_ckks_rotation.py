"""Tests for ckks_evaluator.py for rotation, conjugation, and matrix multiplication."""

from math import sqrt
import os
import unittest

from ckks.ckks_decryptor import CKKSDecryptor
from ckks.ckks_encoder import CKKSEncoder
from ckks.ckks_encryptor import CKKSEncryptor
from ckks.ckks_evaluator import CKKSEvaluator
from ckks.ckks_key_generator import CKKSKeyGenerator
from ckks.ckks_parameters import CKKSParameters
from tests.helper import check_complex_vector_approx_eq
from util.ciphertext import Ciphertext
from util.matrix_operations import matrix_vector_multiply
from util.polynomial import Polynomial
from util.random_sample import sample_random_complex_vector
from util.secret_key import SecretKey

TEST_DIRECTORY = os.path.dirname(__file__)

class TestRotation(unittest.TestCase):
    def setUp(self):
        self.degree = 16
        self.ciph_modulus = 1 << 1200
        self.big_modulus = 1 << 1200
        self.scaling_factor = 1 << 30
        self.params = CKKSParameters(poly_degree=self.degree,
                                     ciph_modulus=self.ciph_modulus,
                                     big_modulus=self.big_modulus,
                                     scaling_factor=self.scaling_factor)
        self.key_generator = CKKSKeyGenerator(self.params)
        public_key = self.key_generator.public_key
        self.secret_key = self.key_generator.secret_key
        self.relin_key = self.key_generator.relin_key
        self.encoder = CKKSEncoder(self.params)
        self.encryptor = CKKSEncryptor(self.params, public_key)
        self.decryptor = CKKSDecryptor(self.params, self.secret_key)
        self.evaluator = CKKSEvaluator(self.params)

    def run_test_simple_rotate(self, message, rot):
        poly = Polynomial(self.degree // 2, message)

        plain = self.encoder.encode(message, self.scaling_factor)

        rot_message = [0] * poly.ring_degree
        for i in range(poly.ring_degree):
            rot_message[i] = poly.coeffs[(i + rot) % poly.ring_degree]

        ciph = self.encryptor.encrypt(plain)
        ciph_rot0 = ciph.c0.rotate(rot).mod_small(self.ciph_modulus)
        ciph_rot1 = ciph.c1.rotate(rot).mod_small(self.ciph_modulus)
        ciph_rot = Ciphertext(ciph_rot0, ciph_rot1, ciph.scaling_factor, self.ciph_modulus)
        decryptor = CKKSDecryptor(self.params, SecretKey(self.secret_key.s.rotate(rot)))
        decrypted_rot = decryptor.decrypt(ciph_rot)
        decoded_rot = self.encoder.decode(decrypted_rot)

        check_complex_vector_approx_eq(rot_message, decoded_rot, error=0.005)

    def run_test_rotate(self, message, r):
        poly = Polynomial(self.degree // 2, message)

        plain = self.encoder.encode(message, self.scaling_factor)

        rot_message = [0] * poly.ring_degree
        for i in range(poly.ring_degree):
            rot_message[i] = poly.coeffs[(i + r) % poly.ring_degree]

        ciph = self.encryptor.encrypt(plain)
        rot_key = self.key_generator.generate_rot_key(r)

        ciph_rot = self.evaluator.rotate(ciph, r, rot_key)
        decrypted_rot = self.decryptor.decrypt(ciph_rot)
        decoded_rot = self.encoder.decode(decrypted_rot)

        check_complex_vector_approx_eq(rot_message, decoded_rot, error=0.005)

    def run_test_conjugate(self, message):
        poly = Polynomial(self.degree // 2, message)

        plain = self.encoder.encode(message, self.scaling_factor)

        conj_message = [c.conjugate() for c in poly.coeffs]

        ciph = self.encryptor.encrypt(plain)
        conj_key = self.key_generator.generate_conj_key()
        ciph_conj = self.evaluator.conjugate(ciph, conj_key)
        decrypted_conj = self.decryptor.decrypt(ciph_conj)
        decoded_conj = self.encoder.decode(decrypted_conj)

        check_complex_vector_approx_eq(conj_message, decoded_conj, error=0.005)

    def run_test_multiply_matrix(self, message, mat):
        matrix_prod_message = matrix_vector_multiply(mat, message)

        plain = self.encoder.encode(message, self.scaling_factor)
        ciph = self.encryptor.encrypt(plain)

        rot_keys = {}
        matrix_len = len(mat)
        matrix_len_factor1 = int(sqrt(matrix_len))
        if matrix_len != matrix_len_factor1 * matrix_len_factor1:
            matrix_len_factor1 = int(sqrt(2 * matrix_len))
        matrix_len_factor2 = matrix_len // matrix_len_factor1

        for i in range(1, matrix_len_factor1):
            rot_keys[i] = self.key_generator.generate_rot_key(i)

        for j in range(matrix_len_factor2):
            rot_keys[matrix_len_factor1 * j] = self.key_generator.generate_rot_key(matrix_len_factor1 * j)

        for i in range(matrix_len):
            rot_keys[i] = self.key_generator.generate_rot_key(i)

        ciph_prod = self.evaluator.multiply_matrix(ciph, mat, rot_keys, self.encoder)
        decrypted_prod = self.decryptor.decrypt(ciph_prod)
        decoded_prod = self.encoder.decode(decrypted_prod)

        check_complex_vector_approx_eq(matrix_prod_message, decoded_prod, error=0.01)

    def test_simple_rotate(self):
        vec = sample_random_complex_vector(self.degree // 2)
        rot = 1

        self.run_test_simple_rotate(vec, rot)

    def test_rotate_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        rot = 2

        self.run_test_rotate(vec, rot)

    def test_conjugate_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        self.run_test_conjugate(vec)

    def test_multiply_matrix_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        mat = [sample_random_complex_vector(self.degree // 2) for _ in range(self.degree // 2)]
        self.run_test_multiply_matrix(vec, mat)


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
