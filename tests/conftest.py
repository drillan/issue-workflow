"""Pytest configuration and shared fixtures."""

from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from _pytest.tmpdir import TempPathFactory


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def temp_git_repo(temp_project_dir: Path) -> Generator[Path]:
    """Create a temporary git repository for testing."""
    import subprocess

    subprocess.run(["git", "init"], cwd=temp_project_dir, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_project_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_project_dir,
        capture_output=True,
        check=True,
    )
    yield temp_project_dir


@pytest.fixture
def sample_workflow_config() -> dict[str, object]:
    """Return a sample workflow configuration."""
    return {
        "version": "1.0",
        "language": "python",
        "quality": {
            "lint": "uv run ruff check --fix .",
            "format": "uv run ruff format .",
            "typecheck": "uv run mypy .",
            "test": "uv run pytest",
            "all": "uv run ruff check --fix . && uv run ruff format . && uv run mypy .",
        },
        "workflow": {
            "tdd_required": True,
            "quality_gate_required": True,
            "auto_report": True,
        },
    }


@pytest.fixture(scope="session")
def shared_temp_dir(tmp_path_factory: "TempPathFactory") -> Path:
    """Create a shared temporary directory for session-scoped fixtures."""
    return tmp_path_factory.mktemp("shared")
