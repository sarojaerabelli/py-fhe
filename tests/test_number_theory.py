"""Tests for number_theory.py."""
import os
import unittest
from util import number_theory

TEST_DIRECTORY = os.path.dirname(__file__)


class TestNumberTheory(unittest.TestCase):
        
    def test_mod_exp(self):
        self.assertEqual(number_theory.mod_exp(12312, 53, 9393333), 2678490)
        self.assertEqual(number_theory.mod_exp(3880, 391, 9000), 1000)
        self.assertEqual(number_theory.mod_exp(-1, 432413, 88), 87)

    def test_mod_inv(self):
        self.assertEqual(number_theory.mod_inv(7, 19), 11)
        self.assertEqual(number_theory.mod_inv(43, 103), 12)
        self.assertEqual(number_theory.mod_inv(94, 97), 32)

    def test_find_generator(self):
        self.assertEqual(number_theory.find_generator(5), 2)
        self.assertEqual(number_theory.find_generator(7), 3)
        self.assertEqual(number_theory.find_generator(11), 2)

    def test_root_of_unity(self):
        self.assertEqual(number_theory.root_of_unity(order=2, modulus=5), 4)
        self.assertEqual(number_theory.root_of_unity(order=3, modulus=7), 2)
        self.assertEqual(number_theory.root_of_unity(order=5, modulus=11), 4)

    def test_is_prime(self):
        self.assertEqual(number_theory.is_prime(2), True)
        self.assertEqual(number_theory.is_prime(3), True)
        self.assertEqual(number_theory.is_prime(5), True)
        self.assertEqual(number_theory.is_prime(7), True)
        self.assertEqual(number_theory.is_prime(11), True)
        self.assertEqual(number_theory.is_prime(12), False)
        self.assertEqual(number_theory.is_prime(14), False)
        self.assertEqual(number_theory.is_prime(15), False)
        self.assertEqual(number_theory.is_prime(21), False)
        self.assertEqual(number_theory.is_prime(25), False)

        self.assertEqual(number_theory.is_prime(7919), True)
        self.assertEqual(number_theory.is_prime(7921), False)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
