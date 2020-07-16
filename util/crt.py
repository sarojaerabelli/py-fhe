"""A module to split a large number into its prime factors using the Chinese Remainder Theorem (CRT).
"""

import util.number_theory as nbtheory

class CRTContext:

    """An instance of Chinese Remainder Theorem parameters.

    We split a large number into its prime factors.

    Attributes:
        primes (list): List of primes.
        mod (int): Large modulus, product of all primes.
    """

    def __init__(self, primes):
        """Inits CRTContext with a list of primes.

        Args:
            primes (list): List of primes.
        """
        self.primes = primes

        self.modulus = 1
        for p in self.primes:
            self.modulus *= p

    def transform(self, values):
        """Transforms vals from the CRT representation to the regular representation.

        Args:
            values (list): List of values which are x_i (mod p_i).
        """

        regular_rep_val = 0

        for i in range(len(values)):
            crt_val = self.modulus // self.primes[i]
            crt_inv_val = nbtheory.mod_inv(crt_val, self.primes[i])
            intermed_val = (values[i] * crt_inv_val) % self.primes[i]
            intermed_val = (intermed_val * crt_val) % self.modulus
            regular_rep_val += intermed_val
            regular_rep_val %= self.modulus

        return regular_rep_val

    def inverse_transform(self, value):
        """Transform value to CRT representation.

        Args:
            value (int): Value to be transformed to CRT representation.
        """
        return [value % p for p in self.primes]