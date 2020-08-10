"""A module to handle polynomial arithmetic in the quotient ring
Z_a[x]/f(x).
"""
from util.ntt import NTTContext, FFTContext

class Polynomial:
    """A polynomial in the ring R_a.

    Here, R is the quotient ring Z[x]/f(x), where f(x) = x^d + 1.
    The polynomial keeps track of the ring degree d, the coefficient
    modulus a, and the coefficients in an array.

    Attributes:
        ring_degree (int): Degree d of polynomial that determines the
            quotient ring R.
        coeffs (array): Array of coefficients of polynomial, where coeffs[i]
            is the coefficient for x^i.
    """

    def __init__(self, degree, coeffs):
        """Inits Polynomial in the ring R_a with the given coefficients.

        Args:
            degree (int): Degree of quotient polynomial for ring R_a.
            coeffs (array): Array of integers of size degree, representing
                coefficients of polynomial.
        """
        self.ring_degree = degree
        assert len(coeffs) == degree, 'Size of polynomial array %d is not \
            equal to degree %d of ring' %(len(coeffs), degree)

        self.coeffs = coeffs

    def add(self, poly, coeff_modulus=None):
        """Adds two polynomials in the ring.

        Adds the current polynomial to poly inside the ring R_a.

        Args:
            poly (Polynomial): Polynomial to be added to the current
                polynomial.
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.

        Returns:
            A Polynomial which is the sum of the two polynomials.
        """
        assert isinstance(poly, Polynomial)

        poly_sum = Polynomial(self.ring_degree, [0] * self.ring_degree)

        poly_sum.coeffs = [self.coeffs[i] + poly.coeffs[i] for i in range(self.ring_degree)]
        if coeff_modulus:
            poly_sum = poly_sum.mod(coeff_modulus)
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
        assert isinstance(poly, Polynomial)

        poly_diff = Polynomial(self.ring_degree, [0] * self.ring_degree)

        poly_diff.coeffs = [self.coeffs[i] - poly.coeffs[i] for i in range(self.ring_degree)]
        if coeff_modulus:
            poly_diff = poly_diff.mod(coeff_modulus)
        return poly_diff

    def multiply(self, poly, coeff_modulus, ntt=None, crt=None):
        """Multiplies two polynomials in the ring using NTT.

        Multiplies the current polynomial to poly inside the ring R_a
        using the Number Theoretic Transform (NTT) in O(nlogn).

        Args:
            poly (Polynomial): Polynomial to be multiplied to the current
                polynomial.
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.
            ntt (NTTContext): An instance of the NTTContext object, which
                can be used for multiplication.
            crt (CRTContext): An instance of the CRTContext object, which
                was created with primes whose product is the coefficient
                modulus. It defaults to None, if we are not using the
                CRT representation.

        Returns:
            A Polynomial which is the product of the two polynomials.
        """
        if crt:
            return self.multiply_crt(poly, crt)

        if ntt:
            a = ntt.ftt_fwd(self.coeffs)
            b = ntt.ftt_fwd(poly.coeffs)
            ab = [a[i] * b[i] for i in range(self.ring_degree)]
            prod = ntt.ftt_inv(ab)
            return Polynomial(self.ring_degree, prod)
        
        return self.multiply_naive(poly, coeff_modulus)

    def multiply_crt(self, poly, crt):
        """Multiplies two polynomials in the ring in CRT representation.

        Multiplies the current polynomial to poly inside the ring by
        splitting it into Chinese Remainder Theorem subrings for the primes
        given. For each subring, we multiply using NTT and recombine with CRT.

        Args:
            poly (Polynomial): Polynomial to be multiplied to the current
                polynomial.
            crt (CRTContext): An instance of the CRTContext object, which
                was created with primes whose product is the coefficient
                modulus.

        Returns:
            A Polynomial which is the product of the two polynomials.
        """
        assert isinstance(poly, Polynomial)

        poly_prods = []

        # Perform NTT for each prime factor.
        for i in range(len(crt.primes)):
            prod = self.multiply(poly, crt.primes[i], ntt=crt.ntts[i])
            poly_prods.append(prod)

        # Combine the products with CRT.
        final_coeffs = [0] * self.ring_degree
        for i in range(self.ring_degree):
            values = [p.coeffs[i] for p in poly_prods]
            final_coeffs[i] = crt.reconstruct(values)

        return Polynomial(self.ring_degree, final_coeffs).mod_small(crt.modulus)


    def multiply_fft(self, poly, round=True):
        """Multiplies two polynomials in the ring using FFT.

        Multiplies the current polynomial to poly inside the ring R_a
        using FFT.

        Args:
            poly (Polynomial): Polynomial to be multiplied to the current
                polynomial.

        Returns:
            A Polynomial which is the product of the two polynomials.
        """
        assert isinstance(poly, Polynomial)

        fft = FFTContext(self.ring_degree * 8)
        a = fft.fft_fwd(self.coeffs + [0] * self.ring_degree)
        b = fft.fft_fwd(poly.coeffs + [0] * self.ring_degree)
        ab = [a[i] * b[i] for i in range(self.ring_degree * 2)]
        prod = fft.fft_inv(ab)
        poly_prod = [0] * self.ring_degree

        for d in range(2 * self.ring_degree - 1):
            # Since x^d = -1, the degree is taken mod d, and the sign
            # changes when the exponent is > d.
            index = d % self.ring_degree
            sign = (int(d < self.ring_degree) - 0.5) * 2
            poly_prod[index] += sign * prod[d]

        if round:
            return Polynomial(self.ring_degree, poly_prod).round()
        else:
            return Polynomial(self.ring_degree, poly_prod)

    def multiply_naive(self, poly, coeff_modulus=None):
        """Multiplies two polynomials in the ring in O(n^2).

        Multiplies the current polynomial to poly inside the ring R_a
        naively in O(n^2) time.

        Args:
            poly (Polynomial): Polynomial to be multiplied to the current
                polynomial.
            coeff_modulus (int): Modulus a of coefficients of polynomial
                ring R_a.

        Returns:
            A Polynomial which is the product of the two polynomials.
        """
        assert isinstance(poly, Polynomial)

        poly_prod = Polynomial(self.ring_degree,
                               [0] * self.ring_degree)

        for d in range(2 * self.ring_degree - 1):
            # Since x^d = -1, the degree is taken mod d, and the sign
            # changes when the exponent is > d.
            index = d % self.ring_degree
            sign = int(d < self.ring_degree) * 2 - 1

            # Perform a convolution to compute the coefficient for x^d.
            coeff = 0
            for i in range(self.ring_degree):
                if 0 <= d - i < self.ring_degree:
                    coeff += self.coeffs[i] * poly.coeffs[d - i]
            poly_prod.coeffs[index] += sign * coeff
            
            if coeff_modulus:
                poly_prod.coeffs[index] %= coeff_modulus

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
        if coeff_modulus:
            new_coeffs = [(scalar * c) % coeff_modulus for c in self.coeffs]
        else:
            new_coeffs = [(scalar * c) for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

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
        if coeff_modulus:
            new_coeffs = [(c // scalar) % coeff_modulus for c in self.coeffs]
        else:
            new_coeffs = [(c // scalar) for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

    def rotate(self, r):
        """Rotates plaintext coefficients by r.

        Rotates all the plaintext coefficients to the left such that the x^r
        coefficient is now the coefficient for x^0. We do so by applying the
        transformation m(X) -> m(X^k), where k = 5^r in the ciphertext
        polynomial.

        Returns:
            A rotated Polynomial.
        """
        k = 5 ** r
        new_coeffs = [0] * self.ring_degree
        for i in range(self.ring_degree):
            index = (i * k) % (2 * self.ring_degree)
            if index < self.ring_degree:
                new_coeffs[index] = self.coeffs[i]
            else:
                new_coeffs[index - self.ring_degree] = -self.coeffs[i]
        return Polynomial(self.ring_degree, new_coeffs)

    def conjugate(self):
        """Conjugates plaintext coefficients.

        Conjugates all the plaintext coefficients. We do so by applying the
        transformation m(X) -> m(X^{-1}).

        Returns:
            A conjugated Polynomial.
        """
        new_coeffs = [0] * self.ring_degree
        new_coeffs[0] = self.coeffs[0]
        for i in range(1, self.ring_degree):
            new_coeffs[i] = -self.coeffs[self.ring_degree - i]
        return Polynomial(self.ring_degree, new_coeffs)


    def round(self):
        """Rounds all coefficients to nearest integer.

        Rounds all the current polynomial's coefficients to the nearest
        integer, where |x| = n + 0.5 rounds to |x| = n
        (i.e. 0.5 rounds to 0 and -1.5 rounds to -1).

        Returns:
            A Polynomial which is the rounded version of the current
            polynomial.
        """
        if type(self.coeffs[0]) == complex:
            new_coeffs = [round(c.real) for c in self.coeffs]
        else:
            new_coeffs = [round(c) for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

    def floor(self):
        """Rounds all coefficients down to nearest integer.

        Rounds all the current polynomial's coefficients down to the nearest
        integer.

        Returns:
            A Polynomial which is the floor of the current
            polynomial.
        """
        new_coeffs = [int(c) for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

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
        new_coeffs = [c % coeff_modulus for c in self.coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

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
        try:
            new_coeffs = [c % coeff_modulus for c in self.coeffs]
            new_coeffs = [c - coeff_modulus if c > coeff_modulus // 2 else c for c in new_coeffs]
        except:
            print(self.coeffs)
            print(coeff_modulus)
            new_coeffs = [c % coeff_modulus for c in self.coeffs]
            new_coeffs = [c - coeff_modulus if c > coeff_modulus // 2 else c for c in new_coeffs]
        return Polynomial(self.ring_degree, new_coeffs)

    def base_decompose(self, base, num_levels):
        """Decomposes each polynomial coefficient into a base T
        representation.

        Args:
            base (int): Base to decompose coefficients with.
            num_levels (int): Log of ciphertext modulus with the specified base.

        Returns:
            An array of Polynomials, where the ith element is the coefficient of
            the base T^i.
        """
        decomposed = [Polynomial(self.ring_degree, [0] * self.ring_degree) for _ in range(num_levels)]
        poly = self

        for i in range(num_levels):
            decomposed[i] = poly.mod(base)
            poly = poly.scalar_multiply(1 / base).floor()
        return decomposed

    def evaluate(self, inp):
        """Evaluates the polynomial at the given input value.

        Evaluates the polynomial using Horner's method.

        Args:
            inp (int): Value to evaluate polynomial at.

        Returns:
            Evaluation of polynomial at input.
        """
        result = self.coeffs[-1]

        for i in range(self.ring_degree - 2, -1, -1):
            result = result * inp + self.coeffs[i]

        return result


    def __str__(self):
        """Represents polynomial as a readable string.

        Returns:
            A string which represents the Polynomial.
        """
        s = ''
        for i in range(self.ring_degree - 1, -1, -1):
            if self.coeffs[i] != 0:
                if s != '':
                    s += ' + '
                if i == 0 or self.coeffs[i] != 1:
                    s += str(int(self.coeffs[i]))
                if i != 0:
                    s += 'x'
                if i > 1:
                    s += '^' + str(i)
        return s
