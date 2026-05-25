# ADR 0009: Flet導入に伴うプレゼンテーション層の再構築

## Status
Accepted

## Date
2026-05-24

## Context
GUIフレームワークを PySide6 から Flet (Flutterベース) に移行した。
これに伴い、Qt固有のイベント駆動やシグナル/スロット構造を前提としていた MVP (Model-View-Presenter) パターン（[ADR 0004](file:///Users/tanakayoshitaka/Projects/password-manager/docs/adr/0004-presentation-layer-mvp-pattern.md)）は不要となり、Fletのコンポーネント指向・宣言的UIに適したシンプルな構成への刷新が必要となった。

## Decision
**プレゼンテーション層の構成を、Presenterを廃止した「Page - Component」構造に簡素化する。**

具体的には以下の通り構成を変更する：

- **Presenterの廃止**: UI制御ロジック（イベントハンドリング）は、View（PageまたはComponent）がユースケースを直接呼び出す形式とする。
- **Themeの廃止**: CSS/QSSに相当するスタイル定義は不要となり、Fletコントロールのプロパティとしてコンポーネント内で直接定義する。
- **ディレクトリ構成の整理**: `presentation/` 配下を以下の2つのカテゴリに分類する。
  - `pages/`: 画面全体の定義、ユースケース呼び出し、画面のステート管理やイベントハンドリング（例: `MainPage`）。
  - `components/`: 画面を構成する再利用可能な最小限のUI部品（例: `AccountCard`, `AccountDialog`）。

```text
src/password_manager/presentation/
├── __init__.py         # MainPage 等を外部に提供する Facade
├── components/         # 再利用可能なUIパーツ
│   ├── account_card.py
│   └── account_dialog.py
└── pages/              # 画面レイアウトとイベントハンドリング
    └── main_page.py
```

## Rationale
- ✅ **フレームワーク親和性の向上**: Fletは宣言的UIの仕組みをとっており、UIコントロールそのものに状態変更ロジックを統合した方がシンプルかつ自然に記述できるため。
- ✅ **開発スピードの向上**: 旧構成での「PresenterとViewを物理的に分離し、初期化時にシグナルを配線する」手間が一切不要になり、簡潔にコードを記述できる。
- ✅ **コード量の削減**: 不要なPresenterの仲介クラスが消え、コード全体のボリュームが大幅に削減される。

## Consequences

### Positive
- ファイル数が減り、どこに何が書かれているかが極めて分かりやすくなった。
- 状態の更新とUIの再描画（`page.update()`）が1箇所で完結するため、データフローのデバッグが容易になった。

### Negative
- 画面が複雑になった場合、ロジックが `pages/`（特に `MainPage`）に集中しやすくなる。
- そのため、ビジネスロジックの漏出を防ぐべく、ロジック自体は適切にユースケース層（UseCase）にカプセル化し、プレゼンテーション層には「イベントを受け取ってユースケースを実行し、結果をUIに反映する」ロジックのみを留める設計を徹底する必要がある。
