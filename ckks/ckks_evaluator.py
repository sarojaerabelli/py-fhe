"""A module to perform computations on ciphertexts in CKKS."""

from math import sqrt
import math

from ckks.ckks_bootstrapping_context import CKKSBootstrappingContext
from util.ciphertext import Ciphertext
from util.crt import CRTContext
from util.dcrt_polynomial import DCRTPolynomial
import util.matrix_operations
from util.plaintext import Plaintext
from util.polynomial import Polynomial

class CKKSEvaluator:

    """An instance of an evaluator for ciphertexts.

    This allows us to add, multiply, and relinearize ciphertexts.

    Attributes:
        degree (int): Polynomial degree of ring.
        big_modulus (int): Modulus q of coefficients of polynomial
            ring R_q.
        scaling_factor (float): Scaling factor to encode new plaintexts with.
        boot_context (CKKSBootstrappingContext): Bootstrapping pre-computations.
        rns (Boolean): True, if using the RNS representation, otherwise False.
        crt_context (CRTContext): CRT functions.
    """

    def __init__(self, params):
        """Inits Evaluator.

        Args:
            params (Parameters): Parameters including polynomial degree, ciphertext modulus,
                and scaling factor.
        """
        self.degree = params.poly_degree
        self.big_modulus = params.big_modulus
        self.scaling_factor = params.scaling_factor
        self.boot_context = CKKSBootstrappingContext(params)
        self.rns = params.rns
        self.crt_context = params.crt_context

    def add(self, ciph1, ciph2):
        """Adds two ciphertexts.

        Adds two ciphertexts within the context.

        Args:
            ciph1 (Ciphertext): First ciphertext.
            ciph2 (Ciphertext): Second ciphertext.

        Returns:
            A Ciphertext which is the sum of the two ciphertexts.
        """
        assert isinstance(ciph1, Ciphertext)
        assert isinstance(ciph2, Ciphertext)
        assert ciph1.scaling_factor == ciph2.scaling_factor, "Scaling factors are not equal. " \
            + "Ciphertext 1 scaling factor: %d bits, Ciphertext 2 scaling factor: %d bits" \
            % (math.log(ciph1.scaling_factor, 2), math.log(ciph2.scaling_factor, 2))
        assert ciph1.modulus == ciph2.modulus, "Moduli are not equal. " \
            + "Ciphertext 1 modulus: %d bits, Ciphertext 2 modulus: %d bits" \
            % (math.log(ciph1.modulus, 2), math.log(ciph2.modulus, 2))

        modulus = ciph1.modulus

        c0 = ciph1.c0.add(ciph2.c0, modulus)
        c0 = c0.mod_small(modulus)
        c1 = ciph1.c1.add(ciph2.c1, modulus)
        c1 = c1.mod_small(modulus)
        return Ciphertext(c0, c1, ciph1.scaling_factor, modulus)

    def add_plain(self, ciph, plain):
        """Adds a ciphertext with a plaintext.

        Adds a ciphertext with a plaintext polynomial within the context.

        Args:
            ciph (Ciphertext): A ciphertext to add.
            plain (Plaintext): A plaintext to add.

        Returns:
            A Ciphertext which is the sum of the ciphertext and plaintext.
        """
        assert isinstance(ciph, Ciphertext)
        assert isinstance(plain, Plaintext)
        assert ciph.scaling_factor == plain.scaling_factor, "Scaling factors are not equal. " \
            + "Ciphertext scaling factor: %d bits, Plaintext scaling factor: %d bits" \
            % (math.log(ciph.scaling_factor, 2), math.log(plain.scaling_factor, 2))

        c0 = ciph.c0.add(plain.poly, ciph.modulus)
        c0 = c0.mod_small(ciph.modulus)

        return Ciphertext(c0, ciph.c1, ciph.scaling_factor, ciph.modulus)

    def subtract(self, ciph1, ciph2):
        """Subtracts second ciphertext from first ciphertext.

        Computes ciph1 - ciph2.

        Args:
            ciph1 (Ciphertext): First ciphertext.
            ciph2 (Ciphertext): Second ciphertext.

        Returns:
            A Ciphertext which is the difference between the two ciphertexts.
        """
        assert isinstance(ciph1, Ciphertext)
        assert isinstance(ciph2, Ciphertext)
        assert ciph1.scaling_factor == ciph2.scaling_factor, "Scaling factors are not equal. " \
            + "Ciphertext 1 scaling factor: %d bits, Ciphertext 2 scaling factor: %d bits" \
            % (math.log(ciph1.scaling_factor, 2), math.log(ciph2.scaling_factor, 2))
        assert ciph1.modulus == ciph2.modulus, "Moduli are not equal. " \
            + "Ciphertext 1 modulus: %d bits, Ciphertext 2 modulus: %d bits" \
            % (math.log(ciph1.modulus, 2), math.log(ciph2.modulus, 2))

        modulus = ciph1.modulus

        c0 = ciph1.c0.subtract(ciph2.c0, modulus)
        c0 = c0.mod_small(modulus)
        c1 = ciph1.c1.subtract(ciph2.c1, modulus)
        c1 = c1.mod_small(modulus)
        return Ciphertext(c0, c1, ciph1.scaling_factor, modulus)

    def multiply(self, ciph1, ciph2, relin_key):
        """Multiplies two ciphertexts.

        Multiplies two ciphertexts within the context, and relinearizes.

        Args:
            ciph1 (Ciphertext): First ciphertext.
            ciph2 (Ciphertext): Second ciphertext.
            relin_key (PublicKey): Relinearization keys.

        Returns:
            A Ciphertext which is the product of the two ciphertexts.
        """
        assert isinstance(ciph1, Ciphertext)
        assert isinstance(ciph2, Ciphertext)
        assert ciph1.modulus == ciph2.modulus, "Moduli are not equal. " \
            + "Ciphertext 1 modulus: %d bits, Ciphertext 2 modulus: %d bits" \
            % (math.log(ciph1.modulus, 2), math.log(ciph2.modulus, 2))

        modulus = ciph1.modulus

        c0 = ciph1.c0.multiply(ciph2.c0, modulus)
        c0 = c0.mod_small(modulus)

        c1 = ciph1.c0.multiply(ciph2.c1, modulus)
        temp = ciph1.c1.multiply(ciph2.c0, modulus)
        c1 = c1.add(temp, modulus)
        c1 = c1.mod_small(modulus)

        c2 = ciph1.c1.multiply(ciph2.c1, modulus)
        c2 = c2.mod_small(modulus)

        return self.relinearize(relin_key, c0, c1, c2, ciph1.scaling_factor * ciph2.scaling_factor,
                                modulus)

    def multiply_plain(self, ciph, plain):
        """Multiplies a ciphertext with a plaintext.

        Multiplies a ciphertext with a plaintext polynomial within the context.

        Args:
            ciph (Ciphertext): A ciphertext to multiply.
            plain (Plaintext): A plaintext to multiply.

        Returns:
            A Ciphertext which is the product of the ciphertext and plaintext.
        """
        assert isinstance(ciph, Ciphertext)
        assert isinstance(plain, Plaintext)

        c0 = ciph.c0.multiply(plain.poly, ciph.modulus)
        c0 = c0.mod_small(ciph.modulus)

        c1 = ciph.c1.multiply(plain.poly, ciph.modulus)
        c1 = c1.mod_small(ciph.modulus)

        return Ciphertext(c0, c1, ciph.scaling_factor * plain.scaling_factor, ciph.modulus)

    def relinearize(self, relin_key, c0, c1, c2, new_scaling_factor, modulus):
        """Relinearizes a 3-dimensional ciphertext.

        Reduces 3-dimensional ciphertext back down to 2 dimensions.

        Args:
            relin_key (PublicKey): Relinearization keys.
            c0 (Polynomial): First component of ciphertext.
            c1 (Polynomial): Second component of ciphertext.
            c2 (Polynomial): Third component of ciphertext.
            new_scaling_factor (float): New scaling factor for ciphertext.
            modulus (int): Ciphertext modulus.

        Returns:
            A Ciphertext which has only two components.
        """
        new_c0 = relin_key.p0.multiply(c2, modulus * self.big_modulus)
        new_c0 = new_c0.mod_small(modulus * self.big_modulus)
        new_c0 = new_c0.scalar_integer_divide(self.big_modulus)
        new_c0 = new_c0.add(c0, modulus)
        new_c0 = new_c0.mod_small(modulus)

        new_c1 = relin_key.p1.multiply(c2, modulus * self.big_modulus)
        new_c1 = new_c1.mod_small(modulus * self.big_modulus)
        new_c1 = new_c1.scalar_integer_divide(self.big_modulus)
        new_c1 = new_c1.add(c1, modulus)
        new_c1 = new_c1.mod_small(modulus)

        return Ciphertext(new_c0, new_c1, new_scaling_factor, modulus)

    def rescale(self, ciph, division_factor):
        """Rescales a ciphertext to a new scaling factor.

        Divides ciphertext by division factor, and updates scaling factor
        and ciphertext. modulus.

        Args:
            ciph (Ciphertext): Ciphertext to modify.
            division_factor (float): Factor to divide by.

        Returns:
            Rescaled ciphertext.
        """
        c0 = ciph.c0.scalar_integer_divide(division_factor)
        c1 = ciph.c1.scalar_integer_divide(division_factor)
        return Ciphertext(c0, c1, ciph.scaling_factor // division_factor,
                          ciph.modulus // division_factor)

    def lower_modulus(self, ciph, division_factor):
        """Rescales a ciphertext to a new scaling factor.

        Divides ciphertext by division factor, and updates scaling factor
        and ciphertext modulus.

        Args:
            ciph (Ciphertext): Ciphertext to modify.
            division_factor (float): Factor to divide by.

        Returns:
            Rescaled ciphertext.
        """
        new_modulus = ciph.modulus // division_factor
        c0 = ciph.c0.mod_small(new_modulus)
        c1 = ciph.c1.mod_small(new_modulus)
        return Ciphertext(c0, c1, ciph.scaling_factor, new_modulus)

    def switch_key(self, ciph, key):
        """Outputs ciphertext with switching key.

        Performs KS procedure as described in CKKS paper.

        Args:
            ciph (Ciphertext): Ciphertext to change.
            switching_key (PublicKey): Switching key.

        Returns:
            A Ciphertext which encrypts the same message under a different key.
        """

        c0 = key.p0.multiply(ciph.c1, ciph.modulus * self.big_modulus)
        c0 = c0.mod_small(ciph.modulus * self.big_modulus)
        c0 = c0.scalar_integer_divide(self.big_modulus)
        c0 = c0.add(ciph.c0, ciph.modulus)
        c0 = c0.mod_small(ciph.modulus)

        c1 = key.p1.multiply(ciph.c1, ciph.modulus * self.big_modulus)
        c1 = c1.mod_small(ciph.modulus * self.big_modulus)
        c1 = c1.scalar_integer_divide(self.big_modulus)
        c1 = c1.mod_small(ciph.modulus)

        return Ciphertext(c0, c1, ciph.scaling_factor, ciph.modulus)

    def rotate(self, ciph, rotation, rot_key):
        """Rotates a ciphertext by the amount specified in rotation.

        Returns a ciphertext for a plaintext which is rotated by the amount
        in rotation.

        Args:
            ciph (Ciphertext): Ciphertext to rotate.
            rotation (int): Amount to rotate by.
            rot_key (RotationKey): Rotation key corresponding to the rotation.

        Returns:
            A Ciphertext which is the encryption of the rotation of the original
            plaintext.
        """
        rot_ciph0 = ciph.c0.rotate(rotation)
        rot_ciph1 = ciph.c1.rotate(rotation)
        rot_ciph = Ciphertext(rot_ciph0, rot_ciph1, ciph.scaling_factor, ciph.modulus)
        return self.switch_key(rot_ciph, rot_key.key)

    def conjugate(self, ciph, conj_key):
        """Conjugates the ciphertext.

        Returns a ciphertext for a plaintext which is conjugated.

        Args:
            ciph (Ciphertext): Ciphertext to conjugate.
            conj_key (PublicKey): Conjugation key.

        Returns:
            A Ciphertext which is the encryption of the conjugation of the original
            plaintext.
        """

        conj_ciph0 = ciph.c0.conjugate().mod_small(ciph.modulus)
        conj_ciph1 = ciph.c1.conjugate().mod_small(ciph.modulus)
        conj_ciph = Ciphertext(conj_ciph0, conj_ciph1, ciph.scaling_factor, ciph.modulus)
        return self.switch_key(conj_ciph, conj_key)

    def multiply_matrix_naive(self, ciph, matrix, rot_keys, encoder):
        """Multiplies the ciphertext by the given matrix.

        Returns a ciphertext for the matrix multiplication.

        Args:
            ciph (Ciphertext): Ciphertext to multiply.
            matrix (2-D Array): Matrix to multiply.
            rot_keys (dict (RotationKey)): Rotation keys
            encoder (CKKSEncoder): Encoder for CKKS.

        Returns:
            A Ciphertext which is the product of matrix and ciph.
        """
        diag = util.matrix_operations.diagonal(matrix, 0)
        diag = encoder.encode(diag, self.scaling_factor)
        ciph_prod = self.multiply_plain(ciph, diag)

        for j in range(1, len(matrix)):
            diag = util.matrix_operations.diagonal(matrix, j)
            diag = encoder.encode(diag, self.scaling_factor)
            rot = self.rotate(ciph, j, rot_keys[j])
            ciph_temp = self.multiply_plain(rot, diag)
            ciph_prod = self.add(ciph_prod, ciph_temp)

        return ciph_prod

    def multiply_matrix(self, ciph, matrix, rot_keys, encoder):
        """Multiplies the ciphertext by the given matrix quickly.

        Returns a ciphertext for the matrix multiplication using the Baby-Step Giant-Step algorithm
        described in the CKKS paper.

        Args:
            ciph (Ciphertext): Ciphertext to multiply.
            matrix (2-D Array): Matrix to multiply.
            rot_keys (dict (RotationKey)): Rotation keys
            encoder (CKKSEncoder): Encoder for CKKS.

        Returns:
            A Ciphertext which is the product of matrix and ciph.
        """

        # Compute two factors of matrix_len (a power of two), both near its square root.
        matrix_len = len(matrix)
        matrix_len_factor1 = int(sqrt(matrix_len))
        if matrix_len != matrix_len_factor1 * matrix_len_factor1:
            matrix_len_factor1 = int(sqrt(2 * matrix_len))
        matrix_len_factor2 = matrix_len // matrix_len_factor1

        # Compute rotations.
        ciph_rots = [0] * matrix_len_factor1
        ciph_rots[0] = ciph
        for i in range(1, matrix_len_factor1):
            ciph_rots[i] = self.rotate(ciph, i, rot_keys[i])

        # Compute sum.
        outer_sum = None
        for j in range(matrix_len_factor2):
            inner_sum = None
            shift = matrix_len_factor1 * j
            for i in range(matrix_len_factor1):
                diagonal = util.matrix_operations.diagonal(matrix, shift + i)
                diagonal = util.matrix_operations.rotate(diagonal, -shift)
                diagonal_plain = encoder.encode(diagonal, self.scaling_factor)
                dot_prod = self.multiply_plain(ciph_rots[i], diagonal_plain)
                if inner_sum:
                    inner_sum = self.add(inner_sum, dot_prod)
                else:
                    inner_sum = dot_prod

            rotated_sum = self.rotate(inner_sum, shift, rot_keys[shift])
            if outer_sum:
                outer_sum = self.add(outer_sum, rotated_sum)
            else:
                outer_sum = rotated_sum

        outer_sum = self.rescale(outer_sum, self.scaling_factor)
        return outer_sum

    # BOOTSTRAPPING

    def create_constant_plain(self, const):
        """Creates a plaintext containing a constant value.

        Takes a floating-point constant, and turns it into a plaintext.

        Args:
            const (float): Constant to encode.

        Returns:
            Plaintext with constant value.
        """
        plain_vec = [0] * (self.degree)
        plain_vec[0] = int(const * self.scaling_factor)
        if self.rns:
            return Plaintext(DCRTPolynomial(self.degree, plain_vec, self.crt_context),
                             self.scaling_factor)
        return Plaintext(Polynomial(self.degree, plain_vec), self.scaling_factor)


    def create_complex_constant_plain(self, const, encoder):
        """Creates a plaintext containing a constant value.

        Takes any constant, and turns it into a plaintext.

        Args:
            const (float): Constant to encode.
            encoder (CKKSEncoder): Encoder.

        Returns:
            Plaintext with constant value.
        """
        plain_vec = [const] * (self.degree // 2)
        return encoder.encode(plain_vec, self.scaling_factor)

    def coeff_to_slot(self, ciph, rot_keys, conj_key, encoder):
        """Takes a ciphertext coefficients and puts into plaintext slots.

        Takes an encryption of t(x) = t_0 + t_1x + ... and transforms to
        encryptions of (t_0, t_1, ..., t_(n/2)) and (t_(n/2 + 1), ..., t_(n-1))
        before these vectors are encoded.

        Args:
            ciph (Ciphertext): Ciphertext to transform.
            rot_keys (dict (RotationKey)): Rotation keys
            conj_key (PublicKey): Conjugation key.
            encoder (CKKSEncoder): Encoder for CKKS.

        Returns:
            Two Ciphertexts which are transformed.
        """
        # Compute new ciphertexts.
        s1 = self.multiply_matrix(ciph, self.boot_context.encoding_mat_conj_transpose0,
                                  rot_keys, encoder)
        s2 = self.conjugate(ciph, conj_key)
        s2 = self.multiply_matrix(s2, self.boot_context.encoding_mat_transpose0, rot_keys,
                                  encoder)
        ciph0 = self.add(s1, s2)
        constant = self.create_constant_plain(1 / self.degree)
        ciph0 = self.multiply_plain(ciph0, constant)
        ciph0 = self.rescale(ciph0, self.scaling_factor)

        s1 = self.multiply_matrix(ciph, self.boot_context.encoding_mat_conj_transpose1,
                                  rot_keys, encoder)
        s2 = self.conjugate(ciph, conj_key)
        s2 = self.multiply_matrix(s2, self.boot_context.encoding_mat_transpose1, rot_keys,
                                  encoder)
        ciph1 = self.add(s1, s2)
        ciph1 = self.multiply_plain(ciph1, constant)
        ciph1 = self.rescale(ciph1, self.scaling_factor)

        return ciph0, ciph1

    def slot_to_coeff(self, ciph0, ciph1, rot_keys, encoder):
        """Takes plaintext slots and puts into ciphertext coefficients.

        Takes encryptions of (t_0, t_1, ..., t_(n/2)) and (t_(n/2 + 1), ..., t_(n-1))
        before these vectors are encoded and transofmrs to an encryption of
        t(x) = t_0 + t_1x + ...

        Args:
            ciph0 (Ciphertext): First ciphertext to transform.
            ciph1 (Ciphertext): Second ciphertext to transform.
            rot_keys (dict (RotationKey)): Rotation keys.
            encoder (CKKSEncoder): Encoder for CKKS.

        Returns:
            Ciphertext which is transformed.
        """
        s1 = self.multiply_matrix(ciph0, self.boot_context.encoding_mat0, rot_keys,
                                  encoder)
        s2 = self.multiply_matrix(ciph1, self.boot_context.encoding_mat1, rot_keys,
                                  encoder)
        ciph = self.add(s1, s2)

        return ciph

    def exp_taylor(self, ciph, relin_key, encoder):
        """Evaluates the exponential function on the ciphertext.

        Takes an encryption of m and returns an encryption of e^(2 * pi * m).

        Args:
            ciph (Ciphertext): Ciphertext to transform.
            relin_key (PublicKey): Relinearization key.
            encoder (CKKSEncoder): Encoder.

        Returns:
            Ciphertext for exponential.
        """
        ciph2 = self.multiply(ciph, ciph, relin_key)
        ciph2 = self.rescale(ciph2, self.scaling_factor)

        ciph4 = self.multiply(ciph2, ciph2, relin_key)
        ciph4 = self.rescale(ciph4, self.scaling_factor)

        const = self.create_constant_plain(1)
        ciph01 = self.add_plain(ciph, const)

        const = self.create_constant_plain(1)
        ciph01 = self.multiply_plain(ciph01, const)
        ciph01 = self.rescale(ciph01, self.scaling_factor)

        const = self.create_constant_plain(3)
        ciph23 = self.add_plain(ciph, const)

        const = self.create_constant_plain(1 / 6)
        ciph23 = self.multiply_plain(ciph23, const)
        ciph23 = self.rescale(ciph23, self.scaling_factor)

        ciph23 = self.multiply(ciph23, ciph2, relin_key)
        ciph23 = self.rescale(ciph23, self.scaling_factor)
        ciph01 = self.lower_modulus(ciph01, self.scaling_factor)
        ciph23 = self.add(ciph23, ciph01)

        const = self.create_constant_plain(5)
        ciph45 = self.add_plain(ciph, const)

        const = self.create_constant_plain(1 / 120)
        ciph45 = self.multiply_plain(ciph45, const)
        ciph45 = self.rescale(ciph45, self.scaling_factor)

        const = self.create_constant_plain(7)
        ciph = self.add_plain(ciph, const)

        const = self.create_constant_plain(1 / 5040)
        ciph = self.multiply_plain(ciph, const)
        ciph = self.rescale(ciph, self.scaling_factor)

        ciph = self.multiply(ciph, ciph2, relin_key)
        ciph = self.rescale(ciph, self.scaling_factor)

        ciph45 = self.lower_modulus(ciph45, self.scaling_factor)
        ciph = self.add(ciph, ciph45)

        ciph = self.multiply(ciph, ciph4, relin_key)
        ciph = self.rescale(ciph, self.scaling_factor)

        ciph23 = self.lower_modulus(ciph23, self.scaling_factor)
        ciph = self.add(ciph, ciph23)

        return ciph

    def raise_modulus(self, ciph):
        """Raises ciphertext modulus.

        Takes a ciphertext (mod q), and scales it up to mod Q_0. Also increases the scaling factor.

        Args:
            ciph (Ciphertext): Ciphertext to scale up.

        Returns:
            Ciphertext for exponential.
        """
        # Raise scaling factor.
        self.scaling_factor = ciph.modulus
        ciph.scaling_factor = self.scaling_factor

        # Raise ciphertext modulus.
        ciph.modulus = self.big_modulus

    def exp(self, ciph, const, relin_key, encoder):
        """Evaluates the exponential function on the ciphertext.

        Takes an encryption of m and returns an encryption of e^(const * m).

        Args:
            ciph (Ciphertext): Ciphertext to transform.
            const (complex): Constant to multiply ciphertext by.
            relin_key (PublicKey): Relinearization key.
            encoder (CKKSEncoder): Encoder.

        Returns:
            Ciphertext for exponential.
        """
        num_iterations = self.boot_context.num_taylor_iterations
        const_plain = self.create_complex_constant_plain(const / 2**num_iterations, encoder)
        ciph = self.multiply_plain(ciph, const_plain)
        ciph = self.rescale(ciph, self.scaling_factor)
        ciph = self.exp_taylor(ciph, relin_key, encoder)

        for _ in range(num_iterations):
            ciph = self.multiply(ciph, ciph, relin_key)
            ciph = self.rescale(ciph, self.scaling_factor)

        return ciph

    def bootstrap(self, ciph, rot_keys, conj_key, relin_key, encoder):
        """Evaluates the bootstrapping circuit on ciph.

        Takes a ciphertext (mod q), that encrypts some value m, and outputs a new
        ciphertext (mod Q_0) that also encrypts m, via bootstrapping.

        Args:
            ciph (Ciphertext): Ciphertext to transform.
            rot_keys (dict (RotationKey)): Dictionary of rotation keys, indexed by rotation number
            conj_key (PublicKey): Conjugation key.
            relin_key (PublicKey): Relinearization key.
            encoder (CKKSEncoder): Encoder.

        Returns:
            Ciphertext for exponential.
        """
        # Raise modulus.
        old_modulus = ciph.modulus
        old_scaling_factor = self.scaling_factor
        self.raise_modulus(ciph)

        # Coeff to slot.
        ciph0, ciph1 = self.coeff_to_slot(ciph, rot_keys, conj_key, encoder)

        # Exponentiate.
        const = self.scaling_factor / old_modulus * 2 * math.pi * 1j
        ciph_exp0 = self.exp(ciph0, const, relin_key, encoder)
        ciph_neg_exp0 = self.conjugate(ciph_exp0, conj_key)
        ciph_exp1 = self.exp(ciph1, const, relin_key, encoder)
        ciph_neg_exp1 = self.conjugate(ciph_exp1, conj_key)

        # Compute sine.
        ciph_sin0 = self.subtract(ciph_exp0, ciph_neg_exp0)
        ciph_sin1 = self.subtract(ciph_exp1, ciph_neg_exp1)

        # Scale answer.
        plain_const = self.create_complex_constant_plain(
            old_modulus / self.scaling_factor * 0.25 / math.pi / 1j, encoder)
        ciph0 = self.multiply_plain(ciph_sin0, plain_const)
        ciph1 = self.multiply_plain(ciph_sin1, plain_const)
        ciph0 = self.rescale(ciph0, self.scaling_factor)
        ciph1 = self.rescale(ciph1, self.scaling_factor)

        # Slot to coeff.
        old_ciph = ciph
        ciph = self.slot_to_coeff(ciph0, ciph1, rot_keys, encoder)

        # Reset scaling factor.
        self.scaling_factor = old_scaling_factor
        ciph.scaling_factor = self.scaling_factor

        print("------------ BOOTSTRAPPING MODULUS CHANGES -------------")
        print("Old modulus q: %d bits" % (int(math.log(old_modulus, 2))))
        print("Raised modulus Q_0: %d bits" % (int(math.log(self.big_modulus, 2))))
        print("Final modulus Q_1: %d bits" % (int(math.log(ciph.modulus, 2))))

        return old_ciph, ciph
