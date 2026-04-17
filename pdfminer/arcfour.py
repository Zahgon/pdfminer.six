"""Python implementation of Arcfour encryption algorithm.
See https://en.wikipedia.org/wiki/RC4
This code is in the public domain.

"""

from collections.abc import Sequence


class Arcfour:
    def __init__(self, key: Sequence[int]) -> None:
        # because Py3 range is not indexable
        s = list(range(256))
        j = 0
        klen = len(key)
        for i in range(256):
            j = (j + s[i] + key[i % klen]) % 256
            (s[i], s[j]) = (s[j], s[i])
        self.s = s
        (self.i, self.j) = (0, 0)

    def process(self, data: bytes) -> bytes:
        pass

    encrypt = decrypt = process
