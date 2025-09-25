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
from pathlib import Path

from _dev import _run


def lint_main() -> None:
    """Run code quality checks using Mypy, Pylint, Ruff, and Ty.

    Executes in order the following code quality checkers:
        * Ruff
        * Pylint
        * Mypy
        * Ty

    Each tool will use its configuration found in pyproject.toml.
    The tool exit statuses are aggregated to form a overall exit status.
    Exits with 0 if all checks pass, 1 if any fail.

    """
    # Run Ruff first.
    statuses: list[int] = [_run([sys.executable, "-m", "ruff", "check", "."])]

    # Pylint over src and tests directories if they exist using pyproject.toml
    # configuration.
    targets = [p for p in ("src", "tests") if Path(p).exists()]
    if targets:
        statuses.append(_run([sys.executable, "-m", "pylint", *targets]))
    else:
        print("[WARN] No 'src' or 'tests' directory found; skipping pylint.")

    # Run mypy type checking
    statuses.append(_run([sys.executable, "-m", "mypy", "-p", "option"]))

    # Run Ty type checking
    statuses.append(_run([sys.executable, "-m", "ty", "check"]))

    sys.exit(0 if all(code == 0 for code in statuses) else 1)
