"""Flet版 アカウント追加・編集用ダイアログコンポーネント."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

# ==============================================================================
# カラー定義
# ==============================================================================
PRIMARY = "#374379"
PRIMARY_CONTAINER = "#4f5b92"
ON_PRIMARY_CONTAINER = "#d0d6ff"
SURFACE_CONTAINER_LOW = "#f0edf2"
SURFACE_CONTAINER_HIGHEST = "#e4e1e7"
SURFACE_CONTAINER_LOWEST = "#ffffff"
ON_SURFACE = "#1b1b1f"
ON_SURFACE_VARIANT = "#45464f"
OUTLINE = "#767680"


class AccountDialog(ft.AlertDialog):
    """アカウント情報を登録・更新するためのダイアログ.

    マテリアルデザイン3仕様の入力コンテナ、パスワード表示切り替え、
    およびランダムパスワード自動生成機能を提供します。
    """

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
        # 1. 各種 TextField の定義 (枠線なし、モック準拠スタイル)
        self.service_name_input = ft.TextField(
            value=site,
            hint_text="例: Netflix, GitHub",
            border=ft.InputBorder.NONE,
            border_width=0,
            border_color="transparent",
            text_style=ft.TextStyle(color=ON_SURFACE, size=16, font_family="Inter"),
            content_padding=ft.Padding(left=0, top=0, right=0, bottom=0),
            height=28,
            expand=True,
            autofocus=True,
        )

        self.login_id_input = ft.TextField(
            value=username,
            hint_text="ユーザー名 または メールアドレス",
            border=ft.InputBorder.NONE,
            border_width=0,
            border_color="transparent",
            text_style=ft.TextStyle(color=ON_SURFACE, size=16, font_family="Inter"),
            content_padding=ft.Padding(left=0, top=0, right=0, bottom=0),
            height=28,
            expand=True,
        )

        self.password_input = ft.TextField(
            value=password,
            hint_text="••••••••••••",
            password=True,
            can_reveal_password=False,
            border=ft.InputBorder.NONE,
            border_width=0,
            border_color="transparent",
            text_style=ft.TextStyle(color=ON_SURFACE, size=16, font_family="Inter"),
            content_padding=ft.Padding(left=0, top=0, right=0, bottom=0),
            height=28,
            expand=True,
        )

        # 2. アクション用ボタン (パスワード表示切り替え ＆ 生成)
        self.password_toggle_btn = ft.IconButton(
            icon=ft.Icons.VISIBILITY_OUTLINED,
            icon_size=20,
            icon_color=ON_SURFACE_VARIANT,
            on_click=lambda _: self._toggle_password(),
            style=ft.ButtonStyle(
                shape=ft.CircleBorder(),
                overlay_color=ft.Colors.with_opacity(0.1, ON_SURFACE_VARIANT),
            ),
            width=36,
            height=36,
        )

        # 3. 入力フィールド用コンテナの組み立て
        input_bg = ft.Colors.with_opacity(0.4, SURFACE_CONTAINER_HIGHEST)

        service_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "サービス名",
                        color=ON_SURFACE_VARIANT,
                        size=11,
                        weight=ft.FontWeight.W_500,
                        font_family="Inter",
                    ),
                    ft.Row(controls=[self.service_name_input]),
                ],
                spacing=4,
            ),
            bgcolor=input_bg,
            border_radius=ft.BorderRadius(top_left=8, top_right=8, bottom_left=0, bottom_right=0),
            padding=ft.Padding(left=16, top=10, right=16, bottom=8),
            border=ft.Border(bottom=ft.BorderSide(1.5, OUTLINE)),
        )

        login_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "ログインID",
                        color=ON_SURFACE_VARIANT,
                        size=11,
                        weight=ft.FontWeight.W_500,
                        font_family="Inter",
                    ),
                    ft.Row(
                        controls=[
                            self.login_id_input,
                        ],
                    ),
                ],
                spacing=4,
            ),
            bgcolor=input_bg,
            border_radius=ft.BorderRadius(top_left=8, top_right=8, bottom_left=0, bottom_right=0),
            padding=ft.Padding(left=16, top=10, right=16, bottom=8),
            border=ft.Border(bottom=ft.BorderSide(1.5, OUTLINE)),
        )

        password_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "パスワード",
                        color=ON_SURFACE_VARIANT,
                        size=11,
                        weight=ft.FontWeight.W_500,
                        font_family="Inter",
                    ),
                    ft.Row(
                        controls=[
                            self.password_input,
                            self.password_toggle_btn,
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=4,
            ),
            bgcolor=input_bg,
            border_radius=ft.BorderRadius(top_left=8, top_right=8, bottom_left=0, bottom_right=0),
            padding=ft.Padding(left=16, top=10, right=16, bottom=8),
            border=ft.Border(bottom=ft.BorderSide(1.5, OUTLINE)),
        )

        # 4. ヘッダーアイコンの切り替え
        header_icon = (
            ft.Icons.ADD_MODERATOR_OUTLINED
            if "登録" in title_text or "Add" in title_text
            else ft.Icons.EDIT_NOTE_OUTLINED
        )

        # 5. ダイアログ全体のコンテンツコンテナ
        dialog_content = ft.Container(
            bgcolor=SURFACE_CONTAINER_LOW,
            border_radius=32,
            width=560,
            padding=24,
            content=ft.Column(
                controls=[
                    # Header
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(header_icon, color=ON_PRIMARY_CONTAINER, size=24),
                                bgcolor=PRIMARY_CONTAINER,
                                border_radius=24,
                                width=48,
                                height=48,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text(
                                title_text,
                                size=32,
                                weight=ft.FontWeight.W_400,
                                color=ON_SURFACE,
                                font_family="Inter",
                            ),
                        ],
                        spacing=16,
                    ),
                    ft.Container(height=16),
                    # Form Fields
                    ft.Column(
                        controls=[
                            service_container,
                            login_container,
                            password_container,
                        ],
                        spacing=20,
                    ),
                    ft.Container(height=16),
                    # Actions
                    ft.Row(
                        controls=[
                            ft.TextButton(
                                "キャンセル",
                                on_click=lambda _: on_cancel(),
                                style=ft.ButtonStyle(
                                    color=PRIMARY,
                                    shape=ft.RoundedRectangleBorder(radius=24),
                                    overlay_color=ft.Colors.with_opacity(0.05, PRIMARY),
                                ),
                                height=40,
                            ),
                            ft.FilledButton(
                                "保存する",
                                on_click=lambda _: on_save(
                                    (self.service_name_input.value or "").strip(),
                                    (self.login_id_input.value or "").strip(),
                                    (self.password_input.value or "").strip(),
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor=PRIMARY,
                                    color=SURFACE_CONTAINER_LOWEST,
                                    shape=ft.RoundedRectangleBorder(radius=24),
                                ),
                                height=40,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=12,
                    ),
                ],
                tight=True,
            ),
        )

        super().__init__(
            modal=True,
            content_padding=0,
            bgcolor="transparent",
            content=dialog_content,
            on_dismiss=lambda _: on_cancel(),
        )

    def _toggle_password(self) -> None:
        """パスワード表示/非表示を切り替えます."""
        self.password_input.password = not self.password_input.password
        self.password_toggle_btn.icon = (
            ft.Icons.VISIBILITY_OUTLINED
            if self.password_input.password
            else ft.Icons.VISIBILITY_OFF_OUTLINED
        )
        self.password_toggle_btn.update()
        self.password_input.update()
