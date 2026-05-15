"""アカウントの新規作成を制御する Presenter."""

from __future__ import annotations

from injector import inject
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QDialog

from password_manager.core.exceptions import AppError
from password_manager.presentation.views import AccountDialog, MainWindow
from password_manager.usecases.account import CreateAccountUseCase, SearchAccountsUseCase


class AccountCreationPresenter(QObject):
    """新規登録フローを担当."""

    @inject
    def __init__(
        self,
        view: MainWindow,
        create_usecase: CreateAccountUseCase,
        search_usecase: SearchAccountsUseCase,
    ) -> None:
        """AccountCreationPresenter を初期化します。

        Args:
            view: 操作対象のメインウィンドウ。
            create_usecase: 作成用ユースケース。
            search_usecase: 更新後の再検索用ユースケース。
        """
        super().__init__()
        self._view = view
        self._create_usecase = create_usecase
        self._search_usecase = search_usecase

        # View のシグナルを接続
        self._view.add_account_requested.connect(self.handle_add_request)

    @Slot()
    def handle_add_request(self) -> None:
        """新規登録ダイアログを表示し、保存を処理します。"""
        dialog = AccountDialog(self._view)
        dialog.set_data("新規登録", "", "", "")

        if dialog.exec() == QDialog.DialogCode.Accepted:
            site, user, pwd = dialog.get_data()

            try:
                self._create_usecase.execute(site, user, pwd)
                self._refresh_list()
            except AppError as e:
                self._view.show_error_message("保存エラー", str(e))
            except Exception as e:
                msg = f"予期せぬエラーが発生しました。\n\n詳細: {e}"
                self._view.show_error_message("予期せぬエラー", msg)

    def _refresh_list(self) -> None:
        """リストを最新状態に更新します。"""
        query = self._view.search_input.text()
        results = self._search_usecase.execute(query)
        self._view.update_results(results)
