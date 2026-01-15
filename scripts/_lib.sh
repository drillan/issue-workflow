#!/bin/bash
# _lib.sh - スクリプト共通ライブラリ
#
# このファイルは他のスクリプトから source されることを想定しています。
# 直接実行しないでください。
#
# Usage:
#   source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

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
# オプション解析
# ========================================

# verboseフラグ（デフォルト: false）
_LIB_VERBOSE=false

# verboseオプションを解析する
# 出力: evalで評価可能な形式（変数設定 + 残りの引数）
# 使用例:
#   OUTPUT=$(lib_parse_verbose_option "$@")
#   eval "$OUTPUT"
#   # これで _LIB_VERBOSE と REMAINING_ARGS が設定される
#
# 出力形式:
#   _LIB_VERBOSE=true; REMAINING_ARGS='arg1 arg2'
#   または
#   _LIB_VERBOSE=false; REMAINING_ARGS='arg1 arg2'
#
# 注意:
#   - printf %q を使用してシェルエスケープを適用
#   - スペースを含む引数は適切にエスケープされる
#   - シングルクォートやメタ文字も安全に処理される
lib_parse_verbose_option() {
    local args=()
    local verbose_flag=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                verbose_flag=true
                shift
                ;;
            *)
                args+=("$1")
                shift
                ;;
        esac
    done
    # evalで評価可能な形式で出力（printf %qで安全にエスケープ）
    local remaining_str=""
    if [[ ${#args[@]} -gt 0 ]]; then
        remaining_str="${args[*]}"
    fi
    # printf %q を使用してコマンドインジェクションを防止
    printf '_LIB_VERBOSE=%s; REMAINING_ARGS=%q\n' "$verbose_flag" "$remaining_str"
}

# verboseモードかどうかを確認
lib_is_verbose() {
    [[ "$_LIB_VERBOSE" == "true" ]]
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
# 使用例:
#   lib_run_claude "$PROMPT"
#   lib_run_claude "$PROMPT" "no_exec"  # 続きの処理がある場合
lib_run_claude() {
    local prompt="$1"
    local no_exec="${2:-}"

    if lib_is_verbose; then
        claude -p "$prompt" --dangerously-skip-permissions --output-format stream-json --verbose 2>&1 | \
            _lib_format_stream_json || true
    else
        if [[ "$no_exec" == "no_exec" ]]; then
            claude -p "$prompt" --dangerously-skip-permissions
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

    # 複数のworktree命名パターンをサポート:
    # 1. project-name-NNN (ゼロパディング形式: issue-workflow-015)
    # 2. project-name-N (ゼロパディングなし形式: issue-workflow-15)
    # 3. project-name-type-N[-title] (ブランチタイプ形式: issue-workflow-feat-15-add-feature)
    ls "$parent_dir" 2>/dev/null | grep -E "^${project_name}-(${padded_num}$|${issue_num}$|[a-z]+-${issue_num}(-|$))" | head -1 || true
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
