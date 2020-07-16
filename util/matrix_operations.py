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
    
    for i in range(len(mat)):
        for j in range(len(vec)):
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
    return [v * constant for v in vec]

def diagonal(mat, i):
    """Returns ith diagonal of matrix.

    Returns the ith diagonal (A_0i, A_1(i+1), ..., A_N(i-1)) of a matrix A.

    Args:
        mat (2-D list): Matrix.
        i (int): Index.

    Returns:
        Diagonal of a matrix.
    """
    N = len(mat)
    return [mat[j % N][(i + j) % N] for j in range(N)]

def rotate(vec, i):
    """Rotates vector to the left by i.

    Returns the rotated vector (v_i, v_(i+1), ..., v_(i-1)) of a vector v.

    Args:
        vec (list): Vector.
        i (int): Index.

    Returns:
        Rotated vector.
    """
    N = len(vec)
    return [vec[(j + i) % N] for j in range(N)]
