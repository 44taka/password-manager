"""SearchAccountsUseCaseのテスト."""

from unittest.mock import MagicMock

import pytest

from password_manager.domain.account import Account, AccountRepository, Accounts
from password_manager.usecases.account.search_accounts import SearchAccountsUseCase


@pytest.fixture
def mock_repo() -> MagicMock:
    """AccountRepositoryのモック."""
    return MagicMock(spec=AccountRepository)


@pytest.fixture
def use_case(mock_repo: MagicMock) -> SearchAccountsUseCase:
    """テスト対象のユースケース."""
    return SearchAccountsUseCase(mock_repo)


def test_search_all_accounts(use_case: SearchAccountsUseCase, mock_repo: MagicMock) -> None:
    """クエリが空の場合、全件取得されることを確認する."""
    # Arrange
    accounts = [
        Account.create(1, "Google", "user1", "pass1"),
        Account.create(2, "GitHub", "user2", "pass2"),
    ]
    mock_repo.find_all.return_value = Accounts(accounts)

    # Act
    results = use_case.execute(query="")

    # Assert
    assert results == accounts
    mock_repo.find_all.assert_called_once()


def test_search_with_query(use_case: SearchAccountsUseCase, mock_repo: MagicMock) -> None:
    """クエリがある場合、フィルタリングされることを確認する."""
    # Arrange
    accounts = [
        Account.create(1, "Google", "user1", "pass1"),
        Account.create(2, "GitHub", "user2", "pass2"),
    ]
    mock_repo.find_all.return_value = Accounts(accounts)

    # Act
    # "Goo" で検索
    results = use_case.execute(query="Goo")

    # Assert
    assert len(results) == 1
    assert results[0].service_name == "Google"
