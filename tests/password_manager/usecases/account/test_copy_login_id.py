"""CopyLoginIDUseCaseのテスト."""

from unittest.mock import MagicMock

import pytest

from password_manager.domain.account import Account, AccountID, AccountRepository, ClipboardService
from password_manager.usecases.account.copy_login_id import CopyLoginIDUseCase


@pytest.fixture
def mock_repo() -> MagicMock:
    """AccountRepositoryのモック."""
    return MagicMock(spec=AccountRepository)


@pytest.fixture
def mock_clipboard() -> MagicMock:
    """ClipboardServiceのモック."""
    return MagicMock(spec=ClipboardService)


@pytest.fixture
def use_case(mock_repo: MagicMock, mock_clipboard: MagicMock) -> CopyLoginIDUseCase:
    """テスト対象のユースケース."""
    return CopyLoginIDUseCase(mock_repo, mock_clipboard)


def test_copy_login_id(
    use_case: CopyLoginIDUseCase, mock_repo: MagicMock, mock_clipboard: MagicMock
) -> None:
    """ログインIDが正しくクリップボードにコピーされることを確認する."""
    # Arrange
    account = Account.create(1, "Site", "user@example.com", "pass")
    mock_repo.find_by_id.return_value = account

    # Act
    use_case.execute(account_id=1)

    # Assert
    mock_clipboard.copy.assert_called_once_with("user@example.com")
    mock_repo.find_by_id.assert_called_once_with(AccountID(1))


def test_copy_login_id_not_found(use_case: CopyLoginIDUseCase, mock_repo: MagicMock) -> None:
    """アカウントが見つからない場合にValueErrorが発生することを確認する."""
    # Arrange
    mock_repo.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="アカウントが見つかりません"):
        use_case.execute(account_id=999)
