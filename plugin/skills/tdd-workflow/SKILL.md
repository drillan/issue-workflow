# TDD Workflow Skill

TDDワークフローを強制し、Red-Green-Refactorサイクルを確実に実行する。

## Trigger Conditions

- 新機能実装開始時
- バグ修正開始時
- リファクタリング開始時

## Phases

### Phase 1: Red（テスト作成・失敗確認）

1. **テストファイルの作成/特定**
   - 命名規則: `test_<機能名>.py`
   - 配置: `tests/`ディレクトリ

2. **テストケースの設計**
   - 期待動作を明確に定義
   - エッジケースを考慮
   - テスト名規則: `test_<機能>_<状況>_<期待結果>`

3. **テスト実行と失敗確認**
   ```bash
   uv run pytest tests/test_<機能名>.py -v
   ```

4. **ユーザー承認**（必須）
   - テストケースを提示
   - 承認を得てから次フェーズへ

### Phase 2: Green（最小限の実装）

1. **実装ファイルの作成**
   - テストを通過させることのみに集中
   - 過剰設計を避ける

2. **テスト実行と成功確認**
   ```bash
   uv run pytest tests/test_<機能名>.py -v
   ```

3. **品質チェック**
   ```bash
   uv run ruff check --fix . && uv run ruff format . && uv run mypy .
   ```

### Phase 3: Refactor（リファクタリング）

1. **コードの改善**
   - 重複の除去
   - 可読性の向上

2. **全テストの再実行**
   ```bash
   uv run pytest
   ```

## File Mapping

| 実装ファイル | テストファイル |
|-------------|--------------|
| `src/auth.py` | `tests/test_auth.py` |
| `src/article.py` | `tests/test_article.py` |
| `src/services/user.py` | `tests/test_user.py` |

## Test Naming Convention

`test_<機能>_<状況>_<期待結果>`

Examples:
- `test_login_with_valid_credentials_returns_session`
- `test_login_with_invalid_password_raises_error`
- `test_create_user_with_duplicate_email_fails`

## Enforcement Rules

1. **テストファイルが存在しない場合**
   - 実装を開始する前にテストファイルの作成を要求
   - 実装ファイルの編集をブロック

2. **テストが失敗していない場合（Red）**
   - テストが意図通り失敗することを確認
   - 失敗しないテストは意味がないことを説明

3. **テストが成功した後（Green）**
   - リファクタリングフェーズへの移行を提案
   - 追加のテストケースが必要か確認

## Quality Gates

- すべてのテストが成功すること
- カバレッジが基準を満たすこと
- 静的解析でエラーがないこと

## Instructions for Claude

When implementing a feature:

1. **Always ask**: "Do you want me to follow TDD workflow?"
2. **If yes**:
   - First, write the test file
   - Show the test to the user
   - Run the test and confirm it fails
   - Get user approval before implementation
   - Implement the minimal code to pass
   - Run tests again
   - Refactor if needed
3. **Track progress**:
   - Mark each phase (Red, Green, Refactor)
   - Report test results at each phase
