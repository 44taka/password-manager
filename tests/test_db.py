"""EntryStore のユニットテスト."""

import sqlite3
from pathlib import Path

import pytest

from password_manager.db import EntryStore


@pytest.fixture
def store(tmp_path: Path) -> EntryStore:
    """テスト用のインメモリDBを使ったEntryStore."""
    db_path = tmp_path / "test.db"
    return EntryStore(db_path)


class TestEntryStoreAdd:
    """add() のテスト."""

    def test_add_returns_id(self, store: EntryStore) -> None:
        entry_id = store.add("GitHub", "user@example.com")
        assert entry_id == 1

    def test_add_multiple_entries(self, store: EntryStore) -> None:
        id1 = store.add("GitHub", "user1@example.com")
        id2 = store.add("Google", "user2@example.com")
        assert id1 == 1
        assert id2 == 2

    def test_add_with_notes(self, store: EntryStore) -> None:
        entry_id = store.add("GitHub", "user@example.com", notes="個人用")
        entry = store.get(entry_id)
        assert entry is not None
        assert entry.notes == "個人用"


class TestEntryStoreGet:
    """get() のテスト."""

    def test_get_existing_entry(self, store: EntryStore) -> None:
        entry_id = store.add("GitHub", "user@example.com")
        entry = store.get(entry_id)
        assert entry is not None
        assert entry.site_name == "GitHub"
        assert entry.username == "user@example.com"

    def test_get_nonexistent_entry(self, store: EntryStore) -> None:
        entry = store.get(999)
        assert entry is None


class TestEntryStoreListAll:
    """list_all() のテスト."""

    def test_list_all_empty(self, store: EntryStore) -> None:
        entries = store.list_all()
        assert entries == []

    def test_list_all_with_entries(self, store: EntryStore) -> None:
        store.add("GitHub", "user1@example.com")
        store.add("Google", "user2@example.com")
        entries = store.list_all()
        assert len(entries) == 2

    def test_list_all_sorted_by_site_name(self, store: EntryStore) -> None:
        store.add("Zoom", "user@example.com")
        store.add("Amazon", "user@example.com")
        store.add("GitHub", "user@example.com")
        entries = store.list_all()
        site_names = [e.site_name for e in entries]
        assert site_names == ["Amazon", "GitHub", "Zoom"]


class TestEntryStoreUpdate:
    """update() のテスト."""

    def test_update_site_name(self, store: EntryStore) -> None:
        entry_id = store.add("GitHab", "user@example.com")  # typo
        result = store.update(entry_id, site_name="GitHub")
        assert result is True
        entry = store.get(entry_id)
        assert entry is not None
        assert entry.site_name == "GitHub"

    def test_update_nonexistent(self, store: EntryStore) -> None:
        result = store.update(999, site_name="GitHub")
        assert result is False

    def test_update_preserves_unchanged_fields(self, store: EntryStore) -> None:
        entry_id = store.add("GitHub", "user@example.com", notes="メモ")
        store.update(entry_id, site_name="GitHub Enterprise")
        entry = store.get(entry_id)
        assert entry is not None
        assert entry.username == "user@example.com"
        assert entry.notes == "メモ"


class TestEntryStoreDelete:
    """delete() のテスト."""

    def test_delete_existing(self, store: EntryStore) -> None:
        entry_id = store.add("GitHub", "user@example.com")
        result = store.delete(entry_id)
        assert result is True
        assert store.get(entry_id) is None

    def test_delete_nonexistent(self, store: EntryStore) -> None:
        result = store.delete(999)
        assert result is False
