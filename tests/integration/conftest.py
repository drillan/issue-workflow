"""Shared fixtures for integration tests."""

import os
import subprocess
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_project(tmp_path: Path) -> Generator[Path]:
    """Create a temporary project directory with git init."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    subprocess.run(["git", "init"], cwd=project_dir, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=project_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=project_dir,
        capture_output=True,
        check=True,
    )

    original_dir = Path.cwd()
    os.chdir(project_dir)
    yield project_dir
    os.chdir(original_dir)
