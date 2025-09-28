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
from git.exc import GitCommandError

sys.path.append("..")
# noinspection PyUnresolvedReferences
from option import Err, Ok, Option, Result

from . import _find_project_root, _run


def _mirror_directory(source: Path, dest: Path) -> Result:
    if not source.is_dir():
        print(f"{source} is not a directory")
        return Err(NotADirectoryError(source))
    if not dest.is_dir():
        print(f"{dest} is not a directory")
        return Err(NotADirectoryError(dest))
    # Copy all directories and files from source/ to dest/
    shutil.copytree(source, dest, dirs_exist_ok=True)
    # Remove any files or directories not found in source/ from dest/
    for root, directories, files in dest.walk(top_down=False):
        # Remove the files first then the now empty directories.
        for file in files:
            file_path = root / file
            if not (source / file_path.relative_to(dest)).exists():
                print(f"Unlink {file_path}")
                file_path.unlink()
        for directory in directories:
            dir_path = root / directory
            if not (source / dir_path.relative_to(dest)).exists():
                print(f"Remove {dir_path}")
                dir_path.rmdir()
    return Ok({})


@contextlib.contextmanager
def _working_directory(path: Path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


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
    # Informational check: does the remote 'gh-pages' branch exist?
    try:
        out = repo.git.ls_remote("--heads", "origin", "gh-pages")
        gh_exists_remote = bool(out.strip())
    except GitCommandError:
        # Treat errors querying remote as non-existent branch;
        # will be created on publish
        gh_exists_remote = False
    if gh_exists_remote:
        print("[INFO] Remote 'gh-pages' branch exists.")
    else:
        print(
            "[INFO] Remote 'gh-pages' branch does not exist;"
            " it will be created on first publish."
        )

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
        except GitCommandError as ex:
            # Ignore the common case of no changes to commit; re-raise others
            msg = str(ex).lower()
            if "nothing to commit" in msg or "nothing added to commit" in msg:
                pass
            else:
                raise
        # Push branch
        repo.git.push("origin", "gh-pages")
    # Clean up the worktree directory
    shutil.rmtree(ghp_dir, ignore_errors=True)
    return 0


def docs_main() -> None:
    """Build Sphinx documentation with sphinx-multiversion and optionally publish.

    Local builds place the generated site under docs/ (multiversion layout).
    Use --publish to push the built site to the gh-pages branch.
    """
    parser = argparse.ArgumentParser(prog="dev-docs", add_help=True)
    parser.add_argument(
        "--source", "-s", default="doc_src", help="Sphinx source directory"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="docs",
        help="Output directory (multiversion root)",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish the built docs to gh-pages branch",
    )
    args = parser.parse_args()

    # Resolve project root
    root_opt: Option = _find_project_root()
    if root_opt.is_none:
        print("[ERROR] No project root found", file=sys.stderr)
        sys.exit(1)
    root: Path = root_opt.unwrap()

    source = (root / args.source).resolve()
    output = (root / args.output).resolve()

    if not source.exists():
        print(f"[ERROR] Sphinx source not found: {source}", file=sys.stderr)
        sys.exit(2)

    print("[RUN] Building Sphinx documentation (sphinx-multiversion)")
    code = _build_sphinx_multiversion(source, output)
    if code != 0:
        sys.exit(code)

    if args.publish:
        print("[RUN] Publishing docs to gh-pages")
        # Verify this is a git repo
        git_dir = root / "gh-pages"
        if not git_dir.exists():
            print(
                "[ERROR] Not a git repository; cannot publish", file=sys.stderr
            )
            sys.exit(3)
        pub_code = _publish_gh_pages(root, output)
        sys.exit(pub_code)

    sys.exit(0)
