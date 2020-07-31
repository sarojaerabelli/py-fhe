"""A module to decrypt for the CKKS scheme."""

from util.plaintext import Plaintext

class CKKSDecryptor:

    """An object that can decrypt data using CKKS given a secret key.

    Attributes:
        poly_degree: Degree of polynomial in quotient ring.
        crt_context: CRT context for multiplication.
        secret_key (SecretKey): Secret key used for encryption.
    """

    def __init__(self, params, secret_key):
        """Initializes decryptor for CKKS scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext modulus, and ciphertext modulus.
            secret_key (SecretKey): Secret key used for decryption.
        """
        self.poly_degree = params.poly_degree
        self.crt_context = params.crt_context
        self.secret_key = secret_key

    def decrypt(self, ciphertext, c2=None):
        """Decrypts a ciphertext.

        Decrypts the ciphertext and returns the corresponding plaintext.

        Args:
            ciphertext (Ciphertext): Ciphertext to be decrypted.
            c2 (Polynomial): Optional additional parameter for a ciphertext that
                has not been relinearized.

        Returns:
            The plaintext corresponding to the decrypted ciphertext.
        """
        (c0, c1) = (ciphertext.c0, ciphertext.c1)

        message = c1.multiply(self.secret_key.s, ciphertext.modulus, crt=self.crt_context)
        message = c0.add(message, ciphertext.modulus)
        if c2:
            secret_key_squared = self.secret_key.s.multiply(self.secret_key.s, ciphertext.modulus)
            c2_message = c2.multiply(secret_key_squared, ciphertext.modulus, crt=self.crt_context)
            message = message.add(c2_message, ciphertext.modulus)

        message = message.mod_small(ciphertext.modulus)
        return Plaintext(message, ciphertext.scaling_factor)
        