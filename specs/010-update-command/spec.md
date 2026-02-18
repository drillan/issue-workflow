# Feature Specification: Update Command

**Feature Branch**: `010-update-command`
**Created**: 2026-01-15
**Updated**: 2026-02-18
**Status**: Draft
**Input**: User description: "specs/001-issue-workflow/spec.mdを親仕様としたupdateコマンドを定義してください、src/issue_workflow/skillsやsrc/issue_workflow/agentsの内容が更新されたときに、ユーザプロジェクトの.claude/skillsや.claude/agentsなどが更新されるイメージです"
**Parent Spec**: `specs/001-issue-workflow/spec.md` (FR-007)

## Clarifications

### Session 2026-01-15

- Q: 選択的更新（--skills-only/--agents-only）は必要か？ → A: 不要。常にskills/agents両方を更新する
- Q: ユーザー編集ファイルの検出方法は？ → A: 検出しない。常に上書きし、カスタムファイルは別ディレクトリで管理する
- Q: 更新前の確認プロンプトは必要か？ → A: 不要。常に即時更新し、事前確認は--dry-runで行う
- Q: 親仕様FR-007との整合性は？ → A: 親仕様を修正（「設定を更新」→「skills/agentsを更新」）

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 基本的な更新操作 (Priority: P1)

開発者として、`issue-workflow update`コマンドを実行することで、プロジェクトの`.claude/skills`と`.claude/agents`ディレクトリを最新バージョンに更新したい。これにより、Issue Workflowの新機能やバグ修正を即座にプロジェクトに反映できる。

**Why this priority**: 更新コマンドの中核機能であり、すべてのユーザーが最も頻繁に使用する操作。

**Independent Test**: `issue-workflow update`を実行し、`.claude/skills`と`.claude/agents`の内容が更新されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** Issue Workflowで初期化済みのプロジェクト, **When** `issue-workflow update`を実行する, **Then** `.claude/skills`と`.claude/agents`ディレクトリの内容が最新のツールキット内容で上書きされる
2. **Given** 初期化済み（`.claude/`存在）だが`.claude/skills`や`.claude/agents`が存在しないプロジェクト, **When** `issue-workflow update`を実行する, **Then** 必要なディレクトリが作成され、最新のファイルがコピーされる
3. **Given** 更新対象のファイルが存在する状態, **When** 更新が完了する, **Then** 更新されたファイルの一覧と変更内容の要約が表示される

---

### User Story 2 - 更新前の差分確認 (Priority: P2)

開発者として、実際の更新前に変更内容を確認したい。`--dry-run`オプションにより、どのファイルが更新されるかを事前に把握し、予期しない変更を防ぐことができる。

**Why this priority**: 安全な更新操作のために重要だが、基本的な更新機能が動作した後に価値を発揮する。

**Independent Test**: `issue-workflow update --dry-run`を実行し、実際のファイル変更なしに差分情報が表示されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** 更新対象のファイルが存在する状態, **When** `issue-workflow update --dry-run`を実行する, **Then** 追加・更新・削除されるファイルの一覧が表示され、実際のファイル変更は行われない
2. **Given** 更新対象のファイルが存在する状態, **When** `--dry-run`で差分を確認する, **Then** 各ファイルの変更内容（追加/変更/削除）が明確に区別して表示される

---

### User Story 3 - hachimoku 更新ヒント表示 (Priority: P3)

開発者として、`issue-workflow update`実行時に hachimoku の新しいバージョンが利用可能な場合にヒントを表示してほしい。これにより、依存ツールの更新タイミングを見逃さずに済む。

**Why this priority**: 情報提供のみで update 本体の動作に影響しない補助的機能。

**Independent Test**: hachimoku がインストール済みかつリモートに新しいバージョンがある状態で `issue-workflow update` を実行し、ヒントメッセージが表示されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** hachimoku がインストール済みでリモートに新しいバージョンがある, **When** `issue-workflow update`を実行する, **Then** アップグレードヒントが表示される
2. **Given** hachimoku がインストール済みで最新バージョン, **When** `issue-workflow update`を実行する, **Then** ヒントは表示されない
3. **Given** hachimoku が未インストール, **When** `issue-workflow update`を実行する, **Then** ヒントはスキップされ、update 本体は正常に動作する
4. **Given** リモートバージョンの取得に失敗（ネットワークエラー等）, **When** `issue-workflow update`を実行する, **Then** ヒントはスキップされ、update 本体は正常に動作する
5. **Given** `--dry-run` モード, **When** `issue-workflow update --dry-run`を実行する, **Then** ヒントは通常通り表示される

---

### Edge Cases

- `.claude/`ディレクトリが存在しない（initコマンド未実行）場合、明確なエラーメッセージと`init`コマンドの案内を表示する
- ツールキットのバージョンがプロジェクトより古い場合 → 警告なしで上書き（v1.2でバージョン比較機能を検討）
- ファイル権限エラー時の適切なエラーメッセージ表示
- 部分的に更新が失敗した場合 → エラーメッセージを表示して終了（ロールバックしない、既にコピーされたファイルは残る）
- hachimoku バージョンチェック失敗時（未インストール、ネットワークエラー、パース失敗）→ ヒントをスキップし、update 本体は継続

## Requirements *(mandatory)*

### Functional Requirements

#### CLIコマンド要件

- **FR-001**: システムは`issue-workflow update`コマンドでskills/agentsを更新できなければならない
- **FR-002**: 更新コマンドはツールキットの`src/issue_workflow/skills/`から`.claude/skills/`へディレクトリ構造を再帰的にコピーしなければならない
- **FR-003**: 更新コマンドはツールキットの`src/issue_workflow/agents/`から`.claude/agents/`へファイルをコピーしなければならない
- **FR-004**: `--dry-run`オプションで実際の更新なしに差分を表示できなければならない

#### 前提条件要件

- **FR-005**: システムは`.claude/`ディレクトリの存在を確認し、存在しない場合はエラーを返さなければならない
- **FR-006**: システムはツールキットのskills/agentsディレクトリの存在を確認できなければならない

#### 出力要件

- **FR-007**: 更新完了時に追加・更新・削除されたファイルの一覧を表示しなければならない
- **FR-008**: エラー発生時は原因と解決方法を含むメッセージを表示しなければならない
- **FR-009**: 終了コードは成功時0、エラー時非0を返さなければならない

#### 動作要件

- **FR-010**: 更新時はskills/agentsを常に上書きしなければならない（確認プロンプトなし、カスタムファイルは別ディレクトリで管理）

#### hachimoku バージョンチェック要件

- **FR-011**: `issue-workflow update`実行時に、hachimoku のローカルバージョンとリモート最新バージョンを比較し、更新が利用可能な場合にヒントメッセージを表示しなければならない
- **FR-012**: ローカルバージョンは`8moku --version`コマンドの出力から取得しなければならない
- **FR-013**: リモート最新バージョンは`https://raw.githubusercontent.com/drillan/hachimoku/refs/heads/main/pyproject.toml`をHTTP GETし、`tomllib`でパースして取得しなければならない
- **FR-014**: バージョンチェックの失敗（未インストール、ネットワークエラー、パース失敗）は update 本体の処理に影響を与えてはならない

### Key Entities

- **Skills**: `.claude/skills/`配下のディレクトリ群。各ディレクトリは`SKILL.md`を含み、Claude Codeのスキル定義を表す。
- **Agents**: `.claude/agents/`配下のMarkdownファイル群。各ファイルはClaude Codeのエージェント定義を含む。
- **Source Directory**: ツールキットの`src/issue_workflow/skills/`と`src/issue_workflow/agents/`。更新元となるマスターファイル群。
- **Target Directory**: ユーザープロジェクトの`.claude/skills/`と`.claude/agents/`。更新先となるファイル群。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 通常のファイル数（skills 10ディレクトリ + agents 5ファイル程度）で30秒以内に更新を完了できる
- **SC-002**: `--dry-run`による差分確認は実際のファイル変更を0件にする
- **SC-003**: 更新操作の成功率は99%以上となる（ファイルアクセス可能な場合）
- **SC-004**: 更新完了後、すべてのskills/agentsがツールキットと同一内容となる
- **SC-005**: エラー発生時は100%の確率で解決方法を含むメッセージが表示される
- **SC-006**: CI/CD環境で追加入力なしに更新が完了する（確認プロンプトなし）

## Assumptions

- `issue-workflow init`コマンドが事前に実行され、`.claude/`ディレクトリが存在すること
- ツールキットがローカルにインストールされていること（`uv`や`pip`経由）
- `.claude/`ディレクトリへの書き込み権限があること
- skills/agentsファイルはMarkdown形式であること

## Out of Scope

- `workflow-config.json`の更新（設定変更は別コマンドまたは手動で対応）
- `git-conventions.md`の更新（プロジェクト固有設定のため）
- hachimoku の自動アップグレード実行（ヒント表示のみ提供）
- hachimoku エージェント定義の自動更新（`8moku init --force` はユーザーが手動実行）
- リモートからの直接ダウンロード更新（現バージョンはローカルインストール前提）
- ユーザーカスタムskills/agentsのバックアップ機能（v1.2で検討）
- 選択的更新（--skills-only/--agents-only）- 常に両方を更新する
- `--non-interactive`オプション - updateコマンドは常に確認プロンプトなしで実行されるため不要
