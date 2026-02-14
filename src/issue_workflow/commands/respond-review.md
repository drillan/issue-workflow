# /respond-review

hachimoku JSONL出力を読み取り、レビュー指摘に対応する。

## Usage

```
/respond-review [PR_NUMBER]
```

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PR_NUMBER` | integer | No | GitHub PR番号（省略時は現在のブランチから検出） |

## Instructions

When the user invokes `/respond-review`, follow these steps:

### Step 1: PR Number Detection

If PR number is not provided, detect from current branch:

```bash
gh pr list --head $(git branch --show-current) --json number --jq '.[0].number'
```

If no PR is found:
```
⚠️ 現在のブランチに紐づくPRが見つかりません
```

### Step 2: Load Review Results

Read the hachimoku JSONL review file:

```bash
cat .hachimoku/reviews/pr-{NUMBER}.jsonl
```

If the file does not exist:
```
⚠️ レビュー結果が見つかりません。`8moku review pr {NUMBER}` を実行してください
```

Parse each line as a JSON object. Each line represents one review finding.

### Step 3: Display Review Table

Sort findings by severity (Critical > Important > Suggestion) and display as a table:

| # | Severity | File | Line | Description | Decision |
|---|----------|------|------|-------------|----------|
| 1 | Important | path/file.py | 28 | Description | (pending) |
| 2 | Suggestion | .gitignore | 228 | Description | (pending) |

Use Rich table formatting for terminal display.

### Step 4: Accept/Reject Decisions

For each finding, determine the response:

- **Accept**: Implement the suggested fix
- **Reject**: Document the reason for rejection

Update the table with decisions:

| # | Severity | File | Line | Description | Decision |
|---|----------|------|------|-------------|----------|
| 1 | Important | path/file.py | 28 | Description | ✅ Accept |
| 2 | Suggestion | .gitignore | 228 | Description | ❌ Reject: cosmetic only |

### Step 5: Implement Fixes

For each accepted finding:
1. Read the referenced file
2. Implement the suggested fix
3. Verify the fix

### Step 6: Commit Changes

After all accepted fixes are implemented:
1. Stage modified files
2. Create a commit with message: `fix: address review feedback for PR #{NUMBER}`

## Output Format

Final summary after all decisions:

```
## Review Response Summary

PR: #{NUMBER}
Accepted: {COUNT}
Rejected: {COUNT}

| # | Decision | File | Action |
|---|----------|------|--------|
| 1 | ✅ Accept | path/file.py | Fixed: added error handling |
| 2 | ❌ Reject | .gitignore | Reason: cosmetic only |
```

## Error Handling

| エラー | 対応 |
|--------|------|
| PR番号が検出できない | `⚠️ 現在のブランチに紐づくPRが見つかりません` |
| JSONLファイルが存在しない | `⚠️ レビュー結果が見つかりません。8moku review pr <番号> を実行してください` |
| JSONLの解析失敗 | `⚠️ レビュー結果ファイルの解析に失敗しました` |
| 修正の適用失敗 | 失敗した修正を報告、他の修正は続行 |
