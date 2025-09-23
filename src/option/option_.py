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

"""Option type for explicit optional values.

This module defines a generic :class:`Option` container that models the presence
(:func:`Some`) or absence (:data:`NONE`) of a value.
It encourages explicit, type-safe handling of missing values without relying on
raw ``None`` checks.

Overview:
    * Container: :class:`Option[T]` with variants represented by truthiness
      (``Some(x)`` is truthy, :data:`NONE` is falsy).
    * Transformations: :meth:`Option.map`, :meth:`Option.flatmap`,
      :meth:`Option.filter`.
    * Extraction: :meth:`Option.unwrap`, :meth:`Option.unwrap_or`,
      :meth:`Option.unwrap_or_else`, :meth:`Option.expect`,
      :pyattr:`Option.value`.
    * Mapping access: :meth:`Option.get` when the inner value is a
      :class:`collections.abc.Mapping`.
    * Construction helpers: :func:`Some`, :func:`maybe`, and the singleton
      :data:`NONE`.

Public API:
    * :func:`maybe`: Construct ``Some(val)`` if ``val is not None``,
      otherwise :data:`NONE`.
    * :class:`Option[T]`: The core optional container.
    * :func:`Some`: Construct a ``Some`` value.
    * :data:`NONE`: The singleton representing the absence of a value.

Key behaviors:

Truthiness:
      >>> bool(Some(1)), bool(NONE)
      (True, False)

Unwrap and defaults:
      >>> Some(10).unwrap()
      10
      >>> NONE.unwrap_or(42)
      42
      >>> NONE.unwrap_or_else(lambda: "fallback")
      'fallback'
      >>> try:
      ...     NONE.unwrap()
      ... except ValueError as e:
      ...     print(e)
      Value is NONE.

Transformations:
      >>> Some(2).map(lambda x: x * x)
      Some(4)
      >>> Some(2).flatmap(lambda x: Some(x + 5))
      Some(7)
      >>> NONE.map(lambda x: x)
      NONE

Filtering:
      >>> Some(3).filter(lambda x: x % 2 == 1)
      Some(3)
      >>> Some(4).filter(lambda x: x % 2 == 1)
      NONE
      >>> NONE.filter(lambda _: True)
      NONE

Mapping access:
      >>> Some({"a": 1}).get("a")
      Some(1)
      >>> Some({}).get("a", 99)
      Some(99)
      >>> NONE.get("a", 5)
      Some(5)
      >>> NONE.get("a") is NONE
      True

Construction helpers:
      >>> Some("hi")
      Some('hi')
      >>> maybe(None) is NONE
      True
      >>> maybe(0)
      Some(0)

Notes:
    * Ordering: :data:`NONE` compares lower than any ``Some`` value; ``Some``
      instances order by their inner values when comparable.
    * The :class:`Option` constructor is internal; use :func:`Some`,
      :func:`maybe`, or :data:`NONE` instead.

"""

from typing import Any, Callable, Generic, Mapping, Optional, Union, cast

from option.types_ import (
    A,
    SupportsDunderGE,
    SupportsDunderGT,
    SupportsDunderLE,
    SupportsDunderLT,
    T,
    U,
    V,
)


class Option(Generic[T]):
    """:py:class:`Option` represents an optional value.

    Every :py:class:`Option` is either ``Some`` and contains a value, or
    :py:data:`NONE` and does not.

    To create a ``Some`` value, please use :py:meth:`Option.Some` or
    :py:func:`Some`.

    To create a :py:data:`NONE` value, please use :py:meth:`Option.NONE` or
    import the constant :py:data:`NONE` directly.

    To let :py:class:`Option` guess the type of :py:class:`Option` to create,
    please use :py:meth:`Option.maybe` or :py:func:`maybe`.

    Calling the ``__init__``  method directly will raise a ``TypeError``.

    Examples:
        >>> Option.Some(1)
        Some(1)
        >>> Option.NONE()
        NONE
        >>> Option.maybe(1)
        Some(1)
        >>> Option.maybe(None)
        NONE

    """

    __slots__ = ("_val", "_is_some", "_type")

    @classmethod
    def NONE(cls) -> "Option[T]":  # noqa N802
        """Shortcut method to :py:data:`NONE`."""
        return cast("Option[T]", NONE)

    @classmethod
    def Some(cls, val: T) -> "Option[T]":  # noqa N802
        """Some value ``val``."""
        return cls(val, True, _force=True)

    def expect(self, msg: object) -> T:
        """Unwraps the option. Raises an exception if the value is
        :py:data:`NONE`.

        Args:
            msg: The exception message.

        Returns:
            The wrapped value.

        Raises:
            ``ValueError`` with message provided by ``msg`` if the value is
            :py:data:`NONE`.

        Examples:
            >>> Some(0).expect("sd")
            0
            >>> try:
            ...     NONE.expect("Oh No!")
            ... except ValueError as e:
            ...     print(e)
            Oh No!

        """
        if self._is_some:
            return self._val
        raise ValueError(msg)

    def filter(self, predicate: Callable[[T], bool]) -> "Option[T]":
        """Returns :py:data:`NONE` if the :py:class:`Option` is :py:data:`NONE`,
        otherwise filter the contained value by ``predicate``.

        Args:
            predicate: The fitler function.

        Returns:
            :py:data:`NONE` if the contained value is :py:data:`NONE`,
            otherwise:
                * The option itself if the predicate returns True
                * :py:data:`NONE` if the predicate returns False

        Examples:
            >>> Some(0).filter(lambda x: x % 2 == 1)
            NONE
            >>> Some(1).filter(lambda x: x % 2 == 1)
            Some(1)
            >>> NONE.filter(lambda x: True)
            NONE

        """
        if self._is_some and predicate(self._val):
            return self
        return cast("Option[T]", NONE)

    def flatmap(self, callback: "Callable[[T], Option[U]]") -> "Option[U]":
        """Applies the callback to the contained value if the option
        is not :py:data:`NONE`.

        This is different from :py:meth:`Option.map` because the result
        of the callback isn't wrapped in a new :py:class:`Option`

        Args:
            callback: The callback to apply to the contained value.

        Returns:
            :py:data:`NONE` if the option is :py:data:`NONE`.

            Otherwise, calls `callback` with the contained value and
            returns the result.

        Examples:
            >>> def square(x):
            ...     return Some(x * x)
            >>> def nope(x):
            ...     return NONE
            >>> Some(2).flatmap(square).flatmap(square)
            Some(16)
            >>> Some(2).flatmap(square).flatmap(nope)
            NONE
            >>> Some(2).flatmap(nope).flatmap(square)
            NONE
            >>> NONE.flatmap(square).flatmap(square)
            NONE

        """
        return (
            callback(self._val)
            if self._is_some
            else cast("Option[U]", self.NONE())
        )

    def get(
        self: "Option[V]", key: Any, default: "Union[V, None]" = None
    ) -> "Option[V]":
        """Gets a mapping value by key in the contained value or returns
        ``default`` if the key doesn't exist.

        Args:
            key: The mapping key.
            default: The defauilt value.

        Returns:
            * ``Some`` variant of the mapping value if the key exists
               and the value is not None.
            * ``Some(default)`` if ``default`` is not None.
            * :py:data:`NONE` if ``default`` is None.

        Examples:
            >>> Some({"hi": 1}).get("hi")
            Some(1)
            >>> Some({}).get("hi", 12)
            Some(12)
            >>> NONE.get("hi", 12)
            Some(12)
            >>> NONE.get("hi")
            NONE

        """
        if not (self._is_some and isinstance(self._val, Mapping)):
            return self._type.maybe(default)
        return self._type.maybe(self._val.get(key, default))

    @property
    def is_none(self) -> bool:
        """Returns ``True`` if the option is a :py:data:`NONE` value.

        Examples:
            >>> Some(0).is_none
            False
            >>> NONE.is_none
            True

        """
        return not self._is_some

    @property
    def is_some(self) -> bool:
        """Returns ``True`` if the option is a ``Some`` value.

        Examples:
            >>> Some(0).is_some
            True
            >>> NONE.is_some
            False

        """
        return self._is_some

    def map(self, callback: Callable[[T], U]) -> "Option[U]":
        """Applies the ``callback`` with the contained value as its argument or
        returns :py:data:`NONE`.

        Args:
            callback: The callback to apply to the contained value.

        Returns:
            The ``callback`` result wrapped in an :class:`Option` if the
            contained value is ``Some``, otherwise :py:data:`NONE`

        Examples:
            >>> Some(10).map(lambda x: x * x)
            Some(100)
            >>> NONE.map(lambda x: x * x)
            NONE

        """
        if self._is_some:
            return cast(
                "Option[U]", self._type.Some(cast("T", callback(self._val)))
            )
        return cast("Option[U]", NONE)

    def map_or(self, callback: Callable[[T], U], default: A) -> Union[U, A]:
        """Applies the ``callback`` to the contained value or returns
        ``default``.

        Args:
            callback: The callback to apply to the contained value.
            default: The default value.

        Returns:
            The ``callback`` result if the contained value is ``Some``,
            otherwise ``default``.

        Notes:
            If you wish to use the result of a function call as ``default``,
            it is recommended to use :py:meth:`map_or_else` instead.

        Examples:
            >>> Some(0).map_or(lambda x: x + 1, 1000)
            1
            >>> NONE.map_or(lambda x: x * x, 1)
            1

        """
        return callback(self._val) if self._is_some else default

    def map_or_else(
        self, callback: Callable[[T], U], default: Callable[[], A]
    ) -> Union[U, A]:
        """Applies the ``callback`` to the contained value or computes a default
        with ``default``.

        Args:
            callback: The callback to apply to the contained value.
            default: The callback fot the default value.

        Returns:
            The ``callback`` result if the contained value is ``Some``,
            otherwise the result of ``default``.

        Examples:
            >>> Some(0).map_or_else(lambda x: x * x, lambda: 1)
            0
            >>> NONE.map_or_else(lambda x: x * x, lambda: 1)
            1

        """
        return callback(self._val) if self._is_some else default()

    @classmethod
    def maybe(cls, val: Optional[T]) -> "Option[T]":
        """Shortcut method to return ``Some`` or :py:data:`NONE` based on
        ``val``.

        Args:
            val: Some value.

        Returns:
            ``Some(val)`` if the ``val`` is not None, otherwise :py:data:`NONE`.

        Examples:
            >>> Option.maybe(0)
            Some(0)
            >>> Option.maybe(None)
            NONE

        """
        if val is None:
            return cls.NONE()
        return cls.Some(val)

    def unwrap(self) -> T:
        """Returns the value in the :py:class:`Option` if it is ``Some``.

        Returns:
            The ```Some`` value of the :py:class:`Option`.

        Raises:
            ``ValueError`` if the value is :py:data:`NONE`.

        Examples:
            >>> Some(0).unwrap()
            0
            >>> try:
            ...     NONE.unwrap()
            ... except ValueError as e:
            ...     print(e)
            Value is NONE.

        """
        return self.value

    def unwrap_or(self, default: U) -> Union[T, U]:
        """Returns the contained value or ``default``.

        Args:
            default: The default value.

        Returns:
            The contained value if the :py:class:`Option` is ``Some``,
            otherwise ``default``.

        Notes:
            If you wish to use a result of a function call as the default,
            it is recommended to use :py:meth:`unwrap_or_else` instead.

        Examples:
            >>> Some(0).unwrap_or(3)
            0
            >>> NONE.unwrap_or(0)
            0

        """
        return self.unwrap_or_else(lambda: default)

    def unwrap_or_else(self, callback: Callable[[], U]) -> Union[T, U]:
        """Returns the contained value or computes it from ``callback``.

        Args:
            callback: The default callback.

        Returns:
            The contained value if the :py:class:`Option` is ``Some``,
            otherwise ``callback()``.

        Examples:
            >>> Some(0).unwrap_or_else(lambda: 111)
            0
            >>> NONE.unwrap_or_else(lambda: "ha")
            'ha'

        """
        return self._val if self._is_some else callback()

    @property
    def value(self) -> T:
        """Property version of :py:meth:`unwrap`."""
        if self._is_some:
            return self._val
        raise ValueError("Value is NONE.")

    def __bool__(self) -> bool:
        return self._is_some

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self._type)
            and self._is_some == other._is_some
            and self._val == other._val
        )

    def __ge__(self: "Option[SupportsDunderGE]", other: object) -> bool:
        if isinstance(other, self._type):
            if self._is_some == other._is_some:
                return self._val >= other._val if self._is_some else True
            return self._is_some
        return NotImplemented

    def __gt__(self: "Option[SupportsDunderGT]", other: object) -> bool:
        if isinstance(other, self._type):
            if self._is_some == other._is_some:
                return self._val > other._val if self._is_some else False
            return self._is_some
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.__class__, self._is_some, self._val))

    def __init__(
        self, value: T, is_some: bool, *, _force: bool = False
    ) -> None:
        """Initialize an :class:`Option` instance (internal-only).

        **WARNING**
            This constructor is not part of the public API.
            Prefer using the factory helpers :func:`Some`, :meth:`Option.maybe`,
            or the :py:data:`NONE` singleton instead.
            Direct calls are rejected unless ``_force`` is explicitly set to
            ``True`` by internal helpers.

        Args:
            value (T): The inner value when ``is_some`` is ``True``;
                ignored when ``is_some`` is ``False``.
            is_some (bool): Whether this instance represents a ``Some`` value
                (``True``) or :py:data:`NONE` (``False``).
            _force (bool, keyword-only): Internal escape hatch used by factory
                helpers to bypass the guard.
                Must be ``True`` for direct construction.

        Raises:
            TypeError: If called directly with ``_force`` set to ``False``.

        Notes:
            Public construction should go through :func:`Some`,
            :meth:`Option.maybe`, or the :py:data:`NONE` singleton.

        Examples:
            Correct usage via factories:
                >>> Some(1)
                Some(1)
                >>> Option.maybe(None) is NONE
                True

            Incorrect direct construction:

            >>> try:
            ...     Option(1, True)
            ... except TypeError as e:
            ...     print("TypeError" in str(e))
            False
        """
        if not _force:
            raise TypeError(
                "Cannot directly initialize, "
                "please use one of the factory functions instead."
            )
        self._val = value
        self._is_some = is_some
        self._type = type(self)

    def __le__(self: "Option[SupportsDunderLE]", other: object) -> bool:
        if isinstance(other, self._type):
            if self._is_some == other._is_some:
                return self._val <= other._val if self._is_some else True
            return other._is_some
        return NotImplemented

    def __lt__(self: "Option[SupportsDunderLT]", other: object) -> bool:
        if isinstance(other, self._type):
            if self._is_some == other._is_some:
                return self._val < other._val if self._is_some else False
            return other._is_some
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return (
            not isinstance(other, self._type)
            or self._is_some != other._is_some
            or self._val != other._val
        )

    def __repr__(self) -> str:
        return "NONE" if self.is_none else f"Some({self._val!r})"


def maybe(val: Optional[T]) -> Option[T]:
    """Shortcut function to :py:meth:`Option.maybe`."""
    return Option.maybe(val)


NONE = Option(None, False, _force=True)
"""Singleton representing the absence of a value."""


def Some(val: T) -> Option[T]:  # noqa N802
    """Shortcut function to :py:meth:`Option.Some`."""
    return Option.Some(val)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
