"""A helper module for test functions.
"""

def check_complex_vector_approx_eq(vec1, vec2, error=0.00001,
                                   error_message="Error: vectors are not approximately equal."):
    """Checks whether two vectors are approximately equal.

    Checks that each entry of two vectors of complex numbers are within the given error.

    Args:
        vec1 (list (complex)): Vector 1.
        vec2 (list (complex)): Vector 2.
        error (float): How close each entry of the two vectors must be to be approximately equal.
        error_message (String): Message to output if not equal.

    Returns:
        A Ciphertext which encrypts the same message under a different key.
    """

    assert(len(vec1) == len(vec2)), 'Length of v1 = %d, Length of v2 = %d' % (len(vec1), len(vec2))
    for i in range(len(vec1)):
        if (abs(vec1[i].real - vec2[i].real) > error) or (abs(vec1[i].imag - vec2[i].imag) > error):
            print("-------- VALUES DO NOT MATCH AT INDEX %d --------" % (i))
            print(str(vec1[i]) + " != " + str(vec2[i]))
            print("v1: " + str(vec1[:10]))
            print("v2: " + str(vec2[:10]))
            raise ValueError(error_message)
