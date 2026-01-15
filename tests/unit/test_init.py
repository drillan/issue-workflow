"""Unit tests for init command functions."""

from unittest.mock import patch

from issue_workflow.cli.commands.init import _get_documentation_settings
from issue_workflow.models.config import (
    DDDSettings,
    DocumentationSettings,
    QualityCommands,
)
from issue_workflow.models.preset import LanguagePreset


class TestGetDocumentationSettings:
    """Tests for _get_documentation_settings function."""

    def _create_preset(
        self,
        paths: list[str] | None = None,
        changelog: str | None = "CHANGELOG.md",
        ddd_enabled: bool = True,
        retcon_writing: bool = True,
    ) -> LanguagePreset:
        """Create a test preset with given documentation settings."""
        return LanguagePreset(
            name="generic",
            display_name="Test",
            quality=QualityCommands(
                lint="lint",
                format="format",
                typecheck="typecheck",
                test="test",
                all="all",
            ),
            files=[],
            documentation=DocumentationSettings(
                paths=paths or ["README.md"],
                changelog=changelog,
                ddd=DDDSettings(enabled=ddd_enabled, retcon_writing=retcon_writing),
            ),
        )

    def test_non_interactive_returns_preset_defaults(self) -> None:
        """Test non-interactive mode returns preset defaults directly."""
        preset = self._create_preset(
            paths=["docs/"],
            changelog="HISTORY.md",
            ddd_enabled=False,
            retcon_writing=False,
        )

        result = _get_documentation_settings(preset, non_interactive=True)

        assert result.paths == ["docs/"]
        assert result.changelog == "HISTORY.md"
        assert result.ddd.enabled is False
        assert result.ddd.retcon_writing is False

    def test_interactive_uses_user_paths(self) -> None:
        """Test interactive mode uses user-provided paths."""
        preset = self._create_preset(paths=["README.md"])

        with (
            patch(
                "issue_workflow.cli.commands.init.ui.input_list",
                return_value=["docs/", "specs/"],
            ),
            patch(
                "issue_workflow.cli.commands.init.ui.input_text",
                return_value="CHANGELOG.md",
            ),
            patch("issue_workflow.cli.commands.init.ui.confirm", return_value=True),
        ):
            result = _get_documentation_settings(preset, non_interactive=False)

        assert result.paths == ["docs/", "specs/"]

    def test_interactive_uses_user_changelog(self) -> None:
        """Test interactive mode uses user-provided changelog."""
        preset = self._create_preset()

        with (
            patch(
                "issue_workflow.cli.commands.init.ui.input_list",
                return_value=["README.md"],
            ),
            patch(
                "issue_workflow.cli.commands.init.ui.input_text",
                return_value="RELEASES.md",
            ),
            patch("issue_workflow.cli.commands.init.ui.confirm", return_value=True),
        ):
            result = _get_documentation_settings(preset, non_interactive=False)

        assert result.changelog == "RELEASES.md"

    def test_interactive_empty_changelog_returns_none(self) -> None:
        """Test empty changelog input returns None."""
        preset = self._create_preset()

        with (
            patch(
                "issue_workflow.cli.commands.init.ui.input_list",
                return_value=["README.md"],
            ),
            patch("issue_workflow.cli.commands.init.ui.input_text", return_value=""),
            patch("issue_workflow.cli.commands.init.ui.confirm", return_value=True),
        ):
            result = _get_documentation_settings(preset, non_interactive=False)

        assert result.changelog is None

    def test_interactive_ddd_enabled_from_confirm(self) -> None:
        """Test DDD enabled state comes from user confirmation."""
        preset = self._create_preset(ddd_enabled=False)

        with (
            patch(
                "issue_workflow.cli.commands.init.ui.input_list",
                return_value=["README.md"],
            ),
            patch(
                "issue_workflow.cli.commands.init.ui.input_text",
                return_value="CHANGELOG.md",
            ),
            patch("issue_workflow.cli.commands.init.ui.confirm", return_value=True),
        ):
            result = _get_documentation_settings(preset, non_interactive=False)

        assert result.ddd.enabled is True

    def test_interactive_retcon_writing_inherited_from_preset(self) -> None:
        """Test retcon_writing is inherited from preset, not prompted."""
        preset = self._create_preset(retcon_writing=False)

        with (
            patch(
                "issue_workflow.cli.commands.init.ui.input_list",
                return_value=["README.md"],
            ),
            patch(
                "issue_workflow.cli.commands.init.ui.input_text",
                return_value="CHANGELOG.md",
            ),
            patch("issue_workflow.cli.commands.init.ui.confirm", return_value=True),
        ):
            result = _get_documentation_settings(preset, non_interactive=False)

        assert result.ddd.retcon_writing is False

    def test_preset_changelog_none_uses_fallback_default(self) -> None:
        """Test when preset changelog is None, fallback to CHANGELOG.md is used."""
        preset = self._create_preset(changelog=None)

        with (
            patch(
                "issue_workflow.cli.commands.init.ui.input_list",
                return_value=["README.md"],
            ),
            patch(
                "issue_workflow.cli.commands.init.ui.input_text",
                return_value="CHANGELOG.md",
            ) as mock_input_text,
            patch("issue_workflow.cli.commands.init.ui.confirm", return_value=True),
        ):
            _get_documentation_settings(preset, non_interactive=False)

        # Verify the fallback default was passed to input_text
        mock_input_text.assert_called_once_with("CHANGELOG file", "CHANGELOG.md")

    def test_returns_documentation_settings_type(self) -> None:
        """Test function returns DocumentationSettings instance."""
        preset = self._create_preset()

        result = _get_documentation_settings(preset, non_interactive=True)

        assert isinstance(result, DocumentationSettings)
        assert isinstance(result.ddd, DDDSettings)
