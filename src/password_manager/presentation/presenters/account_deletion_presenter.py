"""アカウントの削除を制御する Presenter."""

from __future__ import annotations

from injector import inject
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox

from password_manager.presentation.views import MainWindow
from password_manager.usecases.account import DeleteAccountUseCase, SearchAccountsUseCase


class AccountDeletionPresenter(QObject):
    """削除フローを担当."""

    @inject
    def __init__(
        self,
        view: MainWindow,
        delete_usecase: DeleteAccountUseCase,
        search_usecase: SearchAccountsUseCase,
    ) -> None:
        """AccountDeletionPresenter を初期化します。

        Args:
            view: 操作対象のメインウィンドウ。
            delete_usecase: 削除用ユースケース。
            search_usecase: データ取得および再検索用ユースケース。
        """
        super().__init__()
        self._view = view
        self._delete_usecase = delete_usecase
        self._search_usecase = search_usecase

        # View のシグナルを接続
        self._view.delete_requested.connect(self.handle_delete_request)

    @Slot(int)
    def handle_delete_request(self, account_id: int) -> None:
        """削除確認を表示し、削除を処理します。

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
            try:
                self._delete_usecase.execute(account_id)
                self._refresh_list()
            except Exception as e:
                msg = f"エラーが発生しました。\n\n詳細: {e}"
                QMessageBox.warning(self._view, "削除エラー", msg)

    def _refresh_list(self) -> None:
        """リストを最新状態に更新します。"""
        query = self._view.search_input.text()
        results = self._search_usecase.execute(query)
        self._view.update_results(results)
