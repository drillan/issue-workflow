# CLAUDE.md

## 非交渉的ルール（例外なし）

### TDD必須
- 実装前にテスト作成 → ユーザー承認 → Red確認
- 1機能 = 1テストファイル（例: `test_auth.py` ← `auth.py`）

### 仕様優先
- 実装前に仕様確認必須
- 曖昧な仕様は実装停止 → 明確化要求

### 品質チェック
- コミット前: `ruff check --fix . && ruff format . && mypy .`
- 全エラー解消まで次工程禁止

### 型安全
- 全関数・メソッドに型注釈必須
- `Any`型禁止、`| None`推奨

## CLI/Plugin設計

- `--help`: 明確な使用方法
- `--non-interactive`: 非対話モード対応
- エラー: 解決方法を含める
- 終了コード: 0=成功, 非0=失敗

## 禁止事項

- マジックナンバー・ハードコード値
- 暗黙的フォールバック・デフォルト値
- コード重複（3回以上は抽出）
- V2/V3クラス作成（既存を修正）
- 不要なラッパー・過剰抽象化

## 命名規則

- 詳細: `.claude/git-conventions.md`
- specs/: `<3桁issue番号>-<name>`（例: `001-issue-workflow`）
- ブランチ: ゼロパディングなし

## Python

- システムの`python3`を使用しないこと
- `uv run` または `.venv/bin/python` を使用

## Active Technologies
- Python 3.13+ + Typer, Pydantic, Rich, readchar, uv (001-issue-workflow)
- ファイルベース（`.claude/workflow-config.json`, `.claude/git-conventions.md`） (001-issue-workflow)
- Python 3.13+ + Typer 0.15+, Pydantic 2.10+, Rich 13.9+, shutil, pathlib (010-update-command)
- ファイルシステム（`.claude/commands/`, `.claude/skills/`） (010-update-command)

## Recent Changes
- 001-issue-workflow: Updated to Python 3.13+ with latest dependencies (Typer 0.15+, Pydantic 2.10+, Rich 13.9+)
