"""Unit tests for issue range parser."""

import pytest

from issue_workflow.lib.issue_range import IssueRangeError, parse_issue_range


class TestParseIssueRangeSingle:
    """Single issue number parsing."""

    def test_single_number(self) -> None:
        assert parse_issue_range("30") == [30]

    def test_single_large_number(self) -> None:
        assert parse_issue_range("199") == [199]


class TestParseIssueRangeCommaSeparated:
    """Comma-separated issue numbers."""

    def test_two_numbers(self) -> None:
        assert parse_issue_range("30,40") == [30, 40]

    def test_three_numbers(self) -> None:
        assert parse_issue_range("30,40,50") == [30, 40, 50]

    def test_unsorted_input_returns_sorted(self) -> None:
        assert parse_issue_range("50,30,40") == [30, 40, 50]


class TestParseIssueRangeRange:
    """Range format (start-end) parsing."""

    def test_range_inclusive(self) -> None:
        assert parse_issue_range("30-35") == [30, 31, 32, 33, 34, 35]

    def test_range_single_element(self) -> None:
        """Range where start == end produces single element."""
        assert parse_issue_range("30-30") == [30]


class TestParseIssueRangeMixed:
    """Mixed format: ranges + individual numbers."""

    def test_range_and_single(self) -> None:
        assert parse_issue_range("30-35,40") == [30, 31, 32, 33, 34, 35, 40]

    def test_two_ranges(self) -> None:
        assert parse_issue_range("30-35,42-45") == [
            30,
            31,
            32,
            33,
            34,
            35,
            42,
            43,
            44,
            45,
        ]

    def test_full_mixed(self) -> None:
        assert parse_issue_range("30-35,40,42-45") == [
            30,
            31,
            32,
            33,
            34,
            35,
            40,
            42,
            43,
            44,
            45,
        ]


class TestParseIssueRangeDedup:
    """Deduplication of overlapping ranges/numbers."""

    def test_duplicate_single(self) -> None:
        assert parse_issue_range("30,30") == [30]

    def test_overlapping_range_and_single(self) -> None:
        assert parse_issue_range("30-35,33") == [30, 31, 32, 33, 34, 35]

    def test_overlapping_ranges(self) -> None:
        assert parse_issue_range("30-35,33-37") == [30, 31, 32, 33, 34, 35, 36, 37]


class TestParseIssueRangeWhitespace:
    """Whitespace tolerance."""

    def test_spaces_around_commas(self) -> None:
        assert parse_issue_range(" 30 , 40 ") == [30, 40]

    def test_spaces_around_dash(self) -> None:
        assert parse_issue_range(" 30 - 35 ") == [30, 31, 32, 33, 34, 35]


class TestParseIssueRangeErrors:
    """Error cases raise IssueRangeError."""

    def test_empty_string(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("")

    def test_whitespace_only(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("   ")

    def test_non_numeric(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("abc")

    def test_reversed_range(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("35-30")

    def test_zero(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("0")

    def test_negative_number(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("-5")

    def test_empty_segment(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("30,,40")

    def test_trailing_comma(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("30,")

    def test_trailing_dash(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("30-")

    def test_leading_dash_in_segment(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("-30")

    def test_multiple_dashes(self) -> None:
        with pytest.raises(IssueRangeError):
            parse_issue_range("30-35-40")

    def test_range_too_large(self) -> None:
        """Range exceeding MAX_ISSUE_COUNT raises IssueRangeError."""
        with pytest.raises(IssueRangeError, match="Too many issues"):
            parse_issue_range("1-101")

    def test_combined_ranges_too_large(self) -> None:
        """Combined ranges exceeding MAX_ISSUE_COUNT raises IssueRangeError."""
        with pytest.raises(IssueRangeError, match="Too many issues"):
            parse_issue_range("1-60,70-130")

    def test_range_at_max_limit_succeeds(self) -> None:
        """Exactly MAX_ISSUE_COUNT issues is allowed."""
        result = parse_issue_range("1-100")
        assert len(result) == 100

    def test_issue_range_error_is_value_error(self) -> None:
        """IssueRangeError is a subclass of ValueError."""
        with pytest.raises(ValueError):
            parse_issue_range("")
