"""PySide6ベースのネイティブアプリケーション. Composition Root."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from injector import Injector, Module, provider, singleton
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from password_manager.domain.repositories import (
    ClipboardService,
    EntryRepository,
    PasswordRepository,
)
from password_manager.infrastructure.mac_clipboard_service import MacClipboardService
from password_manager.infrastructure.macos_keychain_repository import (
    MacosKeychainRepository,
)
from password_manager.infrastructure.sqlite_entry_repository import (
    SqliteEntryRepository,
)
from password_manager.presentation.controller import AppController
from password_manager.usecases.password_usecase import PasswordUseCase


class PasswordManagerModule(Module):
    """DIコンテナの設定を行うモジュール."""

    @singleton
    @provider
    def provide_entry_repository(self) -> EntryRepository:
        return SqliteEntryRepository()

    @singleton
    @provider
    def provide_password_repository(self) -> PasswordRepository:
        return MacosKeychainRepository()

    @singleton
    @provider
    def provide_clipboard_service(self) -> ClipboardService:
        return MacClipboardService()

    @provider
    def provide_app_controller(
        self,
        app: QApplication,
        usecase: PasswordUseCase,
    ) -> AppController:
        return AppController(app, usecase)


def main() -> None:
    os.environ["QT_MAC_WANTS_LAYER"] = "1"

    app = QApplication(sys.argv)

    base_dir = Path(__file__).resolve().parent.parent.parent
    icon_path = base_dir / "resources" / "AppIcon.icns"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # DIコンテナの構築
    # アプリケーションのインスタンスをDIコンテナに登録する場合は手動でバインドする
    injector = Injector([PasswordManagerModule()])
    injector.binder.bind(QApplication, to=app)

    # Controllerを取得（必要な依存関係は自動で注入される）
    injector.get(AppController)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
