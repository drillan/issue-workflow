"""Service for checking hachimoku version updates."""

import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from packaging.version import InvalidVersion, Version

HACHIMOKU_PYPROJECT_URL: str = (
    "https://raw.githubusercontent.com/drillan/hachimoku/refs/heads/main/pyproject.toml"
)

HACHIMOKU_UPGRADE_COMMAND: str = (
    "uv tool install --reinstall git+https://github.com/drillan/hachimoku.git"
)

HACHIMOKU_AGENT_UPDATE_COMMAND: str = "8moku init --force"

COMMAND_TIMEOUT_SECONDS: int = 5


@dataclass(frozen=True)
class HachimokuVersionResult:
    """Result of hachimoku version check."""

    installed_version: str
    remote_version: str
    update_available: bool


def get_installed_version() -> str | None:
    """Get the locally installed hachimoku version.

    Returns:
        Version string (e.g. "0.0.2") or None if not installed or check fails.
    """
    if shutil.which("8moku") is None:
        return None

    try:
        completed = subprocess.run(
            ["8moku", "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if completed.returncode != 0:
        return None

    return completed.stdout.strip() or None


def get_remote_version() -> str | None:
    """Get the latest hachimoku version from GitHub.

    Fetches pyproject.toml from the main branch and parses the version.

    Returns:
        Version string (e.g. "0.0.3") or None if fetch or parse fails.
    """
    request = Request(HACHIMOKU_PYPROJECT_URL)
    try:
        with urlopen(request, timeout=COMMAND_TIMEOUT_SECONDS) as response:
            content = response.read()
    except (OSError, URLError):
        return None

    try:
        data = tomllib.loads(content.decode())
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        return None

    try:
        version = data["project"]["version"]
    except (KeyError, TypeError):
        return None

    if not isinstance(version, str):
        return None

    return version


def check_hachimoku_version() -> HachimokuVersionResult | None:
    """Check if a newer version of hachimoku is available.

    Returns:
        HachimokuVersionResult with version info, or None if check cannot be performed
        (not installed, network error, parse error).
    """
    installed = get_installed_version()
    if installed is None:
        return None

    remote = get_remote_version()
    if remote is None:
        return None

    try:
        installed_ver = Version(installed)
        remote_ver = Version(remote)
    except InvalidVersion:
        return None

    return HachimokuVersionResult(
        installed_version=installed,
        remote_version=remote,
        update_available=remote_ver > installed_ver,
    )


def format_upgrade_hint(result: HachimokuVersionResult) -> str:
    """Format the upgrade hint message for display.

    Args:
        result: Version check result with update info.

    Returns:
        Formatted hint message string.
    """
    return (
        f"hachimoku の新しいバージョンが利用可能です "
        f"(現在: {result.installed_version}, 最新: {result.remote_version})\n"
        f"  アップグレード:   {HACHIMOKU_UPGRADE_COMMAND}\n"
        f"  エージェント更新: {HACHIMOKU_AGENT_UPDATE_COMMAND}"
    )
