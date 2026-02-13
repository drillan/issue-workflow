# Feature Specification: Issue Workflow Toolkit

**Feature Branch**: `001-issue-workflow`
**Created**: 2026-01-15
**Updated**: 2026-02-13
**Status**: Draft
**Input**: User description: "Issue Workflow - GitHub Issue駆動の開発ワークフローをClaude Codeで実現するためのツールキット"

## Clarifications

### Session 2026-01-15

- Q: GitHubリポジトリ所有者は誰か？ → A: `drillan/issue-workflow`
- Q: 対象プロジェクトの言語制限は？ → A: 言語非依存（5つのプリセット + カスタム対応）
- Q: Worktreeクリーンアップのトリガーは？ → A: PRマージ時のみ自動クリーンアップ（手動削除は`git worktree remove`を使用）
- Q: 言語プリセットの構成は？ → A: Node.js→TypeScriptに名称変更（Python, TypeScript, Go, Rust, Generic）

### Session 2026-02-13 (Issue #32: 外部プラグイン依存排除)

- Q: 外部プラグイン（commit-commands, pr-review-toolkit）はどう置き換えるか？ → A: git-workflow-haikuのcommands/とagents/をissue-workflowにバンドル。hachimokuは`uv tool install`で外部ツールとして導入
- Q: レビュー方式はどう変わるか？ → A: pr-review-toolkitの代わりにhachimoku CLI（`8moku`）を使用。JSONL出力（`.hachimoku/reviews/pr-{number}.jsonl`）を読み取る新コマンドを新設
- Q: ci_review設定はどうなるか？ → A: 削除。レビューはhachimokuに統一
- Q: review-pr-commentsコマンドはどうなるか？ → A: hachimoku JSONLベースの新コマンドを`/review-pr-comments`とは別に新設
- Q: agents/ディレクトリの扱いは？ → A: `issue-workflow init`/`update`で`.claude/agents/`にコピー。commands/と同様のバンドル機構
- Q: hachimoku JSONLレビュー対応の新コマンド名は？ → A: `/respond-review`（`/review-pr-comments`と区別）
- Q: hachimokuが既にインストール済みの場合の動作は？ → A: スキップ（インストール済みなら何もしない）
- Q: hachimokuの認証・設定要件は？ → A: hachimoku側の責務でありスコープ外。issue-workflowはインストールのみ担当
- Q: hachimokuのバージョン指定方針は？ → A: バージョン指定なし（常に最新版をインストール）
- Q: ワークフロースクリプトでのhachimoku呼び出し方法は？ → A: スクリプトから`8moku`を直接呼び出し（Claude Code経由ではない）
- Q: `8moku init`は`issue-workflow init`で吸収すべきか？ → A: サブプロセス委譲（`8moku init`を呼び出す）。ロジック再実装はバージョン不整合リスクがあるため不可
- Q: agents/commands内の`main`ハードコードはどうするか？ → A: `git symbolic-ref refs/remotes/origin/HEAD`で default branch を自動検出する。`main`、`master`、`develop`（Gitflow）等を問わず動作する
- Q: default branch の設定オプションは必要か？ → A: 不要。git から自動検出する方式で統一する

## User Scenarios & Testing *(mandatory)*

### User Story 1 - プロジェクト初期化 (Priority: P1)

開発者として、新規または既存プロジェクトにIssue Workflowを導入したい。CLIコマンドを実行することで、必要な設定ファイル、コマンド、エージェント、および外部ツールが自動的にセットアップされ、Issue駆動開発をすぐに始められるようになる。

**Why this priority**: これはツールキット導入の入り口であり、すべての他の機能の前提条件となる。初期化なしには他の機能は使用できない。

**Independent Test**: `issue-workflow init`コマンドを実行し、`.claude/`ディレクトリ内に設定ファイル、commands/、agents/が生成され、hachimokuがインストールされることを確認することで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** プロジェクトディレクトリ内でCLIがインストールされている状態, **When** `issue-workflow init -l python`を実行する, **Then** Python用の設定ファイル（`.claude/workflow-config.json`, `.claude/git-conventions.md`）が生成され、`.claude/commands/`と`.claude/agents/`にバンドルファイルがコピーされる
2. **Given** 言語オプションを指定せずに初期化を開始する状態, **When** `issue-workflow init`を実行する, **Then** 対話形式で言語プリセットを選択でき、選択後に適切な設定が生成される
3. **Given** 既に設定ファイルが存在するプロジェクト, **When** `issue-workflow init`を実行する, **Then** 既存設定を上書きするか確認され、ユーザーの選択に応じて処理される
4. **Given** hachimokuが未インストールの状態, **When** `issue-workflow init`を実行する, **Then** `uv tool install hachimoku`によりhachimokuが自動インストールされ、`8moku init`により`.hachimoku/`ディレクトリが初期化される

---

### User Story 2 - Issue作業の開始 (Priority: P1)

開発者として、GitHub Issueを指定するだけで作業を開始したい。Issueの内容が読み込まれ、適切なブランチが自動作成され、実装計画が立案されることで、すぐにコーディングに集中できる。

**Why this priority**: Issue駆動開発の中核機能であり、日常的に最も頻繁に使用されるコマンドとなる。

**Independent Test**: 既存のGitHub Issueに対して`/start-issue`を実行し、ブランチ作成と計画立案が完了することで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** GitHub Issue #123（ラベル: enhancement）が存在する状態, **When** `/start-issue 123`を実行する, **Then** `feat/123-[issue-title]`形式のブランチが作成され、実装計画がMarkdown形式で出力される
2. **Given** GitHub Issue #456（ラベル: bug）が存在する状態, **When** `/start-issue 456`を実行する, **Then** `fix/456-[issue-title]`形式のブランチが作成される
3. **Given** Issue作業を開始した状態, **When** 計画立案が完了する, **Then** issue-reporterスキルによりIssueに計画がコメントとして投稿される

---

### User Story 3 - TDD駆動の実装 (Priority: P2)

開発者として、Red-Green-Refactorサイクルに従った実装を強制されたい。テストを先に書き、失敗を確認してから実装することで、コード品質を担保できる。

**Why this priority**: コード品質を担保する重要な機能だが、初期化とIssue開始が機能した後に価値を発揮する。

**Independent Test**: 新しい機能実装時にtdd-workflowスキルが起動し、テスト作成→実装→リファクタリングの順序が強制されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** Issue作業中でtdd-workflowが有効な状態, **When** 新しい機能の実装を開始する, **Then** まずテストファイルの作成が要求される
2. **Given** テストを作成した状態, **When** テストを実行する, **Then** テストが失敗し、ユーザー承認後に実装フェーズに移行できる
3. **Given** 実装が完了しテストが成功した状態, **When** リファクタリングを行う, **Then** 全テストが再実行され、成功することが確認される

---

### User Story 4 - 品質チェックゲート (Priority: P2)

開発者として、コミット前に自動的に品質チェックが実行されたい。lint、フォーマット、型チェックが通過しないとコミットできないことで、一貫したコード品質が維持される。

**Why this priority**: TDDと同様にコード品質を担保する機能で、実装フェーズで活用される。

**Independent Test**: コミット前にcode-quality-gateスキルが起動し、設定されたチェックが実行されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** Pythonプロジェクトで品質チェックが有効な状態, **When** コミットを試みる, **Then** ruff, mypy等の品質チェックが実行される
2. **Given** 品質チェックで警告またはエラーがある状態, **When** チェックが失敗する, **Then** コミットがブロックされ、問題箇所が報告される
3. **Given** すべての品質チェックが通過した状態, **When** コミットを実行する, **Then** コミットが正常に完了する

---

### User Story 5 - コミット・プッシュ・PR作成 (Priority: P2)

開発者として、実装完了後のコミット、プッシュ、PR作成を一連の流れで実行したい。バンドルされたgit-workflow-haikuのコマンド・エージェントを使用することで、外部プラグインなしにPR作成まで完了できる。

**Why this priority**: 実装後のPR作成はワークフローの中核ステップであり、すべてのコード変更がPRを通じてマージされる。

**Independent Test**: 実装済みの変更がある状態で`/commit-push-pr`を実行し、コミット、プッシュ、PR作成が完了することで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** 実装済みの変更が存在する状態, **When** `/commit-push-pr`を実行する, **Then** 変更がコミットされ、リモートにプッシュされ、PRが作成される
2. **Given** コミットメッセージが未指定の状態, **When** `/commit`を実行する, **Then** 変更内容から適切なコミットメッセージが自動生成される

---

### User Story 6 - PRレビューの実行 (Priority: P2)

開発者として、PRに対するコードレビューを自動実行したい。hachimoku CLIを使用してPRの差分をレビューし、結果をJSONL形式で保存することで、体系的なレビュープロセスを実現できる。

**Why this priority**: コード品質を担保する重要な機能。PR作成後、マージ前に実行される。

**Independent Test**: PRが存在する状態でhachimokuでレビューを実行し、`.hachimoku/reviews/pr-{number}.jsonl`にレビュー結果が出力されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** PR #300が存在する状態, **When** hachimoku CLIでレビューを実行する, **Then** `.hachimoku/reviews/pr-300.jsonl`にレビュー結果が出力される
2. **Given** レビュー結果がJSONL形式で出力された状態, **When** 結果を確認する, **Then** 各指摘の重要度、ファイル、行番号、内容が構造化されている

---

### User Story 7 - PRマージとクリーンアップ (Priority: P2)

開発者として、PRマージ後の後処理を自動化したい。CIの完了を待ち、マージを実行し、不要になったブランチやワークツリーを削除することで、作業環境がクリーンに保たれる。

**Why this priority**: ワークフローの終了処理であり、開発サイクル完了に必要。

**Independent Test**: マージ可能なPRに対して`/merge-pr`を実行し、マージ完了とクリーンアップが行われることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** CI通過済みのPR #100が存在する状態, **When** `/merge-pr 100`を実行する, **Then** PRがsquashマージされ、ローカルブランチが削除される
2. **Given** CIが実行中のPR #101が存在する状態, **When** `/merge-pr 101`を実行する, **Then** CI完了まで待機し、完了後にマージが実行される
3. **Given** ワークツリーを使用して作業していたPR, **When** マージが完了する, **Then** 対応するワークツリーとブランチが削除される

---

### User Story 8 - ワークツリーでの並行作業 (Priority: P3)

開発者として、複数のIssueを並行して作業したい。Issue毎にワークツリーを作成することで、ブランチ切り替えなしに複数の作業を同時進行できる。

**Why this priority**: 並行作業は高度なユースケースであり、基本ワークフローが機能した後のオプション機能。

**Independent Test**: `/add-worktree`コマンドを実行し、新しいワークツリーが作成されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** GitHub Issue #200が存在する状態, **When** `/add-worktree 200`を実行する, **Then** `../[project-name]-feat-200-[title]`形式のワークツリーが作成される
2. **Given** 複数のワークツリーが存在する状態, **When** それぞれのワークツリーで作業する, **Then** 互いに干渉せず独立して開発を進められる

---

### User Story 9 - レビュー指摘への対応 (Priority: P3)

開発者として、hachimokuによるレビュー結果を効率的に確認・対応したい。JSONL形式のレビュー出力を一覧で確認し、各指摘への対応方針を決定し、修正までを一連の流れで行える。

**Why this priority**: レビュー対応はワークフローの一部だが、基本的なPR作成・マージが機能した後の機能。

**Independent Test**: hachimokuのレビュー出力（`.hachimoku/reviews/pr-{number}.jsonl`）が存在する状態で`/respond-review`を実行し、指摘一覧と対応オプションが表示されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** hachimokuによるレビュー結果（`.hachimoku/reviews/pr-300.jsonl`）が存在する状態, **When** `/respond-review 300`を実行する, **Then** 指摘一覧が表示され、各指摘への対応方針を選択できる
2. **Given** 現在のブランチに紐づくPRのレビュー結果がある状態, **When** `/respond-review`（引数なし）を実行する, **Then** 自動的にPR番号が検出され、対応するJSONLファイルから指摘一覧が表示される

---

### User Story 10 - レビューコメント対応 (Priority: P3)

開発者として、PRレビューコメント（GitHub上の人間レビューア等）を確認・対応したい。コメントを一覧で確認し、対応方針を決定し、返信までを一連の流れで行える。

**Why this priority**: 人間レビューアからのフィードバック対応に必要。hachimokuレビュー対応とは別の経路。

**Independent Test**: レビューコメントのあるPRに対して`/review-pr-comments`を実行し、コメント一覧と対応オプションが表示されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** レビューコメントのあるPR #300が存在する状態, **When** `/review-pr-comments 300`を実行する, **Then** コメント一覧が表示され、各コメントへの対応方針を選択できる
2. **Given** 現在のブランチに紐づくPRがある状態, **When** `/review-pr-comments`（引数なし）を実行する, **Then** 自動的にPR番号が検出され、コメント一覧が表示される

---

### User Story 11 - 進捗の自動報告 (Priority: P3)

開発者として、作業進捗がIssueに自動報告されたい。計画立案時、問題発覚時、知見発見時に自動でコメントが投稿されることで、関係者が進捗を把握できる。

**Why this priority**: 進捗報告は付加価値機能であり、基本ワークフローの上に構築される。

**Independent Test**: issue-reporterスキルが各種イベント発生時にIssueコメントを投稿することで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** Issue #400で作業中の状態, **When** 計画立案が完了する, **Then** 📋アイコン付きで計画がIssueにコメントされる
2. **Given** 実装中に問題が発覚した状態, **When** issue-reporterに問題を報告する, **Then** ⚠️アイコン付きで問題内容がIssueにコメントされる

---

### Edge Cases

- CLIインストール時に必要な依存関係（gh CLI、uv等）が存在しない場合、明確なエラーメッセージと解決方法を提示する
- Issue番号が存在しない、またはアクセス権がない場合、適切なエラーハンドリングを行う
- ネットワーク接続がない状態での操作に対して、オフライン動作可能な範囲を明確にする
- 設定ファイルが破損または不完全な場合、検証と修復オプションを提供する
- 複数の開発者が同じIssueで同時に作業を開始した場合の競合処理
- CI実行時間が長い場合のタイムアウト処理
- PRマージ以外でworktreeを削除する場合（作業中断、Issue取り下げ等）は、ユーザーが`git worktree remove`で手動削除する
- hachimokuのインストールに失敗した場合（uv未インストール、ネットワークエラー等）、明確なエラーメッセージを表示する
- hachimokuのレビューJSONLファイルが存在しない場合、レビュー未実行である旨を通知する
- `git symbolic-ref refs/remotes/origin/HEAD`が未設定の場合（`git clone`直後でない場合等）、`git remote set-head origin --auto`で自動設定を試み、それでも失敗した場合はエラーメッセージを表示する

## Requirements *(mandatory)*

### Functional Requirements

#### CLI要件

- **FR-001**: システムは`issue-workflow init`コマンドでプロジェクトを初期化できなければならない
- **FR-002**: システムは5つの言語プリセット（Python, TypeScript, Go, Rust, Generic）をサポートしなければならない
- **FR-003**: 初期化時に対話形式または`--language`オプションで言語を選択できなければならない
- **FR-004**: `--non-interactive`オプションでプロンプトをスキップできなければならない
- **FR-005**: 初期化により`.claude/workflow-config.json`、`.claude/git-conventions.md`、`.claude/commands/`、`.claude/agents/`が生成されなければならない
- **FR-006**: 初期化時にhachimokuが未インストールの場合、`uv tool install hachimoku`により自動インストールしなければならない。既にインストール済みの場合はスキップする。インストール後、`8moku init`をサブプロセスとして呼び出し、`.hachimoku/`ディレクトリを初期化しなければならない
- **FR-007**: システムは`issue-workflow update`コマンドでcommands/、skills/、agents/ファイルを更新できなければならない

#### バンドルコマンド・エージェント要件

- **FR-008**: `/start-issue <issue番号>`でIssueを読み込み、ブランチを作成し、計画を立案できなければならない
- **FR-009**: ブランチプレフィックスはIssueラベルに基づいて自動判定されなければならない（enhancement→feat/, bug→fix/等）
- **FR-010**: `/commit-push-pr`で変更のコミット、プッシュ、PR作成を一連で実行できなければならない（git-workflow-haikuバンドル）
- **FR-011**: `/merge-pr <PR番号>`でCI完了待機、マージ、クリーンアップを実行できなければならない（git-workflow-haikuバンドル）
- **FR-012**: マージ戦略はsquash（デフォルト）、merge、rebaseから選択できなければならない
- **FR-013**: `/add-worktree <issue番号>`でIssue用のワークツリーを作成できなければならない

#### レビュー要件

- **FR-014**: hachimoku CLI（`8moku`）によるPRレビューをワークフローに組み込まなければならない。スクリプトからは`8moku`を直接呼び出す
- **FR-015**: hachimokuのレビュー結果は`.hachimoku/reviews/pr-{number}.jsonl`に出力されなければならない
- **FR-016**: `/respond-review [PR番号]`は、hachimoku JSONL出力を読み取り指摘一覧を表示できなければならない
- **FR-017**: `/respond-review`は引数なしの場合、ブランチ名からPR番号を自動検出できなければならない
- **FR-018**: `/review-pr-comments [PR番号]`でGitHub APIベースのレビューコメントを確認・対応できなければならない

#### スキル要件

- **FR-019**: tdd-workflowスキルはRed-Green-Refactorサイクルを強制しなければならない
- **FR-020**: Redフェーズでテスト失敗を確認してからGreenフェーズに移行できなければならない
- **FR-021**: code-quality-gateスキルは`workflow-config.json`の`quality.all`コマンドを実行しなければならない
- **FR-022**: 品質チェック失敗時はコミットをブロックしなければならない
- **FR-023**: issue-reporterスキルは計画立案時、問題発覚時等にIssueへコメントを投稿しなければならない
- **FR-024**: ブランチ名からIssue番号を抽出できなければならない（feat/123-xxx → #123）

#### Git操作要件

- **FR-025**: すべてのコマンド、エージェント、スクリプトは base branch を`main`にハードコードしてはならない。`git symbolic-ref refs/remotes/origin/HEAD`により default branch を自動検出しなければならない
- **FR-026**: Gitflow（`develop`ブランチ）、`master`ブランチ、その他のブランチ戦略を使うプロジェクトでも正しく動作しなければならない

#### 設定要件

- **FR-027**: `workflow-config.json`はJSON Schemaによる検証をサポートしなければならない
- **FR-028**: 品質コマンド（lint, format, typecheck, test, all）は言語プリセット毎に適切なデフォルト値を持たなければならない
- **FR-029**: Git規約（ブランチ命名、コミットメッセージ形式）は`git-conventions.md`で定義されなければならない

### Key Entities

- **Issue**: GitHub Issue。番号、タイトル、ラベル、本文を持つ。作業の起点となる。
- **Branch**: Gitブランチ。Issueに紐づき、プレフィックスとIssue番号を含む命名規則に従う。
- **Worktree**: Git worktree。Issueごとの独立した作業ディレクトリを提供する。
- **PR (Pull Request)**: GitHub PR。ブランチからメインブランチへの変更提案。マージ戦略を持つ。
- **Workflow Config**: プロジェクト設定。言語、品質コマンド、Git設定、ワークフロー設定を含む。
- **Language Preset**: 言語別の初期設定テンプレート。Python, TypeScript, Go, Rust, Genericの5種類。
- **Review Result**: hachimokuによるレビュー結果。JSONL形式で`.hachimoku/reviews/`に保存される。指摘の重要度、ファイル、行番号、内容を含む。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 開発者は5分以内にプロジェクトへIssue Workflowを導入完了できる（hachimokuインストール含む）
- **SC-002**: Issue作業開始から計画立案まで2分以内で完了する
- **SC-003**: 5つの言語プリセット（Python, TypeScript, Go, Rust, Generic）で同一のワークフロー体験を提供する
- **SC-004**: TDDサイクル遵守率が100%となる（スキル有効時にRed-Green-Refactorをスキップできない）
- **SC-005**: 品質チェック通過なしのコミット発生率が0%となる（スキル有効時）
- **SC-006**: PRマージ後のブランチ・ワークツリーのクリーンアップ成功率が100%となる
- **SC-007**: Issue進捗報告の自動投稿成功率が95%以上となる
- **SC-008**: CLIコマンドは明確なフィードバック（進捗表示、完了メッセージ）を提供する
- **SC-009**: 外部プラグイン（commit-commands, pr-review-toolkit）への依存が0となる

## Assumptions

- GitHub CLIツール（`gh`）がインストールされ、認証済みであること
- Claude Codeがインストールされ、利用可能であること
- プロジェクトがGitリポジトリとして初期化されていること
- GitHubリポジトリへの適切なアクセス権があること
- ネットワーク接続が利用可能であること（Issue取得、PR操作等に必要）
- `uv`がインストールされていること（hachimokuのインストールに必要）

## Distribution

- **リポジトリ**: `github.com/drillan/issue-workflow`
- **CLIインストール**: `uv tool install issue-workflow`
- **バンドルコンテンツ**: git-workflow-haikuのcommands/とagents/を`issue-workflow init`/`update`で`.claude/commands/`と`.claude/agents/`にコピー
- **外部ツール**: hachimoku（`uv tool install hachimoku`で`issue-workflow init`時に自動インストール）
- **対象プロジェクト**: 言語非依存（Python, TypeScript, Go, Rust, Generic + カスタム）

## Out of Scope

- spec-kit（仕様駆動開発ツール）との統合（独立したツールとして手動インストール）
- プロジェクト固有のconstitution（ユーザーが定義すべき内容）
- GitHub Actions統合（v2.0で検討）
- Slack/Discord通知（v2.0で検討）
- メトリクス収集・可視化（v2.0で検討）
- hachimokuの内部実装、認証設定、レビューロジックのカスタマイズ（hachimoku側の責務）
