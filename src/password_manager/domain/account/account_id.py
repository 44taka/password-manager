"""AccountIDの定義."""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class AccountID:
    """アカウントを一意に識別するID."""

    value: str

    @classmethod
    def generate(cls) -> "AccountID":
        """新しいアカウントIDを生成します。

        Returns:
            生成された AccountID。
        """
        return cls(str(uuid.uuid4()))

    def __str__(self) -> str:
        """IDの文字列値を返します。

        Returns:
            アカウントIDの文字列。
        """
        return self.value
