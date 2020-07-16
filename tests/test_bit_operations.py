"""Tests for bit_operations.py."""
import os
import unittest
from util import bit_operations

TEST_DIRECTORY = os.path.dirname(__file__)


class TestBitOperations(unittest.TestCase):
        
    def test_reverse_bits(self):
        self.assertEqual(bit_operations.reverse_bits(value=6, width=5), 12)
        self.assertEqual(bit_operations.reverse_bits(value=19, width=8), 200)
        self.assertEqual(bit_operations.reverse_bits(value=189, width=8), 189)

    def test_bit_reverse_vec(self):
        self.assertEqual(bit_operations.bit_reverse_vec([0, 1, 2, 3]), [0, 2, 1, 3])
        self.assertEqual(bit_operations.bit_reverse_vec([0, 1, 2, 3, 4, 5, 6, 7]), [0, 4, 2, 6, 1, 5, 3, 7])
        self.assertEqual(bit_operations.bit_reverse_vec([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
            [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15])

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
