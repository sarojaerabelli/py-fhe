"""Tests for evaluator.py."""

import os
import unittest

from bfv.bfv_decryptor import BFVDecryptor
from bfv.bfv_encryptor import BFVEncryptor
from bfv.bfv_evaluator import BFVEvaluator
from bfv.bfv_key_generator import BFVKeyGenerator
from bfv.bfv_parameters import BFVParameters
from util.plaintext import Plaintext
from util.polynomial import Polynomial
from util.random_sample import sample_uniform

TEST_DIRECTORY = os.path.dirname(__file__)

class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.degree = 512
        self.plain_modulus = 256
        self.ciph_modulus = 0x3fffffff000001
        params = BFVParameters(poly_degree=self.degree,
                               plain_modulus=self.plain_modulus,
                               ciph_modulus=self.ciph_modulus)
        key_generator = BFVKeyGenerator(params)
        public_key = key_generator.public_key
        secret_key = key_generator.secret_key
        self.relin_key = key_generator.relin_key
        self.encryptor = BFVEncryptor(params, public_key)
        self.decryptor = BFVDecryptor(params, secret_key)
        self.evaluator = BFVEvaluator(params)

    def run_test_add(self, message1, message2):
        poly1 = Polynomial(self.degree, message1)
        poly2 = Polynomial(self.degree, message2)
        plain1 = Plaintext(poly1)
        plain2 = Plaintext(poly2)
        plain_sum = Plaintext(poly1.add(poly2, self.plain_modulus))
        ciph1 = self.encryptor.encrypt(plain1)
        ciph2 = self.encryptor.encrypt(plain2)
        ciph_sum = self.evaluator.add(ciph1, ciph2)
        decrypted_sum = self.decryptor.decrypt(ciph_sum)
        self.assertEqual(str(plain_sum), str(decrypted_sum))

    def test_add_01(self):
        vec1 = sample_uniform(0, self.plain_modulus, self.degree)
        vec2 = sample_uniform(0, self.plain_modulus, self.degree)
        self.run_test_add(vec1, vec2)

    def run_test_multiply(self, message1, message2):
        poly1 = Polynomial(self.degree, message1)
        poly2 = Polynomial(self.degree, message2)
        plain1 = Plaintext(poly1)
        plain2 = Plaintext(poly2)
        plain_prod = Plaintext(poly1.multiply(poly2, self.plain_modulus))
        ciph1 = self.encryptor.encrypt(plain1)
        ciph2 = self.encryptor.encrypt(plain2)
        ciph_prod = self.evaluator.multiply(ciph1, ciph2, self.relin_key)
        decrypted_prod = self.decryptor.decrypt(ciph_prod)
        self.assertEqual(str(plain_prod), str(decrypted_prod))

    def test_multiply_01(self):
        vec1 = sample_uniform(0, self.plain_modulus, self.degree)
        vec2 = sample_uniform(0, self.plain_modulus, self.degree)
        self.run_test_multiply(vec1, vec2)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
