"""Unit tests for .specify/scripts/bash/create-new-feature.sh.

Validates that error suppression patterns (2>/dev/null || echo "")
have been replaced with explicit error propagation (Issue #76).
"""

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

SCRIPT_RELATIVE_PATH = ".specify/scripts/bash/create-new-feature.sh"


def _repo_root() -> Path:
    """Resolve the repository root (two levels above tests/unit/)."""
    return Path(__file__).resolve().parents[2]


def _script_path() -> Path:
    """Return absolute path to the script under test."""
    path = _repo_root() / SCRIPT_RELATIVE_PATH
    if not path.exists():
        pytest.skip(f"Script not found: {path}")
    return path


def _run_script(
    cwd: Path,
    *extra_args: str,
    timeout: int = 30,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run create-new-feature.sh with standard arguments."""
    return subprocess.run(
        ["bash", str(_script_path()), "--json", *extra_args, "test feature"],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _create_git_wrapper_that_fails_on_branch(
    temp_dir: Path,
) -> dict[str, str]:
    """Create a git wrapper that fails on 'git branch' but delegates all else.

    Returns an env dict with the modified PATH.
    """
    real_git = shutil.which("git")
    assert real_git is not None, "git not found on PATH"

    bin_dir = temp_dir / "fake-bin"
    bin_dir.mkdir(exist_ok=True)
    git_wrapper = bin_dir / "git"
    git_wrapper.write_text(
        f"#!/bin/bash\n"
        f'if [[ "$1" == "branch" ]]; then\n'
        f'    echo "fatal: unable to read tree" >&2\n'
        f"    exit 128\n"
        f"fi\n"
        f'exec {real_git} "$@"\n'
    )
    git_wrapper.chmod(stat.S_IRWXU)

    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + ":" + env["PATH"]
    return env


class TestGetHighestFromBranchesErrorHandling:
    """git branch -a failure must propagate as a script error."""

    def test_git_branch_failure_exits_with_error(self, temp_git_repo: Path) -> None:
        """When git branch -a fails, the script must exit non-zero."""
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "initial"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        env = _create_git_wrapper_that_fails_on_branch(temp_git_repo)

        result = _run_script(temp_git_repo, "--short-name", "test-feat", env=env)

        assert result.returncode != 0, (
            "Script should exit non-zero when git branch -a fails, "
            f"but got returncode={result.returncode}. "
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )

    def test_git_branch_failure_shows_error_message(self, temp_git_repo: Path) -> None:
        """When git branch -a fails, stderr must contain diagnostic info."""
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "initial"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        env = _create_git_wrapper_that_fails_on_branch(temp_git_repo)

        result = _run_script(temp_git_repo, "--short-name", "test-feat", env=env)

        # stderr should contain the git error, not just be empty
        assert "fatal" in result.stderr.lower() or "error" in result.stderr.lower(), (
            "stderr should contain git error details when git branch -a fails. "
            f"Got stderr={result.stderr!r}"
        )


class TestNormalOperation:
    """Script should work correctly when git is healthy."""

    def test_success_with_valid_repo(self, temp_git_repo: Path) -> None:
        """Script succeeds and produces JSON output in a valid repo."""
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "initial"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Create .specify directory structure expected by the script
        specify_dir = temp_git_repo / ".specify"
        specify_dir.mkdir()
        (specify_dir / "templates").mkdir()

        result = _run_script(temp_git_repo, "--short-name", "test-feat")

        assert result.returncode == 0, (
            f"Script should succeed, but got returncode={result.returncode}. "
            f"stderr={result.stderr!r}"
        )
        output = json.loads(result.stdout.strip())
        assert "BRANCH_NAME" in output
        assert "FEATURE_NUM" in output

    def test_existing_numbered_branches_detected(self, temp_git_repo: Path) -> None:
        """Existing 00N-* branches increment the number correctly."""
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "initial"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        # Create an existing numbered branch
        subprocess.run(
            ["git", "branch", "003-existing-feature"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        specify_dir = temp_git_repo / ".specify"
        specify_dir.mkdir(exist_ok=True)
        (specify_dir / "templates").mkdir(exist_ok=True)

        result = _run_script(temp_git_repo, "--short-name", "new-feat")

        assert result.returncode == 0, (
            f"Script should succeed, but got returncode={result.returncode}. "
            f"stderr={result.stderr!r}"
        )
        output = json.loads(result.stdout.strip())
        assert output["FEATURE_NUM"] == "004", (
            f"Expected FEATURE_NUM='004' (next after 003), got '{output['FEATURE_NUM']}'"
        )
