"""macOS Keychainによるパスワードの永続化を担当するストア."""

import keyring
import keyring.errors

SERVICE_NAME = "password-manager"


class MacosKeychainStore:
    """macOS Keychainを用いたパスワードの管理."""

    def __init__(self, service_name: str = SERVICE_NAME) -> None:
        """MacosKeychainStoreを初期化します."""
        self._service_name = service_name

    def save(self, account_id: int, password: str) -> None:
        """パスワードをKeychainに保存します."""
        keyring.set_password(self._service_name, str(account_id), password)

    def get(self, account_id: int) -> str | None:
        """Keychainからパスワードを取得します."""
        return keyring.get_password(self._service_name, str(account_id))

    def delete(self, account_id: int) -> None:
        """Keychainからパスワードを削除します."""
        try:
            keyring.delete_password(self._service_name, str(account_id))
        except keyring.errors.PasswordDeleteError:
            # 存在しない場合は無視
            pass
