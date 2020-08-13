"""Tests for encryptor.py and decryptor.py.

Tests that encrypting and decrypting several plaintexts
gives back the same plaintext.
"""

import os
import unittest
from bfv.bfv_decryptor import BFVDecryptor
from bfv.bfv_encryptor import BFVEncryptor
from bfv.bfv_key_generator import BFVKeyGenerator
from bfv.bfv_parameters import BFVParameters
from util.plaintext import Plaintext
from util.polynomial import Polynomial
from util.random_sample import sample_uniform

TEST_DIRECTORY = os.path.dirname(__file__)


class TestEncryptDecrypt(unittest.TestCase):
    def setUp(self):
        self.small_degree = 5
        self.small_plain_modulus = 60
        self.small_ciph_modulus = 50000
        self.large_degree = 2048
        self.large_plain_modulus = 256
        self.large_ciph_modulus = 0x3fffffff000001

    def run_test_tiny_encrypt_decrypt(self, message):
        params = BFVParameters(poly_degree=self.small_degree,
                               plain_modulus=self.small_plain_modulus,
                               ciph_modulus=self.small_ciph_modulus)
        key_generator = BFVKeyGenerator(params)
        public_key = key_generator.public_key
        secret_key = key_generator.secret_key
        encryptor = BFVEncryptor(params, public_key)
        decryptor = BFVDecryptor(params, secret_key)
        message = Plaintext(Polynomial(self.small_degree, message))
        ciphertext = encryptor.encrypt(message)
        decrypted_message = decryptor.decrypt(ciphertext)
        self.assertEqual(str(message), str(decrypted_message))

    def run_test_large_encrypt_decrypt(self, message):
        params = BFVParameters(poly_degree=self.large_degree,
                               plain_modulus=self.large_plain_modulus,
                               ciph_modulus=self.large_ciph_modulus)
        key_generator = BFVKeyGenerator(params)
        public_key = key_generator.public_key
        secret_key = key_generator.secret_key
        encryptor = BFVEncryptor(params, public_key)
        decryptor = BFVDecryptor(params, secret_key)
        message = Plaintext(Polynomial(self.large_degree, message))
        ciphertext = encryptor.encrypt(message)
        decrypted_message = decryptor.decrypt(ciphertext)
        self.assertEqual(str(message), str(decrypted_message))

    def test_tiny_encrypt_decrypt_01(self):
        self.run_test_tiny_encrypt_decrypt([0, 23, 48, 52, 6])

    def test_tiny_encrypt_decrypt_02(self):
        self.run_test_tiny_encrypt_decrypt([19, 7, 42, 1, 54])

    def test_tiny_encrypt_decrypt_03(self):
        self.run_test_tiny_encrypt_decrypt([33, 20, 4, 2, 59])

    def test_tiny_encrypt_decrypt_04(self):
        self.run_test_tiny_encrypt_decrypt([9, 18, 47, 50, 30])

    def test_large_encrypt_decrypt_01(self):
        vec = sample_uniform(0, self.large_plain_modulus, self.large_degree)
        self.run_test_large_encrypt_decrypt(vec)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
