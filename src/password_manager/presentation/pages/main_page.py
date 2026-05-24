"""Flet版 メインページ（UI構築 ＆ イベント制御）."""

from __future__ import annotations

import flet as ft

from password_manager.presentation.components.account_card import AccountCard
from password_manager.presentation.components.account_dialog import AccountDialog
from password_manager.usecases.account import (
    CopyLoginIDUseCase,
    CopyPasswordUseCase,
    CreateAccountUseCase,
    DeleteAccountUseCase,
    SearchAccountsUseCase,
    UpdateAccountUseCase,
)


class MainPage(ft.Column):
    """パスワードマネージャーのメイン画面."""

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
        self.spacing = 20

        # UIコントロールの定義
        self.search_input = ft.TextField(
            hint_text="検索...",
            prefix_icon=ft.Icons.SEARCH,
            width=250,
            height=40,
            content_padding=ft.Padding(10, 0, 10, 0),
            border_color=ft.Colors.BLUE_GREY_700,
            focused_border_color=ft.Colors.BLUE_400,
            on_change=self.on_search_changed,  # type: ignore
        )

        self.add_btn = ft.Button(
            "＋ 新規登録",
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            height=40,
            on_click=self.on_add_clicked,  # type: ignore
        )

        self.list_view = ft.ListView(
            expand=True,
            spacing=10,
        )

        # 画面の全体構造
        self.controls = [
            # トップヘッダー
            ft.Row(
                controls=[
                    ft.Text(
                        "Password Manager",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Row(
                        controls=[
                            self.search_input,
                            self.add_btn,
                        ],
                        spacing=12,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            # アカウント一覧
            self.list_view,
        ]

    def load_accounts(self, query: str = "") -> None:
        """アカウントデータを読み込み、リスト表示を更新します。"""
        try:
            accounts = self.search_usecase.execute(query)
            print(f"[DEBUG] load_accounts: found {len(accounts)} accounts")
            self.list_view.controls.clear()

            for account in accounts:
                print(f"[DEBUG] Adding card: {account.service_name.value}")
                card = AccountCard(
                    account=account,
                    on_copy_password=self.copy_password,
                    on_copy_username=self.copy_username,
                    on_edit=self.edit_account,
                    on_delete=self.confirm_delete,
                )
                self.list_view.controls.append(card)

            self._page_ref.update()
        except Exception as e:
            print(f"[DEBUG] load_accounts exception: {e}")
            import traceback

            traceback.print_exc()
            self.show_error("データ読み込みエラー", str(e))

    def on_search_changed(self, e: ft.ControlEvent) -> None:  # type: ignore
        """検索欄のテキストが変更された時に実行されます。"""
        self.load_accounts(self.search_input.value)

    def show_error(self, title: str, message: str) -> None:
        """画面下部にエラー用スナックバーを表示します。"""
        self._page_ref.snack_bar = ft.SnackBar(  # type: ignore
            content=ft.Text(f"{title}: {message}", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_800,
        )
        self._page_ref.snack_bar.open = True  # type: ignore
        self._page_ref.update()

    def show_success(self, message: str) -> None:
        """画面下部に成功用スナックバーを表示します。"""
        self._page_ref.snack_bar = ft.SnackBar(  # type: ignore
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_800,
        )
        self._page_ref.snack_bar.open = True  # type: ignore
        self._page_ref.update()

    def copy_password(self, account_id: str) -> None:
        """パスワードのクリップボードへのコピー処理。"""
        try:
            self.copy_password_usecase.execute(account_id)
            self.show_success("パスワードをクリップボードにコピーしました 🔑")
        except Exception as e:
            self.show_error("コピー失敗", str(e))

    def copy_username(self, account_id: str) -> None:
        """ログインIDのクリップボードへのコピー処理。"""
        try:
            self.copy_login_id_usecase.execute(account_id)
            self.show_success("ログインIDをクリップボードにコピーしました 👤")
        except Exception as e:
            self.show_error("コピー失敗", str(e))

    def on_add_clicked(self, e: ft.ControlEvent) -> None:  # type: ignore
        """新規登録ボタンがクリックされた時の処理。"""

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
        self._page_ref.show_dialog(dialog)

    def edit_account(self, account_id: str) -> None:
        """編集ボタンがクリックされた時の処理。"""
        results = self.search_usecase.execute()
        account = next((a for a in results if str(a.id) == account_id), None)
        if not account:
            self.show_error("エラー", "対象のアカウント情報が見つかりません。")
            return

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
        self._page_ref.show_dialog(dialog)

    def confirm_delete(self, account_id: str) -> None:
        """削除ボタンがクリックされた時の確認ダイアログ表示。"""
        results = self.search_usecase.execute()
        account = next((a for a in results if str(a.id) == account_id), None)
        if not account:
            self.show_error("エラー", "対象のアカウント情報が見つかりません。")
            return

        def on_yes(e: ft.ControlEvent) -> None:  # type: ignore
            try:
                self.delete_usecase.execute(account_id)
                dialog.open = False
                self.load_accounts(self.search_input.value)
                self.show_success("アカウントを削除しました 🗑️")
            except Exception as ex:
                self.show_error("削除エラー", str(ex))

        def on_no(e: ft.ControlEvent) -> None:  # type: ignore
            dialog.open = False
            self._page_ref.update()

        dialog = ft.AlertDialog(
            title=ft.Text("削除の確認", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Text(f"「{account.service_name}」を削除してもよろしいですか？"),
            actions=[
                ft.TextButton("キャンセル", on_click=on_no),  # type: ignore
                ft.Button(
                    "削除",
                    bgcolor=ft.Colors.RED_600,
                    color=ft.Colors.WHITE,
                    on_click=on_yes,  # type: ignore
                ),
            ],  # type: ignore
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._page_ref.show_dialog(dialog)
