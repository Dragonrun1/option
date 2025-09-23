# Copyright © 2018-2022 Peijun Ma
# Copyright © 2025 Michael Cummings <mgcummings@yahoo.com>
#
# Licensed under the MIT license
# [MIT](https://opensource.org/license/mit-0)
#
# Files in this project may not be copied, modified, or distributed except
# according to those terms.
#
# The full text of the license can be found in the project LICENSE.md file.
#
# SPDX-License-Identifier: MIT
###############################################################################
# pylint: disable=R0903
"""Core protocols and type variable definitions for type hinting.

This module defines utility TypeVars for frequently used type hints and
provides Protocols representing objects that support comparison operations
through dunder methods (`__ge__`, `__gt__`, `__le__`, `__lt__`).

Classes:
 * SupportsDunderGE: Protocol for objects supporting `__ge__`
   (greater than or equal).
 * SupportsDunderGT: Protocol for objects supporting `__gt__`
   (greater than).
 * SupportsDunderLE: Protocol for objects supporting `__le__`
   (less than or equal).
 * SupportsDunderLT: Protocol for objects supporting `__lt__`
   (less than).

Raises:
    DeprecationWarning: If the Python version is lower than 3.12.

"""

import sys
from typing import TypeVar

if (3, 12) <= sys.version_info:
    from typing import Protocol
else:
    raise DeprecationWarning("Python 3.12 or higher is required.")

A = TypeVar("A")
E = TypeVar("E")
F = TypeVar("F")
K = TypeVar("K")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class SupportsDunderGE(Protocol):
    """Represents a protocol for objects that support the __ge__
    (greater than or equal to) operation.

    This class is designed to specify a contract for objects, ensuring that any
    object implementing this protocol includes a `__ge__` method.
    The `__ge__` method determines if the instance is greater than or equal to
    another object.
    This protocol is particularly useful when defining generic types or ensuring
    compatibility with certain operations that rely on the `__ge__` operator.
    """

    def __ge__(self, __other: object) -> bool: ...  # noqa: D105


class SupportsDunderGT(Protocol):
    """Protocol representing objects that support the greater-than (__gt__)
    operator.

    This class is part of the typing module's support for structural subtyping
    and is used as a marker for classes that implement the __gt__ method,
    allowing instances of these classes to be compared using the greater-than
    operator.

    Methods:
        __gt__: Enables comparison between objects, determining if the current
            object is greater than another.

    """

    def __gt__(self, __other: object) -> bool: ...  # noqa: D105


class SupportsDunderLE(Protocol):
    """Protocol to define objects that support the less than or equal to (`<=`)
    operator.

    This class represents a contract for implementing the `<=` operation for
    objects.
    Classes inheriting this protocol should provide an implementation for the
    `__le__` method, ensuring compatibility with the `<=` operator.
    It is typically used in scenarios where ordering constraints or comparisons
    between objects are required.
    """

    def __le__(self, __other: object) -> bool: ...  # noqa: D105


class SupportsDunderLT(Protocol):
    """Represents a protocol requiring implementation of the __lt__ method.

    The SupportsDunderLT protocol is designed to enforce the presence of the
    __lt__ ('less than') method for implementing comparison functionality in
    classes. This is useful when working with generics or ensuring a specific
    interface for objects that need to be comparable.
    """

    def __lt__(self, __other: object) -> bool: ...  # noqa: D105
