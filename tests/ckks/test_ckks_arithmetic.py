"""Tests for ckks_evaluator.py for addition and multiplication."""

import os
import unittest

from ckks.ckks_decryptor import CKKSDecryptor
from ckks.ckks_encoder import CKKSEncoder
from ckks.ckks_encryptor import CKKSEncryptor
from ckks.ckks_evaluator import CKKSEvaluator
from ckks.ckks_key_generator import CKKSKeyGenerator
from ckks.ckks_parameters import CKKSParameters
from tests.helper import check_complex_vector_approx_eq
from util.polynomial import Polynomial
from util.random_sample import sample_random_complex_vector

TEST_DIRECTORY = os.path.dirname(__file__)

class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.degree = 16
        self.ciph_modulus = 1 << 600
        self.big_modulus = 1 << 1200
        self.scaling_factor = 1 << 30
        self.params = CKKSParameters(poly_degree=self.degree,
                                     ciph_modulus=self.ciph_modulus,
                                     big_modulus=self.big_modulus,
                                     scaling_factor=self.scaling_factor)
        self.key_generator = CKKSKeyGenerator(self.params)
        public_key = self.key_generator.public_key
        secret_key = self.key_generator.secret_key
        self.relin_key = self.key_generator.relin_key
        self.encoder = CKKSEncoder(self.params)
        self.encryptor = CKKSEncryptor(self.params, public_key, secret_key)
        self.decryptor = CKKSDecryptor(self.params, secret_key)
        self.evaluator = CKKSEvaluator(self.params)

    def run_test_add(self, message1, message2):
        poly1 = Polynomial(self.degree // 2, message1)
        poly2 = Polynomial(self.degree // 2, message2)
        plain1 = self.encoder.encode(message1, self.scaling_factor)
        plain2 = self.encoder.encode(message2, self.scaling_factor)
        plain_sum = poly1.add(poly2)
        ciph1 = self.encryptor.encrypt(plain1)
        ciph2 = self.encryptor.encrypt(plain2)
        ciph_sum = self.evaluator.add(ciph1, ciph2)
        decrypted_sum = self.decryptor.decrypt(ciph_sum)
        decoded_sum = self.encoder.decode(decrypted_sum)
        check_complex_vector_approx_eq(plain_sum.coeffs, decoded_sum, error=0.005)

    def run_test_subtract(self, message1, message2):
        poly1 = Polynomial(self.degree // 2, message1)
        poly2 = Polynomial(self.degree // 2, message2)
        plain1 = self.encoder.encode(message1, self.scaling_factor)
        plain2 = self.encoder.encode(message2, self.scaling_factor)
        plain_diff = poly1.subtract(poly2)
        ciph1 = self.encryptor.encrypt(plain1)
        ciph2 = self.encryptor.encrypt(plain2)
        ciph_diff = self.evaluator.subtract(ciph1, ciph2)
        decrypted_diff = self.decryptor.decrypt(ciph_diff)
        decoded_diff = self.encoder.decode(decrypted_diff)
        check_complex_vector_approx_eq(plain_diff.coeffs, decoded_diff, error=0.005)

    def run_test_secret_key_add(self, message1, message2):
        poly1 = Polynomial(self.degree // 2, message1)
        poly2 = Polynomial(self.degree // 2, message2)
        plain1 = self.encoder.encode(message1, self.scaling_factor)
        plain2 = self.encoder.encode(message2, self.scaling_factor)
        plain_sum = poly1.add(poly2)
        ciph1 = self.encryptor.encrypt_with_secret_key(plain1)
        ciph2 = self.encryptor.encrypt_with_secret_key(plain2)
        ciph_sum = self.evaluator.add(ciph1, ciph2)
        decrypted_sum = self.decryptor.decrypt(ciph_sum)
        decoded_sum = self.encoder.decode(decrypted_sum)
        check_complex_vector_approx_eq(plain_sum.coeffs, decoded_sum, error=0.001)

    def run_test_add_plain(self, message1, message2):
        plain1 = self.encoder.encode(message1, self.scaling_factor)
        plain2 = self.encoder.encode(message2, self.scaling_factor)
        plain_sum = [0] * (self.degree // 2)
        for i in range(self.degree // 2):
            plain_sum[i] = message1[i] + message2[i]

        ciph1 = self.encryptor.encrypt(plain1)

        ciph_sum = self.evaluator.add_plain(ciph1, plain2)
        decrypted_sum = self.decryptor.decrypt(ciph_sum)
        decoded_sum = self.encoder.decode(decrypted_sum)
        check_complex_vector_approx_eq(plain_sum, decoded_sum, error=0.001)

    def run_test_multiply(self, message1, message2):
        num_slots = len(message1)
        plain1 = self.encoder.encode(message1, self.scaling_factor)
        plain2 = self.encoder.encode(message2, self.scaling_factor)
        plain_prod = [0] * num_slots
        for i in range(num_slots):
            plain_prod[i] = message1[i] * message2[i]
        ciph1 = self.encryptor.encrypt(plain1)
        ciph2 = self.encryptor.encrypt(plain2)
        ciph_prod = self.evaluator.multiply(ciph1, ciph2, self.relin_key)
        decrypted_prod = self.decryptor.decrypt(ciph_prod)
        decoded_prod = self.encoder.decode(decrypted_prod)
        check_complex_vector_approx_eq(plain_prod, decoded_prod, error=0.01)

    def run_test_secret_key_multiply(self, message1, message2):
        num_slots = len(message1)
        plain1 = self.encoder.encode(message1, self.scaling_factor)
        plain2 = self.encoder.encode(message2, self.scaling_factor)
        plain_prod = [0] * num_slots
        for i in range(num_slots):
            plain_prod[i] = message1[i] * message2[i]
        ciph1 = self.encryptor.encrypt_with_secret_key(plain1)
        ciph2 = self.encryptor.encrypt_with_secret_key(plain2)
        ciph_prod = self.evaluator.multiply(ciph1, ciph2, self.relin_key)
        decrypted_prod = self.decryptor.decrypt(ciph_prod)
        decoded_prod = self.encoder.decode(decrypted_prod)
        check_complex_vector_approx_eq(plain_prod, decoded_prod, error=0.001)

    def run_test_multiply_plain(self, message1, message2):
        plain1 = self.encoder.encode(message1, self.scaling_factor)
        plain2 = self.encoder.encode(message2, self.scaling_factor)
        plain_prod = [0] * (self.degree // 2)
        for i in range(self.degree // 2):
            plain_prod[i] = message1[i] * message2[i]

        ciph1 = self.encryptor.encrypt(plain1)

        ciph_prod = self.evaluator.multiply_plain(ciph1, plain2)
        decrypted_prod = self.decryptor.decrypt(ciph_prod)
        decoded_prod = self.encoder.decode(decrypted_prod)
        check_complex_vector_approx_eq(plain_prod, decoded_prod, error=0.001)

    def test_add_01(self):
        vec1 = sample_random_complex_vector(self.degree // 2)
        vec2 = sample_random_complex_vector(self.degree // 2)
        self.run_test_add(vec1, vec2)

    def test_secret_key_add_01(self):
        vec1 = sample_random_complex_vector(self.degree // 2)
        vec2 = sample_random_complex_vector(self.degree // 2)
        self.run_test_secret_key_add(vec1, vec2)

    def test_subtract_01(self):
        vec1 = sample_random_complex_vector(self.degree // 2)
        vec2 = sample_random_complex_vector(self.degree // 2)
        self.run_test_subtract(vec1, vec2)

    def test_multiply_01(self):
        vec1 = sample_random_complex_vector(self.degree // 2)
        vec2 = sample_random_complex_vector(self.degree // 2)

        self.run_test_multiply(vec1, vec2)

    def test_secret_key_multiply_01(self):
        vec1 = sample_random_complex_vector(self.degree // 2)
        vec2 = sample_random_complex_vector(self.degree // 2)

        self.run_test_secret_key_multiply(vec1, vec2)

    def test_multiply_plain_01(self):
        vec1 = sample_random_complex_vector(self.degree // 2)
        vec2 = sample_random_complex_vector(self.degree // 2)
        self.run_test_multiply_plain(vec1, vec2)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
