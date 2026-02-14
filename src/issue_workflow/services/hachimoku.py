"""Hachimoku tool setup service."""

import shutil
import subprocess
from pathlib import Path


class HachimokuInstallError(Exception):
    """Raised when hachimoku installation fails."""


class HachimokuInitError(Exception):
    """Raised when hachimoku initialization fails."""


def setup_hachimoku(project_dir: Path) -> tuple[bool, bool]:
    """Setup hachimoku tool: install if needed, initialize if needed.

    Args:
        project_dir: Project root directory

    Returns:
        Tuple of (installed, initialized) indicating what actions were taken.
        installed=True if hachimoku was newly installed.
        initialized=True if .hachimoku/ was newly created.

    Raises:
        HachimokuInstallError: If installation fails.
        HachimokuInitError: If initialization fails.
    """
    installed = False
    initialized = False

    # Check if hachimoku CLI is installed
    if shutil.which("8moku") is None:
        try:
            result = subprocess.run(
                ["uv", "tool", "install", "hachimoku"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            msg = "uv is not installed. Install it from https://docs.astral.sh/uv/ and try again."
            raise HachimokuInstallError(msg) from None
        if result.returncode != 0:
            msg = f"Failed to install hachimoku: {result.stderr}"
            raise HachimokuInstallError(msg)
        installed = True

    # Check if hachimoku is initialized in this project
    hachimoku_dir = project_dir / ".hachimoku"
    if not hachimoku_dir.exists():
        try:
            result = subprocess.run(
                ["8moku", "init"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            msg = (
                "8moku command not found on PATH. Restart your shell or run '8moku init' manually."
            )
            raise HachimokuInitError(msg) from None
        if result.returncode != 0:
            msg = f"Failed to initialize hachimoku: {result.stderr}"
            raise HachimokuInitError(msg)
        initialized = True

    return installed, initialized
