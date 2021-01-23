"""A module to handle polynomial arithmetic in the quotient ring
Z_a[x]/f(x), using its Chinese Remainder Theorem (CRT) representation.
"""
from util.polynomial import Polynomial

class DCRTPolynomial:
    """A polynomial in the ring R_a.

    Here, R is the quotient ring Z[x]/f(x), where f(x) = x^d + 1.
    The polynomial keeps track of the ring degree d, the coefficient
    modulus a, and the coefficients in an array.

    Attributes:
        ring_degree (int): Degree d of polynomial that determines the
            quotient ring R.
        polys (array): Array of polynomials, where polys[i]
            is the polynomial corresponding to the ith prime.
        crt (CRTContext): An instance of the CRTContext object, which
            was created with primes whose product is the coefficient
            modulus.
    """

    def __init__(self, degree, coeffs, crt):
        """Inits Polynomial in the ring R_a with the given coefficients.

        Args:
            degree (int): Degree of quotient polynomial for ring R_a.
            coeffs (array): Array of integers of size degree, representing
                coefficients of polynomial.
            crt (CRTContext): An instance of the CRTContext object, which
                was created with primes whose product is the coefficient
                modulus.
        """
        self.ring_degree = degree
        assert len(coeffs) == degree, 'Size of polynomial array %d is not \
            equal to degree %d of ring' %(len(coeffs), degree)

        self.polys = []
        self.crt = crt
        self.num_primes = len(crt.primes)

        for prime in crt.primes:
            crt_coeffs = [c % prime for c in coeffs]
            poly = Polynomial(self.ring_degree, crt_coeffs)
            self.polys.append(poly)


    def add(self, poly, coeff_modulus=None):
        """Adds two DCRT polynomials in the ring.

        Adds the current polynomial to poly inside the ring R_a.

        Args:
            poly (Polynomial): Polynomial to be added to the current
                polynomial.
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.

        Returns:
            A Polynomial which is the sum of the two polynomials.
        """
        assert isinstance(poly, DCRTPolynomial)
        assert self.crt == poly.crt

        poly_sum = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_sum.polys[i] = self.polys[i].add(poly.polys[i], self.crt.primes[i])
        return poly_sum

    def subtract(self, poly, coeff_modulus=None):
        """Subtracts second polynomial from first polynomial in the ring.

        Computes self - poly.

        Args:
            poly (Polynomial): Polynomial to be added to the current
                polynomial.
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.

        Returns:
            A Polynomial which is the difference between the two polynomials.
        """
        assert isinstance(poly, DCRTPolynomial)
        assert self.crt == poly.crt

        poly_diff = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_diff.polys[i] = self.polys[i].subtract(poly.polys[i], self.crt.primes[i])
        return poly_diff

    def multiply(self, poly, coeff_modulus=None):
        """Multiplies two polynomials in the ring using NTT.

        Multiplies the current polynomial to poly inside the ring R_a
        using the Number Theoretic Transform (NTT) in O(nlogn).

        Args:
            poly (Polynomial): Polynomial to be multiplied to the current
                polynomial.
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.

        Returns:
            A Polynomial which is the product of the two polynomials.
        """
        assert isinstance(poly, DCRTPolynomial)
        assert self.crt == poly.crt

        poly_prod = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_prod.polys[i] = self.polys[i].multiply(poly.polys[i], self.crt.primes[i],
                                                        ntt=self.crt.ntts[i])
        return poly_prod

    def scalar_multiply(self, scalar, coeff_modulus=None):
        """Multiplies polynomial by a scalar.

        Multiplies the current polynomial to scalar inside the ring R_a.

        Args:
            scalar (int): Scalar to be multiplied to the current
                polynomial.
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.

        Returns:
            A Polynomial which is the product of the polynomial and the
            scalar.
        """
        poly_scaled = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_scaled.polys[i] = self.polys[i].scalar_multiply(scalar, self.crt.primes[i])
        return poly_scaled

    def scalar_integer_divide(self, scalar, coeff_modulus=None):
        """Divides polynomial by a scalar.

        Performs integer division on the current polynomial by the scalar inside
        the ring R_a.

        Args:
            scalar (int): Scalar to be divided by.
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.

        Returns:
            A Polynomial which is the quotient of the polynomial and the
            scalar.
        """
        poly_scaled = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_scaled.polys[i] = self.polys[i].scalar_integer_divide(scalar, self.crt.primes[i])
        return poly_scaled

    def rotate(self, r):
        """Rotates plaintext coefficients by r.

        Rotates all the plaintext coefficients to the left such that the x^r
        coefficient is now the coefficient for x^0. We do so by applying the
        transformation m(X) -> m(X^k), where k = 5^r in the ciphertext
        polynomial.

        Returns:
            A rotated Polynomial.
        """
        poly_rot = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_rot.polys[i] = self.polys[i].rotate(r)
        return poly_rot

    def conjugate(self):
        """Conjugates plaintext coefficients.

        Conjugates all the plaintext coefficients. We do so by applying the
        transformation m(X) -> m(X^{-1}).

        Returns:
            A conjugated Polynomial.
        """
        poly_conj = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_conj.polys[i] = self.polys[i].conjugate()
        return poly_conj


    def round(self):
        """Rounds all coefficients to nearest integer.

        Rounds all the current polynomial's coefficients to the nearest
        integer, where |x| = n + 0.5 rounds to |x| = n
        (i.e. 0.5 rounds to 0 and -1.5 rounds to -1).

        Returns:
            A Polynomial which is the rounded version of the current
            polynomial.
        """
        poly_round = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_round.polys[i] = self.polys[i].round()
        return poly_round

    def floor(self):
        """Rounds all coefficients down to nearest integer.

        Rounds all the current polynomial's coefficients down to the nearest
        integer.

        Returns:
            A Polynomial which is the floor of the current
            polynomial.
        """
        poly_floor = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_floor.polys[i] = self.polys[i].floor()
        return poly_floor

    def mod(self, coeff_modulus):
        """Mods all coefficients in the given coefficient modulus.

        Mods all coefficients of the current polynomial using the
        given coefficient modulus.

        Args:
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.

        Returns:
            A Polynomial whose coefficients are modulo coeff_modulus.
        """
        poly_mod = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_mod.polys[i] = self.polys[i].mod(self.crt.primes[i])
        return poly_mod

    def mod_small(self, coeff_modulus):
        """Turns all coefficients in the given coefficient modulus
        to the range (-q/2, q/2].

        Turns all coefficients of the current polynomial
        in the given coefficient modulus to the range (-q/2, q/2].

        Args:
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.

        Returns:
            A Polynomial whose coefficients are modulo coeff_modulus.
        """
        poly_mod = DCRTPolynomial(self.ring_degree, [0] * self.ring_degree, self.crt)

        for i in range(self.num_primes):
            poly_mod.polys[i] = self.polys[i].mod_small(self.crt.primes[i])
        return poly_mod

    def reconstruct(self):
        """Reconstructs original polynomial from vals from the CRT representation to the regular
        representation.

        Returns:
            A Polynomial whose coefficients are reconstructed.
        """
        coeffs = [0] * self.ring_degree
        for i in range(self.ring_degree):
            values = [poly.coeffs[i] for poly in self.polys]
            coeffs[i] = self.crt.reconstruct(values)

        return Polynomial(self.ring_degree, coeffs)
