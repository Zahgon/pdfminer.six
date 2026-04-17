import itertools
import logging
import re
import struct
from collections.abc import Callable, Iterable, Iterator, KeysView, Sequence
from hashlib import md5, sha256, sha384, sha512
from typing import (
    Any,
    ClassVar,
    cast,
)

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from pdfminer import settings
from pdfminer.arcfour import Arcfour
from pdfminer.casting import safe_int
from pdfminer.data_structures import NumberTree
from pdfminer.pdfexceptions import (
    PDFException,
    PDFKeyError,
    PDFObjectNotFound,
    PDFTypeError,
)
from pdfminer.pdfparser import PDFParser, PDFStreamParser, PDFSyntaxError
from pdfminer.pdftypes import (
    DecipherCallable,
    PDFStream,
    decipher_all,
    dict_value,
    int_value,
    list_value,
    str_value,
    stream_value,
    uint_value,
)
from pdfminer.psexceptions import PSEOF
from pdfminer.psparser import KWD, LIT, literal_name
from pdfminer.utils import (
    choplist,
    decode_text,
    format_int_alpha,
    format_int_roman,
    nunpack,
    unpad_aes,
)

log = logging.getLogger(__name__)


class PDFNoValidXRef(PDFSyntaxError):
    pass


class PDFNoValidXRefWarning(SyntaxWarning):
    """Legacy warning for missing xref.

    Not used anymore because warnings.warn is replaced by logger.Logger.warn.
    """


class PDFNoOutlines(PDFException):
    pass


class PDFNoPageLabels(PDFException):
    pass


class PDFDestinationNotFound(PDFException):
    pass


class PDFEncryptionError(PDFException):
    pass


class PDFPasswordIncorrect(PDFEncryptionError):
    pass


class PDFEncryptionWarning(UserWarning):
    """Legacy warning for failed decryption.

    Not used anymore because warnings.warn is replaced by logger.Logger.warn.
    """


class PDFTextExtractionNotAllowedWarning(UserWarning):
    """Legacy warning for PDF that does not allow extraction.

    Not used anymore because warnings.warn is replaced by logger.Logger.warn.
    """


class PDFTextExtractionNotAllowed(PDFEncryptionError):
    pass


# some predefined literals and keywords.
LITERAL_OBJSTM = LIT("ObjStm")
LITERAL_XREF = LIT("XRef")
LITERAL_CATALOG = LIT("Catalog")


class PDFBaseXRef:
    def get_trailer(self) -> dict[str, Any]:
        raise NotImplementedError

    def get_objids(self) -> Iterable[int]:
        pass

    # Must return
    #     (strmid, index, genno)
    #  or (None, pos, genno)
    def get_pos(self, objid: int) -> tuple[int | None, int, int]:
        raise PDFKeyError(objid)

    def load(self, parser: PDFParser) -> None:
        raise NotImplementedError


class PDFXRef(PDFBaseXRef):
    def __init__(self) -> None:
        self.offsets: dict[int, tuple[int | None, int, int]] = {}
        self.trailer: dict[str, Any] = {}

    def __repr__(self) -> str:
        return f"<PDFXRef: offsets={self.offsets.keys()!r}>"

    def load(self, parser: PDFParser) -> None:
        pass

    def load_trailer(self, parser: PDFParser) -> None:
        pass

    def get_trailer(self) -> dict[str, Any]:
        pass

    def get_objids(self) -> KeysView[int]:
        pass

    def get_pos(self, objid: int) -> tuple[int | None, int, int]:
        pass


class PDFXRefFallback(PDFXRef):
    def __repr__(self) -> str:
        return f"<PDFXRefFallback: offsets={self.offsets.keys()!r}>"

    PDFOBJ_CUE = re.compile(r"^(\d+)\s+(\d+)\s+obj\b")

    def load(self, parser: PDFParser) -> None:
        pass


class PDFXRefStream(PDFBaseXRef):
    def __init__(self) -> None:
        self.data: bytes | None = None
        self.entlen: int | None = None
        self.fl1: int | None = None
        self.fl2: int | None = None
        self.fl3: int | None = None
        self.ranges: list[tuple[int, int]] = []

    def __repr__(self) -> str:
        return f"<PDFXRefStream: ranges={self.ranges!r}>"

    def load(self, parser: PDFParser) -> None:
        pass

    def get_trailer(self) -> dict[str, Any]:
        pass

    def get_objids(self) -> Iterator[int]:
        pass

    def get_pos(self, objid: int) -> tuple[int | None, int, int]:
        pass


class PDFStandardSecurityHandler:
    PASSWORD_PADDING = (
        b"(\xbfN^Nu\x8aAd\x00NV\xff\xfa\x01\x08..\x00\xb6\xd0h>\x80/\x0c\xa9\xfedSiz"
    )
    supported_revisions: tuple[int, ...] = (2, 3)

    def __init__(
        self,
        docid: Sequence[bytes],
        param: dict[str, Any],
        password: str = "",
    ) -> None:
        self.docid = docid
        self.param = param
        self.password = password
        self.init()

    def init(self) -> None:
        pass

    def init_params(self) -> None:
        pass

    def init_key(self) -> None:
        pass

    def is_printable(self) -> bool:
        pass

    def is_modifiable(self) -> bool:
        pass

    def is_extractable(self) -> bool:
        pass

    def compute_u(self, key: bytes) -> bytes:
        pass

    def compute_encryption_key(self, password: bytes) -> bytes:
        # Algorithm 3.2
        pass

    def authenticate(self, password: str) -> bytes | None:
        pass

    def authenticate_user_password(self, password: bytes) -> bytes | None:
        pass

    def verify_encryption_key(self, key: bytes) -> bool:
        # Algorithm 3.6
        pass

    def authenticate_owner_password(self, password: bytes) -> bytes | None:
        # Algorithm 3.7
        pass

    def decrypt(
        self,
        objid: int,
        genno: int,
        data: bytes,
        attrs: dict[str, Any] | None = None,
    ) -> bytes:
        pass

    def decrypt_rc4(self, objid: int, genno: int, data: bytes) -> bytes:
        pass


class PDFStandardSecurityHandlerV4(PDFStandardSecurityHandler):
    supported_revisions: tuple[int, ...] = (4,)

    def init_params(self) -> None:
        pass

    def get_cfm(self, name: str) -> Callable[[int, int, bytes], bytes] | None:
        pass

    def decrypt(
        self,
        objid: int,
        genno: int,
        data: bytes,
        attrs: dict[str, Any] | None = None,
        name: str | None = None,
    ) -> bytes:
        pass

    def decrypt_identity(self, objid: int, genno: int, data: bytes) -> bytes:
        pass

    def decrypt_aes128(self, objid: int, genno: int, data: bytes) -> bytes:
        pass


class PDFStandardSecurityHandlerV5(PDFStandardSecurityHandlerV4):
    supported_revisions = (5, 6)

    def init_params(self) -> None:
        pass

    def get_cfm(self, name: str) -> Callable[[int, int, bytes], bytes] | None:
        pass

    def authenticate(self, password: str) -> bytes | None:
        pass

    def _normalize_password(self, password: str) -> bytes:
        pass

    def _password_hash(
        self,
        password: bytes,
        salt: bytes,
        vector: bytes | None = None,
    ) -> bytes:
        """Compute password hash depending on revision number"""
        pass

    def _r5_password(
        self,
        password: bytes,
        salt: bytes,
        vector: bytes | None = None,
    ) -> bytes:
        """Compute the password for revision 5"""
        pass

    def _r6_password(
        self,
        password: bytes,
        salt: bytes,
        vector: bytes | None = None,
    ) -> bytes:
        """Compute the password for revision 6"""
        pass

    @staticmethod
    def _bytes_mod_3(input_bytes: bytes) -> int:
        # 256 is 1 mod 3, so we can just sum 'em
        pass

    def _aes_cbc_encrypt(self, key: bytes, iv: bytes, data: bytes) -> bytes:
        pass

    def decrypt_aes256(self, objid: int, genno: int, data: bytes) -> bytes:
        pass


class PDFDocument:
    """PDFDocument object represents a PDF document.

    Since a PDF file can be very big, normally it is not loaded at
    once. So PDF document has to cooperate with a PDF parser in order to
    dynamically import the data as processing goes.

    Typical usage:
      doc = PDFDocument(parser, password)
      obj = doc.getobj(objid)

    """

    security_handler_registry: ClassVar[dict[int, type[PDFStandardSecurityHandler]]] = {
        1: PDFStandardSecurityHandler,
        2: PDFStandardSecurityHandler,
        4: PDFStandardSecurityHandlerV4,
        5: PDFStandardSecurityHandlerV5,
    }

    def __init__(
        self,
        parser: PDFParser,
        password: str = "",
        caching: bool = True,
        fallback: bool = True,
    ) -> None:
        """Set the document to use a given PDFParser object."""
        self.caching = caching
        self.xrefs: list[PDFBaseXRef] = []
        self.info = []
        self.catalog: dict[str, Any] = {}
        self.encryption: tuple[Any, Any] | None = None
        self.decipher: DecipherCallable | None = None
        self._parser = None
        self._cached_objs: dict[int, tuple[object, int]] = {}
        self._parsed_objs: dict[int, tuple[list[object], int]] = {}
        self._parser = parser
        self._parser.set_document(self)
        self.is_printable = self.is_modifiable = self.is_extractable = True
        # Retrieve the information of each header that was appended
        # (maybe multiple times) at the end of the document.
        self._xrefpos: set[int] = set()
        try:
            pos = self.find_xref(parser)
            self.read_xref_from(parser, pos, self.xrefs)
        except PDFNoValidXRef:
            if fallback:
                parser.fallback = True
                newxref = PDFXRefFallback()
                newxref.load(parser)
                self.xrefs.append(newxref)

        for xref in self.xrefs:
            trailer = xref.get_trailer()
            if not trailer:
                continue
            # If there's an encryption info, remember it.
            if "Encrypt" in trailer:
                # Some documents may not have a /ID, use two empty
                # byte strings instead. Solves
                # https://github.com/pdfminer/pdfminer.six/issues/594
                id_value = list_value(trailer["ID"]) if "ID" in trailer else (b"", b"")
                self.encryption = (id_value, dict_value(trailer["Encrypt"]))
                self._initialize_password(password)
            if "Info" in trailer:
                self.info.append(dict_value(trailer["Info"]))
            if "Root" in trailer:
                # Every PDF file must have exactly one /Root dictionary.
                self.catalog = dict_value(trailer["Root"])
                break
        else:
            raise PDFSyntaxError("No /Root object! - Is this really a PDF?")
        if self.catalog.get("Type") is not LITERAL_CATALOG and settings.STRICT:
            raise PDFSyntaxError("Catalog not found!")

    KEYWORD_OBJ = KWD(b"obj")

    # _initialize_password(password=b'')
    #   Perform the initialization with a given password.
    def _initialize_password(self, password: str = "") -> None:
        pass

    def _getobj_objstm(self, stream: PDFStream, index: int, objid: int) -> object:
        pass

    def _get_objects(self, stream: PDFStream) -> tuple[list[object], int]:
        pass

    def _getobj_parse(self, pos: int, objid: int) -> object:
        pass

    # can raise PDFObjectNotFound
    def getobj(self, objid: int) -> object:
        """Get object from PDF

        :raises PDFException if PDFDocument is not initialized
        :raises PDFObjectNotFound if objid does not exist in PDF
        """
        pass

    OutlineType = tuple[Any, Any, Any, Any, Any]

    def get_outlines(self) -> Iterator[OutlineType]:
        pass

    def get_page_labels(self) -> Iterator[str]:
        """Generate page label strings for the PDF document.

        If the document includes page labels, generates strings, one per page.
        If not, raises PDFNoPageLabels.

        The resulting iteration is unbounded.
        """
        pass

    def lookup_name(self, cat: str, key: str | bytes) -> Any:
        pass

    def get_dest(self, name: str | bytes) -> Any:
        pass

    # find_xref
    def find_xref(self, parser: PDFParser) -> int:
        """Internal function used to locate the first XRef."""
        pass

    # read xref table
    def read_xref_from(
        self,
        parser: PDFParser,
        start: int,
        xrefs: list[PDFBaseXRef],
    ) -> None:
        """Reads XRefs from the given location."""
        pass


class PageLabels(NumberTree):
    """PageLabels from the document catalog.

    See Section 8.3.1 in the PDF Reference.
    """

    @property
    def labels(self) -> Iterator[str]:
        pass

    @staticmethod
    def _format_page_label(value: int, style: Any) -> str:
        """Format page label value in a specific style"""
        pass
