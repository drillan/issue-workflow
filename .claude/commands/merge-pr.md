# /merge-pr

Wait for PR CI checks to complete, then execute merge.

## Usage

```
/merge-pr <pr-number> [--merge|--rebase]
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `pr-number` | integer | Yes | GitHub PR number |
| `--merge` | flag | No | Create a merge commit |
| `--rebase` | flag | No | Rebase merge |

Default: `--squash` (squash commits into one)

## Instructions

When the user invokes `/merge-pr <number>`, follow these steps:

### Step 1: Verify PR Status

```bash
gh pr view <number> --json number,title,state,mergeable,baseRefName,headRefName
```

Check:
- PR exists
- PR is not already merged
- PR is not closed
- PR is mergeable (no conflicts)

### Step 2: Wait for CI

```bash
gh pr checks <number> --watch
```

If CI fails:
- Report failed checks
- Ask user if they want to proceed anyway (not recommended)

### Step 3: Execute Merge

Default (squash):
```bash
gh pr merge <number> --squash --delete-branch
```

With merge commit:
```bash
gh pr merge <number> --merge --delete-branch
```

With rebase:
```bash
gh pr merge <number> --rebase --delete-branch
```

### Step 4: Post-Merge Cleanup

1. Switch to main branch:
   ```bash
   git checkout main
   ```

2. Pull latest changes:
   ```bash
   git pull
   ```

3. Check for associated worktree:
   - Find worktree for the merged branch
   - If found, remove it:
     ```bash
     git worktree remove <path>
     git worktree prune
     ```

4. Delete local branch (already done by --delete-branch, but verify):
   ```bash
   git branch -d <branch-name>
   ```

## Output Format

### Success

```
✅ PR #100 merged successfully

Merge method: squash
Base branch: main
Remote branch: deleted
Local branch: deleted
Worktree: deleted (if applicable)
```

### Failure

```
❌ Failed to merge PR #100

Cause: [specific cause]
Resolution: [suggestion]
```

## Error Handling

| Error | Action |
|-------|--------|
| PR not found | `⚠️ PR #N not found` |
| PR already merged | `ℹ️ PR #N is already merged` |
| PR closed | `⚠️ PR #N is closed` |
| Has conflicts | Provide conflict resolution guidance |
| CI failed | Show failed checks and ask for confirmation |
| Merge blocked | Show block reason (branch protection, etc.) |

## Safety Checks

1. **Never force merge** without explicit user confirmation
2. **Always show diff** before merge if changes are large
3. **Warn about breaking changes** if detected in commit messages
4. **Suggest squash** for PRs with many small commits
