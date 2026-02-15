---
name: merge-pr
description: Wait for PR CI checks to complete, then execute merge.
---

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

When the user invokes `/merge-pr <number>`, use the bundled `pr-merger` agent to execute the complete workflow.

### Step 1: Spawn PR Merger Agent

Use the Task tool to launch the `pr-merger` agent from `.claude/agents/pr-merger.md`:

```
Task tool with subagent_type: "pr-merger"
```

Pass the PR number and any merge strategy flags as the prompt (e.g., `"123"`, `"456 --merge"`, `"789 --rebase"`).

The agent will handle:
1. PR validation (existence, state, mergeability)
2. CI check waiting
3. Merge execution with specified strategy
4. Post-merge cleanup (branch switch, pull, worktree removal)

## Output Format

### 成功

```
✅ PR #100 merged successfully

Merge method: squash
Base branch: <default-branch>
Remote branch: deleted
Local branch: deleted
Worktree: deleted (if applicable)
```

### 失敗

```
❌ Failed to merge PR #100

Cause: [specific cause]
Resolution: [suggestion]
```

## Error Handling

| エラー | 対応 |
|--------|------|
| PR not found | `PR #N not found` |
| PR already merged | `PR #N is already merged` |
| PR closed | `PR #N is closed` |
| Has conflicts | コンフリクト解消手順を表示 |
| CI failed | 失敗したチェックを表示、確認を求める |
| Merge blocked | ブロック理由を表示（ブランチ保護等） |
