"""A module to generate public and private keys for the CKKS scheme."""

from util.dcrt_polynomial import DCRTPolynomial
from util.polynomial import Polynomial
from util.public_key import PublicKey
from util.rotation_key import RotationKey
from util.secret_key import SecretKey
from util.random_sample import sample_triangle, sample_uniform, sample_hamming_weight_vector

class CKKSKeyGenerator:

    """An instance to generate a public/secret key pair and relinearization keys.

    The secret key s is generated randomly, and the public key is the
    pair (-as + e, a). The relinearization keys are generated, as
    specified in the CKKS paper.

    Attributes:
        params (Parameters): Parameters including polynomial degree, plaintext,
            and ciphertext modulus.
        secret_key (Polynomial): secret key randomly generated from R_q.
        public_key (tuple of Polynomials): public key generated from
            secret key.
        relin_key (tuple of Polynomials): relinearization key generated
            from secret key.
    """

    def __init__(self, params):
        """Generates secret/public key pair for CKKS scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext, and ciphertext modulus.
        """
        self.params = params
        self.generate_secret_key(params)
        self.generate_public_key(params)
        self.generate_relin_key(params)

    def generate_secret_key(self, params):
        """Generates a secret key for CKKS scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext, and ciphertext modulus.
        """
        key = sample_hamming_weight_vector(params.poly_degree, params.hamming_weight)
        if self.params.rns:
            self.secret_key = SecretKey(DCRTPolynomial(params.poly_degree, key,
                                                       self.params.crt_context))
        else:
            self.secret_key = SecretKey(Polynomial(params.poly_degree, key))

    def generate_public_key(self, params):
        """Generates a public key for CKKS scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext, and ciphertext modulus.
        """
        mod = self.params.big_modulus

        if self.params.rns:
            pk_coeff = DCRTPolynomial(params.poly_degree,
                                      sample_uniform(0, mod, params.poly_degree),
                                      self.params.crt_context)
            pk_error = DCRTPolynomial(params.poly_degree, sample_triangle(params.poly_degree),
                                      self.params.crt_context)
        else:
            pk_coeff = Polynomial(params.poly_degree, sample_uniform(0, mod, params.poly_degree))
            pk_error = Polynomial(params.poly_degree, sample_triangle(params.poly_degree))
        p0 = pk_coeff.multiply(self.secret_key.s, mod)
        p0 = p0.scalar_multiply(-1, mod)
        p0 = p0.add(pk_error, mod)
        p1 = pk_coeff
        self.public_key = PublicKey(p0, p1)

    def generate_switching_key(self, new_key):
        """Generates a switching key for CKKS scheme.

        Generates a switching key as described in KSGen in the CKKS paper.

        Args:
            new_key (Polynomial): New key to generate switching key.

        Returns:
            A switching key.
        """
        mod = self.params.big_modulus
        mod_squared = mod ** 2

        if self.params.rns:
            swk_coeff = DCRTPolynomial(self.params.poly_degree,
                                       sample_uniform(0, mod_squared, self.params.poly_degree),
                                       self.params.crt_context)
            swk_error = DCRTPolynomial(self.params.poly_degree,
                                       sample_triangle(self.params.poly_degree),
                                       self.params.crt_context)
        else:
            swk_coeff = Polynomial(self.params.poly_degree,
                                   sample_uniform(0, mod_squared, self.params.poly_degree))
            swk_error = Polynomial(self.params.poly_degree,
                                   sample_triangle(self.params.poly_degree))

        sw0 = swk_coeff.multiply(self.secret_key.s, mod_squared)
        sw0 = sw0.scalar_multiply(-1, mod_squared)
        sw0 = sw0.add(swk_error, mod_squared)
        temp = new_key.scalar_multiply(mod, mod_squared)
        sw0 = sw0.add(temp, mod_squared)
        sw1 = swk_coeff
        return PublicKey(sw0, sw1)

    def generate_relin_key(self, params):
        """Generates a relinearization key for CKKS scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                plaintext, and ciphertext modulus.
        """
        sk_squared = self.secret_key.s.multiply(self.secret_key.s, params.big_modulus)
        self.relin_key = self.generate_switching_key(sk_squared)

    def generate_rot_key(self, rotation):
        """Generates a rotation key for CKKS scheme.

        Args:
            rotation (int): Amount ciphertext is to be rotated by.

        Returns:
            A rotation key.
        """

        # Generate K_5^r(s).
        new_key = self.secret_key.s.rotate(rotation)
        rk = self.generate_switching_key(new_key)
        return RotationKey(rotation, rk)

    def generate_conj_key(self):
        """Generates a conjugation key for CKKS scheme.

        Returns:
            A conjugation key.
        """

        # Generate K_{-1}(s).
        new_key = self.secret_key.s.conjugate()
        return self.generate_switching_key(new_key)
