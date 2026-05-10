"""SqliteEntryRepository のユニットテスト."""

from password_manager.infrastructure.sqlite_entry_repository import (
    SqliteEntryRepository,
)


class TestEntryStoreAdd:
    """add() のテスト."""

    def test_add_returns_id(self, store: SqliteEntryRepository) -> None:
        """エントリを追加した際、生成された ID が正しく返ることをテストします。."""
        entry_id = store.add("GitHub", "user@example.com")
        assert entry_id == 1

    def test_add_multiple_entries(self, store: SqliteEntryRepository) -> None:
        """複数のエントリを追加した際、ID がインクリメントされることをテストします。."""
        id1 = store.add("GitHub", "user1@example.com")
        id2 = store.add("Google", "user2@example.com")
        assert id1 == 1
        assert id2 == 2

    def test_add_with_notes(self, store: SqliteEntryRepository) -> None:
        """備考付きでエントリを追加した際、備考が正しく保存されることをテストします。."""
        entry_id = store.add("GitHub", "user@example.com", notes="個人用")
        entry = store.get(entry_id)
        assert entry is not None
        assert entry.notes == "個人用"


class TestEntryStoreGet:
    """get() のテスト."""

    def test_get_existing_entry(self, store: SqliteEntryRepository) -> None:
        """存在するエントリの ID を指定して、正しく情報が取得できることをテストします。."""
        entry_id = store.add("GitHub", "user@example.com")
        entry = store.get(entry_id)
        assert entry is not None
        assert entry.site_name == "GitHub"
        assert entry.username == "user@example.com"

    def test_get_nonexistent_entry(self, store: SqliteEntryRepository) -> None:
        """存在しないエントリの ID を指定した際、None が返ることをテストします。."""
        entry = store.get(999)
        assert entry is None


class TestEntryStoreListAll:
    """list_all() のテスト."""

    def test_list_all_empty(self, store: SqliteEntryRepository) -> None:
        """エントリが 1 つも登録されていない場合、空のリストが返ることをテストします。."""
        entries = store.list_all()
        assert entries == []

    def test_list_all_with_entries(self, store: SqliteEntryRepository) -> None:
        """登録されているすべてのエントリが正しく取得できることをテストします。."""
        store.add("GitHub", "user1@example.com")
        store.add("Google", "user2@example.com")
        entries = store.list_all()
        assert len(entries) == 2

    def test_list_all_sorted_by_site_name(self, store: SqliteEntryRepository) -> None:
        """取得されるエントリ一覧がサイト名の昇順でソートされていることをテストします。."""
        store.add("Zoom", "user@example.com")
        store.add("Amazon", "user@example.com")
        store.add("GitHub", "user@example.com")
        entries = store.list_all()
        site_names = [e.site_name for e in entries]
        assert site_names == ["Amazon", "GitHub", "Zoom"]


class TestEntryStoreUpdate:
    """update() のテスト."""

    def test_update_site_name(self, store: SqliteEntryRepository) -> None:
        """エントリのサイト名を正しく更新できることをテストします。."""
        entry_id = store.add("GitHab", "user@example.com")  # typo
        result = store.update(entry_id, site_name="GitHub")
        assert result is True
        entry = store.get(entry_id)
        assert entry is not None
        assert entry.site_name == "GitHub"

    def test_update_nonexistent(self, store: SqliteEntryRepository) -> None:
        """存在しないエントリを更新しようとした際、False が返ることをテストします。."""
        result = store.update(999, site_name="GitHub")
        assert result is False

    def test_update_preserves_unchanged_fields(self, store: SqliteEntryRepository) -> None:
        """一部のフィールドのみを更新した際、他のフィールドが維持されることをテストします。."""
        entry_id = store.add("GitHub", "user@example.com", notes="メモ")
        store.update(entry_id, site_name="GitHub Enterprise")
        entry = store.get(entry_id)
        assert entry is not None
        assert entry.username == "user@example.com"
        assert entry.notes == "メモ"


class TestEntryStoreDelete:
    """delete() のテスト."""

    def test_delete_existing(self, store: SqliteEntryRepository) -> None:
        """存在するエントリを正しく削除できることをテストします。."""
        entry_id = store.add("GitHub", "user@example.com")
        result = store.delete(entry_id)
        assert result is True
        assert store.get(entry_id) is None

    def test_delete_nonexistent(self, store: SqliteEntryRepository) -> None:
        """存在しないエントリを削除しようとした際、False が返ることをテストします。."""
        result = store.delete(999)
        assert result is False
