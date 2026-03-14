"""Parser for issue range specifier strings."""


class IssueRangeError(ValueError):
    """Raised when the issue range string is invalid."""


def _parse_segment(segment: str) -> list[int]:
    """Parse a single segment (number or range) into issue numbers.

    Args:
        segment: A single number ("30") or range ("30-35").

    Returns:
        List of issue numbers from this segment.

    Raises:
        IssueRangeError: If the segment is invalid.
    """
    stripped = segment.strip()
    if not stripped:
        raise IssueRangeError(f"Empty segment in issue range: '{segment}'")

    parts = stripped.split("-")

    if len(parts) == 1:
        try:
            num = int(parts[0])
        except ValueError:
            raise IssueRangeError(f"Invalid issue number: '{parts[0]}'") from None
        if num <= 0:
            raise IssueRangeError(f"Issue number must be positive: {num}")
        return [num]

    if len(parts) == 2:
        try:
            start = int(parts[0].strip())
            end = int(parts[1].strip())
        except ValueError:
            raise IssueRangeError(f"Invalid range: '{stripped}'") from None
        if start <= 0 or end <= 0:
            raise IssueRangeError(f"Issue numbers must be positive: '{stripped}'")
        if start > end:
            raise IssueRangeError(f"Invalid range: start ({start}) > end ({end}) in '{stripped}'")
        return list(range(start, end + 1))

    raise IssueRangeError(f"Invalid segment (multiple dashes): '{stripped}'")


def parse_issue_range(spec: str) -> list[int]:
    """Parse issue range specifier into sorted, deduplicated issue numbers.

    Supports single numbers, comma-separated lists, ranges, and combinations.

    Examples:
        "30"            -> [30]
        "30,40,50"      -> [30, 40, 50]
        "30-35"         -> [30, 31, 32, 33, 34, 35]
        "30-35,40,42-45" -> [30, 31, 32, 33, 34, 35, 40, 42, 43, 44, 45]

    Args:
        spec: Issue range specifier string.

    Returns:
        Sorted, deduplicated list of positive issue numbers.

    Raises:
        IssueRangeError: If the specifier is empty, contains invalid
            tokens, reversed ranges, or non-positive numbers.
    """
    if not spec.strip():
        raise IssueRangeError("Issue range specifier cannot be empty")

    segments = spec.split(",")
    issue_numbers: set[int] = set()

    for segment in segments:
        issue_numbers.update(_parse_segment(segment))

    return sorted(issue_numbers)
