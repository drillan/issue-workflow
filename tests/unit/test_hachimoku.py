"""Unit tests for HachimokuService (T082)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from issue_workflow.services.hachimoku import (
    HachimokuInitError,
    HachimokuInstallError,
    setup_hachimoku,
)


class TestSetupHachimoku:
    """Tests for setup_hachimoku function (T082)."""

    def test_installs_and_initializes_when_both_missing(self, tmp_path: Path) -> None:
        """Test installing and initializing when both are missing."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with (
            patch(
                "issue_workflow.services.hachimoku.shutil.which", return_value=None
            ) as mock_which,
            patch("issue_workflow.services.hachimoku.subprocess.run") as mock_run,
        ):
            mock_install = MagicMock()
            mock_install.returncode = 0
            mock_init = MagicMock()
            mock_init.returncode = 0
            mock_run.side_effect = [mock_install, mock_init]

            installed, initialized = setup_hachimoku(project_dir)

            assert installed is True
            assert initialized is True
            mock_which.assert_called_once_with("8moku")
            assert mock_run.call_count == 2
            assert mock_run.call_args_list[0][0][0] == [
                "uv",
                "tool",
                "install",
                "hachimoku",
            ]
            assert mock_run.call_args_list[1][0][0] == ["8moku", "init"]

    def test_only_initializes_when_already_installed(self, tmp_path: Path) -> None:
        """Test only initializing when hachimoku is already installed."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with (
            patch(
                "issue_workflow.services.hachimoku.shutil.which",
                return_value="/usr/local/bin/8moku",
            ),
            patch("issue_workflow.services.hachimoku.subprocess.run") as mock_run,
        ):
            mock_init = MagicMock()
            mock_init.returncode = 0
            mock_run.return_value = mock_init

            installed, initialized = setup_hachimoku(project_dir)

            assert installed is False
            assert initialized is True
            assert mock_run.call_count == 1
            assert mock_run.call_args_list[0][0][0] == ["8moku", "init"]

    def test_skips_when_both_exist(self, tmp_path: Path) -> None:
        """Test skipping when both hachimoku and .hachimoku/ exist."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".hachimoku").mkdir()

        with (
            patch(
                "issue_workflow.services.hachimoku.shutil.which",
                return_value="/usr/local/bin/8moku",
            ),
            patch("issue_workflow.services.hachimoku.subprocess.run") as mock_run,
        ):
            installed, initialized = setup_hachimoku(project_dir)

            assert installed is False
            assert initialized is False
            mock_run.assert_not_called()

    def test_raises_error_on_install_failure(self, tmp_path: Path) -> None:
        """Test raising HachimokuInstallError on installation failure."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with (
            patch("issue_workflow.services.hachimoku.shutil.which", return_value=None),
            patch("issue_workflow.services.hachimoku.subprocess.run") as mock_run,
        ):
            mock_install = MagicMock()
            mock_install.returncode = 1
            mock_install.stderr = "Permission denied"
            mock_run.return_value = mock_install

            with pytest.raises(HachimokuInstallError, match="Permission denied"):
                setup_hachimoku(project_dir)

    def test_raises_error_on_init_failure(self, tmp_path: Path) -> None:
        """Test raising HachimokuInitError on initialization failure."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with (
            patch(
                "issue_workflow.services.hachimoku.shutil.which",
                return_value="/usr/local/bin/8moku",
            ),
            patch("issue_workflow.services.hachimoku.subprocess.run") as mock_run,
        ):
            mock_init = MagicMock()
            mock_init.returncode = 1
            mock_init.stderr = "Init failed"
            mock_run.return_value = mock_init

            with pytest.raises(HachimokuInitError, match="Init failed"):
                setup_hachimoku(project_dir)

    def test_raises_install_error_when_uv_not_found(self, tmp_path: Path) -> None:
        """Test raising HachimokuInstallError when uv is not installed."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with (
            patch("issue_workflow.services.hachimoku.shutil.which", return_value=None),
            patch(
                "issue_workflow.services.hachimoku.subprocess.run",
                side_effect=FileNotFoundError("uv"),
            ),
            pytest.raises(HachimokuInstallError, match="uv is not installed"),
        ):
            setup_hachimoku(project_dir)

    def test_raises_init_error_when_8moku_not_on_path(self, tmp_path: Path) -> None:
        """Test raising HachimokuInitError when 8moku not found after install."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with (
            patch(
                "issue_workflow.services.hachimoku.shutil.which",
                return_value="/usr/local/bin/8moku",
            ),
            patch(
                "issue_workflow.services.hachimoku.subprocess.run",
                side_effect=FileNotFoundError("8moku"),
            ),
            pytest.raises(HachimokuInitError, match="8moku command not found"),
        ):
            setup_hachimoku(project_dir)
