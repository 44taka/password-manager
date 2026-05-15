"""ドメイン層のバリデーションテスト."""

import pytest

from password_manager.domain.account import Account, Password
from password_manager.domain.exceptions import ValidationError


def test_password_empty_should_raise_validation_error() -> None:
    """空のパスワードが ValidationError を投げることを確認します."""
    with pytest.raises(ValidationError) as excinfo:
        Password("")
    assert "パスワードは空であってはなりません。" in str(excinfo.value)


def test_account_create_with_empty_service_should_raise_validation_error() -> None:
    """空のサービス名が ValidationError を投げることを確認します."""
    with pytest.raises(ValidationError) as excinfo:
        Account.create(service_name="", login_id="user", password_str="pass")
    assert "サービス名は必須です。" in str(excinfo.value)


def test_account_create_with_empty_login_id_should_raise_validation_error() -> None:
    """空のログインIDが ValidationError を投げることを確認します."""
    with pytest.raises(ValidationError) as excinfo:
        Account.create(service_name="service", login_id="", password_str="pass")
    assert "ログインIDは必須です。" in str(excinfo.value)
