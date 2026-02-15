# CLI Contract: Workflow Subcommands

**Feature Branch**: `011-workflow-subcommands`
**Date**: 2026-02-15

## Global Options (all subcommands)

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--verbose` | `-v` | `bool` | `False` | stream-json 形式で途中経過を表示 |
| `--timeout` | | `int` | `3600` | claude -p のタイムアウト（秒） |
| `--help` | `-h` | | | 使用方法を表示 |

**Note**: `-v` はメインコマンドでは `--version` に使用されているが、サブコマンドレベルでは `--verbose` に使用する。Typer はサブコマンドごとにオプションを分離するため競合しない。

---

## Subcommand: `start-issue`

```
issue-workflow start-issue [OPTIONS] ISSUE_NUMBER
```

### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ISSUE_NUMBER` | `int` | Yes | GitHub Issue 番号 |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--worktree` | `bool` | `False` | worktree を作成してスキル実行 |

### Behavior

1. 依存チェック: `claude` (+ `gh` when `--worktree`)
2. `--worktree` 時:
   a. 既存 worktree を検出（`find_worktree_for_branch` + `lib_find_worktree_dir` 相当）
   b. なければ worktree 作成 + `.hachimoku/` コピー
   c. worktree ディレクトリを cwd として `claude -p` 実行
3. `--worktree` なし時:
   a. カレントディレクトリを cwd として `claude -p` 実行

### Prompt

```
/start-issue {issue_number}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 成功 |
| 1 | 引数エラー / 依存コマンド不足 / claude -p 失敗 |

---

## Subcommand: `create-pr`

```
issue-workflow create-pr [OPTIONS]
```

### Arguments

なし

### Behavior

1. 依存チェック: `claude`
2. カレントディレクトリで `claude -p` 実行

### Prompt

```
/commit-push-pr
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 成功 |
| 1 | 依存コマンド不足 / claude -p 失敗 |

---

## Subcommand: `review-pr`

```
issue-workflow review-pr [OPTIONS] [PR_NUMBER]
```

### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `PR_NUMBER` | `int` | No | PR 番号（省略時は自動検出） |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--review-only` | `bool` | `False` | hachimoku レビューのみ実行 |
| `--respond-only` | `bool` | `False` | respond-review のみ実行 |

### Validation

- `--review-only` と `--respond-only` は相互排他。同時指定時はエラー

### Behavior

1. 依存チェック: 条件に応じて `claude`, `gh`, `8moku`
2. PR 番号検出（引数優先、省略時は自動検出）
3. `--respond-only` でなければ: `8moku {pr_number}` を `subprocess.run` で実行
4. `--review-only` でなければ: `claude -p "/respond-review {pr_number}"` を実行

### Prompt (respond phase)

```
/respond-review {pr_number}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 成功 |
| 1 | 引数エラー / 相互排他エラー / PR未検出 / 依存コマンド不足 / 実行失敗 |

---

## Subcommand: `push-changes`

```
issue-workflow push-changes [OPTIONS]
```

### Arguments

なし

### Behavior

1. 依存チェック: `claude`
2. カレントディレクトリで `claude -p` 実行

### Prompt

```
/commit-push-pr

レビュー対応後の変更をコミットし、リモートにプッシュしてください。PRが既に存在する場合はPR作成をスキップしてください。
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 成功 |
| 1 | 依存コマンド不足 / claude -p 失敗 |

---

## Subcommand: `respond-comments`

```
issue-workflow respond-comments [OPTIONS] [PR_NUMBER]
```

### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `PR_NUMBER` | `int` | No | PR 番号（省略時は自動検出） |

### Behavior

1. 依存チェック: `claude`, `gh`
2. PR 番号検出（引数優先、省略時は自動検出）
3. `claude -p "/review-pr-comments {pr_number}"` を実行

### Prompt

```
/review-pr-comments {pr_number}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 成功 |
| 1 | PR未検出 / 依存コマンド不足 / claude -p 失敗 |

---

## Subcommand: `merge-pr`

```
issue-workflow merge-pr [OPTIONS] [PR_NUMBER]
```

### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `PR_NUMBER` | `int` | No | PR 番号（省略時は自動検出） |

### Behavior

1. 依存チェック: `claude`, `gh`
2. PR 番号検出（引数優先、省略時は自動検出）
3. `claude -p "/merge-pr {pr_number}"` を実行

### Prompt

```
/merge-pr {pr_number}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 成功 |
| 1 | PR未検出 / 依存コマンド不足 / claude -p 失敗 |

---

## Subcommand: `run`

```
issue-workflow run [OPTIONS] ISSUE_NUMBER
```

### Arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ISSUE_NUMBER` | `int` | Yes | GitHub Issue 番号 |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--worktree` | `bool` | `False` | worktree を使用してワークフロー実行 |

### Behavior (WorkflowContext による順次実行)

`WorkflowContext` (インメモリ) でステップ間のメタデータを伝播する。

| Step | Command | ctx 入力 | ctx 出力 | cwd (no worktree) | cwd (with worktree) |
|------|---------|----------|----------|--------------------|--------------------|
| 0 (optional) | worktree 準備 | `issue_number` | `worktree_path` | N/A | メインリポジトリ |
| 1 | start-issue | `issue_number` | `step_results` | カレント | `ctx.worktree_path` |
| 2 | create-pr | - | `step_results`, `pr_number` (detect_pr_number) | カレント | `ctx.worktree_path` |
| 3a | review-pr (hachimoku) | `pr_number` | - | カレント | `ctx.worktree_path` |
| 3b | review-pr (respond) | `pr_number` | `step_results` | カレント | `ctx.worktree_path` |
| 3c | respond-comments | `pr_number` | `step_results` | カレント | `ctx.worktree_path` |
| 3d | push-changes | - | `step_results` | カレント | `ctx.worktree_path` |
| 4 | merge-pr | `pr_number` | `step_results` | カレント | `ctx.cwd_for_merge` (= None) |

### Step 間のフロー制御

各ステップ完了後:
1. `ClaudeResult` を `ctx.step_results` に追加
2. `ctx.has_error` チェック → `True` なら即時終了（失敗ステップ名とログパスを表示）
3. Step 2 完了後: `detect_pr_number()` で PR 番号を取得 → `ctx.pr_number` に設定
4. ログファイル名に `ctx.log_number_for_step(command)` を使用（Issue番号/PR番号を含む）

### 失敗時の再開

`WorkflowContext` は永続化しない。途中再開は個別サブコマンドで対応:

```bash
# Step 3 で失敗した場合:
issue-workflow review-pr          # PR番号は gh から自動検出
issue-workflow push-changes
issue-workflow merge-pr
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 全ステップ成功 |
| 1 | いずれかのステップで失敗（失敗ステップ名を表示） |

---

## JSONL Log Format

### File Path

```
.issue-workflow/logs/YYYY-MM-DD/<command>-<number>-<ISO8601>.jsonl
```

Examples:
- `start-issue-199-2026-02-15T10-30-00.jsonl`
- `create-pr-2026-02-15T10-45-00.jsonl` (番号なし)

### Log Entry (one line per execution)

```json
{
  "timestamp": "2026-02-15T10:30:00+09:00",
  "command": "start-issue",
  "args": {"issue_number": 199, "worktree": true},
  "exit_code": 0,
  "result": { "type": "result", "subtype": "success", "result": "...", ... }
}
```

### Error Case

```json
{
  "timestamp": "2026-02-15T10:30:00+09:00",
  "command": "start-issue",
  "args": {"issue_number": 199},
  "exit_code": 1,
  "result": { "type": "result", "subtype": "error_max_budget_usd", "is_error": true, ... }
}
```

### Timeout Case

```json
{
  "timestamp": "2026-02-15T10:30:00+09:00",
  "command": "start-issue",
  "args": {"issue_number": 199},
  "exit_code": -1,
  "result": {"error": "timeout", "timeout_seconds": 3600}
}
```

---

## Console Output (non-verbose)

```
[start-issue] Starting...
[start-issue] Done. (exit_code=0)
```

## Console Output (verbose)

```
[start-issue] Starting... (verbose mode)
● Bash(git status...)
● Read(/path/to/file...)
● Edit(/path/to/file...)
[start-issue] Done. (exit_code=0)
```

## Security Notice (`--help` output)

各サブコマンドの `--help` に以下を含める:

```
⚠️  Security: This command uses --dangerously-skip-permissions to bypass
Claude Code's permission checks for automated execution. Only run in
trusted environments.
```
