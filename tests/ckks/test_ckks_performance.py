"""Tests for ckks_evaluator.py for bootstrapping."""

import math
import cmath
import os
import time
import unittest

from ckks.ckks_decryptor import CKKSDecryptor
from ckks.ckks_encoder import CKKSEncoder
from ckks.ckks_encryptor import CKKSEncryptor
from ckks.ckks_evaluator import CKKSEvaluator
from ckks.ckks_key_generator import CKKSKeyGenerator
from ckks.ckks_parameters import CKKSParameters
from tests.helper import check_complex_vector_approx_eq
from util.plaintext import Plaintext
import util.matrix_operations as mat
from util.random_sample import sample_random_complex_vector

TEST_DIRECTORY = os.path.dirname(__file__)

class TestBootstrapping(unittest.TestCase):

    def setUp(self):
        self.degree = 16
        self.ciph_modulus = 1 << 40
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

    def run_test_bootstrap(self, message):
        num_slots = len(message)
        plain = self.encoder.encode(message, self.scaling_factor)
        ciph = self.encryptor.encrypt(plain)

        rot_keys = {}
        for i in range(num_slots):
            rot_keys[i] = self.key_generator.generate_rot_key(i)

        conj_key = self.key_generator.generate_conj_key()

        start_time = time.clock()
        ciph, new_ciph = self.evaluator.bootstrap(ciph, rot_keys, conj_key, self.relin_key,
                                                  self.encoder)
        total_time = time.clock() - start_time
        new_plain = self.decryptor.decrypt(new_ciph)
        new_plain = self.encoder.decode(new_plain)
        check_complex_vector_approx_eq(message, new_plain, error=0.05)
        return total_time

    def test_bootstrap_time(self):
        num_iterations = 1
        print("Number of bootstraps: %d" % (num_iterations))
        total_time = 0

        for _ in range(num_iterations):
            vec = sample_random_complex_vector(self.degree // 2)
            total_time += self.run_test_bootstrap(vec)

        print("Average time per bootstrap operation: %f seconds" % (total_time / num_iterations))

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
