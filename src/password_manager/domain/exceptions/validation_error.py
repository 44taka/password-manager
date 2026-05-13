"""バリデーションエラーの定義."""

from .domain_error import DomainError


class ValidationError(DomainError):
    """入力値の妥当性検証に失敗した際に投げられる例外."""

    pass
