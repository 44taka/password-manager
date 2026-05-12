"""クリップボード操作 - OS依存の処理 (Infrastructure Layer)."""

from __future__ import annotations

import pyperclip

from password_manager.usecases.interfaces import ClipboardService


class MacClipboardService(ClipboardService):
    """macOS (またはその他のOS) のクリップボード操作を提供するサービス."""

    def __init__(self) -> None:
        """MacClipboardService を初期化します。"""
        self._last_text: str | None = None

    def copy(self, text: str) -> bool:
        """テキストをクリップボードにコピーします。

        Args:
            text: コピーするテキスト。

        Returns:
            成功した場合は True。
        """
        try:
            pyperclip.copy(text)
            self._last_text = text
            return True
        except Exception:
            return False

    def clear(self) -> None:
        """クリップボードの内容を消去します。

        ユーザーがコピー後に別のテキストをコピーしていた場合は消去しません。
        """
        try:
            # 現在の内容が自分が最後にコピーしたものと同じ場合のみクリア
            if self._last_text and pyperclip.paste() == self._last_text:
                pyperclip.copy("")
        except Exception:  # noqa: S110
            pass
        finally:
            self._last_text = None
