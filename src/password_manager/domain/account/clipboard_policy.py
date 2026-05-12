"""クリップボードのセキュリティポリシー定義."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ClipboardPolicy:
    """機密情報のクリップボード保持に関するルールを定義する値オブジェクト."""

    retention_seconds: int = 15

    def is_expired(self, copied_at: datetime, current_time: datetime) -> bool:
        """コピーした情報が保持期限を過ぎているか判定します。

        Args:
            copied_at: コピーを実行した時刻。
            current_time: 現在の時刻。

        Returns:
            期限切れの場合は True。
        """
        elapsed = (current_time - copied_at).total_seconds()
        return elapsed >= self.retention_seconds
