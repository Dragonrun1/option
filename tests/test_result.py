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
##############################################################################
"""Unit tests for Result-oriented functionality in Python.

This module contains a suite of unit tests designed to validate the behavior and
utility of `Result` classes and their respective methods.
It ensures correctness in constructing Result instances (`Ok` and `Err` types),
conversion into Options, mapping capabilities, unwrapping of values, and proper
error handling.
The tests include parameterized cases to cover a comprehensive range of
scenarios, including edge cases and comparisons between `Ok` and `Err`
instances.

Several methods and functionalities are tested to ensure compliance with defined
behavior, such as conditions under which errors or values are extracted,
expectations raised, default values applied, or specific transformations
performed.

Each feature is rigorously validated to assess its correctness, including
ordering semantics, equality, and custom hash implementations to confirm
consistency in various use cases.
"""

import pytest
from option.option_ import NONE, Some
from option.result import Err, Ok, Result

from .conftest import parametrize


@parametrize(
    "constructor, value, is_ok_expected, repr_expected",
    [
        (Result.Ok, 1, True, "Ok(1)"),
        (Result.Err, "boom", False, "Err('boom')"),
        (Ok, 42, True, "Ok(42)"),
        (Err, 0, False, "Err(0)"),
    ],
)
def test_construction_and_repr(
    constructor, value, is_ok_expected, repr_expected
) -> None:
    res = constructor(value)
    assert res.is_ok == is_ok_expected
    assert res.is_err == (not is_ok_expected)
    assert bool(res) == is_ok_expected
    assert repr(res) == repr_expected


@parametrize(
    "res, expected_ok_opt, expected_err_opt",
    [
        (Ok(1), Some(1), NONE),
        (Err("e"), NONE, Some("e")),
    ],
)
def test_ok_err_option_conversions(
    res, expected_ok_opt, expected_err_opt
) -> None:
    assert res.ok() == expected_ok_opt
    assert res.err() == expected_err_opt


@parametrize(
    "res, mapper, expected",
    [
        (Ok(1), lambda x: x + 1, Ok(2)),
        (Ok("a"), lambda s: s.upper(), Ok("A")),
        (Err("e"), lambda x: x, Err("e")),
    ],
)
def test_map(res, mapper, expected) -> None:
    assert res.map(mapper) == expected


@parametrize(
    "res, mapper, expected",
    [
        (Ok(1), lambda e: e + 1, Ok(1)),
        (Err(2), lambda e: e + 1, Err(3)),
        (Err("a"), str.upper, Err("A")),
    ],
)
def test_map_err(res, mapper, expected) -> None:
    assert res.map_err(mapper) == expected


@parametrize(
    "res, mapper, expected",
    [
        (Ok(2), lambda x: Ok(x * x), Ok(4)),
        (Ok(2), lambda x: Err(x + 1), Err(3)),
        (Err(5), lambda x: Ok(x + 1), Err(5)),
    ],
)
def test_flatmap(res, mapper, expected) -> None:
    assert res.flatmap(mapper) == expected


@parametrize(
    "res, expected",
    [
        (Ok(10), 10),
        (Ok("x"), "x"),
    ],
)
def test_unwrap_ok(res, expected) -> None:
    assert res.unwrap() == expected


@parametrize(
    "res, match",
    [
        (Err(1), "1"),
        (Err("boom"), "boom"),
    ],
)
def test_unwrap_err_raises(res, match) -> None:
    with pytest.raises(ValueError, match=match):
        res.unwrap()


@parametrize(
    "res, expected",
    [
        (Err(1), 1),
        (Err("e"), "e"),
    ],
)
def test_unwrap_err_ok(res, expected) -> None:
    assert res.unwrap_err() == expected


@parametrize(
    "res, match",
    [
        (Ok(1), "1"),
        (Ok("good"), "good"),
    ],
)
def test_unwrap_err_on_ok_raises(res, match) -> None:
    with pytest.raises(ValueError, match=match):
        res.unwrap_err()


@parametrize(
    "res, msg, expected",
    [
        (Ok(2), "msg", 2),
    ],
)
def test_expect_ok(res, msg, expected) -> None:
    assert res.expect(msg) == expected


@parametrize(
    "res, msg",
    [
        (Err("bad"), "nope"),
        (Err(0), "zero"),
    ],
)
def test_expect_err_raises(res, msg) -> None:
    with pytest.raises(ValueError, match=str(msg)):
        res.expect(msg)


@parametrize(
    "res, msg, expected",
    [
        (Err(3), "boom", 3),
    ],
)
def test_expect_err_ok(res, msg, expected) -> None:
    assert res.expect_err(msg) == expected


@parametrize(
    "res, msg",
    [
        (Ok(3), "nope"),
        (Ok("x"), "bad"),
    ],
)
def test_expect_err_on_ok_raises(res, msg) -> None:
    with pytest.raises(ValueError, match=str(msg)):
        res.expect_err(msg)


@parametrize(
    "res, fallback, expected",
    [
        (Ok(1), 9, 1),
        (Err(1), 9, 9),
        (Err("e"), "f", "f"),
    ],
)
def test_unwrap_or(res, fallback, expected) -> None:
    assert res.unwrap_or(fallback) == expected


@parametrize(
    "res, func, expected",
    [
        (Ok(1), lambda e: e * 10, 1),
        (Err(2), lambda e: e * 10, 20),
        (Err("a"), str.upper, "A"),
    ],
)
def test_unwrap_or_else(res, func, expected) -> None:
    assert res.unwrap_or_else(func) == expected


def test_direct_constructor_disallowed() -> None:
    with pytest.raises(TypeError):
        Result(1, True)


# Ordering semantics:
# - When both are Ok: compare inner values.
# - When both are Err: compare inner values.
# - When kinds differ: Ok < Err (based on implementation rules).
@parametrize(
    "a, b, lt, le, gt, ge",
    [
        # same kind, inner comparison
        (Ok(1), Ok(2), True, True, False, False),
        (Ok(2), Ok(2), False, True, False, True),
        (Ok(3), Ok(2), False, False, True, True),
        (Err(1), Err(2), True, True, False, False),
        (Err(2), Err(2), False, True, False, True),
        (Err(3), Err(2), False, False, True, True),
        # cross kind: Ok < Err
        (Ok(1), Err(0), True, True, False, False),
        (Err(0), Ok(1), False, False, True, True),
    ],
)
# pylint: disable=too-many-positional-arguments
def test_ordering(a, b, lt, le, gt, ge) -> None:
    assert (a < b) is lt
    assert (a <= b) is le
    assert (a > b) is gt
    assert (a >= b) is ge


@parametrize(
    "a, b, expected_eq",
    [
        (Ok(1), Ok(1), True),
        (Err("x"), Err("x"), True),
        (Ok(1), Ok(2), False),
        (Err("x"), Err("y"), False),
        (Ok(1), Err(1), False),
    ],
)
def test_equality_and_hash(a, b, expected_eq) -> None:
    assert (a == b) is expected_eq
    assert (a != b) is (not expected_eq)
    if expected_eq:
        assert hash(a) == hash(b)


@parametrize(
    "res, expected_repr",
    [
        (Ok(1), "Ok(1)"),
        (Err("boom"), "Err('boom')"),
        (Ok([1, 2]), "Ok([1, 2])"),
    ],
)
def test_repr(res, expected_repr) -> None:
    assert repr(res) == expected_repr
