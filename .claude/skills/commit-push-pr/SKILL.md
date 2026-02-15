---
name: commit-push-pr
description: Commit changes, push to remote, and create a PR in a single workflow.
---

# /commit-push-pr

変更のコミット、プッシュ、PR作成を一連で実行する。

## Usage

```
/commit-push-pr
```

## Instructions

When the user invokes `/commit-push-pr`, use the bundled `pr-creator` agent to execute the complete workflow.

### Step 1: Spawn PR Creator Agent

Use the Task tool to launch the `pr-creator` agent from `.claude/agents/pr-creator.md`:

```
Task tool with subagent_type: "pr-creator"
```

The agent will handle:
1. Branch management
2. Commit creation with auto-generated message
3. Push to remote
4. PR existence check
5. PR creation with issue linkage (only if no PR exists for the branch)

### Step 2: Base Branch Detection

The agent automatically detects the base branch using:
```bash
BASE_BRANCH=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')
git remote set-head origin "$BASE_BRANCH"
```

This queries the GitHub API for the actual default branch and syncs the local reference.

### Step 3: Quality Verification

Before creating the PR, verify that quality checks pass according to `workflow-config.json`:
```bash
cat .claude/workflow-config.json
```

If `workflow.quality_gate_required` is true, run the quality checks defined in `quality.all` before committing.

## Output Format

### PRが新規作成された場合

```
✅ コミット、プッシュ、PR作成が完了しました

コミット: {COMMIT_HASH} {COMMIT_MESSAGE}
PR: #{PR_NUMBER} - {PR_TITLE}
URL: {PR_URL}
```

### PRが既に存在する場合

```
✅ コミット、プッシュが完了しました（PR作成スキップ）

コミット: {COMMIT_HASH} {COMMIT_MESSAGE}
プッシュ: {BRANCH_NAME}
既存PR: #{PR_NUMBER}
```

## Error Handling

| エラー | 対応 |
|--------|------|
| 変更なし | `ℹ️ コミットする変更がありません` |
| プッシュ失敗 | 原因を表示（認証、ネットワーク等） |
| PR既存 | `ℹ️ PRが既に存在するためPR作成をスキップし、commit + pushのみ実行しました` |
| PR作成失敗 | 原因を表示（権限等） |
| 品質チェック失敗 | 失敗したチェックを表示、修正を促す |
