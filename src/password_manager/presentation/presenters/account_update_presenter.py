"""アカウントの更新を制御する Presenter."""

from __future__ import annotations

from injector import inject
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QDialog, QMessageBox

from password_manager.presentation.views import AccountDialog, MainWindow
from password_manager.usecases.account import SearchAccountsUseCase, UpdateAccountUseCase


class AccountUpdatePresenter(QObject):
    """更新フローを担当."""

    @inject
    def __init__(
        self,
        view: MainWindow,
        update_usecase: UpdateAccountUseCase,
        search_usecase: SearchAccountsUseCase,
    ) -> None:
        """AccountUpdatePresenter を初期化します。

        Args:
            view: 操作対象のメインウィンドウ。
            update_usecase: 更新用ユースケース。
            search_usecase: データ取得および再検索用ユースケース。
        """
        super().__init__()
        self._view = view
        self._update_usecase = update_usecase
        self._search_usecase = search_usecase

        # View のシグナルを接続
        self._view.edit_requested.connect(self.handle_edit_request)

    @Slot(str)
    def handle_edit_request(self, account_id: str) -> None:
        """編集ダイアログを表示し、更新を処理します。

        Args:
            account_id: アカウント ID（UUID文字列）。
        """
        # 現在のデータを取得
        results = self._search_usecase.execute()
        account = next((a for a in results if str(a.id) == account_id), None)

        if not account:
            return

        dialog = AccountDialog(self._view)
        dialog.set_data(
            "パスワードの編集",
            account.service_name,
            account.login_id,
            account.password.get_raw_value(),
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_site, new_user, new_pwd = dialog.get_data()
            if not new_site or not new_pwd:
                return

            try:
                self._update_usecase.execute(account_id, new_site, new_user, new_pwd)
                self._refresh_list()
            except Exception as e:
                msg = f"エラーが発生しました。\n\n詳細: {e}"
                QMessageBox.warning(self._view, "保存エラー", msg)

    def _refresh_list(self) -> None:
        """リストを最新状態に更新します。"""
        query = self._view.search_input.text()
        results = self._search_usecase.execute(query)
        self._view.update_results(results)
