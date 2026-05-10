"""macOS キーチェーン操作 - パスワードの保存・取得・削除 (Infrastructure Layer)."""

from __future__ import annotations

import keyring
import keyring.errors

# キーチェーンでこのアプリのエントリを識別するサービス名
SERVICE_NAME = "password-manager"


class MacosKeychainRepository:
    """macOS キーチェーンを使ったパスワード管理 (PasswordRepositoryの実装)."""

    def __init__(self, service_name: str = SERVICE_NAME) -> None:
        """MacosKeychainRepository を初期化します。.

        Args:
            service_name: キーチェーンで使用するサービス名。
        """
        self._service_name = service_name

    def save(self, entry_id: int, password: str) -> None:
        """パスワードをキーチェーンに保存します。.

        Args:
            entry_id: パスワードを紐付けるエントリ ID。
            password: 保存するパスワード文字列。
        """
        keyring.set_password(self._service_name, str(entry_id), password)

    def get(self, entry_id: int) -> str | None:
        """キーチェーンからパスワードを取得します。.

        Args:
            entry_id: パスワードを取得する対象のエントリ ID。

        Returns:
            str | None: 見つかった場合はパスワード、そうでない場合は None。
        """
        return keyring.get_password(self._service_name, str(entry_id))

    def delete(self, entry_id: int) -> None:
        """キーチェーンからパスワードを削除します。.

        Args:
            entry_id: 削除対象のエントリ ID。
        """
        try:
            keyring.delete_password(self._service_name, str(entry_id))
        except keyring.errors.PasswordDeleteError:
            # パスワードが存在しない場合は無視
            pass
