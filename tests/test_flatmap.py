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

from option import NONE, Err, Ok, Some

from tests.conftest import parametrize


@parametrize(
    "option,maps,expected",
    [
        (Some(2), [lambda x: Some(x + 1)] * 2, Some(4)),
        (Some(2), [lambda x: Some(x + 1)] * 2 + [lambda x: NONE], NONE),
        (Some(2), [lambda x: NONE] + [lambda x: Some(x + 1)] * 2, NONE),
        (NONE, [lambda x: Some(x + 1)] * 2, NONE),
    ],
)
def test_option(option, maps, expected):
    for map_ in maps:
        option = option.flatmap(map_)
    assert option == expected


@parametrize(
    "result,maps,expected",
    [
        (Ok(2), [lambda x: Ok(x + 1)] * 2, Ok(4)),
        (Ok(2), [lambda x: Ok(x + 1)] * 2 + [lambda x: Err(x + 1)], Err(5)),
        (
            Ok(2),
            [lambda x: Ok(x + 1)] * 2
            + [lambda x: Err(x + 1)]
            + [lambda x: Ok(x + 1)],
            Err(5),
        ),
        (Ok(2), [lambda x: Err(x + 1)] + [lambda x: Ok(x + 1)] * 2, Err(3)),
        (Err(2), [lambda x: Ok(x + 1)] * 2, Err(2)),
        (Err(2), [lambda x: Ok(x + 1)] * 2 + [lambda x: Err(x + 1)], Err(2)),
        (
            Err(2),
            [lambda x: Ok(x + 1)] * 2
            + [lambda x: Err(x + 1)]
            + [lambda x: Ok(x + 1)],
            Err(2),
        ),
        (Err(2), [lambda x: Err(x + 1)] + [lambda x: Ok(x + 1)] * 2, Err(2)),
    ],
)
def test_result(result, maps, expected):
    for map_ in maps:
        result = result.flatmap(map_)
    assert result == expected
