"""クリップボード操作のインターフェース."""

from typing import Protocol


class ClipboardService(Protocol):
    """クリップボード操作を抽象化するサービス."""

    def copy(self, text: str, clear_after: int | None = None) -> bool:
        """テキストをクリップボードにコピーします。.

        Args:
            text: コピーするテキスト。
            clear_after: 指定された秒数後にクリップボードをクリアします。

        Returns:
            bool: 成功した場合は True。
        """
        ...
