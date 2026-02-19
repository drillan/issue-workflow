"""Branch service for type detection and name generation."""

from issue_workflow.models.branch import BranchType
from issue_workflow.models.issue import Issue

# Label to branch type mapping
LABEL_MAPPING: dict[str, BranchType] = {
    "enhancement": BranchType.FEAT,
    "feature": BranchType.FEAT,
    "bug": BranchType.FIX,
    "refactoring": BranchType.REFACTOR,
    "refactor": BranchType.REFACTOR,
    "documentation": BranchType.DOCS,
    "docs": BranchType.DOCS,
    "test": BranchType.TEST,
    "chore": BranchType.CHORE,
}

# Keyword to branch type mapping (fallback)
KEYWORD_MAPPING: dict[BranchType, list[str]] = {
    BranchType.FIX: ["bug", "fix", "error", "issue"],
    BranchType.REFACTOR: ["refactor", "cleanup", "improve", "reorganize"],
    BranchType.DOCS: ["doc", "readme", "documentation"],
    BranchType.TEST: ["test", "testing"],
    BranchType.CHORE: ["chore", "config", "setup", "dependency"],
    BranchType.FEAT: ["add", "feature", "implement", "create", "new"],
}


def detect_branch_type(issue: Issue) -> BranchType:
    """Detect branch type from issue labels and keywords.

    Detection priority:
    1. GitHub labels (highest)
    2. Keywords in title/body
    3. Default to feat (lowest)

    Args:
        issue: Issue to analyze

    Returns:
        Detected branch type
    """
    # Check labels first
    for label in issue.labels:
        label_lower = label.lower()
        if label_lower in LABEL_MAPPING:
            return LABEL_MAPPING[label_lower]

    # Check keywords in title and body
    text = f"{issue.title} {issue.body}".lower()
    for branch_type, keywords in KEYWORD_MAPPING.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return branch_type

    # Default to feat
    return BranchType.FEAT
