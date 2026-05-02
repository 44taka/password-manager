# Ruff / Pyright 導入時のトラブルシューティング

本プロジェクトに Ruff（リンター・フォーマッター）および Pyright（静的型チェッカー）を導入した際に発生した主なエラーとその修正内容のまとめです。

## Ruff (Linter & Formatter) のエラーと対応

### 1. `E501 Line too long` (行が長すぎる)
* **原因**: コードの行の長さがデフォルトの制限（88文字）を超過していました。特に PySide6 の UI コンポーネントにおける `setStyleSheet()` 内の文字列定義などで頻発しました。
* **対応**:
  1. `pyproject.toml` にて、Ruff の `line-length` を **100** に緩和しました。
  2. それでも 100 文字を超える行（長いエラーメッセージや複雑なスタイル定義など）については、括弧 `()` を使った暗黙の文字列表結や、変数への抽出を行って複数行に分割しました。

### 2. `F841 Local variable is assigned to but never used` (未使用のローカル変数)
* **原因**: `src/password_manager/app.py` において、副作用（依存関係の注入とUIの初期化）目的で `AppController` を取得していましたが、その戻り値を変数 `controller` に代入したまま使用していませんでした。
  ```python
  # 修正前
  controller = injector.get(AppController)
  ```
* **対応**: 変数への代入を削除し、純粋なメソッド呼び出しに変更しました。
  ```python
  # 修正後
  injector.get(AppController)
  ```

### 3. `W293 Blank line contains whitespace` (空白行にスペースが含まれている)
* **原因**: Docstring 内の空行などに余分な空白スペースが混入していました。
* **対応**: `ruff check --fix` コマンドによる自動修正、および一部手動で末尾の空白を削除しました。

### 4. `I001 Import block is un-sorted or un-formatted` / `F401 Unused import` (importの順序・未使用)
* **原因**: import の順序がアルファベット順や標準ライブラリ/サードパーティ/自作モジュールのグループごとに整理されていなかったり、不要なモジュールがインポートされていました。
* **対応**: `ruff check --fix` コマンドにより自動で最適化・削除されました（Ruff は isort と Pyflakes の機能を内包しています）。

---

## Pyright (静的型チェッカー) のエラーと対応

### 1. `keyring.errors` の属性アクセスエラー
* **エラー内容**: `"errors" はモジュール "keyring" の既知の属性ではありません`
* **原因**: Python の動的な性質上、`import keyring` だけでは型チェッカーが `keyring.errors` サブモジュールの存在を静的に認識できないケースがありました。
* **対応**: `src/password_manager/infrastructure/macos_keychain_repository.py` にて、サブモジュールを明示的にインポートしました。
  ```python
  import keyring
  import keyring.errors  # 追加
  ```

### 2. PySide6 UIコンポーネントでの `QLabel` 初期化時の引数エラー
* **エラー内容**: `指定された引数に一致する "__init__" のオーバーロードがありません`
* **原因**: `QLabel("テキスト", styleSheet="...")` のようにキーワード引数 `styleSheet` をコンストラクタで直接渡していましたが、PySide6 の Python バインディング（および Pyright が認識する型スタブ）ではこの形式が許可されていませんでした。
* **対応**: QLabel インスタンスを生成した後に、`setStyleSheet()` メソッドを明示的に呼び出す形に修正しました。
  ```python
  # 修正前
  QLabel("📝 サイト名", styleSheet="color: #8e8e93;")
  
  # 修正後
  label = QLabel("📝 サイト名")
  label.setStyleSheet("color: #8e8e93;")
  ```

### 3. `QGraphicsOpacityEffect` の型推論エラー
* **エラー内容**: `クラス "QGraphicsEffect" の属性 "setOpacity" にアクセスできません`
* **原因**: `self.actions_widget.graphicsEffect()` の戻り値はベースクラスである `QGraphicsEffect` 型として推論されます。しかし、実際に呼び出そうとした `setOpacity()` はサブクラスである `QGraphicsOpacityEffect` 固有のメソッドであったため、型チェッカーが警告を出しました。
* **対応**: `isinstance` を用いてダウンキャスト（型の絞り込み）を行うことで、安全にメソッドを呼び出せるようにしました。
  ```python
  effect = self.actions_widget.graphicsEffect()
  if isinstance(effect, QGraphicsOpacityEffect):
      effect.setOpacity(alpha)
  ```
* **補足**: この修正の過程で、関数内部で行っていた `import PySide6.QtWidgets as QtWidgets` を削除し、ファイル上部のトップレベルで `QGraphicsOpacityEffect` を明示的にインポートするよう整理しました。

### 4. 存在しないモジュールのインポートエラー
* **エラー内容**: `インポート "password_manager.db" を解決できませんでした`
* **原因**: アーキテクチャリファクタリングに伴い `db` モジュールが消滅/移動していましたが、古いインポートパスが `ui.py` の `TYPE_CHECKING` ブロック内に残っていました。
* **対応**: 正しいドメインモデルのパス (`password_manager.domain.models`) をインポートするように修正しました。
