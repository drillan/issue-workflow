#!/bin/bash
# complete-issue.sh - 実装完了後にcommit, push, PR作成を実行
#
# Usage: ./scripts/complete-issue.sh [-v|--verbose]
#
# Options:
#   -v, --verbose  途中経過を表示（ツール呼び出しを含む）
#
# worktreeディレクトリ内で実行してください。

set -euo pipefail

# 共通ライブラリを読み込む
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

# オプション解析（evalで _LIB_VERBOSE と REMAINING_ARGS を設定）
OUTPUT=$(lib_parse_verbose_option "$@")
# 出力形式を検証してからeval
if [[ ! "$OUTPUT" =~ ^_LIB_VERBOSE=(true|false)\;\ REMAINING_ARGS= ]]; then
    echo "ERROR: Option parsing failed" >&2
    exit 1
fi
eval "$OUTPUT"
eval set -- "$REMAINING_ARGS"

# 不明なオプションのチェック
if [[ $# -gt 0 ]]; then
    echo "⚠️ 不明なオプション: $1"
    exit 1
fi

echo "🚀 commit-push-pr を実行中..."
echo ""

PROMPT="以下のスキルを実行してください:

/commit-commands:commit-push-pr

実装された変更をコミットし、リモートにプッシュして、プルリクエストを作成してください。"

lib_run_claude "$PROMPT"
