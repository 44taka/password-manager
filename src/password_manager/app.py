"""アプリケーションのエントリーポイント (Composition Root)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from injector import Injector, Module, provider, singleton
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from password_manager.domain.account import AccountRepository, ClipboardService
from password_manager.infrastructure.mac_clipboard_service import MacClipboardService
from password_manager.infrastructure.macos_keychain_store import MacosKeychainStore
from password_manager.infrastructure.sqlite_account_store import SqliteAccountStore
from password_manager.infrastructure.unified_account_repository import (
    UnifiedAccountRepository,
)
from password_manager.presentation.presenters.account_presenter import AccountPresenter
from password_manager.presentation.presenters.clipboard_presenter import (
    ClipboardPresenter,
)
from password_manager.presentation.presenters.search_presenter import SearchPresenter
from password_manager.presentation.views.main_window import MainWindow


class PasswordManagerModule(Module):
    """DIコンテナの設定を行うモジュール."""

    @singleton
    @provider
    def provide_account_repository(self) -> AccountRepository:
        """アカウントリポジトリの実装を提供します。."""
        # データベースパスの設定
        db_path = Path.home() / ".password_manager" / "passwords.db"

        sqlite_store = SqliteAccountStore(db_path=db_path)
        keychain_store = MacosKeychainStore()

        return UnifiedAccountRepository(sqlite_store, keychain_store)

    @singleton
    @provider
    def provide_clipboard_service(self) -> ClipboardService:
        """クリップボードサービスの実装を提供します。."""
        return MacClipboardService()

    @singleton
    @provider
    def provide_main_window(self) -> MainWindow:
        """メインウィンドウの実装を提供します。."""
        return MainWindow()


def main() -> None:
    """アプリケーションのエントリーポイントです。."""
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
    # 循環参照を防ぐため、Presenter 側で View を保持し、View からは知らない構造
    _search_presenter = injector.get(SearchPresenter)
    _account_presenter = injector.get(AccountPresenter)
    _clipboard_presenter = injector.get(ClipboardPresenter)

    # 初期データの読み込み
    window.show()
    _search_presenter.handle_search("")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
