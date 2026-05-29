"""Flet版 アカウント表示用カードコンポーネント."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

import flet as ft

from password_manager.domain.account import Account

# ==============================================================================
# カラー定義
# ==============================================================================
PRIMARY = "#374379"
SURFACE_CONTAINER_LOW = "#f6f2f8"
SURFACE_CONTAINER_HIGH = "#eae7ed"
SURFACE_CONTAINER_HIGHEST = "#e4e1e7"
ON_SURFACE = "#1b1b1f"
ON_SURFACE_VARIANT = "#45464f"


class AccountCard(ft.Container):
    """リスト内に表示するカードコンポーネント.

    ホバー時に背景色と枠線が滑らかに変化し、右側のアクションボタンがフェードインします。
    また、コピー操作時にチェックマークに変化するマイクロインタラクションを提供します。
    """

    def __init__(
        self,
        account: Account,
        on_copy_password: Callable[[str], None],
        on_copy_username: Callable[[str], None],
        on_edit: Callable[[Account], None],
        on_delete: Callable[[Account], None],
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
        self.on_copy_password = on_copy_password
        self.on_copy_username = on_copy_username
        self.on_edit = on_edit
        self.on_delete = on_delete

        # 1. アクションボタン群 (右側)
        self.action_buttons = [
            self._create_action_button(
                ft.Icons.PERSON_OUTLINE,
                "ログインIDをコピー",
                self._on_copy_username_clicked,
            ),
            self._create_action_button(
                ft.Icons.CONTENT_COPY,
                "パスワードをコピー",
                self._on_copy_password_clicked,
            ),
            self._create_action_button(
                ft.Icons.EDIT,
                "編集",
                lambda: self.on_edit(self.account),
            ),
            self._create_action_button(
                ft.Icons.DELETE_OUTLINE,
                "削除",
                lambda: self.on_delete(self.account),
            ),
        ]

        self.action_row = ft.Row(
            controls=self.action_buttons,  # type: ignore
            spacing=8,
            opacity=0.0,  # 初期状態は非表示
            animate_opacity=200,  # 200ms でフェードイン・アウト
        )

        # 2. イニシャルアイコン
        initial = account.service_name.value[0].upper() if account.service_name.value else "?"
        icon_container = ft.Container(
            content=ft.Text(
                initial,
                size=16,
                weight=ft.FontWeight.BOLD,
                color=PRIMARY,
                font_family="Inter",
            ),
            width=48,
            height=48,
            bgcolor=SURFACE_CONTAINER_HIGHEST,
            border_radius=12,
            alignment=ft.Alignment(0, 0),  # 中央揃え
        )

        # 3. テキスト（サービス名 ＆ ログインID）
        text_column = ft.Column(
            controls=[
                ft.Text(
                    account.service_name.value,
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=ON_SURFACE,
                    font_family="Inter",
                ),
                ft.Text(
                    account.login_id.value,
                    size=14,
                    color=ON_SURFACE_VARIANT,
                    font_family="Inter",
                ),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # UIの組み立て
        self.content = ft.Row(
            controls=[
                # 左側：アイコン ＆ テキスト
                ft.Row(
                    controls=[
                        icon_container,
                        text_column,
                    ],
                    spacing=16,
                ),
                # 右側：ホバーアクション
                self.action_row,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # カード基本スタイル
        self.bgcolor = SURFACE_CONTAINER_LOW
        self.padding = ft.Padding(left=16, top=16, right=16, bottom=16)
        self.border_radius = 32
        # ホバー時のボーダーや背景色の変化を滑らかにするアニメーション設定
        self.animate = ft.Animation(200, "easeOut")  # type: ignore

        # 透明な枠線を定義してホバー時のガタつきを防ぐ
        transparent_side = ft.BorderSide(1, "transparent")
        self.border = ft.Border(
            top=transparent_side,
            bottom=transparent_side,
            left=transparent_side,
            right=transparent_side,
        )
        self.on_hover = self._handle_hover  # type: ignore

    def _create_action_button(
        self,
        icon: ft.IconData,
        tooltip: str,
        on_click: Callable[[], None],
    ) -> ft.IconButton:
        """アクション用アイコンボタンを作成します."""
        return ft.IconButton(
            icon=icon,
            icon_size=20,
            tooltip=tooltip,
            on_click=lambda _: on_click(),
            style=ft.ButtonStyle(
                color=ON_SURFACE_VARIANT,
                shape=ft.CircleBorder(),
                overlay_color=ft.Colors.with_opacity(0.1, ON_SURFACE_VARIANT),
            ),
            width=36,
            height=36,
        )

    def _handle_hover(self, e: ft.ControlEvent) -> None:
        """ホバー時にボーダー、背景色、およびアクションボタンの透過度を変更します."""
        is_hovered = e.data in (True, "true")

        # 背景色と枠線の切り替え
        if is_hovered:
            self.bgcolor = SURFACE_CONTAINER_HIGH
            primary_side = ft.BorderSide(1, ft.Colors.with_opacity(0.2, PRIMARY))
            self.border = ft.Border(
                top=primary_side,
                bottom=primary_side,
                left=primary_side,
                right=primary_side,
            )
            self.action_row.opacity = 1.0
        else:
            self.bgcolor = SURFACE_CONTAINER_LOW
            transparent_side = ft.BorderSide(1, "transparent")
            self.border = ft.Border(
                top=transparent_side,
                bottom=transparent_side,
                left=transparent_side,
                right=transparent_side,
            )
            self.action_row.opacity = 0.0

        self.update()

    def _on_copy_username_clicked(self) -> None:
        """ログインIDをコピーした際のマイクロインタラクション."""
        control = self.action_buttons[0]

        # ユースケースの呼び出し
        self.on_copy_username(str(self.account.id))

        # ボタンのアイコンをチェックマークに変えるマイクロインタラクション
        self._animate_success_icon(control)

    def _on_copy_password_clicked(self) -> None:
        """パスワードをコピーした際のマイクロインタラクション."""
        control = self.action_buttons[1]

        # ユースケースの呼び出し
        self.on_copy_password(str(self.account.id))

        # ボタンのアイコンをチェックマークに変えるマイクロインタラクション
        self._animate_success_icon(control)

    def _animate_success_icon(self, control: ft.IconButton) -> None:
        """アイコンを一時的にチェックマークに変更するアニメーション."""
        original_icon = control.icon
        control.icon = ft.Icons.CHECK
        control.style = ft.ButtonStyle(
            color=PRIMARY,
            shape=ft.CircleBorder(),
            overlay_color=ft.Colors.with_opacity(0.1, ON_SURFACE_VARIANT),
        )
        control.update()

        def reset_icon() -> None:
            time.sleep(2)
            control.icon = original_icon
            control.style = ft.ButtonStyle(
                color=ON_SURFACE_VARIANT,
                shape=ft.CircleBorder(),
                overlay_color=ft.Colors.with_opacity(0.1, ON_SURFACE_VARIANT),
            )
            control.update()

        threading.Thread(target=reset_icon, daemon=True).start()
