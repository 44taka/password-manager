"""PySide6ベースのネイティブアプリケーション."""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt, QObject, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from password_manager.clipboard import copy_to_clipboard
from password_manager.db import EntryStore
from password_manager.keychain import KeychainManager
from password_manager.search import fuzzy_search
from password_manager.ui import MainWindow

CLIPBOARD_CLEAR_SECONDS = 15


class AppController(QObject):
    """アプリケーション全体を統括するコントローラ."""

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self._store = EntryStore()
        self._keychain = KeychainManager()

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        self.window = MainWindow()
        self.window.update_results(self._store.list_all())
        self.window.show()

    def _connect_signals(self) -> None:
        self.window.search_requested.connect(self._on_search_requested)
        self.window.copy_requested.connect(self._on_copy_requested)
        self.window.edit_requested.connect(self._on_edit_requested)
        self.window.delete_requested.connect(self._on_delete_requested)
        self.window.save_requested.connect(self._on_save_requested)

    @Slot(str)
    def _on_search_requested(self, query: str) -> None:
        entries = self._store.list_all()
        if not query:
            self.window.update_results(entries)
            return

        results = fuzzy_search(query, entries)
        self.window.update_results(results)

    @Slot(int)
    def _on_copy_requested(self, entry_id: int) -> None:
        entry = self._store.get(entry_id)
        if not entry:
            return

        password = self._keychain.get(entry_id)
        if password is None:
            QMessageBox.warning(self.window, "エラー", f"「{entry.site_name}」のパスワードがキーチェーンに見つかりません。")
            return

        copy_to_clipboard(password, clear_after=CLIPBOARD_CLEAR_SECONDS)

    @Slot(int)
    def _on_edit_requested(self, entry_id: int) -> None:
        entry = self._store.get(entry_id)
        if not entry:
            return
            
        password = self._keychain.get(entry_id)
        if password is None:
            password = ""
            
        self.window.show_edit_form(entry_id, entry.site_name, entry.username, password)

    @Slot(int)
    def _on_delete_requested(self, entry_id: int) -> None:
        entry = self._store.get(entry_id)
        if not entry:
            return
            
        reply = QMessageBox.question(
            self.window,
            "削除の確認",
            f"「{entry.site_name}」を削除してもよろしいですか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._store.delete(entry_id)
            self._keychain.delete(entry_id)
            # 完了後リストを再読み込み
            self._on_search_requested(self.window.search_input.text())

    @Slot(object, str, str, str)
    def _on_save_requested(self, entry_id: int | None, site_name: str, username: str, password: str) -> None:
        if entry_id is None:
            new_id = self._store.add(site_name, username)
            self._keychain.save(new_id, password)
        else:
            self._store.update(entry_id, site_name=site_name, username=username)
            self._keychain.save(entry_id, password)
            
        # 更新・追加したらリストを再読み込み
        self._on_search_requested(self.window.search_input.text())


from pathlib import Path
from PySide6.QtGui import QIcon

def main() -> None:
    os.environ["QT_MAC_WANTS_LAYER"] = "1"
    
    app = QApplication(sys.argv)
    
    base_dir = Path(__file__).resolve().parent.parent.parent
    icon_path = base_dir / "resources" / "AppIcon.icns"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    controller = AppController(app)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
