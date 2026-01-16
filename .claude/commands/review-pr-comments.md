# /review-pr-comments

Review and respond to PR review comments.

## Usage

```
/review-pr-comments [pr-number]
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `pr-number` | integer | No | GitHub PR number (auto-detect from current branch if omitted) |

## Instructions

When the user invokes `/review-pr-comments`, follow these steps:

### Step 1: Determine PR Number

If PR number is provided:
- Use the provided number

If not provided:
- Get current branch name
- Find PR for this branch:
  ```bash
  gh pr list --head <branch-name> --json number --limit 1
  ```

### Step 2: Fetch Comments

```bash
gh api repos/{owner}/{repo}/pulls/<number>/comments
```

Parse and group comments by thread/file.

### Step 3: Display Comment Table

Present comments in a table format:

```
| Thread ID | File | Issue | Decision | Action |
|-----------|------|-------|----------|--------|
| PRRT_xxx | src/auth.py:10 | "Fix null check" | ? | - |
| PRRT_yyy | src/user.py:20 | "Consider error handling" | ? | - |
```

### Step 4: Process Each Comment

For each comment, ask the user:
1. **Accept** - Make the suggested change
2. **Reject** - Reply with reason and resolve thread
3. **Discuss** - Reply asking for clarification
4. **Skip** - Leave for later

### Step 5: Execute Actions

For accepted comments:
- Make the code changes
- Reply to thread: "Fixed in <commit-hash>"
- Resolve the thread

For rejected comments:
- Reply with reason provided by user
- Resolve the thread

### Step 6: Create Summary

Post a summary comment on the PR:

```markdown
## Review Response Summary

### Accepted (2)
- [src/auth.py:10] Fixed null check
- [src/user.py:20] Added error handling

### Rejected (1)
- [src/api.py:5] Reason: Current approach is intentional for...

### Pending (0)
None

---
*Reviewed by Claude Code at YYYY-MM-DD HH:MM*
```

### Step 7: Commit Changes

If changes were made:
```bash
git add .
git commit -m "address review comments"
```

## Output Format

### Comment List

```
## PR #100 - Review Comments

### Unresolved Comments (3)

| # | File | Line | Comment | Author |
|---|------|------|---------|--------|
| 1 | src/auth.py | 10 | "Add null check" | @reviewer |
| 2 | src/auth.py | 25 | "Consider edge case" | @reviewer |
| 3 | src/user.py | 15 | "Rename variable" | @lead |

For each comment, choose:
[A]ccept | [R]eject | [D]iscuss | [S]kip
```

## Error Handling

| Error | Action |
|-------|--------|
| PR not detected | `⚠️ No PR found for current branch` |
| PR not found | Display error message |
| No comments | `ℹ️ No review comments found` |
| API error | Display error details |

## Tips

- Use `--web` to open PR in browser for context:
  ```bash
  gh pr view <number> --web
  ```
- Group related comments and address them together
- Explain rejections clearly to avoid back-and-forth
