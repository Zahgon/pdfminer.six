"""Functions that can be used for the most common use-cases for pdfminer.six"""

import logging
import sys
from collections.abc import Container, Iterator
from io import StringIO
from typing import Any, BinaryIO, cast

from pdfminer.converter import (
    HOCRConverter,
    HTMLConverter,
    PDFPageAggregator,
    TextConverter,
    XMLConverter,
)
from pdfminer.image import ImageWriter
from pdfminer.layout import LAParams, LTPage
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfexceptions import PDFValueError
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.utils import AnyIO, FileOrName, open_filename


def extract_text_to_fp(
    inf: BinaryIO,
    outfp: AnyIO,
    output_type: str = "text",
    codec: str = "utf-8",
    laparams: LAParams | None = None,
    maxpages: int = 0,
    page_numbers: Container[int] | None = None,
    password: str = "",
    scale: float = 1.0,
    rotation: int = 0,
    layoutmode: str = "normal",
    output_dir: str | None = None,
    strip_control: bool = False,
    debug: bool = False,
    disable_caching: bool = False,
    **kwargs: Any,
) -> None:
    """Parses text from inf-file and writes to outfp file-like object.

    Takes loads of optional arguments but the defaults are somewhat sane.
    Beware laparams: Including an empty LAParams is not the same as passing
    None!

    :param inf: a file-like object to read PDF structure from, such as a
        file handler (using the builtin `open()` function) or a `BytesIO`.
    :param outfp: a file-like object to write the text to.
    :param output_type: May be 'text', 'xml', 'html', 'hocr', 'tag'.
        Only 'text' works properly.
    :param codec: Text decoding codec
    :param laparams: An LAParams object from pdfminer.layout. Default is None
        but may not layout correctly.
    :param maxpages: How many pages to stop parsing after
    :param page_numbers: zero-indexed page numbers to operate on.
    :param password: For encrypted PDFs, the password to decrypt.
    :param scale: Scale factor
    :param rotation: Rotation factor
    :param layoutmode: Default is 'normal', see
        pdfminer.converter.HTMLConverter
    :param output_dir: If given, creates an ImageWriter for extracted images.
    :param strip_control: Does what it says on the tin
    :param debug: Output more logging data
    :param disable_caching: Does what it says on the tin
    :param other:
    :return: nothing, acting as it does on two streams. Use StringIO to get
        strings.
    """
    pass


def extract_text(
    pdf_file: FileOrName,
    password: str = "",
    page_numbers: Container[int] | None = None,
    maxpages: int = 0,
    caching: bool = True,
    codec: str = "utf-8",
    laparams: LAParams | None = None,
) -> str:
    """Parse and return the text contained in a PDF file.

    :param pdf_file: Either a file path or a file-like object for the PDF file
        to be worked on.
    :param password: For encrypted PDFs, the password to decrypt.
    :param page_numbers: List of zero-indexed page numbers to extract.
    :param maxpages: The maximum number of pages to parse
    :param caching: If resources should be cached
    :param codec: Text decoding codec
    :param laparams: An LAParams object from pdfminer.layout. If None, uses
        some default settings that often work well.
    :return: a string containing all of the text extracted.
    """
    pass


def extract_pages(
    pdf_file: FileOrName,
    password: str = "",
    page_numbers: Container[int] | None = None,
    maxpages: int = 0,
    caching: bool = True,
    laparams: LAParams | None = None,
) -> Iterator[LTPage]:
    """Extract and yield LTPage objects

    :param pdf_file: Either a file path or a file-like object for the PDF file
        to be worked on.
    :param password: For encrypted PDFs, the password to decrypt.
    :param page_numbers: List of zero-indexed page numbers to extract.
    :param maxpages: The maximum number of pages to parse
    :param caching: If resources should be cached
    :param laparams: An LAParams object from pdfminer.layout. If None, uses
        some default settings that often work well.
    :return: LTPage objects
    """
    pass
