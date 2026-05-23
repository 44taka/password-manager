"""LoginID値オブジェクトの定義."""

from dataclasses import dataclass

from password_manager.domain.exceptions import ValidationError


@dataclass(frozen=True)
class LoginID:
    """アカウントのログインIDを表す値オブジェクト."""

    value: str

    def __post_init__(self) -> None:
        """バリデーションを行います。

        Raises:
            ValidationError: ログインIDが空の場合。
        """
        if not self.value:
            raise ValidationError("ログインIDは必須です。")

    def __str__(self) -> str:
        """ログインIDの文字列値を返します。

        Returns:
            ログインIDの文字列。
        """
        return self.value
