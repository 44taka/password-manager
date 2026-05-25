# ADR 0004: プレゼンテーション層の MVP パターン採用とコンポーネント分割

## Status
Superseded by [ADR 0009](file:///Users/tanakayoshitaka/Projects/password-manager/docs/adr/0009-presentation-layer-flet-integration.md) (Flet導入に伴うプレゼンテーション層の再構築により非推奨)

## Date
2026-05-11

## Context
現在のプレゼンテーション層は `ui.py` (約 570 行) と `controller.py` (約 150 行) で構成されているが、以下の課題がある：

- `ui.py` にメインウィンドウ、カード型ウィジェット、ダイアログの全てのロジックが含まれており、肥大化している。
- `AppController` が全てのユースケースと UI イベントを管理する「Fat Controller」になっている。
- UI のスタイル定義（CSS）が Python コード内に埋もれており、デザインの変更がロジックに影響を与えやすい。

## Decision
**プレゼンテーション層を MVP (Model-View-Presenter) パターンに基づいて再構成し、ディレクトリ単位で役割を分離する。**

具体的には以下の構成とする：
- **View の分離**: `presentation/views/` に UI 部品を分割し、View は「Passive View（受動的な表示）」に徹する。表示ロジックを持たず、イベントをシグナルとして Presenter に通知する。
- **Presenter の分割**: `presentation/presenters/` に制御ロジックを分割する。AppController を廃止し、1機能1クラスを原則として `Search`, `Creation`, `Update`, `Deletion`, `Clipboard` の各 Presenter に分割する。**各パッケージの `__init__.py` は Facade として機能させ、インポートを簡潔にする。**
- **Theme の独立**: `presentation/theme/` に QSS (CSS) やカラーパレットなどのスタイル定義を抽出し、デザインシステムとして管理する。

## Rationale
- ✅ **単一責任原則の徹底**: UI の構築（View）、表示の制御（Presenter）、デザイン定義（Theme）が物理的に分離される。
- ✅ **テストの容易性**: Presenter が View のインターフェース（あるいはシグナル）のみに依存するため、UI を表示せずに Presenter のロジックをテストしやすくなる。
- ✅ **メンテナンス性の向上**: UI の構造（HTML/Qt構造）を変えたい時と、ボタンを押した時の動き（Logic）を変えたい時の作業箇所が明確になる。
- ✅ **コードのカタログ化**: `views/` を見れば画面を構成する部品が分かり、`presenters/` を見れば画面で何ができるかが明確になる。

## Consequences

### Positive
- 各レイヤーの責務がクリーンになり、ドメイン層やユースケース層の疎結合さと整合性が取れる。
- スタイルの変更（Theme）がロジックに影響を与えないため、デザインの微調整が容易になる。

### Negative
- ファイル数が増加し、DI（依存性注入）の設定箇所が増える。
- シグナル/スロットの配線を Presenter で行う必要があるため、初期化コードが若干増える。

## Example
```text
src/password_manager/presentation/
├── views/              # UI部品 (Passive View)
│   ├── main_window.py
│   ├── account_card.py
│   ├── account_dialog.py
│   └── action_button.py
├── presenters/         # 制御ロジック (1機能 1クラス)
│   ├── search_presenter.py
│   ├── account_creation_presenter.py
│   ├── account_update_presenter.py
│   ├── account_deletion_presenter.py
│   └── clipboard_presenter.py
└── theme/              # デザインシステム
    └── styles.py       # QSS (CSS) 定義
```
