---
description: プロジェクト全体で遵守すべきPythonコーディング規約を定義します。
---

# 🎨 コーディングスタイル・ガイドライン

本プロジェクトでは、コードの可読性、保守性、および一貫性を保つために以下の規約を遵守します。

## 1. 基本スタイル
- **PEP 8 準拠**: 基本的なスタイルは [PEP 8](https://peps.python.org/pep-0008/) に従います。
- **最大行長**: 100文字（`pyproject.toml` の設定に準拠）。
- **インデント**: 半角スペース 4 つ。
- **引用符**: 文字列には原則としてダブルクォート (`"`) を使用します（Ruffの自動整形に従います）。
- **空行**:
    - トップレベルのクラスや関数定義の間には 2 行の空行を置く。
    - クラス内のメソッド定義の間には 1 行の空行を置く。

## 2. 命名規則
- **変数・関数・メソッド**: `snake_case` (例: `user_name`, `get_password()`)
- **クラス**: `PascalCase` (例: `PasswordRepository`, `AppController`)
- **定数**: `UPPER_SNAKE_CASE` (例: `CLIPBOARD_CLEAR_SECONDS`)
- **プライベート属性/メソッド**: 先頭にアンダースコアを 1 つ付ける (例: `_internal_method()`)

## 3. インポート規約
Ruff の `isort` ルールに従い、以下の順序で空行を挟んでグループ化します。
1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルのアプリケーションモジュール

- **Facade (ファサード) パターン**: 各パッケージの `__init__.py` で主要なクラスを Re-export します。外部のレイヤーからはパッケージルートからインポートすることを推奨します。
    - ✅ 推奨: `from password_manager.domain.account import Account`
    - ❌ 非推奨: `from password_manager.domain.account.account import Account`

## 4. 型ヒント (Type Hints)
- **原則必須**: すべての関数とメソッドの引数、および戻り値に対して型ヒントを記述してください。
- **Pyright**: `Pyright` による静的解析でエラーが出ない状態を維持してください。

## 5. ドキュメント (docstring)
- **フォーマット**: [Googleスタイル](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) を採用します。
- **対象**: すべてのパブリックなクラス、メソッド、関数に docstring を記述してください。

### 例:
```python
def example_function(param1: int, param2: str) -> bool:
    """関数の概要をここに記述します。

    Args:
        param1: 1つ目の引数の説明。
        param2: 2つ目の引数の説明。

    Returns:
        処理結果の真偽値。
    """
    return True
```

    return True
```

## 6. 設計・クラス構造
- **1クラス・1ファイル方針**:
    - 原則として 1 つのファイルには 1 つのクラス（または 1 つのユースケース）のみを定義してください。
    - これにより物理的なファイル構造がシステムの責務の分割を反映し、メンテナンス性を向上させます。
- **依存性の注入 (DI)**:
    - インフラ層、ユースケース、および Presenter のインスタンス化は `app.py` (Composition Root) に集約します。
    - 各クラスは依存するオブジェクトをコンストラクタで受け取るように設計し、`@inject` デコレータを付与してください。
- **Passive View**:
    - 表示層（View）は表示と入力の通知のみを担当し、ビジネスロジックや制御フロー（ダイアログの表示判定など）は Presenter が担当します。

## 7. 禁止事項
- **ワイルドカードインポート禁止**: `from module import *` は絶対に使用しないでください。
- **安全でない関数の使用禁止**: `eval()`, `exec()` など、セキュリティリスクのある関数は原則使用禁止です。
- **不要なコメント**: コードそのもので意図が伝わるように命名を工夫し、実装の「なぜ」を説明する場合を除き、過剰なコメントは控えてください。
