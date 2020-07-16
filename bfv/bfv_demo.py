"""Demo of BFV without bootstrapping."""

from bfv.bfv_decryptor import BFVDecryptor
from bfv.bfv_encryptor import BFVEncryptor
from bfv.bfv_evaluator import BFVEvaluator
from bfv.bfv_key_generator import BFVKeyGenerator
from bfv.bfv_parameters import BFVParameters
from util.ciphertext import Ciphertext
from util.plaintext import Plaintext
from util.polynomial import Polynomial
from util.public_key import PublicKey
from util.random_sample import sample_uniform
from util.secret_key import SecretKey

def main():
    '''
    We demonstrate performing simple computations (a polynomial
    evaluation) on encrypted integers using the BFV encryption scheme.

    The first task is to set up an instance of the Parameters class. There are
    three encryption parameters that are necessary to set:

        - poly_degree (degree of polynomial modulus);
        - plain_modulus (plaintext modulus);
        - ciph_modulus (ciphertext modulus).
    '''

    '''
    The first parameter we set is the degree of the `polynomial modulus'. This
    must be a positive power of 2, representing the degree of a power-of-two
    cyclotomic polynomial.

    Larger poly_degree makes ciphertext sizes larger and all operations
    slower, but enables more complicated encrypted computations. Recommended
    values are 1024, 2048, 4096, 8192, 16384, 32768, but it is also possible
    to go beyond this range.

    In this example we use a relatively small polynomial modulus. Anything
    smaller than this will enable only very restricted encrypted computations.
    '''
    poly_degree = 2048

    '''
    The plaintext modulus can be any positive integer, even though here we take
    it to be a power of two. In fact, in many cases one might instead want it
    to be a prime number; we will see this in later examples. The plaintext
    modulus determines the size of the plaintext data type and the consumption
    of noise budget in multiplications. Thus, it is essential to try to keep the
    plaintext data type as small as possible for best performance. The noise
    budget in a freshly encrypted ciphertext is

        ~ log2(coeff_modulus/plain_modulus) (bits)

    and the noise budget consumption in a homomorphic multiplication is of the
    form log2(plain_modulus) + (other terms).

    The plaintext modulus is specific to the BFV scheme, and cannot be set when
    using the CKKS scheme.
    '''
    plain_modulus = 256

    '''
    Next we set the ciphertext modulus (ciph_modulus). This
    parameter is a large integer, which is a product of distinct prime numbers,
    each up to 60 bits in size. The
    bit-length of ciph_modulus means the sum of the bit-lengths of its prime
    factors.

    A larger ciph_modulus implies more encrypted
    computation capabilities. However, an upper bound for the total bit-length
    of the ciph_modulus is determined by the poly_modulus_degree, as follows:

        +----------------------------------------------------+
        | poly_modulus_degree | max coeff_modulus bit-length |
        +---------------------+------------------------------+
        | 1024                | 27                           |
        | 2048                | 54                           |
        | 4096                | 109                          |
        | 8192                | 218                          |
        | 16384               | 438                          |
        | 32768               | 881                          |
        +---------------------+------------------------------+
    '''
    ciph_modulus = 0x3fffffff000001

    params = Parameters(poly_degree, plain_modulus, ciph_modulus)

    # Print the parameters that we have chosen.
    params.print_parameters()

    print("~~~~~~ A naive way to calculate 2(x^2+1)(x+1)^2. ~~~~~~")

    '''
    We are now ready to generate the secret and public keys. For this purpose
    we need an instance of the KeyGenerator class. Constructing a KeyGenerator
    automatically generates the public and secret key, which can immediately be
    read to local variables.

    This also generates a relinearization key, which is used after a homomorphic
    multiplication occurs.
    '''
    key_generator = BFVKeyGenerator(params)
    public_key = key_generator.public_key
    secret_key = key_generator.secret_key
    relin_key = key_generator.relin_key

    '''
    To be able to encrypt we need to construct an instance of Encryptor. Note
    that the Encryptor only requires the public key, as expected.
    '''
    encryptor = BFVEncryptor(params, public_key)

    '''
    Computations on the ciphertexts are performed with the Evaluator class. In
    a real use-case the Evaluator would not be constructed by the same party
    that holds the secret key.
    '''
    evaluator = BFVEvaluator(params)

    '''
    We will of course want to decrypt our results to verify that everything worked,
    so we need to also construct an instance of Decryptor. Note that the Decryptor
    requires the secret key.
    '''
    decryptor = BFVDecryptor(params, secret_key)

    '''
    As an example, we evaluate the degree 4 polynomial

        2x^4 + 4x^3 + 4x^2 + 4x + 2

    over an encrypted x = 6. The coefficients of the polynomial can be considered
    as plaintext inputs, as we will see below. The computation is done modulo the
    plain_modulus 256.

    To get started, we create a plaintext containing the constant 6. For the
    plaintext element we use a constructor that takes the desired polynomial as
    a string with coefficients represented as hexadecimal numbers.
    '''

def run_test_add(self, m1, m2):
    p1 = Polynomial(self.degree, m1)
    p2 = Polynomial(self.degree, m2)
    plain1 = Plaintext(p1)
    plain2 = Plaintext(p2)
    plain_sum = Plaintext(p1.add(p2, self.plain_modulus))
    ciph1 = self.encryptor.encrypt(plain1)
    ciph2 = self.encryptor.encrypt(plain2)
    ciph_sum = self.evaluator.add(ciph1, ciph2)
    decrypted_sum = self.decryptor.decrypt(ciph_sum)
    self.assertEqual(str(plain_sum), str(decrypted_sum))

def test_add_01(self):
    m1 = sample_uniform(0, self.plain_modulus, self.degree)
    m2 = sample_uniform(0, self.plain_modulus, self.degree)
    self.run_test_add(m1, m2)

def run_test_multiply(self, m1, m2):
    p1 = Polynomial(self.degree, m1)
    p2 = Polynomial(self.degree, m2)
    plain1 = Plaintext(p1)
    plain2 = Plaintext(p2)
    plain_prod = Plaintext(p1.multiply(p2, self.plain_modulus))
    ciph1 = self.encryptor.encrypt(plain1)
    ciph2 = self.encryptor.encrypt(plain2)
    ciph_prod = self.evaluator.multiply(ciph1, ciph2, self.relin_key)
    decrypted_prod = self.decryptor.decrypt(ciph_prod)
    self.assertEqual(str(plain_prod), str(decrypted_prod))   

def test_multiply_01(self):
    m1 = sample_uniform(0, self.plain_modulus, self.degree)
    m2 = sample_uniform(0, self.plain_modulus, self.degree)
    self.run_test_multiply(m1, m2)

if __name__ == '__main__':
    main()
