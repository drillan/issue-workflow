---
name: respond-review
description: Read hachimoku JSONL output and respond to review feedback.
---

# /respond-review

hachimoku JSONL出力を読み取り、レビュー指摘に対応する。

## Usage

```
/respond-review [PR_NUMBER]
/respond-review --diff
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PR_NUMBER` | integer | No | GitHub PR番号（省略時は現在のブランチから検出） |
| `--diff` | flag | No | diff型のレビュー結果を読み取る |

## Instructions

When the user invokes `/respond-review`, follow these steps:

### Step 1: Review File Detection

Determine the JSONL file path based on arguments:

**Case 1: `--diff` が指定された場合**

```bash
cat .hachimoku/reviews/diff.jsonl
```

**Case 2: PR番号が指定された場合**

```bash
cat .hachimoku/reviews/pr-{NUMBER}.jsonl
```

**Case 3: 引数なし（PR番号を自動検出）**

```bash
gh pr list --head "$(git branch --show-current)" --state open --json number --jq '.[0].number'
```

検出されたPR番号で `.hachimoku/reviews/pr-{NUMBER}.jsonl` を読み取る。

**エラーハンドリング:**

PRが検出できない場合:
```
現在のブランチに紐づくPRが見つかりません。PR番号を指定するか --diff を使用してください。
```

ファイルが存在しない場合:
```
レビュー結果が見つかりません。
  PR型: `8moku {NUMBER}` を実行してください
  diff型: `8moku` を実行してください
```

### Step 2: Parse JSONL

JSONL ファイルの各行は **1つのレビューセッション** を表す JSON オブジェクトです。

#### JSONL 構造

```json
{
  "review_mode": "diff" | "pr",
  "commit_hash": "40文字の16進数",
  "branch_name": "ブランチ名",
  "reviewed_at": "ISO 8601 タイムスタンプ",
  "results": [
    {
      "status": "success" | "error",
      "agent_name": "エージェント名",
      "issues": [
        {
          "agent_name": "エージェント名",
          "severity": "Critical" | "Important" | "Suggestion" | "Nitpick",
          "description": "指摘内容",
          "location": {"file_path": "ファイルパス", "line_number": 行番号} | null,
          "suggestion": "修正提案" | null,
          "category": "カテゴリ名" | null
        }
      ],
      "elapsed_time": 秒数
    }
  ],
  "summary": {
    "total_issues": 指摘数,
    "max_severity": "最大重要度" | null
  }
}
```

#### パース手順

1. 各行を JSON としてパースする
2. **最新のレビューセッション**（最終行）を使用する
3. `results[]` 配列の各エージェント結果を確認:
   - `status: "success"` のエージェントから `issues[]` を収集
   - `status: "error"` のエージェントはスキップし、警告を表示:
     ```
     エージェント "{agent_name}" はエラーで終了しました: {error_message}
     ```
4. 全エージェントの `issues[]` をフラット化して1つのリストにまとめる

パースに失敗した場合:
```
レビュー結果ファイルの解析に失敗しました
```

### Step 3: Display Review Table

指摘を重要度順にソートして表示する。

**ソート順**: Critical > Important > Suggestion > Nitpick

| # | Severity | Agent | File | Line | Description | Decision |
|---|----------|-------|------|------|-------------|----------|
| 1 | Critical | code-reviewer | path/file.py | 28 | Description | (pending) |
| 2 | Important | type-analyzer | path/other.py | 42 | Description | (pending) |
| 3 | Suggestion | code-reviewer | .gitignore | 228 | Description | (pending) |
| 4 | Nitpick | code-reviewer | tasks.md | 334 | Description | (pending) |

ヘッダーに以下のメタデータを表示:

```
## Review Results

Mode: {review_mode} | Commit: {commit_hash の先頭7文字} | Date: {reviewed_at}
Total Issues: {summary.total_issues} | Max Severity: {summary.max_severity}
```

### Step 4: Accept/Reject Decisions

各指摘について対応方針を決定する:

- **Accept**: 修正を実装する
- **Reject**: 理由を記録してスキップ

テーブルを更新:

| # | Severity | Agent | File | Line | Description | Decision |
|---|----------|-------|------|------|-------------|----------|
| 1 | Critical | code-reviewer | path/file.py | 28 | Description | Accept |
| 2 | Important | type-analyzer | path/other.py | 42 | Description | Reject: cosmetic only |

### Step 5: Implement Fixes

Accept した各指摘に対して:

1. 該当ファイルを読み込む
2. `suggestion` フィールドの内容を参考に修正を実装
3. 修正が正しいことを確認

### Step 6: Commit Changes

全ての Accept した修正が完了したら:

1. 変更されたファイルをステージング
2. コミットメッセージを作成: `fix: address hachimoku review feedback`

## Output Format

最終サマリー:

```
## Review Response Summary

Mode: {review_mode} | Commit: {commit_hash の先頭7文字}
Accepted: {COUNT} | Rejected: {COUNT}

| # | Decision | File | Action |
|---|----------|------|--------|
| 1 | Accept | path/file.py | Fixed: added error handling |
| 2 | Reject | .gitignore | Reason: cosmetic only |
```

## Error Handling

| エラー | 対応 |
|--------|------|
| PR番号が検出できない | `現在のブランチに紐づくPRが見つかりません。PR番号を指定するか --diff を使用してください。` |
| JSONLファイルが存在しない | `レビュー結果が見つかりません。8moku <番号> または 8moku を実行してください` |
| JSONLの解析失敗 | `レビュー結果ファイルの解析に失敗しました` |
| エージェントがエラー終了 | `エージェント "{name}" はエラーで終了しました: {message}` （他のエージェント結果は続行） |
| 修正の適用失敗 | 失敗した修正を報告、他の修正は続行 |
