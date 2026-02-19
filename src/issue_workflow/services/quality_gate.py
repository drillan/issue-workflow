"""Quality gate service for loading and executing quality commands."""

import json
import warnings
from pathlib import Path

from issue_workflow.models.config import QualityCommands, WorkflowConfig


def _load_config(project_dir: Path) -> WorkflowConfig | None:
    """Load and parse workflow config from project directory.

    Args:
        project_dir: Project root directory

    Returns:
        WorkflowConfig if config exists and is valid, None otherwise
    """
    config_path = project_dir / ".claude" / "workflow-config.json"

    if not config_path.exists():
        return None

    try:
        with config_path.open() as f:
            data = json.load(f)
        return WorkflowConfig(**data)
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


def load_quality_commands(project_dir: Path) -> QualityCommands | None:
    """Load quality commands from workflow config.

    Args:
        project_dir: Project root directory

    Returns:
        QualityCommands if config exists, None otherwise
    """
    config = _load_config(project_dir)
    if config is None:
        return None
    return config.quality


def is_quality_gate_required(project_dir: Path) -> bool:
    """Check if quality gate is required for the project.

    Args:
        project_dir: Project root directory

    Returns:
        True if quality gate is required
    """
    config = _load_config(project_dir)
    if config is None:
        return False
    return config.workflow.quality_gate_required
