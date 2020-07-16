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

## Samples a random complex vector of length n
def sample_random_complex_vector(n):
    l = [0] * n
    for i in range(n):
        
        a = random.random()
        b = random.random()
        l[i] = a + b * 1j
    return l

## Samples a random real vector of length n
def sample_random_real_vector(n):
    l = [0] * n
    for i in range(n):
        
        a = random.random()
        l[i] = a
    return l