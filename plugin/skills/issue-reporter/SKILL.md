# issue-reporter

作業進捗をIssueにコメントとして自動報告する。

## Overview

このスキルは、Claude Codeが作業完了時に該当のGitHub Issueに進捗レポートを自動投稿するための仕組みを提供します。

## Trigger

- ユーザーから明示的に指示された場合
- 重要なマイルストーン完了時（PR作成、マージ完了など）
- エラーや問題発生時にユーザーが記録を望む場合

## Instructions

### Step 1: Identify Current Issue

現在のブランチ名からIssue番号を抽出:

```bash
# Get current branch name
git branch --show-current
```

ブランチ名パターン: `<type>/<issue-number>-<description>`

例: `feat/123-add-auth` → Issue #123

### Step 2: Gather Progress Information

以下の情報を収集:

1. **完了したタスク** - 実装した機能・修正
2. **変更ファイル** - `git diff --stat`の概要
3. **テスト結果** - テストの実行状況
4. **次のステップ** - 残りのタスク

### Step 3: Format Report

```markdown
## 📊 Progress Update

### Completed
- [x] Implemented user authentication
- [x] Added unit tests for auth module
- [x] Passed all quality checks

### Changes
- Modified 5 files
- Added 200 lines, removed 50 lines

### Test Results
✅ All tests passing (24/24)

### Next Steps
- [ ] Add integration tests
- [ ] Update documentation

---
*Auto-reported by Claude Code at YYYY-MM-DD HH:MM*
```

### Step 4: Post Comment

```bash
gh issue comment <issue-number> --body "<formatted-report>"
```

## Configuration

### Report Types

| Type | Trigger | Content |
|------|---------|---------|
| `milestone` | Major completion | Full progress report |
| `daily` | End of work session | Summary of changes |
| `error` | Problem encountered | Error details and context |
| `completion` | Issue resolved | Final summary |

### Automation Level

| Level | Behavior |
|-------|----------|
| `manual` | Only when requested |
| `milestone` | On major milestones |
| `auto` | Automatic at intervals |

## Output Format

### Success

```
✅ Issue #123 に進捗レポートを投稿しました

投稿内容:
  - 完了タスク: 3件
  - 変更ファイル: 5件
  - テスト結果: 24/24 通過
```

### Failure

```
⚠️ Issue #123 へのコメント投稿に失敗しました

原因: <error-message>
解決方法: <suggestion>
```

## Error Handling

| Error | Action |
|-------|--------|
| Issue number not found | `⚠️ 現在のブランチからIssue番号を検出できません` |
| Issue not found | `⚠️ Issue #N が見つかりません` |
| No permission | `⚠️ このリポジトリへのコメント権限がありません` |
| API error | エラー詳細を表示 |

## Integration with Workflow

このスキルは以下のワークフローステップと連携します:

1. **start-issue後** - 作業開始の通知
2. **PR作成後** - PR番号とリンクの報告
3. **レビュー対応後** - 対応内容のサマリー
4. **マージ完了後** - クローズ報告

## Best Practices

1. **簡潔に** - 長すぎるレポートは避ける
2. **具体的に** - 実装した機能を明確に記載
3. **次のステップ** - 残りのタスクを明確化
4. **適度な頻度** - 頻繁すぎる投稿は避ける
