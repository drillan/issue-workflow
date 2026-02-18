"""Unit tests for hachimoku version check service."""

from unittest.mock import patch

import pytest

from issue_workflow.services.hachimoku_version import (
    HACHIMOKU_PYPROJECT_URL,
    HACHIMOKU_UPGRADE_COMMAND,
    HTTP_TIMEOUT_SECONDS,
    HachimokuVersionResult,
    check_hachimoku_version,
    format_upgrade_hint,
    get_installed_version,
    get_remote_version,
)


class TestGetInstalledVersion:
    """Tests for get_installed_version function."""

    def test_returns_version_when_installed(self) -> None:
        """Test returns version string when 8moku is installed."""
        with patch("issue_workflow.services.hachimoku_version.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "hachimoku 0.0.2\n"
            result = get_installed_version()
            assert result == "0.0.2"

    def test_returns_none_when_not_installed(self) -> None:
        """Test returns None when 8moku is not installed."""
        with patch("issue_workflow.services.hachimoku_version.shutil.which") as mock_which:
            mock_which.return_value = None
            result = get_installed_version()
            assert result is None

    def test_returns_none_when_command_fails(self) -> None:
        """Test returns None when 8moku --version returns non-zero exit code."""
        with patch("issue_workflow.services.hachimoku_version.shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/8moku"
            with patch(
                "issue_workflow.services.hachimoku_version.subprocess.run"
            ) as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stdout = ""
                result = get_installed_version()
                assert result is None

    def test_returns_none_when_version_parse_fails(self) -> None:
        """Test returns None when version output cannot be parsed."""
        with patch("issue_workflow.services.hachimoku_version.shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/8moku"
            with patch(
                "issue_workflow.services.hachimoku_version.subprocess.run"
            ) as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "unexpected output format"
                result = get_installed_version()
                assert result is None

    def test_returns_none_on_subprocess_error(self) -> None:
        """Test returns None when subprocess raises an exception."""
        with patch("issue_workflow.services.hachimoku_version.shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/8moku"
            with patch(
                "issue_workflow.services.hachimoku_version.subprocess.run"
            ) as mock_run:
                mock_run.side_effect = OSError("Command not found")
                result = get_installed_version()
                assert result is None

    def test_calls_8moku_with_version_flag(self) -> None:
        """Test that 8moku --version is called correctly."""
        with patch("issue_workflow.services.hachimoku_version.shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/8moku"
            with patch(
                "issue_workflow.services.hachimoku_version.subprocess.run"
            ) as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "hachimoku 0.0.3\n"
                get_installed_version()
                mock_run.assert_called_once_with(
                    ["8moku", "--version"],
                    capture_output=True,
                    text=True,
                )


class TestGetRemoteVersion:
    """Tests for get_remote_version function."""

    def test_returns_version_from_pyproject_toml(self) -> None:
        """Test returns version from remote pyproject.toml."""
        pyproject_content = b'[project]\nname = "hachimoku"\nversion = "0.0.3"\n'
        with patch("issue_workflow.services.hachimoku_version.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = pyproject_content
            result = get_remote_version()
            assert result == "0.0.3"

    def test_returns_none_on_network_error(self) -> None:
        """Test returns None when HTTP request fails."""
        with patch("issue_workflow.services.hachimoku_version.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = OSError("Network error")
            result = get_remote_version()
            assert result is None

    def test_returns_none_on_timeout(self) -> None:
        """Test returns None when HTTP request times out."""
        from urllib.error import URLError

        with patch("issue_workflow.services.hachimoku_version.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = URLError("timeout")
            result = get_remote_version()
            assert result is None

    def test_returns_none_on_invalid_toml(self) -> None:
        """Test returns None when pyproject.toml has invalid content."""
        with patch("issue_workflow.services.hachimoku_version.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = b"not valid toml {{"
            result = get_remote_version()
            assert result is None

    def test_returns_none_when_version_key_missing(self) -> None:
        """Test returns None when pyproject.toml lacks version key."""
        pyproject_content = b'[project]\nname = "hachimoku"\n'
        with patch("issue_workflow.services.hachimoku_version.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = pyproject_content
            result = get_remote_version()
            assert result is None

    def test_uses_correct_url(self) -> None:
        """Test that the correct URL is used for fetching."""
        pyproject_content = b'[project]\nname = "hachimoku"\nversion = "0.0.1"\n'
        with patch("issue_workflow.services.hachimoku_version.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = pyproject_content
            get_remote_version()
            call_args = mock_urlopen.call_args
            request = call_args[0][0]
            assert request.full_url == HACHIMOKU_PYPROJECT_URL
            assert call_args[1]["timeout"] == HTTP_TIMEOUT_SECONDS


class TestCheckHachimokuVersion:
    """Tests for check_hachimoku_version function."""

    def test_returns_update_available_when_remote_is_newer(self) -> None:
        """Test returns result with update_available=True when remote > local."""
        with (
            patch(
                "issue_workflow.services.hachimoku_version.get_installed_version",
                return_value="0.0.2",
            ),
            patch(
                "issue_workflow.services.hachimoku_version.get_remote_version",
                return_value="0.0.3",
            ),
        ):
            result = check_hachimoku_version()
            assert result is not None
            assert result.update_available is True
            assert result.installed_version == "0.0.2"
            assert result.remote_version == "0.0.3"

    def test_returns_no_update_when_versions_equal(self) -> None:
        """Test returns result with update_available=False when versions match."""
        with (
            patch(
                "issue_workflow.services.hachimoku_version.get_installed_version",
                return_value="0.0.3",
            ),
            patch(
                "issue_workflow.services.hachimoku_version.get_remote_version",
                return_value="0.0.3",
            ),
        ):
            result = check_hachimoku_version()
            assert result is not None
            assert result.update_available is False

    def test_returns_no_update_when_local_is_newer(self) -> None:
        """Test returns result with update_available=False when local > remote."""
        with (
            patch(
                "issue_workflow.services.hachimoku_version.get_installed_version",
                return_value="0.0.4",
            ),
            patch(
                "issue_workflow.services.hachimoku_version.get_remote_version",
                return_value="0.0.3",
            ),
        ):
            result = check_hachimoku_version()
            assert result is not None
            assert result.update_available is False

    def test_returns_none_when_not_installed(self) -> None:
        """Test returns None when hachimoku is not installed."""
        with patch(
            "issue_workflow.services.hachimoku_version.get_installed_version",
            return_value=None,
        ):
            result = check_hachimoku_version()
            assert result is None

    def test_returns_none_when_remote_fetch_fails(self) -> None:
        """Test returns None when remote version cannot be fetched."""
        with (
            patch(
                "issue_workflow.services.hachimoku_version.get_installed_version",
                return_value="0.0.2",
            ),
            patch(
                "issue_workflow.services.hachimoku_version.get_remote_version",
                return_value=None,
            ),
        ):
            result = check_hachimoku_version()
            assert result is None

    def test_returns_none_when_version_comparison_fails(self) -> None:
        """Test returns None when version strings are invalid for comparison."""
        with (
            patch(
                "issue_workflow.services.hachimoku_version.get_installed_version",
                return_value="not-a-version",
            ),
            patch(
                "issue_workflow.services.hachimoku_version.get_remote_version",
                return_value="0.0.3",
            ),
        ):
            result = check_hachimoku_version()
            assert result is None


class TestFormatUpgradeHint:
    """Tests for format_upgrade_hint function."""

    def test_formats_hint_message(self) -> None:
        """Test hint message format."""
        result = HachimokuVersionResult(
            installed_version="0.0.2",
            remote_version="0.0.3",
            update_available=True,
        )
        hint = format_upgrade_hint(result)
        assert "0.0.2" in hint
        assert "0.0.3" in hint
        assert HACHIMOKU_UPGRADE_COMMAND in hint
        assert "8moku init --force" in hint

    def test_hint_contains_upgrade_command(self) -> None:
        """Test hint contains the uv tool install command."""
        result = HachimokuVersionResult(
            installed_version="0.0.1",
            remote_version="0.0.2",
            update_available=True,
        )
        hint = format_upgrade_hint(result)
        assert "uv tool install --reinstall" in hint


class TestHachimokuVersionResult:
    """Tests for HachimokuVersionResult dataclass."""

    def test_creation(self) -> None:
        """Test creating a version result."""
        result = HachimokuVersionResult(
            installed_version="0.0.2",
            remote_version="0.0.3",
            update_available=True,
        )
        assert result.installed_version == "0.0.2"
        assert result.remote_version == "0.0.3"
        assert result.update_available is True

    def test_is_frozen(self) -> None:
        """Test HachimokuVersionResult is immutable."""
        result = HachimokuVersionResult(
            installed_version="0.0.2",
            remote_version="0.0.3",
            update_available=True,
        )
        with pytest.raises(AttributeError):
            result.installed_version = "0.0.4"  # type: ignore[misc]


class TestConstants:
    """Tests for module constants."""

    def test_pyproject_url(self) -> None:
        """Test HACHIMOKU_PYPROJECT_URL points to correct location."""
        assert "drillan/hachimoku" in HACHIMOKU_PYPROJECT_URL
        assert "pyproject.toml" in HACHIMOKU_PYPROJECT_URL

    def test_timeout_is_reasonable(self) -> None:
        """Test HTTP_TIMEOUT_SECONDS is a reasonable value."""
        assert HTTP_TIMEOUT_SECONDS == 5

    def test_upgrade_command(self) -> None:
        """Test HACHIMOKU_UPGRADE_COMMAND contains expected components."""
        assert "uv tool install" in HACHIMOKU_UPGRADE_COMMAND
        assert "--reinstall" in HACHIMOKU_UPGRADE_COMMAND
        assert "hachimoku" in HACHIMOKU_UPGRADE_COMMAND
