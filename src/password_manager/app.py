"""PySide6ベースのネイティブアプリケーション. Composition Root."""

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
from password_manager.presentation.controller import AppController


class PasswordManagerModule(Module):
    """DIコンテナの設定を行うモジュール."""

    @singleton
    @provider
    def provide_account_repository(self) -> AccountRepository:
        """アカウントリポジトリの実装を提供します。."""
        # データベースパスの設定（将来的に設定ファイルから読み込むように拡張可能）
        db_path = Path.home() / ".password_manager" / "passwords.db"

        sqlite_store = SqliteAccountStore(db_path=db_path)
        keychain_store = MacosKeychainStore()

        return UnifiedAccountRepository(sqlite_store, keychain_store)

    @singleton
    @provider
    def provide_clipboard_service(self) -> ClipboardService:
        """クリップボードサービスの実装を提供します。."""
        return MacClipboardService()


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

    # Controllerを取得（必要な依存関係は自動で注入される）
    app.controller = injector.get(AppController)  # type: ignore

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
