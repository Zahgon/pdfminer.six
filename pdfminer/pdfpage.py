import itertools
import logging
from collections.abc import Container, Iterator
from typing import Any, BinaryIO, ClassVar

from pdfminer import settings
from pdfminer.pdfdocument import (
    PDFDocument,
    PDFNoPageLabels,
    PDFTextExtractionNotAllowed,
)
from pdfminer.pdfexceptions import PDFObjectNotFound, PDFValueError
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import dict_value, int_value, list_value, resolve1
from pdfminer.psparser import LIT
from pdfminer.utils import Rect, parse_rect

log = logging.getLogger(__name__)

# some predefined literals and keywords.
LITERAL_PAGE = LIT("Page")
LITERAL_PAGES = LIT("Pages")


class PDFPage:
    """An object that holds the information about a page.

    A PDFPage object is merely a convenience class that has a set
    of keys and values, which describe the properties of a page
    and point to its contents.

    Attributes
    ----------
      doc: a PDFDocument object.
      pageid: any Python object that can uniquely identify the page.
      attrs: a dictionary of page attributes.
      contents: a list of PDFStream objects that represents the page content.
      lastmod: the last modified time of the page.
      resources: a dictionary of resources used by the page.
      mediabox: the physical size of the page.
      cropbox: the crop rectangle of the page.
      rotate: the page rotation (in degree).
      annots: the page annotations.
      beads: a chain that represents natural reading order.
      label: the page's label (typically, the logical page number).

    """

    def __init__(
        self,
        doc: PDFDocument,
        pageid: object,
        attrs: object,
        label: str | None,
    ) -> None:
        """Initialize a page object.

        doc: a PDFDocument object.
        pageid: any Python object that can uniquely identify the page.
        attrs: a dictionary of page attributes.
        label: page label string.
        """
        self.doc = doc
        self.pageid = pageid
        self.attrs = dict_value(attrs)
        self.label = label
        self.lastmod = resolve1(self.attrs.get("LastModified"))
        self.resources: dict[object, object] = resolve1(
            self.attrs.get("Resources", {}),
        )

        self.mediabox = self._parse_mediabox(self.attrs.get("MediaBox"))
        self.cropbox = self._parse_cropbox(self.attrs.get("CropBox"), self.mediabox)
        self.contents = self._parse_contents(self.attrs.get("Contents"))

        self.rotate = (int_value(self.attrs.get("Rotate", 0)) + 360) % 360
        self.annots = self.attrs.get("Annots")
        self.beads = self.attrs.get("B")

    def __repr__(self) -> str:
        return f"<PDFPage: Resources={self.resources!r}, MediaBox={self.mediabox!r}>"

    INHERITABLE_ATTRS: ClassVar[set[str]] = {
        "Resources",
        "MediaBox",
        "CropBox",
        "Rotate",
    }

    @classmethod
    def create_pages(cls, document: PDFDocument) -> Iterator["PDFPage"]:
        pass

    @classmethod
    def get_pages(
        cls,
        fp: BinaryIO,
        pagenos: Container[int] | None = None,
        maxpages: int = 0,
        password: str = "",
        caching: bool = True,
        check_extractable: bool = False,
    ) -> Iterator["PDFPage"]:
        # Create a PDF parser object associated with the file object.
        pass

    def _parse_mediabox(self, value: Any) -> Rect:
        pass

    def _parse_cropbox(self, value: Any, mediabox: Rect) -> Rect:
        pass

    def _parse_contents(self, value: Any) -> list[Any]:
        pass
