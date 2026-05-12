"""アプリケーションのエントリーポイント (Composition Root)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from injector import Injector, Module, provider, singleton
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from password_manager.domain.account import AccountRepository
from password_manager.infrastructure import (
    MacClipboardService,
    MacosKeychainStore,
    SqliteAccountStore,
    UnifiedAccountRepository,
)
from password_manager.presentation.presenters import (
    AccountCreationPresenter,
    AccountDeletionPresenter,
    AccountUpdatePresenter,
    ClipboardPresenter,
    SearchPresenter,
)
from password_manager.presentation.views import MainWindow
from password_manager.usecases.interfaces import ClipboardService


class PasswordManagerModule(Module):
    """DIコンテナの設定を行うモジュール."""

    @singleton
    @provider
    def provide_account_repository(self) -> AccountRepository:
        """アカウントリポジトリの実装を提供します。

        Returns:
            UnifiedAccountRepository インスタンス。
        """
        # データベースパスの設定
        db_path = Path.home() / ".password_manager" / "passwords.db"

        sqlite_store = SqliteAccountStore(db_path=db_path)
        keychain_store = MacosKeychainStore()

        return UnifiedAccountRepository(sqlite_store, keychain_store)

    @singleton
    @provider
    def provide_clipboard_service(self) -> ClipboardService:
        """クリップボードサービスの実装を提供します。

        Returns:
            MacClipboardService インスタンス。
        """
        return MacClipboardService()

    @singleton
    @provider
    def provide_main_window(self) -> MainWindow:
        """メインウィンドウの実装を提供します。

        Returns:
            MainWindow インスタンス。
        """
        return MainWindow()


def main() -> None:
    """アプリケーションのエントリーポイントです。"""
    os.environ["QT_MAC_WANTS_LAYER"] = "1"

    app = QApplication(sys.argv)

    base_dir = Path(__file__).resolve().parent.parent.parent
    icon_path = base_dir / "resources" / "AppIcon.icns"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # DIコンテナの構築
    injector = Injector([PasswordManagerModule()])
    injector.binder.bind(QApplication, to=app)

    # UI と Presenter の解決
    window = injector.get(MainWindow)

    # 各 Presenter を初期化 (MainWindow や UseCase が自動注入される)
    _search_presenter = injector.get(SearchPresenter)
    _creation_presenter = injector.get(AccountCreationPresenter)
    _update_presenter = injector.get(AccountUpdatePresenter)
    _deletion_presenter = injector.get(AccountDeletionPresenter)
    _clipboard_presenter = injector.get(ClipboardPresenter)

    # 初期データの読み込み
    window.show()
    _search_presenter.handle_search("")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
