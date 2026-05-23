"""ServiceName値オブジェクトの定義."""

from dataclasses import dataclass

from password_manager.domain.exceptions import ValidationError


@dataclass(frozen=True)
class ServiceName:
    """アカウントのサービス名を表す値オブジェクト."""

    value: str

    def __post_init__(self) -> None:
        """バリデーションを行います。

        Raises:
            ValidationError: サービス名が空の場合。
        """
        if not self.value:
            raise ValidationError("サービス名は必須です。")

    def __str__(self) -> str:
        """サービス名の文字列値を返します。

        Returns:
            サービス名の文字列。
        """
        return self.value
