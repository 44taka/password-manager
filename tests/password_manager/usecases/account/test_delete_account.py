"""DeleteAccountUseCaseのテスト."""

from unittest.mock import MagicMock

import pytest

from password_manager.domain.account import AccountID, AccountRepository
from password_manager.usecases.account.delete_account import DeleteAccountUseCase


@pytest.fixture
def mock_repo() -> MagicMock:
    """AccountRepositoryのモック."""
    return MagicMock(spec=AccountRepository)


@pytest.fixture
def use_case(mock_repo: MagicMock) -> DeleteAccountUseCase:
    """テスト対象のユースケース."""
    return DeleteAccountUseCase(mock_repo)


def test_delete_account(use_case: DeleteAccountUseCase, mock_repo: MagicMock) -> None:
    """アカウントが正しく削除されることを確認する."""
    # Act
    use_case.execute(account_id=123)

    # Assert
    mock_repo.delete.assert_called_once_with(AccountID(123))
