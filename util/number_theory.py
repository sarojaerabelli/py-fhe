"""A module with number theory functions necessary for other functions.
"""

import random
import sympy

def mod_exp(val, exp, modulus):
    """Computes an exponent in a modulus.

    Raises val to power exp in the modulus without overflowing.

    Args:
        val (int): Value we wish to raise the power of.
        exp (int): Exponent.
        modulus (int): Modulus where computation is performed.

    Returns:
        A value raised to a power in a modulus.
    """
    return pow(int(val), int(exp), int(modulus))

def mod_inv(val, modulus):
    """Finds an inverse in a given prime modulus.

    Finds the inverse of val in the modulus.

    Args:
        val (int): Value to find the inverse of.
        modulus (int): Modulus where computation is performed.
            Note: MUST BE PRIME.

    Returns:
        The inverse of the given value in the modulus.
    """
    return mod_exp(val, modulus - 2, modulus)

def find_generator(modulus):
    """Finds a generator in the given modulus.

    Finds a generator, or primitive root, in the given prime modulus.

    Args:
        modulus (int): Modulus to find the generator in. Note: MUST
            BE PRIME.

    Returns:
        A generator, or primitive root in the given modulus.
    """
    return sympy.ntheory.primitive_root(modulus)

def root_of_unity(order, modulus):
    """Finds a root of unity in the given modulus.

    Finds a root of unity with the given order in the given prime modulus.

    Args:
        order (int): Order n of the root of unity (an nth root of unity).
        modulus (int): Modulus to find the root of unity in. Note: MUST BE
            PRIME

    Returns:
        A root of unity with the given order in the given modulus.
    """
    if ((modulus - 1) % order) != 0:
        raise ValueError('Must have order q | m - 1, where m is the modulus. \
            The values m = ' + str(modulus) + ' and q = ' + str(order) + ' do not satisfy this.')

    generator = find_generator(modulus)
    if generator is None:
        raise ValueError('No primitive root of unity mod m = ' + str(modulus))

    result = mod_exp(generator, (modulus - 1)//order, modulus)

    if result == 1:
        return root_of_unity(order, modulus)

    return result

def is_prime(number, num_trials=200):
    """Determines whether a number is prime.

    Runs the Miller-Rabin probabilistic primality test many times on the given number.

    Args:
        number (int): Number to perform primality test on.
        num_trials (int): Number of times to perform the Miller-Rabin test.

    Returns:
        True if number is prime, False otherwise.
    """
    if number < 2:
        return False
    if number != 2 and number % 2 == 0:
        return False

    # Find largest odd factor of n-1.
    exp = number - 1
    while exp % 2 == 0:
        exp //= 2

    for _ in range(num_trials):
        rand_val = int(random.SystemRandom().randrange(1, number))
        new_exp = exp
        power = pow(rand_val, new_exp, number)
        while new_exp != number - 1 and power != 1 and power != number - 1:
            power = (power * power) % number
            new_exp *= 2
        if power != number - 1 and new_exp % 2 == 0:
            return False

    return True
