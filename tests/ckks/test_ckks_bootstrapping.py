"""Tests for ckks_evaluator.py for bootstrapping."""

import math
import cmath
import os
import unittest

from ckks.ckks_decryptor import CKKSDecryptor
from ckks.ckks_encoder import CKKSEncoder
from ckks.ckks_encryptor import CKKSEncryptor
from ckks.ckks_evaluator import CKKSEvaluator
from ckks.ckks_key_generator import CKKSKeyGenerator
from ckks.ckks_parameters import CKKSParameters
from tests.helper import check_complex_vector_approx_eq
from util.plaintext import Plaintext
import util.matrix_operations as mat
from util.random_sample import sample_random_complex_vector

TEST_DIRECTORY = os.path.dirname(__file__)

def taylor_exp(vec, const, num_iterations, taylor_coeff=7):
    """Evaluates exponential function using its Taylor series.

    Takes a vector and computes e^(const * vector) using its Taylor series. To increase precision,
    we first compute e^(const * vector / 2^num_iterations), and square it num_iterations times. This
    way the argument to the exponential function is small, making its Taylor series more accurate.

    Args:
        vec (list (complex)): List of numbers to compute exp on.
        const (complex): Constant to multiply argument by.
        num_iterations (int): Number of times to square by.
        taylor_coeff (int): Last Taylor series exponent to truncate by.

    Returns:
        List of numbers representing e^(const * vector).
    """
    taylor_exp_vec = [0] * len(vec)

    for i, val in enumerate(vec):
        # Compute argument to input to exponent.
        argument = val * const / (2 ** num_iterations)

        # Compute Taylor series of exp function.
        power = 1
        factorial = 1
        for j in range(taylor_coeff + 1):
            taylor_exp_vec[i] += power / factorial
            power *= argument
            factorial *= j + 1

        # Square repeatedly.
        for _ in range(num_iterations):
            taylor_exp_vec[i] = taylor_exp_vec[i] ** 2

    return taylor_exp_vec

class TestBootstrappingMethods(unittest.TestCase):
    def setUp(self):
        self.degree = 16
        self.ciph_modulus = 1 << 600
        self.big_modulus = 1 << 1200
        self.scaling_factor = 1 << 30

        self.params = CKKSParameters(poly_degree=self.degree,
                                     ciph_modulus=self.ciph_modulus,
                                     big_modulus=self.big_modulus,
                                     scaling_factor=self.scaling_factor)
        self.key_generator = CKKSKeyGenerator(self.params)
        public_key = self.key_generator.public_key
        secret_key = self.key_generator.secret_key
        self.relin_key = self.key_generator.relin_key
        self.encoder = CKKSEncoder(self.params)
        self.encryptor = CKKSEncryptor(self.params, public_key, secret_key)
        self.decryptor = CKKSDecryptor(self.params, secret_key)
        self.evaluator = CKKSEvaluator(self.params)

    def run_test_coeff_to_slot(self, message):
        num_slots = len(message)
        plain = self.encoder.encode(message, self.scaling_factor)
        plain_ans1 = mat.scalar_multiply(plain.poly.coeffs[:num_slots], 1 / self.scaling_factor)
        plain_ans2 = mat.scalar_multiply(plain.poly.coeffs[num_slots:], 1 / self.scaling_factor)
        ciph = self.encryptor.encrypt(plain)

        rot_keys = {}
        for i in range(num_slots):
            rot_keys[i] = self.key_generator.generate_rot_key(i)

        conj_key = self.key_generator.generate_conj_key()

        ciph1, ciph2 = self.evaluator.coeff_to_slot(ciph, rot_keys, conj_key, self.encoder)
        decrypted_1 = self.decryptor.decrypt(ciph1)
        decrypted_1 = self.encoder.decode(decrypted_1)
        decrypted_2 = self.decryptor.decrypt(ciph2)
        decrypted_2 = self.encoder.decode(decrypted_2)

        check_complex_vector_approx_eq(plain_ans1, decrypted_1, error=0.01)
        check_complex_vector_approx_eq(plain_ans2, decrypted_2, error=0.01)

    def run_test_slot_to_coeff(self, message):
        num_slots = len(message)
        plain = self.encoder.encode(message, self.scaling_factor)
        ciph = self.encryptor.encrypt(plain)

        rot_keys = {}
        for i in range(num_slots):
            rot_keys[i] = self.key_generator.generate_rot_key(i)

        conj_key = self.key_generator.generate_conj_key()

        ciph1, ciph2 = self.evaluator.coeff_to_slot(ciph, rot_keys, conj_key, self.encoder)
        decrypted_1 = self.decryptor.decrypt(ciph1)
        decrypted_1 = self.encoder.decode(decrypted_1)
        decrypted_2 = self.decryptor.decrypt(ciph2)
        decrypted_2 = self.encoder.decode(decrypted_2)

        ciph_ans = self.evaluator.slot_to_coeff(ciph1, ciph2, rot_keys, self.encoder)
        decrypted = self.decryptor.decrypt(ciph_ans)
        plain_ans1 = mat.scalar_multiply(decrypted.poly.coeffs[:num_slots],
                                         1 / decrypted.scaling_factor)
        plain_ans2 = mat.scalar_multiply(decrypted.poly.coeffs[num_slots:],
                                         1 / decrypted.scaling_factor)

        prim_root = math.e ** (math.pi * 1j / 2 / num_slots)
        primitive_roots = [prim_root] * (num_slots)
        for i in range(1, num_slots):
            primitive_roots[i] = primitive_roots[i - 1] ** 5

        mat_0 = [[1] * (num_slots) for _ in range(num_slots)]
        mat_1 = [[1] * (num_slots) for _ in range(num_slots)]

        for i in range(num_slots):
            for k in range(1, num_slots):
                mat_0[i][k] = mat_0[i][k - 1] * primitive_roots[i]

        for i in range(num_slots):
            mat_1[i][0] = mat_0[i][-1] * primitive_roots[i]

        for i in range(num_slots):
            for k in range(1, num_slots):
                mat_1[i][k] = mat_1[i][k - 1] * primitive_roots[i]

        plain_1 = mat.matrix_vector_multiply(mat_0, decrypted_1)
        plain_2 = mat.matrix_vector_multiply(mat_1, decrypted_2)
        new_plain = [plain_1[i] + plain_2[i] for i in range(num_slots)]

        encoded = self.encoder.encode(new_plain, self.scaling_factor)
        plain_check1 = mat.scalar_multiply(encoded.poly.coeffs[:num_slots],
                                           1 / decrypted.scaling_factor)
        plain_check2 = mat.scalar_multiply(encoded.poly.coeffs[num_slots:],
                                           1 / decrypted.scaling_factor)

        decrypted = self.encoder.decode(decrypted)
        check_complex_vector_approx_eq(decrypted, new_plain, error=0.001)

        check_complex_vector_approx_eq(plain_check1, plain_ans1, error=0.001)
        check_complex_vector_approx_eq(plain_check2, plain_ans2, error=0.001)
        check_complex_vector_approx_eq(decrypted_1, plain_ans1, error=0.001)
        check_complex_vector_approx_eq(decrypted_2, plain_ans2, error=0.001)

        check_complex_vector_approx_eq(message, new_plain, error=0.001)

    def run_test_exp(self, message):
        plain = self.encoder.encode(message, self.scaling_factor)
        const = 2 * math.pi
        plain_exp = taylor_exp(message, const, num_iterations=5)
        ciph = self.encryptor.encrypt(plain)
        ciph_exp = self.evaluator.exp(ciph, const, self.relin_key, self.encoder)
        decrypted_exp = self.decryptor.decrypt(ciph_exp)
        decrypted_exp = self.encoder.decode(decrypted_exp)
        check_complex_vector_approx_eq(plain_exp, decrypted_exp, error=0.1)

    def test_coeff_to_slot_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        self.run_test_coeff_to_slot(vec)

    def test_slot_to_coeff_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        self.run_test_slot_to_coeff(vec)

    def test_exp_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        self.run_test_exp(vec)

class TestBootstrapping(unittest.TestCase):

    def setUp(self):
        self.degree = 16
        self.ciph_modulus = 1 << 40
        self.big_modulus = 1 << 1200
        self.scaling_factor = 1 << 30

        self.params = CKKSParameters(poly_degree=self.degree,
                                     ciph_modulus=self.ciph_modulus,
                                     big_modulus=self.big_modulus,
                                     scaling_factor=self.scaling_factor)
        self.key_generator = CKKSKeyGenerator(self.params)
        public_key = self.key_generator.public_key
        secret_key = self.key_generator.secret_key
        self.relin_key = self.key_generator.relin_key
        self.encoder = CKKSEncoder(self.params)
        self.encryptor = CKKSEncryptor(self.params, public_key, secret_key)
        self.decryptor = CKKSDecryptor(self.params, secret_key)
        self.evaluator = CKKSEvaluator(self.params)

        self.num_taylor_exp_iterations = 12

    def run_test_bootstrap_steps(self, message):

        # ------------------- SETUP -------------------- #
        num_slots = self.degree // 2
        plain = self.encoder.encode(message, self.scaling_factor)
        ciph = self.encryptor.encrypt(plain)

        rot_keys = {}
        for i in range(num_slots):
            rot_keys[i] = self.key_generator.generate_rot_key(i)

        conj_key = self.key_generator.generate_conj_key()

        # Raise modulus.
        old_modulus = ciph.modulus
        old_scaling_factor = self.scaling_factor
        self.evaluator.raise_modulus(ciph)

        print(message)
        print("-----------------------")
        print(plain.poly.coeffs)
        plain = self.decryptor.decrypt(ciph)
        test_plain = Plaintext(plain.poly.mod_small(self.ciph_modulus), self.scaling_factor)
        print("-------- TEST --------")
        print(test_plain.poly.coeffs)
        print(self.encoder.decode(test_plain))

        print("---------- BIT SIZE ------------")
        print(math.log(self.scaling_factor, 2))
        print(math.log(self.ciph_modulus, 2))
        print(math.log(abs(plain.poly.coeffs[0]), 2))
        print("---------- MOD ------------")
        print(plain.poly.coeffs[0])
        print(plain.poly.coeffs[0] > self.ciph_modulus / 2)
        print(math.sin(2 * math.pi * plain.poly.coeffs[0] / self.ciph_modulus))
        print(2 * math.pi * (plain.p.coeffs[0] % self.ciph_modulus) / self.ciph_modulus)
        print(math.sin(2 * math.pi * plain.poly.coeffs[0] / self.ciph_modulus) * self.ciph_modulus / 2 / math.pi)
        print(plain.poly.coeffs[0] % self.ciph_modulus)

        # Coeff to slot.
        ciph0, ciph1 = self.evaluator.coeff_to_slot(ciph, rot_keys, conj_key, self.encoder)
        plain_slots0 = [plain.poly.coeffs[i] / self.evaluator.scaling_factor for i in range(num_slots)]
        plain_slots1 = [plain.poly.coeffs[i] / self.evaluator.scaling_factor
                        for i in range(num_slots, 2 * num_slots)]
        print("----- COEFF TO SLOT -------")
        print(plain_slots0)
        print(plain_slots1)
        decrypted0 = self.decryptor.decrypt(ciph0)
        decoded0 = self.encoder.decode(decrypted0)
        decrypted1 = self.decryptor.decrypt(ciph1)
        decoded1 = self.encoder.decode(decrypted1)
        check_complex_vector_approx_eq(decoded0, plain_slots0, error_message="COEFF TO SLOT FAILED")
        check_complex_vector_approx_eq(decoded1, plain_slots1, error_message="COEFF TO SLOT FAILED")

        # Exponentiate.
        const = self.evaluator.scaling_factor / old_modulus * 2 * math.pi * 1j
        ciph_exp0 = self.evaluator.exp(ciph0, const, self.relin_key, self.encoder)
        ciph_neg_exp0 = self.evaluator.conjugate(ciph_exp0, conj_key)
        ciph_exp1 = self.evaluator.exp(ciph1, const, self.relin_key, self.encoder)
        ciph_neg_exp1 = self.evaluator.conjugate(ciph_exp1, conj_key)

        pre_exp0 = [plain_slots0[i] * const for i in range(num_slots)]
        pre_exp1 = [plain_slots1[i] * const for i in range(num_slots)]
        exp0 = [cmath.exp(pre_exp0[i]) for i in range(num_slots)]
        exp1 = [cmath.exp(pre_exp1[i]) for i in range(num_slots)]
        taylor_exp0 = taylor_exp(plain_slots0, const, num_iterations=self.num_taylor_exp_iterations)
        taylor_exp1 = taylor_exp(plain_slots1, const, num_iterations=self.num_taylor_exp_iterations)
        neg_exp0 = [cmath.exp(-pre_exp0[i]) for i in range(num_slots)]
        neg_exp1 = [cmath.exp(-pre_exp1[i]) for i in range(num_slots)]
        print("----- EXP -------")
        print("----- argument -----")
        print(pre_exp0)
        print(pre_exp1)
        print("---- actual exp ------")
        print(exp0)
        print(exp1)
        print("---- taylor series exp ----")
        print(taylor_exp0)
        print(taylor_exp1)
        print("---- actual negative exp -----")
        print(neg_exp0)
        print(neg_exp1)

        decrypted_exp0 = self.decryptor.decrypt(ciph_exp0)
        decoded_exp0 = self.encoder.decode(decrypted_exp0)
        decrypted_neg_exp0 = self.decryptor.decrypt(ciph_neg_exp0)
        decoded_neg_exp0 = self.encoder.decode(decrypted_neg_exp0)
        decrypted_exp1 = self.decryptor.decrypt(ciph_exp1)
        decoded_exp1 = self.encoder.decode(decrypted_exp1)
        decrypted_neg_exp1 = self.decryptor.decrypt(ciph_neg_exp1)
        decoded_neg_exp1 = self.encoder.decode(decrypted_neg_exp1)
        check_complex_vector_approx_eq(decoded_exp0, exp0, error=0.001, error_message="EXP FAILED")
        check_complex_vector_approx_eq(decoded_exp1, exp1, error=0.001, error_message="EXP FAILED")
        check_complex_vector_approx_eq(decoded_neg_exp0, neg_exp0, error=0.001,
                                       error_message="EXP FAILED")
        check_complex_vector_approx_eq(decoded_neg_exp1, neg_exp1, error=0.001,
                                       error_message="EXP FAILED")

        # Compute sine.
        ciph_sin0 = self.evaluator.subtract(ciph_exp0, ciph_neg_exp0)
        ciph_sin1 = self.evaluator.subtract(ciph_exp1, ciph_neg_exp1)

        sin0 = [(exp0[i] - neg_exp0[i])/ 2 / 1j for i in range(num_slots)]
        sin1 = [(exp1[i] - neg_exp1[i]) / 2 / 1j for i in range(num_slots)]

        # Scale sine.
        const = self.evaluator.create_complex_constant_plain(
            old_modulus / self.evaluator.scaling_factor * 0.25 / math.pi / 1j, self.encoder)
        ciph0 = self.evaluator.multiply_plain(ciph_sin0, const)
        ciph1 = self.evaluator.multiply_plain(ciph_sin1, const)
        ciph0 = self.evaluator.rescale(ciph0, self.evaluator.scaling_factor)
        ciph1 = self.evaluator.rescale(ciph1, self.evaluator.scaling_factor)

        print("----- SIN -------")
        print(sin0)
        print(sin1)
        sin_check0 = [cmath.sin(pre_exp0[i]) for i in range(num_slots)]
        sin_check1 = [cmath.sin(pre_exp1[i]) for i in range(num_slots)]
        print(sin_check0)
        print(sin_check1)

        scaled_sin0 = [sin0[i] * self.ciph_modulus / self.evaluator.scaling_factor / 2 / math.pi
                       for i in range(num_slots)]
        scaled_sin1 = [sin1[i] * self.ciph_modulus / self.evaluator.scaling_factor / 2 / math.pi
                       for i in range(num_slots)]
        print("----- SCALED SIN -------")
        print(scaled_sin0)
        print(scaled_sin1)
        expected_slots0 = [(plain.poly.coeffs[i] % self.ciph_modulus) / self.evaluator.scaling_factor
                           for i in range(num_slots)]
        expected_slots1 = [(plain.poly.coeffs[i] % self.ciph_modulus) / self.evaluator.scaling_factor
                           for i in range(num_slots, 2 * num_slots)]
        print(expected_slots0)
        print(expected_slots1)

        decrypted0 = self.decryptor.decrypt(ciph0)
        decoded0 = self.encoder.decode(decrypted0)
        decrypted1 = self.decryptor.decrypt(ciph1)
        decoded1 = self.encoder.decode(decrypted1)
        check_complex_vector_approx_eq(decoded0, scaled_sin0, error=0.1, error_message="SIN FAILED")
        check_complex_vector_approx_eq(decoded1, scaled_sin1, error=0.1, error_message="SIN FAILED")

        # Slot to coeff.
        ciph = self.evaluator.slot_to_coeff(ciph0, ciph1, rot_keys, self.encoder)

        # Reset scaling factor.
        self.scaling_factor = old_scaling_factor
        ciph.scaling_factor = self.scaling_factor

        new_plain = self.decryptor.decrypt(ciph)
        new_plain = self.encoder.decode(new_plain)\

        print("-------- ANSWER -------")
        print(new_plain)
        check_complex_vector_approx_eq(message, new_plain, error=0.05,
                                       error_message="FINAL CHECK FAILED")

        print("------------ BOOTSTRAPPING MODULUS CHANGES -------------")
        print("Old modulus q: %d bits" % (int(math.log(old_modulus, 2))))
        print("Raised modulus Q_0: %d bits" % (int(math.log(self.big_modulus, 2))))
        print("Final modulus Q_1: %d bits" % (int(math.log(ciph.modulus, 2))))

    def run_test_bootstrap(self, message):
        num_slots = len(message)
        plain = self.encoder.encode(message, self.scaling_factor)
        ciph = self.encryptor.encrypt(plain)

        rot_keys = {}
        for i in range(num_slots):
            rot_keys[i] = self.key_generator.generate_rot_key(i)

        conj_key = self.key_generator.generate_conj_key()

        ciph, new_ciph = self.evaluator.bootstrap(ciph, rot_keys, conj_key, self.relin_key,
                                                  self.encoder)
        new_plain = self.decryptor.decrypt(new_ciph)
        new_plain = self.encoder.decode(new_plain)
        check_complex_vector_approx_eq(message, new_plain, error=0.05)

    def test_bootstrap_01(self):
        vec = sample_random_complex_vector(self.degree // 2)
        try:
            self.run_test_bootstrap(vec)
        except Exception:
            self.run_test_bootstrap_steps(vec)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
