"""クリップボード操作のインターフェース (Application Services Layer)."""

from typing import Protocol


class ClipboardService(Protocol):
    """アプリケーションが要求するクリップボード操作のインターフェース."""

    def copy(self, text: str) -> bool:
        """テキストをクリップボードにコピーします。

        Args:
            text: コピーするテキスト。

        Returns:
            成功した場合は True。
        """
        ...

    def clear(self) -> None:
        """クリップボードの内容を消去します。"""
        ...
