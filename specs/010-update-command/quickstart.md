# Quickstart: Update Command

**Date**: 2026-01-15
**Feature**: Update Command
**Spec**: [spec.md](./spec.md)

## Overview

`issue-workflow update`コマンドは、ユーザープロジェクトの`.claude/commands`と`.claude/skills`ディレクトリを最新のツールキット内容で更新します。

## Prerequisites

1. `issue-workflow init`が実行済みで、`.claude/`ディレクトリが存在すること
2. ツールキットがローカルにインストールされていること

## Basic Usage

### 更新の実行

```bash
# commands/skillsを最新版に更新
issue-workflow update
```

出力例:
```
Updating commands and skills...

Commands:
  + review-pr-comments.md (added)
  ~ start-issue.md (updated)

Skills:
  + doc-updater/ (added)

Updated 1 file, added 2 items.
```

### 事前確認（dry-run）

```bash
# 実際の更新を行わず、差分のみ確認
issue-workflow update --dry-run
```

出力例:
```
[DRY-RUN] Calculating changes...

Commands:
  + review-pr-comments.md (would be added)
  ~ start-issue.md (would be updated)

Skills:
  + doc-updater/ (would be added)

Would update 1 file, add 2 items.
No changes were made (dry-run mode).
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--dry-run` | | 実際の更新を行わず差分のみ表示 |
| `--help` | | ヘルプを表示 |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 成功（更新完了またはdry-run完了） |
| 1 | エラー（ファイル操作失敗など） |
| 2 | 未初期化（`.claude/`が存在しない） |

## Error Handling

### `.claude/`が存在しない場合

```
Error: Project not initialized

The .claude/ directory does not exist.
Run 'issue-workflow init' first to initialize the project.
```

### ファイル権限エラー

```
Error: Failed to update some files

The following files could not be updated:
  - commands/start-issue.md: Permission denied

Please check file permissions and try again.
```

## Common Workflows

### 1. ツールキット更新後のプロジェクト同期

```bash
# ツールキットをアップデート
uv pip install -U issue-workflow

# プロジェクトのcommands/skillsを同期
issue-workflow update
```

### 2. CI/CDでの自動更新

```yaml
# GitHub Actions example
- name: Update Issue Workflow
  run: |
    issue-workflow update
```

確認プロンプトなしで実行されるため、CI/CD環境で安全に使用できます。

### 3. 更新前の差分確認

```bash
# 差分を確認
issue-workflow update --dry-run

# 問題なければ実行
issue-workflow update
```

## Notes

- カスタムcommands/skillsは別ディレクトリで管理してください
- 更新はcommands/skillsのみ対象です（workflow-config.jsonやgit-conventions.mdは更新されません）
- ツールキットに存在しないファイルがプロジェクトにある場合、警告が表示されますが自動削除はされません
