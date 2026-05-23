"""SqliteAccountStoreのユニットテスト."""

import uuid

import pytest
import pytest_mock

from password_manager.infrastructure.sqlite_account_store import SqliteAccountStore


def test_save_new_account(sqlite_store: SqliteAccountStore) -> None:
    """新規アカウントの保存ができることを確認する."""
    # Arrange
    new_id = str(uuid.uuid4())

    # Act
    sqlite_store.save(new_id, "Service A", "User A")

    # Assert
    fetched = sqlite_store.fetch_by_id(new_id)
    assert fetched is not None
    assert fetched["id"] == new_id
    assert fetched["site_name"] == "Service A"
    assert fetched["username"] == "User A"


def test_update_existing_account(sqlite_store: SqliteAccountStore) -> None:
    """既存アカウントの更新ができることを確認する."""
    # Arrange
    original_id = str(uuid.uuid4())
    sqlite_store.save(original_id, "Old Service", "Old User")

    # Act
    sqlite_store.save(original_id, "New Service", "New User")

    # Assert
    fetched = sqlite_store.fetch_by_id(original_id)
    assert fetched is not None
    assert fetched["site_name"] == "New Service"
    assert fetched["username"] == "New User"


def test_fetch_by_id_not_found(sqlite_store: SqliteAccountStore) -> None:
    """存在しないIDを指定した場合に None が返ることを確認する."""
    # Act
    fetched = sqlite_store.fetch_by_id("non-existent-uuid")

    # Assert
    assert fetched is None


def test_fetch_all(sqlite_store: SqliteAccountStore) -> None:
    """全件取得ができることを確認する."""
    # Arrange
    sqlite_store.save(str(uuid.uuid4()), "S1", "U1")
    sqlite_store.save(str(uuid.uuid4()), "S2", "U2")

    # Act
    all_entries = sqlite_store.fetch_all()

    # Assert
    assert len(all_entries) == 2
    assert any(e["site_name"] == "S1" for e in all_entries)
    assert any(e["site_name"] == "S2" for e in all_entries)


def test_delete_account(sqlite_store: SqliteAccountStore) -> None:
    """アカウントの削除ができることを確認する."""
    # Arrange
    target_id = str(uuid.uuid4())
    sqlite_store.save(target_id, "To Delete", "User")
    assert sqlite_store.fetch_by_id(target_id) is not None

    # Act
    sqlite_store.delete(target_id)

    # Assert
    assert sqlite_store.fetch_by_id(target_id) is None


def test_save_account_database_error_should_raise_database_error(
    sqlite_store: SqliteAccountStore, mocker: pytest_mock.MockerFixture
) -> None:
    """データベースへの保存に失敗した場合に DatabaseError を投げることを確認する."""
    # Arrange
    from sqlalchemy.exc import SQLAlchemyError

    from password_manager.infrastructure import DatabaseError

    # Session.commit でエラーが発生するようにモック
    mocker.patch("sqlmodel.Session.commit", side_effect=SQLAlchemyError("Connection lost"))

    # Act & Assert
    with pytest.raises(DatabaseError) as excinfo:
        sqlite_store.save(str(uuid.uuid4()), "Service", "User")
    assert "データベース操作に失敗しました" in str(excinfo.value)
