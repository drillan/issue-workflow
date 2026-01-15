# Feature Specification: Update Command

**Feature Branch**: `010-update-command`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description: "specs/001-issue-workflow/spec.mdを親仕様としたupdateコマンドを定義してください、src/issue_workflow/commandsやsrc/issue_workflow/skillsの内容が更新されたときに、ユーザプロジェクトの.claude/commandsや.claude/skillsなどが更新されるイメージです"
**Parent Spec**: `specs/001-issue-workflow/spec.md` (FR-007)

## Clarifications

### Session 2026-01-15

- Q: 選択的更新（--commands-only/--skills-only）は必要か？ → A: 不要。常にcommands/skills両方を更新する
- Q: ユーザー編集ファイルの検出方法は？ → A: 検出しない。常に上書きし、カスタムファイルは別ディレクトリで管理する
- Q: 更新前の確認プロンプトは必要か？ → A: 不要。常に即時更新し、事前確認は--dry-runで行う
- Q: 親仕様FR-007との整合性は？ → A: 親仕様を修正（「設定を更新」→「commands/skillsを更新」）

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 基本的な更新操作 (Priority: P1)

開発者として、`issue-workflow update`コマンドを実行することで、プロジェクトの`.claude/commands`と`.claude/skills`ディレクトリを最新バージョンに更新したい。これにより、Issue Workflowの新機能やバグ修正を即座にプロジェクトに反映できる。

**Why this priority**: 更新コマンドの中核機能であり、すべてのユーザーが最も頻繁に使用する操作。

**Independent Test**: `issue-workflow update`を実行し、`.claude/commands`と`.claude/skills`の内容が更新されることで、独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** Issue Workflowで初期化済みのプロジェクト, **When** `issue-workflow update`を実行する, **Then** `.claude/commands`と`.claude/skills`ディレクトリの内容が最新のツールキット内容で上書きされる
2. **Given** 初期化済み（`.claude/`存在）だが`.claude/commands`や`.claude/skills`が存在しないプロジェクト, **When** `issue-workflow update`を実行する, **Then** 必要なディレクトリが作成され、最新のファイルがコピーされる
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

### Edge Cases

- `.claude/`ディレクトリが存在しない（initコマンド未実行）場合、明確なエラーメッセージと`init`コマンドの案内を表示する
- ツールキットのバージョンがプロジェクトより古い場合 → 警告なしで上書き（v1.2でバージョン比較機能を検討）
- ファイル権限エラー時の適切なエラーメッセージ表示
- 部分的に更新が失敗した場合 → エラーメッセージを表示して終了（ロールバックしない、既にコピーされたファイルは残る）

## Requirements *(mandatory)*

### Functional Requirements

#### CLIコマンド要件

- **FR-001**: システムは`issue-workflow update`コマンドでcommands/skillsを更新できなければならない
- **FR-002**: 更新コマンドはツールキットの`src/issue_workflow/commands/`から`.claude/commands/`へファイルをコピーしなければならない
- **FR-003**: 更新コマンドはツールキットの`src/issue_workflow/skills/`から`.claude/skills/`へディレクトリ構造を再帰的にコピーしなければならない
- **FR-004**: `--dry-run`オプションで実際の更新なしに差分を表示できなければならない

#### 前提条件要件

- **FR-005**: システムは`.claude/`ディレクトリの存在を確認し、存在しない場合はエラーを返さなければならない
- **FR-006**: システムはツールキットのcommands/skillsディレクトリの存在を確認できなければならない

#### 出力要件

- **FR-007**: 更新完了時に追加・更新・削除されたファイルの一覧を表示しなければならない
- **FR-008**: エラー発生時は原因と解決方法を含むメッセージを表示しなければならない
- **FR-009**: 終了コードは成功時0、エラー時非0を返さなければならない

#### 動作要件

- **FR-010**: 更新時はcommands/skillsを常に上書きしなければならない（確認プロンプトなし、カスタムファイルは別ディレクトリで管理）

### Key Entities

- **Commands**: `.claude/commands/`配下のMarkdownファイル群。各ファイルはClaude Codeのスラッシュコマンド定義を含む。
- **Skills**: `.claude/skills/`配下のディレクトリ群。各ディレクトリは`SKILL.md`を含み、Claude Codeのスキル定義を表す。
- **Source Directory**: ツールキットの`src/issue_workflow/commands/`と`src/issue_workflow/skills/`。更新元となるマスターファイル群。
- **Target Directory**: ユーザープロジェクトの`.claude/commands/`と`.claude/skills/`。更新先となるファイル群。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 通常のファイル数（commands 10ファイル + skills 5ディレクトリ程度）で30秒以内に更新を完了できる
- **SC-002**: `--dry-run`による差分確認は実際のファイル変更を0件にする
- **SC-003**: 更新操作の成功率は99%以上となる（ファイルアクセス可能な場合）
- **SC-004**: 更新完了後、すべてのcommands/skillsがツールキットと同一内容となる
- **SC-005**: エラー発生時は100%の確率で解決方法を含むメッセージが表示される
- **SC-006**: CI/CD環境で追加入力なしに更新が完了する（確認プロンプトなし）

## Assumptions

- `issue-workflow init`コマンドが事前に実行され、`.claude/`ディレクトリが存在すること
- ツールキットがローカルにインストールされていること（`uv`や`pip`経由）
- `.claude/`ディレクトリへの書き込み権限があること
- commands/skillsファイルはMarkdown形式であること

## Out of Scope

- `workflow-config.json`の更新（設定変更は別コマンドまたは手動で対応）
- `git-conventions.md`の更新（プロジェクト固有設定のため）
- 自動バージョン管理・更新通知機能（v1.2で検討）
- リモートからの直接ダウンロード更新（現バージョンはローカルインストール前提）
- ユーザーカスタムcommands/skillsのバックアップ機能（v1.2で検討）
- 選択的更新（--commands-only/--skills-only）- 常に両方を更新する
- `--non-interactive`オプション - updateコマンドは常に確認プロンプトなしで実行されるため不要
