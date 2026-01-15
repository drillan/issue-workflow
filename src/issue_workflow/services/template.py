"""Template service for generating config files."""

import json
import shutil
from pathlib import Path

from issue_workflow.models.config import WorkflowConfig, WorkflowSettings
from issue_workflow.models.preset import LanguagePreset


def get_commands_source_dir() -> Path:
    """Get the source directory for command files.

    Returns:
        Path to the commands directory bundled with the package.
    """
    return Path(__file__).parent.parent / "commands"


def get_skills_source_dir() -> Path:
    """Get the source directory for skill files.

    Returns:
        Path to the skills directory bundled with the package.
    """
    return Path(__file__).parent.parent / "skills"


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

    def copy_commands(self, target_dir: Path) -> Path:
        """Copy command files to target directory.

        Copies the bundled command files to .claude/commands/.
        Preserves existing command files.

        Args:
            target_dir: Directory to write commands to (.claude/)

        Returns:
            Path to the commands directory
        """
        source_dir = get_commands_source_dir()
        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True, exist_ok=True)

        for source_file in source_dir.glob("*.md"):
            target_file = commands_target / source_file.name
            if not target_file.exists():
                shutil.copy2(source_file, target_file)

        return commands_target

    def copy_skills(self, target_dir: Path) -> Path:
        """Copy skill directories to target directory.

        Copies the bundled skill directories to .claude/skills/.
        Preserves existing skill directories.

        Args:
            target_dir: Directory to write skills to (.claude/)

        Returns:
            Path to the skills directory
        """
        source_dir = get_skills_source_dir()
        skills_target = target_dir / "skills"
        skills_target.mkdir(parents=True, exist_ok=True)

        for skill_dir in source_dir.iterdir():
            if skill_dir.is_dir():
                target_skill = skills_target / skill_dir.name
                if not target_skill.exists():
                    shutil.copytree(skill_dir, target_skill)

        return skills_target

    def generate_all(self, preset: LanguagePreset, target_dir: Path) -> list[Path]:
        """Generate all config files from preset.

        Args:
            preset: Language preset to use
            target_dir: Directory to write config files to (.claude/)

        Returns:
            List of paths to generated files/directories
        """
        generated: list[Path] = []
        generated.append(self.generate_workflow_config(preset, target_dir))
        generated.append(self.generate_git_conventions(target_dir))
        generated.append(self.copy_commands(target_dir))
        generated.append(self.copy_skills(target_dir))
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
