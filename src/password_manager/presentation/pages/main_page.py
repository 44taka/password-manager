"""Flet版 メインページ（UI構築 ＆ イベント制御）."""

from __future__ import annotations

import flet as ft
from injector import inject

from password_manager.core.logger import get_logger
from password_manager.domain.account import Account
from password_manager.presentation.components.account_card import AccountCard
from password_manager.presentation.components.account_dialog import AccountDialog
from password_manager.presentation.components.error_dialog import ErrorDialog
from password_manager.usecases.account import (
    CopyLoginIDUseCase,
    CopyPasswordUseCase,
    CreateAccountUseCase,
    DeleteAccountUseCase,
    SearchAccountsUseCase,
    UpdateAccountUseCase,
)

logger = get_logger(__name__)

# ==============================================================================
# カラー定義
# ==============================================================================
PRIMARY = "#374379"
PRIMARY_CONTAINER = "#4f5b92"
ON_PRIMARY_CONTAINER = "#d0d6ff"
SURFACE = "#fbf8fe"
SURFACE_CONTAINER_HIGH = "#eae7ed"
SURFACE_CONTAINER_HIGHEST = "#e4e1e7"
SURFACE_CONTAINER_LOWEST = "#ffffff"
BACKGROUND = "#fbf8fe"
ON_SURFACE = "#1b1b1f"
ON_SURFACE_VARIANT = "#45464f"
ERROR = "#ba1a1a"


class MainPage(ft.Column):
    """パスワードマネージャーのメイン画面.

    マテリアルデザイン3のヘッダー、レスポンシブ検索バー、リスト表示、
    および画面リサイズ時の自動アライメント調整機能を提供します。
    """

    @inject
    def __init__(
        self,
        page: ft.Page,
        search_usecase: SearchAccountsUseCase,
        create_usecase: CreateAccountUseCase,
        update_usecase: UpdateAccountUseCase,
        delete_usecase: DeleteAccountUseCase,
        copy_login_id_usecase: CopyLoginIDUseCase,
        copy_password_usecase: CopyPasswordUseCase,
    ) -> None:
        """MainPage を初期化します。

        Args:
            page: Flet の Page オブジェクト。
            search_usecase: 検索・全件取得用ユースケース。
            create_usecase: 新規作成用ユースケース。
            update_usecase: アカウント更新用ユースケース。
            delete_usecase: アカウント削除用ユースケース。
            copy_login_id_usecase: IDコピー用ユースケース。
            copy_password_usecase: パスワードコピー用ユースケース。
        """
        super().__init__()
        self._page_ref = page
        self.search_usecase = search_usecase
        self.create_usecase = create_usecase
        self.update_usecase = update_usecase
        self.delete_usecase = delete_usecase
        self.copy_login_id_usecase = copy_login_id_usecase
        self.copy_password_usecase = copy_password_usecase

        self.expand = True
        self.spacing = 0

        # Google Fonts から Inter を読み込む
        self._page_ref.fonts = {
            "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap"
        }
        self._page_ref.bgcolor = BACKGROUND

        # 1. 検索フィールド & 検索コンテナ (ホバーエフェクト付き)
        self.search_input = ft.TextField(
            hint_text="サービス名で検索...",
            hint_style=ft.TextStyle(color=ON_SURFACE_VARIANT, font_family="Inter", size=16),
            border=ft.InputBorder.NONE,
            content_padding=ft.Padding(left=0, top=0, right=0, bottom=12),
            text_style=ft.TextStyle(color=ON_SURFACE, font_family="Inter", size=16),
            expand=True,
            height=40,
            on_change=self.on_search_changed,  # type: ignore
        )

        self.search_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SEARCH, color=ON_SURFACE_VARIANT, size=24),
                    self.search_input,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=SURFACE_CONTAINER_HIGH,
            border_radius=24,
            padding=ft.Padding(left=16, top=0, right=16, bottom=0),
            height=48,
            width=672,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_hover=self._handle_search_hover,  # type: ignore
        )

        # 2. 新規登録ボタン
        self.add_btn = ft.FilledButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ADD, color=ON_PRIMARY_CONTAINER, size=20),
                    ft.Text(
                        "新規登録",
                        color=ON_PRIMARY_CONTAINER,
                        weight=ft.FontWeight.W_500,
                        font_family="Inter",
                        size=14,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=PRIMARY_CONTAINER,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=24),
                padding=ft.Padding(left=20, top=10, right=20, bottom=10),
            ),
            height=44,
            on_click=self.on_add_clicked,  # type: ignore
        )

        # 3. ヘッダーバーの構築
        self.header_content = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Password Manager",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY,
                        font_family="Inter",
                    ),
                    self.search_container,
                    self.add_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
        )

        header = ft.Container(
            content=ft.Row(
                controls=[self.header_content],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=24, top=0, right=24, bottom=0),
            height=64,
            bgcolor=SURFACE,
        )

        # 4. アカウント一覧
        self.list_view = ft.ListView(
            expand=True,
            spacing=12,
        )

        # メインコンテンツエリア (スクロール可能)
        self.main_area = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=16),
                    self.list_view,
                    ft.Container(height=16),
                ],
                expand=True,
            ),
            expand=True,
            padding=ft.Padding(left=24, top=0, right=24, bottom=0),
        )

        # 全体レイアウトの中央寄せRow
        main_row = ft.Row(
            controls=[self.main_area],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

        # 画面の全体構造
        self.controls = [
            header,
            main_row,
        ]

        # ページリサイズ時のレスポンシブ設定
        self._page_ref.on_resize = self.on_resize

    def on_resize(self, e: ft.PageResizeEvent | None) -> None:
        """ウィンドウサイズ変更時に幅を動的に再計算します."""
        win_width = self._page_ref.window.width if self._page_ref.window.width else 1280
        target_width = min(win_width - 48, 1200)
        self.main_area.width = target_width
        self.header_content.width = target_width
        self.update()

    def _handle_search_hover(self, e: ft.ControlEvent) -> None:
        """検索バーホバー時の背景色アニメーション."""
        is_hovered = e.data in (True, "true")
        self.search_container.bgcolor = (
            SURFACE_CONTAINER_HIGHEST if is_hovered else SURFACE_CONTAINER_HIGH
        )
        self.search_container.update()

    def load_accounts(self, query: str = "") -> None:
        """アカウントデータを読み込み、リスト表示を更新します。

        Args:
            query: 検索クエリ。指定しない場合は全件取得します。
        """
        try:
            accounts = self.search_usecase.execute(query)
            logger.debug(f"load_accounts: found {len(accounts)} accounts")
            self.list_view.controls.clear()

            for account in accounts:
                logger.debug(f"Adding card: {account.service_name.value}")
                card = AccountCard(
                    account=account,
                    on_copy_password=self.copy_password,
                    on_copy_username=self.copy_username,
                    on_edit=self.edit_account,
                    on_delete=self.confirm_delete,
                )
                self.list_view.controls.append(card)

            self._page_ref.update()
            # 初期サイズ合わせ用のリサイズ呼び出し
            self.on_resize(None)
        except Exception as e:
            logger.exception(f"load_accounts exception: {e}")
            self.show_error("データ読み込みエラー", str(e))

    def on_search_changed(self, e: ft.ControlEvent) -> None:
        """検索欄のテキストが変更された時に実行されます。

        Args:
            e: コントロールイベントオブジェクト。
        """
        self.load_accounts(self.search_input.value)

    def show_error(self, title: str, message: str) -> None:
        """エラーダイアログを表示します。

        Args:
            title: エラーのタイトル。
            message: エラーメッセージ。
        """
        full_message = f"{title}: {message}" if title else message

        def close_dialog() -> None:
            dialog.open = False
            self._page_ref.update()

        dialog = ErrorDialog(message=full_message, on_close=close_dialog)
        self._page_ref.overlay.append(dialog)
        dialog.open = True
        self._page_ref.update()

    def show_success(self, message: str) -> None:
        """画面下部に成功用スナックバーを表示します。

        Args:
            message: 表示する成功メッセージ。
        """
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color="#ffffff", font_family="Inter"),
            bgcolor=PRIMARY,
        )
        self._page_ref.overlay.append(snack_bar)
        snack_bar.open = True
        self._page_ref.update()

    def copy_password(self, account_id: str) -> None:
        """パスワードのクリップボードへのコピー処理。

        Args:
            account_id: コピー対象のアカウントID。
        """
        try:
            self.copy_password_usecase.execute(account_id)
            self.show_success("パスワードをクリップボードにコピーしました 🔑")
        except Exception as e:
            self.show_error("コピー失敗", str(e))

    def copy_username(self, account_id: str) -> None:
        """ログインIDのクリップボードへのコピー処理。

        Args:
            account_id: コピー対象のアカウントID。
        """
        try:
            self.copy_login_id_usecase.execute(account_id)
            self.show_success("ログインIDをクリップボードにコピーしました 👤")
        except Exception as e:
            self.show_error("コピー失敗", str(e))

    def on_add_clicked(self, e: ft.ControlEvent) -> None:
        """新規登録ボタンがクリックされた時の処理。

        Args:
            e: コントロールイベントオブジェクト。
        """

        def on_save(site: str, user: str, pwd: str) -> None:
            try:
                self.create_usecase.execute(site, user, pwd)
                dialog.open = False
                self.load_accounts(self.search_input.value)
                self.show_success(f"「{site}」を新規登録しました")
            except Exception as ex:
                self.show_error("保存エラー", str(ex))

        def on_cancel() -> None:
            dialog.open = False
            self._page_ref.update()

        dialog = AccountDialog(
            title_text="新規登録",
            on_save=on_save,
            on_cancel=on_cancel,
        )
        self._page_ref.overlay.append(dialog)
        dialog.open = True
        self._page_ref.update()

    def edit_account(self, account: Account) -> None:
        """編集ボタンがクリックされた時の処理。

        Args:
            account: 編集対象のアカウント情報。
        """
        account_id = str(account.id)

        def on_save(site: str, user: str, pwd: str) -> None:
            try:
                self.update_usecase.execute(account_id, site, user, pwd)
                dialog.open = False
                self.load_accounts(self.search_input.value)
                self.show_success("アカウント情報を更新しました")
            except Exception as ex:
                self.show_error("更新エラー", str(ex))

        def on_cancel() -> None:
            dialog.open = False
            self._page_ref.update()

        dialog = AccountDialog(
            title_text="パスワードの編集",
            on_save=on_save,
            on_cancel=on_cancel,
            site=account.service_name.value,
            username=account.login_id.value,
            password=account.password.get_raw_value(),
        )
        self._page_ref.overlay.append(dialog)
        dialog.open = True
        self._page_ref.update()

    def confirm_delete(self, account: Account) -> None:
        """削除ボタンがクリックされた時の確認ダイアログ表示。

        Args:
            account: 削除対象のアカウント情報。
        """
        account_id = str(account.id)

        def yes_clicked(e: ft.ControlEvent) -> None:
            try:
                self.delete_usecase.execute(account_id)
                dialog.open = False
                self.load_accounts(self.search_input.value)
                self.show_success("アカウントを削除しました 🗑️")
            except Exception as ex:
                self.show_error("削除エラー", str(ex))

        def no_clicked(e: ft.ControlEvent) -> None:
            dialog.open = False
            self._page_ref.update()

        dialog_content = ft.Container(
            bgcolor=SURFACE_CONTAINER_HIGHEST,
            border_radius=28,
            width=312,
            padding=24,
            content=ft.Column(
                controls=[  # type: ignore
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.DELETE_OUTLINE, color=ON_SURFACE_VARIANT, size=24),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        "アカウントの削除確認",
                        size=22,
                        color=ON_SURFACE,
                        font_family="Inter",
                        weight=ft.FontWeight.W_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"この操作を実行すると、{account.service_name.value} "
                        "のアカウント情報が完全に削除されます。"
                        "この操作は取り消せません。",
                        size=14,
                        color=ON_SURFACE_VARIANT,
                        font_family="Inter",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        controls=[
                            ft.TextButton(
                                "キャンセル",
                                on_click=no_clicked,  # type: ignore
                                style=ft.ButtonStyle(
                                    color=PRIMARY,
                                    overlay_color=ft.Colors.with_opacity(0.05, PRIMARY),
                                ),
                            ),
                            ft.TextButton(
                                "削除する",
                                on_click=yes_clicked,  # type: ignore
                                style=ft.ButtonStyle(
                                    color=ERROR,
                                    overlay_color=ft.Colors.with_opacity(0.05, ERROR),
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=8,
                    ),
                ],
                spacing=16,
                tight=True,
            ),
        )

        dialog = ft.AlertDialog(
            modal=True,
            content_padding=0,
            bgcolor="transparent",
            content=dialog_content,
            on_dismiss=no_clicked,  # type: ignore
        )

        self._page_ref.overlay.append(dialog)
        dialog.open = True
        self._page_ref.update()
