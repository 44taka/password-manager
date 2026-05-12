# ADR 0006: AccountID の整数から UUID への移行

## Status
Accepted

## Date
2026-05-12

## Context
当初、アカウントの識別子（`AccountID`）は SQLite の `AUTOINCREMENT` 機能に依存した整数型（`int`）を使用していた。しかし、この設計には以下の課題があった：

1. **ドメイン層のインフラ依存**: エンティティを新規作成した時点では ID が確定せず、リポジトリに保存した後に DB 側で採番された ID をエンティティに「後付け」する必要があった。
2. **不自然なコードハック**: `UnifiedAccountRepository` において、不変オブジェクトである `Account` エンティティの ID を、保存後に `object.__setattr__` を用いて強制的に書き換えるという、ドメイン駆動設計（DDD）の原則に反する実装が行われていた。
3. **キーチェーン連携の複雑さ**: SQLite の ID が確定するまで、パスワードをキーチェーンに保存する際のキー（ID）が定まらず、不整合が起きやすい状態だった。

## Decision
**「AccountID をアプリケーション側で発行する UUID (v4) に変更する」**

具体的には以下の変更を実施した：
- **AccountID の再定義**: `int` ベースから、内部に UUID 文字列を持つバリューオブジェクトに変更。
- **ID 生成の主導権**: ドメイン層の `Account.create()` メソッド内で `AccountID.generate()` を呼び出し、インスタンス化の瞬間に一意な ID を確定させる。
- **永続化層の変更**: SQLite の主キーを `INTEGER` から `TEXT` に変更し、オートインクリメントを廃止。
- **ファクトリの明確化**: 新規作成用の `create()` と、既存データ復元用の `reconstruct()` にファクトリメソッドを分離。

## Rationale
- ✅ **ドメインモデルの純粋性**: エンティティが生成された瞬間から完全な状態（ID 込み）となり、インフラ層の挙動に左右されなくなった。
- ✅ **コードの安全性**: リポジトリ内での危険な `__setattr__` ハックを完全に排除できた。
- ✅ **一貫性**: データベース保存前であっても ID が確定しているため、キーチェーンへの保存や他のオブジェクトとの関連付けが安全に行える。

## Consequences

### Positive
- `UnifiedAccountRepository` の実装がクリーンになり、保守性が向上した。
- エンティティのテストにおいて、DB の採番を模倣する必要がなくなった。

### Negative
- 既存のデータベース（整数 ID）との互換性が失われた。移行にあたっては既存の `passwords.db` を削除し、再作成する必要がある。

### Neutral
- ID が 1, 2, 3... ではなく `e8e29712...` のような長い文字列になるが、内部的な識別子であるため UX への影響はない。

## Example
```python
# 新規作成
account = Account.create(service_name="Google", ...)
print(account.id)  # 'e8e29712-be3d-4c31-96a0-0e69b1921fc5'

# 保存（Repository 側で ID を書き換える必要はない）
repo.save(account)
```
