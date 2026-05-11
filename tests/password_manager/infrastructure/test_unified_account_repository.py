"""UnifiedAccountRepositoryの統合テスト."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from password_manager.domain.account import Account
from password_manager.infrastructure.macos_keychain_store import MacosKeychainStore
from password_manager.infrastructure.sqlite_account_store import SqliteAccountStore
from password_manager.infrastructure.unified_account_repository import UnifiedAccountRepository


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """テスト用のテンポラリDBパス."""
    return tmp_path / "test_accounts.db"


@pytest.fixture
def mock_keychain() -> MagicMock:
    """Keychainのモック."""
    mock = MagicMock(spec=MacosKeychainStore)
    # シンプルな辞書でモックの挙動をシミュレート
    storage: dict[int, str] = {}
    mock.save.side_effect = lambda aid, pwd: storage.update({int(aid): pwd})
    mock.get.side_effect = lambda aid: storage.get(int(aid))
    mock.delete.side_effect = lambda aid: storage.pop(int(aid), None)
    return mock


@pytest.fixture
def repository(temp_db: Path, mock_keychain: MagicMock) -> UnifiedAccountRepository:
    """テスト対象のリポジトリ."""
    sqlite_store = SqliteAccountStore(db_path=temp_db)
    return UnifiedAccountRepository(sqlite_store, mock_keychain)


def test_save_and_find_account(
    repository: UnifiedAccountRepository, mock_keychain: MagicMock
) -> None:
    """アカウントを保存し、正しく取得できることを確認する."""
    # Arrange
    account = Account.create(
        account_id=0,  # 新規作成時は0（SQLiteの自動採番に任せる）
        service_name="GitHub",
        login_id="octocat",
        password_str="meow123",  # noqa: S106
        memo="テストアカウント",
    )

    # Act
    repository.save(account)

    # Assert
    # 保存後にIDが割り振られているはず（ここでは最初のデータなので1と仮定）
    found_accounts = repository.find_all()
    assert len(found_accounts) == 1
    found = found_accounts[0]

    assert found.service_name == "GitHub"
    assert found.login_id == "octocat"
    assert found.password.get_raw_value() == "meow123"
    assert found.memo == "テストアカウント"

    # 個別取得も確認
    found_by_id = repository.find_by_id(found.id)
    assert found_by_id == found


def test_delete_account(
    repository: UnifiedAccountRepository, mock_keychain: MagicMock
) -> None:
    """アカウントを削除した際、両方のストアから消えることを確認する."""
    # Arrange
    account = Account.create(0, "Test", "User", "Pass")
    repository.save(account)
    found = repository.find_all()[0]

    # Act
    repository.delete(found.id)

    # Assert
    assert repository.find_by_id(found.id) is None
    assert len(repository.find_all()) == 0
    # Keychain側も削除が呼ばれているはず
    mock_keychain.delete.assert_called_with(int(found.id))
