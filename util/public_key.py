"""A module to keep track of a public key."""

class PublicKey:

    """An instance of a public key.

    The public key consists of a pair of polynomials generated
    from key_generator.py.

    Attributes:
        p0 (Polynomial): First element of public key.
        p1 (Polynomial): Second element of public key.
    """

    def __init__(self, p0, p1):
        """Sets public key to given inputs.

        Args:
            p0 (Polynomial): First element of public key.
            p1 (Polynomial): Second element of public key.
        """
        self.p0 = p0
        self.p1 = p1

    def __str__(self):
        """Represents PublicKey as a string.

        Returns:
            A string which represents the PublicKey.
        """
        return 'p0: ' + str(self.p0) + '\n + p1: ' + str(self.p1)