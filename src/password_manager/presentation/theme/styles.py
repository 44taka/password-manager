"""UIのスタイル定義 (QSS) を管理するモジュール."""

# カラーパレット定義 (デザインの一貫性を保つため)
COLOR_BG_MAIN = "#1c1c1e"
COLOR_BG_CARD = "#2c2c2e"
COLOR_BG_CARD_HOVER = "#3a3a3c"
COLOR_BG_DIALOG = "#1c1c1e"
COLOR_ACCENT = "#0a84ff"
COLOR_ACCENT_HOVER = "#007aff"
COLOR_DANGER_HOVER = "rgba(255, 69, 58, 0.15)"
COLOR_TEXT_PRIMARY = "#ffffff"
COLOR_TEXT_SECONDARY = "#8e8e93"
COLOR_BORDER = "rgba(255, 255, 255, 0.05)"
COLOR_BORDER_FOCUS = "#0a84ff"

# 共通アクションボタンのスタイル
ACTION_BUTTON_STYLE = """
    QPushButton {
        background: transparent;
        border: none;
        border-radius: 6px;
        font-size: 16px;
        color: #ffffff;
    }
    QPushButton:hover {
        background: %s;
    }
    QPushButton:pressed {
        background: rgba(0, 0, 0, 0.2);
    }
"""

# エントリカードのスタイル
ENTRY_CARD_STYLE = f"""
    QFrame#card {{
        background-color: {COLOR_BG_CARD};
        border-radius: 12px;
        border: 1px solid {COLOR_BORDER};
    }}
    QFrame#card:hover {{
        background-color: {COLOR_BG_CARD_HOVER};
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
"""

# カード内アイコンのスタイル
CARD_ICON_STYLE = f"""
    QLabel {{
        background-color: {COLOR_ACCENT};
        color: {COLOR_TEXT_PRIMARY};
        border-radius: 8px;
        font-weight: bold;
        font-size: 18px;
    }}
"""

# ダイアログ背景のスタイル
DIALOG_BG_STYLE = f"""
    QFrame#dialogBg {{
        background-color: {COLOR_BG_DIALOG};
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
"""

# 入力フィールドのスタイル
INPUT_FIELD_STYLE = f"""
    QLineEdit {{
        background: {COLOR_BG_CARD};
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0 12px;
        color: {COLOR_TEXT_PRIMARY};
        font-size: 15px;
        height: 40px;
    }}
    QLineEdit:focus {{
        border: 1px solid {COLOR_BORDER_FOCUS};
        background: {COLOR_BG_CARD_HOVER};
    }}
"""

# セカンダリボタン (キャンセルなど)
SECONDARY_BUTTON_STYLE = f"""
    QPushButton {{
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 10px;
        color: {COLOR_TEXT_PRIMARY};
        font-size: 14px;
        font-weight: 500;
    }}
    QPushButton:hover {{ background: rgba(255, 255, 255, 0.1); }}
"""

# プライマリボタン (保存など)
PRIMARY_BUTTON_STYLE = f"""
    QPushButton {{
        background: {COLOR_ACCENT};
        border: none;
        border-radius: 8px;
        padding: 10px;
        color: {COLOR_TEXT_PRIMARY};
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
"""

# メインウィンドウ全体の背景
MAIN_WINDOW_STYLE = f"QMainWindow {{ background-color: {COLOR_BG_MAIN}; }}"

# 検索ボックス背景
SEARCH_BOX_STYLE = (
    f"background: {COLOR_BG_CARD}; border-radius: 10px; border: 1px solid {COLOR_BORDER};"
)

# 検索入力
SEARCH_INPUT_STYLE = (
    f"background: transparent; border: none; color: {COLOR_TEXT_PRIMARY}; font-size: 14px;"
)

# リストウィジェット
LIST_WIDGET_STYLE = """
    QListWidget {
        background: transparent;
        border: none;
        outline: none;
    }
    QListWidget::item {
        background: transparent;
        border: none;
        padding-bottom: 8px;
    }
    QListWidget::item:selected {
        background: transparent;
    }
"""
