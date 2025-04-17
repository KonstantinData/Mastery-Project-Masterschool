import numpy as np

words = ["data", "travel", "AI", "analytics", "code", "Python", "map"]


def filter_and_uppercase(words):
    return [word.upper() for word in words if len(word) >= 5]


# Ausgabe
print(filter_and_uppercase(words))
