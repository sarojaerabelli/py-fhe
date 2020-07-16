"""A module to keep track of a rotation key."""

class RotationKey:

    """An instance of a rotation key.

    The rotation key consists of a value determined by the rotation value r.

    Attributes:
        rotation (int): Rotation value r.
        key (PublicKey): Key values.
    """

    def __init__(self, r, key):
        """Sets rotation key to given inputs.

        Args:
            r (int): Value to be rotated by.
            key (PublicKey): Key.
        """
        self.rotation = r
        self.key = key

    def __str__(self):
        """Represents RotationKey as a string.

        Returns:
            A string which represents the RotationKey.
        """
        return 'Rotation: ' + str(self.rotation) + '\nr0: ' + str(self.key.p0) + '\nr1: ' + str(self.key.p1)
