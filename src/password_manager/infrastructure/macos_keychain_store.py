"""macOS Keychainによるパスワードの永続化を担当するストア."""

import keyring
import keyring.errors

from password_manager.core.logger import get_logger
from password_manager.infrastructure.exceptions import KeyringError

SERVICE_NAME = "password-manager"

logger = get_logger(__name__)


class MacosKeychainStore:
    """macOS Keychainを用いたパスワードの管理."""

    def __init__(self, service_name: str = SERVICE_NAME) -> None:
        """MacosKeychainStore を初期化します。

        Args:
            service_name: Keychain で使用するサービス名。
        """
        self._service_name = service_name

    def save(self, account_id: str, password: str) -> None:
        """パスワードを Keychain に保存します。

        Args:
            account_id: アカウントID（UUID文字列）。
            password: 保存するパスワード。
        """
        try:
            keyring.set_password(self._service_name, account_id, password)
        except keyring.errors.KeyringError as e:
            msg = "キーチェーンへの保存に失敗しました"
            logger.critical(
                msg,
                exc_info=True,
                extra={
                    "event": "keychain_access",
                    "context": {
                        "account_id": account_id,
                        "service": self._service_name,
                    },
                },
            )
            raise KeyringError(f"{msg} (account_id={account_id}): {e}") from e

    def get(self, account_id: str) -> str | None:
        """Keychain からパスワードを取得します。

        Args:
            account_id: 取得対象のアカウントID（UUID文字列）。

        Returns:
            取得したパスワード。存在しない場合は None。
        """
        return keyring.get_password(self._service_name, account_id)

    def delete(self, account_id: str) -> None:
        """Keychain からパスワードを削除します。

        Args:
            account_id: 削除対象のアカウントID（UUID文字列）。
        """
        try:
            keyring.delete_password(self._service_name, account_id)
        except keyring.errors.PasswordDeleteError:
            # 存在しない場合は無視
            pass
