import math
from collections import Counter


def calculate_entropy(value: str) -> float:
    """
    Calculate the Shannon entropy of a string.

    Higher entropy usually means the characters
    are less predictable and more random-looking.
    """

    if not value:
        return 0.0

    character_counts = Counter(value)

    length = len(value)

    entropy = 0.0

    for count in character_counts.values():

        probability = count / length

        entropy -= probability * math.log2(probability)

    return entropy