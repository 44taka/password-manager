"""UnifiedAccountRepositoryの統合テスト."""

from collections.abc import Generator
from pathlib import Path

import pytest

from password_manager.domain.account import Account
from password_manager.infrastructure.macos_keychain_store import MacosKeychainStore
from password_manager.infrastructure.sqlite_account_store import SqliteAccountStore
from password_manager.infrastructure.unified_account_repository import UnifiedAccountRepository

from .keyring_fakes import InMemoryKeyring


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """テスト用のテンポラリDBパス."""
    return tmp_path / "test_accounts.db"


@pytest.fixture
def keychain_store(mock_keyring: InMemoryKeyring) -> MacosKeychainStore:
    """本物の MacosKeychainStore (インメモリバックエンド使用) を提供します."""
    return MacosKeychainStore(service_name="test-service")


@pytest.fixture
def repository(
    temp_db: Path, keychain_store: MacosKeychainStore
) -> Generator[UnifiedAccountRepository]:
    """テスト対象のリポジトリ."""
    sqlite_store = SqliteAccountStore(db_path=temp_db)
    yield UnifiedAccountRepository(sqlite_store, keychain_store)
    sqlite_store._engine.dispose()


def test_save_and_find_account(
    repository: UnifiedAccountRepository, mock_keyring: InMemoryKeyring
) -> None:
    """アカウントを保存し、正しく取得できることを確認する."""
    # Arrange
    account = Account.create(
        service_name="GitHub",
        login_id="octocat",
        password_str="meow123",  # noqa: S106
        memo="テストアカウント",
    )

    # Act
    repository.save(account)

    # Assert
    found_accounts = repository.find_all()
    assert len(found_accounts) == 1
    found = found_accounts.to_list()[0]

    assert found.service_name == "GitHub"
    assert found.login_id == "octocat"
    assert found.password.get_raw_value() == "meow123"
    assert found.memo == "テストアカウント"

    # 個別取得も確認
    found_by_id = repository.find_by_id(found.id)
    assert found_by_id == found

    # Keychain側にも正しく保存されているか（統合テストとしての確認）
    assert mock_keyring.get_password("test-service", str(found.id)) == "meow123"


def test_delete_account(
    repository: UnifiedAccountRepository, mock_keyring: InMemoryKeyring
) -> None:
    """アカウントを削除した際、両方のストアから消えることを確認する."""
    # Arrange
    account = Account.create(service_name="Test", login_id="User", password_str="Pass")  # noqa: S106
    repository.save(account)
    found = repository.find_all().to_list()[0]

    # Act
    repository.delete(found.id)

    # Assert
    assert repository.find_by_id(found.id) is None
    assert len(repository.find_all()) == 0
    # Keychain側も実際にデータが消えていることを確認
    assert mock_keyring.get_password("test-service", str(found.id)) is None
