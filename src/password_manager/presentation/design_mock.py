"""Flet版 code.htmlのデザイン再現モックアプリケーション."""

from __future__ import annotations

import random
import string
import threading
import time
from collections.abc import Callable

import flet as ft
import pyperclip

# ==============================================================================
# カラー定義 (code.html の tailwind.config より抽出)
# ==============================================================================
PRIMARY = "#374379"
PRIMARY_CONTAINER = "#4f5b92"
ON_PRIMARY_CONTAINER = "#d0d6ff"
SURFACE = "#fbf8fe"
SURFACE_CONTAINER_LOW = "#f6f2f8"
SURFACE_CONTAINER = "#f0edf2"
SURFACE_CONTAINER_HIGH = "#eae7ed"
SURFACE_CONTAINER_HIGHEST = "#e4e1e7"
SURFACE_CONTAINER_LOWEST = "#ffffff"
BACKGROUND = "#fbf8fe"
ON_SURFACE = "#1b1b1f"
ON_SURFACE_VARIANT = "#45464f"
OUTLINE = "#767680"
OUTLINE_VARIANT = "#c6c5d1"
TERTIARY = "#5d3c55"
ERROR = "#ba1a1a"
ON_SECONDARY_FIXED_VARIANT = "#434559"


class MockAccountCard(ft.Container):
    """code.htmlのパスワードエントリカードをFletで再現したコンポーネント.

    ホバー時に背景色と枠線が滑らかに変化し、右側のアクションボタンがフェードインします。
    """

    def __init__(
        self,
        service_name: str,
        login_id: str,
        icon_name: ft.IconData | str,
        icon_color: str,
        show_extra_actions: bool = False,
    ) -> None:
        """MockAccountCard を初期化します。

        Args:
            service_name: サービス名。
            login_id: ログインID。
            icon_name: マテリアルアイコン名。
            icon_color: アイコンのカラーコード。
            show_extra_actions: 追加のアクションを表示するかどうか。
        """
        super().__init__()
        self.service_name = service_name
        self.login_id = login_id

        # アクションボタン群 (右側)
        self.action_buttons: list[ft.Control] = []

        if show_extra_actions:
            # 各種バリエーションに合わせたボタン配置
            if service_name == "Amazon":
                # Amazon はコピーとメニューボタン
                self.action_buttons = [
                    self._create_action_button(
                        ft.Icons.CONTENT_COPY, "コピー", self._on_copy_clicked
                    ),
                    self._create_action_button(ft.Icons.MORE_VERT, "詳細", None),
                ]
            elif service_name == "GitHub":
                # GitHub はコピーとスターボタン
                self.action_buttons = [
                    self._create_action_button(
                        ft.Icons.CONTENT_COPY, "コピー", self._on_copy_clicked
                    ),
                    self._create_action_button(ft.Icons.STAR_BORDER, "お気に入り", None),
                ]
            else:
                # デフォルトはコピーのみ
                self.action_buttons = [
                    self._create_action_button(
                        ft.Icons.CONTENT_COPY, "コピー", self._on_copy_clicked
                    ),
                ]
        else:
            # Googleのようにフルアクションを持つ場合
            self.action_buttons = [
                self._create_action_button(
                    ft.Icons.PERSON_OUTLINE,
                    "ユーザー名をコピー",
                    self._on_user_copy_clicked,
                ),
                self._create_action_button(
                    ft.Icons.CONTENT_COPY, "パスワードをコピー", self._on_copy_clicked
                ),
                self._create_action_button(ft.Icons.OPEN_IN_NEW, "開く", None),
            ]

        # 削除ボタン
        self.action_buttons.append(
            self._create_action_button(
                ft.Icons.DELETE_OUTLINE, "削除", self._on_delete_clicked
            )
        )

        self.action_row = ft.Row(
            controls=self.action_buttons,
            spacing=8,
            opacity=0.0,  # 初期状態は非表示
            animate_opacity=200,  # 200ms でフェードイン・アウト
        )

        # UIの組み立て
        self.content = ft.Row(
            controls=[
                # 左側：アイコン ＆ テキスト
                ft.Row(
                    controls=[
                        # アイコンコンテナ
                        ft.Container(
                            content=ft.Icon(
                                icon_name,  # type: ignore
                                color=icon_color,
                                size=24,
                            ),
                            width=48,
                            height=48,
                            bgcolor=SURFACE_CONTAINER_HIGHEST,
                            border_radius=12,
                            alignment=ft.Alignment(0, 0),  # 中央揃え
                        ),
                        # テキスト（サービス名 ＆ ログインID）
                        ft.Column(
                            controls=[
                                ft.Text(
                                    service_name,
                                    size=16,
                                    weight=ft.FontWeight.W_500,
                                    color=ON_SURFACE,
                                    font_family="Inter",
                                ),
                                ft.Text(
                                    login_id,
                                    size=14,
                                    color=ON_SURFACE_VARIANT,
                                    font_family="Inter",
                                ),
                            ],
                            spacing=2,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
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
        on_click: Callable[[ft.ControlEvent], None] | None,
    ) -> ft.Control:
        """アクション用アイコンボタンを作成します."""
        return ft.IconButton(
            icon=icon,
            icon_size=20,
            tooltip=tooltip,
            on_click=on_click,  # type: ignore
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

    def _on_copy_clicked(self, e: ft.ControlEvent) -> None:
        """パスワードコピー時のインタラクション."""
        control = e.control
        if not isinstance(control, ft.IconButton):
            return

        page = e.page
        if not isinstance(page, ft.Page):
            return

        # クリップボードコピー
        pyperclip.copy("mock_password_value_123")

        # スナックバー表示
        snack_bar = ft.SnackBar(
            content=ft.Text(
                "パスワードをクリップボードにコピーしました 🔑",
                color="#ffffff",
                font_family="Inter",
            ),
            bgcolor=PRIMARY,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

        # ボタンのアイコンをチェックマークに変えるマイクロインタラクション
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

    def _on_user_copy_clicked(self, e: ft.ControlEvent) -> None:
        """ユーザー名コピー時のインタラクション."""
        control = e.control
        if not isinstance(control, ft.IconButton):
            return

        page = e.page
        if not isinstance(page, ft.Page):
            return

        # クリップボードコピー
        pyperclip.copy(self.login_id)

        # スナックバー表示
        snack_bar = ft.SnackBar(
            content=ft.Text(
                "ログインIDをクリップボードにコピーしました 👤",
                color="#ffffff",
                font_family="Inter",
            ),
            bgcolor=PRIMARY,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

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

    def _on_delete_clicked(self, e: ft.ControlEvent) -> None:
        """削除ボタンクリック時の処理."""
        page = e.page
        if isinstance(page, ft.Page):
            show_delete_confirm_dialog(page, self)


def create_add_service_dialog(
    page: ft.Page, entry_list: ft.Column
) -> tuple[ft.AlertDialog, Callable[[ft.ControlEvent], None]]:
    """Add New Service モーダルを作成します."""
    # フィールド変数を定義
    service_name_input = ft.TextField(
        hint_text="e.g. Netflix, Github",
        border=ft.InputBorder.NONE,
        border_width=0,
        border_color="transparent",
        text_style=ft.TextStyle(color=ON_SURFACE, size=16, font_family="Inter"),
        content_padding=ft.Padding(left=0, top=0, right=0, bottom=0),
        height=28,
        expand=True,
    )
    
    login_id_input = ft.TextField(
        hint_text="Username or Email",
        border=ft.InputBorder.NONE,
        border_width=0,
        border_color="transparent",
        text_style=ft.TextStyle(color=ON_SURFACE, size=16, font_family="Inter"),
        content_padding=ft.Padding(left=0, top=0, right=0, bottom=0),
        height=28,
        expand=True,
    )
    
    password_input = ft.TextField(
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

    # パスワード表示切り替えイベント
    def toggle_password(e: ft.ControlEvent) -> None:
        password_input.password = not password_input.password
        password_toggle_btn.icon = (
            ft.Icons.VISIBILITY_OUTLINED if password_input.password else ft.Icons.VISIBILITY_OFF_OUTLINED
        )
        password_toggle_btn.update()
        password_input.update()

    password_toggle_btn = ft.IconButton(
        icon=ft.Icons.VISIBILITY_OUTLINED,
        icon_size=20,
        icon_color=ON_SURFACE_VARIANT,
        on_click=toggle_password,
        style=ft.ButtonStyle(
            shape=ft.CircleBorder(),
            overlay_color=ft.Colors.with_opacity(0.1, ON_SURFACE_VARIANT),
        ),
        width=36,
        height=36,
    )

    # パスワード生成イベント
    def generate_password(e: ft.ControlEvent) -> None:
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+"
        pwd = "".join(random.choice(chars) for _ in range(16))
        password_input.value = pwd
        password_input.password = False  # 生成時は一旦パスワードを見せる
        password_toggle_btn.icon = ft.Icons.VISIBILITY_OFF_OUTLINED
        
        # 一時的にテキストの色を PRIMARY にしてマイクロインタラクションを再現
        password_input.text_style = ft.TextStyle(color=PRIMARY, size=16, font_family="Inter")
        password_input.update()
        password_toggle_btn.update()
        
        def reset_color() -> None:
            time.sleep(0.5)
            password_input.text_style = ft.TextStyle(color=ON_SURFACE, size=16, font_family="Inter")
            password_input.update()
            
        threading.Thread(target=reset_color, daemon=True).start()
    
    password_gen_btn = ft.IconButton(
        icon=ft.Icons.CASINO_OUTLINED,
        icon_size=20,
        icon_color=PRIMARY,
        on_click=generate_password,
        style=ft.ButtonStyle(
            shape=ft.CircleBorder(),
            overlay_color=ft.Colors.with_opacity(0.1, PRIMARY),
        ),
        width=36,
        height=36,
    )

    # ダイアログを閉じる
    def close_dialog(e: ft.ControlEvent) -> None:
        dialog.open = False
        page.update()

    # 保存処理
    def save_clicked(e: ft.ControlEvent) -> None:
        if service_name_input.value:
            # 入力された内容でカードを追加
            name_lower = service_name_input.value.lower()
            icon = ft.Icons.LANGUAGE
            color = PRIMARY
            if "git" in name_lower:
                icon = ft.Icons.TERMINAL
                color = ON_SURFACE
            elif "amazon" in name_lower:
                icon = ft.Icons.SHOPPING_CART
                color = TERTIARY
            elif "netflix" in name_lower:
                icon = ft.Icons.MOVIE
                color = ERROR
            elif "spotify" in name_lower:
                icon = ft.Icons.MUSIC_NOTE
                color = ON_SECONDARY_FIXED_VARIANT
            
            new_card = MockAccountCard(
                service_name=service_name_input.value,
                login_id=login_id_input.value or "no-username",
                icon_name=icon,
                icon_color=color,
                show_extra_actions=True,
            )
            entry_list.controls.insert(0, new_card)
            entry_list.update()

            # スナックバー表示
            snack_bar = ft.SnackBar(
                content=ft.Text(
                    f"{service_name_input.value} を追加しました 🎉",
                    color="#ffffff",
                    font_family="Inter",
                ),
                bgcolor=PRIMARY,
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            dialog.open = False
            page.update()
        else:
            # Service Name が空の場合はエラーダイアログを表示
            show_error_dialog(page, "An unexpected error has occurred. Please try again later.")

    # UIの組み立て (HTMLのmodalを忠実に再現)
    input_bg = ft.Colors.with_opacity(0.4, SURFACE_CONTAINER_HIGHEST) # surface-variant/40 と完全に一致
    
    # 各入力フィールドのコンテナ
    service_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Service Name",
                    color=ON_SURFACE_VARIANT,
                    size=11,
                    weight=ft.FontWeight.W_500,
                    font_family="Inter",
                ),
                ft.Row(
                    controls=[
                        service_name_input,
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

    login_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Login ID",
                    color=ON_SURFACE_VARIANT,
                    size=11,
                    weight=ft.FontWeight.W_500,
                    font_family="Inter",
                ),
                ft.Row(
                    controls=[
                        login_id_input,
                        ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, color=ON_SURFACE_VARIANT, size=24),
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

    password_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Password",
                    color=ON_SURFACE_VARIANT,
                    size=11,
                    weight=ft.FontWeight.W_500,
                    font_family="Inter",
                ),
                ft.Row(
                    controls=[
                        password_input,
                        ft.Row(
                            controls=[
                                password_toggle_btn,
                                password_gen_btn,
                            ],
                            spacing=4,
                        ),
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

    # ダイアログ全体のコンテンツ
    dialog_content = ft.Container(
        bgcolor=SURFACE_CONTAINER_LOW,
        border_radius=32, # rounded-lg = 2rem = 32px
        width=560, # max-w-[560px]
        padding=24, # p-xl = 24px
        content=ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        # Icon Container
                        ft.Container(
                            content=ft.Icon(ft.Icons.ADD_MODERATOR_OUTLINED, color=ON_PRIMARY_CONTAINER, size=24),
                            bgcolor=PRIMARY_CONTAINER,
                            border_radius=24,
                            width=48,
                            height=48,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(
                            "Add New Service",
                            size=32,
                            weight=ft.FontWeight.W_400,
                            color=ON_SURFACE,
                            font_family="Inter",
                        ),
                    ],
                    spacing=16,
                ),
                ft.Container(height=16), # 余白
                # Form Fields
                ft.Column(
                    controls=[
                        service_container,
                        login_container,
                        password_container,
                    ],
                    spacing=20,
                ),
                ft.Container(height=16), # 余白
                # Actions
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Cancel",
                            on_click=close_dialog,
                            style=ft.ButtonStyle(
                                color=PRIMARY,
                                shape=ft.RoundedRectangleBorder(radius=24),
                                overlay_color=ft.Colors.with_opacity(0.05, PRIMARY),
                            ),
                            height=40,
                        ),
                        ft.FilledButton(
                            "Save",
                            on_click=save_clicked,
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

    dialog = ft.AlertDialog(
        modal=True,
        content_padding=0,
        bgcolor="transparent",
        content=dialog_content,
    )
    
    def show_dialog(e: ft.ControlEvent) -> None:
        print("DEBUG: show_dialog called")
        service_name_input.value = ""
        login_id_input.value = ""
        password_input.value = ""
        password_input.password = True
        password_toggle_btn.icon = ft.Icons.VISIBILITY_OUTLINED
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()
        
    return dialog, show_dialog


def show_delete_confirm_dialog(page: ft.Page, card: MockAccountCard) -> None:
    """Delete service? 削除確認ダイアログを表示します."""
    def yes_clicked(e: ft.ControlEvent) -> None:
        parent = card.parent
        if isinstance(parent, ft.Column):
            parent.controls.remove(card)
            parent.update()
        
        # スナックバー表示
        snack_bar = ft.SnackBar(
            content=ft.Text(
                f"{card.service_name} を削除しました 🗑️",
                color="#ffffff",
                font_family="Inter",
            ),
            bgcolor=PRIMARY,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        
        dialog.open = False
        page.update()

    def no_clicked(e: ft.ControlEvent) -> None:
        dialog.open = False
        page.update()

    # w-full max-w-[312px] bg-surface-container-highest rounded-lg p-xl flex flex-col gap-lg shadow-2xl
    dialog_content = ft.Container(
        bgcolor=SURFACE_CONTAINER_HIGHEST, # e4e1e7
        border_radius=28, # rounded-lg = 28px
        width=312, # max-w-[312px]
        padding=24, # p-xl = 24px
        content=ft.Column(
            controls=[
                # Icon
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.DELETE_OUTLINE, color=ON_SURFACE_VARIANT, size=24),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                # Title
                ft.Text(
                    "Delete service?",
                    size=22,
                    color=ON_SURFACE,
                    font_family="Inter",
                    weight=ft.FontWeight.W_400,
                    text_align=ft.TextAlign.CENTER,
                ),
                # Body Text
                ft.Text(
                    f"This will permanently remove the {card.service_name} credentials from your vault. This action cannot be undone.",
                    size=14,
                    color=ON_SURFACE_VARIANT,
                    font_family="Inter",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8), # 余白
                # Actions (No / Yes)
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "No",
                            on_click=no_clicked,
                            style=ft.ButtonStyle(
                                color=PRIMARY,
                                overlay_color=ft.Colors.with_opacity(0.05, PRIMARY),
                            ),
                        ),
                        ft.TextButton(
                            "Yes",
                            on_click=yes_clicked,
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
            spacing=16, # gap-lg
            tight=True,
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        content_padding=0,
        bgcolor="transparent",
        content=dialog_content,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def show_error_dialog(page: ft.Page, message: str) -> None:
    """An error occurred エラーダイアログを表示します."""
    def close_clicked(e: ft.ControlEvent) -> None:
        dialog.open = False
        page.update()

    # bg-surface-container-high rounded-xl max-w-[312px] md:max-w-[400px] w-full p-xl shadow-lg
    dialog_content = ft.Container(
        bgcolor=SURFACE_CONTAINER_HIGH, # #eae7ed
        border_radius=28, # rounded-xl = 3rem = 48pxだが、ダイアログ用に28px
        width=320, # max-w-[312px]
        padding=24, # p-xl = 24px
        content=ft.Column(
            controls=[
                # Icon
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.ERROR_OUTLINE, color=ERROR, size=32),
                            bgcolor="#ffdad6", # error-container = #ffdad6
                            border_radius=24,
                            width=48,
                            height=48,
                            alignment=ft.Alignment(0, 0),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                # Title
                ft.Text(
                    "An error occurred",
                    size=22,
                    color=ON_SURFACE,
                    font_family="Inter",
                    weight=ft.FontWeight.W_400,
                    text_align=ft.TextAlign.CENTER,
                ),
                # Body Text
                ft.Text(
                    message,
                    size=14,
                    color=ON_SURFACE_VARIANT,
                    font_family="Inter",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8), # 余白
                # Actions (Close)
                ft.Row(
                    controls=[
                        ft.FilledButton(
                            "Close",
                            on_click=close_clicked,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY,
                                color=SURFACE_CONTAINER_LOWEST,
                                shape=ft.RoundedRectangleBorder(radius=24),
                            ),
                            width=120,
                            height=40,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=16, # gap-lg
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        content_padding=0,
        bgcolor="transparent",
        content=dialog_content,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def main(page: ft.Page) -> None:
    """デザインモックのメイン関数."""
    page.title = "Vaultly - Secure Password Manager (Design Mock)"
    page.bgcolor = BACKGROUND

    # ウィンドウの初期サイズ
    page.window.width = 1280
    page.window.height = 1000
    page.window.resizable = False

    # Google Fonts から Inter を読み込む
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap"
    }

    # ==============================================================================
    # 1. メインコンテンツ (先に定義してダイアログを準備)
    # ==============================================================================

    # セクションタイトル
    content_title = ft.Text(
        "All Service",
        size=32,
        weight=ft.FontWeight.W_400,
        color=ON_SURFACE,
        font_family="Inter",
    )

    # エントリリスト
    entry_list = ft.Column(
        controls=[
            MockAccountCard("Google", "alex.rivera@gmail.com", ft.Icons.LANGUAGE, PRIMARY),
            MockAccountCard(
                "GitHub",
                "arivera-dev",
                ft.Icons.TERMINAL,
                ON_SURFACE,
                show_extra_actions=True,
            ),
            MockAccountCard(
                "Amazon",
                "alex.rivera@gmail.com",
                ft.Icons.SHOPPING_CART,
                TERTIARY,
                show_extra_actions=True,
            ),
            MockAccountCard(
                "Netflix",
                "family_account@rivera.me",
                ft.Icons.MOVIE,
                ERROR,
                show_extra_actions=True,
            ),
            MockAccountCard(
                "Spotify",
                "arivera-dev",
                ft.Icons.MUSIC_NOTE,
                ON_SECONDARY_FIXED_VARIANT,
                show_extra_actions=True,
            ),
        ],
        spacing=12,
    )

    # ダイアログの作成と紐付け
    add_service_dialog, show_add_service_modal = create_add_service_dialog(page, entry_list)
    page.dialog = add_service_dialog

    # ==============================================================================
    # 2. ヘッダー (TopAppBar)
    # ==============================================================================

    # 検索フィールド
    search_field = ft.TextField(
        hint_text="Search services...",
        hint_style=ft.TextStyle(color=ON_SURFACE_VARIANT, font_family="Inter", size=16),
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(left=0, top=0, right=0, bottom=12),
        text_style=ft.TextStyle(color=ON_SURFACE, font_family="Inter", size=16),
        expand=True,
        height=40,
    )

    # HTML: bg-surface-container-high rounded-full h-12 px-lg transition-all hover:bg-surface-container-highest
    search_container = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SEARCH, color=ON_SURFACE_VARIANT, size=24),
                search_field,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=SURFACE_CONTAINER_HIGH,
        border_radius=24,
        padding=ft.Padding(left=16, top=0, right=16, bottom=0),
        height=48,
        width=672,  # HTML: max-w-2xl = 672px
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),  # transition-all 相当
    )

    def _handle_search_hover(e: ft.ControlEvent) -> None:
        """検索コンテナのホバー時背景色変化 (hover:bg-surface-container-highest)."""
        is_hovered = e.data in (True, "true")
        search_container.bgcolor = (
            SURFACE_CONTAINER_HIGHEST if is_hovered else SURFACE_CONTAINER_HIGH
        )
        search_container.update()

    search_container.on_hover = _handle_search_hover  # type: ignore

    # アクションボタン（新規登録）
    # HTML: bg-primary-container (#4f5b92) + text-on-primary-container (#d0d6ff)
    add_button = ft.FilledButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD, color=ON_PRIMARY_CONTAINER, size=20),
                ft.Text(
                    "Add New Service",
                    color=ON_PRIMARY_CONTAINER,
                    weight=ft.FontWeight.W_500,
                    font_family="Inter",
                    size=14,
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=PRIMARY_CONTAINER,  # bg-primary-container = #4f5b92
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=24),
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
        ),
        height=44,
        on_click=show_add_service_modal,
    )

    # ヘッダー内のコンテンツコンテナ (最大幅制限用)
    header_content = ft.Container(
        content=ft.Row(
            controls=[
                # タイトル
                ft.Text(
                    "Password Manager",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY,
                    font_family="Inter",
                ),
                # 検索バー
                search_container,
                # 追加ボタン
                add_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
    )

    header = ft.Container(
        content=ft.Row(
            controls=[header_content],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=24, top=0, right=24, bottom=0),
        height=64,
        bgcolor=SURFACE,
    )

    # 同期ステータスカード (Fletの制限により、Dashed of Solidの薄いボーダー)
    sync_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.VERIFIED_USER_OUTLINED, color=OUTLINE, size=48),
                ft.Text(
                    "Your vault is synchronized",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=ON_SURFACE_VARIANT,
                    font_family="Inter",
                ),
                ft.Text(
                    "All entries are encrypted with your master key.",
                    size=14,
                    color=OUTLINE,
                    font_family="Inter",
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=SURFACE_CONTAINER_LOWEST,
        border=ft.Border(
            top=ft.BorderSide(1.5, OUTLINE_VARIANT),
            bottom=ft.BorderSide(1.5, OUTLINE_VARIANT),
            left=ft.BorderSide(1.5, OUTLINE_VARIANT),
            right=ft.BorderSide(1.5, OUTLINE_VARIANT),
        ),
        border_radius=16,
        padding=ft.Padding(left=24, top=32, right=24, bottom=32),
        alignment=ft.Alignment(0, 0),
    )

    # スコープ制限コンテナ (横幅はon_resizeで動的制御)
    main_area = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=24),  # pt-24 相当の余白
                content_title,
                ft.Container(height=32),  # mb-xxl = 32px
                entry_list,
                ft.Container(height=24),  # 余白用透明コンテナ
                sync_card,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        expand=True,
        padding=ft.Padding(left=24, top=0, right=24, bottom=0),
    )

    # 画面全体に適用 (メインエリアを中央寄せにするため Row でラップ)
    main_row = ft.Row(
        controls=[main_area],
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )

    page.add(
        ft.Column(
            controls=[
                header,
                main_row,
            ],
            spacing=0,
            expand=True,
        )
    )

    # 横幅制限のためのレスポンシブハンドラー
    def on_resize(e: ft.PageResizeEvent | None) -> None:
        win_width = page.window.width if page.window.width else 1280
        target_width = min(win_width - 48, 1200)
        main_area.width = target_width
        header_content.width = target_width
        page.update()

    page.on_resize = on_resize  # type: ignore
    # 初回の幅計算を実行
    on_resize(None)


if __name__ == "__main__":
    ft.run(main)
