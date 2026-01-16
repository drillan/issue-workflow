# Git Conventions

このファイルはプロジェクトのGit命名規則を定義するSingle Source of Truth（正式ソース）です。

## Branch Naming

### Format

```
<type>/<issue-number>-<description>
```

### Type Prefixes

| タイプ | プレフィックス | 用途 |
|--------|---------------|------|
| 機能追加 | `feat/` | 新機能の実装 |
| バグ修正 | `fix/` | バグの修正 |
| リファクタリング | `refactor/` | コードの整理・改善 |
| ドキュメント | `docs/` | ドキュメントの追加・修正 |
| テスト | `test/` | テストの追加・修正 |
| 雑務 | `chore/` | 設定変更、依存関係更新など |

### Issue Number

- ゼロパディングなし: `123`（正）、`001`（誤）
- issue番号がない場合は省略可: `feat/add-logging`

### Description

- 英語で記述
- ハイフン区切り（kebab-case）
- 2-4語程度の簡潔な説明
- 小文字のみ

### Examples

```
feat/123-add-user-authentication
fix/456-fix-login-error
refactor/789-cleanup-api-client
docs/101-update-readme
test/111-add-e2e-tests
chore/222-update-dependencies
```

### Branch Type Detection (for start-issue)

issueからブランチタイプを自動判別する際のマッピング:

**GitHubラベル → プレフィックス:**

| ラベル | プレフィックス |
|--------|---------------|
| `enhancement`, `feature` | `feat/` |
| `bug` | `fix/` |
| `refactoring`, `refactor` | `refactor/` |
| `documentation`, `docs` | `docs/` |
| `test` | `test/` |
| `chore` | `chore/` |

**キーワード → プレフィックス（ラベルがない場合）:**

| キーワード | プレフィックス |
|-----------|---------------|
| `bug`, `fix`, `バグ`, `修正`, `不具合`, `エラー` | `fix/` |
| `refactor`, `リファクタ`, `整理`, `改善` | `refactor/` |
| `doc`, `ドキュメント`, `README`, `説明` | `docs/` |
| `test`, `テスト` | `test/` |
| `chore`, `設定`, `config` | `chore/` |
| `add`, `追加`, `新機能`, `implement`, `実装` | `feat/` |

**デフォルト:** `feat/`

## Commit Message

### Format

[Conventional Commits](https://www.conventionalcommits.org/) 形式に従う:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Type

ブランチプレフィックスと同一:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: その他

### Scope（任意）

- issue番号: `feat(#123): add login feature`
- モジュール名: `fix(api): handle timeout error`

### Description

- 英語で記述
- 命令形（imperative mood）: "add" not "added"
- 小文字で開始
- 末尾にピリオドを付けない

### Examples

```
feat(#123): add user authentication

fix(api): handle session expiration correctly

docs: update installation guide

refactor(#456): extract common validation logic

chore: update dependencies to latest versions
```

## Git Worktree

### Format

```
../<project-name>-<branch-name>
```

### Rules

- 配置場所: メインリポジトリの親ディレクトリ
- プロジェクト名: リポジトリのディレクトリ名を使用（例: `my-project`）
- ブランチ名: `/` を `-` に置換

### Examples

| ブランチ | ワークツリーディレクトリ |
|---------|------------------------|
| `feat/123-add-auth` | `../${PROJECT_NAME}-feat-123-add-auth` |
| `fix/456-fix-login` | `../${PROJECT_NAME}-fix-456-fix-login` |
| `refactor/789-cleanup` | `../${PROJECT_NAME}-refactor-789-cleanup` |

### Commands

```bash
# 既存ブランチのワークツリー作成
git worktree add ../${PROJECT_NAME}-feat-123-add-auth feat/123-add-auth

# 新規ブランチとワークツリーを同時作成
git worktree add -b feat/123-add-auth ../${PROJECT_NAME}-feat-123-add-auth

# ワークツリーの一覧
git worktree list

# ワークツリーの削除
git worktree remove ../${PROJECT_NAME}-feat-123-add-auth
```
