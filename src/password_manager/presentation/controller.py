"""PySide6ベースのネイティブアプリケーションコントローラ (Presentation Layer)."""

from __future__ import annotations

from injector import inject
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from password_manager.presentation.ui import MainWindow
from password_manager.usecases.account import (
    CopyLoginIDUseCase,
    CopyPasswordUseCase,
    CreateAccountUseCase,
    DeleteAccountUseCase,
    SearchAccountsUseCase,
    UpdateAccountUseCase,
)

CLIPBOARD_CLEAR_SECONDS = 15


class AppController(QObject):
    """アプリケーション全体を統括するコントローラ."""

    @inject
    def __init__(
        self,
        app: QApplication,
        search_accounts_usecase: SearchAccountsUseCase,
        create_account_usecase: CreateAccountUseCase,
        update_account_usecase: UpdateAccountUseCase,
        delete_account_usecase: DeleteAccountUseCase,
        copy_login_id_usecase: CopyLoginIDUseCase,
        copy_password_usecase: CopyPasswordUseCase,
    ) -> None:
        """AppController を初期化します。."""
        super().__init__()
        self.app = app
        self._search_accounts_usecase = search_accounts_usecase
        self._create_account_usecase = create_account_usecase
        self._update_account_usecase = update_account_usecase
        self._delete_account_usecase = delete_account_usecase
        self._copy_login_id_usecase = copy_login_id_usecase
        self._copy_password_usecase = copy_password_usecase

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """UI を初期化し、メインウィンドウを表示します。."""
        self.window = MainWindow()
        # 初期状態は全件表示
        self.window.update_results(self._search_accounts_usecase.execute())
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
        """検索リクエストを処理し、UI を更新します。."""
        results = self._search_accounts_usecase.execute(query)
        self.window.update_results(results)

    @Slot(int)
    def _on_copy_password_requested(self, account_id: int) -> None:
        """パスワードのコピーリクエストを処理します。."""
        try:
            self._copy_password_usecase.execute(account_id, clear_after=CLIPBOARD_CLEAR_SECONDS)
        except ValueError as e:
            QMessageBox.warning(self.window, "エラー", str(e))

    @Slot(int)
    def _on_copy_username_requested(self, account_id: int) -> None:
        """ログインIDのコピーリクエストを処理します。."""
        try:
            self._copy_login_id_usecase.execute(account_id)
        except ValueError as e:
            QMessageBox.warning(self.window, "エラー", str(e))

    @Slot(int)
    def _on_edit_requested(self, account_id: int) -> None:
        """編集リクエストを処理し、編集フォームを表示します。."""
        # 編集用に現在のデータを取得
        results = self._search_accounts_usecase.execute()
        account = next((a for a in results if int(a.id) == account_id), None)

        if not account:
            return

        self.window.show_edit_form(
            account_id, account.service_name, account.login_id, account.password.get_raw_value()
        )

    @Slot(int)
    def _on_delete_requested(self, account_id: int) -> None:
        """削除リクエストを処理し、確認ダイアログを表示します。."""
        # 削除確認のために名前を取得
        results = self._search_accounts_usecase.execute()
        account = next((a for a in results if int(a.id) == account_id), None)

        if not account:
            return

        reply = QMessageBox.question(
            self.window,
            "削除の確認",
            f"「{account.service_name}」を削除してもよろしいですか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._delete_account_usecase.execute(account_id)
            # 完了後リストを再読み込み
            self._on_search_requested(self.window.search_input.text())

    @Slot(object, str, str, str)
    def _on_save_requested(
        self,
        account_id: int | None,
        service_name: str,
        login_id: str,
        password_str: str,
    ) -> None:
        """保存リクエストを処理し、アカウントを追加または更新します。."""
        try:
            if account_id is None:
                self._create_account_usecase.execute(service_name, login_id, password_str)
            else:
                self._update_account_usecase.execute(
                    account_id, service_name, login_id, password_str
                )
        except Exception as e:
            QMessageBox.warning(
                self.window,
                "保存エラー",
                f"エラーが発生しました。\n\n詳細: {e}",
            )
        finally:
            # 更新・追加したらリストを必ず再読み込み
            self._on_search_requested(self.window.search_input.text())
