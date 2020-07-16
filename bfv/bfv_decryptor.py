"""A module to decrypt for the BFV scheme."""

from util.plaintext import Plaintext

class BFVDecryptor:

    """An object that can decrypt data using BFV given a secret key.

    Attributes:
        poly_degree: Degree of polynomial in quotient ring.
        ciph_modulus: Coefficient modulus in ciphertext space.
        plain_modulus: Coefficient modulus in plaintext space.
        secret_key (SecretKey): Secret key used for encryption.
    """

    def __init__(self, params, secret_key):
        """Generates private/public key pair for BFV scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext modulus, and ciphertext modulus.
            secret_key (SecretKey): Secret key used for decryption.
        """
        self.poly_degree = params.poly_degree
        self.ciph_modulus = params.ciph_modulus
        self.plain_modulus = params.plain_modulus
        self.scaling_factor = params.scaling_factor
        self.secret_key = secret_key

    def decrypt(self, ciphertext, c2=None):
        """Decrypts a ciphertext.

        Decrypts the ciphertext and returns the corresponding plaintext.

        Args:
            ciphertext (Ciphertext): Ciphertext to be decrypted.

        Returns:
            The plaintext corresponding to the decrypted ciphertext.
        """
        (c0, c1) = (ciphertext.c0, ciphertext.c1)
        intermed_message = c0.add(c1.multiply(self.secret_key.s, self.ciph_modulus),
                                  self.ciph_modulus)
        if c2:
            secret_key_squared = self.secret_key.s.multiply(self.secret_key.s, self.ciph_modulus)
            intermed_message = intermed_message.add(c2.multiply(secret_key_squared, self.ciph_modulus), self.ciph_modulus)
        
        intermed_message = intermed_message.scalar_multiply(1 / self.scaling_factor)
        intermed_message = intermed_message.round()
        intermed_message = intermed_message.mod(self.plain_modulus)
        return Plaintext(intermed_message)
        