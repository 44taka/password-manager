"""AccountIDの定義."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountID:
    """アカウントを一意に識別するID."""

    value: int

    def __int__(self) -> int:
        """IDの整数値を返します。

        Returns:
            アカウントIDの整数値。
        """
        return self.value
