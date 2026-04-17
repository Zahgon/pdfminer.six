"""Adobe character mapping (CMap) support.

CMaps provide the mapping between character codes and Unicode
code-points to character ids (CIDs).

More information is available on:

  https://github.com/adobe-type-tools/cmap-resources

"""

import contextlib
import gzip
import json
import logging
import os
import os.path
import struct
import sys
from collections.abc import Iterable, Iterator, MutableMapping
from typing import (
    Any,
    BinaryIO,
    ClassVar,
    TextIO,
    Union,
    cast,
)

from pdfminer.encodingdb import name2unicode
from pdfminer.pdfexceptions import PDFException, PDFTypeError
from pdfminer.psexceptions import PSEOF, PSSyntaxError
from pdfminer.psparser import KWD, PSKeyword, PSLiteral, PSStackParser, literal_name
from pdfminer.utils import choplist, nunpack

log = logging.getLogger(__name__)


class CMapError(PDFException):
    pass


class CMapBase:
    debug = 0

    def __init__(self, **kwargs: object) -> None:
        self.attrs: MutableMapping[str, object] = kwargs.copy()

    def is_vertical(self) -> bool:
        pass

    def set_attr(self, k: str, v: object) -> None:
        pass

    def add_code2cid(self, code: str, cid: int) -> None:
        pass

    def add_cid2unichr(self, cid: int, code: PSLiteral | bytes | int) -> None:
        pass

    def use_cmap(self, cmap: "CMapBase") -> None:
        pass

    def decode(self, code: bytes) -> Iterable[int]:
        raise NotImplementedError


class CMap(CMapBase):
    def __init__(self, **kwargs: str | int) -> None:
        CMapBase.__init__(self, **kwargs)
        self.code2cid: dict[int, object] = {}

    def __repr__(self) -> str:
        return "<CMap: {}>".format(self.attrs.get("CMapName"))

    def use_cmap(self, cmap: CMapBase) -> None:
        pass

    def decode(self, code: bytes) -> Iterator[int]:
        pass

    def dump(
        self,
        out: TextIO = sys.stdout,
        code2cid: dict[int, object] | None = None,
        code: tuple[int, ...] = (),
    ) -> None:
        pass


class IdentityCMap(CMapBase):
    def decode(self, code: bytes) -> tuple[int, ...]:
        pass


class IdentityCMapByte(IdentityCMap):
    def decode(self, code: bytes) -> tuple[int, ...]:
        pass


class UnicodeMap(CMapBase):
    def __init__(self, **kwargs: str | int) -> None:
        CMapBase.__init__(self, **kwargs)
        self.cid2unichr: dict[int, str] = {}

    def __repr__(self) -> str:
        return "<UnicodeMap: {}>".format(self.attrs.get("CMapName"))

    def get_unichr(self, cid: int) -> str:
        pass

    def dump(self, out: TextIO = sys.stdout) -> None:
        pass


class IdentityUnicodeMap(UnicodeMap):
    def get_unichr(self, cid: int) -> str:
        """Interpret character id as unicode codepoint"""
        pass


class FileCMap(CMap):
    def add_code2cid(self, code: str, cid: int) -> None:
        pass


class FileUnicodeMap(UnicodeMap):
    def add_cid2unichr(self, cid: int, code: PSLiteral | bytes | int) -> None:
        pass


class PyCMap(CMap):
    def __init__(self, name: str, module: Any) -> None:
        super().__init__(CMapName=name)
        self.code2cid = module.CODE2CID
        if module.IS_VERTICAL:
            self.attrs["WMode"] = 1


class PyUnicodeMap(UnicodeMap):
    def __init__(self, name: str, module: Any, vertical: bool) -> None:
        super().__init__(CMapName=name)
        if vertical:
            self.cid2unichr = module.CID2UNICHR_V
            self.attrs["WMode"] = 1
        else:
            self.cid2unichr = module.CID2UNICHR_H


class CMapDB:
    _cmap_cache: ClassVar[dict[str, PyCMap]] = {}
    _umap_cache: ClassVar[dict[str, list[PyUnicodeMap]]] = {}

    class CMapNotFound(CMapError):
        pass

    @staticmethod
    def _convert_code2cid_keys(
        d: Union[dict[str, object], int],
    ) -> Union[dict[int, object], int]:
        """Recursively convert string keys to integers in CODE2CID dictionaries."""
        pass

    @classmethod
    def _load_data(cls, name: str) -> type[Any]:
        pass

    @classmethod
    def get_cmap(cls, name: str) -> CMapBase:
        pass

    @classmethod
    def get_unicode_map(cls, name: str, vertical: bool = False) -> UnicodeMap:
        pass


class CMapParser(PSStackParser[PSKeyword]):
    def __init__(self, cmap: CMapBase, fp: BinaryIO) -> None:
        PSStackParser.__init__(self, fp)
        self.cmap = cmap
        # some ToUnicode maps don't have "begincmap" keyword.
        self._in_cmap = True
        self._warnings: set[str] = set()

    def run(self) -> None:
        pass

    KEYWORD_BEGINCMAP = KWD(b"begincmap")
    KEYWORD_ENDCMAP = KWD(b"endcmap")
    KEYWORD_USECMAP = KWD(b"usecmap")
    KEYWORD_DEF = KWD(b"def")
    KEYWORD_BEGINCODESPACERANGE = KWD(b"begincodespacerange")
    KEYWORD_ENDCODESPACERANGE = KWD(b"endcodespacerange")
    KEYWORD_BEGINCIDRANGE = KWD(b"begincidrange")
    KEYWORD_ENDCIDRANGE = KWD(b"endcidrange")
    KEYWORD_BEGINCIDCHAR = KWD(b"begincidchar")
    KEYWORD_ENDCIDCHAR = KWD(b"endcidchar")
    KEYWORD_BEGINBFRANGE = KWD(b"beginbfrange")
    KEYWORD_ENDBFRANGE = KWD(b"endbfrange")
    KEYWORD_BEGINBFCHAR = KWD(b"beginbfchar")
    KEYWORD_ENDBFCHAR = KWD(b"endbfchar")
    KEYWORD_BEGINNOTDEFRANGE = KWD(b"beginnotdefrange")
    KEYWORD_ENDNOTDEFRANGE = KWD(b"endnotdefrange")

    def do_keyword(self, pos: int, token: PSKeyword) -> None:
        """ToUnicode CMaps

        See Section 5.9.2 - ToUnicode CMaps of the PDF Reference.
        """
        pass

    def _warn_once(self, msg: str) -> None:
        """Warn once for each unique message"""
        pass
