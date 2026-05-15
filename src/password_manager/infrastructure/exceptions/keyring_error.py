"""キーチェーンエラーの定義."""

from .infrastructure_error import InfrastructureError


class KeyringError(InfrastructureError):
    """キーチェーン（Keychain）操作に失敗した際に投げられる例外."""

    pass
