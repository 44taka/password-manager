"""クリップボードエラーの定義."""

from .infrastructure_error import InfrastructureError


class ClipboardError(InfrastructureError):
    """クリップボード操作に失敗した際に投げられる例外."""

    pass
