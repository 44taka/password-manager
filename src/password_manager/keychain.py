"""macOS キーチェーン操作 - パスワードの保存・取得・削除."""

from __future__ import annotations

import keyring


# キーチェーンでこのアプリのエントリを識別するサービス名
SERVICE_NAME = "password-manager"


class KeychainManager:
    """macOS キーチェーンを使ったパスワード管理."""

    def __init__(self, service_name: str = SERVICE_NAME) -> None:
        self._service_name = service_name

    def save(self, entry_id: int, password: str) -> None:
        """パスワードをキーチェーンに保存する."""
        keyring.set_password(self._service_name, str(entry_id), password)

    def get(self, entry_id: int) -> str | None:
        """キーチェーンからパスワードを取得する."""
        return keyring.get_password(self._service_name, str(entry_id))

    def delete(self, entry_id: int) -> None:
        """キーチェーンからパスワードを削除する."""
        try:
            keyring.delete_password(self._service_name, str(entry_id))
        except keyring.errors.PasswordDeleteError:
            # パスワードが存在しない場合は無視
            pass
