# Issue Workflow Toolkit

[English](README.md) | 日本語

GitHub Issue駆動開発ワークフローツールキット for Claude Code。

## システム要件

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (パッケージマネージャー)
- [gh CLI](https://cli.github.com/) (GitHub CLI)

## インストール

```bash
uv pip install -e .
```

## コマンド

| コマンド | 説明 |
|---------|------|
| `issue-workflow init` | プロジェクトにIssue Workflowを初期化 |
| `issue-workflow init --language python` | 言語プリセットを指定して初期化 |
| `issue-workflow --version` | バージョンを表示 |
| `issue-workflow --help` | ヘルプを表示 |

## 使い方

```bash
# ワークフロー設定を初期化
issue-workflow init

# 特定の言語プリセットを指定
issue-workflow init --language python
```

## ライセンス

MIT
