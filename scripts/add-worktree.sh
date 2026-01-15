#!/bin/bash
# add-worktree.sh - issue番号を指定してgit worktreeを追加する
#
# Usage: ./scripts/add-worktree.sh [-h|--help] [--debug] <issue番号>
# Example: ./scripts/add-worktree.sh 141

set -euo pipefail

# 共通ライブラリを読み込む
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

PROJECT_ROOT=$(lib_get_project_root)
COMMAND_FILE="$PROJECT_ROOT/.claude/commands/add-worktree.md"

# オプション解析（--debugオプションを追加）
_SHOW_HELP=false
_DEBUG_MODE=false
_REMAINING=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            _SHOW_HELP=true
            shift
            ;;
        --debug)
            _DEBUG_MODE=true
            shift
            ;;
        *)
            _REMAINING+=("$1")
            shift
            ;;
    esac
done

set -- "${_REMAINING[@]}"

# ヘルプ表示
if [[ "$_SHOW_HELP" == "true" ]]; then
    echo "issue番号を指定してgit worktreeを追加する"
    echo ""
    echo "使用方法: add-worktree.sh [-h|--help] [--debug] <issue番号>"
    echo ""
    echo "オプション:"
    echo "  -h, --help  このヘルプを表示"
    echo "  --debug     プロンプト内容を表示して終了（デバッグ用）"
    exit 0
fi

# 引数チェック
if [[ $# -lt 1 ]]; then
    echo "⚠️ issue番号が必要です" >&2
    echo "" >&2
    echo "使用方法: $0 [-h|--help] [--debug] <issue番号>" >&2
    echo "例: $0 141" >&2
    exit 1
fi

ISSUE_NUM="$1"

# 数値チェック
if ! [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]]; then
    echo "⚠️ issue番号は数値で指定してください: $ISSUE_NUM" >&2
    exit 1
fi

# コマンドファイルの存在チェック
if [[ ! -f "$COMMAND_FILE" ]]; then
    echo "⚠️ コマンドファイルが見つかりません: $COMMAND_FILE" >&2
    exit 1
fi

# コマンドの内容を読み込み、$ARGUMENTSを置換
CONTENT="$(cat "$COMMAND_FILE")"
CONTENT_REPLACED="${CONTENT//\$ARGUMENTS/$ISSUE_NUM}"

# 実行指示を先頭に追加
PROMPT="以下の指示に従って、issue #${ISSUE_NUM} のワークツリーを作成してください。引数は既に ${ISSUE_NUM} として渡されています。Step 1の検証は成功として扱い、Step 2から実行してください。

${CONTENT_REPLACED}"

# デバッグ: --debug オプションでプロンプト内容を表示
if [[ "$_DEBUG_MODE" == "true" ]]; then
    echo "=== Generated Prompt ==="
    echo "$PROMPT"
    echo "========================"
    exit 0
fi

# claude -p で実行
# --allowedTools: Bash(git, gh), Read, Glob を許可
cd "$PROJECT_ROOT"
exec claude -p "$PROMPT" --allowedTools "Bash(git:*),Bash(gh:*),Read,Glob"
