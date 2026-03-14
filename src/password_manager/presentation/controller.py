"""PySide6ベースのネイティブアプリケーションコントローラ (Presentation Layer)."""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, QObject, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from password_manager.presentation.ui import MainWindow
from password_manager.usecases.password_usecase import PasswordUseCase

CLIPBOARD_CLEAR_SECONDS = 15


class AppController(QObject):
    """アプリケーション全体を統括するコントローラ."""

    def __init__(self, app: QApplication, usecase: PasswordUseCase) -> None:
        super().__init__()
        self.app = app
        self._usecase = usecase

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        self.window = MainWindow()
        self.window.update_results(self._usecase.get_all_entries())
        self.window.show()

    def _connect_signals(self) -> None:
        self.window.search_requested.connect(self._on_search_requested)
        self.window.copy_requested.connect(self._on_copy_requested)
        self.window.edit_requested.connect(self._on_edit_requested)
        self.window.delete_requested.connect(self._on_delete_requested)
        self.window.save_requested.connect(self._on_save_requested)

    @Slot(str)
    def _on_search_requested(self, query: str) -> None:
        results = self._usecase.search_entries(query)
        self.window.update_results(results)

    @Slot(int)
    def _on_copy_requested(self, entry_id: int) -> None:
        entry = self._usecase.get_entry(entry_id)
        if not entry:
            return

        success = self._usecase.copy_password(entry_id, clear_after=CLIPBOARD_CLEAR_SECONDS)
        if not success:
            QMessageBox.warning(self.window, "エラー", f"「{entry.site_name}」のパスワードがキーチェーンに見つかりません。")

    @Slot(int)
    def _on_edit_requested(self, entry_id: int) -> None:
        entry = self._usecase.get_entry(entry_id)
        if not entry:
            return
            
        password = self._usecase.get_password(entry_id)
        if password is None:
            password = ""
            
        self.window.show_edit_form(entry_id, entry.site_name, entry.username, password)

    @Slot(int)
    def _on_delete_requested(self, entry_id: int) -> None:
        entry = self._usecase.get_entry(entry_id)
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
            self._usecase.delete_entry(entry_id)
            # 完了後リストを再読み込み
            self._on_search_requested(self.window.search_input.text())

    @Slot(object, str, str, str)
    def _on_save_requested(self, entry_id: int | None, site_name: str, username: str, password: str) -> None:
        self._usecase.save_entry(entry_id, site_name, username, password)
        # 更新・追加したらリストを再読み込み
        self._on_search_requested(self.window.search_input.text())
