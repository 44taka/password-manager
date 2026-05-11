# ADR 0002: 統合リポジトリ（Composite パターン）の採用

## Status
Accepted

## Date
2026-05-11

## Context
本アプリケーションでは、アカウント情報を以下の2つの異なるストレージに保存している：
1. **SQLite**: メタデータ（サービス名、ログインID、メモ、作成日時等）
2. **OS Keychain**: 秘密情報（パスワード）

これらを扱う際、ユースケース層で個別にリポジトリを呼び出すか、あるいはインフラ層で統合して見せるかを検討する必要があった。

### 検討した選択肢
1. **ユースケース制御型**: ユースケースが `MetadataRepository` と `SecretRepository` の両方に依存し、保存・取得の順序を制御する。
2. **統合リポジトリ型（Composite パターン）**: インフラ層に `UnifiedAccountRepository` を作成し、ドメイン層の `AccountRepository` インターフェースを実装する。内部で SQLite と Keychain の各コンポーネントを呼び出す。

## Decision
**「2. 統合リポジトリ型（Composite パターン）」を採用する**

具体的には以下の構成とする：
- ドメイン層の `AccountRepository` は、パスワードを含む `Account` 集約全体を扱う。
- インフラ層において、SQLite 担当の `SqliteAccountStore` と Keychain 担当の `KeychainAccountStore` を個別のファイルに実装する。
- これらを合成（Composition）した `UnifiedAccountRepository` を作成し、ドメイン層のインターフェースを満たす唯一の実体とする。

## Rationale
- ✅ **ドメインモデルの完全性の保証**: リポジトリから取得した時点で `Account` オブジェクトがパスワードも含めて「完全な状態」であることを保証できる。不完全なモデルがドメイン層やユースケース層に漏れ出すのを防ぐ。
- ✅ **ユースケース層の簡素化**: ユースケースは保存先の詳細（SQLite か Keychain か）を知る必要がなく、単一のリポジトリを操作するだけで済む。
- ✅ **関心の分離（SoC）**: SQLite の操作ロジックと Keychain の操作ロジックを別ファイルに分離したまま保てるため、技術的な変更（例：Keychain を暗号化ファイルに置き換える等）の影響を局所化できる。

## Consequences

### Positive
- ユースケースの実装が極めてシンプルになり、データの保存し忘れや読み込み忘れといったバグを防げる。
- ビジネスロジック（UseCase/Domain）とインフラ詳細（Storage）の分離がより強固になる。

### Negative
- 複数の保存先を束ねるための「糊付け」のコード（Composite クラス）が必要になる。
- 片方の保存が成功し、もう片方が失敗した場合の整合性管理（トランザクション的な振る舞い）に注意を払う必要がある。

## Example
```python
# unified_account_repository.py
class UnifiedAccountRepository(AccountRepository):
    def __init__(self, sqlite_store: SqliteAccountStore, keychain_store: KeychainAccountStore):
        self.sqlite = sqlite_store
        self.keychain = keychain_store

    def find_by_id(self, account_id: AccountID) -> Account | None:
        metadata = self.sqlite.fetch(account_id)
        password = self.keychain.fetch(account_id)
        return Account.reconstruct(metadata, password)
```
