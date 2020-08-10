"""A module to encrypt for the BFV scheme."""

from util.ciphertext import Ciphertext
from util.polynomial import Polynomial
from util.random_sample import sample_triangle

class BFVEncryptor:

    """An object that can encrypt data using BFV given a public key.

    Attributes:
        poly_degree: Degree of polynomial in quotient ring.
        coeff_modulus: Coefficient modulus in ciphertext space.
        public_key (PublicKey): Public key used for encryption.
        delta (int): Floor of ciphertext modulus divided by plaintext modulus.
    """

    def __init__(self, params, public_key):
        """Generates private/public key pair for BFV scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext modulus, and ciphertext modulus.
            public_key (PublicKey): Public key used for encryption.
        """
        self.poly_degree = params.poly_degree
        self.coeff_modulus = params.ciph_modulus
        self.public_key = public_key
        self.scaling_factor = int(params.scaling_factor)

    def encrypt(self, message):
        """Encrypts a message.

        Encrypts the message and returns the corresponding ciphertext.

        Args:
            message (Plaintext): Plaintext to be encrypted.

        Returns:
            A ciphertext consisting of a pair of polynomials in the ciphertext
            space.
        """
        p0 = self.public_key.p0
        p1 = self.public_key.p1
        scaled_message = message.poly.scalar_multiply(self.scaling_factor, self.coeff_modulus)

        random_vec = Polynomial(self.poly_degree,
                                sample_triangle(self.poly_degree))
        error1 = Polynomial(self.poly_degree,
                            sample_triangle(self.poly_degree))
        error1 = Polynomial(self.poly_degree,
                            [0] * self.poly_degree)
        error2 = Polynomial(self.poly_degree,
                            sample_triangle(self.poly_degree))
        error2 = Polynomial(self.poly_degree,
                            [0] * self.poly_degree)
        c0 = error1.add(p0.multiply(random_vec, self.coeff_modulus),
                        self.coeff_modulus).add(scaled_message, self.coeff_modulus)
        c1 = error2.add(p1.multiply(random_vec, self.coeff_modulus), self.coeff_modulus)

        return Ciphertext(c0, c1)
        