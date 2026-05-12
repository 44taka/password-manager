"""メインウィンドウコンポーネント."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from password_manager.domain.account import Account
from password_manager.presentation.theme.styles import (
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    LIST_WIDGET_STYLE,
    MAIN_WINDOW_STYLE,
    PRIMARY_BUTTON_STYLE,
    SEARCH_BOX_STYLE,
    SEARCH_INPUT_STYLE,
)
from password_manager.presentation.views.account_card import AccountCard


class MainWindow(QMainWindow):
    """リッチなダークテーマメインウィンドウ."""

    search_requested = Signal(str)
    copy_password_requested = Signal(str)
    copy_username_requested = Signal(str)
    edit_requested = Signal(str)
    delete_requested = Signal(str)
    save_requested = Signal(object, str, str, str)
    add_account_requested = Signal()

    def __init__(self) -> None:
        """MainWindow を初期化します。"""
        super().__init__()
        self._accounts: list[Account] = []

        self.setWindowTitle("Password Manager")
        self.resize(700, 500)
        self._center_on_screen()

        # 全体をダークテーマの背景色に
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # トップバー (タイトル、検索 ＆ 追加)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(16)

        title_label = QLabel("Password Manager")
        title_label.setStyleSheet(
            f"font-size: 24px; font-weight: 800; color: {COLOR_TEXT_PRIMARY};"
        )
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        # 検索ボックス
        search_bg = QFrame()
        search_bg.setStyleSheet(SEARCH_BOX_STYLE)
        search_bg.setFixedSize(250, 40)
        search_layout = QHBoxLayout(search_bg)
        search_layout.setContentsMargins(12, 0, 12, 0)
        search_layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 14px;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("検索...")
        self.search_input.setStyleSheet(SEARCH_INPUT_STYLE)
        self.search_input.textChanged.connect(self.search_requested.emit)
        search_layout.addWidget(self.search_input)

        top_layout.addWidget(search_bg)

        # 追加ボタン
        self.add_btn = QPushButton("＋ 新規登録")
        self.add_btn.setFixedSize(120, 40)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.add_btn.clicked.connect(self.add_account_requested.emit)
        top_layout.addWidget(self.add_btn)

        main_layout.addLayout(top_layout)

        # リストウィジェット
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(LIST_WIDGET_STYLE)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        main_layout.addWidget(self.list_widget)

    def _center_on_screen(self) -> None:
        screen = self.screen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    @Slot(list)
    def update_results(self, accounts: list[Account]) -> None:
        """検索結果リストを更新します。

        Args:
            accounts: 表示するアカウントのリスト。
        """
        self._accounts = accounts
        self.list_widget.clear()

        for account in accounts:
            item = QListWidgetItem(self.list_widget)

            # 各行をカードとして生成
            card = AccountCard(account)

            # シグナルをウィンドウにフォワード
            card.copy_password_requested.connect(self.copy_password_requested.emit)
            card.copy_username_requested.connect(self.copy_username_requested.emit)
            card.edit_requested.connect(self.edit_requested.emit)
            card.delete_requested.connect(self.delete_requested.emit)

            item.setSizeHint(card.sizeHint())
            self.list_widget.setItemWidget(item, card)

            item.setSizeHint(card.sizeHint())
            self.list_widget.setItemWidget(item, card)
