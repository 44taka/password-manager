"""UnifiedAccountRepositoryの統合テスト."""

from collections.abc import Generator
from pathlib import Path

import pytest
import pytest_mock

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
    )

    # Act
    repository.save(account)

    # Assert
    found_accounts = repository.find_all()
    assert len(found_accounts) == 1
    found = found_accounts.to_list()[0]

    assert found.service_name.value == "GitHub"
    assert found.login_id.value == "octocat"
    assert found.password.get_raw_value() == "meow123"

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


def test_save_rollback_when_sqlite_fails(
    repository: UnifiedAccountRepository,
    mock_keyring: InMemoryKeyring,
    mocker: pytest_mock.MockerFixture,
) -> None:
    """SQLite保存に失敗した場合、Keychainへの変更がロールバックされることを確認する."""
    # Arrange
    from password_manager.infrastructure import DatabaseError

    account = Account.create(
        service_name="RollbackTest",
        login_id="user",
        password_str="pass",  # noqa: S106
    )

    # SQLite の保存をわざと失敗させる
    mocker.patch.object(repository._sqlite, "save", side_effect=DatabaseError("DB Failure"))

    # Act & Assert
    with pytest.raises(DatabaseError):
        repository.save(account)

    # Keychain側にデータが残っていないことを確認（ロールバックされていること）
    assert mock_keyring.get_password("test-service", str(account.id)) is None


def test_save_rollback_update_when_sqlite_fails(
    repository: UnifiedAccountRepository,
    mock_keyring: InMemoryKeyring,
    mocker: pytest_mock.MockerFixture,
) -> None:
    """既存アカウントの更新中にSQLite保存に失敗した場合、元のパスワードが復元されることを確認する."""
    # Arrange
    from password_manager.infrastructure import DatabaseError

    # 1. 既存アカウントを作成
    account = Account.create(service_name="UpdateTest", login_id="user", password_str="original")
    repository.save(account)
    assert mock_keyring.get_password("test-service", str(account.id)) == "original"

    # 2. 更新用データ作成
    updated_account = Account.reconstruct(
        account_id=str(account.id),
        service_name="UpdateTest",
        login_id="user",
        password_str="new_password",
    )

    # SQLite の保存をわざと失敗させる
    mocker.patch.object(repository._sqlite, "save", side_effect=DatabaseError("DB Failure"))

    # Act & Assert
    with pytest.raises(DatabaseError):
        repository.save(updated_account)

    # Keychain側のパスワードが "original" に戻っていることを確認
    assert mock_keyring.get_password("test-service", str(account.id)) == "original"
