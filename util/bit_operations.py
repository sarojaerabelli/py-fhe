"""A module to perform bit operations.
"""
from math import log

def reverse_bits(value, width):
    """Reverses bits of an integer.

    Reverse bits of the given value with a specified bit width.
    For example, reversing the value 6 = 0b110 with a width of 5
    would result in reversing 0b00110, which becomes 0b01100 = 12.

    Args:
        value (int): Value to be reversed.   
        width (int): Number of bits to consider in reversal.

    Returns:
        The reversed int value of the input.
    """
    binary_val = '{:0{width}b}'.format(value, width=width)
    return int(binary_val[::-1], 2)

def bit_reverse_vec(values):
    """Reverses list by reversing the bits of the indices.

    Reverse indices of the given list.
    For example, reversing the list [0, 1, 2, 3, 4, 5, 6, 7] would become
    [0, 4, 2, 6, 1, 5, 3, 7], since 1 = 0b001 reversed is 0b100 = 4,
    3 = 0b011 reversed is 0b110 = 6.

    Args:
        values (list): List of values to be reversed. Length of list must be a power of two. 

    Returns:
        The reversed list based on indices.
    """
    result = [0] * len(values)
    for i in range(len(values)):
        result[i] = values[reverse_bits(i, int(log(len(values), 2)))]
    return result