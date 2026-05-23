"""CreateAccountUseCaseのテスト."""

from unittest.mock import MagicMock

import pytest

from password_manager.domain.account import Account, AccountRepository
from password_manager.usecases.account.create_account import CreateAccountUseCase


@pytest.fixture
def mock_repo() -> MagicMock:
    """AccountRepositoryのモック."""
    return MagicMock(spec=AccountRepository)


@pytest.fixture
def use_case(mock_repo: MagicMock) -> CreateAccountUseCase:
    """テスト対象のユースケース."""
    return CreateAccountUseCase(mock_repo)


def test_create_account(use_case: CreateAccountUseCase, mock_repo: MagicMock) -> None:
    """アカウントが正しく作成・保存されることを確認する."""
    # Act
    use_case.execute(
        service_name="Google",
        login_id="user@gmail.com",
        password_str="secret123",  # noqa: S106
        memo="メモ",
    )

    # Assert
    # saveが1回呼ばれ、引数として適切なAccountオブジェクトが渡されていること
    mock_repo.save.assert_called_once()
    saved_account = mock_repo.save.call_args[0][0]
    assert isinstance(saved_account, Account)
    assert saved_account.service_name.value == "Google"
    assert saved_account.login_id.value == "user@gmail.com"
    assert saved_account.password.get_raw_value() == "secret123"
    assert saved_account.memo == "メモ"
