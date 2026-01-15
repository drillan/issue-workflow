# Plugin Skills Contract

Claude Code Plugin（Skills形式）として提供されるバックグラウンドスキル。

---

## tdd-workflow

TDDワークフローを強制し、Red-Green-Refactorサイクルを確実に実行する。

### Trigger Conditions

- 新機能実装開始時
- バグ修正開始時
- リファクタリング開始時

### Phases

#### Phase 1: Red（テスト作成・失敗確認）

1. テストファイルの作成/特定
   - 命名規則: `test_<機能名>.py`
   - 配置: `tests/`ディレクトリ

2. テストケースの設計
   - 期待動作を明確に定義
   - エッジケースを考慮

3. テスト実行と失敗確認
   ```bash
   uv run pytest tests/test_<機能名>.py -v
   ```

4. **ユーザー承認**（必須）
   - テストケースを提示
   - 承認を得てから次フェーズへ

#### Phase 2: Green（最小限の実装）

1. 実装ファイルの作成
   - テストを通過させることのみに集中
   - 過剰設計を避ける

2. テスト実行と成功確認
   ```bash
   uv run pytest tests/test_<機能名>.py -v
   ```

3. 品質チェック
   ```bash
   uv run ruff check --fix . && uv run ruff format . && uv run mypy .
   ```

#### Phase 3: Refactor（リファクタリング）

1. コードの改善
   - 重複の除去
   - 可読性の向上

2. 全テストの再実行
   ```bash
   uv run pytest
   ```

### File Mapping

| 実装ファイル | テストファイル |
|-------------|--------------|
| `src/auth.py` | `tests/test_auth.py` |
| `src/article.py` | `tests/test_article.py` |

### Test Naming Convention

`test_<機能>_<状況>_<期待結果>`

例: `test_login_with_valid_credentials_returns_session`

---

## code-quality-gate

コード品質基準の完全遵守を保証する。

### Trigger Conditions

- コミット前
- PR作成前
- 品質問題検出時
- 明示的な依頼時

### Quality Checks

1. **Ruff Linter**
   ```bash
   uv run ruff check .
   uv run ruff check --fix .  # 自動修正
   ```

2. **Ruff Formatter**
   ```bash
   uv run ruff format --check .
   uv run ruff format .  # 自動フォーマット
   ```

3. **Mypy Type Checker**
   ```bash
   uv run mypy .
   ```

### Configuration

品質コマンドは`.claude/workflow-config.json`から読み込み:

```json
{
  "quality": {
    "lint": "uv run ruff check --fix .",
    "format": "uv run ruff format .",
    "typecheck": "uv run mypy .",
    "test": "uv run pytest",
    "all": "uv run ruff check --fix . && uv run ruff format . && uv run mypy ."
  }
}
```

### Gate Criteria

**PASS条件**: すべてのチェックがエラーなしで完了

```
✓ ruff check: 0 errors
✓ ruff format: No changes needed
✓ mypy: Success: no issues found
```

**FAIL条件**: いずれかのチェックでエラー発生 → コミット/PR作成をブロック

### Report Format

```
## Code Quality Gate Report

### チェック結果
| Tool | Status | Details |
|------|--------|---------|
| ruff check | ✓ PASS | 0 errors |
| ruff format | ✓ PASS | No changes |
| mypy | ✓ PASS | No issues |

### 総合判定: PASS
```

---

## issue-reporter

作業進捗をGitHub Issueに自動報告する。

### Trigger Conditions

- 計画立案時
- 知見獲得時
- 問題発覚時
- その他記録すべき重要情報があるとき

### Branch Parsing

ブランチ名からIssue番号を抽出:

```bash
branch=$(git branch --show-current)
issue_number=$(echo "$branch" | sed -n 's#^\(feat\|fix\|chore\|docs\|refactor\|test\|feature\|bugfix\)/\([0-9]\+\)-.*#\2#p')
```

サポートパターン:
- `feat/123-xxx` → 123
- `fix/456-xxx` → 456
- `feature/789-xxx` → 789 (レガシー)

### Comment Templates

#### 計画立案時（Plan）

```markdown
## 📋 実装計画

**作業内容**: [作業の概要]

### 計画
1. [ステップ1]
2. [ステップ2]

### 予想される課題
- [課題1]

---
*Posted by Claude Code at YYYY-MM-DD HH:MM*
```

#### 知見獲得時（Insight）

```markdown
## 💡 新たな知見

**発見内容**: [発見の概要]

### 詳細
[発見の詳細説明]

### プロジェクトへの影響
- [影響1]

### 推奨アクション
- [ ] [アクション1]

---
*Posted by Claude Code at YYYY-MM-DD HH:MM*
```

#### 問題発覚時（Problem）

```markdown
## ⚠️ 問題発覚

**問題**: [問題の概要]

### 詳細
[問題の詳細説明]

### 再現手順
1. [手順1]

### 暫定対応
- [対応1]

### 根本対応（提案）
- [ ] [対応提案1]

---
*Posted by Claude Code at YYYY-MM-DD HH:MM*
```

### Duplicate Prevention

以下の場合はコメントを投稿しない:
- 同一セッション内で既に同様の内容を報告済み
- 軽微な進捗（単なるファイル読み取りや軽微な調査）
- まだ結論が出ていない調査途中

---

## doc-updater

コード変更に応じてドキュメントを自動更新する。

### Trigger Conditions

- API/インターフェース変更
- 新機能追加
- アーキテクチャ変更
- 明示的な依頼
- ドキュメントの不整合検出

### Process

1. **変更内容の分析**
   - 変更されたファイル
   - 新規追加されたクラス/関数
   - 変更されたAPIシグネチャ

2. **影響を受けるドキュメントの特定**
   - `docs/index.md`
   - `docs/architecture.md`
   - 機能固有のドキュメント

3. **ドキュメント更新案の作成**
   - プロジェクトのマークアップ構文を使用
   - 内部表記を避ける
   - 保証表現を避ける

4. **ユーザーへの確認**
   - 変更の妥当性
   - 追加すべき情報の有無

5. **更新の実行**

6. **ビルド検証**
