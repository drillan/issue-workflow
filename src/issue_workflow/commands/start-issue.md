# /start-issue

Load a GitHub Issue, create a branch, and develop an implementation plan.

## Usage

```
/start-issue <issue-number> [--force]
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `issue-number` | integer | Yes | GitHub Issue number |
| `--force` | flag | No | Start implementation without confirmation |

## Instructions

When the user invokes `/start-issue <number>`, follow these steps:

### Step 1: Load Issue

```bash
gh issue view <number> --json number,title,body,labels,state
```

Verify the issue exists and is open. If not open, warn the user.

### Step 2: Determine Branch Type

Based on the issue labels and content, determine the appropriate branch prefix:

| Label | Prefix |
|-------|--------|
| `enhancement`, `feature` | `feat/` |
| `bug` | `fix/` |
| `refactoring`, `refactor` | `refactor/` |
| `documentation`, `docs` | `docs/` |
| `test` | `test/` |
| `chore` | `chore/` |

If no matching label, check title/body for keywords. Default to `feat/`.

### Step 3: Create Branch

Generate branch name: `<prefix>/<issue-number>-<normalized-title>`

Normalization rules:
- Lowercase
- Remove special characters
- Replace spaces with hyphens
- Limit to 40 characters

```bash
git checkout -b <branch-name>
```

If branch exists, checkout instead of create.

### Step 4: Plan Implementation

Unless `--force` is specified, enter plan mode and create an implementation plan:

1. Analyze the issue requirements
2. Identify affected files
3. Design test cases (TDD approach)
4. Create step-by-step implementation plan
5. Identify potential risks

### Step 5: Report to Issue

Post the plan as a comment on the issue using issue-reporter skill:

```markdown
## Implementation Plan

**Task**: [Issue title]

### Plan
1. [Step 1]
2. [Step 2]
...

### Expected Challenges
- [Challenge 1]

---
*Posted by Claude Code at YYYY-MM-DD HH:MM*
```

## Output Format

```
## Issue #<number>: <title>

### Requirements
[Requirements extracted from issue body]

### Implementation Plan
1. [Step 1]
2. [Step 2]
...

### Test Plan
- [Test case 1]
- [Test case 2]

### Verification
[Verification steps]
```

## Error Handling

| Error | Action |
|-------|--------|
| Issue not found | Display error with `gh issue view` suggestion |
| Issue is closed | Warn user and ask for confirmation |
| gh not authenticated | Display `gh auth login` instruction |
| Uncommitted changes | Ask user to commit or stash changes |
| Branch creation failed | Display error details |
