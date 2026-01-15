"""Quality gate service for loading and executing quality commands."""

import json
import warnings
from pathlib import Path

from issue_workflow.models.config import QualityCommands, WorkflowConfig


def load_quality_commands(project_dir: Path) -> QualityCommands | None:
    """Load quality commands from workflow config.

    Args:
        project_dir: Project root directory

    Returns:
        QualityCommands if config exists, None otherwise
    """
    config_path = project_dir / ".claude" / "workflow-config.json"

    if not config_path.exists():
        return None

    try:
        with config_path.open() as f:
            data = json.load(f)
        config = WorkflowConfig(**data)
        return config.quality
    except json.JSONDecodeError as e:
        warnings.warn(
            f"Invalid JSON in {config_path}: {e}",
            UserWarning,
            stacklevel=2,
        )
        return None
    except ValueError as e:
        warnings.warn(
            f"Invalid config in {config_path}: {e}",
            UserWarning,
            stacklevel=2,
        )
        return None


def is_quality_gate_required(project_dir: Path) -> bool:
    """Check if quality gate is required for the project.

    Args:
        project_dir: Project root directory

    Returns:
        True if quality gate is required
    """
    config_path = project_dir / ".claude" / "workflow-config.json"

    if not config_path.exists():
        return False

    try:
        with config_path.open() as f:
            data = json.load(f)
        config = WorkflowConfig(**data)
        return config.workflow.quality_gate_required
    except json.JSONDecodeError as e:
        warnings.warn(
            f"Invalid JSON in {config_path}: {e}",
            UserWarning,
            stacklevel=2,
        )
        return False
    except ValueError as e:
        warnings.warn(
            f"Invalid config in {config_path}: {e}",
            UserWarning,
            stacklevel=2,
        )
        return False


def get_all_command(project_dir: Path) -> str | None:
    """Get the 'all' quality command for the project.

    Args:
        project_dir: Project root directory

    Returns:
        The 'all' command string if available, None otherwise
    """
    commands = load_quality_commands(project_dir)
    if commands is None:
        return None
    return commands.all
