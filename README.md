# 🔑 Password Manager

macOS向けの美しく軽量なデスクトップネイティブ・パスワードマネージャー。
PySide6を用いた角丸ダークテーマのカード型UIを提供し、パスワードはmacOS純正のキーチェーンへ安全に保存されます。

## 特徴

- 🔍 **あいまい検索** - サイト名の一部を入力するだけで高速に絞り込み
- 🔐 **macOS キーチェーン連携** - パスワード本体はmacOSキーチェーン(`keyring`)に安全に保存
- 🧹 **クリップボード自動クリア** - コピー操作から15秒後に自動的にクリップボードをクリア
- 🎨 **リッチなダークUI** - 角丸のカード型リスト、ホバーエフェクト、マテリアルデザイン風ダイアログ
- 🧅 **オニオンアーキテクチャ** - Domain, UseCases, Infrastructure, Presentation の各層が疎結合になっており、高いテスト容易性と拡張性を実現

## アーキテクチャ

本プロジェクトは **オニオンアーキテクチャ (Onion Architecture)** に基づいて設計されており、各関心が明確に分離されています。

### レイヤー・プロジェクト構造

- **Domain層** (`src/password_manager/domain/account/`)
    - アプリケーションの中枢。集約（`Account`）、値オブジェクト（`Password`, `AccountID`）、およびリポジトリのインターフェースを含みます。
- **UseCase層** (`src/password_manager/usecases/account/`)
    - アプリケーション固有のビジネスルール。1つのユースケースを1つのクラスとして定義し、単一責任原則を徹底しています（例: `SearchAccountsUseCase`, `CopyPasswordUseCase`）。
- **Infrastructure層** (`src/password_manager/infrastructure/`)
    - 外部詳細の実装。SQLiteへの永続化（`sqlite_account_store.py`）、macOS Keychain連携（`macos_keychain_store.py`）、およびそれらを統合する `unified_account_repository.py` を含みます。
- **Presentation層** (`src/password_manager/presentation/`)
    - ユーザーインターフェースと表示制御を担当。MVP パターンを採用しています。
    - `views/`: 純粋な UI 部品（MainWindow, AccountCard 等）。表示に専念し、イベントはシグナルとして発行します。
    - `presenters/`: 表示制御ロジック。View のシグナルを受けてユースケースを呼び出し、結果を View に反映します。
    - `theme/`: QSS (CSS) によるスタイル定義やカラーパレットのデザインシステムを管理します。
- **Composition Root** (`src/password_manager/app.py`)
    - `injector` ライブラリを使用して依存関係を解決（Dependency Injection）し、アプリケーションを組み立てるエントリーポイントです。

## コーディング規約

本プロジェクトでは、保守性と可読性を高めるために以下の規約を採用しています。

- **1クラス・1ファイル方針**: 原則として 1 つのファイルには 1 つのクラスのみを定義します。これにより関心の分離を物理的に強制します。
- **Facade (ファサード) パターン**: 各パッケージの `__init__.py` で主要なクラスを Re-export しています。
- **堅牢なエラーハンドリング**: レイヤーごとに定義された例外クラスと、Keyring/SQLite 間の補償トランザクションにより、データ不整合を防止します。
- **包括的なロギング**: `~/Library/Logs/PasswordManager/` に日付付きのログを出力し、異常時の調査を容易にします。また、Sentry との統合もサポートしています。

### 設計の意思決定 (ADR)

プロジェクトの重要な設計判断（リポジトリの構成やユースケースの分割方針など）は、`docs/adr/` 配下に **ADR (Architecture Decision Records)** として記録されています。開発時にはこれらを参照してください。

## アプリの起動とパッケージング

このプロジェクトは、Pythonパッケージマネージャーである `uv` を使用して構築されています。

### 1. 開発環境での起動

```bash
# プロジェクトディレクトリへ移動
cd /Users/<username>/Projects/password-manager

# 依存関係のインストール（初回のみ）
uv sync

# アプリの起動
uv run password-manager
```

### 2. .app としてのビルド（パッケージング）

プロジェクトには、ビルド、コード署名、バージョン更新を自動化する `Makefile` が用意されています。

```bash
# アプリをビルドし、dist/Password Manager.app を生成
make build
```

ビルドが成功すると、`dist/Password Manager.app` が生成されます。これをMacの「アプリケーション (`/Applications`)」フォルダに移動してご使用いただけます。

## テストの実行

`pytest` を用いたユニットテストスイートが同梱されています。
テストコードもプロジェクト本体のオニオンアーキテクチャに合わせて `tests/password_manager/` 配下（`domain`, `usecases`, `infrastructure` など）に分割・整理されています。

```bash
# 全てのテストを実行
make test

# 特定のテストのみ実行
uv run pytest tests/path/to/test_file.py
```

## 技術スタック

### ランタイム / ライブラリ

| カテゴリ | ライブラリ | 用途 |
|---|---|---|
| **GUI Framework** | [PySide6](https://pypi.org/project/PySide6/) | Qt6ベースのデスクトップUI（ダークテーマ、リッチなアニメーション） |
| **DI Container** | [injector](https://injector.readthedocs.io/en/latest/) | 依存性注入 (DI) による疎結合なアーキテクチャの実現 |
| **Security** | [keyring](https://github.com/jaraco/keyring) | macOS純正キーチェーンへの安全なアクセス |
| **Monitoring** | [sentry-sdk](https://sentry.io/) | エラーの自動検知とバックグラウンドトラッキング |
| **Search Engine** | difflib (Standard Lib) | 標準ライブラリを用いた高速なあいまい検索・タイポ吸収 |
| **Utility** | [pyperclip](https://github.com/asweigart/pyperclip) | クリップボードへのセキュアなコピー操作 |
| **Database** | SQLite (Standard Lib) | メタデータのローカル保存（`sqlite3`） |

### 開発・ビルドツール

| カテゴリ | ツール | 用途 |
|---|---|---|
| **Package Manager** | [uv](https://github.com/astral-sh/uv) | 高速なPythonパッケージ管理、仮想環境構築、ビルド |
| **Testing** | [pytest](https://pytest.org/), [pytest-mock](https://github.com/pytest-dev/pytest-mock) | ユニットテストおよびモックテストの実行 |
| **Packaging** | [PyInstaller](https://pyinstaller.org/), [py2app](https://github.com/ronaldoussoren/py2app) | macOSネイティブアプリ (`.app`) へのパッケージング |

## 💡 注意事項

- **データベースの互換性**: バージョン 0.5.0 (UUID への移行) 以降、以前のバージョンで作成された `passwords.db` との互換性はありません。アップデート後に起動エラーが発生する場合は、`rm ~/.password_manager/passwords.db` を実行してデータベースをリセットしてください。

## データ保存先

| データ | 保存先 |
|---|---|
| パスワード本体 | macOS キーチェーン |
| メタデータ（サイト名・ユーザー名等） | `~/.password_manager/passwords.db` |
