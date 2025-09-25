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

import contextlib
import os
import shutil
import sys
from pathlib import Path

from git import Repo
from option import Option

from _dev import _find_project_root, _run


@contextlib.contextmanager
def _working_directory(path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def docs_main() -> None:
    """Build HTML documentation using Sphinx.

    Use the ``conf.py`` and the ``*.rst`` files from the ``doc_src/`` directory
    to generate the html documentation to the ``docs/`` directory and exits with
    build command's return code.
    """
    print("[RUN] Building HTML documentation using Sphinx")
    # Get project root to use as git base path.
    root: Option[Path] = _find_project_root()
    if root.is_none:
        print("[ERROR] No project root found", file=sys.stderr)
        sys.exit(1)
    root: Path = root.unwrap()
    git_base: Path = root.joinpath(".git")
    if not (git_base.exists() and git_base.is_dir()):
        print("[ERROR] Git root not found", file=sys.stderr)
        sys.exit(1)
    # Get Sphinx paths.
    doc_src: Path = git_base / "doc_src"
    docs_dir: Path = git_base / "docs"

    # First clean the output directory with shutil.
    shutil.rmtree(docs_dir, ignore_errors=True)

    repo = Repo(git_base)

    with _working_directory(docs_dir):
        repo.git.checkout("--orphan", "gh-pages")
        repo.git.reset("--hard")
        repo.git.commit("--allow-empty", "-m", "Initial gh-pages commit")
        repo.git.push("origin", "gh-pages")
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
