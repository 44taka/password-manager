"""クリップボード操作 - OS依存の処理 (Infrastructure Layer)."""

from __future__ import annotations

import pyperclip

from password_manager.core.logger import get_logger
from password_manager.infrastructure.exceptions import ClipboardError
from password_manager.usecases.interfaces import ClipboardService

logger = get_logger(__name__)


class MacClipboardService(ClipboardService):
    """macOS向けのクリップボード操作サービス."""

    def copy(self, text: str) -> bool:
        """テキストをクリップボードにコピーします。

        Args:
            text: コピーするテキスト。

        Returns:
            成功した場合はTrue。

        Raises:
            ClipboardError: コピーに失敗した場合。
        """
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            msg = "クリップボードへのコピーに失敗しました"
            logger.warning(
                msg,
                extra={
                    "event": "clipboard_copy",
                    "context": {"error": str(e)},
                },
            )
            raise ClipboardError(f"{msg}: {e}") from e

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
