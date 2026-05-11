"""Account集約のドメインモデルに関するテスト."""

import pytest

from password_manager.domain.account import Account, AccountID, Password


def test_account_creation():
    """Accountが正しく生成されることを確認する."""
    account = Account.create(
        account_id=1,
        service_name="Google",
        login_id="user@gmail.com",
        password_str="secret123",  # noqa: S106
        memo="テスト用メモ",
    )

    assert account.id == AccountID(1)
    assert account.service_name == "Google"
    assert account.login_id == "user@gmail.com"
    assert account.password.get_raw_value() == "secret123"
    assert account.memo == "テスト用メモ"


def test_password_masking():
    """Passwordが正しくマスクされることを確認する."""
    password = Password("secret123")
    assert str(password) == "********"
    assert password.get_raw_value() == "secret123"


def test_password_empty_error():
    """空のパスワードでエラーが出ることを確認する."""
    with pytest.raises(ValueError, match="パスワードは空であってはなりません。"):
        Password("")


def test_account_id_conversion():
    """AccountIDがintに変換できることを確認する."""
    account_id = AccountID(123)
    assert int(account_id) == 123
