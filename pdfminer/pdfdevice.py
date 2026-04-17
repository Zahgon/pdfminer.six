import logging
from collections.abc import Iterable, Sequence
from typing import (
    TYPE_CHECKING,
    BinaryIO,
    Optional,
    cast,
)

from pdfminer import utils
from pdfminer.pdfcolor import PDFColorSpace
from pdfminer.pdffont import PDFFont, PDFUnicodeNotDefined
from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import PDFStream
from pdfminer.psparser import PSLiteral
from pdfminer.utils import Matrix, PathSegment, Point, Rect

if TYPE_CHECKING:
    from pdfminer.pdfinterp import (
        PDFGraphicState,
        PDFResourceManager,
        PDFStackT,
        PDFTextState,
    )


PDFTextSeq = Iterable[int | float | bytes]

logger = logging.getLogger(__name__)


class PDFDevice:
    """Translate the output of PDFPageInterpreter to the output that is needed"""

    def __init__(self, rsrcmgr: "PDFResourceManager") -> None:
        self.rsrcmgr = rsrcmgr
        self.ctm: Matrix | None = None

    def __repr__(self) -> str:
        return "<PDFDevice>"

    def __enter__(self) -> "PDFDevice":
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()

    def close(self) -> None:
        pass

    def set_ctm(self, ctm: Matrix) -> None:
        pass

    def begin_tag(self, tag: PSLiteral, props: Optional["PDFStackT"] = None) -> None:
        pass

    def end_tag(self) -> None:
        pass

    def do_tag(self, tag: PSLiteral, props: Optional["PDFStackT"] = None) -> None:
        pass

    def begin_page(self, page: PDFPage, ctm: Matrix) -> None:
        pass

    def end_page(self, page: PDFPage) -> None:
        pass

    def begin_figure(self, name: str, bbox: Rect, matrix: Matrix) -> None:
        pass

    def end_figure(self, name: str) -> None:
        pass

    def paint_path(
        self,
        graphicstate: "PDFGraphicState",
        stroke: bool,
        fill: bool,
        evenodd: bool,
        path: Sequence[PathSegment],
    ) -> None:
        pass

    def render_image(self, name: str, stream: PDFStream) -> None:
        pass

    def render_string(
        self,
        textstate: "PDFTextState",
        seq: PDFTextSeq,
        ncs: PDFColorSpace,
        graphicstate: "PDFGraphicState",
    ) -> None:
        pass


class PDFTextDevice(PDFDevice):
    def render_string(
        self,
        textstate: "PDFTextState",
        seq: PDFTextSeq,
        ncs: PDFColorSpace,
        graphicstate: "PDFGraphicState",
    ) -> None:
        pass

    def render_string_horizontal(
        self,
        seq: PDFTextSeq,
        matrix: Matrix,
        pos: Point,
        font: PDFFont,
        fontsize: float,
        scaling: float,
        charspace: float,
        wordspace: float,
        rise: float,
        dxscale: float,
        ncs: PDFColorSpace,
        graphicstate: "PDFGraphicState",
    ) -> Point:
        pass

    def render_string_vertical(
        self,
        seq: PDFTextSeq,
        matrix: Matrix,
        pos: Point,
        font: PDFFont,
        fontsize: float,
        scaling: float,
        charspace: float,
        wordspace: float,
        rise: float,
        dxscale: float,
        ncs: PDFColorSpace,
        graphicstate: "PDFGraphicState",
    ) -> Point:
        pass

    def render_char(
        self,
        matrix: Matrix,
        font: PDFFont,
        fontsize: float,
        scaling: float,
        rise: float,
        cid: int,
        ncs: PDFColorSpace,
        graphicstate: "PDFGraphicState",
    ) -> float:
        pass


class TagExtractor(PDFDevice):
    def __init__(
        self,
        rsrcmgr: "PDFResourceManager",
        outfp: BinaryIO,
        codec: str = "utf-8",
    ) -> None:
        PDFDevice.__init__(self, rsrcmgr)
        self.outfp = outfp
        self.codec = codec
        self.pageno = 0
        self._stack: list[PSLiteral] = []

    def render_string(
        self,
        textstate: "PDFTextState",
        seq: PDFTextSeq,
        ncs: PDFColorSpace,
        graphicstate: "PDFGraphicState",
    ) -> None:
        pass

    def begin_page(self, page: PDFPage, ctm: Matrix) -> None:
        pass

    def end_page(self, page: PDFPage) -> None:
        pass

    def begin_tag(self, tag: PSLiteral, props: Optional["PDFStackT"] = None) -> None:
        pass

    def end_tag(self) -> None:
        pass

    def do_tag(self, tag: PSLiteral, props: Optional["PDFStackT"] = None) -> None:
        pass

    def _write(self, s: str) -> None:
        pass
