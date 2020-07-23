"""A module to encrypt for the CKKS scheme."""

import math

from util.ciphertext import Ciphertext
import util.matrix_operations
from util.polynomial import Polynomial
from util.random_sample import sample_triangle

class CKKSBootstrappingContext:

    """An object that stores information necessary for bootstrapping.

    Attributes:
        poly_degree: Polynomial degree of ring.
        old_modulus: Original modulus of initial ciphertext.
        coeff_to_slot_context: Stores matrix information necessary for coeff_to_slot.
        slot_to_coeff_context: Stores matrix information necessary for slot_to_coeff.
    """

    def __init__(self, params):
        """Generates private/public key pair for CKKS scheme.

        Args:
            params (Parameters): Parameters including polynomial degree,
                ciphertext modulus, etc.
        """
        self.poly_degree = params.poly_degree
        self.old_modulus = params.ciph_modulus
        self.generate_encoding_matrices()

    def generate_encoding_matrices(self):
        """Generates encoding matrices for coeff_to_slot and slot_to_coeff operations.
        """
        num_slots = self.poly_degree // 2
        prim_root = math.e ** (math.pi * 1j / 2 / num_slots)
        primitive_roots = [prim_root] * num_slots
        for i in range(1, num_slots):
            primitive_roots[i] = primitive_roots[i - 1] ** 5

        # Compute matrices for slot to coeff transformation.
        self.encoding_mat0 = [[1] * num_slots for _ in range(num_slots)]
        self.encoding_mat1 = [[1] * num_slots for _ in range(num_slots)]

        for i in range(num_slots):
            for k in range(1, num_slots):
                self.encoding_mat0[i][k] = self.encoding_mat0[i][k - 1] * primitive_roots[i]

        for i in range(num_slots):
            self.encoding_mat1[i][0] = self.encoding_mat0[i][-1] * primitive_roots[i]

        for i in range(num_slots):
            for k in range(1, num_slots):
                self.encoding_mat1[i][k] = self.encoding_mat1[i][k - 1] * primitive_roots[i]

        # Compute matrices for coeff to slot transformation.
        self.encoding_mat_transpose0 = util.matrix_operations.transpose_matrix(self.encoding_mat0)
        self.encoding_mat_conj_transpose0 = util.matrix_operations.conjugate_matrix(self.encoding_mat_transpose0)
        self.encoding_mat_transpose1 = util.matrix_operations.transpose_matrix(self.encoding_mat1)
        self.encoding_mat_conj_transpose1 = util.matrix_operations.conjugate_matrix(self.encoding_mat_transpose1)
