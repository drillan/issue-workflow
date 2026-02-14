"""Tests for version consistency between __init__.py and pyproject.toml."""

import tomllib
from pathlib import Path

from typer.testing import CliRunner

from issue_workflow import __version__
from issue_workflow.cli.main import app

runner = CliRunner()

PROJECT_ROOT = Path(__file__).parent.parent.parent


def _read_pyproject_version() -> str:
    """Read version from pyproject.toml."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)
    version: str = data["project"]["version"]
    return version


class TestVersion:
    """Version consistency tests."""

    def test_version_is_string(self) -> None:
        """__version__ should be a string."""
        assert isinstance(__version__, str)

    def test_version_matches_pyproject(self) -> None:
        """__version__ should match pyproject.toml version."""
        pyproject_version = _read_pyproject_version()
        assert __version__ == pyproject_version

    def test_version_callback_output(self) -> None:
        """CLI --version should output correct version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert f"issue-workflow {__version__}" in result.output
