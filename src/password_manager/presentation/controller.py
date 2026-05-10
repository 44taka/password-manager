"""PySide6ベースのネイティブアプリケーションコントローラ (Presentation Layer)."""

from __future__ import annotations

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from password_manager.presentation.ui import MainWindow
from password_manager.usecases.password_usecase import PasswordUseCase

CLIPBOARD_CLEAR_SECONDS = 15


class AppController(QObject):
    """アプリケーション全体を統括するコントローラ."""

    def __init__(self, app: QApplication, usecase: PasswordUseCase) -> None:
        """AppController を初期化します。.

        Args:
            app: QApplication インスタンス。
            usecase: ビジネスロジックを提供するユースケース。
        """
        super().__init__()
        self.app = app
        self._usecase = usecase

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """UI を初期化し、メインウィンドウを表示します。."""
        self.window = MainWindow()
        self.window.update_results(self._usecase.get_all_entries())
        self.window.show()

    def _connect_signals(self) -> None:
        """UI からのシグナルをコントローラーのメソッドに接続します。."""
        self.window.search_requested.connect(self._on_search_requested)
        self.window.copy_password_requested.connect(self._on_copy_password_requested)
        self.window.copy_username_requested.connect(self._on_copy_username_requested)
        self.window.edit_requested.connect(self._on_edit_requested)
        self.window.delete_requested.connect(self._on_delete_requested)
        self.window.save_requested.connect(self._on_save_requested)

    @Slot(str)
    def _on_search_requested(self, query: str) -> None:
        """検索リクエストを処理し、UI を更新します。.

        Args:
            query: 検索クエリ文字列。
        """
        results = self._usecase.search_entries(query)
        self.window.update_results(results)

    @Slot(int)
    def _on_copy_password_requested(self, entry_id: int) -> None:
        """パスワードのコピーリクエストを処理します。.

        Args:
            entry_id: 対象のエントリ ID。
        """
        entry = self._usecase.get_entry(entry_id)
        if not entry:
            return

        success = self._usecase.copy_password(entry_id, clear_after=CLIPBOARD_CLEAR_SECONDS)
        if not success:
            msg = f"「{entry.site_name}」のパスワードがキーチェーンに見つかりません。"
            QMessageBox.warning(self.window, "エラー", msg)

    @Slot(int)
    def _on_copy_username_requested(self, entry_id: int) -> None:
        """ユーザー名のコピーリクエストを処理します。.

        Args:
            entry_id: 対象のエントリ ID。
        """
        entry = self._usecase.get_entry(entry_id)
        if not entry:
            return

        success = self._usecase.copy_username(entry_id)
        if not success:
            msg = f"「{entry.site_name}」のユーザー名が見つかりません。"
            QMessageBox.warning(self.window, "エラー", msg)

    @Slot(int)
    def _on_edit_requested(self, entry_id: int) -> None:
        """編集リクエストを処理し、編集フォームを表示します。.

        Args:
            entry_id: 対象のエントリ ID。
        """
        entry = self._usecase.get_entry(entry_id)
        if not entry:
            return

        password = self._usecase.get_password(entry_id)
        if password is None:
            password = ""

        self.window.show_edit_form(entry_id, entry.site_name, entry.username, password)

    @Slot(int)
    def _on_delete_requested(self, entry_id: int) -> None:
        """削除リクエストを処理し、確認ダイアログを表示します。.

        Args:
            entry_id: 対象のエントリ ID。
        """
        entry = self._usecase.get_entry(entry_id)
        if not entry:
            return

        reply = QMessageBox.question(
            self.window,
            "削除の確認",
            f"「{entry.site_name}」を削除してもよろしいですか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._usecase.delete_entry(entry_id)
            # 完了後リストを再読み込み
            self._on_search_requested(self.window.search_input.text())

    @Slot(object, str, str, str)
    def _on_save_requested(
        self,
        entry_id: int | None,
        site_name: str,
        username: str,
        password: str,
    ) -> None:
        """保存リクエストを処理し、エントリを追加または更新します。.

        Args:
            entry_id: 更新対象の ID。新規追加の場合は None。
            site_name: サイト名。
            username: ユーザー名。
            password: パスワード。
        """
        try:
            self._usecase.save_entry(entry_id, site_name, username, password)
        except Exception as e:
            QMessageBox.warning(
                self.window,
                "保存エラー",
                f"サイト情報は保存されましたが、パスワードの保存に失敗しました。\n\n詳細: {e}",
            )
        finally:
            # 更新・追加したらリストを必ず再読み込み
            self._on_search_requested(self.window.search_input.text())
