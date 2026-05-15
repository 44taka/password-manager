"""クリップボード操作を制御する Presenter."""

from __future__ import annotations

from injector import inject
from PySide6.QtCore import QObject, Slot

from password_manager.core.exceptions import AppError
from password_manager.presentation.views import MainWindow
from password_manager.usecases.account import CopyLoginIDUseCase, CopyPasswordUseCase


class ClipboardPresenter(QObject):
    """コピー操作のリクエストを処理する担当."""

    @inject
    def __init__(
        self,
        view: MainWindow,
        copy_login_id_usecase: CopyLoginIDUseCase,
        copy_password_usecase: CopyPasswordUseCase,
    ) -> None:
        """ClipboardPresenter を初期化します。

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

    @Slot(str)
    def handle_copy_login_id(self, account_id: str) -> None:
        """ログインIDのコピーを処理します。

        Args:
            account_id: アカウント ID（UUID文字列）。
        """
        try:
            self._copy_login_id_usecase.execute(account_id)
        except AppError as e:
            self._view.show_error_message("エラー", str(e))
        except Exception as e:
            msg = f"予期せぬエラーが発生しました。\n\n詳細: {e}"
            self._view.show_error_message("予期せぬエラー", msg)

    @Slot(str)
    def handle_copy_password(self, account_id: str) -> None:
        """パスワードのコピーを処理します。

        Args:
            account_id: アカウント ID（UUID文字列）。
        """
        try:
            self._copy_password_usecase.execute(account_id)
        except AppError as e:
            self._view.show_error_message("エラー", str(e))
        except Exception as e:
            msg = f"予期せぬエラーが発生しました。\n\n詳細: {e}"
            self._view.show_error_message("予期せぬエラー", msg)
