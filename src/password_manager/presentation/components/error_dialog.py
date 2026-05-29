"""Flet版 エラー表示用ダイアログコンポーネント."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

# ==============================================================================
# カラー定義
# ==============================================================================
PRIMARY = "#374379"
ON_SURFACE = "#1b1b1f"
ON_SURFACE_VARIANT = "#45464f"
SURFACE_CONTAINER_HIGH = "#eae7ed"
SURFACE_CONTAINER_LOWEST = "#ffffff"
ERROR = "#ba1a1a"


class ErrorDialog(ft.AlertDialog):
    """エラーメッセージをユーザーに通知するためのマテリアルデザイン3風ダイアログ."""

    def __init__(self, message: str, on_close: Callable[[], None]) -> None:
        """ErrorDialog を初期化します。

        Args:
            message: ダイアログ中央に表示するエラー詳細メッセージ。
            on_close: 「閉じる」ボタンが押下された際のコールバック。
        """
        # ダイアログのコンテンツの組み立て
        dialog_content = ft.Container(
            bgcolor=SURFACE_CONTAINER_HIGH,
            border_radius=28,
            width=320,
            padding=24,
            content=ft.Column(
                controls=[
                    # 赤色エラーアイコン
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.ERROR_OUTLINE, color=ERROR, size=32),
                                bgcolor="#ffdad6",  # error-container = #ffdad6
                                border_radius=24,
                                width=48,
                                height=48,
                                alignment=ft.Alignment(0, 0),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    # タイトル
                    ft.Text(
                        "エラーが発生しました",
                        size=22,
                        color=ON_SURFACE,
                        font_family="Inter",
                        weight=ft.FontWeight.W_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    # エラーメッセージ本文
                    ft.Text(
                        message,
                        size=14,
                        color=ON_SURFACE_VARIANT,
                        font_family="Inter",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),  # 余白
                    # アクション（閉じるボタン）
                    ft.Row(
                        controls=[
                            ft.FilledButton(
                                "閉じる",
                                on_click=lambda _: on_close(),
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
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
        )

        super().__init__(
            modal=True,
            content_padding=0,
            bgcolor="transparent",
            content=dialog_content,
        )
