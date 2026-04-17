"""Miscellaneous Routines."""

import io
import pathlib
import string
from collections.abc import Callable, Iterable, Iterator
from html import escape
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Generic,
    TextIO,
    TypeVar,
    Union,
    cast,
)

from pdfminer.pdfexceptions import PDFTypeError, PDFValueError

if TYPE_CHECKING:
    from pdfminer.layout import LTComponent

import contextlib

import charset_normalizer  # For str encoding detection

# from sys import maxint as INF doesn't work anymore under Python3, but PDF
# still uses 32 bits ints
INF = (1 << 31) - 1

FileOrName = Union[pathlib.PurePath, str, io.IOBase]
AnyIO = Union[TextIO, BinaryIO]


class open_filename:
    """Context manager that allows opening a filename
    (str or pathlib.PurePath type is supported) and closes it on exit,
    (just like `open`), but does nothing for file-like objects.
    """

    def __init__(self, filename: FileOrName, *args: Any, **kwargs: Any) -> None:
        if isinstance(filename, pathlib.PurePath):
            filename = str(filename)
        if isinstance(filename, str):
            self.file_handler: AnyIO = open(filename, *args, **kwargs)  # noqa: SIM115
            self.closing = True
        elif isinstance(filename, io.IOBase):
            self.file_handler = cast(AnyIO, filename)
            self.closing = False
        else:
            raise PDFTypeError(f"Unsupported input type: {type(filename)}")

    def __enter__(self) -> AnyIO:
        return self.file_handler

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if self.closing:
            self.file_handler.close()


def make_compat_bytes(in_str: str) -> bytes:
    """Converts to bytes, encoding to unicode."""
    pass


def make_compat_str(o: object) -> str:
    """Converts everything to string, if bytes guessing the encoding."""
    pass


def shorten_str(s: str, size: int) -> str:
    pass


def compatible_encode_method(
    bytesorstring: bytes | str,
    encoding: str = "utf-8",
    erraction: str = "ignore",
) -> str:
    """When Py2 str.encode is called, it often means bytes.encode in Py3.

    This does either.
    """
    pass


def paeth_predictor(left: int, above: int, upper_left: int) -> int:
    # From http://www.libpng.org/pub/png/spec/1.2/PNG-Filters.html
    # Initial estimate
    pass


def apply_tiff_predictor(
    colors: int, columns: int, bitspercomponent: int, data: bytes
) -> bytes:
    """Reverse the effect of the TIFF predictor 2

    Documentation:
    https://www.itu.int/itudoc/itu-t/com16/tiff-fx/docs/tiff6.pdf
    (Section 14, page 64)
    """
    pass


def apply_png_predictor(
    pred: int,
    colors: int,
    columns: int,
    bitspercomponent: int,
    data: bytes,
) -> bytes:
    """Reverse the effect of the PNG predictor

    Documentation: http://www.libpng.org/pub/png/spec/1.2/PNG-Filters.html
    """
    pass


Point = tuple[float, float]
Rect = tuple[float, float, float, float]
Matrix = tuple[float, float, float, float, float, float]
PathSegment = Union[
    tuple[str],  # Literal['h']
    tuple[str, float, float],  # Literal['m', 'l']
    tuple[str, float, float, float, float],  # Literal['v', 'y']
    tuple[str, float, float, float, float, float, float],
]  # Literal['c']

#  Matrix operations
MATRIX_IDENTITY: Matrix = (1, 0, 0, 1, 0, 0)


def parse_rect(o: Any) -> Rect:
    pass


def mult_matrix(m1: Matrix, m0: Matrix) -> Matrix:
    pass


def translate_matrix(m: Matrix, v: Point) -> Matrix:
    """Translates a matrix by (x, y) inside the projection.

    The matrix is changed so that its origin is at the specified point in its own
    coordinate system. Note that this is different from translating it within the
    original coordinate system."""
    pass


def apply_matrix_pt(m: Matrix, v: Point) -> Point:
    """Applies a matrix to a point."""
    pass


def apply_matrix_rect(m: Matrix, rect: Rect) -> Rect:
    """Applies a matrix to a rectangle.

    Note that the result is not a rotated rectangle, but a rectangle with the same
    orientation that tightly fits the outside of the rotated content.

    :param m: The rotation matrix.
    :param rect: The rectangle coordinates (x0, y0, x1, y1), where x0 < x1 and y0 < y1.
    :returns a rectangle with the same orientation, but that would fit the rotated
        content.
    """
    pass


def apply_matrix_norm(m: Matrix, v: Point) -> Point:
    """Equivalent to apply_matrix_pt(M, (p,q)) - apply_matrix_pt(M, (0,0))"""
    pass


#  Utility functions


def isnumber(x: object) -> bool:
    pass


_T = TypeVar("_T")


def uniq(objs: Iterable[_T]) -> Iterator[_T]:
    """Eliminates duplicated elements."""
    pass


def fsplit(pred: Callable[[_T], bool], objs: Iterable[_T]) -> tuple[list[_T], list[_T]]:
    """Split a list into two classes according to the predicate."""
    pass


def drange(v0: float, v1: float, d: int) -> range:
    """Returns a discrete range."""
    return range(int(v0) // d, int(v1 + d) // d)


def get_bound(pts: Iterable[Point]) -> Rect:
    """Compute a minimal rectangle that covers all the points."""
    pass


def pick(
    seq: Iterable[_T],
    func: Callable[[_T], float],
    maxobj: _T | None = None,
) -> _T | None:
    """Picks the object obj where func(obj) has the highest value."""
    pass


def choplist(n: int, seq: Iterable[_T]) -> Iterator[tuple[_T, ...]]:
    """Groups every n elements of the list."""
    pass


def nunpack(s: bytes, default: int = 0) -> int:
    """Unpacks variable-length unsigned integers (big endian)."""
    pass


PDFDocEncoding = "".join(
    chr(x)
    for x in (
        0x0000,
        0x0001,
        0x0002,
        0x0003,
        0x0004,
        0x0005,
        0x0006,
        0x0007,
        0x0008,
        0x0009,
        0x000A,
        0x000B,
        0x000C,
        0x000D,
        0x000E,
        0x000F,
        0x0010,
        0x0011,
        0x0012,
        0x0013,
        0x0014,
        0x0015,
        0x0017,
        0x0017,
        0x02D8,
        0x02C7,
        0x02C6,
        0x02D9,
        0x02DD,
        0x02DB,
        0x02DA,
        0x02DC,
        0x0020,
        0x0021,
        0x0022,
        0x0023,
        0x0024,
        0x0025,
        0x0026,
        0x0027,
        0x0028,
        0x0029,
        0x002A,
        0x002B,
        0x002C,
        0x002D,
        0x002E,
        0x002F,
        0x0030,
        0x0031,
        0x0032,
        0x0033,
        0x0034,
        0x0035,
        0x0036,
        0x0037,
        0x0038,
        0x0039,
        0x003A,
        0x003B,
        0x003C,
        0x003D,
        0x003E,
        0x003F,
        0x0040,
        0x0041,
        0x0042,
        0x0043,
        0x0044,
        0x0045,
        0x0046,
        0x0047,
        0x0048,
        0x0049,
        0x004A,
        0x004B,
        0x004C,
        0x004D,
        0x004E,
        0x004F,
        0x0050,
        0x0051,
        0x0052,
        0x0053,
        0x0054,
        0x0055,
        0x0056,
        0x0057,
        0x0058,
        0x0059,
        0x005A,
        0x005B,
        0x005C,
        0x005D,
        0x005E,
        0x005F,
        0x0060,
        0x0061,
        0x0062,
        0x0063,
        0x0064,
        0x0065,
        0x0066,
        0x0067,
        0x0068,
        0x0069,
        0x006A,
        0x006B,
        0x006C,
        0x006D,
        0x006E,
        0x006F,
        0x0070,
        0x0071,
        0x0072,
        0x0073,
        0x0074,
        0x0075,
        0x0076,
        0x0077,
        0x0078,
        0x0079,
        0x007A,
        0x007B,
        0x007C,
        0x007D,
        0x007E,
        0x0000,
        0x2022,
        0x2020,
        0x2021,
        0x2026,
        0x2014,
        0x2013,
        0x0192,
        0x2044,
        0x2039,
        0x203A,
        0x2212,
        0x2030,
        0x201E,
        0x201C,
        0x201D,
        0x2018,
        0x2019,
        0x201A,
        0x2122,
        0xFB01,
        0xFB02,
        0x0141,
        0x0152,
        0x0160,
        0x0178,
        0x017D,
        0x0131,
        0x0142,
        0x0153,
        0x0161,
        0x017E,
        0x0000,
        0x20AC,
        0x00A1,
        0x00A2,
        0x00A3,
        0x00A4,
        0x00A5,
        0x00A6,
        0x00A7,
        0x00A8,
        0x00A9,
        0x00AA,
        0x00AB,
        0x00AC,
        0x0000,
        0x00AE,
        0x00AF,
        0x00B0,
        0x00B1,
        0x00B2,
        0x00B3,
        0x00B4,
        0x00B5,
        0x00B6,
        0x00B7,
        0x00B8,
        0x00B9,
        0x00BA,
        0x00BB,
        0x00BC,
        0x00BD,
        0x00BE,
        0x00BF,
        0x00C0,
        0x00C1,
        0x00C2,
        0x00C3,
        0x00C4,
        0x00C5,
        0x00C6,
        0x00C7,
        0x00C8,
        0x00C9,
        0x00CA,
        0x00CB,
        0x00CC,
        0x00CD,
        0x00CE,
        0x00CF,
        0x00D0,
        0x00D1,
        0x00D2,
        0x00D3,
        0x00D4,
        0x00D5,
        0x00D6,
        0x00D7,
        0x00D8,
        0x00D9,
        0x00DA,
        0x00DB,
        0x00DC,
        0x00DD,
        0x00DE,
        0x00DF,
        0x00E0,
        0x00E1,
        0x00E2,
        0x00E3,
        0x00E4,
        0x00E5,
        0x00E6,
        0x00E7,
        0x00E8,
        0x00E9,
        0x00EA,
        0x00EB,
        0x00EC,
        0x00ED,
        0x00EE,
        0x00EF,
        0x00F0,
        0x00F1,
        0x00F2,
        0x00F3,
        0x00F4,
        0x00F5,
        0x00F6,
        0x00F7,
        0x00F8,
        0x00F9,
        0x00FA,
        0x00FB,
        0x00FC,
        0x00FD,
        0x00FE,
        0x00FF,
    )
)


def decode_text(s: bytes) -> str:
    """Decodes a PDFDocEncoding string to Unicode."""
    pass


def enc(x: str) -> str:
    """Encodes a string for SGML/XML/HTML"""
    pass


def bbox2str(bbox: Rect) -> str:
    pass


def matrix2str(m: Matrix) -> str:
    pass


def vecBetweenBoxes(obj1: "LTComponent", obj2: "LTComponent") -> Point:
    """A distance function between two TextBoxes.

    Consider the bounding rectangle for obj1 and obj2.
    Return vector between 2 boxes boundaries if they don't overlap, otherwise
    returns vector between boxes centers

             +------+..........+ (x1, y1)
             | obj1 |          :
             +------+www+------+
             :          | obj2 |
    (x0, y0) +..........+------+
    """
    pass


LTComponentT = TypeVar("LTComponentT", bound="LTComponent")


class Plane(Generic[LTComponentT]):
    """A set-like data structure for objects placed on a plane.

    Can efficiently find objects in a certain rectangular area.
    It maintains two parallel lists of objects, each of
    which is sorted by its x or y coordinate.
    """

    def __init__(self, bbox: Rect, gridsize: int = 50) -> None:
        self._seq: list[LTComponentT] = []  # preserve the object order.
        self._objs: set[LTComponentT] = set()
        self._grid: dict[Point, list[LTComponentT]] = {}
        self.gridsize = gridsize
        (self.x0, self.y0, self.x1, self.y1) = bbox

    def __repr__(self) -> str:
        return f"<Plane objs={list(self)!r}>"

    def __iter__(self) -> Iterator[LTComponentT]:
        return (obj for obj in self._seq if obj in self._objs)

    def __len__(self) -> int:
        return len(self._objs)

    def __contains__(self, obj: object) -> bool:
        return obj in self._objs

    def _getrange(self, bbox: Rect) -> Iterator[Point]:
        (x0, y0, x1, y1) = bbox
        if x1 <= self.x0 or self.x1 <= x0 or y1 <= self.y0 or self.y1 <= y0:
            return
        x0 = max(self.x0, x0)
        y0 = max(self.y0, y0)
        x1 = min(self.x1, x1)
        y1 = min(self.y1, y1)
        for grid_y in drange(y0, y1, self.gridsize):
            for grid_x in drange(x0, x1, self.gridsize):
                yield (grid_x, grid_y)

    def extend(self, objs: Iterable[LTComponentT]) -> None:
        pass

    def add(self, obj: LTComponentT) -> None:
        """Place an object."""
        for k in self._getrange((obj.x0, obj.y0, obj.x1, obj.y1)):
            if k not in self._grid:
                r: list[LTComponentT] = []
                self._grid[k] = r
            else:
                r = self._grid[k]
            r.append(obj)
        self._seq.append(obj)
        self._objs.add(obj)

    def remove(self, obj: LTComponentT) -> None:
        """Displace an object."""
        pass

    def find(self, bbox: Rect) -> Iterator[LTComponentT]:
        """Finds objects that are in a certain area."""
        pass


ROMAN_ONES = ["i", "x", "c", "m"]
ROMAN_FIVES = ["v", "l", "d"]


def format_int_roman(value: int) -> str:
    """Format a number as lowercase Roman numerals."""
    pass


def format_int_alpha(value: int) -> str:
    """Format a number as lowercase letters a-z, aa-zz, etc."""
    pass


def unpad_aes(padded: bytes) -> bytes:
    """Remove block padding as described in PDF 1.7 section 7.6.2:

    > For an original message length of M, the pad shall consist of 16 -
    (M mod 16) bytes whose value shall also be 16 - (M mod 16).
    > Note that the pad is present when M is evenly divisible by 16;
    it contains 16 bytes of 0x10.
    """
    pass
