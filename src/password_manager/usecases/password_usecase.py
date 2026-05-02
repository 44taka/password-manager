"""Use Case Layer."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from injector import inject

from password_manager.domain.models import Entry
from password_manager.domain.repositories import (
    ClipboardService,
    EntryRepository,
    PasswordRepository,
)
from password_manager.search import fuzzy_search


class PasswordUseCase:
    """パスワード管理アプリケーションの主要ユースケース."""

    @inject
    def __init__(
        self,
        entry_repo: EntryRepository,
        password_repo: PasswordRepository,
        clipboard_service: ClipboardService,
    ) -> None:
        self._entry_repo = entry_repo
        self._password_repo = password_repo
        self._clipboard_service = clipboard_service

    def get_all_entries(self) -> list[Entry]:
        """全エントリを取得する."""
        return self._entry_repo.list_all()

    def search_entries(self, query: str) -> list[Entry]:
        """指定したクエリでエントリを検索する."""
        entries = self.get_all_entries()
        if not query:
            return entries
        return fuzzy_search(query, entries)

    def get_entry(self, entry_id: int) -> Entry | None:
        """エントリを取得する."""
        return self._entry_repo.get(entry_id)

    def get_password(self, entry_id: int) -> str | None:
        """パスワードを取得する."""
        return self._password_repo.get(entry_id)

    def copy_password(self, entry_id: int, clear_after: int = 15) -> bool:
        """パスワードをクリップボードにコピーする.
        
        Returns:
            bool: コピーに成功した場合はTrue.
        """
        password = self.get_password(entry_id)
        if password is None:
            return False

        self._clipboard_service.copy(password, clear_after=clear_after)
        return True

    def copy_username(self, entry_id: int, clear_after: int = 0) -> bool:
        """ユーザー名をクリップボードにコピーする.

        ユーザー名は機密情報ではないため、デフォルトでは自動クリアしない.

        Returns:
            bool: コピーに成功した場合はTrue.
        """
        entry = self.get_entry(entry_id)
        if entry is None:
            return False

        self._clipboard_service.copy(entry.username, clear_after=clear_after)
        return True

    def save_entry(
        self,
        entry_id: int | None,
        site_name: str,
        username: str,
        password: str,
    ) -> None:
        """エントリ（およびパスワード）を追加・更新する."""
        if entry_id is None:
            new_id = self._entry_repo.add(site_name, username)
            self._password_repo.save(new_id, password)
        else:
            self._entry_repo.update(entry_id, site_name=site_name, username=username)
            self._password_repo.save(entry_id, password)

    def delete_entry(self, entry_id: int) -> bool:
        """エントリとパスワードを削除する."""
        deleted = self._entry_repo.delete(entry_id)
        if deleted:
            self._password_repo.delete(entry_id)
        return deleted
