"""Unit tests for plugin copy functionality."""

import json
from pathlib import Path

import pytest

from issue_workflow.services.template import TemplateService


class TestPluginCopy:
    """Tests for plugin copy functionality in TemplateService."""

    @pytest.fixture
    def template_service(self) -> TemplateService:
        """Create template service instance."""
        return TemplateService()

    @pytest.fixture
    def target_dir(self, tmp_path: Path) -> Path:
        """Create target .claude directory."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        return claude_dir

    def test_copy_plugin_creates_plugin_directory(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_plugin creates .claude/plugin directory."""
        template_service.copy_plugin(target_dir)

        plugin_dir = target_dir / "plugin"
        assert plugin_dir.exists()
        assert plugin_dir.is_dir()

    def test_copy_plugin_creates_claude_plugin_manifest(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_plugin creates .claude-plugin/plugin.json."""
        template_service.copy_plugin(target_dir)

        manifest_path = target_dir / "plugin" / ".claude-plugin" / "plugin.json"
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text())
        assert manifest["name"] == "issue-workflow"
        assert "version" in manifest
        assert "description" in manifest

    def test_copy_plugin_copies_commands(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_plugin copies command files."""
        template_service.copy_plugin(target_dir)

        commands_dir = target_dir / "plugin" / "commands"
        assert commands_dir.exists()

        # Check that command files exist
        expected_commands = [
            "start-issue.md",
            "merge-pr.md",
            "add-worktree.md",
            "review-pr-comments.md",
        ]
        for cmd in expected_commands:
            assert (commands_dir / cmd).exists(), f"Command {cmd} should exist"

    def test_copy_plugin_copies_skills(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that copy_plugin copies skill directories."""
        template_service.copy_plugin(target_dir)

        skills_dir = target_dir / "plugin" / "skills"
        assert skills_dir.exists()

        # Check that skill directories exist with SKILL.md
        expected_skills = ["tdd-workflow", "code-quality-gate", "issue-reporter", "doc-updater"]
        for skill in expected_skills:
            skill_dir = skills_dir / skill
            assert skill_dir.exists(), f"Skill directory {skill} should exist"
            assert (skill_dir / "SKILL.md").exists(), f"SKILL.md in {skill} should exist"

    def test_generate_all_includes_plugin_copy(
        self, template_service: TemplateService, target_dir: Path
    ) -> None:
        """Test that generate_all includes plugin copy."""
        from issue_workflow.services.preset_loader import PresetLoader

        loader = PresetLoader()
        preset = loader.load("python")

        generated = template_service.generate_all(preset, target_dir)

        # Plugin directory should be in the generated list
        plugin_dir = target_dir / "plugin"
        assert plugin_dir in generated or any(str(plugin_dir) in str(p) for p in generated)
        assert plugin_dir.exists()


class TestSettingsJsonLocalPath:
    """Tests for settings.json with local plugin path."""

    @pytest.fixture
    def target_dir(self, tmp_path: Path) -> Path:
        """Create target .claude directory."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        return claude_dir

    def test_update_settings_json_uses_local_path(self, target_dir: Path) -> None:
        """Test that settings.json uses local plugin path."""
        from issue_workflow.services.template import update_settings_json

        # Plugin path should be relative to .claude directory
        update_settings_json(target_dir, "./.claude/plugin")

        settings_path = target_dir / "settings.json"
        assert settings_path.exists()

        settings = json.loads(settings_path.read_text())
        assert "plugins" in settings
        assert "./.claude/plugin" in settings["plugins"]

    def test_update_settings_json_preserves_existing_plugins(self, target_dir: Path) -> None:
        """Test that existing plugins are preserved."""
        from issue_workflow.services.template import update_settings_json

        # Create existing settings with another plugin
        settings_path = target_dir / "settings.json"
        settings_path.write_text('{"plugins": ["other-plugin"]}')

        update_settings_json(target_dir, "./.claude/plugin")

        settings = json.loads(settings_path.read_text())
        assert "other-plugin" in settings["plugins"]
        assert "./.claude/plugin" in settings["plugins"]
