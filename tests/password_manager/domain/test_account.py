"""Account集約のドメインモデルに関するテスト."""

import uuid

import pytest

from password_manager.domain.account import Account, AccountID, LoginID, Password, ServiceName
from password_manager.domain.exceptions import ValidationError


def test_account_create_generates_uuid():
    """Account.create() を呼ぶと UUID が自動発行されることを確認する."""
    account = Account.create(
        service_name="Google",
        login_id="user@gmail.com",
        password_str="secret123",  # noqa: S106
        memo="テスト用メモ",
    )

    # ID は自動発行された UUID 文字列であること
    assert isinstance(account.id.value, str)
    uuid.UUID(account.id.value)  # 有効な UUID 形式であること
    assert account.service_name.value == "Google"
    assert account.login_id.value == "user@gmail.com"
    assert account.password.get_raw_value() == "secret123"
    assert account.memo == "テスト用メモ"


def test_account_create_generates_unique_ids():
    """Account.create() を複数回呼ぶと、それぞれ異なる ID が発行されることを確認する."""
    a1 = Account.create(service_name="S1", login_id="u1", password_str="p1")  # noqa: S106
    a2 = Account.create(service_name="S2", login_id="u2", password_str="p2")  # noqa: S106
    assert a1.id != a2.id


def test_account_reconstruct_uses_given_id():
    """Account.reconstruct() は指定した ID でエンティティを復元できることを確認する."""
    existing_id = str(uuid.uuid4())
    account = Account.reconstruct(
        account_id=existing_id,
        service_name="GitHub",
        login_id="octocat",
        password_str="meow123",  # noqa: S106
        memo="メモ",
    )

    assert account.id == AccountID(existing_id)
    assert account.service_name.value == "GitHub"


def test_password_masking():
    """Passwordが正しくマスクされることを確認する."""
    password = Password("secret123")
    assert str(password) == "********"
    assert password.get_raw_value() == "secret123"


def test_password_empty_error():
    """空のパスワードでエラーが出ることを確認する."""
    with pytest.raises(ValidationError, match="パスワードは空であってはなりません。"):
        Password("")


def test_account_id_str_conversion():
    """AccountID が str に変換できることを確認する."""
    uid = str(uuid.uuid4())
    account_id = AccountID(uid)
    assert str(account_id) == uid


def test_account_id_generate():
    """AccountID.generate() が有効な UUID を返すことを確認する."""
    account_id = AccountID.generate()
    assert isinstance(account_id.value, str)
    uuid.UUID(account_id.value)  # 有効な UUID 形式であること


def test_service_name_str_conversion():
    """ServiceName が str に変換できることを確認する."""
    name = ServiceName("Google")
    assert str(name) == "Google"
    assert name.value == "Google"


def test_login_id_str_conversion():
    """LoginID が str に変換できることを確認する."""
    login_id = LoginID("user@gmail.com")
    assert str(login_id) == "user@gmail.com"
    assert login_id.value == "user@gmail.com"
