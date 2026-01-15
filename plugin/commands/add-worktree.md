# /add-worktree

Issue用のワークツリーを新規作成する。

## Usage

```
/add-worktree <issue番号>
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `issue番号` | integer | Yes | GitHub Issue番号 |

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
✅ ワークツリーを作成しました

Issue: #200 - [Issue title]
ブランチ: feat/200-add-feature
ディレクトリ: ../my-project-feat-200-add-feature

作業を開始するには:
  cd ../my-project-feat-200-add-feature
```

## Output Format

### Success

```
✅ ワークツリーを作成しました

Issue: #<number> - <title>
ブランチ: <branch-name>
ディレクトリ: <worktree-path>

作業を開始するには:
  cd <worktree-path>
```

### Already Exists

```
⚠️ ワークツリーが既に存在します

Issue: #<number> - <title>
既存パス: <existing-path>

既存のワークツリーで作業を続けるには:
  cd <existing-path>
```

## Error Handling

| Error | Action |
|-------|--------|
| Issue not found | エラーメッセージを表示 |
| Branch exists (no worktree) | 既存ブランチで worktree 作成を提案 |
| Worktree exists | 既存パスを表示 |
| Directory creation failed | 原因を表示（権限、パス等） |
| Git not in repo | リポジトリ外であることを通知 |

## Worktree Management Tips

```bash
# List all worktrees
git worktree list

# Remove a worktree
git worktree remove ../my-project-feat-200-add-feature

# Prune stale worktree info
git worktree prune
```
