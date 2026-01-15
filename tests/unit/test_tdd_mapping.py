"""Unit tests for TDD file mapping validation."""


class TestTddFileMapping:
    """Tests for TDD file mapping (source to test file)."""

    def test_python_source_to_test_mapping(self) -> None:
        """Test Python source file maps to correct test file."""
        from issue_workflow.services.tdd import get_test_file_path

        source = "src/auth.py"
        expected = "tests/test_auth.py"
        assert get_test_file_path(source) == expected

    def test_nested_python_source_to_test_mapping(self) -> None:
        """Test nested Python source file maps correctly."""
        from issue_workflow.services.tdd import get_test_file_path

        source = "src/services/auth.py"
        expected = "tests/test_auth.py"
        assert get_test_file_path(source) == expected

    def test_test_file_to_source_mapping(self) -> None:
        """Test test file maps to correct source file."""
        from issue_workflow.services.tdd import get_source_file_path

        test = "tests/test_auth.py"
        expected = "src/auth.py"
        assert get_source_file_path(test) == expected

    def test_is_test_file(self) -> None:
        """Test identifying test files."""
        from issue_workflow.services.tdd import is_test_file

        assert is_test_file("tests/test_auth.py") is True
        assert is_test_file("test_auth.py") is True
        assert is_test_file("src/auth.py") is False

    def test_is_source_file(self) -> None:
        """Test identifying source files."""
        from issue_workflow.services.tdd import is_source_file

        assert is_source_file("src/auth.py") is True
        assert is_source_file("tests/test_auth.py") is False
