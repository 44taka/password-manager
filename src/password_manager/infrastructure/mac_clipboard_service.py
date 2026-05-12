"""クリップボード操作 - OS依存の処理 (Infrastructure Layer)."""

from __future__ import annotations

import pyperclip

from password_manager.usecases.interfaces import ClipboardService


class MacClipboardService(ClipboardService):
    """macOS (またはその他のOS) のクリップボード操作を提供するサービス."""

    def copy(self, text: str) -> bool:
        """テキストをクリップボードにコピーします。

        Args:
            text: コピーするテキスト。

        Returns:
            成功した場合は True。
        """
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False

    def clear(self, text: str) -> None:
        """指定されたテキストが現在のクリップボードの内容と一致する場合のみ消去します。

        Args:
            text: 消去対象のテキスト。
        """
        try:
            # 現在の内容が指定されたものと同じ場合のみクリア
            if pyperclip.paste() == text:
                pyperclip.copy("")
        except Exception:  # noqa: S110
            pass
