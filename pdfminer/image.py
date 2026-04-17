import os
import os.path
import struct
from io import BytesIO
from typing import BinaryIO, Literal

from pdfminer.jbig2 import JBIG2StreamReader, JBIG2StreamWriter
from pdfminer.layout import LTImage
from pdfminer.pdfcolor import (
    LITERAL_DEVICE_CMYK,
    LITERAL_DEVICE_GRAY,
    LITERAL_DEVICE_RGB,
    LITERAL_INLINE_DEVICE_GRAY,
    LITERAL_INLINE_DEVICE_RGB,
)
from pdfminer.pdfexceptions import PDFValueError
from pdfminer.pdftypes import (
    LITERALS_DCT_DECODE,
    LITERALS_FLATE_DECODE,
    LITERALS_JBIG2_DECODE,
    LITERALS_JPX_DECODE,
)

PIL_ERROR_MESSAGE = (
    "Could not import Pillow. This dependency of pdfminer.six is not "
    "installed by default. You need it to to save jpg images to a file. Install it "
    "with `pip install 'pdfminer.six[image]'`"
)


def align32(x: int) -> int:
    pass


class BMPWriter:
    def __init__(self, fp: BinaryIO, bits: int, width: int, height: int) -> None:
        self.fp = fp
        self.bits = bits
        self.width = width
        self.height = height
        if bits == 1:
            ncols = 2
        elif bits == 8:
            ncols = 256
        elif bits == 24:
            ncols = 0
        else:
            raise PDFValueError(bits)
        self.linesize = align32((self.width * self.bits + 7) // 8)
        self.datasize = self.linesize * self.height
        headersize = 14 + 40 + ncols * 4
        info = struct.pack(
            "<IiiHHIIIIII",
            40,
            self.width,
            self.height,
            1,
            self.bits,
            0,
            self.datasize,
            0,
            0,
            ncols,
            0,
        )
        assert len(info) == 40, str(len(info))
        header = struct.pack(
            "<ccIHHI",
            b"B",
            b"M",
            headersize + self.datasize,
            0,
            0,
            headersize,
        )
        assert len(header) == 14, str(len(header))
        self.fp.write(header)
        self.fp.write(info)
        if ncols == 2:
            # B&W color table
            for i in (0, 255):
                self.fp.write(struct.pack("BBBx", i, i, i))
        elif ncols == 256:
            # grayscale color table
            for i in range(256):
                self.fp.write(struct.pack("BBBx", i, i, i))
        self.pos0 = self.fp.tell()
        self.pos1 = self.pos0 + self.datasize

    def write_line(self, y: int, data: bytes) -> None:
        pass


class ImageWriter:
    """Write image to a file

    Supports various image types: JPEG, JBIG2 and bitmaps
    """

    def __init__(self, outdir: str) -> None:
        self.outdir = outdir
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

    def export_image(self, image: LTImage) -> str:
        """Save an LTImage to disk"""
        pass

    def _save_jpeg(self, image: LTImage) -> str:
        """Save a JPEG encoded image"""
        pass

    def _save_jpeg2000(self, image: LTImage) -> str:
        """Save a JPEG 2000 encoded image"""
        pass

    def _save_jbig2(self, image: LTImage) -> str:
        """Save a JBIG2 encoded image"""
        pass

    def _save_bmp(
        self,
        image: LTImage,
        width: int,
        height: int,
        bytes_per_line: int,
        bits: int,
    ) -> str:
        """Save a BMP encoded image"""
        pass

    def _save_bytes(self, image: LTImage) -> str:
        """Save an image without encoding, just bytes"""
        pass

    def _save_raw(self, image: LTImage) -> str:
        """Save an image with unknown encoding"""
        pass

    @staticmethod
    def _is_jbig2_iamge(image: LTImage) -> bool:
        pass

    def _create_unique_image_name(self, image: LTImage, ext: str) -> tuple[str, str]:
        pass
