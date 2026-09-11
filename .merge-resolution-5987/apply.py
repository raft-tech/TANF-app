#!/usr/bin/env python3
"""Apply the reviewed develop merge resolution to the unchanged feature branch."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run Git against the requested checkout."""
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=check
    )


def main() -> None:
    """Validate the checkout, merge develop, and stage the prepared resolution."""
    package = Path(__file__).resolve().parent
    manifest = json.loads((package / "manifest.json").read_text())
    repo = package.parent
    if git(repo, "branch", "--show-current").stdout.strip() != manifest["branch"]:
        raise SystemExit("Switch to the original #5987 feature branch first.")
    if git(repo, "rev-parse", "HEAD").stdout.strip() != manifest["head"]:
        raise SystemExit("The feature branch has changed; this resolution needs review.")
    if git(repo, "rev-parse", "--verify", "MERGE_HEAD", check=False).returncode == 0:
        raise SystemExit("A merge is already active; review it before using this helper.")
    status = git(repo, "status", "--porcelain", "--", ".", ":!.merge-resolution-5987")
    if status.stdout.strip():
        raise SystemExit("The checkout has local changes; preserve them before merging.")
    git(repo, "cat-file", "-e", manifest["develop"] + "^{commit}")

    for name, expected_hash in manifest["files"].items():
        data = (package / "files" / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected_hash:
            raise SystemExit(f"Prepared file changed since validation: {name}")

    result = git(
        repo, "merge", "--no-commit", "--no-ff", manifest["develop"], check=False
    )
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    conflicts = set(
        git(repo, "diff", "--name-only", "--diff-filter=U").stdout.splitlines()
    )
    merge_head = git(repo, "rev-parse", "--verify", "MERGE_HEAD", check=False)
    if (
        result.returncode not in {0, 1}
        or merge_head.stdout.strip() != manifest["develop"]
        or conflicts != set(manifest["conflicts"])
    ):
        raise SystemExit("The merge differs from the reviewed preview; no files were copied.")

    for name in manifest["files"]:
        target = repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(package / "files" / name, target)
    git(repo, "add", "--", *manifest["files"])
    if git(repo, "diff", "--name-only", "--diff-filter=U").stdout.strip():
        raise SystemExit("Unexpected unresolved entries remain; review git status.")
    git(repo, "diff", "--cached", "--check", "--", "*.py", "*.go")
    print("All 15 conflicts are resolved and staged. The merge is not committed.")
    print("Run the backend checks listed in this package's README.md, then git commit.")


if __name__ == "__main__":
    main()
