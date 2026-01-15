#!/bin/bash
# add-worktree.sh - issue番号を指定してgit worktreeを追加する
#
# Usage: ./scripts/add-worktree.sh <issue番号>
# Example: ./scripts/add-worktree.sh 141

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMMAND_FILE="$PROJECT_ROOT/.claude/commands/add-worktree.md"

# 引数チェック
if [[ $# -lt 1 ]]; then
    echo "⚠️ issue番号が必要です"
    echo ""
    echo "使用方法: $0 <issue番号>"
    echo "例: $0 141"
    exit 1
fi

ISSUE_NUM="$1"

# 数値チェック
if ! [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]]; then
    echo "⚠️ issue番号は数値で指定してください: $ISSUE_NUM"
    exit 1
fi

# コマンドファイルの存在チェック
if [[ ! -f "$COMMAND_FILE" ]]; then
    echo "⚠️ コマンドファイルが見つかりません: $COMMAND_FILE"
    exit 1
fi

# コマンドの内容を読み込み、$ARGUMENTSを置換
CONTENT="$(cat "$COMMAND_FILE")"
CONTENT_REPLACED="${CONTENT//\$ARGUMENTS/$ISSUE_NUM}"

# 実行指示を先頭に追加
PROMPT="以下の指示に従って、issue #${ISSUE_NUM} のワークツリーを作成してください。引数は既に ${ISSUE_NUM} として渡されています。Step 1の検証は成功として扱い、Step 2から実行してください。

${CONTENT_REPLACED}"

# デバッグ: --debug オプションでプロンプト内容を表示
if [[ "${2:-}" == "--debug" ]]; then
    echo "=== Generated Prompt ==="
    echo "$PROMPT"
    echo "========================"
    exit 0
fi

# claude -p で実行
# --allowedTools: Bash(git, gh), Read, Glob を許可
cd "$PROJECT_ROOT"
exec claude -p "$PROMPT" --allowedTools "Bash(git:*),Bash(gh:*),Read,Glob"
