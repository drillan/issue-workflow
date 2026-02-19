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


class TestLoadConfig:
    """Tests for _load_config helper (shared config loading)."""

    def test_load_config_returns_workflow_config(self, tmp_path: Path) -> None:
        """Test _load_config returns WorkflowConfig when valid."""
        from issue_workflow.services.quality_gate import _load_config

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
            "workflow": {"quality_gate_required": True},
        }

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "workflow-config.json").write_text(json.dumps(config_data))

        config = _load_config(tmp_path)
        assert config is not None
        assert config.workflow.quality_gate_required is True

    def test_load_config_missing_file_returns_none(self, tmp_path: Path) -> None:
        """Test _load_config returns None when config file is missing."""
        from issue_workflow.services.quality_gate import _load_config

        assert _load_config(tmp_path) is None

    def test_load_config_invalid_json_returns_none(self, tmp_path: Path) -> None:
        """Test _load_config returns None and warns on invalid JSON."""
        from issue_workflow.services.quality_gate import _load_config

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "workflow-config.json").write_text("{invalid json")

        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            assert _load_config(tmp_path) is None
            assert len(w) == 1
            assert "Invalid JSON" in str(w[0].message)

    def test_load_config_invalid_schema_returns_none(self, tmp_path: Path) -> None:
        """Test _load_config returns None and warns on invalid schema."""
        from issue_workflow.services.quality_gate import _load_config

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "workflow-config.json").write_text(json.dumps({"bad": "schema"}))

        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            assert _load_config(tmp_path) is None
            assert len(w) == 1
            assert "Invalid config" in str(w[0].message)
