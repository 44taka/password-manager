"""Flet版 アプリケーションのエントリーポイント (Composition Root)."""

from __future__ import annotations

from pathlib import Path

import flet as ft
from injector import Injector, Module, provider, singleton

from password_manager.core.logger import get_logger, setup_logger
from password_manager.domain.account import AccountRepository, ClipboardPolicy
from password_manager.infrastructure import (
    MacClipboardService,
    MacosKeychainStore,
    SqliteAccountStore,
    UnifiedAccountRepository,
)
from password_manager.presentation.views_flet import MainPage
from password_manager.usecases.account import (
    CopyLoginIDUseCase,
    CopyPasswordUseCase,
    CreateAccountUseCase,
    DeleteAccountUseCase,
    SearchAccountsUseCase,
    UpdateAccountUseCase,
)
from password_manager.usecases.interfaces import ClipboardService

logger = get_logger(__name__)


class PasswordManagerFletModule(Module):
    """Flet アプリケーション用の DIコンテナ設定を行うモジュール."""

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
    def provide_clipboard_policy(self) -> ClipboardPolicy:
        """クリップボードポリシーの実体を提供します。

        Returns:
            ClipboardPolicy インスタンス。
        """
        return ClipboardPolicy()


def main() -> None:
    """アプリケーションのエントリーポイントです。"""
    # ロギングの初期化
    setup_logger()
    logger.info("Flet application starting...")

    # DIコンテナの構築
    injector = Injector([PasswordManagerFletModule()])

    def flet_main(page: ft.Page) -> None:
        """Flet のメインウィンドウを設定・起動します。"""
        page.title = "Password Manager"

        # ウィンドウ初期サイズ設定
        page.window_width = 750  # type: ignore
        page.window_height = 550  # type: ignore
        page.window_resizable = True  # type: ignore

        # ダークテーマ設定
        page.theme_mode = ft.ThemeMode.DARK

        # MainPage の解決と描画
        search_usecase = injector.get(SearchAccountsUseCase)
        create_usecase = injector.get(CreateAccountUseCase)
        update_usecase = injector.get(UpdateAccountUseCase)
        delete_usecase = injector.get(DeleteAccountUseCase)
        copy_login_id_usecase = injector.get(CopyLoginIDUseCase)
        copy_password_usecase = injector.get(CopyPasswordUseCase)

        main_page = MainPage(
            page=page,
            search_usecase=search_usecase,
            create_usecase=create_usecase,
            update_usecase=update_usecase,
            delete_usecase=delete_usecase,
            copy_login_id_usecase=copy_login_id_usecase,
            copy_password_usecase=copy_password_usecase,
        )

        page.add(main_page)

        # 初期データの読み込みと一覧表示
        main_page.load_accounts()

    # デスクトップアプリとして起動
    ft.run(flet_main)


if __name__ == "__main__":
    main()
