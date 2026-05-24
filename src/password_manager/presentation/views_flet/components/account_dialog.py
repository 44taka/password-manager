"""Flet版 アカウント追加・編集用ダイアログコンポーネント."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft


class AccountDialog(ft.AlertDialog):
    """アカウント情報を登録・更新するためのダイアログ."""

    def __init__(
        self,
        title_text: str,
        on_save: Callable[[str, str, str], None],
        on_cancel: Callable[[], None],
        site: str = "",
        username: str = "",
        password: str = "",
    ) -> None:
        """AccountDialog を初期化します。

        Args:
            title_text: ダイアログ上部に表示するタイトル。
            on_save: 保存ボタン押下時のコールバック。
                (site, username, password) を受け取ります。
            on_cancel: 「キャンセル」ボタンまたはダイアログ外クリック時のコールバック。
            site: サイト名の初期値。
            username: ユーザー名の初期値。
            password: パスワードの初期値。
        """
        self.site_input = ft.TextField(
            label="📝 サイト名",
            hint_text="例: GitHub",
            value=site,
            autofocus=True,
            border_color=ft.Colors.BLUE_GREY_700,
            focused_border_color=ft.Colors.BLUE_400,
        )

        self.user_input = ft.TextField(
            label="👤 ユーザー名",
            value=username,
            border_color=ft.Colors.BLUE_GREY_700,
            focused_border_color=ft.Colors.BLUE_400,
        )

        self.pass_input = ft.TextField(
            label="🔑 パスワード",
            value=password,
            password=True,
            can_reveal_password=True,  # 目のアイコン（パスワード表示/非表示切り替え）を自動配置
            border_color=ft.Colors.BLUE_GREY_700,
            focused_border_color=ft.Colors.BLUE_400,
        )

        # 保存ボタン
        save_btn = ft.Button(
            "保存する",
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            on_click=lambda _: on_save(
                self.site_input.value.strip(),
                self.user_input.value.strip(),
                self.pass_input.value.strip(),
            ),
        )

        # キャンセルボタン
        cancel_btn = ft.TextButton(
            "キャンセル",
            on_click=lambda _: on_cancel(),
        )

        super().__init__(
            title=ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    self.site_input,
                    self.user_input,
                    self.pass_input,
                ],
                spacing=16,
                tight=True,
                width=350,
            ),
            actions=[cancel_btn, save_btn],
            actions_alignment=ft.MainAxisAlignment.END,
            # ダイアログの外側をクリックして閉じた際もキャンセル扱い
            on_dismiss=lambda _: on_cancel(),
        )
