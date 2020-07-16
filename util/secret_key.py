"""A module to keep track of a secret key."""

class SecretKey:

    """An instance of a secret key.

    The secret key consists of one polynomials generated
    from key_generator.py.

    Attributes:
        s (Polynomial): Secret key.
    """

    def __init__(self, s):
        """Sets public key to given inputs.

        Args:
            s (Polynomial): Secret key.
        """
        self.s = s

    def __str__(self):
        """Represents secret key as a string.

        Returns:
            A string which represents the secret key.
        """
        return str(self.s)