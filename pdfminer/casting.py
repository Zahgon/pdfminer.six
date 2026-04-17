import itertools
from typing import Any

from pdfminer.utils import Matrix, Rect

_FloatTriple = tuple[float, float, float]
_FloatQuadruple = tuple[float, float, float, float]


def safe_int(o: Any) -> int | None:
    pass


def safe_float(o: Any) -> float | None:
    pass


def safe_matrix(a: Any, b: Any, c: Any, d: Any, e: Any, f: Any) -> Matrix | None:
    pass


def safe_rgb(r: Any, g: Any, b: Any) -> tuple[float, float, float] | None:
    pass


def safe_cmyk(
    c: Any, m: Any, y: Any, k: Any
) -> tuple[float, float, float, float] | None:
    pass


def safe_rect_list(value: Any) -> Rect | None:
    pass


def safe_rect(a: Any, b: Any, c: Any, d: Any) -> Rect | None:
    pass


def _safe_float_triple(a: Any, b: Any, c: Any) -> _FloatTriple | None:
    pass


def _safe_float_quadruple(a: Any, b: Any, c: Any, d: Any) -> _FloatQuadruple | None:
    pass
