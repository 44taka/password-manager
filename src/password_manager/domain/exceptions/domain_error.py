"""ドメイン層の基底例外クラスの定義."""

from password_manager.core.exceptions import AppError


class DomainError(AppError):
    """ドメイン層で発生する例外の基底クラス."""

    pass
