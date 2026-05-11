"""クリップボード操作 - OS依存の処理 (Infrastructure Layer)."""

from __future__ import annotations

import threading

import pyperclip

from password_manager.domain.account import ClipboardService


class MacClipboardService(ClipboardService):
    """macOS (またはその他のOS) のクリップボード操作を提供するサービス."""

    def __init__(self) -> None:
        """MacClipboardServiceを初期化します."""
        self._timer: threading.Timer | None = None

    def copy(self, text: str, clear_after: int | None = None) -> bool:
        """テキストをクリップボードにコピーします。."""
        try:
            pyperclip.copy(text)

            # 以前のタイマーがあればキャンセル
            if self._timer:
                self._timer.cancel()

            if clear_after:
                self._timer = threading.Timer(clear_after, self._clear_clipboard)
                self._timer.start()

            return True
        except Exception:
            return False

    def _clear_clipboard(self) -> None:
        """クリップボードの内容を消去します。."""
        try:
            pyperclip.copy("")
        except Exception:  # noqa: S110
            pass
        finally:
            self._timer = None
