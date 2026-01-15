"""TDD file mapping service."""

from pathlib import Path


def get_test_file_path(source_path: str) -> str:
    """Get test file path for a source file.

    Args:
        source_path: Path to source file (e.g., 'src/auth.py')

    Returns:
        Path to corresponding test file (e.g., 'tests/test_auth.py')
    """
    path = Path(source_path)
    filename = path.name

    # Remove src/ prefix if present
    if "src" in path.parts:
        filename = path.name

    # Add test_ prefix
    test_filename = f"test_{filename}"
    return f"tests/{test_filename}"


def get_source_file_path(test_path: str) -> str:
    """Get source file path for a test file.

    Args:
        test_path: Path to test file (e.g., 'tests/test_auth.py')

    Returns:
        Path to corresponding source file (e.g., 'src/auth.py')
    """
    path = Path(test_path)
    filename = path.name

    # Remove test_ prefix
    if filename.startswith("test_"):
        filename = filename[5:]

    return f"src/{filename}"


def is_test_file(file_path: str) -> bool:
    """Check if a file is a test file.

    Args:
        file_path: Path to check

    Returns:
        True if file is a test file
    """
    path = Path(file_path)
    return path.name.startswith("test_") or "tests" in path.parts


def is_source_file(file_path: str) -> bool:
    """Check if a file is a source file (not a test).

    Args:
        file_path: Path to check

    Returns:
        True if file is a source file
    """
    return not is_test_file(file_path)


def validate_tdd_order(files_modified: list[str]) -> tuple[bool, str]:
    """Validate that tests were written before implementation.

    Args:
        files_modified: List of modified files in order

    Returns:
        Tuple of (is_valid, message)
    """
    test_files_seen: set[str] = set()
    source_files_seen: set[str] = set()

    for file_path in files_modified:
        if is_test_file(file_path):
            test_files_seen.add(file_path)
        elif is_source_file(file_path):
            # Check if corresponding test was seen first
            expected_test = get_test_file_path(file_path)
            if expected_test not in test_files_seen:
                source_files_seen.add(file_path)

    if source_files_seen:
        missing_tests = [get_test_file_path(f) for f in source_files_seen]
        return False, f"Tests not written before implementation: {missing_tests}"

    return True, "TDD order validated"
