# ADR 0010: 子インジェクターを用いたプレゼンテーション層の依存性注入

## Status
Accepted

## Date
2026-05-26

## Context
Flet の UI プレゼンテーション層を担う `MainPage` は、Fletの実行時に動的に生成される `ft.Page` オブジェクトを必要としている。
以前は、Composition Root である `main.py` において、`injector.get` を使って各種ユースケース（`SearchAccountsUseCase` や `CreateAccountUseCase` など）を個別に手動で解決し、それらを `MainPage` のコンストラクタ引数へ明示的に渡してインスタンス化していた。

この設計には以下の課題があった：
- `main.py` に手動で依存解決を行うボイラープレートコードが多く記述され、見通しが悪くなっていた。
- `main.py` で `MainPage` をインスタンス化するためだけに、多数のユースケースクラスを直接インポートする必要があった。
- `MainPage` 自体が DI コンテナ外で手動生成されていたため、依存オブジェクト（ユースケース）が追加・変更されるたびに `main.py` の修正も必要になっていた。

## Decision
**Fletが生成した `page: ft.Page` インスタンスをその場だけバインドした子インジェクター（`child_injector`）を作成し、`MainPage` とその配下のすべての依存関係を DI コンテナから一発で自動解決する構成にする。**

具体的には、`main.py` の `flet_main` 関数内で以下のように実装する：

```python
# Fletが生成したpageオブジェクトを、その場だけバインドした子インジェクターを作成
child_injector = injector.create_child_injector(
    modules=[lambda binder: binder.bind(ft.Page, to=page)]
)

# MainPageとその配下のすべての依存関係（ユースケース群）を自動解決
main_page = child_injector.get(MainPage)
```

## Rationale
- ✅ **Composition Root のクリーン化**: `main.py` に記述されていた手動解決のボイラープレートコードが完全に排除され、不要なユースケースのインポートも不要になった。
- ✅ **DI コンテナによる一括依存解決の徹底**: `MainPage` 自体が DI コンテナ経由で解決されるようになり、将来的に `MainPage` に依存オブジェクトが追加された場合でも `main.py` を修正することなく自動解決されるようになった。
- ✅ **疎結合の維持**: UI プレゼンテーション層とユースケース層の結合関係を DI コンテナが解決するため、クラス設計がより疎結合でテストしやすくなった。

## Consequences

### Positive
- `main.py` のコードが極めて簡潔になり、DI の設定とアプリケーション起動フローという本来の役割に集中させることができた。
- 依存関係の定義変更が `main.py` に波及しなくなるため、モジュールの保守性が向上した。

### Negative
- 親インジェクターから動的オブジェクトを引き継ぐために子インジェクターを作成する（`create_child_injector`）という `injector` ライブラリ特有の概念が導入されるため、DI の仕組みに対する学習コストがわずかに高くなる。
- このデメリットについては、`docs/dependency_injection.md` などの技術解説ドキュメントに仕組みと理由を詳細に記載することで対処する。
