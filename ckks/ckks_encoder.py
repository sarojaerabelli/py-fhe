"""A module to encode integers as specified in the CKKS scheme.
"""

from math import floor
from util.ntt import FFTContext
from util.plaintext import Plaintext
from util.polynomial import Polynomial

class CKKSEncoder:
    """An encoder for several complex numbers as specified in the CKKS scheme.

    Attributes:
        degree (int): Degree of polynomial that determines quotient ring.
        fft (FFTContext): FFTContext object to encode/decode.
    """

    def __init__(self, params):
        """Inits CKKSEncoder with the given parameters.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext modulus, and ciphertext modulus.
        """
        self.degree = params.poly_degree
        self.fft = FFTContext(1 << 17)  

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

        # FFT inverse.
        to_scale = self.fft.emb_inv(values)
        
        # Multiply by scaling factor, and split up real and imaginary parts.
        message = [0] * plain_len
        for i in range(num_values):
            message[i] = int(to_scale[i].real * scaling_factor + 0.5)
            message[i + num_values] = int(to_scale[i].imag * scaling_factor + 0.5)

        return Plaintext(Polynomial(plain_len, message), scaling_factor)
        

    def decode(self, plain):
        """Decodes a plaintext polynomial.

        Decodes a plaintext polynomial back to a list of integers.

        Args: 
            plain (Plaintext): Plaintext to decode.

        Returns:
            A decoded list of integers.
        """
        if (not isinstance(plain, Plaintext)):
            raise ValueError("Input to decode must be a Plaintext")

        plain_len = len(plain.p.coeffs)
        num_values = plain_len >> 1

        # Divide by scaling factor, and turn back into a complex number.
        to_scale_down = [0] * num_values
        for i in range(num_values):
            to_scale_down[i] = complex(plain.p.coeffs[i] / plain.scaling_factor,
                                       plain.p.coeffs[i + num_values] / plain.scaling_factor)

        # Forward FFT.
        return self.fft.emb(to_scale_down)
