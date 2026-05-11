"""テスト用の keyring 関連の Fake 実装."""

import keyring
from keyring.backend import KeyringBackend


class InMemoryKeyring(KeyringBackend):
    """テスト用のインメモリ keyring バックエンド."""

    priority = 1

    def __init__(self) -> None:
        """InMemoryKeyring を初期化します."""
        self._passwords: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, username: str) -> str | None:
        """パスワードを取得します.

        Args:
            service: サービス名。
            username: ユーザー名。

        Returns:
            str | None: パスワード。存在しない場合は None。
        """
        return self._passwords.get((service, username))

    def set_password(self, service: str, username: str, password: str) -> None:
        """パスワードを保存します.

        Args:
            service: サービス名。
            username: ユーザー名。
            password: 保存するパスワード。
        """
        self._passwords[(service, username)] = password

    def delete_password(self, service: str, username: str) -> None:
        """パスワードを削除します.

        Args:
            service: サービス名。
            username: ユーザー名。

        Raises:
            keyring.errors.PasswordDeleteError: パスワードが存在しない場合。
        """
        if (service, username) in self._passwords:
            del self._passwords[(service, username)]
        else:
            raise keyring.errors.PasswordDeleteError(f"Password not found for {service}/{username}")
