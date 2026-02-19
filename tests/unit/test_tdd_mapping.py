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
        """Test nested Python source file preserves directory structure."""
        from issue_workflow.services.tdd import get_test_file_path

        source = "src/issue_workflow/services/branch.py"
        expected = "tests/services/test_branch.py"
        assert get_test_file_path(source) == expected

    def test_package_only_source_to_test_mapping(self) -> None:
        """Test source with package dir only (no subdirectory)."""
        from issue_workflow.services.tdd import get_test_file_path

        source = "src/issue_workflow/auth.py"
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


class TestValidateTddOrder:
    """Tests for validate_tdd_order function."""

    def test_valid_tdd_order(self) -> None:
        """Test valid TDD order: test before implementation."""
        from issue_workflow.services.tdd import validate_tdd_order

        files = [
            "tests/test_auth.py",  # Test first
            "src/auth.py",  # Implementation second
        ]
        is_valid, message = validate_tdd_order(files)
        assert is_valid is True
        assert message == "TDD order validated"

    def test_invalid_tdd_order(self) -> None:
        """Test invalid TDD order: implementation before test."""
        from issue_workflow.services.tdd import validate_tdd_order

        files = [
            "src/auth.py",  # Implementation first (violation)
            "tests/test_auth.py",  # Test second
        ]
        is_valid, message = validate_tdd_order(files)
        assert is_valid is False
        assert "tests/test_auth.py" in message

    def test_multiple_files_valid(self) -> None:
        """Test valid TDD order with multiple file pairs."""
        from issue_workflow.services.tdd import validate_tdd_order

        files = [
            "tests/test_auth.py",
            "tests/test_user.py",
            "src/auth.py",
            "src/user.py",
        ]
        is_valid, _message = validate_tdd_order(files)
        assert is_valid is True

    def test_multiple_files_one_violation(self) -> None:
        """Test TDD order violation with one file out of order."""
        from issue_workflow.services.tdd import validate_tdd_order

        files = [
            "tests/test_auth.py",
            "src/auth.py",
            "src/user.py",  # No test before this
        ]
        is_valid, message = validate_tdd_order(files)
        assert is_valid is False
        assert "tests/test_user.py" in message

    def test_empty_list(self) -> None:
        """Test empty file list is valid."""
        from issue_workflow.services.tdd import validate_tdd_order

        is_valid, message = validate_tdd_order([])
        assert is_valid is True
        assert message == "TDD order validated"

    def test_test_files_only(self) -> None:
        """Test only test files is valid."""
        from issue_workflow.services.tdd import validate_tdd_order

        files = ["tests/test_auth.py", "tests/test_user.py"]
        is_valid, message = validate_tdd_order(files)
        assert is_valid is True
        assert message == "TDD order validated"

    def test_source_file_without_test(self) -> None:
        """Test source file without any corresponding test."""
        from issue_workflow.services.tdd import validate_tdd_order

        files = ["src/auth.py"]
        is_valid, message = validate_tdd_order(files)
        assert is_valid is False
        assert "tests/test_auth.py" in message

    def test_non_python_files_treated_as_source(self) -> None:
        """Test non-Python files are treated as source files in current implementation."""
        from issue_workflow.services.tdd import validate_tdd_order

        # Current implementation treats all non-test files as source files
        # This may be improved in future to filter by file extension
        files = [
            "README.md",  # Treated as source, no test expected
        ]
        is_valid, _message = validate_tdd_order(files)
        # Non-Python files are treated as source files needing tests
        assert is_valid is False
