"""検索機能とリスト更新を制御する Presenter."""

from __future__ import annotations

from injector import inject
from PySide6.QtCore import QObject, Slot

from password_manager.presentation.views import MainWindow
from password_manager.usecases.account import SearchAccountsUseCase


class SearchPresenter(QObject):
    """検索リクエストを処理し、View のリストを更新する担当."""

    @inject
    def __init__(self, view: MainWindow, search_usecase: SearchAccountsUseCase) -> None:
        """SearchPresenter を初期化します。

        Args:
            view: 操作対象のメインウィンドウ。
            search_usecase: 検索用ユースケース。
        """
        super().__init__()
        self._view = view
        self._search_usecase = search_usecase

        # View のシグナルを接続
        self._view.search_requested.connect(self.handle_search)

    @Slot(str)
    def handle_search(self, query: str = "") -> None:
        """検索リクエストを処理し、View を更新します。

        Args:
            query: 検索クエリ。
        """
        results = self._search_usecase.execute(query)
        self._view.update_results(results)
