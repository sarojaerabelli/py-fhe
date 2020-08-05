"""A module to split a large number into its prime factors using the Chinese Remainder Theorem (CRT).
"""

import util.number_theory as nbtheory
from util.ntt import NTTContext

class CRTContext:

    """An instance of Chinese Remainder Theorem parameters.

    We split a large number into its prime factors.

    Attributes:
        poly_degree (int): Polynomial ring degree.
        primes (list): List of primes.
        modulus (int): Large modulus, product of all primes.
    """

    def __init__(self, num_primes, prime_size, poly_degree):
        """Inits CRTContext with a list of primes.

        Args:
            num_primes (int): Number of primes.
            prime_size (int): Minimum number of bits in primes.
            poly_degree (int): Polynomial degree of ring.
        """
        self.poly_degree = poly_degree
        self.generate_primes(num_primes, prime_size, mod=2*poly_degree)
        self.generate_ntt_contexts()

        self.modulus = 1
        for prime in self.primes:
            self.modulus *= prime

        self.precompute_crt()

    def generate_primes(self, num_primes, prime_size, mod):
        """Generates primes that are 1 (mod M), where M is twice the polynomial degree.

        Args:
            num_primes (int): Number of primes.
            prime_size (int): Minimum number of bits in primes.
            mod (int): Value M (must be a power of two) such that primes are 1 (mod M).
        """
        self.primes = [1] * num_primes
        possible_prime = (1 << prime_size) + 1
        for i in range(num_primes):
            possible_prime += mod
            while not nbtheory.is_prime(possible_prime):
                possible_prime += mod
            self.primes[i] = possible_prime

    def generate_ntt_contexts(self):
        """Generates NTTContexts for each primes.
        """
        self.ntts = []
        for prime in self.primes:
            ntt = NTTContext(self.poly_degree, prime)
            self.ntts.append(ntt)

    def precompute_crt(self):
        """Perform precomputations required for switching representations.
        """
        num_primes = len(self.primes)
        self.crt_vals = [1] * num_primes
        self.crt_inv_vals = [1] * num_primes
        for i in range(num_primes):
            self.crt_vals[i] = self.modulus // self.primes[i]
            self.crt_inv_vals[i] = nbtheory.mod_inv(self.crt_vals[i], self.primes[i])

    def crt(self, value):
        """Transform value to CRT representation.

        Args:
            value (int): Value to be transformed to CRT representation.
            primes (list): List of primes to use for CRT representation.
        """
        return [value % p for p in self.primes]

    def reconstruct(self, values):
        """Reconstructs original value from vals from the CRT representation to the regular representation.

        Args:
            values (list): List of values which are x_i (mod p_i).
        """
        assert len(values) == len(self.primes)
        regular_rep_val = 0

        for i in range(len(values)):
            intermed_val = (values[i] * self.crt_inv_vals[i]) % self.primes[i]
            intermed_val = (intermed_val * self.crt_vals[i]) % self.modulus
            regular_rep_val += intermed_val
            regular_rep_val %= self.modulus

        return regular_rep_val