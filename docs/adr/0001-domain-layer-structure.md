# ADR 0001: ドメイン層のディレクトリ構成とファイル分割方針

## Status
Accepted

## Date
2026-05-11

## Context
DDD（Domain-Driven Design）を導入するにあたり、ドメイン層のコード（Entity, Value Object, Repository Interface等）をどのように整理・配置するかを決定する必要があった。
Pythonの一般的な慣習では1つのモジュール（ファイル）に関連する複数のクラスを定義することが多いが、大規模なドメインロジックを扱う場合、関心の分離や境界の明確化が課題となる。

### 検討した選択肢
1. **フラット構成**: `domain/models.py`, `domain/repositories.py` に全て記述する（現状）。
2. **集約ごとのファイル構成**: `domain/account.py` に Account 集約に関する全てを記述する。
3. **集約ごとのディレクトリ構成 + 1クラス1ファイル**: `domain/account/` 配下に `account.py`, `password.py` 等を個別に配置する。

## Decision
**「3. 集約ごとのディレクトリ構成 + 1クラス1ファイル」を採用する**

具体的には以下のルールに従う：
- `src/password_manager/domain/[aggregate_name]/` というディレクトリを作成する。
- その配下に、Entity、Value Object、Repository Interface などを、1クラス1ファイルの単位で分割して定義する。
- 各ディレクトリの `__init__.py` で主要なクラスを Re-export し、**Facade (ファサード) パターン** を適用することで、外部からのインポートを簡潔かつ直感的に保つ。

## Rationale
- ✅ **関心の分離**: ファイル単位で責務が明確になり、コードの凝集度が高まる。
- ✅ **集約の境界の可視化**: ディレクトリ構造そのものがドメインの境界（Aggregate）を表すため、構造が理解しやすくなる。
- ✅ **変更の影響範囲の最小化**: 特定の Value Object の変更が他のモデルに物理的に影響しにくくなる。
- ✅ **メンテナンス性**: 1ファイルが軽量に保たれ、単体テストとの対応も取りやすくなる。

## Consequences

### Positive
- モデルの責任範囲が物理的なファイル構造と一致するため、迷いなくコードを配置できる。
- 複数人での開発時や将来的な拡張時に、コードの衝突や肥大化を防げる。

### Negative
- ファイル数が増加するため、プロジェクト全体のファイル管理が煩雑に感じる可能性がある。
- インポート文がそのままでは冗長になる（ただし、`__init__.py` による Re-export で回避可能）。

### Neutral
- Pythonの一般的な慣習（1モジュール多クラス）とは異なるため、新規参画者への周知が必要。

## Example
```text
src/password_manager/domain/
└── account/
    ├── __init__.py
    ├── account.py           (Entity / Aggregate Root)
    ├── account_id.py        (Value Object)
    ├── password.py          (Value Object)
    └── account_repository.py (Repository Interface)
```
