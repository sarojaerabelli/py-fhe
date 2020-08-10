"""A module to encode integers as plaintext polynomials by expressing them
in some base b.
"""
from util.plaintext import Plaintext
from util.polynomial import Polynomial

class IntegerEncoder:
    """An encoder for integers to polynomials in some base.

    We encode integers using a given base b. For example, for the base b = 2,
    we encode 6 = 1 * 2^2 + 1 * 2^1 as x^2 + x^1, and we decode
    f(x) = x^2 + x^1, by evaluating f(2) = 6.

    Attributes:
        base (int): Base to encode plaintext with.
        degree (int): Degree of polynomial that determines quotient ring.
    """

    def __init__(self, params, base=2):
        """Inits IntegerEncoder with the given parameters and base.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext modulus, and ciphertext modulus.
            base (int): Base to encode plaintext with.
        """
        self.base = base
        self.degree = params.poly_degree
        

    def encode(self, value):
        """Encodes an integer into a polynomial.

        Encodes an integer into a polynomial using the appropriate base.

        Args: 
            value (int): Integer to encode.

        Returns:
            A Plaintext object which represents the encoded value.
        """
        coeffs = [0] * self.degree
        i = 0
        while value > 0:
            coeffs[i] = value % self.base
            value //= self.base
            i += 1

        return Plaintext(Polynomial(self.degree, coeffs))

    def decode(self, plain):
        """Decodes a plaintext polynomial.

        Decodes a plaintext polynomial back to an integer.

        Args: 
            plain (Plaintext): Plaintext to decode.

        Returns:
            A decoded integer.
        """
        value = 0
        power = 1
        for c in plain.poly.coeffs:
            value += c * power
            power *= self.base
        return value
