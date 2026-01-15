#!/bin/bash
# merge-pr.sh - PRをマージ（CI完了待機 → マージ → 後処理）
#
# Usage: ./scripts/merge-pr.sh [-v|--verbose] [-h|--help]
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

# オプション解析
lib_parse_options "$@"

# ヘルプ表示
if lib_should_show_help; then
    lib_show_usage "merge-pr.sh" "PRをマージ（CI完了待機 → マージ → 後処理）"
    exit 0
fi

# 不明なオプションのチェック
if ! lib_check_unknown_options 0; then
    exit 1
fi

# PR番号を検出
lib_detect_pr_or_exit

echo ""
echo "🔀 merge-pr を実行中..."
echo "   (CIチェック完了まで待機します)"
echo ""

PROMPT="/merge-pr $PR_NUM"

lib_run_claude "$PROMPT"
