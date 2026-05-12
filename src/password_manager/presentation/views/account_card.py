"""アカウント情報を表示するカードウィジェット."""

from __future__ import annotations

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from password_manager.domain.account import Account
from password_manager.presentation.theme.styles import (
    CARD_ICON_STYLE,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    ENTRY_CARD_STYLE,
)
from password_manager.presentation.views.action_button import ActionButton


class AccountCard(QFrame):
    """リスト内に表示する角丸のカードウィジェット."""

    copy_password_requested = Signal(str)
    copy_username_requested = Signal(str)
    edit_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, account: Account, parent: QWidget | None = None) -> None:
        """AccountCard を初期化します。

        Args:
            account: 表示対象のアカウント情報。
            parent: 親ウィジェット。
        """
        super().__init__(parent)
        self.account = account

        # カード自体の基本スタイル
        self.setObjectName("card")
        self.setStyleSheet(ENTRY_CARD_STYLE)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # アイコン領域 (アプリカラー風の四角)
        self.icon_label = QLabel(account.service_name[0].upper() if account.service_name else "?")
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(CARD_ICON_STYLE)
        layout.addWidget(self.icon_label)

        # テキスト情報領域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.service_label = QLabel(account.service_name)
        self.service_label.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};"
        )

        self.login_label = QLabel(account.login_id)
        self.login_label.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_SECONDARY};")

        info_layout.addWidget(self.service_label)
        info_layout.addWidget(self.login_label)
        layout.addLayout(info_layout)
        layout.addStretch()

        # アクション領域 (デフォルトは非表示にしておき、ホバー時などに表示する)
        self.actions_widget = QWidget()
        actions_layout = QHBoxLayout(self.actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        btn_copy_pwd = ActionButton("🔑", "パスワードをコピー")
        btn_copy_pwd.clicked.connect(
            lambda checked=False, id_=str(self.account.id): self.copy_password_requested.emit(id_)
        )

        btn_copy_user = ActionButton("👤", "ログインIDをコピー")
        btn_copy_user.clicked.connect(
            lambda checked=False, id_=str(self.account.id): self.copy_username_requested.emit(id_)
        )

        btn_edit = ActionButton("✏️", "編集")
        btn_edit.clicked.connect(
            lambda checked=False, id_=str(self.account.id): self.edit_requested.emit(id_)
        )

        btn_delete = ActionButton("🗑️", "削除", is_danger=True)
        btn_delete.clicked.connect(
            lambda checked=False, id_=str(self.account.id): self.delete_requested.emit(id_)
        )

        actions_layout.addWidget(btn_copy_pwd)
        actions_layout.addWidget(btn_copy_user)
        actions_layout.addWidget(btn_edit)
        actions_layout.addWidget(btn_delete)

        self.actions_widget.setGraphicsEffect(self._create_fade_effect())
        self.setAlphaMultiplier(0.0)  # 初期状態は見えない

        layout.addWidget(self.actions_widget)

    def _create_fade_effect(self) -> QGraphicsOpacityEffect:
        """フェード効果を生成します。

        Returns:
            QGraphicsOpacityEffect: 生成された透明度エフェクト。
        """
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.0)
        return effect

    def setAlphaMultiplier(self, alpha: float) -> None:
        """アクションボタンの透明度を設定します。

        Args:
            alpha: 透明度 (0.0 から 1.0)。
        """
        effect = self.actions_widget.graphicsEffect()
        if isinstance(effect, QGraphicsOpacityEffect):
            effect.setOpacity(alpha)

    def enterEvent(self, event: QEnterEvent) -> None:
        """マウスがウィジェットに入った際のイベント。アクションを表示します。

        Args:
            event: 入場イベント情報。
        """
        super().enterEvent(event)
        self.setAlphaMultiplier(1.0)

    def leaveEvent(self, event: QEvent) -> None:
        """マウスがウィジェットから出た際のイベント。アクションを非表示にします。

        Args:
            event: 退場イベント情報。
        """
        super().leaveEvent(event)
        self.setAlphaMultiplier(0.0)
