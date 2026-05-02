"""クリップボード操作 - OS依存の処理 (Infrastructure Layer)."""

import threading

import pyperclip


class MacClipboardService:
    """macOS (またはその他のOS) のクリップボード操作を提供するサービス."""

    def __init__(self) -> None:
        self._clear_timer: threading.Timer | None = None
        self._last_copied_text: str | None = None

    def copy(self, text: str, clear_after: int = 0) -> None:
        """テキストをクリップボードにコピーする.

        Args:
            text: コピーするテキスト.
            clear_after: 指定秒数後にクリップボードと内部状態をクリアする.  # noqa: E501
                0以下の場合はクリアしない.
        """
        pyperclip.copy(text)
        self._last_copied_text = text

        # 既存のタイマーがあればキャンセル
        if self._clear_timer is not None:
            self._clear_timer.cancel()
            self._clear_timer = None

        if clear_after > 0:
            # 指定秒数後にクリア処理を実行するタイマーをセット
            self._clear_timer = threading.Timer(
                clear_after, self._clear_clipboard_if_unchanged, args=[text]
            )
            self._clear_timer.daemon = True
            self._clear_timer.start()

    def _clear_clipboard_if_unchanged(self, expected_text: str) -> None:
        """クリップボードの内容が変更されていなければクリアする."""
        current_clipboard = pyperclip.paste()
        if current_clipboard == expected_text:
            pyperclip.copy("")
            self._last_copied_text = None
