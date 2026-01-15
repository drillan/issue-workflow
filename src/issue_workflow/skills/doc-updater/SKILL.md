# doc-updater

関連ドキュメントの更新が必要な変更を検出し、更新を提案・実行する。

## Overview

このスキルは、コード変更に伴うドキュメントの更新漏れを防ぎます。API変更、設定オプション追加、機能追加などを検出し、関連するREADME、API仕様、設定ガイドなどの更新を提案します。

## Trigger

- コード変更がドキュメント影響を持つ可能性がある場合
- ユーザーが明示的にドキュメント更新を要求した場合
- PR作成前のチェックリスト実行時

## Instructions

### Step 1: Analyze Changes

変更内容を分析してドキュメント影響を判定:

```bash
# Get changed files
git diff --name-only HEAD~1

# Get detailed diff
git diff HEAD~1
```

### Step 2: Identify Documentation Impact

以下のパターンを検出:

| Change Type | Documentation Impact |
|-------------|---------------------|
| New CLI option | `--help` output, README |
| API endpoint added/changed | API documentation |
| Configuration option added | Config guide |
| Environment variable added | Setup guide |
| Feature added | Feature documentation |
| Breaking change | Migration guide, CHANGELOG |

### Step 3: Find Related Documents

```bash
# Find documentation files
find . -name "*.md" -type f
find . -name "README*" -type f
find docs/ -type f 2>/dev/null
```

ドキュメントの場所を特定:
- `README.md` - プロジェクト概要
- `docs/` - 詳細ドキュメント
- `CHANGELOG.md` - 変更履歴
- `API.md` - API仕様
- `CONTRIBUTING.md` - 貢献ガイド

### Step 4: Generate Update Suggestions

変更タイプに応じた更新提案を生成:

#### CLI Option Added

```markdown
## 📝 ドキュメント更新提案

### README.md
`--new-option` オプションの説明を追加:

```diff
+ ### New Option
+ Use `--new-option` to enable the new feature.
```

### Configuration Change

```markdown
## 📝 ドキュメント更新提案

### docs/configuration.md
新しい設定オプションを追加:

```diff
+ ## new_setting
+
+ Type: `boolean`
+ Default: `false`
+
+ Enables the new feature.
```

### Step 5: Execute Updates

ユーザーの承認後、ドキュメントを更新:

1. 対象ファイルを編集
2. 変更をステージング
3. 変更内容をプレビュー

```bash
# Stage documentation changes
git add README.md docs/
```

## Detection Rules

### Auto-detect Patterns

```python
# CLI options
r"add_argument\s*\(\s*['\"]--(\w+)"
r"Option\s*\(\s*['\"]--(\w+)"
r"typer\.Option\("

# API endpoints
r"@(app|router)\.(get|post|put|delete|patch)"
r"def\s+\w+\s*\(.*request"

# Configuration
r"Config\s*\("
r"settings\.\w+"
r"os\.environ\.get\("

# Environment variables
r"getenv\s*\(\s*['\"](\w+)"
r"environ\[.(\w+).\]"
```

### Changelog Detection

以下の変更はCHANGELOG更新を提案:

- Breaking changes (API signature変更)
- New features
- Bug fixes
- Security patches

## Output Format

### Documentation Impact Report

```
## 📄 ドキュメント更新チェック

### 検出された変更
| 種類 | 影響 | 対象ドキュメント |
|------|------|------------------|
| CLI オプション追加 | `--format` | README.md |
| 環境変数追加 | `API_KEY` | docs/setup.md |
| API変更 | `/users` endpoint | docs/api.md |

### 推奨アクション
1. README.md に新しいオプションの説明を追加
2. docs/setup.md に環境変数の設定方法を追加
3. docs/api.md にエンドポイントの変更を反映

更新を実行しますか？ [y/N]
```

### Success

```
✅ ドキュメントを更新しました

更新ファイル:
  - README.md (+15 lines)
  - docs/setup.md (+8 lines)
  - CHANGELOG.md (+5 lines)

次のステップ:
  git commit -m "docs: update documentation for new features"
```

## Error Handling

| Error | Action |
|-------|--------|
| No docs found | `ℹ️ ドキュメントファイルが見つかりません` |
| Doc not writable | `⚠️ ファイルの書き込み権限がありません` |
| Pattern not found | 手動での確認を提案 |

## Integration

このスキルは以下と連携:

1. **code-quality-gate** - コミット前のドキュメントチェック
2. **issue-reporter** - ドキュメント更新の進捗報告
3. **PR Template** - ドキュメント更新チェックリスト

## Best Practices

1. **コード変更と同時に** - ドキュメント更新を後回しにしない
2. **変更の影響範囲を明確に** - 何が変わったかを具体的に記載
3. **例を含める** - コード例や使用例を追加
4. **CHANGELOGを維持** - 重要な変更は履歴に残す
