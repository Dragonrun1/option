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

import argparse
import contextlib
import os
import shutil
import sys
from pathlib import Path

from git import Repo
from option import Option

from _dev import _find_project_root, _run


@contextlib.contextmanager
def _working_directory(path: Path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def _build_sphinx(source: Path, output: Path, builder: str) -> int:
    """Run single-version Sphinx build using module form."""
    output.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "sphinx.cmd.build",
        "-b",
        builder,
        str(source),
        str(output),
    ]
    return _run(cmd)


def _build_sphinx_multiversion(source: Path, output: Path) -> int:
    """Run sphinx-multiversion build via module form.

    This will build documentation for the configured branches and tags
    as defined by sphinx-multiversion settings in conf.py.
    """
    output.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "sphinx_multiversion",
        str(source),
        str(output),
    ]
    return _run(cmd)


def _publish_gh_pages(root: Path, built_dir: Path) -> int:
    """Publish built docs to gh-pages branch using a git worktree.

    This keeps the main working tree clean and is safe to run in CI.
    """
    repo = Repo(root)
    ghp_dir = root / ".gh-pages"
    # Clean worktree dir if present
    if ghp_dir.exists():
        shutil.rmtree(ghp_dir, ignore_errors=True)
    ghp_dir.parent.mkdir(parents=True, exist_ok=True)

    # Prepare worktree tracking gh-pages (create/reset branch to current HEAD)
    # 'git worktree add -B gh-pages <dir>' creates or resets branch to current
    # HEAD
    repo.git.worktree("add", "-B", "gh-pages", str(ghp_dir))

    # Now ghp_dir is a checkout of gh-pages branch
    with _working_directory(ghp_dir):
        # Remove everything except .git
        for entry in ghp_dir.iterdir():
            if entry.name == ".git":
                continue
            if entry.is_dir():
                shutil.rmtree(entry, ignore_errors=True)
            else:
                entry.unlink(missing_ok=True)
        # Copy built docs into worktree root
        for item in built_dir.iterdir():
            dest = ghp_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        # Ensure a friendly landing page exists at the site root
        index_tpl = root / "doc_src" / "_templates" / "_index.html"
        if index_tpl.exists():
            shutil.copy2(index_tpl, ghp_dir / "index.html")
        # Ensure no Jekyll processing on GitHub Pages
        (ghp_dir / ".nojekyll").write_text("\n", encoding="utf-8")
        # Commit and push
        repo.git.add("-A")
        # Use a generic commit message; ignore if nothing to commit
        try:
            repo.git.commit("-m", "Update Sphinx docs")
        except Exception:
            # Nothing to commit
            pass
        # Push branch
        repo.git.push("origin", "gh-pages")
    # Clean up the worktree directory
    shutil.rmtree(ghp_dir, ignore_errors=True)
    return 0


def docs_main() -> None:
    """Build Sphinx documentation locally and optionally publish to gh-pages.

    Default local build places HTML under docs/main (safe for development).
    In CI, run with --publish to push the built site to the gh-pages branch.
    """
    parser = argparse.ArgumentParser(prog="dev-docs", add_help=True)
    parser.add_argument(
        "--builder",
        "-b",
        default="html",
        help="Sphinx builder (single-version only)",
    )
    parser.add_argument(
        "--source", "-s", default="doc_src", help="Sphinx source directory"
    )
    parser.add_argument(
        "--output", "-o", default="docs/main", help="Output directory"
    )
    mv_group = parser.add_mutually_exclusive_group()
    mv_group.add_argument(
        "--multiversion",
        dest="multiversion",
        action="store_true",
        help="Build using sphinx-multiversion (default)",
    )
    mv_group.add_argument(
        "--single",
        dest="multiversion",
        action="store_false",
        help="Build a single-version site with Sphinx",
    )
    # Note: no default here; we'll infer default based on --publish below
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish the built docs to gh-pages branch",
    )
    args = parser.parse_args()

    # Determine default build mode: multiversion for publish, single for local
    if getattr(args, "multiversion", None) is None:
        # If user did not specify --single/--multiversion explicitly
        args.multiversion = bool(args.publish)

    # Resolve project root
    root_opt: Option[Path] = _find_project_root()
    if root_opt.is_none:
        print("[ERROR] No project root found", file=sys.stderr)
        sys.exit(1)
    root: Path = root_opt.unwrap()

    source = (root / args.source).resolve()

    # If building multiversion and the default output is still in use,
    # place versions directly under docs/ (docs/main is for single-version).
    if args.multiversion and args.output == "docs/main":
        args.output = "docs"

    output = (root / args.output).resolve()

    if not source.exists():
        print(f"[ERROR] Sphinx source not found: {source}", file=sys.stderr)
        sys.exit(2)

    if args.multiversion:
        print("[RUN] Building Sphinx documentation (multiversion)")
        code = _build_sphinx_multiversion(source, output)
    else:
        print("[RUN] Building Sphinx documentation (single-version)")
        code = _build_sphinx(source, output, args.builder)
    if code != 0:
        sys.exit(code)

    if args.publish:
        print("[RUN] Publishing docs to gh-pages")
        # Verify this is a git repo
        git_dir = root / ".git"
        if not git_dir.exists():
            print(
                "[ERROR] Not a git repository; cannot publish", file=sys.stderr
            )
            sys.exit(3)
        pub_code = _publish_gh_pages(root, output)
        sys.exit(pub_code)

    sys.exit(0)
