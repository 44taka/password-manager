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

- **Domain層** (`src/password_manager/domain/`)
    - アプリケーションの中枢。外部に依存しない純粋なビジネスエンティティ（`models.py`）と、外部サービスとの境界を定義する抽象インターフェース（`repositories.py` の Protocols）を含みます。
- **UseCase層** (`src/password_manager/usecases/`)
    - アプリケーション固有のビジネスルール（`password_usecase.py`）を含みます。ドメインモデルとリポジトリのインターフェースを使用して、具体的な業務フローをオーケストレーションします。
- **Infrastructure層** (`src/password_manager/infrastructure/`)
    - 外部詳細の実装。SQLite (`sqlite_entry_repository.py`)、macOS Keychain (`macos_keychain_repository.py`)、クリップボード (`mac_clipboard_service.py`) などの具体的な実装を提供します。
- **Presentation層** (`src/password_manager/presentation/`)
    - ユーザーインターフェース（PySide6による `ui.py`）と、UIイベントを制御してユースケースを呼び出す `controller.py` を含んでいます。
- **Composition Root** (`src/password_manager/app.py`)
    - `injector` ライブラリを使用して依存関係を解決（Dependency Injection）し、アプリケーションを組み立てるエントリーポイントです。

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

`PyInstaller` を使用して、Macでそのまま実行可能な `.app` 形式にビルドすることができます。

```bash
# PyInstallerを用いて、アイコン付きの.appをビルド
uv run pyinstaller --windowed --name "Password Manager" --icon=resources/AppIcon.icns src/password_manager/app.py
```

ビルドが成功すると、`dist/Password Manager.app` が生成されます。
これをMacの「アプリケーション (`/Applications`)」フォルダに移動してご使用いただけます。

## テストの実行

`pytest` を用いたユニットテストスイートが同梱されています。

```bash
# テストの実行
uv run pytest tests/ -v
```

## 技術スタック

### ランタイム / ライブラリ

| カテゴリ | ライブラリ | 用途 |
|---|---|---|
| **GUI Framework** | [PySide6](https://pypi.org/project/PySide6/) | Qt6ベースのデスクトップUI（ダークテーマ、リッチなアニメーション） |
| **DI Container** | [injector](https://injector.readthedocs.io/en/latest/) | 依存性注入 (DI) による疎結合なアーキテクチャの実現 |
| **Security** | [keyring](https://github.com/jaraco/keyring) | macOS純正キーチェーンへの安全なアクセス |
| **Search Engine** | [thefuzz](https://github.com/seatgeek/thefuzz) | Python-Levenshtein等を用いた高速なあいまい検索 |
| **Utility** | [pyperclip](https://github.com/asweigart/pyperclip) | クリップボードへのセキュアなコピー操作 |
| **Database** | SQLite (Standard Lib) | メタデータのローカル保存（`sqlite3`） |

### 開発・ビルドツール

| カテゴリ | ツール | 用途 |
|---|---|---|
| **Package Manager** | [uv](https://github.com/astral-sh/uv) | 高速なPythonパッケージ管理、仮想環境構築、ビルド |
| **Testing** | [pytest](https://pytest.org/), [pytest-mock](https://github.com/pytest-dev/pytest-mock) | ユニットテストおよびモックテストの実行 |
| **Packaging** | [PyInstaller](https://pyinstaller.org/), [py2app](https://github.com/ronaldoussoren/py2app) | macOSネイティブアプリ (`.app`) へのパッケージング |

## データ保存先

| データ | 保存先 |
|---|---|
| パスワード本体 | macOS キーチェーン |
| メタデータ（サイト名・ユーザー名等） | `~/.password-manager/entries.db` |
