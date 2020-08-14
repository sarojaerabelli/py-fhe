"""Time how long multiplication for BFV takes.

Need to run test with a command line argument for the polynomial degree.
For multiplication with polynomial degree 16, run
python3 run_bfv_performance.py TestMultiply 16"""

import os
import sys
import time
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
arg = None

class TestMultiply(unittest.TestCase):
    def setUp(self):
        self.degree = int(arg)
        self.plain_modulus = 256
        self.ciph_modulus = 0x3fffffff000001
        self.params = BFVParameters(poly_degree=self.degree,
                                    plain_modulus=self.plain_modulus,
                                    ciph_modulus=self.ciph_modulus)
        key_generator = BFVKeyGenerator(self.params)
        public_key = key_generator.public_key
        secret_key = key_generator.secret_key
        self.relin_key = key_generator.relin_key
        self.encryptor = BFVEncryptor(self.params, public_key)
        self.decryptor = BFVDecryptor(self.params, secret_key)
        self.evaluator = BFVEvaluator(self.params)

    def run_test_multiply(self, message1, message2):
        poly1 = Polynomial(self.degree, message1)
        poly2 = Polynomial(self.degree, message2)
        plain1 = Plaintext(poly1)
        plain2 = Plaintext(poly2)
        plain_prod = Plaintext(poly1.multiply(poly2, self.plain_modulus))
        ciph1 = self.encryptor.encrypt(plain1)
        ciph2 = self.encryptor.encrypt(plain2)
        start_time = time.clock()
        ciph_prod = self.evaluator.multiply(ciph1, ciph2, self.relin_key)
        total_time = time.clock() - start_time
        decrypted_prod = self.decryptor.decrypt(ciph_prod)
        self.assertEqual(str(plain_prod), str(decrypted_prod))
        return total_time

    def test_multiply_time(self):
        self.params.print_parameters()
        num_iterations = 1
        print("Number of multiplications: %d" % (num_iterations))
        total_time = 0

        for _ in range(num_iterations):
            vec1 = sample_uniform(0, self.plain_modulus, self.degree)
            vec2 = sample_uniform(0, self.plain_modulus, self.degree)
            total_time += self.run_test_multiply(vec1, vec2)

        print("Average time per multiply operation: %f seconds" % (total_time / num_iterations))

if __name__ == '__main__':
    arg = sys.argv[2]
    sys.argv = sys.argv[:2]
    res = unittest.main(verbosity=3, exit=False)
