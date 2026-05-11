"""クリップボード操作を制御する Presenter."""

from __future__ import annotations

from injector import inject
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox

from password_manager.presentation.views.main_window import MainWindow
from password_manager.usecases.account.copy_login_id import CopyLoginIDUseCase
from password_manager.usecases.account.copy_password import CopyPasswordUseCase

# 定数
CLIPBOARD_CLEAR_SECONDS = 15


class ClipboardPresenter(QObject):
    """コピー操作のリクエストを処理する担当."""

    @inject
    def __init__(
        self,
        view: MainWindow,
        copy_login_id_usecase: CopyLoginIDUseCase,
        copy_password_usecase: CopyPasswordUseCase,
    ) -> None:
        """ClipboardPresenter を初期化します。.

        Args:
            view: 操作対象のメインウィンドウ。
            copy_login_id_usecase: ログインIDコピー用ユースケース。
            copy_password_usecase: パスワードコピー用ユースケース。
        """
        super().__init__()
        self._view = view
        self._copy_login_id_usecase = copy_login_id_usecase
        self._copy_password_usecase = copy_password_usecase

        # View のシグナルを接続
        self._view.copy_username_requested.connect(self.handle_copy_login_id)
        self._view.copy_password_requested.connect(self.handle_copy_password)

    @Slot(int)
    def handle_copy_login_id(self, account_id: int) -> None:
        """ログインIDのコピーを処理します。.

        Args:
            account_id: アカウント ID。
        """
        try:
            self._copy_login_id_usecase.execute(account_id)
        except ValueError as e:
            QMessageBox.warning(self._view, "エラー", str(e))

    @Slot(int)
    def handle_copy_password(self, account_id: int) -> None:
        """パスワードのコピーを処理します。.

        Args:
            account_id: アカウント ID。
        """
        try:
            self._copy_password_usecase.execute(account_id, clear_after=CLIPBOARD_CLEAR_SECONDS)
        except ValueError as e:
            QMessageBox.warning(self._view, "エラー", str(e))
