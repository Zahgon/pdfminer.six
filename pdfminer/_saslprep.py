# Copyright 2016-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Some changes copyright 2021-present Matthias Valvekens,
# licensed under the license of the pyHanko project (see LICENSE file).


"""An implementation of RFC4013 SASLprep."""

__all__ = ["saslprep"]

import stringprep
import unicodedata
from collections.abc import Callable

from pdfminer.pdfexceptions import PDFValueError

# RFC4013 section 2.3 prohibited output.
_PROHIBITED: tuple[Callable[[str], bool], ...] = (
    # A strict reading of RFC 4013 requires table c12 here, but
    # characters from it are mapped to SPACE in the Map step. Can
    # normalization reintroduce them somehow?
    stringprep.in_table_c12,
    stringprep.in_table_c21_c22,
    stringprep.in_table_c3,
    stringprep.in_table_c4,
    stringprep.in_table_c5,
    stringprep.in_table_c6,
    stringprep.in_table_c7,
    stringprep.in_table_c8,
    stringprep.in_table_c9,
)


def saslprep(data: str, prohibit_unassigned_code_points: bool = True) -> str:
    """An implementation of RFC4013 SASLprep.
    :param data:
        The string to SASLprep.
    :param prohibit_unassigned_code_points:
        RFC 3454 and RFCs for various SASL mechanisms distinguish between
        `queries` (unassigned code points allowed) and
        `stored strings` (unassigned code points prohibited). Defaults
        to ``True`` (unassigned code points are prohibited).
    :return: The SASLprep'ed version of `data`.
    """
    pass
