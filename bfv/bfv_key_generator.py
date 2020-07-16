"""A module to generate public and private keys for the BFV scheme."""

from math import ceil, floor, log, sqrt
from util.polynomial import Polynomial
from util.public_key import PublicKey
from bfv.bfv_relin_key import BFVRelinKey
from util.secret_key import SecretKey
from util.random_sample import sample_triangle, sample_uniform

class BFVKeyGenerator:

    """An instance to generate a public/secret key pair and relinearization keys.

    The secret key s is generated randomly, and the public key is the
    pair (-(as + e), a). The relinearization keys are generated, as
    specified in the BFV paper.

    Attributes:
        secret_key (Polynomial): secret key randomly generated from R_q.
        public_key (tuple of Polynomials): public key generated from
            secret key.
        relin_key (tuple of Polynomials): relinearization key generated
            from secret key.
    """

    def __init__(self, params):
        """Generates secret/public key pair for BFV scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext, and ciphertext modulus.
        """
        self.generate_secret_key(params)
        self.generate_public_key(params)
        self.generate_relin_key(params)

    def generate_secret_key(self, params):
        """Generates a secret key for BFV scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext, and ciphertext modulus.
        """
        self.secret_key = SecretKey(Polynomial(params.poly_degree,
                                               sample_triangle(params.poly_degree)))

    def generate_public_key(self, params):
        """Generates a public key for BFV scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext, and ciphertext modulus.
        """
        pk_coeff = Polynomial(params.poly_degree,
                              sample_uniform(0, params.ciph_modulus, params.poly_degree))
        pk_error = Polynomial(params.poly_degree,
                              sample_triangle(params.poly_degree))
        p0 = pk_error.add(pk_coeff.multiply(
            self.secret_key.s, params.ciph_modulus), params.ciph_modulus).scalar_multiply(
                -1, params.ciph_modulus)
        p1 = pk_coeff
        self.public_key = PublicKey(p0, p1)

    def generate_relin_key(self, params):
        """Generates a relinearization key for BFV scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext, and ciphertext modulus.
        """
        base = ceil(sqrt(params.ciph_modulus))
        num_levels = floor(log(params.ciph_modulus, base)) + 1

        keys = [0] * num_levels
        power = 1
        sk_squared = self.secret_key.s.multiply(self.secret_key.s, params.ciph_modulus)

        for i in range(num_levels):
            k1 = Polynomial(params.poly_degree, sample_uniform(0, params.ciph_modulus, params.poly_degree))
            error = Polynomial(params.poly_degree, sample_triangle(params.poly_degree))
            k0 = self.secret_key.s.multiply(k1, params.ciph_modulus).add(
                    error, params.ciph_modulus).scalar_multiply(-1).add(
                        sk_squared.scalar_multiply(power), params.ciph_modulus).mod(params.ciph_modulus)
            keys[i] = (k0, k1)
            power *= base
            power %= params.ciph_modulus

        self.relin_key = BFVRelinKey(base, keys)

