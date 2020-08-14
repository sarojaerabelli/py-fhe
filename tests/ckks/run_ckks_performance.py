"""Time how long multiplication and bootstrapping take.

Need to run test with a command line argument with for the polynomial degree.
For multiplication with polynomial degree 16, run
python3 run_ckks_performance.py TestMultiply 16
For bootstrapping with polynomial degree 32, run
python3 run_ckks_performance.py TestBootstrapping 32"""

import os
import sys
import time
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
arg = None

class TestMultiply(unittest.TestCase):
    def setUp(self):
        self.degree = int(arg)
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

    def run_test_multiply(self, message1, message2):
        num_slots = len(message1)
        plain1 = self.encoder.encode(message1, self.scaling_factor)
        plain2 = self.encoder.encode(message2, self.scaling_factor)
        plain_prod = [0] * num_slots
        for i in range(num_slots):
            plain_prod[i] = message1[i] * message2[i]
        ciph1 = self.encryptor.encrypt(plain1)
        ciph2 = self.encryptor.encrypt(plain2)
        start_time = time.clock()
        ciph_prod = self.evaluator.multiply(ciph1, ciph2, self.relin_key)
        total_time = time.clock() - start_time
        decrypted_prod = self.decryptor.decrypt(ciph_prod)
        decoded_prod = self.encoder.decode(decrypted_prod)
        check_complex_vector_approx_eq(plain_prod, decoded_prod, error=0.01)
        return total_time

    def test_multiply_time(self):
        self.params.print_parameters()
        num_iterations = 1
        print("Number of multiplications: %d" % (num_iterations))
        total_time = 0

        for _ in range(num_iterations):
            vec1 = sample_random_complex_vector(self.degree // 2)
            vec2 = sample_random_complex_vector(self.degree // 2)
            total_time += self.run_test_multiply(vec1, vec2)

        print("Average time per multiply operation: %f seconds" % (total_time / num_iterations))

class TestBootstrapping(unittest.TestCase):

    def setUp(self):
        self.degree = int(arg)
        self.ciph_modulus = 1 << 40
        self.big_modulus = 1 << 1200
        self.scaling_factor = 1 << 30

        self.params = CKKSParameters(poly_degree=self.degree,
                                     ciph_modulus=self.ciph_modulus,
                                     big_modulus=self.big_modulus,
                                     scaling_factor=self.scaling_factor,
                                     taylor_iterations=7,
                                     prime_size=None)
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
        self.params.print_parameters()
        num_iterations = 1
        print("Number of bootstraps: %d" % (num_iterations))
        total_time = 0

        for _ in range(num_iterations):
            vec = sample_random_complex_vector(self.degree // 2)
            total_time += self.run_test_bootstrap(vec)

        print("Average time per bootstrap operation: %f seconds" % (total_time / num_iterations))

if __name__ == '__main__':
    arg = sys.argv[2]
    sys.argv = sys.argv[:2]
    res = unittest.main(verbosity=3, exit=False)
