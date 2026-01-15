"""Template service for generating config files."""

import json
from pathlib import Path

from issue_workflow.models.config import WorkflowConfig, WorkflowSettings
from issue_workflow.models.preset import LanguagePreset


class TemplateService:
    """Service for generating configuration files from presets."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        """Initialize template service."""
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_dir = templates_dir

    def generate_workflow_config(self, preset: LanguagePreset, target_dir: Path) -> Path:
        """Generate workflow-config.json from preset.

        Args:
            preset: Language preset to use
            target_dir: Directory to write config to (.claude/)

        Returns:
            Path to generated config file
        """
        config = WorkflowConfig(
            version="1.0",
            language=preset.name.value,
            quality=preset.quality,
            workflow=WorkflowSettings(),
        )

        target_dir.mkdir(parents=True, exist_ok=True)
        config_path = target_dir / "workflow-config.json"

        config_dict = config.model_dump()
        config_dict["$schema"] = (
            "https://raw.githubusercontent.com/drillan/issue-workflow/main/"
            "schemas/workflow-config.schema.json"
        )

        with config_path.open("w") as f:
            json.dump(config_dict, f, indent=2)
            f.write("\n")

        return config_path

    def generate_git_conventions(self, target_dir: Path) -> Path:
        """Copy git-conventions.md template to target directory.

        Args:
            target_dir: Directory to write file to (.claude/)

        Returns:
            Path to generated file
        """
        source_path = self.templates_dir / "git-conventions.md"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / "git-conventions.md"

        if source_path.exists():
            target_path.write_text(source_path.read_text())
        else:
            # Generate minimal content if template not found
            target_path.write_text(self._get_default_git_conventions())

        return target_path

    def generate_all(self, preset: LanguagePreset, target_dir: Path) -> list[Path]:
        """Generate all config files from preset.

        Args:
            preset: Language preset to use
            target_dir: Directory to write config files to (.claude/)

        Returns:
            List of paths to generated files
        """
        generated: list[Path] = []
        generated.append(self.generate_workflow_config(preset, target_dir))
        generated.append(self.generate_git_conventions(target_dir))
        return generated

    def _get_default_git_conventions(self) -> str:
        """Get default git conventions content."""
        return """# Git Conventions

## Branch Naming

Format: `<type>/<issue-number>-<description>`

Types: feat/, fix/, refactor/, docs/, test/, chore/

## Commit Message

Format: `<type>(<scope>): <description>`

Follow Conventional Commits specification.
"""


def update_settings_json(target_dir: Path, plugin_url: str) -> Path:
    """Update or create .claude/settings.json with plugin configuration.

    Args:
        target_dir: Directory to write settings to (.claude/)
        plugin_url: Plugin URL to add

    Returns:
        Path to settings file
    """
    settings_path = target_dir / "settings.json"
    target_dir.mkdir(parents=True, exist_ok=True)

    if settings_path.exists():
        with settings_path.open() as f:
            settings = json.load(f)
    else:
        settings = {}

    # Initialize plugins array if not exists
    if "plugins" not in settings:
        settings["plugins"] = []

    # Add plugin if not already present
    if plugin_url not in settings["plugins"]:
        settings["plugins"].append(plugin_url)

    with settings_path.open("w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    return settings_path


def check_user_scope_plugin(plugin_url: str) -> bool:
    """Check if plugin is already installed in user scope.

    Args:
        plugin_url: Plugin URL to check

    Returns:
        True if plugin is installed in user scope
    """
    user_settings_path = Path.home() / ".config" / "claude-code" / "settings.json"

    if not user_settings_path.exists():
        return False

    try:
        with user_settings_path.open() as f:
            settings = json.load(f)
        plugins = settings.get("plugins", [])
        return plugin_url in plugins
    except (json.JSONDecodeError, OSError):
        return False
