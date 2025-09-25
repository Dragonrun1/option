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
# ##############################################################################
from __future__ import annotations

import sys

from _dev import _run


def test_main() -> None:
    """Run pytest with configuration from pyproject.toml.

    Executes all project tests using pytest and exits with pytest's return code.
    """
    # Uses pytest configuration from pyproject.toml
    code = _run([sys.executable, "-m", "pytest"])
    sys.exit(code)
