"""共通のアクションボタンコンポーネント."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

from password_manager.presentation.theme.styles import (
    ACTION_BUTTON_STYLE,
    COLOR_DANGER_HOVER,
)


class ActionButton(QPushButton):
    """洗練されたアクションアイコンボタン."""

    def __init__(
        self,
        icon_text: str,
        tooltip: str,
        is_danger: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        """ActionButton を初期化します。

        Args:
            icon_text: ボタンに表示するテキスト（アイコン絵文字等）。
            tooltip: ツールチップテキスト。
            is_danger: 危険なアクション（削除等）かどうか。デフォルトは False。
            parent: 親ウィジェット。
        """
        super().__init__(icon_text, parent)
        self.setFixedSize(32, 32)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 色設定
        hover_bg = COLOR_DANGER_HOVER if is_danger else "rgba(255, 255, 255, 0.1)"
        self.setStyleSheet(ACTION_BUTTON_STYLE % hover_bg)
