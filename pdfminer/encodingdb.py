import logging
import re
from collections.abc import Iterable
from typing import ClassVar, cast

from pdfminer.glyphlist import glyphname2unicode
from pdfminer.latin_enc import ENCODING
from pdfminer.pdfexceptions import PDFKeyError
from pdfminer.psparser import PSLiteral

HEXADECIMAL = re.compile(r"[0-9a-fA-F]+")

log = logging.getLogger(__name__)


def name2unicode(name: str) -> str:
    """Converts Adobe glyph names to Unicode numbers.

    In contrast to the specification, this raises a KeyError instead of return
    an empty string when the key is unknown.
    This way the caller must explicitly define what to do
    when there is not a match.

    Reference:
    https://github.com/adobe-type-tools/agl-specification#2-the-mapping

    :returns unicode character if name resembles something,
    otherwise a KeyError
    """
    pass


def raise_key_error_for_invalid_unicode(unicode_digit: int) -> None:
    """Unicode values should not be in the range D800 through DFFF because
    that is used for surrogate pairs in UTF-16

    :raises KeyError if unicode digit is invalid
    """
    pass


class EncodingDB:
    std2unicode: ClassVar[dict[int, str]] = {}
    mac2unicode: ClassVar[dict[int, str]] = {}
    win2unicode: ClassVar[dict[int, str]] = {}
    pdf2unicode: ClassVar[dict[int, str]] = {}
    for name, std, mac, win, pdf in ENCODING:
        c = name2unicode(name)
        if std:
            std2unicode[std] = c
        if mac:
            mac2unicode[mac] = c
        if win:
            win2unicode[win] = c
        if pdf:
            pdf2unicode[pdf] = c

    encodings: ClassVar[dict[str, dict[int, str]]] = {
        "StandardEncoding": std2unicode,
        "MacRomanEncoding": mac2unicode,
        "WinAnsiEncoding": win2unicode,
        "PDFDocEncoding": pdf2unicode,
    }

    @classmethod
    def get_encoding(
        cls,
        name: str,
        diff: Iterable[object] | None = None,
    ) -> dict[int, str]:
        pass
