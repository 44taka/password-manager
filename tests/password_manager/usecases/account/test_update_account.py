"""UpdateAccountUseCaseのテスト."""

from unittest.mock import MagicMock

import pytest

from password_manager.domain.account import Account, AccountRepository
from password_manager.domain.exceptions import ValidationError
from password_manager.usecases.account.update_account import UpdateAccountUseCase


@pytest.fixture
def mock_repo() -> MagicMock:
    """AccountRepositoryのモック."""
    return MagicMock(spec=AccountRepository)


@pytest.fixture
def use_case(mock_repo: MagicMock) -> UpdateAccountUseCase:
    """テスト対象のユースケース."""
    return UpdateAccountUseCase(mock_repo)


def test_update_account(use_case: UpdateAccountUseCase, mock_repo: MagicMock) -> None:
    """既存のアカウント情報が正しく更新されることを確認する."""
    # Arrange
    existing_account = Account.create(
        service_name="Old Site",
        login_id="olduser",
        password_str="oldpass",  # noqa: S106
        memo="old memo",
    )
    mock_repo.find_by_id.return_value = existing_account
    account_id = str(existing_account.id)

    # Act
    use_case.execute(
        account_id=account_id,
        service_name="New Site",
        login_id="newuser",
        password_str="newpass",  # noqa: S106
        memo="new memo",
    )

    # Assert
    mock_repo.save.assert_called_once()
    saved = mock_repo.save.call_args[0][0]
    assert str(saved.id) == account_id
    assert saved.service_name == "New Site"
    assert saved.login_id == "newuser"
    assert saved.password.get_raw_value() == "newpass"
    assert saved.memo == "new memo"


def test_update_account_not_found(use_case: UpdateAccountUseCase, mock_repo: MagicMock) -> None:
    """アカウントが存在しない場合にValueErrorが発生することを確認する."""
    # Arrange
    mock_repo.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="アカウントが見つかりません"):
        use_case.execute(account_id="non-existent-uuid", service_name="Any")


def test_update_account_validation_error(use_case: UpdateAccountUseCase, mock_repo: MagicMock) -> None:
    """無効な値（空のサービス名など）で更新しようとした場合にValidationErrorが発生することを確認する."""
    # Arrange
    existing_account = Account.create(
        service_name="Old Site",
        login_id="olduser",
        password_str="oldpass",  # noqa: S106
        memo="old memo",
    )
    mock_repo.find_by_id.return_value = existing_account
    account_id = str(existing_account.id)

    # Act & Assert
    # サービス名を空にして更新しようとすると、エンティティのバリデーションでエラーになるはず
    with pytest.raises(ValidationError, match="サービス名は必須です。"):
        use_case.execute(
            account_id=account_id,
            service_name="",  # 無効な値
        )

    # 保存処理が呼ばれていないことも確認
    mock_repo.save.assert_not_called()
