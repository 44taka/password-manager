"""Domain Interfaces (Protocols)."""

from typing import Protocol

from password_manager.domain.models import Entry


class EntryRepository(Protocol):
    """パスワードエントリのメタデータを管理するリポジトリ."""

    def add(self, site_name: str, username: str, notes: str = "") -> int:
        """エントリを追加し、IDを返す."""
        ...

    def get(self, entry_id: int) -> Entry | None:
        """IDでエントリを取得する."""
        ...

    def list_all(self) -> list[Entry]:
        """全エントリを取得する."""
        ...

    def update(
        self,
        entry_id: int,
        *,
        site_name: str | None = None,
        username: str | None = None,
        notes: str | None = None,
    ) -> bool:
        """エントリを更新する. 更新があればTrueを返す."""
        ...

    def delete(self, entry_id: int) -> bool:
        """エントリを削除する. 削除があればTrueを返す."""
        ...


class PasswordRepository(Protocol):
    """パスワードの実体を安全に保存・管理するリポジトリ."""

    def save(self, entry_id: int, password: str) -> None:
        """パスワードを保存する."""
        ...

    def get(self, entry_id: int) -> str | None:
        """パスワードを取得する."""
        ...

    def delete(self, entry_id: int) -> None:
        """パスワードを削除する."""
        ...


class ClipboardService(Protocol):
    """クリップボード操作を提供するサービス."""

    def copy(self, text: str, clear_after: int = 0) -> None:
        """テキストをクリップボードにコピーする."""
        ...
