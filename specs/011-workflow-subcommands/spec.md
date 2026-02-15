# Feature Specification: Workflow Subcommands

**Feature Branch**: `011-workflow-subcommands`
**Created**: 2026-02-15
**Updated**: 2026-02-15
**Status**: Draft
**Input**: User description: "シェルスクリプト (scripts/*.sh) を Python CLI サブコマンドに変換する。サブコマンドは `claude -p` を介してスキルを呼び出し、JSONL 形式で生のログを記録する"
**Parent Spec**: `specs/001-issue-workflow/spec.md` (FR-008〜FR-018)
**Prerequisites**: Issue #58 (commands → skills 移行) 完了済み

## Clarifications

### Session 2026-02-15

- Q: サブコマンドからスキルの呼び出し方法は？ → A: `claude -p "/skill-name <args>" --output-format json` でスキルを呼び出す。同じスキルファイルが対話的 Claude Code セッション (`/skill-name`) とターミナル自動化 (`issue-workflow <subcommand>`) の両方で使用される
- Q: JSONL ログのパース・分析は行うか？ → A: 行わない。生の JSON を記録するのみ。分析は将来のスコープ
- Q: `--verbose` オプションの動作は？ → A: `claude -p --output-format stream-json --verbose` の出力をフォーマットして表示。Python の json モジュールで処理するため jq は不要
- Q: `create-pr` と `push-changes` は同一スキルを呼ぶが区別は？ → A: 両方とも `/commit-push-pr` スキルを呼ぶ。`push-changes` は PR 作成スキップの指示をプロンプトに含める
- Q: `review-pr` の `--review-only` / `--respond-only` オプションは？ → A: CLI サブコマンドのオプションとして実装する
- Q: `full-workflow` (`run`) サブコマンドの段階的実行は？ → A: 4段階を順次実行（Step 1: start-issue → Step 2: create-pr → Step 3: review+respond+push → Step 4: merge-pr）。`--worktree` 指定時はStep 0（worktree準備）を先頭に追加。各ステップの失敗で即時終了
- Q: claudecode-model（pydantic-ai + Claude Agent SDK）を使用するか？ → A: 不要。サブコマンドは `claude -p` の結果を raw JSON としてログに記録するだけであり、構造化出力やカスタムツール実行は不要。`subprocess.run` + `json.loads` で十分
- Q: スクリプトをプロジェクトに配布する方式は？ → A: 配布しない。サブコマンド化により `uv tool install issue-workflow` だけで全機能が利用可能になる
- Q: ログの配置先は？ → A: `.issue-workflow/logs/` に配置。プロジェクト直下の `scripts/` との衝突を避けるためドットディレクトリを使用
- Q: `review-pr`, `merge-pr` はPR番号を引数として受け付けるか？ → A: はい。`review-pr`, `merge-pr`, `respond-comments` はPR番号をオプション引数として受け付ける。省略時は現在のブランチから自動検出。親仕様（001）の `/merge-pr <PR番号>`, `/respond-review [PR番号]` と整合
- Q: worktree上でサブコマンドを実行する前提か？ → A: worktree作成と `merge-pr` はメインリポジトリから実行する。それ以外のサブコマンド（start-issue, create-pr, review-pr, push-changes, respond-comments）はworktree内で実行する。`merge-pr` はworktreeクリーンアップを含むため、worktree上では実行しない
- Q: JSONLログファイルの構造は？ → A: 1実行1ファイル。ファイル名は `<command>-<番号>-<ISO8601タイムスタンプ>.jsonl` 形式。Issue番号またはPR番号が利用可能な場合はファイル名に含める（例: `start-issue-199-2026-02-15T10-30-00.jsonl`）。番号が利用不可の場合は省略する（例: `create-pr-2026-02-15T10-45-00.jsonl`）。GitHubではIssue番号とPR番号は同一番号空間のため重複しない
- Q: `claude -p` のタイムアウト値は？ → A: デフォルト1時間。`--timeout` オプションで設定可能にする
- Q: 非verboseモード時のユーザー向け出力は？ → A: 開始・完了メッセージとステップ名を表示する（例: `[start-issue] Starting...`, `[start-issue] Done.`）

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Issue作業開始サブコマンド (Priority: P1)

開発者として、`issue-workflow start-issue <issue-number>` コマンドを実行することで、Issue作業を開始したい。worktree作成はオプションであり、`--worktree` 指定時のみworktreeを作成する。デフォルトではカレントディレクトリでスキルを実行する。

**Why this priority**: Issue駆動開発の起点であり、最も頻繁に使用されるコマンド。

**Independent Test**: `issue-workflow start-issue 199` を実行し、`claude -p` によるstart-issueスキルの実行が完了することで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** GitHub Issue #199 が存在する状態, **When** `issue-workflow start-issue 199` を実行する, **Then** カレントディレクトリで `claude -p` によりstart-issueスキルが実行される
2. **Given** GitHub Issue #199 が存在する状態, **When** `issue-workflow start-issue 199 --worktree` を実行する, **Then** worktreeが作成され、`.hachimoku/` がコピーされ、worktreeディレクトリで `claude -p` によりstart-issueスキルが実行される
3. **Given** `--worktree` 指定で Issue #199 の worktree が既に存在する状態, **When** `issue-workflow start-issue 199 --worktree` を実行する, **Then** 既存worktreeを検出し、新規作成をスキップしてスキル実行のみ行う
4. **Given** Issue番号として非数値が指定された状態, **When** `issue-workflow start-issue abc` を実行する, **Then** 明確なエラーメッセージが表示され終了コード非0で終了する
5. **Given** サブコマンド実行完了後, **When** ログディレクトリを確認する, **Then** JSONL形式の実行ログが記録されている

---

### User Story 2 - PR作成サブコマンド (Priority: P1)

開発者として、`issue-workflow create-pr` コマンドを実行することで、変更のコミット、プッシュ、PR作成を一連で実行したい。

**Why this priority**: 実装後のPR作成はワークフローの中核ステップ。

**Independent Test**: 変更がある状態で `issue-workflow create-pr` を実行し、commit-push-prスキルが実行されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** 実装済みの変更が存在する状態, **When** `issue-workflow create-pr` を実行する, **Then** `claude -p` により commit-push-pr スキルが実行される
2. **Given** `--verbose` オプションが指定された状態, **When** `issue-workflow create-pr --verbose` を実行する, **Then** stream-json形式でツール呼び出しの途中経過が表示される
3. **Given** サブコマンド実行完了後, **When** ログファイルを確認する, **Then** `claude -p --output-format json` の生の出力がJSONL形式で記録されている

---

### User Story 3 - PRレビューサブコマンド (Priority: P2)

開発者として、`issue-workflow review-pr [pr-number]` コマンドを実行することで、hachimokuでのPRレビューとレビュー結果への対応を実行したい。PR番号は省略可能で、省略時は現在のブランチから自動検出される。

**Why this priority**: コード品質を担保する重要な機能だが、PR作成が機能した後に価値を発揮する。

**Independent Test**: PRが存在する状態で `issue-workflow review-pr` を実行し、hachimokuレビューと respond-review スキルが実行されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** 現在のブランチに紐づくPRが存在する状態, **When** `issue-workflow review-pr` を実行する, **Then** PR番号が自動検出され、`8moku <PR番号>` が実行された後、`claude -p "/respond-review <PR番号>"` が実行される
2. **Given** PR #300 が存在する状態, **When** `issue-workflow review-pr 300` を実行する, **Then** 指定されたPR番号が使用され、自動検出はスキップされる
3. **Given** `--review-only` オプションが指定された状態, **When** `issue-workflow review-pr --review-only` を実行する, **Then** hachimokuレビューのみ実行され、respond-reviewはスキップされる
4. **Given** `--respond-only` オプションが指定された状態, **When** `issue-workflow review-pr --respond-only` を実行する, **Then** hachimokuレビューをスキップし、既存レビュー結果への対応のみ実行される
5. **Given** `--review-only` と `--respond-only` が同時に指定された状態, **When** コマンドを実行する, **Then** 相互排他エラーが表示され終了コード非0で終了する

---

### User Story 4 - 変更プッシュサブコマンド (Priority: P2)

開発者として、`issue-workflow push-changes` コマンドを実行することで、レビュー対応後の変更をコミット・プッシュしたい。PR作成はスキップされる。

**Why this priority**: レビュー対応後のプッシュはレビューサイクルの一部。

**Independent Test**: 変更がある状態で `issue-workflow push-changes` を実行し、commit-push-prスキルがPR作成スキップ指示付きで実行されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** レビュー対応済みの変更が存在する状態, **When** `issue-workflow push-changes` を実行する, **Then** `claude -p` により commit-push-pr スキルが「既存PR時はPR作成スキップ」の指示付きで実行される
2. **Given** サブコマンド実行完了後, **When** ログファイルを確認する, **Then** JSONL形式の実行ログが記録されている

---

### User Story 5 - レビューコメント対応サブコマンド (Priority: P2)

開発者として、`issue-workflow respond-comments [pr-number]` コマンドを実行することで、PRのレビューコメント（GitHub上の人間レビューア等）に対応したい。PR番号は省略可能で、省略時は現在のブランチから自動検出される。

**Why this priority**: 人間レビューアからのフィードバック対応に必要。

**Independent Test**: レビューコメントのあるPRに対して `issue-workflow respond-comments` を実行し、review-pr-commentsスキルが実行されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** 現在のブランチに紐づくPRが存在する状態, **When** `issue-workflow respond-comments` を実行する, **Then** PR番号が自動検出され、`claude -p "/review-pr-comments <PR番号>"` が実行される
2. **Given** PR #300 が存在する状態, **When** `issue-workflow respond-comments 300` を実行する, **Then** 指定されたPR番号が使用され、自動検出はスキップされる
3. **Given** PRが存在しない状態かつPR番号も未指定, **When** `issue-workflow respond-comments` を実行する, **Then** 明確なエラーメッセージ（PRを先に作成するよう促す）が表示される

---

### User Story 6 - PRマージサブコマンド (Priority: P2)

開発者として、`issue-workflow merge-pr [pr-number]` コマンドを実行することで、CI完了待機、マージ、後処理を実行したい。PR番号は省略可能で、省略時は現在のブランチから自動検出される。worktreeクリーンアップを含むため、メインリポジトリから実行する。

**Why this priority**: ワークフローの終了処理であり、開発サイクル完了に必要。

**Independent Test**: PRが存在する状態で `issue-workflow merge-pr` を実行し、merge-prスキルが実行されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** 現在のブランチに紐づくPRが存在する状態, **When** メインリポジトリから `issue-workflow merge-pr` を実行する, **Then** PR番号が自動検出され、`claude -p "/merge-pr <PR番号>"` が実行される
2. **Given** PR #100 が存在する状態, **When** `issue-workflow merge-pr 100` を実行する, **Then** 指定されたPR番号が使用され、自動検出はスキップされる
3. **Given** PRが存在しない状態かつPR番号も未指定, **When** `issue-workflow merge-pr` を実行する, **Then** 明確なエラーメッセージが表示される
4. **Given** worktreeで作業していたPRが存在する状態, **When** メインリポジトリから `issue-workflow merge-pr` を実行する, **Then** マージ後に対応するworktreeとブランチが削除される

---

### User Story 7 - フルワークフロー実行 (Priority: P2)

開発者として、`issue-workflow run <issue-number>` コマンドを実行することで、Issue対応の全ワークフロー（start-issue → create-pr → review+respond → merge-pr）を一括で自動実行したい。`--worktree` 指定時はworktree準備を先頭ステップに追加する。

**Why this priority**: 完全自動化のユースケースであり、個別サブコマンドが機能した後に実現される。

**Independent Test**: `issue-workflow run 199` を実行し、全段階の処理が順次実行されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** GitHub Issue #199 が存在する状態, **When** `issue-workflow run 199` を実行する, **Then** Step 1: start-issue → Step 2: create-pr → Step 3: review+respond+push → Step 4: merge-pr が順次実行される
2. **Given** `--worktree` オプションが指定された状態, **When** `issue-workflow run 199 --worktree` を実行する, **Then** Step 0: worktree準備（メインリポジトリ） → Step 1: start-issue（worktree） → Step 2: create-pr（worktree） → Step 3: review+respond+push（worktree） → Step 4: merge-pr（メインリポジトリ） が順次実行される
3. **Given** Step 2 (create-pr) で失敗した状態, **When** エラーが発生する, **Then** 失敗したステップと原因が表示され、後続ステップは実行されずに終了する
4. **Given** `--verbose` オプションが指定された状態, **When** `issue-workflow run -v 199` を実行する, **Then** 各ステップでstream-json形式の途中経過が表示される
5. **Given** 各ステップの実行完了後, **When** ログディレクトリを確認する, **Then** 各ステップのJSONLログが個別に記録されている

---

### User Story 8 - JSONL生ログ記録 (Priority: P2)

開発者として、各サブコマンドの `claude -p` 実行結果が自動的にJSONL形式で記録されたい。記録された生ログは将来の分析に使用できる。

**Why this priority**: ログ記録は全サブコマンドの横断的関心事であり、デバッグと分析の基盤となる。

**Independent Test**: 任意のサブコマンドを実行し、`.issue-workflow/logs/` にJSONLファイルが作成されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** `issue-workflow create-pr` を実行した状態, **When** ログディレクトリを確認する, **Then** `.issue-workflow/logs/YYYY-MM-DD/` 配下にログファイルが存在する
2. **Given** ログファイルの各行, **When** JSONとしてパースする, **Then** `timestamp`, `command`, `args`, `exit_code`, `result` フィールドが存在し、`result` は `claude -p --output-format json` の生の出力を含む
3. **Given** `claude -p` の実行が失敗した状態, **When** ログを確認する, **Then** `exit_code` が非0であり、可能な限りのエラー情報が `result` に記録されている

---

### Edge Cases

- `claude` コマンドが見つからない場合、インストールURL付きの明確なエラーメッセージを表示する
- `8moku` コマンドが見つからない場合、`uv tool install hachimoku` の案内を表示する
- `gh` コマンドが見つからない場合、または認証されていない場合、既存の `check_gh_availability()` を使用してエラーメッセージを表示する
- `claude -p` のプロセスがタイムアウトした場合（デフォルト3600秒、`--timeout` で変更可能）、タイムアウト情報をログに記録して非0終了コードで終了する
- worktree作成時に `.hachimoku/` が存在しない場合、コピーステップをスキップする（警告を表示、メイン処理は継続）
- `--verbose` モードでの stream-json パースは Python の json モジュールで処理するため jq 依存は不要
- ログディレクトリへの書き込み権限がない場合、ログ記録の失敗を警告として表示し、メインの処理は継続する
- `run` サブコマンドで途中ステップが失敗した場合、それまでのステップのログは保持される
- PR番号の自動検出で複数のPRが見つかった場合、最初の1件を使用する（既存の `get_pr_for_branch` と同一動作）
- `review-pr` サブコマンドで `--review-only` と `--respond-only` が同時に指定された場合は相互排他エラーで終了する

## Requirements *(mandatory)*

### Functional Requirements

#### Claude実行サービス要件

- **FR-001**: システムは `claude -p <prompt> --output-format json` をサブプロセスとして実行する機能を提供しなければならない
- **FR-002**: 自動化実行時は `--dangerously-skip-permissions` フラグを含めなければならない。このフラグはClaude Codeの権限チェックをバイパスするため、`--help` 出力にセキュリティに関する注意事項を記載しなければならない
- **FR-003**: verbose モード時は `--output-format stream-json --verbose` を使用し、途中経過をフォーマットして標準出力に表示しなければならない
- **FR-004**: `claude` コマンドの存在を確認し、見つからない場合はインストールURLを含むエラーを送出しなければならない
- **FR-005**: `claude -p` の終了コードとJSON出力を返さなければならない
- **FR-005a**: 非verboseモード（デフォルト）では、サブコマンドの開始・完了メッセージとステップ名を標準出力に表示しなければならない（例: `[start-issue] Starting...`, `[start-issue] Done.`）

#### CLIサブコマンド要件

- **FR-006**: `issue-workflow start-issue <issue-number>` サブコマンドを追加し、start-issueスキルを実行しなければならない。`--worktree` オプション指定時のみworktreeを作成する
- **FR-007**: `issue-workflow create-pr` サブコマンドを追加し、commit-push-prスキルを実行しなければならない
- **FR-008**: `issue-workflow review-pr [pr-number]` サブコマンドを追加し、hachimokuレビュー + respond-reviewスキルを実行しなければならない。PR番号は省略可能で、省略時は自動検出する。`--review-only` と `--respond-only` オプションをサポートする
- **FR-009**: `issue-workflow push-changes` サブコマンドを追加し、commit-push-prスキルをPR作成スキップ指示付きで実行しなければならない
- **FR-010**: `issue-workflow respond-comments [pr-number]` サブコマンドを追加し、review-pr-commentsスキルを実行しなければならない。PR番号は省略可能で、省略時は自動検出する
- **FR-011**: `issue-workflow merge-pr [pr-number]` サブコマンドを追加し、merge-prスキルを実行しなければならない。PR番号は省略可能で、省略時は自動検出する
- **FR-012**: `issue-workflow run <issue-number>` サブコマンドを追加し、全ステップ（Step 1: start-issue → Step 2: create-pr → Step 3: review+respond+push → Step 4: merge-pr）を順次実行しなければならない。Step 3 は hachimoku レビュー、レビュー対応、変更プッシュを含む。`--worktree` オプション指定時は Step 0（worktree準備）を先頭に追加する
- **FR-013**: すべてのサブコマンドは `--verbose` / `-v` オプションで途中経過表示をサポートしなければならない
- **FR-013a**: すべてのサブコマンドは `--timeout` オプションで `claude -p` のタイムアウト値（秒）を指定できなければならない。デフォルトは3600秒（1時間）とする
- **FR-014**: すべてのサブコマンドは `--help` / `-h` オプションで使用方法を表示しなければならない

#### PR番号検出要件

- **FR-015**: `review-pr`, `respond-comments`, `merge-pr` サブコマンドはPR番号をオプション引数として受け付けなければならない。省略時は現在のブランチからPR番号を自動検出する。明示的に指定された場合は自動検出をスキップする
- **FR-015a**: `push-changes` サブコマンドは現在のブランチからPR番号を自動検出しなければならない
- **FR-016**: PR番号が指定されず、かつ自動検出でも見つからない場合は、明確なエラーメッセージ（PR作成を促す案内）を表示しなければならない

#### Worktree操作要件

- **FR-017**: `start-issue` サブコマンドは `--worktree` オプション指定時に既存worktreeの検出と新規作成をサポートしなければならない。worktreeの作成はメインリポジトリから実行する
- **FR-018**: `start-issue` サブコマンドは `--worktree` でworktree作成後に `.hachimoku/` をコピーしなければならない
- **FR-019**: `--worktree` 指定時のスキル実行（`start-issue`, `create-pr`, `review-pr`, `push-changes`, `respond-comments`）は、worktreeディレクトリを作業ディレクトリとして設定しなければならない
- **FR-019a**: `merge-pr` はworktreeクリーンアップを含むため、常にメインリポジトリを作業ディレクトリとして実行しなければならない
- **FR-019b**: `run --worktree` サブコマンドは、worktree準備と`merge-pr`をメインリポジトリから、それ以外のステップをworktreeディレクトリから実行しなければならない

#### JSONL ログ要件

- **FR-020**: 各サブコマンドの `claude -p` 実行結果を JSONL 形式でログに記録しなければならない
- **FR-021**: JSONL ログの各行は以下のフィールドを含まなければならない: `timestamp` (ISO 8601), `command` (サブコマンド名), `args` (引数辞書), `exit_code` (整数), `result` (claude -p の生JSON出力)
- **FR-022**: ログファイルは `.issue-workflow/logs/YYYY-MM-DD/<command>-<番号>-<ISO8601タイムスタンプ>.jsonl` に配置しなければならない。Issue番号またはPR番号が利用可能な場合はファイル名に含める（例: `start-issue-199-2026-02-15T10-30-00.jsonl`）。番号が利用不可の場合は省略する（例: `create-pr-2026-02-15T10-45-00.jsonl`）。1実行につき1ファイルを生成する
- **FR-023**: `result` フィールドは `claude -p --output-format json` の出力をパースせずそのまま記録しなければならない

#### 依存コマンドチェック要件

- **FR-024**: 各サブコマンドは実行前に必要な外部コマンド（`claude`, `gh`, `8moku` 等）の存在を確認しなければならない
- **FR-025**: 外部コマンドが見つからない場合、インストール方法を含む明確なエラーメッセージを表示して非0終了コードで終了しなければならない

### Key Entities

- **Skill**: `.claude/skills/*/SKILL.md` に配置されるClaude Codeスキル定義。対話的セッション (`/skill-name`) と自動化 (`claude -p "/skill-name"`) の両方で使用可能。全10スキルが `issue-workflow init` / `update` で配布される。
- **ClaudeRunner**: `claude -p` コマンドをサブプロセスとして実行するサービス。プロンプト、出力形式、verbose制御、作業ディレクトリ指定を管理する。
- **ExecutionLog**: JSONL形式の実行ログエントリ。タイムスタンプ、コマンド名、引数、終了コード、生のJSON結果で構成される。
- **Subcommand**: CLIサブコマンド。オーケストレーション（worktree作成、PR検出、オプション解析、ログ記録）を担当し、Claudeへの指示はスキルに委譲する。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 全7サブコマンド（start-issue, create-pr, review-pr, push-changes, respond-comments, merge-pr, run）が `--help` で使用方法を表示できる
- **SC-002**: 各サブコマンドの実行でJSONLログファイルが生成され、必須5フィールド（timestamp, command, args, exit_code, result）を含む
- **SC-003**: `scripts/` の既存シェルスクリプトと同等の機能がCLIサブコマンドで提供される
- **SC-004**: `claude` コマンドが見つからない場合に100%の確率でインストール案内付きエラーメッセージが表示される
- **SC-005**: verbose モードで stream-json 出力がリアルタイムにフォーマットされて表示される
- **SC-006**: `run` サブコマンドで全段階が順次実行され、各段階の成否がログに記録される

## Assumptions

- Claude Code CLI (`claude`) がインストールされ、`claude -p` がターミナルから実行可能であること
- GitHub CLI (`gh`) がインストールされ、認証済みであること
- hachimoku (`8moku`) がインストール済みであること（`issue-workflow init` で自動インストール）
- `uv` がインストールされていること
- プロジェクトが Git リポジトリとして初期化されていること
- `issue-workflow init` が事前に実行され、`.claude/skills/` に全スキルが配置されていること
- Python 3.13 以上が使用されていること
- `claude -p --output-format json` がJSON形式の結果を標準出力に出力すること
- commands → skills 移行（Issue #58）が完了済みであること

## Distribution

- **CLIインストール**: `uv tool install issue-workflow`（サブコマンドを含む）
- **スキル配布**: `issue-workflow init` / `update` で `.claude/skills/` にコピー
- **スクリプト配布**: 不要（サブコマンド化により `uv tool install` で完結）
- **ログ出力先**: `.issue-workflow/logs/`（プロジェクトローカル）

## Out of Scope

- JSONL ログの分析・可視化機能（将来のスコープ）
- `scripts/` ディレクトリのシェルスクリプトの自動削除（手動で削除する）
- CI/CD パイプラインとの統合（別途検討）
- サブコマンドの並列実行（`run` は順次実行のみ）
- `claude -p` のリトライ・再試行機構
- ログファイルのローテーション・クリーンアップ
- ログファイルの暗号化・アクセス制御
- サブコマンド間の状態共有（各サブコマンドは独立して実行される）

## Architecture Notes

### サブコマンドとスキルの関係

```
ターミナル自動化:
  issue-workflow start-issue 199
    → subprocess: claude -p "/start-issue 199" --output-format json
    → Python: raw JSON をエンベロープに包んでJSONLに記録

  issue-workflow start-issue 199 --worktree
    → Python: worktree作成、.hachimoku/コピー
    → subprocess: claude -p "/start-issue 199" --output-format json (cwd=worktree)
    → Python: raw JSON をエンベロープに包んでJSONLに記録

対話的利用:
  Claude Code セッション内で /start-issue 199
    → Claude が .claude/skills/start-issue/SKILL.md を読んで実行

同じスキルファイルが両方のエントリーポイントから使われる
```

### サブコマンドの役割分担

| 層 | 責務 | 実装 |
|---|---|---|
| サブコマンド | オーケストレーション（前処理、ログ、エラーハンドリング） | Python (Typer) |
| スキル | Claudeへの指示（何をすべきか） | Markdown (SKILL.md) |
| ClaudeRunner | `claude -p` の実行と結果取得 | Python (subprocess) |
| ExecutionLogger | JSONL ログの書き込み | Python (json) |

### サブコマンド → スキル マッピング

| サブコマンド | スキル | 前処理 |
|---|---|---|
| `start-issue <n>` | `/start-issue <n>` | `--worktree` 時: worktree作成（メインリポジトリ）、.hachimoku/コピー、スキル実行（worktree） |
| `create-pr` | `/commit-push-pr` | なし（worktree内で実行） |
| `review-pr [PR]` | `/respond-review <PR>` | PR番号検出（引数優先、省略時は自動検出）、8moku実行（worktree内で実行） |
| `push-changes` | `/commit-push-pr` | PR存在確認（スキップ指示付き）（worktree内で実行） |
| `respond-comments [PR]` | `/review-pr-comments <PR>` | PR番号検出（引数優先、省略時は自動検出）（worktree内で実行） |
| `merge-pr [PR]` | `/merge-pr <PR>` | PR番号検出（引数優先、省略時は自動検出）（メインリポジトリで実行） |
| `run <n>` | 上記すべてを順次 | Step 0(任意): worktree準備 → Step 1: start-issue → Step 2: create-pr → Step 3: review+respond+push → Step 4: merge-pr |
