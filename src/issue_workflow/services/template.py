"""Template service for generating config files."""

import filecmp
import json
import shutil
from pathlib import Path

from issue_workflow.models.config import (
    DocumentationSettings,
    WorkflowConfig,
    WorkflowSettings,
)
from issue_workflow.models.preset import LanguagePreset
from issue_workflow.models.update import FileChangeInfo, FileChangeType, UpdateResult

# URL for workflow config JSON schema
WORKFLOW_CONFIG_SCHEMA_URL = (
    "https://raw.githubusercontent.com/drillan/issue-workflow/main/"
    "schemas/workflow-config.schema.json"
)


class SourceDirectoryNotFoundError(Exception):
    """Raised when source directory for commands or skills is not found."""


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


def _get_file_changes(
    source_dir: Path, target_dir: Path, pattern: str
) -> tuple[list[FileChangeInfo], list[tuple[Path, str]]]:
    """Detect file changes between source and target directories.

    Args:
        source_dir: Source directory with new files
        target_dir: Target directory with existing files
        pattern: Glob pattern to match files (e.g., "*.md")

    Returns:
        Tuple of (list of FileChangeInfo describing changes, list of error tuples)
    """
    changes: list[FileChangeInfo] = []
    errors: list[tuple[Path, str]] = []

    # Added and updated files
    for source_file in source_dir.glob(pattern):
        target_file = target_dir / source_file.name
        if not target_file.exists():
            changes.append(
                FileChangeInfo(
                    path=target_file,
                    change_type=FileChangeType.ADDED,
                    source_path=source_file,
                )
            )
        else:
            try:
                if not filecmp.cmp(source_file, target_file, shallow=False):
                    changes.append(
                        FileChangeInfo(
                            path=target_file,
                            change_type=FileChangeType.UPDATED,
                            source_path=source_file,
                        )
                    )
            except OSError as e:
                errors.append((target_file, str(e)))

    # Note: Files in target but not in source are intentionally ignored.
    # These are user files or files from other tools and should not be
    # reported as needing deletion (#15).

    return changes, errors


def _has_recursive_diff(dcmp: filecmp.dircmp[str]) -> bool:
    """Check if there are differences recursively in a dircmp result.

    Args:
        dcmp: A dircmp comparison result

    Returns:
        True if there are differences in this directory or any subdirectory
    """
    if dcmp.diff_files or dcmp.left_only or dcmp.right_only:
        return True

    return any(_has_recursive_diff(subdir_dcmp) for subdir_dcmp in dcmp.subdirs.values())


def _get_dir_changes(source_dir: Path, target_dir: Path) -> list[FileChangeInfo]:
    """Detect directory changes between source and target directories.

    Args:
        source_dir: Source directory with new subdirectories
        target_dir: Target directory with existing subdirectories

    Returns:
        List of FileChangeInfo describing changes
    """
    changes: list[FileChangeInfo] = []

    # Added and updated directories
    for source_subdir in source_dir.iterdir():
        if not source_subdir.is_dir():
            continue
        target_subdir = target_dir / source_subdir.name
        if not target_subdir.exists():
            changes.append(
                FileChangeInfo(
                    path=target_subdir,
                    change_type=FileChangeType.ADDED,
                    source_path=source_subdir,
                )
            )
        else:
            # Check if any file in the directory changed (recursively)
            dcmp = filecmp.dircmp(source_subdir, target_subdir)
            if _has_recursive_diff(dcmp):
                changes.append(
                    FileChangeInfo(
                        path=target_subdir,
                        change_type=FileChangeType.UPDATED,
                        source_path=source_subdir,
                    )
                )

    # Note: Directories in target but not in source are intentionally ignored.
    # These are user directories or directories from other tools and should not be
    # reported as needing deletion (#15).

    return changes


class TemplateService:
    """Service for generating configuration files from presets."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        """Initialize template service."""
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_dir = templates_dir

    def generate_workflow_config(
        self,
        preset: LanguagePreset,
        target_dir: Path,
        documentation: DocumentationSettings | None = None,
    ) -> Path:
        """Generate workflow-config.json from preset.

        Args:
            preset: Language preset to use
            target_dir: Directory to write config to (.claude/)
            documentation: Documentation settings (uses preset defaults if None)

        Returns:
            Path to generated config file
        """
        config = WorkflowConfig(
            version="1.0",
            language=preset.name.value,
            quality=preset.quality,
            workflow=WorkflowSettings(),
            documentation=documentation or preset.documentation,
        )

        target_dir.mkdir(parents=True, exist_ok=True)
        config_path = target_dir / "workflow-config.json"

        config_dict = config.model_dump()
        config_dict["$schema"] = WORKFLOW_CONFIG_SCHEMA_URL

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

        if not source_path.exists():
            msg = f"Template file not found: {source_path}"
            raise FileNotFoundError(msg)

        target_path.write_text(source_path.read_text())

        return target_path

    def copy_commands(self, target_dir: Path) -> Path:
        """Copy command files to target directory.

        Copies the bundled command files to .claude/commands/.
        Preserves existing command files.

        Args:
            target_dir: Directory to write commands to (.claude/)

        Returns:
            Path to the commands directory

        Raises:
            SourceDirectoryNotFoundError: If source commands directory does not exist.
        """
        source_dir = get_commands_source_dir()
        if not source_dir.exists():
            msg = f"Commands source directory not found: {source_dir}"
            raise SourceDirectoryNotFoundError(msg)

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

        Raises:
            SourceDirectoryNotFoundError: If source skills directory does not exist.
        """
        source_dir = get_skills_source_dir()
        if not source_dir.exists():
            msg = f"Skills source directory not found: {source_dir}"
            raise SourceDirectoryNotFoundError(msg)

        skills_target = target_dir / "skills"
        skills_target.mkdir(parents=True, exist_ok=True)

        for skill_dir in source_dir.iterdir():
            if skill_dir.is_dir():
                target_skill = skills_target / skill_dir.name
                if not target_skill.exists():
                    shutil.copytree(skill_dir, target_skill)

        return skills_target

    def update_commands(self, target_dir: Path, dry_run: bool = False) -> UpdateResult:
        """Update command files with force overwrite.

        Args:
            target_dir: Directory containing commands (.claude/)
            dry_run: If True, only calculate changes without applying

        Returns:
            UpdateResult with details of changes

        Raises:
            SourceDirectoryNotFoundError: If source commands directory does not exist.
        """
        source_dir = get_commands_source_dir()
        if not source_dir.exists():
            msg = f"Commands source directory not found: {source_dir}"
            raise SourceDirectoryNotFoundError(msg)

        commands_target = target_dir / "commands"
        commands_target.mkdir(parents=True, exist_ok=True)

        changes, errors = _get_file_changes(source_dir, commands_target, "*.md")

        if not dry_run:
            for change in changes:
                if (
                    change.change_type in (FileChangeType.ADDED, FileChangeType.UPDATED)
                    and change.source_path is not None
                ):
                    try:
                        shutil.copy2(change.source_path, change.path)
                    except OSError as e:
                        errors.append((change.path, str(e)))

        return UpdateResult(
            commands_changes=changes,
            skills_changes=[],
            errors=errors,
            dry_run=dry_run,
        )

    def update_skills(self, target_dir: Path, dry_run: bool = False) -> UpdateResult:
        """Update skill directories with force overwrite.

        Args:
            target_dir: Directory containing skills (.claude/)
            dry_run: If True, only calculate changes without applying

        Returns:
            UpdateResult with details of changes

        Raises:
            SourceDirectoryNotFoundError: If source skills directory does not exist.
        """
        source_dir = get_skills_source_dir()
        if not source_dir.exists():
            msg = f"Skills source directory not found: {source_dir}"
            raise SourceDirectoryNotFoundError(msg)

        skills_target = target_dir / "skills"
        skills_target.mkdir(parents=True, exist_ok=True)

        changes = _get_dir_changes(source_dir, skills_target)
        errors: list[tuple[Path, str]] = []

        if not dry_run:
            for change in changes:
                if change.change_type == FileChangeType.ADDED and change.source_path is not None:
                    try:
                        shutil.copytree(change.source_path, change.path)
                    except OSError as e:
                        errors.append((change.path, str(e)))
                elif (
                    change.change_type == FileChangeType.UPDATED and change.source_path is not None
                ):
                    target_removed = False
                    try:
                        shutil.rmtree(change.path)
                        target_removed = True
                        shutil.copytree(change.source_path, change.path)
                    except OSError as e:
                        if target_removed:
                            error_msg = (
                                f"{e} (WARNING: Original directory was removed "
                                "but new version could not be copied)"
                            )
                        else:
                            error_msg = str(e)
                        errors.append((change.path, error_msg))

        return UpdateResult(
            commands_changes=[],
            skills_changes=changes,
            errors=errors,
            dry_run=dry_run,
        )

    def generate_all(
        self,
        preset: LanguagePreset,
        target_dir: Path,
        documentation: DocumentationSettings | None = None,
    ) -> list[Path]:
        """Generate all config files from preset.

        Args:
            preset: Language preset to use
            target_dir: Directory to write config files to (.claude/)
            documentation: Documentation settings (uses preset defaults if None)

        Returns:
            List of paths to generated files/directories
        """
        generated: list[Path] = []
        generated.append(self.generate_workflow_config(preset, target_dir, documentation))
        generated.append(self.generate_git_conventions(target_dir))
        generated.append(self.copy_commands(target_dir))
        generated.append(self.copy_skills(target_dir))
        return generated
