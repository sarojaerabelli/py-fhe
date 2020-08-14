"""A module to encode integers as plaintext polynomials by using
Chinese Remainder Theorem (CRT) batching.
"""

from util.ntt import NTTContext
from util.plaintext import Plaintext
from util.polynomial import Polynomial

class BatchEncoder:
    """An encoder for several integers to polynomials using Chinese
    Remainder Theorem (CRT) batching.

    We encode N integers using CRT batching, where N is the degree of the
    polynomial that determines the quotient ring. Each polynomial p(x) in
    the ring Z[x]/f(x), where f(x) = x^N + 1 maps to the N-length vector
    [p(a_0), p(a_1), ..., p(a_N)] where a_i are the roots of f(x). This
    uniquely identifies a polynomial in the quotient ring, so we use it
    to define our encoding, where each of these N-length vectors encodes to
    its unique corresponding polynomial in the quotient ring. However, we
    instead use the Fermat Theoretic Transform to obtain a slightly
    modified N-length vector in faster time.

    Attributes:
        degree (int): Degree of polynomial that determines quotient ring.
        ntt (NTTContext): NTTContext object to encode/decode.
    """

    def __init__(self, params):
        """Inits BatchEncoder with the given parameters.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext modulus, and ciphertext modulus.
        """
        self.degree = params.poly_degree
        self.plain_modulus = params.plain_modulus
        self.ntt = NTTContext(params.poly_degree, params.plain_modulus)  

    def encode(self, values):
        """Encodes a list of integers into a polynomial.

        Encodes a N-length list of integers (where N is the polynomial degree)
        into a polynomial using CRT batching.

        Args: 
            values (list): Integers to encode.

        Returns:
            A Plaintext object which represents the encoded value.
        """
        assert len(values) == self.degree, 'Length of list does not equal \
            polynomial degree.'
        coeffs = self.ntt.ftt_inv(values)
        return Plaintext(Polynomial(self.degree, coeffs))

    def decode(self, plain):
        """Decodes a plaintext polynomial.

        Decodes a plaintext polynomial back to a list of integers.

        Args: 
            plain (Plaintext): Plaintext to decode.

        Returns:
            A decoded list of integers.
        """
        result = self.ntt.ftt_fwd(plain.poly.coeffs)
        return [val % self.plain_modulus for val in result]
