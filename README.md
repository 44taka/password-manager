# 🔑 Password Manager

macOS向けの美しく軽量なデスクトップネイティブ・パスワードマネージャー。
PySide6を用いた角丸ダークテーマのカード型UIを提供し、パスワードはmacOS純正のキーチェーンへ安全に保存されます。

## 特徴

- 🔍 **あいまい検索** - サイト名の一部を入力するだけで高速に絞り込み
- 🔐 **macOS キーチェーン連携** - パスワード本体はmacOSキーチェーン(`keyring`)に安全に保存
- 🧹 **クリップボード自動クリア** - コピー操作から15秒後に自動的にクリップボードをクリア
- 🎨 **リッチなダークUI** - 角丸のカード型リスト、ホバーエフェクト、マテリアルデザイン風ダイアログ

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

| ライブラリ | 用途 |
|---|---|
| [PySide6](https://pypi.org/project/PySide6/) | メインのGUI機能（Qt6ベースのダークテーマ・リッチUI） |
| [keyring](https://github.com/jaraco/keyring) | macOS キーチェーンアクセス |
| [thefuzz](https://github.com/seatgeek/thefuzz) | あいまい検索 |
| [pyperclip](https://github.com/asweigart/pyperclip) | クリップボード操作 |
| [PyInstaller](https://pyinstaller.org/en/stable/) | macOSネイティブアプリ(`.app`)へのパッケージング |

## データ保存先

| データ | 保存先 |
|---|---|
| パスワード本体 | macOS キーチェーン |
| メタデータ（サイト名・ユーザー名等） | `~/.password-manager/entries.db` |
