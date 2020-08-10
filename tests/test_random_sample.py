"""Tests for random_sample.py."""
import os
import unittest
from util import random_sample

TEST_DIRECTORY = os.path.dirname(__file__)


class TestRandomSample(unittest.TestCase):
        
    def test_sample_hamming_weight_vector(self):
        hamming_weight = 64
        length = 128
        vector = random_sample.sample_hamming_weight_vector(length, hamming_weight)
        self.assertEqual(vector.count(0), length - hamming_weight)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
