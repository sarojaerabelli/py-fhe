"""A module to keep track of a relinearization key."""

class BFVRelinKey:

    """An instance of a relinearization key.

    The relinearization key consists of a list of values, as specified
    in Version 1 of the BFV paper, generated in key_generator.py.

    Attributes:
        base (int): Base used in relinearization in Version 1.
        keys (list of tuples of Polynomials): List of elements in the
            relinearization key. Each element of the list is a pair of
            polynomials.
    """

    def __init__(self, base, keys):
        """Sets relinearization key to given inputs.

        Args:
            base (int): Base used for relinearization.
            keys (list of tuples of Polynomials): List of elements in the
                relinearization key.
        """
        self.base = base
        self.keys = keys

    def __str__(self):
        """Represents RelinKey as a string.

        Returns:
            A string which represents the RelinKey.
        """
        return 'Base: ' + str(self.base) + '\n' + str(self.keys)
