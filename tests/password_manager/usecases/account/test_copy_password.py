"""CopyPasswordUseCaseのテスト."""

from unittest.mock import MagicMock

import pytest

from password_manager.domain.account import Account, AccountID, AccountRepository, ClipboardService
from password_manager.usecases.account.copy_password import CopyPasswordUseCase


@pytest.fixture
def mock_repo() -> MagicMock:
    """AccountRepositoryのモック."""
    return MagicMock(spec=AccountRepository)


@pytest.fixture
def mock_clipboard() -> MagicMock:
    """ClipboardServiceのモック."""
    return MagicMock(spec=ClipboardService)


@pytest.fixture
def use_case(mock_repo: MagicMock, mock_clipboard: MagicMock) -> CopyPasswordUseCase:
    """テスト対象のユースケース."""
    return CopyPasswordUseCase(mock_repo, mock_clipboard)


def test_copy_password(
    use_case: CopyPasswordUseCase, mock_repo: MagicMock, mock_clipboard: MagicMock
) -> None:
    """パスワードが正しくクリップボードにコピーされ、消去設定が有効であることを確認する."""
    # Arrange
    account = Account.create(1, "Site", "user", "secret-password")
    mock_repo.find_by_id.return_value = account

    # Act
    use_case.execute(account_id=1)

    # Assert
    # パスワードが生でコピーされ、かつ15秒後にクリアされる設定になっていること
    mock_clipboard.copy.assert_called_once_with("secret-password", clear_after=15)
    mock_repo.find_by_id.assert_called_once_with(AccountID(1))


def test_copy_password_not_found(use_case: CopyPasswordUseCase, mock_repo: MagicMock) -> None:
    """アカウントが見つからない場合にValueErrorが発生することを確認する."""
    # Arrange
    mock_repo.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="アカウントが見つかりません"):
        use_case.execute(account_id=999)
