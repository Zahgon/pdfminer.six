#!/usr/bin/env python3
import contextlib
import io
import logging
import re
from collections.abc import Iterator
from typing import (
    Any,
    BinaryIO,
    Generic,
    TypeVar,
    Union,
)

from pdfminer import psexceptions, settings
from pdfminer.utils import choplist

log = logging.getLogger(__name__)


# Adding aliases for these exceptions for backwards compatibility
PSException = psexceptions.PSException
PSEOF = psexceptions.PSEOF
PSSyntaxError = psexceptions.PSSyntaxError
PSTypeError = psexceptions.PSTypeError
PSValueError = psexceptions.PSValueError


class PSObject:
    """Base class for all PS or PDF-related data types."""


class PSLiteral(PSObject):
    """A class that represents a PostScript literal.

    Postscript literals are used as identifiers, such as
    variable names, property names and dictionary keys.
    Literals are case sensitive and denoted by a preceding
    slash sign (e.g. "/Name")

    Note: Do not create an instance of PSLiteral directly.
    Always use PSLiteralTable.intern().
    """

    NameType = Union[str, bytes]

    def __init__(self, name: NameType) -> None:
        self.name = name

    def __repr__(self) -> str:
        name = self.name
        return f"/{name!r}"


class PSKeyword(PSObject):
    """A class that represents a PostScript keyword.

    PostScript keywords are a dozen of predefined words.
    Commands and directives in PostScript are expressed by keywords.
    They are also used to denote the content boundaries.

    Note: Do not create an instance of PSKeyword directly.
    Always use PSKeywordTable.intern().
    """

    def __init__(self, name: bytes) -> None:
        self.name = name

    def __repr__(self) -> str:
        name = self.name
        return f"/{name!r}"


_SymbolT = TypeVar("_SymbolT", PSLiteral, PSKeyword)


class PSSymbolTable(Generic[_SymbolT]):
    """A utility class for storing PSLiteral/PSKeyword objects.

    Interned objects can be checked its identity with "is" operator.
    """

    def __init__(self, klass: type[_SymbolT]) -> None:
        self.dict: dict[PSLiteral.NameType, _SymbolT] = {}
        self.klass: type[_SymbolT] = klass

    def intern(self, name: PSLiteral.NameType) -> _SymbolT:
        pass


PSLiteralTable = PSSymbolTable(PSLiteral)
PSKeywordTable = PSSymbolTable(PSKeyword)
LIT = PSLiteralTable.intern
KWD = PSKeywordTable.intern
KEYWORD_PROC_BEGIN = KWD(b"{")
KEYWORD_PROC_END = KWD(b"}")
KEYWORD_ARRAY_BEGIN = KWD(b"[")
KEYWORD_ARRAY_END = KWD(b"]")
KEYWORD_DICT_BEGIN = KWD(b"<<")
KEYWORD_DICT_END = KWD(b">>")


def literal_name(x: Any) -> str:
    pass


def keyword_name(x: Any) -> Any:
    pass


EOL = re.compile(rb"[\r\n]")
SPC = re.compile(rb"\s")
NONSPC = re.compile(rb"\S")
HEX = re.compile(rb"[0-9a-fA-F]")
END_LITERAL = re.compile(rb"[#/%\[\]()<>{}\s]")
END_HEX_STRING = re.compile(rb"[^\s0-9a-fA-F]")
HEX_PAIR = re.compile(rb"[0-9a-fA-F]{2}|.")
END_NUMBER = re.compile(rb"[^0-9]")
END_KEYWORD = re.compile(rb"[#/%\[\]()<>{}\s]")
END_STRING = re.compile(rb"[()\134]")
OCT_STRING = re.compile(rb"[0-7]")
ESC_STRING = {
    b"b": 8,
    b"t": 9,
    b"n": 10,
    b"f": 12,
    b"r": 13,
    b"(": 40,
    b")": 41,
    b"\\": 92,
}


PSBaseParserToken = Union[float, bool, PSLiteral, PSKeyword, bytes]


class PSBaseParser:
    """Most basic PostScript parser that performs only tokenization."""

    BUFSIZ = 4096

    def __init__(self, fp: BinaryIO) -> None:
        self.fp = fp
        self.eof = False
        self.seek(0)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.fp!r}, bufpos={self.bufpos}>"

    def flush(self) -> None:
        pass

    def seek(self, pos: int) -> None:
        """Seeks the parser to the given position."""
        pass

    def fillbuf(self) -> bool:
        pass

    def nextline(self) -> tuple[int, bytes]:
        """Fetches a next line that ends either with \\r or \\n."""
        pass

    def revreadlines(self) -> Iterator[bytes]:
        """Fetches a next line backward.

        This is used to locate the trailers at the end of a file.
        """
        pass

    def _parse_main(self, s: bytes, i: int) -> int:
        pass

    def _add_token(self, obj: PSBaseParserToken) -> None:
        pass

    def _parse_comment(self, s: bytes, i: int) -> int:
        pass

    def _parse_literal(self, s: bytes, i: int) -> int:
        pass

    def _parse_literal_hex(self, s: bytes, i: int) -> int:
        pass

    def _parse_number(self, s: bytes, i: int) -> int:
        pass

    def _parse_float(self, s: bytes, i: int) -> int:
        pass

    def _parse_keyword(self, s: bytes, i: int) -> int:
        pass

    def _parse_string(self, s: bytes, i: int) -> int:
        pass

    def _parse_string_1(self, s: bytes, i: int) -> int:
        """Parse literal strings

        PDF Reference 3.2.3
        """
        pass

    def _parse_wopen(self, s: bytes, i: int) -> int:
        pass

    def _parse_wclose(self, s: bytes, i: int) -> int:
        pass

    def _parse_hexstring(self, s: bytes, i: int) -> int:
        pass

    def nexttoken(self) -> tuple[int, PSBaseParserToken]:
        pass


# Stack slots may by occupied by any of:
#  * the name of a literal
#  * the PSBaseParserToken types
#  * list (via KEYWORD_ARRAY)
#  * dict (via KEYWORD_DICT)
#  * subclass-specific extensions (e.g. PDFStream, PDFObjRef) via ExtraT
ExtraT = TypeVar("ExtraT")
PSStackType = Union[
    str, float, bool, PSLiteral, bytes, list[Any], dict[Any, Any], ExtraT
]
PSStackEntry = tuple[int, PSStackType[ExtraT]]


class PSStackParser(PSBaseParser, Generic[ExtraT]):
    def __init__(self, fp: BinaryIO) -> None:
        PSBaseParser.__init__(self, fp)
        self.reset()

    def reset(self) -> None:
        pass

    def seek(self, pos: int) -> None:
        pass

    def push(self, *objs: PSStackEntry[ExtraT]) -> None:
        pass

    def pop(self, n: int) -> list[PSStackEntry[ExtraT]]:
        pass

    def popall(self) -> list[PSStackEntry[ExtraT]]:
        pass

    def add_results(self, *objs: PSStackEntry[ExtraT]) -> None:
        pass

    def start_type(self, pos: int, type: str) -> None:
        pass

    def end_type(self, type: str) -> tuple[int, list[PSStackType[ExtraT]]]:
        pass

    def do_keyword(self, pos: int, token: PSKeyword) -> None:
        pass

    def nextobject(self) -> PSStackEntry[ExtraT]:
        """Yields a list of objects.

        Arrays and dictionaries are represented as Python lists and
        dictionaries.

        :return: keywords, literals, strings, numbers, arrays and dictionaries.
        """
        pass
