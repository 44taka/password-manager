# 🔑 Password Manager

macOS メニューバーに常駐する超軽量パスワードマネージャー。

サイト名を検索するだけで、パスワードがクリップボードにコピーされます。

## 特徴

- 🔍 **あいまい検索** - サイト名の一部を入力するだけで候補が表示される
- ⌨️ **グローバルショートカット** - `Cmd+Shift+P` でどこからでも検索ウィンドウを呼び出せる
- 🔐 **macOS キーチェーン連携** - パスワードは macOS キーチェーンに安全に保存
- 🧹 **クリップボード自動クリア** - コピーから15秒後に自動的にクリップボードをクリア
- 🪶 **超軽量** - メニューバーに常駐するだけで、リソースをほとんど消費しない

## セットアップ

### 前提条件

- macOS
- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

### インストール

```bash
git clone <repository-url>
cd password-manager
uv sync
```

### 初回セットアップ

通知機能を有効にするために、以下のコマンドを実行してください:

```bash
/usr/libexec/PlistBuddy -c 'Add :CFBundleIdentifier string "password-manager"' .venv/bin/Info.plist
```

### 起動

```bash
uv run password-manager
```

メニューバーに 🔑 アイコンが表示されます。

## 使い方

### パスワードの追加

1. メニューバーの 🔑 をクリック
2. **➕ 新規追加** を選択
3. サイト名 → ユーザー名 → パスワード を順に入力

### パスワードの検索・コピー

1. メニューバーの 🔑 → **🔍 パスワードを検索**（または `Cmd+Shift+P`）
2. サイト名の一部を入力して **検索**
3. パスワードがクリップボードにコピーされる（15秒後に自動クリア）

### 権限設定

グローバルショートカット（`Cmd+Shift+P`）を使用するには、アクセシビリティ権限が必要です:

**システム設定 > プライバシーとセキュリティ > アクセシビリティ** で、使用しているターミナルアプリに権限を付与してください。

## 技術スタック

| ライブラリ | 用途 |
|---|---|
| [rumps](https://github.com/jaredks/rumps) | メニューバーアプリ基盤 |
| [keyring](https://github.com/jaraco/keyring) | macOS キーチェーンアクセス |
| [thefuzz](https://github.com/seatgeek/thefuzz) | あいまい検索 |
| [pyperclip](https://github.com/asweigart/pyperclip) | クリップボード操作 |
| [pynput](https://github.com/moses-palmer/pynput) | グローバルショートカット |

## テスト

```bash
uv run pytest tests/ -v
```

## データ保存先

| データ | 保存先 |
|---|---|
| パスワード本体 | macOS キーチェーン |
| メタデータ（サイト名等） | `~/.password-manager/entries.db` |
