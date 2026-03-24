# CLAUDE.md

## CLI/Plugin設計

- `--help`: 明確な使用方法
- `--non-interactive`: 非対話モード対応
- エラー: 解決方法を含める
- 終了コード: 0=成功, 非0=失敗

## 命名規則

- 詳細: `.claude/git-conventions.md`
- specs/: `<3桁issue番号>-<name>`（例: `001-issue-workflow`）
- ブランチ: ゼロパディングなし

## Active Technologies
- Python 3.13+ + Typer 0.15+, Pydantic 2.10+, Rich 13.9+, readchar 4.2+, shutil, pathlib, subprocess (001-issue-workflow)
- ファイルベース（`.claude/workflow-config.json`, `.claude/git-conventions.md`, `.hachimoku/reviews/*.jsonl`） (001-issue-workflow)
- Python 3.13+ + Typer 0.15+, Pydantic 2.10+, Rich 13.9+, shutil, pathlib (010-update-command)
- ファイルシステム（`.claude/skills/`, `.claude/agents/`） (010-update-command)
- Python 3.13+ + Typer 0.15+, Pydantic 2.10+, Rich 13.9+ (既存依存) (011-workflow-subcommands)
- ファイルベース (`.issue-workflow/logs/YYYY-MM-DD/*.jsonl`) (011-workflow-subcommands)

## Recent Changes
- 001-issue-workflow: Updated to Python 3.13+ with latest dependencies (Typer 0.15+, Pydantic 2.10+, Rich 13.9+)
