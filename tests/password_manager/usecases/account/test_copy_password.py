"""CopyPasswordUseCaseのテスト."""

from unittest.mock import MagicMock, patch

import pytest

from password_manager.domain.account import Account, AccountID, AccountRepository
from password_manager.usecases.account.copy_password import CopyPasswordUseCase
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
def use_case(mock_repo: MagicMock, mock_clipboard: MagicMock) -> CopyPasswordUseCase:
    """テスト対象のユースケース."""
    return CopyPasswordUseCase(mock_repo, mock_clipboard)


@patch("password_manager.usecases.account.copy_password.threading.Thread")
def test_copy_password(
    mock_thread: MagicMock,
    use_case: CopyPasswordUseCase,
    mock_repo: MagicMock,
    mock_clipboard: MagicMock,
) -> None:
    """パスワードが正しくクリップボードにコピーされ、バックグラウンド消去スレッドが起動することを確認する."""
    # Arrange
    account = Account.create(1, "Site", "user", "secret-password")
    mock_repo.find_by_id.return_value = account

    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance

    # Act
    use_case.execute(account_id=1)

    # Assert
    # パスワードが生でコピーされたこと
    mock_clipboard.copy.assert_called_once_with("secret-password")
    mock_repo.find_by_id.assert_called_once_with(AccountID(1))

    # スレッドが起動されたこと
    mock_thread.assert_called_once()
    mock_thread_instance.start.assert_called_once()


def test_copy_password_not_found(use_case: CopyPasswordUseCase, mock_repo: MagicMock) -> None:
    """アカウントが見つからない場合にValueErrorが発生することを確認する."""
    # Arrange
    mock_repo.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="アカウントが見つかりません"):
        use_case.execute(account_id=999)
