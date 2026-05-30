# ADR 0011: Fletイベントハンドラーにおける型チェックエラー回避方針

## Status
Accepted

## Date
2026-05-29

## Context
Fletの各UIコントロール（例: `ft.IconButton` や `ft.FilledButton`）の `on_click` プロパティなどには、 `ControlEventHandler[T]` 型のハンドラーが期待されている。
しかし、Flet側のジェネリクス型定義において、 `Event[EventControlType]` の型引数 `EventControlType` が不変（invariant）として実装されているため、Pyright等の静的型チェッカー（`make typecheck` で実行）によって以下のような型不一致エラーが頻発する課題が生じた：

```
Argument (self: Self@AccountDialog, e: Event[BaseControl]) -> None is not assignable to parameter on_click with type (() -> Any) | ((Event[IconButton]) -> Any) | None
```

これは、より広範な `Event[BaseControl]` (＝ `ft.ControlEvent`) を受け取るコールバック関数を、 `Event[IconButton]` のような具体的な型を受け取る場所に代入できないという Python の型システムの制約に起因する。

また、型エラーを回避するために引数を `Any` 型にすると、プロジェクトで導入されている Ruff の型アノテーションルール（`ANN401`: Dynamically typed expressions are disallowed）に違反して Lint エラーが発生するため、これらを考慮した解決策が必要である。

## Decision
**Fletのイベントハンドラーの静的型チェックとLintエラーを両立して回避するために、以下の「二段構えの運用ルール」を採用する。**

1. **基本方針（対策A）: イベント引数 `e` が不要な場合は、メソッドを「引数なし」で定義し、割り当て時にラムダ式でラップする。**
   メソッド内での処理においてイベント情報（`e.control` やマウス座標など）を利用しない場合は、コールバック用メソッドを引数なし（`self` のみ）で定義する。そして `on_click` へのバインド時に `lambda _: self.my_handler()` でラップして渡す。これにより型チェッカーと Ruff の両方に適合する。
   - 例:
     ```python
     # 定義
     def _toggle_password(self) -> None:
         self.password_input.password = not self.password_input.password

     # バインド
     self.password_toggle_btn = ft.IconButton(
         on_click=lambda _: self._toggle_password(),
     )
     ```

2. **例外方針（対策B）: イベントオブジェクト `e` の情報が必須な場合は、具体的なコントロール型を指定した `Event[T]` をアノテーションに指定する。**
   メソッド内でクリックされたコントロール（`e.control`）等の情報をどうしても使用する必要がある場合は、 `ft.ControlEvent` の代わりに `flet.controls.control_event.Event` をインポートし、具体的なコントロール型でアノテーションする。
   - 例:
     ```python
     from flet.controls.control_event import Event

     # 定義
     def _on_copy_username_clicked(self, e: Event[ft.IconButton]) -> None:
         control = e.control  # 自動的に ft.IconButton として安全に推論される
         self._animate_success_icon(control)

     # バインド (直接渡しても Pyright エラーにならない)
     self.btn = ft.IconButton(
         on_click=self._on_copy_username_clicked,
     )
     ```

3. **禁止方針: `Any` を使った型不一致の回避は行わない（Ruff ANN401 の遵守）。**
   `e: Any` などのアノテーションによる型チェックの回避は行わない。

## Rationale
- ✅ **Pyright 型チェックの完全通過**: Fletライブラリ内の不変性制約を回避して、型安全なコードを維持できる。
- ✅ **Ruff Lint ルールの順守**: `Any` の使用を禁止する `ANN401` ルールを無効化せずに、クリーンな型アノテーションを維持できる。
- ✅ **コードの再利用性の向上**: イベント引数 `e` が不要なメソッドを引数なしで定義することで、イベントトリガーの種類に依存せずメソッドを使い回すことができる。
- ✅ **意図の明確化**: イベント情報に依存しているメソッド（対策B）と依存していないメソッド（対策A）がシグネチャ上で明確に区別されるため、コードの可読性が向上する。

## Consequences

### Positive
- `make check` (Ruff & Pyright) の実行時に、Fletイベントハンドラー周りでの型チェックエラーが完全に防止される。
- 設計ルールが明確になり、プロジェクト全体で一貫した UI コードの記述スタイルが維持される。

### Negative
- イベント引数を不要とするために、バインド側に `lambda _: ...` の記述がわずかに増える。
- イベントオブジェクトを使用する際、 `flet.controls.control_event.Event` をインポートして詳細にアノテーションするという Python 固有の記述が必要になる。
