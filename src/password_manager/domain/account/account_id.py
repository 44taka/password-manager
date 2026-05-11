"""AccountIDの定義."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountID:
    """アカウントを一意に識別するID."""

    value: int

    def __int__(self) -> int:
        """整数に変換する."""
        return self.value
