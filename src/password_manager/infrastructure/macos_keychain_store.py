"""macOS Keychainによるパスワードの永続化を担当するストア."""

import keyring
import keyring.errors

SERVICE_NAME = "password-manager"


class MacosKeychainStore:
    """macOS Keychainを用いたパスワードの管理."""

    def __init__(self, service_name: str = SERVICE_NAME) -> None:
        """MacosKeychainStore を初期化します。

        Args:
            service_name: Keychain で使用するサービス名。
        """
        self._service_name = service_name

    def save(self, account_id: int, password: str) -> None:
        """パスワードを Keychain に保存します。

        Args:
            account_id: アカウントID。
            password: 保存するパスワード。
        """
        keyring.set_password(self._service_name, str(account_id), password)

    def get(self, account_id: int) -> str | None:
        """Keychain からパスワードを取得します。

        Args:
            account_id: 取得対象のアカウントID。

        Returns:
            取得したパスワード。存在しない場合は None。
        """
        return keyring.get_password(self._service_name, str(account_id))

    def delete(self, account_id: int) -> None:
        """Keychain からパスワードを削除します。

        Args:
            account_id: 削除対象のアカウントID。
        """
        try:
            keyring.delete_password(self._service_name, str(account_id))
        except keyring.errors.PasswordDeleteError:
            # 存在しない場合は無視
            pass
