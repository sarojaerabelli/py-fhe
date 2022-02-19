"""A module to sample randomly from various distributions."""
import random

def sample_uniform(min_val, max_val, num_samples):
    """Samples from a uniform distribution.

    Samples num_samples integer values from the range [min, max)
    uniformly at random.

    Args:
        min_val (int): Minimum value (inclusive).
        max_val (int): Maximum value (exclusive).
        num_samples (int): Number of samples to be drawn.

    Returns:
        A list of randomly sampled values.
    """
    if num_samples == 1:
        #return random.SystemRandom().randrange(min_val, max_val)
        return random.randrange(min_val, max_val)
    #return [random.SystemRandom().randrange(min_val, max_val)
    #    for _ in range(num_samples)]
    return [random.randrange(min_val, max_val)
        for _ in range(num_samples)]


def sample_triangle(num_samples):
    """Samples from a discrete triangle distribution.

    Samples num_samples values from [-1, 0, 1] with probabilities
    [0.25, 0.5, 0.25], respectively.

    Args:
        num_samples (int): Number of samples to be drawn.

    Returns:
        A list of randomly sampled values.
    """
    sample = [0] * num_samples

    for i in range(num_samples):
        # r = random.SystemRandom().randrange(0, 4)
        r = random.randrange(0, 4)
        if r == 0: sample[i] = -1
        elif r == 1: sample[i] = 1
        else: sample[i] = 0
    return sample

def sample_hamming_weight_vector(length, hamming_weight):
    """Samples from a Hamming weight distribution.

    Samples uniformly from the set [-1, 0, 1] such that the
    resulting vector has exactly h nonzero values.

    Args:
        length (int): Length of resulting vector.
        hamming_weight (int): Hamming weight h of resulting vector.

    Returns:
        A list of randomly sampled values.
    """
    sample = [0] * length
    total_weight = 0

    while total_weight < hamming_weight:
        index = random.randrange(0, length)
        if sample[index] == 0:
            r = random.randint(0, 1)
            if r == 0: sample[index] = -1
            else: sample[index] = 1
            total_weight += 1

    return sample

def sample_random_complex_vector(length):
    """Samples a random complex vector,

    Samples a vector with elements of the form a + bi where a and b
    are chosen uniformly at random from the set [0, 1).

    Args:
        length (int): Length of vector.

    Returns:
        A list of randomly sampled complex values.
    """
    sample = [0] * length
    for i in range(length):   
        a = random.random()
        b = random.random()
        sample[i] = a + b * 1j
    return sample

def sample_random_real_vector(length):
    """Samples a random complex vector,

    Samples a vector with elements chosen uniformly at random from
    the set [0, 1).

    Args:
        length (int): Length of vector.

    Returns:
        A list of randomly sampled real values.
    """
    sample = [0] * length
    for i in range(length):
        sample[i] = random.random()
    return sample
