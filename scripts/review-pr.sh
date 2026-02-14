#!/bin/bash
# review-pr.sh - hachimokuでPRをレビューし、結果に対応
#
# Usage: ./scripts/review-pr.sh [-v|--verbose] [-h|--help]
#
# worktreeディレクトリ内で実行してください。
# 現在のブランチに紐づくPRを自動検出します。

set -euo pipefail

# 共通ライブラリを読み込む
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

# オプション解析
lib_parse_options "$@"

# ヘルプ表示
if lib_should_show_help; then
    lib_show_usage "review-pr.sh" "PRをレビューしてコメントを投稿"
    exit 0
fi

# 不明なオプションのチェック
if ! lib_check_unknown_options 0; then
    exit 1
fi

# PR番号を検出
lib_detect_pr_or_exit

echo ""
echo "🔍 hachimokuレビューを実行中..."
echo ""

if ! 8moku review pr "$PR_NUM"; then
    echo "⚠️ hachimokuレビューの実行に失敗しました" >&2
    exit 1
fi

echo ""
echo "📝 hachimokuレビュー結果に対応中..."
echo ""

PROMPT="/respond-review $PR_NUM"

if ! lib_run_claude "$PROMPT"; then
    exit 1
fi
