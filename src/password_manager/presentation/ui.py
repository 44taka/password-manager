"""リッチでモダンなカード型デスクトップUI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
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

if TYPE_CHECKING:
    from password_manager.domain.models import Entry


class ActionButton(QPushButton):
    """洗練されたアクションアイコンボタン."""

    def __init__(self, icon_text: str, tooltip: str, is_danger: bool = False, parent=None):
        super().__init__(icon_text, parent)
        self.setFixedSize(32, 32)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 色設定
        hover_bg = "rgba(255, 69, 58, 0.15)" if is_danger else "rgba(255, 255, 255, 0.1)"

        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                color: #ffffff;
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
            QPushButton:pressed {{
                background: rgba(0, 0, 0, 0.2);
            }}
        """)


class EntryCardWidget(QFrame):
    """リスト内に表示する角丸のカードウィジェット."""

    copy_password_requested = Signal(int)
    copy_username_requested = Signal(int)
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, entry: Entry, parent=None):
        super().__init__(parent)
        self.entry = entry

        # カード自体の基本スタイル
        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card {
                background-color: #2c2c2e;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            QFrame#card:hover {
                background-color: #3a3a3c;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # アイコン領域 (アプリカラー風の四角)
        self.icon_label = QLabel(entry.site_name[0].upper() if entry.site_name else "?")
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: #0a84ff;
                color: #ffffff;
                border-radius: 8px;
                font-weight: bold;
                font-size: 18px;
            }
        """)
        layout.addWidget(self.icon_label)

        # テキスト情報領域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.site_label = QLabel(entry.site_name)
        self.site_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff;")

        self.user_label = QLabel(entry.username)
        self.user_label.setStyleSheet("font-size: 13px; color: #8e8e93;")

        info_layout.addWidget(self.site_label)
        info_layout.addWidget(self.user_label)
        layout.addLayout(info_layout)
        layout.addStretch()

        # アクション領域 (デフォルトは非表示にしておき、ホバー時などに表示する)
        self.actions_widget = QWidget()
        actions_layout = QHBoxLayout(self.actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        btn_copy_pwd = ActionButton("🔑", "パスワードをコピー")
        btn_copy_pwd.clicked.connect(lambda: self.copy_password_requested.emit(self.entry.id))

        btn_copy_user = ActionButton("👤", "ユーザー名をコピー")
        btn_copy_user.clicked.connect(lambda: self.copy_username_requested.emit(self.entry.id))

        btn_edit = ActionButton("✏️", "編集")
        btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.entry.id))

        btn_delete = ActionButton("🗑️", "削除", is_danger=True)
        btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.entry.id))

        actions_layout.addWidget(btn_copy_pwd)
        actions_layout.addWidget(btn_copy_user)
        actions_layout.addWidget(btn_edit)
        actions_layout.addWidget(btn_delete)

        self.actions_widget.setGraphicsEffect(self._create_fade_effect())
        self.setAlphaMultiplier(0.0)  # 初期状態は見えない

        layout.addWidget(self.actions_widget)

    def _create_fade_effect(self) -> QGraphicsOpacityEffect:
        # より滑らかな表示のための基礎
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.0)
        return effect

    def setAlphaMultiplier(self, alpha: float) -> None:
        effect = self.actions_widget.graphicsEffect()
        if isinstance(effect, QGraphicsOpacityEffect):
            effect.setOpacity(alpha)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setAlphaMultiplier(1.0)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setAlphaMultiplier(0.0)


class CustomDialog(QDialog):
    """マテリアル/フラットデザイン風の角丸ダイアログ."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(380, 420)

        # 影を含めた全体のレイアウト
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 実際のダイアログ背景
        self.bg = QFrame()
        self.bg.setObjectName("dialogBg")
        self.bg.setStyleSheet("""
            QFrame#dialogBg {
                background-color: #1c1c1e;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

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
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # フォーム
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)

        input_style = """
            QLineEdit {
                background: #2c2c2e;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 0 12px;
                color: #ffffff;
                font-size: 15px;
                height: 40px;
            }
            QLineEdit:focus {
                border: 1px solid #0a84ff;
                background: #3a3a3c;
            }
        """

        def make_field(placeholder, is_password=False):
            inp = QLineEdit()
            inp.setStyleSheet(input_style)
            inp.setPlaceholderText(placeholder)
            if is_password:
                inp.setEchoMode(QLineEdit.EchoMode.Password)
            return inp

        self.site_input = make_field("サイト名 (例: GitHub)")
        self.user_input = make_field("ユーザー名")
        self.pass_input = make_field("パスワード", True)

        label_style = "color: #8e8e93; font-size: 13px;"
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
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover { background: rgba(255, 255, 255, 0.1); }
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("保存する")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: #0a84ff;
                border: none;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #007aff; }
        """)
        self.btn_save.clicked.connect(self.accept)
        self.btn_save.setDefault(True)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

    def get_data(self) -> tuple[str, str, str]:
        return (
            self.site_input.text().strip(),
            self.user_input.text().strip(),
            self.pass_input.text().strip(),
        )

    def set_data(self, title: str, site: str, user: str, pwd: str) -> None:
        self.title_label.setText(title)
        self.site_input.setText(site)
        self.user_input.setText(user)
        self.pass_input.setText(pwd)
        self.site_input.setFocus()

    def mousePressEvent(self, event):
        # ウィンドウのドラッグ移動対応
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()


class MainWindow(QMainWindow):
    """リッチなダークテーマメインウィンドウ."""

    search_requested = Signal(str)
    copy_password_requested = Signal(int)
    copy_username_requested = Signal(int)
    edit_requested = Signal(int)
    delete_requested = Signal(int)
    save_requested = Signal(object, str, str, str)

    def __init__(self) -> None:
        super().__init__()
        self._entries: list[Entry] = []

        self.setWindowTitle("Password Manager")
        self.resize(700, 500)
        self._center_on_screen()

        # 全体をダークテーマの背景色に
        self.setStyleSheet("QMainWindow { background-color: #1c1c1e; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # トップバー (タイトル、検索 ＆ 追加)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(16)

        title_label = QLabel("Password Manager")
        title_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #ffffff;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        # 検索ボックス (丸みを帯びたデザイン)
        search_bg = QFrame()
        search_bg_style = (
            "background: #2c2c2e; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);"
        )
        search_bg.setStyleSheet(search_bg_style)
        search_bg.setFixedSize(250, 40)
        search_layout = QHBoxLayout(search_bg)
        search_layout.setContentsMargins(12, 0, 12, 0)
        search_layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color: #8e8e93; font-size: 14px;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("検索...")
        search_input_style = (
            "background: transparent; border: none; color: #ffffff; font-size: 14px;"
        )
        self.search_input.setStyleSheet(search_input_style)
        self.search_input.textChanged.connect(self.search_requested.emit)
        search_layout.addWidget(self.search_input)

        top_layout.addWidget(search_bg)

        # 追加ボタン
        self.add_btn = QPushButton("＋ 新規登録")
        self.add_btn.setFixedSize(120, 40)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #0a84ff;
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #007aff; }
        """)
        self.add_btn.clicked.connect(self.show_add_form)
        top_layout.addWidget(self.add_btn)

        main_layout.addLayout(top_layout)

        # リストウィジェット (テーブルではなくカードのリスト表示用)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                padding-bottom: 8px; /* カード間の隙間 */
            }
            QListWidget::item:selected {
                background: transparent;
            }
        """)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        main_layout.addWidget(self.list_widget)

    def _center_on_screen(self) -> None:
        screen = self.screen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def update_results(self, entries: list[Entry]) -> None:
        self._entries = entries
        self.list_widget.clear()

        for entry in entries:
            item = QListWidgetItem(self.list_widget)

            # 各行をカードとして生成
            card = EntryCardWidget(entry)

            # シグナルをウィンドウにフォワード
            card.copy_password_requested.connect(self.copy_password_requested.emit)
            card.copy_username_requested.connect(self.copy_username_requested.emit)
            card.edit_requested.connect(self.edit_requested.emit)
            card.delete_requested.connect(self.delete_requested.emit)

            item.setSizeHint(card.sizeHint())
            self.list_widget.setItemWidget(item, card)

    def show_add_form(self) -> None:
        dialog = CustomDialog(self)
        dialog.set_data("新規登録", "", "", "")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            site, user, pwd = dialog.get_data()
            if site and pwd:
                self.save_requested.emit(None, site, user, pwd)

    def show_edit_form(self, entry_id: int, site: str, user: str, pwd: str) -> None:
        dialog = CustomDialog(self)
        dialog.set_data("パスワードの編集", site, user, pwd)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_site, new_user, new_pwd = dialog.get_data()
            if new_site and new_pwd:
                self.save_requested.emit(entry_id, new_site, new_user, new_pwd)
