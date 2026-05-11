"""アカウントの作成・更新・削除を制御する Presenter."""

from __future__ import annotations

from injector import inject
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox

from password_manager.presentation.views.main_window import MainWindow
from password_manager.usecases.account.create_account import CreateAccountUseCase
from password_manager.usecases.account.delete_account import DeleteAccountUseCase
from password_manager.usecases.account.search_accounts import SearchAccountsUseCase
from password_manager.usecases.account.update_account import UpdateAccountUseCase


class AccountPresenter(QObject):
    """アカウントのデータ操作リクエストを処理する担当."""

    @inject
    def __init__(
        self,
        view: MainWindow,
        create_usecase: CreateAccountUseCase,
        update_usecase: UpdateAccountUseCase,
        delete_usecase: DeleteAccountUseCase,
        search_usecase: SearchAccountsUseCase,
    ) -> None:
        """AccountPresenter を初期化します。.

        Args:
            view: 操作対象のメインウィンドウ。
            create_usecase: 作成用ユースケース。
            update_usecase: 更新用ユースケース。
            delete_usecase: 削除用ユースケース。
            search_usecase: 更新後の再検索用ユースケース。
        """
        super().__init__()
        self._view = view
        self._create_usecase = create_usecase
        self._update_usecase = update_usecase
        self._delete_usecase = delete_usecase
        self._search_usecase = search_usecase

        # View のシグナルを接続
        self._view.edit_requested.connect(self.handle_edit_request)
        self._view.delete_requested.connect(self.handle_delete_request)
        self._view.save_requested.connect(self.handle_save_request)

    @Slot(int)
    def handle_edit_request(self, account_id: int) -> None:
        """編集フォームの表示リクエストを処理します。.

        Args:
            account_id: アカウント ID。
        """
        # 現在のデータを取得
        results = self._search_usecase.execute()
        account = next((a for a in results if int(a.id) == account_id), None)

        if not account:
            return

        self._view.show_edit_form(
            account_id, account.service_name, account.login_id, account.password.get_raw_value()
        )

    @Slot(int)
    def handle_delete_request(self, account_id: int) -> None:
        """削除リクエストを処理します。.

        Args:
            account_id: アカウント ID。
        """
        # 削除確認のために名前を取得
        results = self._search_usecase.execute()
        account = next((a for a in results if int(a.id) == account_id), None)

        if not account:
            return

        reply = QMessageBox.question(
            self._view,
            "削除の確認",
            f"「{account.service_name}」を削除してもよろしいですか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._delete_usecase.execute(account_id)
            # 完了後リストを再読み込み
            self._refresh_list()

    @Slot(object, str, str, str)
    def handle_save_request(
        self,
        account_id: int | None,
        service_name: str,
        login_id: str,
        password_str: str,
    ) -> None:
        """保存リクエストを処理します。.

        Args:
            account_id: アカウント ID（新規の場合は None）。
            service_name: サービス名。
            login_id: ログイン ID。
            password_str: パスワード文字列。
        """
        try:
            if account_id is None:
                self._create_usecase.execute(service_name, login_id, password_str)
            else:
                self._update_usecase.execute(account_id, service_name, login_id, password_str)
        except Exception as e:
            QMessageBox.warning(self._view, "保存エラー", f"エラーが発生しました。\n\n詳細: {e}")
        finally:
            # 更新・追加したらリストを必ず再読み込み
            self._refresh_list()

    def _refresh_list(self) -> None:
        """リストを現在の検索条件で再読み込みします。."""
        query = self._view.search_input.text()
        results = self._search_usecase.execute(query)
        self._view.update_results(results)
