---
name: issue-reporter
description: Automatically report work progress as comments on GitHub Issues. Use upon completion of major milestones, PR creation, merge completion, or when explicitly requested.
---

# issue-reporter

Automatically report work progress as comments on Issues.

## Overview

This skill enables Claude Code to automatically post progress reports to the relevant GitHub Issue upon work completion.

## Trigger

- When explicitly requested by user
- Upon completion of major milestones (PR creation, merge completion, etc.)
- When user wants to record errors or issues

## Instructions

### Step 1: Identify Current Issue

Extract Issue number from current branch name:

```bash
# Get current branch name
git branch --show-current
```

Branch name pattern: `<type>/<issue-number>-<description>`

Example: `feat/123-add-auth` → Issue #123

### Step 2: Gather Progress Information

Collect the following information:

1. **Completed tasks** - Features implemented/fixed
2. **Changed files** - Summary of `git diff --stat`
3. **Test results** - Test execution status
4. **Next steps** - Remaining tasks

### Step 3: Format Report

```markdown
## Progress Update

### Completed
- [x] Implemented user authentication
- [x] Added unit tests for auth module
- [x] Passed all quality checks

### Changes
- Modified 5 files
- Added 200 lines, removed 50 lines

### Test Results
✅ All tests passing (24/24)

### Next Steps
- [ ] Add integration tests
- [ ] Update documentation

---
*Auto-reported by Claude Code at YYYY-MM-DD HH:MM*
```

### Step 4: Post Comment

```bash
gh issue comment <issue-number> --body "<formatted-report>"
```

## Configuration

### Report Types

| Type | Trigger | Content |
|------|---------|---------|
| `milestone` | Major completion | Full progress report |
| `daily` | End of work session | Summary of changes |
| `error` | Problem encountered | Error details and context |
| `completion` | Issue resolved | Final summary |

### Automation Level

| Level | Behavior |
|-------|----------|
| `manual` | Only when requested |
| `milestone` | On major milestones |
| `auto` | Automatic at intervals |

## Output Format

### Success

```
✅ Progress report posted to Issue #123

Posted content:
  - Completed tasks: 3
  - Changed files: 5
  - Test results: 24/24 passing
```

### Failure

```
⚠️ Failed to post comment to Issue #123

Cause: <error-message>
Resolution: <suggestion>
```

## Error Handling

| Error | Action |
|-------|--------|
| Issue number not found | `⚠️ Cannot detect Issue number from current branch` |
| Issue not found | `⚠️ Issue #N not found` |
| No permission | `⚠️ No permission to comment on this repository` |
| API error | Display error details |

## Integration with Workflow

This skill integrates with the following workflow steps:

1. **After start-issue** - Notify work start
2. **After PR creation** - Report PR number and link
3. **After review response** - Summary of responses
4. **After merge completion** - Close report

## Best Practices

1. **Be concise** - Avoid overly long reports
2. **Be specific** - Clearly describe implemented features
3. **Next steps** - Clarify remaining tasks
4. **Moderate frequency** - Avoid posting too frequently
