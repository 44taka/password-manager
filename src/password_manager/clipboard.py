"""クリップボード操作 - パスワードのコピーと自動クリア."""

from __future__ import annotations

import threading

import pyperclip


def copy_to_clipboard(text: str, clear_after: int = 15) -> None:
    """テキストをクリップボードにコピーし、指定秒数後に自動クリアする.

    Args:
        text: コピーするテキスト
        clear_after: 自動クリアまでの秒数 (0以下の場合はクリアしない)
    """
    pyperclip.copy(text)

    if clear_after > 0:
        timer = threading.Timer(clear_after, _clear_if_unchanged, args=[text])
        timer.daemon = True
        timer.start()


def _clear_if_unchanged(original_text: str) -> None:
    """クリップボードの内容が変わっていなければクリアする."""
    try:
        current = pyperclip.paste()
        if current == original_text:
            pyperclip.copy("")
    except Exception:
        # クリップボード操作に失敗しても静かに無視
        pass
