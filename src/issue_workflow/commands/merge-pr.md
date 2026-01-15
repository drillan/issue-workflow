# /merge-pr

PRのCIチェックが完了するまで待機し、マージを実行する。

## Usage

```
/merge-pr <PR番号> [--merge|--rebase]
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PR番号` | integer | Yes | GitHub PR番号 |
| `--merge` | flag | No | マージコミットを作成 |
| `--rebase` | flag | No | リベースマージ |

デフォルト: `--squash`（コミットを1つにまとめる）

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
✅ PR #100 をマージしました

マージ方法: squash
ベースブランチ: main
リモートブランチ: 削除済み
ローカルブランチ: 削除済み
ワークツリー: 削除済み (該当する場合)
```

### Failure

```
❌ PR #100 のマージに失敗しました

原因: [具体的な原因]
解決方法: [提案]
```

## Error Handling

| Error | Action |
|-------|--------|
| PR not found | `⚠️ PR #N が見つかりません` |
| PR already merged | `ℹ️ PR #N は既にマージ済みです` |
| PR closed | `⚠️ PR #N はクローズされています` |
| Has conflicts | コンフリクト解消方法を案内 |
| CI failed | 失敗したチェックを表示し確認を求める |
| Merge blocked | ブロック理由（branch protection等）を表示 |

## Safety Checks

1. **Never force merge** without explicit user confirmation
2. **Always show diff** before merge if changes are large
3. **Warn about breaking changes** if detected in commit messages
4. **Suggest squash** for PRs with many small commits
