"""Unit tests for UI module functions."""

from unittest.mock import patch

import pytest

from issue_workflow.cli.ui import input_list, input_text


class TestInputList:
    """Tests for input_list function."""

    def test_empty_input_returns_default(self) -> None:
        """Test empty input returns default list."""
        default = ["path1", "path2"]
        with patch("builtins.input", return_value=""):
            result = input_list("Test prompt", default)
        assert result == default

    def test_whitespace_only_input_returns_default(self) -> None:
        """Test whitespace-only input returns default list."""
        default = ["path1", "path2"]
        with patch("builtins.input", return_value="   "):
            result = input_list("Test prompt", default)
        assert result == default

    def test_comma_separated_input_splits_correctly(self) -> None:
        """Test comma-separated input is correctly split."""
        with patch("builtins.input", return_value="item1, item2, item3"):
            result = input_list("Test prompt", [])
        assert result == ["item1", "item2", "item3"]

    def test_empty_items_filtered(self) -> None:
        """Test empty items from splitting are filtered out."""
        with patch("builtins.input", return_value="item1,, item2,  ,item3"):
            result = input_list("Test prompt", [])
        assert result == ["item1", "item2", "item3"]

    def test_items_trimmed(self) -> None:
        """Test items are trimmed of whitespace."""
        with patch("builtins.input", return_value="  item1  ,  item2  "):
            result = input_list("Test prompt", [])
        assert result == ["item1", "item2"]

    def test_single_item_input(self) -> None:
        """Test single item without comma."""
        with patch("builtins.input", return_value="single_item"):
            result = input_list("Test prompt", [])
        assert result == ["single_item"]

    def test_keyboard_interrupt_raised(self) -> None:
        """Test KeyboardInterrupt is raised on interrupt."""
        with (
            patch("builtins.input", side_effect=KeyboardInterrupt),
            pytest.raises(KeyboardInterrupt),
        ):
            input_list("Test prompt", [])

    def test_eof_error_raises_keyboard_interrupt(self) -> None:
        """Test EOFError is converted to KeyboardInterrupt."""
        with (
            patch("builtins.input", side_effect=EOFError),
            pytest.raises(KeyboardInterrupt),
        ):
            input_list("Test prompt", [])


class TestInputText:
    """Tests for input_text function."""

    def test_empty_input_returns_default(self) -> None:
        """Test empty input returns default value."""
        default = "default_value"
        with patch("builtins.input", return_value=""):
            result = input_text("Test prompt", default)
        assert result == default

    def test_whitespace_only_input_returns_default(self) -> None:
        """Test whitespace-only input returns default value."""
        default = "default_value"
        with patch("builtins.input", return_value="   "):
            result = input_text("Test prompt", default)
        assert result == default

    def test_user_input_returned(self) -> None:
        """Test user input is returned when provided."""
        with patch("builtins.input", return_value="user_value"):
            result = input_text("Test prompt", "default")
        assert result == "user_value"

    def test_user_input_trimmed(self) -> None:
        """Test user input is trimmed of whitespace."""
        with patch("builtins.input", return_value="  user_value  "):
            result = input_text("Test prompt", "default")
        assert result == "user_value"

    def test_empty_default_with_empty_input(self) -> None:
        """Test empty default with empty input returns empty string."""
        with patch("builtins.input", return_value=""):
            result = input_text("Test prompt", "")
        assert result == ""

    def test_keyboard_interrupt_raised(self) -> None:
        """Test KeyboardInterrupt is raised on interrupt."""
        with (
            patch("builtins.input", side_effect=KeyboardInterrupt),
            pytest.raises(KeyboardInterrupt),
        ):
            input_text("Test prompt", "default")

    def test_eof_error_raises_keyboard_interrupt(self) -> None:
        """Test EOFError is converted to KeyboardInterrupt."""
        with (
            patch("builtins.input", side_effect=EOFError),
            pytest.raises(KeyboardInterrupt),
        ):
            input_text("Test prompt", "default")
