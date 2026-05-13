"""データベースエラーの定義."""

from .infrastructure_error import InfrastructureError


class DatabaseError(InfrastructureError):
    """データベース操作に失敗した際に投げられる例外."""

    pass
