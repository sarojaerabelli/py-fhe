"""Tests for ckks_encryptor.py and ckks_decryptor.py.

Tests that encrypting a plaintext and decrypting it
gives back the same plaintext.
"""

import os
import unittest
from ckks.ckks_encoder import CKKSEncoder
from ckks.ckks_decryptor import CKKSDecryptor
from ckks.ckks_encryptor import CKKSEncryptor
from ckks.ckks_key_generator import CKKSKeyGenerator
from ckks.ckks_parameters import CKKSParameters
from tests.helper import check_complex_vector_approx_eq
from util.plaintext import Plaintext
from util.polynomial import Polynomial
from util.random_sample import sample_random_complex_vector

TEST_DIRECTORY = os.path.dirname(__file__)

class TestEncryptDecrypt(unittest.TestCase):
    def setUp(self):
        self.degree = 64
        self.ciph_modulus = 1 << 1200
        self.big_modulus = 1 << 1200
        self.scaling_factor = 1 << 30
        self.params = CKKSParameters(poly_degree=self.degree,
                                     ciph_modulus=self.ciph_modulus,
                                     big_modulus=self.big_modulus,
                                     scaling_factor=self.scaling_factor)
        key_generator = CKKSKeyGenerator(self.params)
        public_key = key_generator.public_key
        secret_key = key_generator.secret_key
        self.encoder = CKKSEncoder(self.params)
        self.encryptor = CKKSEncryptor(self.params, public_key, secret_key)
        self.decryptor = CKKSDecryptor(self.params, secret_key)

    def run_test_encrypt_decrypt(self, message):
        plain = self.encoder.encode(message, self.scaling_factor)

        ciphertext = self.encryptor.encrypt(plain)
        decrypted = self.decryptor.decrypt(ciphertext)
        decoded = self.encoder.decode(decrypted)

        check_complex_vector_approx_eq(message, decoded, 0.001)

    def run_test_secret_key_encrypt_decrypt(self, message):
        plain = self.encoder.encode(message, self.scaling_factor)

        ciphertext = self.encryptor.encrypt_with_secret_key(plain)
        decrypted = self.decryptor.decrypt(ciphertext)
        decoded = self.encoder.decode(decrypted)

        check_complex_vector_approx_eq(message, decoded, 0.001)

    def test_encrypt_decrypt_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        self.run_test_encrypt_decrypt(vec)

    def test_secret_key_encrypt_decrypt_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        self.run_test_secret_key_encrypt_decrypt(vec)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
