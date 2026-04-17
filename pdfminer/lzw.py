import logging
from collections.abc import Iterator
from io import BytesIO
from typing import BinaryIO, cast

from pdfminer.pdfexceptions import PDFEOFError, PDFException

logger = logging.getLogger(__name__)


class CorruptDataError(PDFException):
    pass


class LZWDecoder:
    def __init__(self, fp: BinaryIO) -> None:
        self.fp = fp
        self.buff = 0
        self.bpos = 8
        self.nbits = 9
        # NB: self.table stores None only in indices 256 and 257
        self.table: list[bytes | None] = []
        self.prevbuf: bytes | None = None

    def readbits(self, bits: int) -> int:
        pass

    def feed(self, code: int) -> bytes:
        pass

    def run(self) -> Iterator[bytes]:
        pass


def lzwdecode(data: bytes) -> bytes:
    pass
