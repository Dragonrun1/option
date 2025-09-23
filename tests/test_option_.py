#  Copyright © 2025 Michael Cummings <mgcummings@yahoo.com>
#
#  Licensed under the MIT license
#  [MIT](https://opensource.org/license/mit-0).
#
#  Files in this project may not be copied, modified, or distributed except
#  according to those terms.
#
#  The full text of the license can be found in the project LICENSE.md file.
#
#  SPDX-License-Identifier: MIT
#
"""Tests for the Option type and helpers using pytest parametrize.

This suite verifies the behavior of the Option container and its helpers:

- Construction and factories:
  - Some, maybe, and the NONE singleton.
  - Guard against direct construction without _force.
  - Option.NONE() returns the singleton.

- Introspection and truthiness:
  - is_some, is_none, and bool().

- Extraction:
  - unwrap, value property, expect, unwrap_or, unwrap_or_else.

- Transformations:
  - map, flatmap, filter, map_or, map_or_else.

- Mapping access convenience:
  - get for mapping-like inner values, including default handling.

- Ordering, equality, hashing, and repr:
  - Comparisons among NONE and Some values.
  - Hash consistency with equality.
  - String representation of options.

The tests favor table-driven style via pytest.mark.parametrize (re-exported
as `parametrize` from conftest.py), to ensure broad coverage across input
combinations.
"""

import re

import pytest
from option.option_ import NONE, Option, Some, maybe

from .conftest import parametrize


@parametrize(
    "opt,is_some,is_none,truthy",
    [
        (Some(1), True, False, True),
        (Some(0), True, False, True),
        (NONE, False, True, False),
    ],
)
def test_truthiness_and_properties(opt, is_some, is_none, truthy):
    assert opt.is_some == is_some
    assert opt.is_none == is_none
    assert bool(opt) == truthy


@parametrize(
    "opt,expected",
    [
        (Some(1), 1),
        (Some("x"), "x"),
        (Some((1, 2)), (1, 2)),
        (Some(None), None),
    ],
    ids=[
        "some",
        "some_string",
        "some_tuple",
        "some_none",
    ],
)
def test_expect_with_some_values(opt, expected) -> None:
    assert opt.expect("boom") == expected


@parametrize(
    "opt, exception, msg",
    [
        (NONE, ValueError, "Value is NONE."),
        (NONE, ValueError, "Oop!"),
    ],
)
def test_expect_with_none_value(opt, exception, msg) -> None:
    with pytest.raises(exception, match=re.escape(msg)):
        opt.expect(msg)


@parametrize(
    "opt,expected",
    [
        (Some(10), 10),
        (Some("x"), "x"),
        (Some((1, 2)), (1, 2)),
    ],
)
def test_unwrap_and_value_success(opt, expected):
    assert opt.unwrap() == expected
    assert opt.value == expected


@parametrize("msg", ["boom", "custom error message", "Value is NONE."])
def test_unwrap_and_value_fail_and_expect(msg):
    # unwrap and value on NONE always raise a ValueError
    with pytest.raises(ValueError):
        _ = NONE.unwrap()
    with pytest.raises(ValueError):
        _ = NONE.value
    # expect uses provided message
    with pytest.raises(ValueError, match=re.escape(msg)):
        _ = NONE.expect(msg)


@parametrize(
    "opt,default,expected",
    [
        (Some(5), 99, 5),
        (NONE, 99, 99),
        (Some(0), "alt", 0),
        (NONE, "alt", "alt"),
    ],
)
def test_unwrap_or(opt, default, expected):
    assert opt.unwrap_or(default) == expected


@parametrize(
    "opt,expected",
    [
        (Some(5), 5),
        (NONE, 99),
    ],
)
def test_unwrap_or_else(opt, expected):
    assert opt.unwrap_or_else(lambda: 99) == expected


@parametrize(
    "opt,fn,expected",
    [
        (Some(3), lambda x: x * x, Some(9)),
        (Some("a"), str.upper, Some("A")),
        (NONE, lambda x: x, NONE),
    ],
)
def test_map(opt, fn, expected):
    res = opt.map(fn)
    assert (res is NONE) if expected is NONE else (res == expected)


# pylint: disable=unnecessary-lambda
@parametrize(
    "opt,fn,expected",
    [
        (Some(3), lambda x: Some(x + 1), Some(4)),
        (Some(3), lambda x: NONE, NONE),
        (NONE, lambda x: Some(x), NONE),
    ],
)
def test_flatmap(opt, fn, expected):
    res = opt.flatmap(fn)
    assert (res is NONE) if expected is NONE else (res == expected)


@parametrize(
    "opt,predicate,expected_is_some,expected_opt",
    [
        (Some(2), lambda x: x % 2 == 0, True, Some(2)),
        (Some(3), lambda x: x % 2 == 0, False, NONE),
        (NONE, lambda x: True, False, NONE),
        (NONE, lambda x: False, False, NONE),
    ],
)
def test_filter(opt, predicate, expected_is_some, expected_opt):
    res = opt.filter(predicate)
    assert res.is_some == expected_is_some
    assert (res is NONE) if expected_opt is NONE else (res == expected_opt)


@parametrize(
    "mapping,key,default,expected",
    [
        ({"a": 1}, "a", None, Some(1)),
        ({"a": None}, "a", 5, NONE),
        ({}, "missing", 7, Some(7)),
        ({}, "missing", None, NONE),
    ],
)
def test_get_on_some(mapping, key, default, expected):
    opt = Some(mapping)
    res = opt.get(key, default)
    assert (res is NONE) if expected is NONE else (res == expected)


@parametrize(
    "default,expected",
    [
        (None, NONE),
        (5, Some(5)),
        ("x", Some("x")),
    ],
)
def test_get_on_none(default, expected):
    res = NONE.get("anything", default)
    assert (res is NONE) if expected is NONE else (res == expected)


@parametrize(
    "opt,mapper,default,expected",
    [
        (Some(2), lambda x: x + 10, 99, 12),
        (NONE, lambda x: x + 10, 99, 99),
        (Some("a"), str.upper, "fallback", "A"),
        (NONE, str.upper, "fallback", "fallback"),
    ],
)
def test_map_or(opt, mapper, default, expected):
    assert opt.map_or(mapper, default) == expected


@parametrize(
    "opt,mapper,default_fn,expected",
    [
        (Some(2), lambda x: x * x, lambda: 99, 4),
        (NONE, lambda x: x * x, lambda: 99, 99),
    ],
)
def test_map_or_else(opt, mapper, default_fn, expected):
    assert opt.map_or_else(mapper, default_fn) == expected


@parametrize(
    "val,expected",
    [
        (None, NONE),
        (0, Some(0)),
        ("hi", Some("hi")),
    ],
)
def test_maybe(val, expected):
    assert (
        (maybe(val) is NONE) if expected is NONE else (maybe(val) == expected)
    )


# pylint: disable=too-many-arguments,too-many-positional-arguments
@parametrize(
    "lhs,rhs,eq,ne,lt,le,gt,ge",
    [
        (NONE, NONE, True, False, False, True, False, True),
        (NONE, Some(0), False, True, True, True, False, False),
        (Some(0), NONE, False, True, False, False, True, True),
        (Some(0), Some(1), False, True, True, True, False, False),
        (Some(1), Some(1), True, False, False, True, False, True),
        (Some(2), Some(1), False, True, False, False, True, True),
    ],
)
def test_comparisons(lhs, rhs, eq, ne, lt, le, gt, ge):
    assert (lhs == rhs) is eq
    assert (lhs != rhs) is ne
    assert (lhs < rhs) is lt
    assert (lhs <= rhs) is le
    assert (lhs > rhs) is gt
    assert (lhs >= rhs) is ge


@parametrize(
    "opt,expected_inner",
    [
        (NONE, None),
        (Some(1), 1),
        (Some("hi"), "hi"),
        (Some({"a": 1}), {"a": 1}),
    ],
)
def test_repr(opt, expected_inner):
    s = repr(opt)
    if opt is NONE:
        assert s == "NONE"
    else:
        # Relax formatting: just ensure it's Some(...) and contains inner repr
        assert s.startswith("Some(") and s.endswith(")")
        assert repr(expected_inner) in s


@parametrize(
    "a,b",
    [
        (NONE, Option.NONE()),
        (Some(1), Some(1)),
        (Some("x"), Some("x")),
    ],
)
def test_hash_consistency_when_equal(a, b):
    # Equality must imply hash equality
    assert a == b
    assert hash(a) == hash(b)


def test_constructor_guard_and_factories():
    with pytest.raises(TypeError):
        _ = Option(1, True)

    s = Some(42)
    assert s.is_some and s.unwrap() == 42

    n = Option.NONE()
    assert n is NONE
    assert n.is_none
