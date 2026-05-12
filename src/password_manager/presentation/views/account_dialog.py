"""アカウント追加・編集用のダイアログ."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from password_manager.presentation.theme.styles import (
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    DIALOG_BG_STYLE,
    INPUT_FIELD_STYLE,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
)


class AccountDialog(QDialog):
    """マテリアル/フラットデザイン風の角丸ダイアログ."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """AccountDialog を初期化します。

        Args:
            parent: 親ウィジェット。
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(380, 420)
        self.old_pos = self.pos()

        # 影を含めた全体のレイアウト
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 実際のダイアログ背景
        self.bg = QFrame()
        self.bg.setObjectName("dialogBg")
        self.bg.setStyleSheet(DIALOG_BG_STYLE)

        # ドロップシャドウ
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        self.bg.setGraphicsEffect(shadow)

        main_layout.addWidget(self.bg)

        # ダイアログ内のレイアウト
        layout = QVBoxLayout(self.bg)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # タイトル
        self.title_label = QLabel("新規登録")
        self.title_label.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};"
        )
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # フォーム
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)

        def make_field(placeholder: str, is_password: bool = False) -> QLineEdit:
            inp = QLineEdit()
            inp.setStyleSheet(INPUT_FIELD_STYLE)
            inp.setPlaceholderText(placeholder)
            if is_password:
                inp.setEchoMode(QLineEdit.EchoMode.Password)
            return inp

        self.site_input = make_field("サイト名 (例: GitHub)")
        self.user_input = make_field("ユーザー名")
        self.pass_input = make_field("パスワード", True)

        label_style = f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px;"
        site_label = QLabel("📝 サイト名")
        site_label.setStyleSheet(label_style)
        form_layout.addWidget(site_label)
        form_layout.addWidget(self.site_input)
        user_label = QLabel("👤 ユーザー名")
        user_label.setStyleSheet(label_style)
        form_layout.addWidget(user_label)
        form_layout.addWidget(self.user_input)
        pass_label = QLabel("🔑 パスワード")
        pass_label.setStyleSheet(label_style)
        form_layout.addWidget(pass_label)
        form_layout.addWidget(self.pass_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # ボタン
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_cancel = QPushButton("キャンセル")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(SECONDARY_BUTTON_STYLE)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("保存する")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.btn_save.clicked.connect(self.accept)
        self.btn_save.setDefault(True)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

    def get_data(self) -> tuple[str, str, str]:
        """ダイアログに入力されたデータを取得します。

        Returns:
            tuple[str, str, str]: (サイト名, ユーザー名, パスワード) のタプル。
        """
        return (
            self.site_input.text().strip(),
            self.user_input.text().strip(),
            self.pass_input.text().strip(),
        )

    def set_data(self, title: str, site: str, user: str, pwd: str) -> None:
        """ダイアログの初期データを設定します。

        Args:
            title: ダイアログのタイトル。
            site: サイト名の初期値。
            user: ユーザー名の初期値。
            pwd: パスワードの初期値。
        """
        self.title_label.setText(title)
        self.site_input.setText(site)
        self.user_input.setText(user)
        self.pass_input.setText(pwd)
        self.site_input.setFocus()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """マウス押下時の処理。ウィンドウ移動の開始点を記録します。

        Args:
            event: マウスイベント情報。
        """
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """マウス移動時の処理。ウィンドウをドラッグ移動させます。

        Args:
            event: マウスイベント情報。
        """
        delta = event.globalPosition().toPoint() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()
