#!/bin/bash
# review-pr.sh - PRをレビューしてコメントを投稿
#
# Usage: ./scripts/review-pr.sh [-v|--verbose]
#
# Options:
#   -v, --verbose  途中経過を表示（ツール呼び出しを含む）
#
# worktreeディレクトリ内で実行してください。
# 現在のブランチに紐づくPRを自動検出します。

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

echo "🔍 現在のブランチからPRを検出中..."

PR_NUM=$(gh pr view --json number --jq '.number' 2>/dev/null || true)

if [[ -z "$PR_NUM" ]]; then
    echo "⚠️ 現在のブランチに紐づくPRが見つかりません"
    echo ""
    echo "先に complete-issue.sh を実行してPRを作成してください。"
    exit 1
fi

echo "📍 PRを検出: #$PR_NUM"
echo ""
echo "🔍 review-pr を実行中..."
echo ""

PROMPT="/pr-review-toolkit:review-pr $PR_NUM PRにコメントしてください"

lib_run_claude "$PROMPT"
