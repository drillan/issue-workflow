#!/bin/bash
# _lib.sh - スクリプト共通ライブラリ
#
# このファイルは他のスクリプトから source されることを想定しています。
# 直接実行しないでください。
#
# Usage:
#   source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

# shellcheck disable=SC2148
# ライブラリファイルのため、呼び出し元の設定に依存
# 単体テスト用: 直接実行された場合のみ設定を適用
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    set -euo pipefail
fi

# ========================================
# プロジェクト設定
# ========================================

# プロジェクトルートとプロジェクト名を動的に取得
_LIB_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_LIB_PROJECT_ROOT="$(cd "$_LIB_SCRIPT_DIR/.." && pwd)"
_LIB_PROJECT_NAME="$(basename "$_LIB_PROJECT_ROOT")"

# 呼び出し元から使用するための変数
lib_get_project_root() {
    echo "$_LIB_PROJECT_ROOT"
}

lib_get_project_name() {
    echo "$_LIB_PROJECT_NAME"
}

# ========================================
# 依存コマンドチェック
# ========================================

# 必須コマンドの存在確認
# 引数: コマンド名のリスト
# 戻り値: 0=すべて存在, 1=不足あり
lib_check_dependencies() {
    local missing=()
    for cmd in "$@"; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "⚠️ 必須コマンドが見つかりません: ${missing[*]}" >&2
        echo "" >&2
        echo "以下のコマンドをインストールしてください:" >&2
        for cmd in "${missing[@]}"; do
            case "$cmd" in
                gh) echo "  - gh: https://cli.github.com/" >&2 ;;
                claude) echo "  - claude: https://www.anthropic.com/claude-code" >&2 ;;
                jq) echo "  - jq: https://jqlang.github.io/jq/" >&2 ;;
                *) echo "  - $cmd" >&2 ;;
            esac
        done
        return 1
    fi
    return 0
}

# ========================================
# オプション解析
# ========================================

# グローバル変数（オプション解析結果）
_LIB_VERBOSE=false
_LIB_SHOW_HELP=false
_LIB_REMAINING_ARGS=()

# オプションを解析する（evalを使わない安全な設計）
# グローバル変数を直接設定:
#   - _LIB_VERBOSE: verboseモードかどうか
#   - _LIB_SHOW_HELP: ヘルプ表示が必要か
#   - _LIB_REMAINING_ARGS: 残りの引数配列
#
# 使用例:
#   lib_parse_options "$@"
#   if lib_should_show_help; then
#       lib_show_usage "スクリプト名" "説明" "[引数]"
#       exit 0
#   fi
#   set -- "${_LIB_REMAINING_ARGS[@]}"
lib_parse_options() {
    _LIB_VERBOSE=false
    _LIB_SHOW_HELP=false
    _LIB_REMAINING_ARGS=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                _LIB_VERBOSE=true
                shift
                ;;
            -h|--help)
                _LIB_SHOW_HELP=true
                shift
                ;;
            *)
                _LIB_REMAINING_ARGS+=("$1")
                shift
                ;;
        esac
    done
}

# verboseモードかどうかを確認
lib_is_verbose() {
    [[ "$_LIB_VERBOSE" == "true" ]]
}

# ヘルプ表示が必要かどうかを確認
lib_should_show_help() {
    [[ "$_LIB_SHOW_HELP" == "true" ]]
}

# 使用方法を表示
# 引数:
#   $1 - スクリプト名
#   $2 - 説明
#   $3 - 引数説明（オプション）
#   $4 - 追加オプション説明（オプション）
lib_show_usage() {
    local script_name="$1"
    local description="$2"
    local args="${3:-}"
    local extra_options="${4:-}"

    echo "$description"
    echo ""
    echo "使用方法: $script_name [-v|--verbose] [-h|--help] $args"
    echo ""
    echo "オプション:"
    echo "  -v, --verbose  途中経過を表示（ツール呼び出しを含む）"
    echo "  -h, --help     このヘルプを表示"
    if [[ -n "$extra_options" ]]; then
        echo "$extra_options"
    fi
}

# 不明なオプションをチェック
# 引数: 残りの引数の数（期待値）
# 使用例: lib_check_unknown_options 0  # 引数なしを期待
#         lib_check_unknown_options 1  # 引数1つを期待
lib_check_unknown_options() {
    local expected_args="${1:-0}"
    local actual_args=${#_LIB_REMAINING_ARGS[@]}

    if [[ $actual_args -gt $expected_args ]]; then
        local first_unknown="${_LIB_REMAINING_ARGS[$expected_args]:-}"
        if [[ "$first_unknown" == -* ]]; then
            echo "⚠️ 不明なオプション: $first_unknown" >&2
            return 1
        fi
    fi
    return 0
}

# ========================================
# PR検出
# ========================================

# 現在のブランチに紐づくPR番号を取得
# 戻り値:
#   成功時: PR番号を標準出力に出力し、戻り値0
#   PRなし: 空を出力し、戻り値0
#   エラー: エラーメッセージを標準エラーに出力し、戻り値1
lib_get_pr_number() {
    # ghコマンドの存在確認
    if ! command -v gh &>/dev/null; then
        echo "⚠️ ghコマンドが見つかりません。GitHub CLIをインストールしてください。" >&2
        echo "   https://cli.github.com/" >&2
        return 1
    fi

    # GitHub認証の確認
    if ! gh auth status &>/dev/null; then
        echo "⚠️ GitHub認証が必要です。以下のコマンドを実行してください:" >&2
        echo "   gh auth login" >&2
        return 1
    fi

    # PR番号を取得（エラーを一時ファイルに保存）
    local error_file
    error_file=$(mktemp)
    # シグナルを受けた場合もクリーンアップ
    trap 'rm -f "$error_file" 2>/dev/null' RETURN

    local pr_num
    if pr_num=$(gh pr view --json number --jq '.number' 2>"$error_file"); then
        echo "$pr_num"
        return 0
    else
        local error_msg
        error_msg=$(cat "$error_file")

        # PRが存在しない場合は空を返す（正常）
        if [[ "$error_msg" == *"no pull requests found"* ]] || \
           [[ "$error_msg" == *"Could not resolve"* ]]; then
            echo ""
            return 0
        fi

        # その他のエラー
        echo "⚠️ PR情報の取得に失敗しました: $error_msg" >&2
        return 1
    fi
}

# PR番号を検出して表示（共通パターン）
# 成功時: PR_NUM変数を設定
# 失敗時: エラーメッセージを表示してexit 1
lib_detect_pr_or_exit() {
    echo "🔍 現在のブランチからPRを検出中..."

    local pr_num
    if ! pr_num=$(lib_get_pr_number); then
        exit 1
    fi

    if [[ -z "$pr_num" ]]; then
        echo "⚠️ 現在のブランチに紐づくPRが見つかりません" >&2
        echo "" >&2
        echo "先に complete-issue.sh を実行してPRを作成してください。" >&2
        exit 1
    fi

    echo "📍 PRを検出: #$pr_num"
    # グローバル変数として設定
    PR_NUM="$pr_num"
}

# ========================================
# claude実行関数
# ========================================

# claudeコマンドを実行する
# verboseモード: stream-json出力でツール呼び出しと結果を表示
# 通常モード: execでプロセスを置き換え（スクリプト終了）
#
# 引数:
#   $1 - プロンプト文字列
#   $2 - (オプション) "no_exec" を指定するとexecを使わない
#
# 戻り値:
#   成功時: 0
#   失敗時: claudeコマンドの終了コード
#
# 使用例:
#   lib_run_claude "$PROMPT"
#   lib_run_claude "$PROMPT" "no_exec"  # 続きの処理がある場合
#   if ! lib_run_claude "$PROMPT" "no_exec"; then
#       echo "claudeの実行に失敗しました"
#       exit 1
#   fi
lib_run_claude() {
    local prompt="$1"
    local no_exec="${2:-}"

    # claudeコマンドの存在確認
    if ! command -v claude &>/dev/null; then
        echo "⚠️ claudeコマンドが見つかりません。Claude Codeをインストールしてください。" >&2
        echo "   https://www.anthropic.com/claude-code" >&2
        return 1
    fi

    if lib_is_verbose; then
        # jqの存在確認（verboseモードで必要）
        if ! command -v jq &>/dev/null; then
            echo "⚠️ jqコマンドが見つかりません。verboseモードにはjqが必要です。" >&2
            echo "   https://jqlang.github.io/jq/" >&2
            return 1
        fi

        # パイプラインの終了コードを取得するためPIPESTATUSを使用
        # 注意: PIPESTATUS配列は次のコマンドで上書きされるため、一度に保存する必要がある
        claude -p "$prompt" --dangerously-skip-permissions --output-format stream-json --verbose 2>&1 | \
            _lib_format_stream_json
        local pipestatus=("${PIPESTATUS[@]}")
        local claude_exit=${pipestatus[0]}
        local jq_exit=${pipestatus[1]}
        if [[ $claude_exit -ne 0 ]]; then
            echo "⚠️ claudeの実行に失敗しました（終了コード: $claude_exit）" >&2
            return $claude_exit
        fi
        if [[ $jq_exit -ne 0 ]]; then
            echo "⚠️ 出力のフォーマットに失敗しました（終了コード: $jq_exit）" >&2
            return $jq_exit
        fi
        return 0
    else
        if [[ "$no_exec" == "no_exec" ]]; then
            claude -p "$prompt" --dangerously-skip-permissions
            return $?
        else
            exec claude -p "$prompt" --dangerously-skip-permissions
        fi
    fi
}

# stream-json出力をフォーマットする（内部関数）
_lib_format_stream_json() {
    jq -r --unbuffered '
        if .type == "assistant" and .message.content then
            .message.content[] |
            if .type == "tool_use" then
                "● \(.name)(\(.input | tostring | .[0:60])...)"
            elif .type == "text" then
                empty
            else
                empty
            end
        elif .type == "result" then
            "\n" + .result
        else
            empty
        end
    '
}

# ========================================
# worktree検出
# ========================================

# 指定されたissue番号に対応するworktreeディレクトリを検出する
# 引数:
#   $1 - issue番号
# 戻り値:
#   見つかった場合: ディレクトリ名（パスではない）
#   見つからない場合: 空文字列
#
# 使用例:
#   EXISTING_DIR=$(lib_find_worktree_dir "199")
lib_find_worktree_dir() {
    local issue_num="$1"
    local project_name
    project_name=$(lib_get_project_name)
    local parent_dir
    parent_dir="$(dirname "$(lib_get_project_root)")"

    # 3桁ゼロパディング版のissue番号
    local padded_num
    padded_num=$(printf "%03d" "$issue_num")

    # プロジェクト名の正規表現メタ文字をエスケープ
    local escaped_name
    escaped_name=$(printf '%s\n' "$project_name" | sed 's/[.[\*^$()+?{|]/\\&/g')

    # ディレクトリの読み取り（エラーを適切に処理）
    local ls_output
    local ls_exit_code=0
    ls_output=$(ls "$parent_dir" 2>&1) || ls_exit_code=$?
    if [[ $ls_exit_code -ne 0 ]]; then
        # ディレクトリが存在しない場合は正常（空を返す）
        if [[ "$ls_output" == *"No such file or directory"* ]]; then
            echo ""
            return 0
        fi
        # 権限エラー等の場合は警告を出力して失敗を返す
        echo "⚠️ ディレクトリの読み取りに失敗: $parent_dir ($ls_output)" >&2
        return 1
    fi

    # 複数のworktree命名パターンをサポート:
    # 1. project-name-NNN (ゼロパディング形式: issue-workflow-015)
    # 2. project-name-N (ゼロパディングなし形式: issue-workflow-15)
    # 3. project-name-type-N[-title] (ブランチタイプ形式: issue-workflow-feat-15-add-feature)
    local result
    local grep_exit=0
    result=$(echo "$ls_output" | grep -E "^${escaped_name}-(${padded_num}$|${issue_num}$|[a-z]+-${issue_num}(-|$))" | head -1) || grep_exit=$?
    # grep終了コード: 0=マッチあり, 1=マッチなし, 2=エラー
    if [[ $grep_exit -eq 2 ]]; then
        echo "⚠️ grepでエラーが発生しました" >&2
        return 1
    fi
    echo "$result"
}

# worktreeの完全パスを取得する
# 引数:
#   $1 - issue番号
# 戻り値:
#   見つかった場合: 完全パス
#   見つからない場合: 空文字列
lib_get_worktree_path() {
    local issue_num="$1"
    local dir_name
    dir_name=$(lib_find_worktree_dir "$issue_num")

    if [[ -n "$dir_name" ]]; then
        echo "$(dirname "$(lib_get_project_root)")/$dir_name"
    fi
}
