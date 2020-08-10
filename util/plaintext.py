"""A module to keep track of a plaintext."""

class Plaintext:

    """An instance of a plaintext.

    This is a wrapper class for a plaintext, which consists
    of one polynomial.

    Attributes:
        poly (Polynomial): Plaintext polynomial.
        scaling_factor (float): Scaling factor.
    """

    def __init__(self, poly, scaling_factor=None):
        """Sets plaintext to given polynomial.

        Args:
            poly (Polynomial): Plaintext polynomial.
            scaling_factor (float): Scaling factor.
        """
        self.poly = poly
        self.scaling_factor = scaling_factor

    def __str__(self):
        """Represents plaintext as a readable string.

        Returns:
            A string which represents the Plaintext.
        """
        return str(self.poly)