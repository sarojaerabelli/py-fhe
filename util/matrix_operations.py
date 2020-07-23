"""A module to perform matrix operations.
"""
from math import log

def matrix_vector_multiply(mat, vec):
    """Multiplies a matrix by a vector.

    Multiplies an m x n matrix by an n x 1 vector (represented
    as a list).

    Args:
        mat (2-D list): Matrix to multiply.
        vec (list): Vector to multiply.

    Returns:
        Product of mat and vec (an m x 1 vector) as a list
    """
    prod = [0] * len(mat)

    for i, row in enumerate(mat):
        for j in range(len(row)):
            prod[i] += mat[i][j] * vec[j]

    return prod

def add(vec1, vec2):
    """Adds two vectors.

    Adds a length-n list to another length-n list.

    Args:
        vec1 (list): First vector.
        vec2 (list): Second vector.

    Returns:
        Sum of vec1 and vec2.
    """
    assert len(vec1) == len(vec2)
    return [vec1[i] + vec2[i] for i in range(len(vec1))]

def scalar_multiply(vec, constant):
    """Multiplies a scalar by a vector.

    Multiplies a vector by a scalar.

    Args:
        vec (list): Vector to multiply.
        constant (float): Scalar to multiply.

    Returns:
        Product of vec and constant.
    """
    return [val * constant for val in vec]

def diagonal(mat, diag_index):
    """Returns ith diagonal of matrix, where i is the diag_index.

    Returns the ith diagonal (A_0i, A_1(i+1), ..., A_N(i-1)) of a matrix A,
    where i is the diag_index.

    Args:
        mat (2-D list): Matrix.
        diag_index (int): Index of diagonal to return.

    Returns:
        Diagonal of a matrix.
    """
    return [mat[j % len(mat)][(diag_index + j) % len(mat)] for j in range(len(mat))]

def rotate(vec, rotation):
    """Rotates vector to the left by rotation.

    Returns the rotated vector (v_i, v_(i+1), ..., v_(i-1)) of a vector v, where i is the rotation.

    Args:
        vec (list): Vector.
        rotation (int): Index.

    Returns:
        Rotated vector.
    """
    return [vec[(j + rotation) % len(vec)] for j in range(len(vec))]

def conjugate_matrix(matrix):
    """Conjugates all entries of matrix.

    Returns the conjugated matrix.

    Args:
        matrix (2-D list): Matrix.

    Returns:
        Conjugated matrix.
    """
    conj_matrix = [[0] * len(matrix[i]) for i in range(len(matrix))]
    for i, row in enumerate(matrix):
        for j in range(len(row)):
            conj_matrix[i][j] = matrix[i][j].conjugate()

    return conj_matrix

def transpose_matrix(matrix):
    """Transposes a matrix.

    Returns the transposed matrix.

    Args:
        matrix (2-D list): Matrix.

    Returns:
        Transposed matrix.
    """
    transpose = [[0] * len(matrix) for _ in range(len(matrix[0]))]
    for i, row in enumerate(matrix):
        for j in range(len(row)):
            transpose[j][i] = matrix[i][j]

    return transpose
