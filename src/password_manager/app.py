"""メニューバーアプリのメイン - rumps ベースの macOS メニューバーアプリ."""

from __future__ import annotations

import os
import subprocess
import sys

import AppKit
import rumps

from password_manager.clipboard import copy_to_clipboard
from password_manager.db import EntryStore
from password_manager.hotkey import HotkeyManager
from password_manager.keychain import KeychainManager
from password_manager.search import fuzzy_search

# クリップボード自動クリアまでの秒数
CLIPBOARD_CLEAR_SECONDS = 15


def _safe_notification(title: str, subtitle: str, message: str) -> None:
    """rumps.notification の安全なラッパー. Info.plist がない場合はスキップする."""
    try:
        rumps.notification(title=title, subtitle=subtitle, message=message)
    except RuntimeError:
        # Info.plist が見つからない場合は無視
        pass


def _ensure_info_plist() -> None:
    """通知に必要な Info.plist を自動生成する."""
    venv_bin = os.path.dirname(sys.executable)
    plist_path = os.path.join(venv_bin, "Info.plist")
    if not os.path.exists(plist_path):
        try:
            subprocess.run(
                [
                    "/usr/libexec/PlistBuddy",
                    "-c",
                    'Add :CFBundleIdentifier string "password-manager"',
                    plist_path,
                ],
                check=True,
                capture_output=True,
            )
        except Exception:
            pass


class PasswordManagerApp(rumps.App):
    """macOS メニューバー常駐型パスワードマネージャー."""

    def __init__(self) -> None:
        super().__init__(
            name="Password Manager",
            icon=None,
            title="🔑",
        )
        self._store = EntryStore()
        self._keychain = KeychainManager()
        self._hotkey = HotkeyManager()

        # メニュー構成
        self.menu = [
            rumps.MenuItem("🔍 パスワードを検索", callback=self._on_search),
            rumps.MenuItem("➕ 新規追加", callback=self._on_add),
            rumps.MenuItem("📋 一覧表示", callback=self._on_list),
            None,  # セパレーター
            rumps.MenuItem("🗑️ エントリ削除", callback=self._on_delete),
        ]

    @staticmethod
    def _activate_app() -> None:
        """ウィンドウ表示前にアプリを一時的にフォアグラウンドに切り替える.

        Regular に切替 → アクティベート → 即座に Accessory に戻すことで
        Dock にアイコンを表示させずにウィンドウにフォーカスを当てる。
        """
        app = AppKit.NSApp
        app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
        app.activateIgnoringOtherApps_(True)
        app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)

    def _setup_hotkey(self) -> None:
        """グローバルホットキーを登録して開始する."""
        self._hotkey.register(self._trigger_search)
        try:
            self._hotkey.start()
        except Exception:
            _safe_notification(
                title="Password Manager",
                subtitle="ホットキーの登録に失敗しました",
                message="システム設定 > プライバシーとセキュリティ > アクセシビリティ で権限を付与してください。",
            )

    def _trigger_search(self) -> None:
        """ホットキーから検索ウィンドウを呼び出す（スレッドセーフ）."""
        # rumps はメインスレッドで動くため、timer で呼び出す
        rumps.Timer(self._on_search, 0.1).start()

    def _on_search(self, sender: rumps.MenuItem | None = None) -> None:
        """検索ウィンドウを表示してパスワードをコピーする."""
        self._activate_app()
        window = rumps.Window(
            title="パスワード検索",
            message="サイト名またはユーザー名の一部を入力してください:",
            default_text="",
            ok="検索",
            cancel="キャンセル",
            dimensions=(300, 24),
        )
        response = window.run()

        if not response.clicked:
            return

        query = response.text.strip()
        if not query:
            return

        entries = self._store.list_all()
        results = fuzzy_search(query, entries)

        if not results:
            _safe_notification(
                title="Password Manager",
                subtitle="検索結果",
                message=f"「{query}」に一致するエントリが見つかりませんでした。",
            )
            return

        # 候補が1つなら即コピー、複数なら選択肢を表示
        if len(results) == 1:
            self._copy_password(results[0].id, results[0].site_name)
        else:
            self._show_selection(results)

    def _show_selection(self, entries: list) -> None:
        """複数候補から選択するウィンドウを表示する."""
        choices = [
            f"{i + 1}. {e.site_name} ({e.username})"
            for i, e in enumerate(entries[:10])  # 最大10件
        ]
        message = "\n".join(choices)

        window = rumps.Window(
            title="候補を選択",
            message=f"番号を入力してください:\n\n{message}",
            default_text="1",
            ok="選択",
            cancel="キャンセル",
            dimensions=(300, 24),
        )
        response = window.run()

        if not response.clicked:
            return

        try:
            idx = int(response.text.strip()) - 1
            if 0 <= idx < len(entries[:10]):
                entry = entries[idx]
                self._copy_password(entry.id, entry.site_name)
            else:
                _safe_notification(
                    title="Password Manager",
                    subtitle="エラー",
                    message="無効な番号です。",
                )
        except ValueError:
            _safe_notification(
                title="Password Manager",
                subtitle="エラー",
                message="数字を入力してください。",
            )

    def _copy_password(self, entry_id: int, site_name: str) -> None:
        """パスワードをクリップボードにコピーする."""
        password = self._keychain.get(entry_id)
        if password is None:
            _safe_notification(
                title="Password Manager",
                subtitle="エラー",
                message=f"「{site_name}」のパスワードがキーチェーンに見つかりません。",
            )
            return

        copy_to_clipboard(password, clear_after=CLIPBOARD_CLEAR_SECONDS)
        _safe_notification(
            title="Password Manager",
            subtitle="コピー完了",
            message=f"「{site_name}」のパスワードをコピーしました。{CLIPBOARD_CLEAR_SECONDS}秒後に自動クリアされます。",
        )

    def _on_add(self, sender: rumps.MenuItem) -> None:
        """新規エントリ追加ダイアログ."""
        self._activate_app()

        # サイト名の入力
        site_window = rumps.Window(
            title="新規追加 (1/3)",
            message="サイト名を入力してください:",
            default_text="",
            ok="次へ",
            cancel="キャンセル",
            dimensions=(300, 24),
        )
        site_response = site_window.run()
        if not site_response.clicked or not site_response.text.strip():
            return

        site_name = site_response.text.strip()

        # ユーザー名の入力
        user_window = rumps.Window(
            title="新規追加 (2/3)",
            message=f"「{site_name}」のユーザー名を入力してください:",
            default_text="",
            ok="次へ",
            cancel="キャンセル",
            dimensions=(300, 24),
        )
        user_response = user_window.run()
        if not user_response.clicked or not user_response.text.strip():
            return

        username = user_response.text.strip()

        # パスワードの入力
        pw_window = rumps.Window(
            title="新規追加 (3/3)",
            message=f"「{site_name}」のパスワードを入力してください:",
            default_text="",
            ok="保存",
            cancel="キャンセル",
            dimensions=(300, 24),
        )
        pw_response = pw_window.run()
        if not pw_response.clicked or not pw_response.text.strip():
            return

        password = pw_response.text.strip()

        # DBとキーチェーンに保存
        entry_id = self._store.add(site_name, username)
        self._keychain.save(entry_id, password)

        _safe_notification(
            title="Password Manager",
            subtitle="追加完了",
            message=f"「{site_name}」({username}) を保存しました。",
        )

    def _on_list(self, sender: rumps.MenuItem) -> None:
        """登録済みエントリの一覧を表示する."""
        entries = self._store.list_all()

        if not entries:
            _safe_notification(
                title="Password Manager",
                subtitle="一覧",
                message="登録されているエントリはありません。",
            )
            return

        lines = [
            f"• {e.site_name} ({e.username})"
            for e in entries[:20]  # 最大20件
        ]
        message = "\n".join(lines)
        if len(entries) > 20:
            message += f"\n... 他 {len(entries) - 20} 件"

        self._activate_app()
        window = rumps.Window(
            title="登録エントリ一覧",
            message=message,
            ok="閉じる",
            dimensions=(0, 0),
        )
        window.run()

    def _on_delete(self, sender: rumps.MenuItem) -> None:
        """エントリを削除する."""
        entries = self._store.list_all()

        if not entries:
            _safe_notification(
                title="Password Manager",
                subtitle="削除",
                message="削除するエントリがありません。",
            )
            return

        choices = [
            f"{i + 1}. {e.site_name} ({e.username})"
            for i, e in enumerate(entries[:20])
        ]
        message = "\n".join(choices)

        self._activate_app()
        window = rumps.Window(
            title="エントリ削除",
            message=f"削除する番号を入力してください:\n\n{message}",
            default_text="",
            ok="削除",
            cancel="キャンセル",
            dimensions=(300, 24),
        )
        response = window.run()

        if not response.clicked:
            return

        try:
            idx = int(response.text.strip()) - 1
            if 0 <= idx < len(entries[:20]):
                entry = entries[idx]
                # DBとキーチェーンから削除
                self._store.delete(entry.id)
                self._keychain.delete(entry.id)
                _safe_notification(
                    title="Password Manager",
                    subtitle="削除完了",
                    message=f"「{entry.site_name}」を削除しました。",
                )
            else:
                _safe_notification(
                    title="Password Manager",
                    subtitle="エラー",
                    message="無効な番号です。",
                )
        except ValueError:
            _safe_notification(
                title="Password Manager",
                subtitle="エラー",
                message="数字を入力してください。",
            )


def main() -> None:
    """アプリケーションのエントリポイント."""
    _ensure_info_plist()
    app = PasswordManagerApp()
    app._setup_hotkey()
    app.run()


if __name__ == "__main__":
    main()
