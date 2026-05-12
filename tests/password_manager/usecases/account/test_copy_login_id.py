"""CopyLoginIDUseCaseのテスト."""

from unittest.mock import MagicMock

import pytest

from password_manager.domain.account import Account, AccountID, AccountRepository
from password_manager.usecases.account.copy_login_id import CopyLoginIDUseCase
from password_manager.usecases.interfaces import ClipboardService


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
    use_case: CopyLoginIDUseCase,
    mock_repo: MagicMock,
    mock_clipboard: MagicMock,
) -> None:
    """ログインIDが正しくクリップボードにコピーされることを確認する."""
    # Arrange
    account = Account.create(service_name="Site", login_id="user@example.com", password_str="pass")  # noqa: S106
    mock_repo.find_by_id.return_value = account
    account_id = str(account.id)

    # Act
    use_case.execute(account_id=account_id)

    # Assert
    mock_clipboard.copy.assert_called_once_with("user@example.com")
    mock_repo.find_by_id.assert_called_once_with(AccountID(account_id))


def test_copy_login_id_not_found(use_case: CopyLoginIDUseCase, mock_repo: MagicMock) -> None:
    """アカウントが見つからない場合にValueErrorが発生することを確認する."""
    # Arrange
    mock_repo.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="アカウントが見つかりません"):
        use_case.execute(account_id="non-existent-uuid")
