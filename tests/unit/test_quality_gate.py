"""Unit tests for quality gate functionality."""

import json
from pathlib import Path


class TestQualityCommandLoading:
    """Tests for loading quality commands from config."""

    def test_load_quality_commands_from_config(self, tmp_path: Path) -> None:
        """Test loading quality commands from workflow config file."""
        from issue_workflow.services.quality_gate import load_quality_commands

        # Create test config
        config_data = {
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

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        config_file = claude_dir / "workflow-config.json"
        config_file.write_text(json.dumps(config_data))

        commands = load_quality_commands(tmp_path)
        assert commands is not None
        assert commands.lint == "uv run ruff check --fix ."
        assert commands.format == "uv run ruff format ."
        assert commands.typecheck == "uv run mypy ."

    def test_load_quality_commands_missing_config(self, tmp_path: Path) -> None:
        """Test loading quality commands when config is missing."""
        from issue_workflow.services.quality_gate import load_quality_commands

        commands = load_quality_commands(tmp_path)
        assert commands is None

    def test_quality_gate_required_check(self, tmp_path: Path) -> None:
        """Test checking if quality gate is required."""
        from issue_workflow.services.quality_gate import is_quality_gate_required

        config_data = {
            "version": "1.0",
            "language": "python",
            "quality": {
                "lint": "lint",
                "format": "format",
                "typecheck": "typecheck",
                "test": "test",
                "all": "all",
            },
            "workflow": {
                "quality_gate_required": True,
            },
        }

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        config_file = claude_dir / "workflow-config.json"
        config_file.write_text(json.dumps(config_data))

        assert is_quality_gate_required(tmp_path) is True

    def test_quality_gate_not_required(self, tmp_path: Path) -> None:
        """Test when quality gate is not required."""
        from issue_workflow.services.quality_gate import is_quality_gate_required

        config_data = {
            "version": "1.0",
            "language": "python",
            "quality": {
                "lint": "lint",
                "format": "format",
                "typecheck": "typecheck",
                "test": "test",
                "all": "all",
            },
            "workflow": {
                "quality_gate_required": False,
            },
        }

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        config_file = claude_dir / "workflow-config.json"
        config_file.write_text(json.dumps(config_data))

        assert is_quality_gate_required(tmp_path) is False
