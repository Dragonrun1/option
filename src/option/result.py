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
"""Result type utilities for explicit success/error handling.

This module defines a generic :class:`Result` that represents either success
(:meth:`Result.Ok`) or failure (:meth:`Result.Err`). It provides ergonomic,
exception-free workflows for transforming and extracting values, inspired by
Rust’s ``Result``.

Exports:
  * :class:`Result` — The core container type.
  * :func:`Ok` — Convenience constructor for a success result.
  * :func:`Err` — Convenience constructor for an error result.

Highlights:
  * Introspection: :pyattr:`Result.is_ok`, :pyattr:`Result.is_err`,
    truthiness (``Ok`` is truthy).
  * Conversions: :meth:`Result.ok` and :meth:`Result.err` interoperate with
    :class:`option.option_.Option`.
  * Transformations: :meth:`Result.map`, :meth:`Result.flatmap`,
    :meth:`Result.map_err`.
  * Extraction: :meth:`Result.unwrap`, :meth:`Result.unwrap_or`,
    :meth:`Result.unwrap_or_else`, :meth:`Result.expect`,
    :meth:`Result.unwrap_err`, :meth:`Result.expect_err`.

The API is fully type-annotated and designed to integrate cleanly with static
type checkers and functional-style workflows.

Examples:
    Basic creation:

    >>> Ok(42)
    Ok(42)
    >>> Err("boom")
    Err('boom')

    Mapping and unwrapping:

    >>> Ok(2).map(lambda x: x + 3).unwrap()
    5
    >>> Err("nope").unwrap_or(10)
    10
"""

from typing import Any, Callable, Generic, Union

from option.option_ import NONE, Option
from option.types_ import (
    E,
    F,
    SupportsDunderGE,
    SupportsDunderGT,
    SupportsDunderLE,
    SupportsDunderLT,
    T,
    U,
)


class Result(Generic[T, E]):
    """:class:`Result` is a type that either success (:meth:`Result.Ok`)
    or failure (:meth:`Result.Err`).

    To create an Ok value, use :meth:`Result.Ok` or :func:`Ok`.

    To create an Err value, use :meth:`Result.Err` or :func:`Err`.

    Calling the :class:`Result` constructor directly will raise a ``TypeError``.

    Examples:
        >>> Result.Ok(1)
        Ok(1)
        >>> Result.Err("Fail!")
        Err('Fail!')
    """

    __slots__ = ("_val", "_is_ok", "_type")

    def __init__(
        self, val: Union[T, E], is_ok: bool, *, _force: bool = False
    ) -> None:
        """Low-level initializer for :class:`Result`.

        This initializer is internal. Use :meth:`Result.Ok`, :meth:`Result.Err`,
        :func:`Ok`, or :func:`Err` instead.

        Args:
            val: The wrapped success (``T``) or error (``E``) value.
            is_ok: True if ``val`` represents success; False if it is an error.
            _force: Internal switch that allows construction.

        Raises:
            TypeError: If called without ``_force=True``.

        Examples:
            Attempting direct initialization:

            >>> try:
            ...     Result(1, True)
            ... except TypeError as e:
            ...     print("TypeError" in str(e))
            True
        """
        if not _force:
            raise TypeError(
                "Cannot directly initialize, "
                "please use one of the factory functions instead."
            )
        self._val = val
        self._is_ok = is_ok
        self._type = type(self)

    # noinspection PyPep8Naming
    @classmethod
    def Err(cls, err: E) -> "Result[Any, E]":
        """Contains the error value.

        Args:
            err: The error value.

        Returns:
            The :class:`Result` containing the error value.

        Examples:
            >>> res = Result.Err("Oh No")
            >>> res
            Err('Oh No')
            >>> res.is_err
            True

        """
        return cls(err, False, _force=True)

    # noinspection PyPep8Naming
    @classmethod
    def Ok(cls, val: T) -> "Result[T, Any]":
        """Create a success result.

        Args:
            val (T): The success value.

        Returns:
             The :class:`Result` containing the success value.

        Examples:
            >>> res = Result.Ok(1)
            >>> res
            Ok(1)
            >>> res.is_ok
            True

        """
        return cls(val, True, _force=True)

    def err(self) -> Option[E]:
        """Converts from :class:`Result` [T, E] to
        :class:`option.option_.Option` [E].

        Returns:
            :class:`Option` containing the error value if `self` is
            :meth:`Result.Err`, otherwise :data:`option.option_.NONE`.

        Examples:
            >>> Ok(1).err()
            NONE
            >>> Err(1).err()
            Some(1)

        """
        return NONE if self._is_ok else Option.Some(self._val)  # type: ignore

    def expect(self, msg: object) -> T:
        """Returns the success value in the :class:`Result` or raises
        a ``ValueError`` with a provided message.

        Args:
            msg: The error message.

        Returns:
            The success value in the :class:`Result` if it is
            a :meth:`Result.Ok` value.

        Raises:
            ``ValueError`` with ``msg`` as the message if the
            :class:`Result` is a :meth:`Result.Err` value.

        Examples:
            >>> Ok(1).expect("no")
            1
            >>> try:
            ...     Err(1).expect("no")
            ... except ValueError as e:
            ...     print(e)
            no

        """
        if self._is_ok:
            return self._val  # type: ignore
        raise ValueError(msg)

    def expect_err(self, msg: object) -> E:
        """Returns the error value in a :class:`Result`, or raises a
        ``ValueError`` with the provided message.

        Args:
            msg: The error message.

        Returns:
            The error value in the :class:`Result` if it is a
            :meth:`Result.Err` value.

        Raises:
            ``ValueError`` with the message provided by ``msg`` if
            the :class:`Result` is a :meth:`Result.Ok` value.

        Examples:
            >>> try:
            ...     Ok(1).expect_err("Oh No")
            ... except ValueError as e:
            ...     print(e)
            Oh No
            >>> Err(1).expect_err("Yes")
            1

        """
        if self._is_ok:
            raise ValueError(msg)
        return self._val  # type: ignore

    def flatmap(self, op: "Callable[[T], Result[U, E]]") -> "Result[U, E]":
        """Applies a function to the contained :meth:`Result.Ok` value.

        This is different from :meth:`Result.map` because the function
        result is not wrapped in a new :class:`Result`.

        Args:
            op: The function to apply to the contained :meth:`Result.Ok` value.

        Returns:
            The result of the function if `self` is an :meth:`Result.Ok` value,
             otherwise returns `self`.

        Examples:
            >>> def sq(x):
            ...     return Ok(x * x)
            >>> def err(x):
            ...     return Err(x)
            >>> Ok(2).flatmap(sq).flatmap(sq)
            Ok(16)
            >>> Ok(2).flatmap(sq).flatmap(err)
            Err(4)
            >>> Ok(2).flatmap(err).flatmap(sq)
            Err(2)
            >>> Err(3).flatmap(sq).flatmap(sq)
            Err(3)

        """
        return op(self._val) if self._is_ok else self  # type: ignore

    @property
    def is_err(self) -> bool:
        """Returns `True` if the result is :meth:`Result.Err`.

        Examples:
            >>> Ok(1).is_err
            False
            >>> Err(1).is_err
            True

        """
        return not self._is_ok

    @property
    def is_ok(self) -> bool:
        """Returns `True` if the result is :meth:`Result.Ok`.

        Examples:
            >>> Ok(1).is_ok
            True
            >>> Err(1).is_ok
            False

        """
        return self._is_ok

    def map(self, op: Callable[[T], U]) -> "Union[Result[U, E], Result[T, E]]":
        """Applies a function to the contained :meth:`Result.Ok` value.

        Args:
            op: The function to apply to the :meth:`Result.Ok` value.

        Returns:
            A :class:`Result` with its success value as the function result
            if `self` is an :meth:`Result.Ok` value, otherwise returns
            `self`.

        Examples:
            >>> Ok(1).map(lambda x: x * 2)
            Ok(2)
            >>> Err(1).map(lambda x: x * 2)
            Err(1)

        """
        return self._type.Ok(op(self._val)) if self._is_ok else self  # type: ignore

    def map_err(
        self, op: Callable[[E], F]
    ) -> "Union[Result[T, F], Result[T, E]]":
        """Applies a function to the contained :meth:`Result.Err` value.

        Args:
            op: The function to apply to the :meth:`Result.Err` value.

        Returns:
            A :class:`Result` with its error value as the function result
            if `self` is a :meth:`Result.Err` value, otherwise returns
            `self`.

        Examples:
            >>> Ok(1).map_err(lambda x: x * 2)
            Ok(1)
            >>> Err(1).map_err(lambda x: x * 2)
            Err(2)

        """
        return self if self._is_ok else self._type.Err(op(self._val))  # type: ignore

    def ok(self) -> Option[T]:
        """Converts from :class:`Result` [T, E] to
        :class:`option.option_.Option` [T].

        Returns:
            :class:`Option` containing the success value if `self` is
            :meth:`Result.Ok`, otherwise :data:`option.option_.NONE`.

        Examples:
            >>> Ok(1).ok()
            Some(1)
            >>> Err(1).ok()
            NONE

        """
        return Option.Some(self._val) if self._is_ok else NONE  # type: ignore

    def unwrap(self) -> T:
        """Returns the success value in the :class:`Result`.

        Returns:
            The success value in the :class:`Result`.

        Raises:
            ``ValueError`` with the message provided by the error value
             if the :class:`Result` is a :meth:`Result.Err` value.

        Examples:
            >>> Ok(1).unwrap()
            1
            >>> try:
            ...     Err(1).unwrap()
            ... except ValueError as e:
            ...     print(e)
            1

        """
        if self._is_ok:
            return self._val  # type: ignore
        raise ValueError(self._val)

    def unwrap_err(self) -> E:
        """Returns the error value in a :class:`Result`.

        Returns:
            The error value in the :class:`Result` if it is a
            :meth:`Result.Err` value.

        Raises:
            ``ValueError`` with the message provided by the success value
             if the :class:`Result` is a :meth:`Result.Ok` value.

        Examples:
            >>> try:
            ...     Ok(1).unwrap_err()
            ... except ValueError as e:
            ...     print(e)
            1
            >>> Err("Oh No").unwrap_err()
            'Oh No'

        """
        if self._is_ok:
            raise ValueError(self._val)
        return self._val  # type: ignore

    def unwrap_or(self, optb: T) -> T:
        """Returns the success value in the :class:`Result` or ``optb``.

        Args:
            optb: The default return value.

        Returns:
            The success value in the :class:`Result` if it is a
            :meth:`Result.Ok` value, otherwise ``optb``.

        Notes:
            If you wish to use a result of a function call as the default,
            it is recommnded to use :meth:`unwrap_or_else` instead.

        Examples:
            >>> Ok(1).unwrap_or(2)
            1
            >>> Err(1).unwrap_or(2)
            2

        """
        return self._val if self._is_ok else optb  # type: ignore

    def unwrap_or_else(self, op: Callable[[E], U]) -> Union[T, U]:
        """Returns the sucess value in the :class:`Result` or computes a default
        from the error value.

        Args:
            op: The function to computes default with.

        Returns:
            The success value in the :class:`Result` if it is
             a :meth:`Result.Ok` value, otherwise ``op(E)``.

        Examples:
            >>> Ok(1).unwrap_or_else(lambda e: e * 10)
            1
            >>> Err(1).unwrap_or_else(lambda e: e * 10)
            10

        """
        return self._val if self._is_ok else op(self._val)  # type: ignore

    def __bool__(self) -> bool:  # noqa: D105
        return self._is_ok

    def __eq__(self, other: object) -> bool:  # noqa: D105
        return (
            isinstance(other, self._type)
            and self._is_ok == other._is_ok
            and self._val == other._val
        )

    def __ge__(  # noqa: D105
        self: "Result[SupportsDunderGE, SupportsDunderGE]", other: object
    ) -> bool:
        if isinstance(other, self._type):
            if self._is_ok == other._is_ok:
                return self._val >= other._val
            return other._is_ok
        return NotImplemented

    def __gt__(  # noqa: D105
        self: "Result[SupportsDunderGT, SupportsDunderGT]", other: object
    ) -> bool:
        if isinstance(other, self._type):
            if self._is_ok == other._is_ok:
                return self._val > other._val
            return other._is_ok
        return NotImplemented

    def __hash__(self) -> int:  # noqa: D105
        return hash((self._type, self._is_ok, self._val))

    def __le__(  # noqa: D105
        self: "Result[SupportsDunderLE, SupportsDunderLE]", other: object
    ) -> bool:
        if isinstance(other, self._type):
            if self._is_ok == other._is_ok:
                return self._val <= other._val
            return self._is_ok
        return NotImplemented

    def __lt__(  # noqa: D105
        self: "Result[SupportsDunderLT, SupportsDunderLT]", other: object
    ) -> bool:
        if isinstance(other, self._type):
            if self._is_ok == other._is_ok:
                return self._val < other._val
            return self._is_ok
        return NotImplemented

    def __ne__(self, other: object) -> bool:  # noqa: D105
        return (
            not isinstance(other, self._type)
            or self._is_ok != other._is_ok
            or self._val != other._val
        )

    def __repr__(self) -> str:  # noqa: D105
        return f"Ok({self._val!r})" if self._is_ok else f"Err({self._val!r})"


# noinspection PyPep8Naming
def Ok(val: T) -> Result[T, Any]:
    """Shortcut function for :meth:`Result.Ok`."""
    return Result.Ok(val)


# noinspection PyPep8Naming
def Err(err: E) -> Result[Any, E]:
    """Shortcut function for :meth:`Result.Err`."""
    return Result.Err(err)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
