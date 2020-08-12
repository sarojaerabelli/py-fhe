"""A module to keep track of parameters for the CKKS scheme."""

import math
from util.crt import CRTContext

class CKKSParameters:

    """An instance of parameters for the CKKS scheme.

    Attributes:
        poly_degree (int): Degree d of polynomial that determines the
            quotient ring R.
        ciph_modulus (int): Coefficient modulus of ciphertexts.
        big_modulus (int): Large modulus used for bootstrapping.
        scaling_factor (float): Scaling factor to multiply by.
        hamming_weight (int): Hamming weight parameter for sampling secret key.
        prime_size (int): Minimum number of bits in primes for RNS representation.
        crt_context (CRTContext): Context to manage RNS representation.
    """

    def __init__(self, poly_degree, ciph_modulus, big_modulus, scaling_factor, prime_size=None):
        """Inits Parameters with the given parameters.

        Args:
            poly_degree (int): Degree d of polynomial of ring R.
            ciph_modulus (int): Coefficient modulus of ciphertexts.
            big_modulus (int): Large modulus used for bootstrapping.
            scaling_factor (float): Scaling factor to multiply by.
            prime_size (int): Minimum number of bits in primes for RNS representation.
        """
        self.poly_degree = poly_degree
        self.ciph_modulus = ciph_modulus
        self.big_modulus = big_modulus
        self.scaling_factor = scaling_factor
        self.hamming_weight = poly_degree // 4
        prime_size = 59
        if prime_size:
            num_primes = 1 + int((1 + math.log(poly_degree, 2) + 4 * math.log(big_modulus, 2) \
             / prime_size))
            self.crt_context = CRTContext(num_primes, prime_size, poly_degree)

    def print_parameters(self):
        """Prints parameters.
        """
        print("Encryption parameters")
        print("\t polynomial degree: %d" %(self.poly_degree))
        print("\t ciphertext modulus size: %d bits" % (int(math.log(self.ciph_modulus, 2))))
        print("\t Big ciphertext modulus size: %d bits" % (int(math.log(self.big_modulus, 2))))
        print("\t Scaling factor size: %d bits" % (int(math.log(self.scaling_factor, 2))))
