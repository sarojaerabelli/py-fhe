"""A module to encrypt for the CKKS scheme."""

from util.ciphertext import Ciphertext
from util.polynomial import Polynomial
from util.random_sample import sample_triangle

class CKKSEncryptor:

    """An object that can encrypt data using CKKS given a public key.

    Attributes:
        poly_degree: Degree of polynomial in quotient ring.
        coeff_modulus: Coefficient modulus in ciphertext space.
        big_modulus: Bootstrapping modulus.
        crt_context: CRT context for multiplication.
        public_key (PublicKey): Public key used for encryption.
        secret_key (SecretKey): Only used for secret key encryption.
    """

    def __init__(self, params, public_key, secret_key=None):
        """Generates private/public key pair for CKKS scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                ciphertext modulus, etc.
            public_key (PublicKey): Public key used for encryption.
            secret_key (SecretKey): Optionally passed for secret key encryption.
        """
        self.poly_degree = params.poly_degree
        self.coeff_modulus = params.ciph_modulus
        self.big_modulus = params.big_modulus
        self.crt_context = params.crt_context
        self.public_key = public_key
        self.secret_key = secret_key

    def encrypt_with_secret_key(self, plain):
        """Encrypts a message with secret key encryption.

        Encrypts the message for secret key encryption and returns the corresponding ciphertext.

        Args:
            plain (Plaintext): Plaintext to be encrypted.

        Returns:
            A ciphertext consisting of a pair of polynomials in the ciphertext
            space.
        """
        assert self.secret_key != None, 'Secret key does not exist'

        sk = self.secret_key.s
        random_vec = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))
        error = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))

        c0 = sk.multiply(random_vec, self.coeff_modulus, crt=self.crt_context)
        c0 = error.add(c0, self.coeff_modulus)
        c0 = c0.add(plain.poly, self.coeff_modulus)
        c0 = c0.mod_small(self.coeff_modulus)

        c1 = random_vec.scalar_multiply(-1, self.coeff_modulus)
        c1 = c1.mod_small(self.coeff_modulus)

        return Ciphertext(c0, c1, plain.scaling_factor, self.coeff_modulus)

    def encrypt(self, plain):
        """Encrypts a message.

        Encrypts the message and returns the corresponding ciphertext.

        Args:
            plain (Plaintext): Plaintext to be encrypted.

        Returns:
            A ciphertext consisting of a pair of polynomials in the ciphertext
            space.
        """
        p0 = self.public_key.p0
        p1 = self.public_key.p1
        
        random_vec = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))
        error1 = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))
        error2 = Polynomial(self.poly_degree, sample_triangle(self.poly_degree))

        c0 = p0.multiply(random_vec, self.coeff_modulus, crt=self.crt_context)
        c0 = error1.add(c0, self.coeff_modulus)
        c0 = c0.add(plain.poly, self.coeff_modulus)
        c0 = c0.mod_small(self.coeff_modulus)

        c1 = p1.multiply(random_vec, self.coeff_modulus, crt=self.crt_context)
        c1 = error2.add(c1, self.coeff_modulus)
        c1 = c1.mod_small(self.coeff_modulus)

        return Ciphertext(c0, c1, plain.scaling_factor, self.coeff_modulus)

    def raise_modulus(self, new_modulus):
        """Rescales scheme to have a new modulus.

        Raises ciphertext modulus.

        Args:
            new_modulus (int): New modulus.
        """
        self.coeff_modulus = new_modulus
        