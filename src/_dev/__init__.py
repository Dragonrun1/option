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
################################################################################
"""Development scripts for running tests, building docs and linting.

This module provides command-line entry points for common development tasks:
  * test_main: Run pytest with configuration from pyproject.toml
  * docs_main: Build HTML documentation using Sphinx
  * lint_main: Run code quality checks using Mypy, Pylint, Ruff, and Ty
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.append("..")
# noinspection PyUnresolvedReferences
from option import Option, Some


def _find_project_root() -> Option:
    """Find the project root directory."""
    fp = Path(__file__)
    target = "pyproject.toml"
    for parent in fp.parents:
        file_path = parent / target
        if file_path.exists() and file_path.is_file():
            return Some(file_path.parent)
    return Option.NONE()


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


__all__ = [
    _find_project_root,
    _run,
]
