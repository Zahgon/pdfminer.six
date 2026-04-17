import io
import logging
import zlib
from collections.abc import Iterable
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Protocol,
    cast,
)
from warnings import warn

from pdfminer import pdfexceptions, settings
from pdfminer.ascii85 import ascii85decode, asciihexdecode
from pdfminer.ccitt import ccittfaxdecode
from pdfminer.lzw import lzwdecode
from pdfminer.pdfexceptions import PDFKeyError
from pdfminer.psparser import LIT, PSObject
from pdfminer.runlength import rldecode
from pdfminer.utils import apply_png_predictor, apply_tiff_predictor

if TYPE_CHECKING:
    from pdfminer.pdfdocument import PDFDocument

logger = logging.getLogger(__name__)

LITERAL_CRYPT = LIT("Crypt")

# Abbreviation of Filter names in PDF 4.8.6. "Inline Images"
LITERALS_FLATE_DECODE = (LIT("FlateDecode"), LIT("Fl"))
LITERALS_LZW_DECODE = (LIT("LZWDecode"), LIT("LZW"))
LITERALS_ASCII85_DECODE = (LIT("ASCII85Decode"), LIT("A85"))
LITERALS_ASCIIHEX_DECODE = (LIT("ASCIIHexDecode"), LIT("AHx"))
LITERALS_RUNLENGTH_DECODE = (LIT("RunLengthDecode"), LIT("RL"))
LITERALS_CCITTFAX_DECODE = (LIT("CCITTFaxDecode"), LIT("CCF"))
LITERALS_DCT_DECODE = (LIT("DCTDecode"), LIT("DCT"))
LITERALS_JBIG2_DECODE = (LIT("JBIG2Decode"),)
LITERALS_JPX_DECODE = (LIT("JPXDecode"),)


class DecipherCallable(Protocol):
    """Fully typed a decipher callback, with optional parameter."""

    def __call__(
        self,
        objid: int,
        genno: int,
        data: bytes,
        attrs: dict[str, Any] | None = None,
    ) -> bytes:
        raise NotImplementedError


class PDFObject(PSObject):
    pass


# Adding aliases for these exceptions for backwards compatibility
PDFException = pdfexceptions.PDFException
PDFTypeError = pdfexceptions.PDFTypeError
PDFValueError = pdfexceptions.PDFValueError
PDFObjectNotFound = pdfexceptions.PDFObjectNotFound
PDFNotImplementedError = pdfexceptions.PDFNotImplementedError

_DEFAULT = object()


class PDFObjRef(PDFObject):
    def __init__(
        self,
        doc: Optional["PDFDocument"],
        objid: int,
        _: Any = _DEFAULT,
    ) -> None:
        """Reference to a PDF object.

        :param doc: The PDF document.
        :param objid: The object number.
        :param _: Unused argument for backwards compatibility.
        """
        if _ is not _DEFAULT:
            warn(
                "The third argument of PDFObjRef is unused and will be removed after "
                "2024",
                DeprecationWarning,
                stacklevel=2,
            )

        if objid == 0 and settings.STRICT:
            raise PDFValueError("PDF object id cannot be 0.")

        self.doc = doc
        self.objid = objid

    def __repr__(self) -> str:
        return f"<PDFObjRef:{self.objid}>"

    def resolve(self, default: object = None) -> Any:
        pass


def resolve1(x: object, default: object = None) -> Any:
    """Resolves an object.

    If this is an array or dictionary, it may still contains
    some indirect objects inside.
    """
    pass


def resolve_all(x: object, default: object = None) -> Any:
    """Recursively resolves the given object and all the internals.

    Make sure there is no indirect reference within the nested object.
    This procedure might be slow.
    """
    pass


def decipher_all(decipher: DecipherCallable, objid: int, genno: int, x: object) -> Any:
    """Recursively deciphers the given object."""
    pass


def int_value(x: object) -> int:
    pass


def float_value(x: object) -> float:
    pass


def num_value(x: object) -> float:
    pass


def uint_value(x: object, n_bits: int) -> int:
    """Resolve number and interpret it as a two's-complement unsigned number"""
    pass


def str_value(x: object) -> bytes:
    pass


def list_value(x: object) -> list[Any] | tuple[Any, ...]:
    pass


def dict_value(x: object) -> dict[Any, Any]:
    pass


def stream_value(x: object) -> "PDFStream":
    pass


def decompress_corrupted(data: bytes) -> bytes:
    """Called on some data that can't be properly decoded because of CRC checksum
    error. Attempt to decode it skipping the CRC.
    """
    pass


class PDFStream(PDFObject):
    def __init__(
        self,
        attrs: dict[str, Any],
        rawdata: bytes,
        decipher: DecipherCallable | None = None,
    ) -> None:
        assert isinstance(attrs, dict), str(type(attrs))
        self.attrs = attrs
        self.rawdata: bytes | None = rawdata
        self.decipher = decipher
        self.data: bytes | None = None
        self.objid: int | None = None
        self.genno: int | None = None

    def set_objid(self, objid: int, genno: int) -> None:
        pass

    def __repr__(self) -> str:
        if self.data is None:
            assert self.rawdata is not None
            return (
                f"<PDFStream({self.objid!r}): raw={len(self.rawdata)}, {self.attrs!r}>"
            )
        else:
            assert self.data is not None
            return f"<PDFStream({self.objid!r}): len={len(self.data)}, {self.attrs!r}>"

    def __contains__(self, name: object) -> bool:
        return name in self.attrs

    def __getitem__(self, name: str) -> Any:
        try:
            return self.attrs[name]
        except KeyError as e:
            raise PDFKeyError(
                f"PDF stream object {self.objid} does not have attribute '{name}'"
            ) from e

    def get(self, name: str, default: object = None) -> Any:
        pass

    def get_any(self, names: Iterable[str], default: object = None) -> Any:
        pass

    def get_filters(self) -> list[tuple[Any, Any]]:
        pass

    def decode(self) -> None:
        pass

    def get_data(self) -> bytes:
        pass

    def get_rawdata(self) -> bytes | None:
        pass
