"""MacosKeychainStoreのユニットテスト."""

import uuid

from password_manager.infrastructure.macos_keychain_store import MacosKeychainStore

from .keyring_fakes import InMemoryKeyring


def test_save_and_get_password(mock_keyring: InMemoryKeyring) -> None:
    """パスワードの保存と取得ができることを確認する."""
    # Arrange
    service = "test-service"
    store = MacosKeychainStore(service_name=service)
    account_id = str(uuid.uuid4())
    password = "secret-password"  # noqa: S105

    # Act
    store.save(account_id, password)
    retrieved = store.get(account_id)

    # Assert
    assert retrieved == password
    # バックエンド側でも正しく保存されているか確認
    assert mock_keyring.get_password(service, account_id) == password


def test_get_non_existent_password(mock_keyring: InMemoryKeyring) -> None:
    """存在しないパスワードを取得しようとした場合に None が返ることを確認する."""
    # Arrange
    store = MacosKeychainStore()

    # Act
    retrieved = store.get("non-existent-uuid")

    # Assert
    assert retrieved is None


def test_delete_password(mock_keyring: InMemoryKeyring) -> None:
    """パスワードが削除できることを確認する."""
    # Arrange
    store = MacosKeychainStore()
    account_id = str(uuid.uuid4())
    store.save(account_id, "to-be-deleted")

    # Act
    store.delete(account_id)

    # Assert
    assert store.get(account_id) is None


def test_delete_non_existent_password_no_error(mock_keyring: InMemoryKeyring) -> None:
    """存在しないパスワードを削除しようとしてもエラーにならないことを確認する."""
    # Arrange
    store = MacosKeychainStore()

    # Act & Assert
    # エラーが発生しなければパス
    store.delete("non-existent-uuid")
