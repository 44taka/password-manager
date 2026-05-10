"""Use Case Layer."""

from __future__ import annotations

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
        """PasswordUseCase を初期化します。.

        Args:
            entry_repo: エントリを管理するリポジトリ。
            password_repo: パスワードを管理するリポジトリ。
            clipboard_service: クリップボード操作を提供するサービス。
        """
        self._entry_repo = entry_repo
        self._password_repo = password_repo
        self._clipboard_service = clipboard_service

    def get_all_entries(self) -> list[Entry]:
        """全エントリを取得します。.

        Returns:
            list[Entry]: 取得したエントリのリスト。
        """
        return self._entry_repo.list_all()

    def search_entries(self, query: str) -> list[Entry]:
        """指定したクエリでエントリを検索します。.

        Args:
            query: 検索クエリ。

        Returns:
            list[Entry]: ヒットしたエントリのリスト。
        """
        entries = self.get_all_entries()
        if not query:
            return entries
        return fuzzy_search(query, entries)

    def get_entry(self, entry_id: int) -> Entry | None:
        """指定した ID のエントリを取得します。.

        Args:
            entry_id: 取得対象のエントリ ID。

        Returns:
            Entry | None: 見つかった場合はエントリ、そうでない場合は None。
        """
        return self._entry_repo.get(entry_id)

    def get_password(self, entry_id: int) -> str | None:
        """指定した ID のパスワードを取得します。.

        Args:
            entry_id: パスワードを取得する対象のエントリ ID。

        Returns:
            str | None: 見つかった場合はパスワード文字列、そうでない場合は None。
        """
        return self._password_repo.get(entry_id)

    def copy_password(self, entry_id: int, clear_after: int = 15) -> bool:
        """パスワードをクリップボードにコピーします。.

        Args:
            entry_id: コピー対象のエントリ ID。
            clear_after: クリップボードをクリアするまでの秒数。デフォルトは15秒。

        Returns:
            bool: コピーに成功した場合は True、そうでない場合は False。
        """
        password = self.get_password(entry_id)
        if password is None:
            return False

        self._clipboard_service.copy(password, clear_after=clear_after)
        return True

    def copy_username(self, entry_id: int, clear_after: int = 0) -> bool:
        """ユーザー名をクリップボードにコピーします。.

        ユーザー名は機密情報ではないため、デフォルトでは自動クリアしません。

        Args:
            entry_id: コピー対象のエントリ ID。
            clear_after: クリップボードをクリアするまでの秒数。0 の場合はクリアしません。

        Returns:
            bool: コピーに成功した場合は True、そうでない場合は False。
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
        """エントリ（およびパスワード）を追加または更新します。.

        Keychainへの保存に失敗した場合は、RuntimeError を発生させます。

        Args:
            entry_id: 更新対象の ID。新規追加の場合は None。
            site_name: サイト名。
            username: ユーザー名。
            password: パスワード。

        Raises:
            RuntimeError: Keychain への保存に失敗した場合。
        """
        target_id = entry_id
        if target_id is None:
            # 新規追加
            target_id = self._entry_repo.add(site_name, username)
        else:
            # 更新
            self._entry_repo.update(target_id, site_name=site_name, username=username)

        # パスワードの保存 (Keychain)
        # ここで失敗しても、SQLite側には既に保存されている状態にする
        try:
            self._password_repo.save(target_id, password)
        except Exception as e:
            raise RuntimeError(f"Keychainへの保存に失敗しました: {e}") from e

    def delete_entry(self, entry_id: int) -> bool:
        """エントリとパスワードを削除します。.

        Args:
            entry_id: 削除対象のエントリ ID。

        Returns:
            bool: 削除に成功した場合は True、そうでない場合は False。
        """
        deleted = self._entry_repo.delete(entry_id)
        if deleted:
            self._password_repo.delete(entry_id)
        return deleted
