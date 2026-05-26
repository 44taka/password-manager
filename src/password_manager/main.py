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
from password_manager.presentation import MainPage
from password_manager.usecases.interfaces import ClipboardService

logger = get_logger(__name__)


class PasswordManagerModule(Module):
    """アプリケーション用の DIコンテナ設定を行うモジュール."""

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
    injector = Injector([PasswordManagerModule()])

    def flet_main(page: ft.Page) -> None:
        """Flet のメインウィンドウを設定・起動します。"""
        page.title = "Password Manager"

        # ウィンドウ初期サイズ設定
        page.window.width = 750
        page.window.height = 550
        page.window.resizable = True

        # ダークテーマ設定
        page.theme_mode = ft.ThemeMode.DARK

        # Fletが生成したpageオブジェクトを、その場だけバインドした子インジェクターを作成
        child_injector = injector.create_child_injector(
            modules=[lambda binder: binder.bind(ft.Page, to=page)]
        )

        # MainPageとその配下のすべての依存関係（ユースケース群）を自動解決
        main_page = child_injector.get(MainPage)

        page.add(main_page)

        # 初期データの読み込みと一覧表示
        main_page.load_accounts()

    # デスクトップアプリとして起動
    ft.run(flet_main)


if __name__ == "__main__":
    main()
