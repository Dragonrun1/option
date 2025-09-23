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
##############################################################################
"""Development scripts for running tests, building docs and linting.

This module provides command-line entry points for common development tasks:
  * test_main: Run pytest with configuration from pyproject.toml
  * docs_main: Build HTML documentation using Sphinx
  * lint_main: Run code quality checks using Ruff, Pylint, and Mypy
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: str | None = None) -> int:
    """Execute a system command and return its exit code.

    Args:
        cmd: List of command arguments where cmd[0] is the executable
        cwd: Optional working directory for command execution

    Returns:
        The command's exit code (0 for success, non-zero for failure)
    """
    exe = cmd[0]
    if shutil.which(exe) is None:
        print(
            f"[ERROR] Required command not found on PATH: {exe}",
            file=sys.stderr,
        )
        return 127
    print(f"[RUN] {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=False).returncode


def test_main() -> None:
    """Run pytest with configuration from pyproject.toml.

    Executes all project tests using pytest and exits with pytest's return code.
    """
    # Uses pytest configuration from pyproject.toml
    code = _run([sys.executable, "-m", "pytest"])
    sys.exit(code)


def docs_main() -> None:
    """Build HTML documentation using Sphinx.

    Use the ``conf.py`` and the ``*.rst`` files from the ``doc_src/`` directory
    to generate the html documentation to the ``docs/`` directory and exits with
    build command's return code.
    """
    # Build HTML docs into docs/
    doc_src = Path("doc_src")
    docs_dir = Path("docs")
    # Prefer module form to avoid relying on a specific sphinx-build path
    cmd = [
        sys.executable,
        "-m",
        "sphinx.cmd.build",
        "-b",
        "html",
        str(doc_src),
        str(docs_dir),
    ]
    code = _run(cmd)
    sys.exit(code)


def lint_main() -> None:
    """Run code quality checks using Ruff, Pylint and Mypy.

    Executes Ruff checks followed by Pylint on src and tests directories,
    then runs mypy type checking on the option module.
    Exits with 0 if all checks pass, 1 if any fail.
    """
    # Run Ruff first, then Pylint.
    # Aggregate exit status (non-zero if any fails).
    statuses: list[int] = [_run([sys.executable, "-m", "ruff", "check", "."])]

    # Pylint over src and tests if they exist
    targets = [p for p in ("src", "tests") if Path(p).exists()]
    if targets:
        statuses.append(_run([sys.executable, "-m", "pylint", *targets]))
    else:
        print("[WARN] No 'src' or 'tests' directory found; skipping pylint.")

    # Run mypy type checking
    statuses.append(_run([sys.executable, "-m", "mypy", "-p", "option"]))

    sys.exit(0 if all(code == 0 for code in statuses) else 1)
