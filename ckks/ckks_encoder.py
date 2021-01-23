"""A module to encode integers as specified in the CKKS scheme.
"""

from util.dcrt_polynomial import DCRTPolynomial
from util.ntt import FFTContext
from util.plaintext import Plaintext
from util.polynomial import Polynomial

class CKKSEncoder:
    """An encoder for several complex numbers as specified in the CKKS scheme.

    Attributes:
        params (CKKSParameters): Parameters.
        degree (int): Degree of polynomial that determines quotient ring.
        fft (FFTContext): FFTContext object to encode/decode.
    """

    def __init__(self, params):
        """Inits CKKSEncoder with the given parameters.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext modulus, and ciphertext modulus.
        """
        self.params = params
        self.degree = params.poly_degree
        self.fft = FFTContext(self.degree * 2)

    def encode(self, values, scaling_factor):
        """Encodes complex numbers into a polynomial.

        Encodes an array of complex number into a polynomial.

        Args:
            values (list): List of complex numbers to encode.
            scaling_factor (float): Scaling factor to multiply by.

        Returns:
            A Plaintext object which represents the encoded value.
        """
        num_values = len(values)
        plain_len = num_values << 1

        # Canonical embedding inverse variant.
        to_scale = self.fft.embedding_inv(values)

        # Multiply by scaling factor, and split up real and imaginary parts.
        message = [0] * plain_len
        for i in range(num_values):
            message[i] = int(to_scale[i].real * scaling_factor + 0.5)
            message[i + num_values] = int(to_scale[i].imag * scaling_factor + 0.5)

        if self.params.rns:
            return Plaintext(DCRTPolynomial(plain_len, message, self.params.crt_context),
                             scaling_factor)
        return Plaintext(Polynomial(plain_len, message), scaling_factor)


    def decode(self, plain):
        """Decodes a plaintext polynomial.

        Decodes a plaintext polynomial back to a list of integers.

        Args:
            plain (Plaintext): Plaintext to decode.

        Returns:
            A decoded list of integers.
        """
        if not isinstance(plain, Plaintext):
            raise ValueError("Input to decode must be a Plaintext")

        if self.params.rns:
            plain.poly = plain.poly.reconstruct()

        plain_len = len(plain.poly.coeffs)
        num_values = plain_len >> 1

        # Divide by scaling factor, and turn back into a complex number.
        message = [0] * num_values
        for i in range(num_values):
            if i == 0:
                print(" i: %i\n plain.poly.coeffs[i]: %i\n plain.poly.coeffs[i + num_values]: %i\n plain.scaling_factor: %i" % (i, plain.poly.coeffs[i], plain.poly.coeffs[i + num_values], plain.scaling_factor))
            try:
                message[i] = complex(plain.poly.coeffs[i] / plain.scaling_factor,
                                     plain.poly.coeffs[i + num_values] / plain.scaling_factor)
            except:
                print(" i: %i\n plain.poly.coeffs[i]: %i\n plain.poly.coeffs[i + num_values]: %i\n plain.scaling_factor: %i" % (i, plain.poly.coeffs[i], plain.poly.coeffs[i + num_values], plain.scaling_factor))
                message[i] = complex(plain.poly.coeffs[i] / plain.scaling_factor,
                                     plain.poly.coeffs[i + num_values] / plain.scaling_factor)

        # Compute canonical embedding variant.
        return self.fft.embedding(message)
