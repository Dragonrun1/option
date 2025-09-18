# noqa: D100
# Copyright © 2018-2022 Peijun Ma
# Copyright © 2025 Michael Cummings <mgcummings@yahoo.com>
#
# Licensed under the MIT license
# [MIT](https:#opensource.org/license/mit-0)
#
# Files in this project may not be copied, modified, or distributed except
# according to those terms.
#
# The full test of the license can be found in the project LICENSE.md file.
#
# SPDX-License-Identifier: MIT
##############################################################################
"""Option and Result types for Python.

This package provides lightweight algebraic data types inspired by Rust's
``Option`` and ``Result`` for expressive, safe handling of absence and error
conditions.

Examples:
    Basic mapping with Option and Result:

        >>> from option import Some, NONE, Ok, Err
        >>> Some(2).map(lambda x: x + 1)
        Some(3)
        >>> Ok(2).map(lambda x: x + 1)
        Ok(3)

Attributes:
  *  ``__version__`` (str): Package version string.
  * ``NONE``: The empty Option singleton representing the absence of a value.

Classes:
  * ``Option``:
    Optional type with Some/NONE-like semantics supporting mapping, chaining,
    and pattern-like operations.
  * ``Result``:
    Disjoint union for success (Ok) or failure (Err) with combinators for
    transformation and flow control.

Functions:
  * ``Some``:
    Construct an Option containing a value.
  * ``Ok``:
    Construct a successful Result.
  * ``Err``:
    Construct an error Result.
  * ``maybe``:
    Convert an optional value (None or a concrete value) into an Option
    (``NONE`` or ``Some``).

See Also:
  * option.option_: ``Option`` implementation and utilities.
  * option.result: ``Result`` implementation and utilities.
"""

from .option_ import NONE, Option, Some, maybe
from .result import Err, Ok, Result

__version__ = "2.1.1"
__all__ = [
    "NONE",
    "Option",
    "Some",
    "maybe",
    "Result",
    "Ok",
    "Err",
    "__version__",
]
