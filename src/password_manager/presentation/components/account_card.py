"""Flet版 アカウント表示用カードコンポーネント."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from password_manager.domain.account import Account


class AccountCard(ft.Container):
    """リスト内に表示するカードコンポーネント.

    ホバー時に各種アクションボタン（コピー、編集、削除）をアニメーション表示します。
    """

    def __init__(
        self,
        account: Account,
        on_copy_password: Callable[[str], None],
        on_copy_username: Callable[[str], None],
        on_edit: Callable[[str], None],
        on_delete: Callable[[str], None],
    ) -> None:
        """AccountCard を初期化します。

        Args:
            account: 表示対象のアカウント情報。
            on_copy_password: パスワードコピー時のコールバック。
            on_copy_username: ユーザー名コピー時のコールバック。
            on_edit: 編集ボタン押下時のコールバック。
            on_delete: 削除ボタン押下時のコールバック。
        """
        super().__init__()
        self.account = account

        # ホバー時に表示するアクションボタン群
        self.action_row = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.KEY,
                    icon_color=ft.Colors.BLUE_200,
                    tooltip="パスワードをコピー",
                    on_click=lambda _: on_copy_password(str(account.id)),
                    width=36,
                    height=36,
                ),
                ft.IconButton(
                    icon=ft.Icons.PERSON,
                    icon_color=ft.Colors.BLUE_200,
                    tooltip="ログインIDをコピー",
                    on_click=lambda _: on_copy_username(str(account.id)),
                    width=36,
                    height=36,
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color=ft.Colors.AMBER_200,
                    tooltip="編集",
                    on_click=lambda _: on_edit(str(account.id)),
                    width=36,
                    height=36,
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_ACCENT,
                    tooltip="削除",
                    on_click=lambda _: on_delete(str(account.id)),
                    width=36,
                    height=36,
                ),
            ],
            spacing=4,
            opacity=0.0,  # 初期状態は非表示
            animate_opacity=200,  # 200ms のフェードイン・フェードアウト
        )

        # サイト名のイニシャル（アイコン用）
        initial = account.service_name.value[0].upper() if account.service_name.value else "?"

        self.content = ft.Row(
            controls=[
                # イニシャルアイコン
                ft.Container(
                    content=ft.Text(
                        initial,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_200,
                    ),
                    alignment=ft.Alignment(0, 0),
                    width=40,
                    height=40,
                    border_radius=20,
                    bgcolor=ft.Colors.BLUE_GREY_800,
                ),
                # テキスト情報 (サイト名 ＆ ログインID)
                ft.Column(
                    controls=[
                        ft.Text(
                            account.service_name.value,
                            size=15,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Text(
                            account.login_id.value,
                            size=12,
                            color=ft.Colors.BLUE_GREY_200,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
                # 右側のアクションボタンエリア
                self.action_row,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # カード自体の基本デザイン
        self.padding = ft.Padding(16, 8, 16, 8)
        self.border_radius = 12

        self.bgcolor = ft.Colors.BLUE_GREY_900
        self.on_hover = self.handle_hover  # type: ignore

    def handle_hover(self, e: ft.HoverEvent) -> None:  # type: ignore
        """ホバーイベントをハンドリングし、ボタンのフェードを制御します。"""
        # e.data は環境やバージョンによって bool型 または 文字列型 になります
        is_hovered = e.data in (True, "true")
        self.action_row.opacity = 1.0 if is_hovered else 0.0
        self.update()
