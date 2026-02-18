"""Gitignore management service."""

from pathlib import Path

GITIGNORE_ENTRY = "/.issue-workflow/"
GITIGNORE_SECTION_COMMENT = "# issue-workflow"


def ensure_gitignore_entry(project_dir: Path) -> bool:
    """Ensure /.issue-workflow/ is in .gitignore.

    Creates .gitignore if it doesn't exist. Appends the entry with a section
    comment if not already present. Skips if the exact entry already exists.

    Args:
        project_dir: Project root directory

    Returns:
        True if entry was added, False if already present.
    """
    gitignore_path = project_dir / ".gitignore"

    if gitignore_path.exists():
        content = gitignore_path.read_text()
        lines = content.splitlines()

        if GITIGNORE_ENTRY in lines:
            return False

        # Ensure content ends with newline before appending
        if content and not content.endswith("\n"):
            content += "\n"

        content += f"\n{GITIGNORE_SECTION_COMMENT}\n{GITIGNORE_ENTRY}\n"
    else:
        content = f"{GITIGNORE_SECTION_COMMENT}\n{GITIGNORE_ENTRY}\n"

    gitignore_path.write_text(content)
    return True
