"""SqliteAccountStoreのユニットテスト."""

from password_manager.infrastructure.sqlite_account_store import SqliteAccountStore


def test_save_new_account(sqlite_store: SqliteAccountStore) -> None:
    """新規アカウントの保存ができることを確認する."""
    # Act
    new_id = sqlite_store.save(0, "Service A", "User A", "Memo A")

    # Assert
    assert new_id > 0
    fetched = sqlite_store.fetch_by_id(new_id)
    assert fetched is not None
    assert fetched["site_name"] == "Service A"
    assert fetched["username"] == "User A"
    assert fetched["notes"] == "Memo A"


def test_update_existing_account(sqlite_store: SqliteAccountStore) -> None:
    """既存アカウントの更新ができることを確認する."""
    # Arrange
    original_id = sqlite_store.save(0, "Old Service", "Old User", "Old Memo")

    # Act
    updated_id = sqlite_store.save(original_id, "New Service", "New User", "New Memo")

    # Assert
    assert updated_id == original_id
    fetched = sqlite_store.fetch_by_id(updated_id)
    assert fetched is not None
    assert fetched["site_name"] == "New Service"
    assert fetched["username"] == "New User"
    assert fetched["notes"] == "New Memo"


def test_fetch_by_id_not_found(sqlite_store: SqliteAccountStore) -> None:
    """存在しないIDを指定した場合に None が返ることを確認する."""
    # Act
    fetched = sqlite_store.fetch_by_id(999)

    # Assert
    assert fetched is None


def test_fetch_all(sqlite_store: SqliteAccountStore) -> None:
    """全件取得ができることを確認する."""
    # Arrange
    sqlite_store.save(0, "S1", "U1", "M1")
    sqlite_store.save(0, "S2", "U2", "M2")

    # Act
    all_entries = sqlite_store.fetch_all()

    # Assert
    assert len(all_entries) == 2
    assert any(e["site_name"] == "S1" for e in all_entries)
    assert any(e["site_name"] == "S2" for e in all_entries)


def test_delete_account(sqlite_store: SqliteAccountStore) -> None:
    """アカウントの削除ができることを確認する."""
    # Arrange
    target_id = sqlite_store.save(0, "To Delete", "User", "Memo")
    assert sqlite_store.fetch_by_id(target_id) is not None

    # Act
    sqlite_store.delete(target_id)

    # Assert
    assert sqlite_store.fetch_by_id(target_id) is None
