#!/bin/bash
# merge-pr.sh - PRをマージ（CI完了待機 → マージ → 後処理）
#
# Usage: ./scripts/merge-pr.sh [-v|--verbose]
#
# Options:
#   -v, --verbose  途中経過を表示（ツール呼び出しを含む）
#
# worktreeディレクトリ内で実行してください。
# 現在のブランチに紐づくPRを自動検出します。
#
# 処理内容:
# 1. CIチェックが完了するまで待機
# 2. すべてのチェックがパスしたらsquash merge
# 3. リモートブランチ削除
# 4. ローカルブランチ・worktree削除

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
echo "🔀 merge-pr を実行中..."
echo "   (CIチェック完了まで待機します)"
echo ""

PROMPT="/merge-pr $PR_NUM"

lib_run_claude "$PROMPT"
