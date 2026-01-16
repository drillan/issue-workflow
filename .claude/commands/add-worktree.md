# /add-worktree

Create a new worktree for an Issue.

## Usage

```
/add-worktree <issue-number>
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `issue-number` | integer | Yes | GitHub Issue number |

## Instructions

When the user invokes `/add-worktree <number>`, follow these steps:

### Step 1: Load Issue

```bash
gh issue view <number> --json number,title,body,labels,state
```

Verify the issue exists and is open.

### Step 2: Determine Branch Type

Same logic as `/start-issue`:
- Check labels for branch type mapping
- Fall back to keyword detection
- Default to `feat/`

### Step 3: Generate Names

Branch name:
```
<prefix>/<issue-number>-<normalized-title>
```

Worktree directory:
```
../<project-name>-<branch-name-with-slashes-as-hyphens>
```

Example:
- Branch: `feat/200-add-feature`
- Worktree: `../my-project-feat-200-add-feature`

### Step 4: Check for Existing

Check if worktree or branch already exists:

```bash
git worktree list
git branch --list <branch-name>
```

If exists, report error and show existing path.

### Step 5: Create Worktree

```bash
git worktree add -b <branch-name> <worktree-path>
```

This creates:
1. New branch
2. New worktree directory
3. Checks out the branch in the worktree

### Step 6: Report Success

```
✅ Worktree created successfully

Issue: #200 - [Issue title]
Branch: feat/200-add-feature
Directory: ../my-project-feat-200-add-feature

To start working:
  cd ../my-project-feat-200-add-feature
```

## Output Format

### Success

```
✅ Worktree created successfully

Issue: #<number> - <title>
Branch: <branch-name>
Directory: <worktree-path>

To start working:
  cd <worktree-path>
```

### Already Exists

```
⚠️ Worktree already exists

Issue: #<number> - <title>
Existing path: <existing-path>

To continue working in the existing worktree:
  cd <existing-path>
```

## Error Handling

| Error | Action |
|-------|--------|
| Issue not found | Display error message |
| Branch exists (no worktree) | Suggest creating worktree with existing branch |
| Worktree exists | Show existing path |
| Directory creation failed | Show cause (permissions, path, etc.) |
| Git not in repo | Notify user they're outside a repository |

## Worktree Management Tips

```bash
# List all worktrees
git worktree list

# Remove a worktree
git worktree remove ../my-project-feat-200-add-feature

# Prune stale worktree info
git worktree prune
```
