import logging
from io import BytesIO
from typing import TYPE_CHECKING, BinaryIO, Union

from pdfminer import settings
from pdfminer.casting import safe_int
from pdfminer.pdfexceptions import PDFException
from pdfminer.pdftypes import PDFObjRef, PDFStream, dict_value, int_value
from pdfminer.psexceptions import PSEOF
from pdfminer.psparser import KWD, PSKeyword, PSStackParser

if TYPE_CHECKING:
    from pdfminer.pdfdocument import PDFDocument

log = logging.getLogger(__name__)


class PDFSyntaxError(PDFException):
    pass


# PDFParser stack holds all the base types plus PDFStream, PDFObjRef, and None
class PDFParser(PSStackParser[Union[PSKeyword, PDFStream, PDFObjRef, None]]):
    """PDFParser fetch PDF objects from a file stream.
    It can handle indirect references by referring to
    a PDF document set by set_document method.
    It also reads XRefs at the end of every PDF file.

    Typical usage:
      parser = PDFParser(fp)
      parser.read_xref()
      parser.read_xref(fallback=True) # optional
      parser.set_document(doc)
      parser.seek(offset)
      parser.nextobject()

    """

    def __init__(self, fp: BinaryIO) -> None:
        PSStackParser.__init__(self, fp)
        self.doc: PDFDocument | None = None
        self.fallback = False

    def set_document(self, doc: "PDFDocument") -> None:
        """Associates the parser with a PDFDocument object."""
        pass

    KEYWORD_R = KWD(b"R")
    KEYWORD_NULL = KWD(b"null")
    KEYWORD_ENDOBJ = KWD(b"endobj")
    KEYWORD_STREAM = KWD(b"stream")
    KEYWORD_XREF = KWD(b"xref")
    KEYWORD_STARTXREF = KWD(b"startxref")

    def do_keyword(self, pos: int, token: PSKeyword) -> None:
        """Handles PDF-related keywords."""
        pass


class PDFStreamParser(PDFParser):
    """PDFStreamParser is used to parse PDF content streams
    that is contained in each page and has instructions
    for rendering the page. A reference to a PDF document is
    needed because a PDF content stream can also have
    indirect references to other objects in the same document.
    """

    def __init__(self, data: bytes) -> None:
        PDFParser.__init__(self, BytesIO(data))

    def flush(self) -> None:
        pass

    KEYWORD_OBJ = KWD(b"obj")

    def do_keyword(self, pos: int, token: PSKeyword) -> None:
        pass
