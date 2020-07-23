"""Tests for matrix_operations.py."""
import os
import unittest
from util import matrix_operations

TEST_DIRECTORY = os.path.dirname(__file__)


class TestMatrixOperations(unittest.TestCase):
        
    def test_matrix_vector_multiply(self):
        mat = [[0, 1, 2], [1, 4, 10], [-5, 6, 10]]
        vec = [3, 8, 9]

        prod = matrix_operations.matrix_vector_multiply(mat, vec)
        self.assertEqual(prod, [26, 125, 123])

    def test_add(self):
        vec1 = [1, 23, 4, 5, 644]
        vec2 = [0, 459, -4, 111, 4]

        s = matrix_operations.add(vec1, vec2)
        self.assertEqual(s, [1, 482, 0, 116, 648])

    def test_scalar_multiply(self):
        vec = [1, 3, 5, 6, 6]
        scal = 4

        prod = matrix_operations.scalar_multiply(vec, scal)
        self.assertEqual(prod, [4, 12, 20, 24, 24])

    def test_diagonal(self):
        mat = [[0, 1, 2], [1, 4, 10], [-5, 6, 10]]
        diag0 = matrix_operations.diagonal(mat, 0)
        diag1 = matrix_operations.diagonal(mat, 1)
        diag2 = matrix_operations.diagonal(mat, 2)

        self.assertEqual(diag0, [0, 4, 10])
        self.assertEqual(diag1, [1, 10, -5])
        self.assertEqual(diag2, [2, 1, 6])

    def test_rotate(self):
        vec = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        rot = matrix_operations.rotate(vec, 3)
        self.assertEqual(rot, [3, 4, 5, 6, 7, 8, 0, 1, 2])

    def test_conjugate_matrix(self):
        mat = [[1j, 1 + 2j, 2 + 3j], [1, 4 - 4j, 10 - 1j], [-5, 6 + 4j, 10 - 2j]]
        conjugated_mat = matrix_operations.conjugate_matrix(mat)
        self.assertEqual(conjugated_mat, [[-1j, 1 - 2j, 2 - 3j], [1, 4 + 4j, 10 + 1j], [-5, 6 - 4j, 10 + 2j]])

    def test_transpose_matrix(self):
        mat = [[0, 1, 2], [1, 4, 10]]
        transpose = matrix_operations.transpose_matrix(mat)
        self.assertEqual(transpose, [[0, 1], [1, 4], [2, 10]])

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
