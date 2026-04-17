import heapq
import logging
from collections.abc import Iterable, Iterator, Sequence
from typing import (
    Generic,
    TypeVar,
    Union,
    cast,
)

from pdfminer.pdfcolor import PDFColorSpace
from pdfminer.pdfexceptions import PDFTypeError, PDFValueError
from pdfminer.pdffont import PDFFont
from pdfminer.pdfinterp import Color, PDFGraphicState
from pdfminer.pdftypes import PDFStream
from pdfminer.utils import (
    INF,
    LTComponentT,
    Matrix,
    PathSegment,
    Plane,
    Point,
    Rect,
    apply_matrix_rect,
    bbox2str,
    fsplit,
    get_bound,
    matrix2str,
    uniq,
)

logger = logging.getLogger(__name__)


class IndexAssigner:
    def __init__(self, index: int = 0) -> None:
        self.index = index

    def run(self, obj: "LTItem") -> None:
        pass


class LAParams:
    """Parameters for layout analysis

    :param line_overlap: If two characters have more overlap than this they
        are considered to be on the same line. The overlap is specified
        relative to the minimum height of both characters.
    :param char_margin: If two characters are closer together than this
        margin they are considered part of the same line. The margin is
        specified relative to the width of the character.
    :param word_margin: If two characters on the same line are further apart
        than this margin then they are considered to be two separate words, and
        an intermediate space will be added for readability. The margin is
        specified relative to the width of the character.
    :param line_margin: If two lines are are close together they are
        considered to be part of the same paragraph. The margin is
        specified relative to the height of a line.
    :param boxes_flow: Specifies how much a horizontal and vertical position
        of a text matters when determining the order of text boxes. The value
        should be within the range of -1.0 (only horizontal position
        matters) to +1.0 (only vertical position matters). You can also pass
        `None` to disable advanced layout analysis, and instead return text
        based on the position of the bottom left corner of the text box.
    :param detect_vertical: If vertical text should be considered during
        layout analysis
    :param all_texts: If layout analysis should be performed on text in
        figures.
    """

    def __init__(
        self,
        line_overlap: float = 0.5,
        char_margin: float = 2.0,
        line_margin: float = 0.5,
        word_margin: float = 0.1,
        boxes_flow: float | None = 0.5,
        detect_vertical: bool = False,
        all_texts: bool = False,
    ) -> None:
        self.line_overlap = line_overlap
        self.char_margin = char_margin
        self.line_margin = line_margin
        self.word_margin = word_margin
        self.boxes_flow = boxes_flow
        self.detect_vertical = detect_vertical
        self.all_texts = all_texts

        self._validate()

    def _validate(self) -> None:
        pass

    def __repr__(self) -> str:
        return (
            f"<LAParams: char_margin={self.char_margin:.1f}, "
            f"line_margin={self.line_margin:.1f}, "
            f"word_margin={self.word_margin:.1f} "
            f"all_texts={self.all_texts!r}>"
        )


class LTItem:
    """Interface for things that can be analyzed"""

    def analyze(self, laparams: LAParams) -> None:
        """Perform the layout analysis."""


class LTText:
    """Interface for things that have text"""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.get_text()!r}>"

    def get_text(self) -> str:
        """Text contained in this object"""
        raise NotImplementedError


class LTComponent(LTItem):
    """Object with a bounding box"""

    def __init__(self, bbox: Rect) -> None:
        LTItem.__init__(self)
        self.set_bbox(bbox)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {bbox2str(self.bbox)}>"

    # Disable comparison.
    def __lt__(self, _: object) -> bool:
        raise PDFValueError

    def __le__(self, _: object) -> bool:
        raise PDFValueError

    def __gt__(self, _: object) -> bool:
        raise PDFValueError

    def __ge__(self, _: object) -> bool:
        raise PDFValueError

    def set_bbox(self, bbox: Rect) -> None:
        (x0, y0, x1, y1) = bbox
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.width = x1 - x0
        self.height = y1 - y0
        self.bbox = bbox

    def is_empty(self) -> bool:
        pass

    def is_hoverlap(self, obj: "LTComponent") -> bool:
        pass

    def hdistance(self, obj: "LTComponent") -> float:
        pass

    def hoverlap(self, obj: "LTComponent") -> float:
        pass

    def is_voverlap(self, obj: "LTComponent") -> bool:
        pass

    def vdistance(self, obj: "LTComponent") -> float:
        pass

    def voverlap(self, obj: "LTComponent") -> float:
        pass


class LTCurve(LTComponent):
    """A generic Bezier curve

    The parameter `original_path` contains the original
    pathing information from the pdf (e.g. for reconstructing Bezier Curves).

    `dashing_style` contains the Dashing information if any.
    """

    def __init__(
        self,
        linewidth: float,
        pts: list[Point],
        stroke: bool = False,
        fill: bool = False,
        evenodd: bool = False,
        stroking_color: Color | None = None,
        non_stroking_color: Color | None = None,
        original_path: list[PathSegment] | None = None,
        dashing_style: tuple[object, object] | None = None,
    ) -> None:
        LTComponent.__init__(self, get_bound(pts))
        self.pts = pts
        self.linewidth = linewidth
        self.stroke = stroke
        self.fill = fill
        self.evenodd = evenodd
        self.stroking_color = stroking_color
        self.non_stroking_color = non_stroking_color
        self.original_path = original_path
        self.dashing_style = dashing_style

    def get_pts(self) -> str:
        pass


class LTLine(LTCurve):
    """A single straight line.

    Could be used for separating text or figures.
    """

    def __init__(
        self,
        linewidth: float,
        p0: Point,
        p1: Point,
        stroke: bool = False,
        fill: bool = False,
        evenodd: bool = False,
        stroking_color: Color | None = None,
        non_stroking_color: Color | None = None,
        original_path: list[PathSegment] | None = None,
        dashing_style: tuple[object, object] | None = None,
    ) -> None:
        LTCurve.__init__(
            self,
            linewidth,
            [p0, p1],
            stroke,
            fill,
            evenodd,
            stroking_color,
            non_stroking_color,
            original_path,
            dashing_style,
        )


class LTRect(LTCurve):
    """A rectangle.

    Could be used for framing another pictures or figures.
    """

    def __init__(
        self,
        linewidth: float,
        bbox: Rect,
        stroke: bool = False,
        fill: bool = False,
        evenodd: bool = False,
        stroking_color: Color | None = None,
        non_stroking_color: Color | None = None,
        original_path: list[PathSegment] | None = None,
        dashing_style: tuple[object, object] | None = None,
    ) -> None:
        (x0, y0, x1, y1) = bbox
        LTCurve.__init__(
            self,
            linewidth,
            [(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
            stroke,
            fill,
            evenodd,
            stroking_color,
            non_stroking_color,
            original_path,
            dashing_style,
        )


class LTImage(LTComponent):
    """An image object.

    Embedded images can be in JPEG, Bitmap or JBIG2.
    """

    def __init__(self, name: str, stream: PDFStream, bbox: Rect) -> None:
        LTComponent.__init__(self, bbox)
        self.name = name
        self.stream = stream
        self.srcsize = (stream.get_any(("W", "Width")), stream.get_any(("H", "Height")))
        self.imagemask = stream.get_any(("IM", "ImageMask"))
        self.bits = stream.get_any(("BPC", "BitsPerComponent"), 1)
        self.colorspace = stream.get_any(("CS", "ColorSpace"))
        if not isinstance(self.colorspace, list):
            self.colorspace = [self.colorspace]

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}({self.name}) "
            f"{bbox2str(self.bbox)} {self.srcsize!r}>"
        )


class LTAnno(LTItem, LTText):
    """Actual letter in the text as a Unicode string.

    Note that, while a LTChar object has actual boundaries, LTAnno objects does
    not, as these are "virtual" characters, inserted by a layout analyzer
    according to the relationship between two characters (e.g. a space).
    """

    def __init__(self, text: str) -> None:
        self._text = text

    def get_text(self) -> str:
        pass


class LTChar(LTComponent, LTText):
    """Actual letter in the text as a Unicode string."""

    def __init__(
        self,
        matrix: Matrix,
        font: PDFFont,
        fontsize: float,
        scaling: float,
        rise: float,
        text: str,
        textwidth: float,
        textdisp: float | tuple[float | None, float],
        ncs: PDFColorSpace,
        graphicstate: PDFGraphicState,
    ) -> None:
        LTText.__init__(self)
        self._text = text
        self.matrix = matrix
        self.fontname = font.fontname
        self.ncs = ncs
        self.graphicstate = graphicstate
        self.adv = textwidth * fontsize * scaling
        # compute the boundary rectangle.
        if font.is_vertical():
            # vertical
            assert isinstance(textdisp, tuple)
            (vx, vy) = textdisp
            vx = fontsize * 0.5 if vx is None else vx * fontsize * 0.001
            vy = (1000 - vy) * fontsize * 0.001
            bbox = (-vx, vy + rise + self.adv, -vx + fontsize, vy + rise)
        else:
            # horizontal
            descent = font.get_descent() * fontsize
            bbox = (0, descent + rise, self.adv, descent + rise + fontsize)
        (a, b, c, d, _e, _f) = self.matrix
        self.upright = a * d * scaling > 0 and b * c <= 0
        (x0, y0, x1, y1) = apply_matrix_rect(self.matrix, bbox)
        if x1 < x0:
            (x0, x1) = (x1, x0)
        if y1 < y0:
            (y0, y1) = (y1, y0)
        LTComponent.__init__(self, (x0, y0, x1, y1))
        if font.is_vertical():
            self.size = self.width
        else:
            self.size = self.height

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} {bbox2str(self.bbox)} "
            f"matrix={matrix2str(self.matrix)} "
            f"font={self.fontname!r} "
            f"adv={self.adv} "
            f"text={self.get_text()!r}>"
        )

    def get_text(self) -> str:
        pass


LTItemT = TypeVar("LTItemT", bound=LTItem)


class LTContainer(LTComponent, Generic[LTItemT]):
    """Object that can be extended and analyzed"""

    def __init__(self, bbox: Rect) -> None:
        LTComponent.__init__(self, bbox)
        self._objs: list[LTItemT] = []

    def __iter__(self) -> Iterator[LTItemT]:
        return iter(self._objs)

    def __len__(self) -> int:
        return len(self._objs)

    def add(self, obj: LTItemT) -> None:
        self._objs.append(obj)

    def extend(self, objs: Iterable[LTItemT]) -> None:
        pass

    def analyze(self, laparams: LAParams) -> None:
        pass


class LTExpandableContainer(LTContainer[LTItemT]):
    def __init__(self) -> None:
        LTContainer.__init__(self, (+INF, +INF, -INF, -INF))

    # Incompatible override: we take an LTComponent (with bounding box), but
    # super() LTContainer only considers LTItem (no bounding box).
    def add(self, obj: LTComponent) -> None:  # type: ignore[override]
        LTContainer.add(self, cast(LTItemT, obj))
        self.set_bbox(
            (
                min(self.x0, obj.x0),
                min(self.y0, obj.y0),
                max(self.x1, obj.x1),
                max(self.y1, obj.y1),
            ),
        )


class LTTextContainer(LTExpandableContainer[LTItemT], LTText):
    def __init__(self) -> None:
        LTText.__init__(self)
        LTExpandableContainer.__init__(self)

    def get_text(self) -> str:
        pass


TextLineElement = Union[LTChar, LTAnno]


class LTTextLine(LTTextContainer[TextLineElement]):
    """Contains a list of LTChar objects that represent a single text line.

    The characters are aligned either horizontally or vertically, depending on
    the text's writing mode.
    """

    def __init__(self, word_margin: float) -> None:
        super().__init__()
        self.word_margin = word_margin

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {bbox2str(self.bbox)} {self.get_text()!r}>"

    def analyze(self, laparams: LAParams) -> None:
        pass

    def find_neighbors(
        self,
        plane: Plane[LTComponentT],
        ratio: float,
    ) -> list["LTTextLine"]:
        raise NotImplementedError

    def is_empty(self) -> bool:
        pass


class LTTextLineHorizontal(LTTextLine):
    def __init__(self, word_margin: float) -> None:
        LTTextLine.__init__(self, word_margin)
        self._x1: float = +INF

    # Incompatible override: we take an LTComponent (with bounding box), but
    # LTContainer only considers LTItem (no bounding box).
    def add(self, obj: LTComponent) -> None:  # type: ignore[override]
        if isinstance(obj, LTChar) and self.word_margin:
            margin = self.word_margin * max(obj.width, obj.height)
            if self._x1 < obj.x0 - margin:
                LTContainer.add(self, LTAnno(" "))
        self._x1 = obj.x1
        super().add(obj)

    def find_neighbors(
        self,
        plane: Plane[LTComponentT],
        ratio: float,
    ) -> list[LTTextLine]:
        """Finds neighboring LTTextLineHorizontals in the plane.

        Returns a list of other LTTestLineHorizontals in the plane which are
        close to self. "Close" can be controlled by ratio. The returned objects
        will be the same height as self, and also either left-, right-, or
        centrally-aligned.
        """
        pass

    def _is_left_aligned_with(self, other: LTComponent, tolerance: float = 0) -> bool:
        """Whether the left-hand edge of `other` is within `tolerance`."""
        pass

    def _is_right_aligned_with(self, other: LTComponent, tolerance: float = 0) -> bool:
        """Whether the right-hand edge of `other` is within `tolerance`."""
        pass

    def _is_centrally_aligned_with(
        self,
        other: LTComponent,
        tolerance: float = 0,
    ) -> bool:
        """Whether the horizontal center of `other` is within `tolerance`."""
        pass

    def _is_same_height_as(self, other: LTComponent, tolerance: float = 0) -> bool:
        pass


class LTTextLineVertical(LTTextLine):
    def __init__(self, word_margin: float) -> None:
        LTTextLine.__init__(self, word_margin)
        self._y0: float = -INF

    # Incompatible override: we take an LTComponent (with bounding box), but
    # LTContainer only considers LTItem (no bounding box).
    def add(self, obj: LTComponent) -> None:  # type: ignore[override]
        if isinstance(obj, LTChar) and self.word_margin:
            margin = self.word_margin * max(obj.width, obj.height)
            if obj.y1 + margin < self._y0:
                LTContainer.add(self, LTAnno(" "))
        self._y0 = obj.y0
        super().add(obj)

    def find_neighbors(
        self,
        plane: Plane[LTComponentT],
        ratio: float,
    ) -> list[LTTextLine]:
        """Finds neighboring LTTextLineVerticals in the plane.

        Returns a list of other LTTextLineVerticals in the plane which are
        close to self. "Close" can be controlled by ratio. The returned objects
        will be the same width as self, and also either upper-, lower-, or
        centrally-aligned.
        """
        pass

    def _is_lower_aligned_with(self, other: LTComponent, tolerance: float = 0) -> bool:
        """Whether the lower edge of `other` is within `tolerance`."""
        pass

    def _is_upper_aligned_with(self, other: LTComponent, tolerance: float = 0) -> bool:
        """Whether the upper edge of `other` is within `tolerance`."""
        pass

    def _is_centrally_aligned_with(
        self,
        other: LTComponent,
        tolerance: float = 0,
    ) -> bool:
        """Whether the vertical center of `other` is within `tolerance`."""
        pass

    def _is_same_width_as(self, other: LTComponent, tolerance: float) -> bool:
        pass


class LTTextBox(LTTextContainer[LTTextLine]):
    """Represents a group of text chunks in a rectangular area.

    Note that this box is created by geometric analysis and does not
    necessarily represents a logical boundary of the text. It contains a list
    of LTTextLine objects.
    """

    def __init__(self) -> None:
        LTTextContainer.__init__(self)
        self.index: int = -1

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}({self.index}) "
            f"{bbox2str(self.bbox)} {self.get_text()!r}>"
        )

    def get_writing_mode(self) -> str:
        raise NotImplementedError


class LTTextBoxHorizontal(LTTextBox):
    def analyze(self, laparams: LAParams) -> None:
        pass

    def get_writing_mode(self) -> str:
        pass


class LTTextBoxVertical(LTTextBox):
    def analyze(self, laparams: LAParams) -> None:
        pass

    def get_writing_mode(self) -> str:
        pass


TextGroupElement = Union[LTTextBox, "LTTextGroup"]


class LTTextGroup(LTTextContainer[TextGroupElement]):
    def __init__(self, objs: Iterable[TextGroupElement]) -> None:
        super().__init__()
        self.extend(objs)


class LTTextGroupLRTB(LTTextGroup):
    def analyze(self, laparams: LAParams) -> None:
        pass


class LTTextGroupTBRL(LTTextGroup):
    def analyze(self, laparams: LAParams) -> None:
        pass


class LTLayoutContainer(LTContainer[LTComponent]):
    def __init__(self, bbox: Rect) -> None:
        LTContainer.__init__(self, bbox)
        self.groups: list[LTTextGroup] | None = None

    # group_objects: group text object to textlines.
    def group_objects(
        self,
        laparams: LAParams,
        objs: Iterable[LTComponent],
    ) -> Iterator[LTTextLine]:
        pass

    def group_textlines(
        self,
        laparams: LAParams,
        lines: Iterable[LTTextLine],
    ) -> Iterator[LTTextBox]:
        """Group neighboring lines to textboxes"""
        pass

    def group_textboxes(
        self,
        laparams: LAParams,
        boxes: Sequence[LTTextBox],
    ) -> list[LTTextGroup]:
        """Group textboxes hierarchically.

        Get pair-wise distances, via dist func defined below, and then merge
        from the closest textbox pair. Once obj1 and obj2 are merged /
        grouped, the resulting group is considered as a new object, and its
        distances to other objects & groups are added to the process queue.

        For performance reason, pair-wise distances and object pair info are
        maintained in a heap of (idx, dist, id(obj1), id(obj2), obj1, obj2)
        tuples. It ensures quick access to the smallest element. Note that
        since comparison operators, e.g., __lt__, are disabled for
        LTComponent, id(obj) has to appear before obj in element tuples.

        :param laparams: LAParams object.
        :param boxes: All textbox objects to be grouped.
        :return: a list that has only one element, the final top level group.
        """
        pass

    def analyze(self, laparams: LAParams) -> None:
        # textobjs is a list of LTChar objects, i.e.
        # it has all the individual characters in the page.
        pass


class LTFigure(LTLayoutContainer):
    """Represents an area used by PDF Form objects.

    PDF Forms can be used to present figures or pictures by embedding yet
    another PDF document within a page. Note that LTFigure objects can appear
    recursively.
    """

    def __init__(self, name: str, bbox: Rect, matrix: Matrix) -> None:
        self.name = name
        self.matrix = matrix
        (x, y, w, h) = bbox
        rect = (x, y, x + w, y + h)
        bbox = apply_matrix_rect(matrix, rect)
        LTLayoutContainer.__init__(self, bbox)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}({self.name}) "
            f"{bbox2str(self.bbox)} "
            f"matrix={matrix2str(self.matrix)}>"
        )

    def analyze(self, laparams: LAParams) -> None:
        pass


class LTPage(LTLayoutContainer):
    """Represents an entire page.

    Like any other LTLayoutContainer, an LTPage can be iterated to obtain child
    objects like LTTextBox, LTFigure, LTImage, LTRect, LTCurve and LTLine.
    """

    def __init__(self, pageid: int, bbox: Rect, rotate: float = 0) -> None:
        LTLayoutContainer.__init__(self, bbox)
        self.pageid = pageid
        self.rotate = rotate

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}({self.pageid!r}) "
            f"{bbox2str(self.bbox)} "
            f"rotate={self.rotate!r}>"
        )
