"""password_manager パッケージ共通フィクスチャ."""

from collections.abc import Callable

import pytest

from password_manager.domain.account import Account


@pytest.fixture
def make_account() -> Callable[..., Account]:
    """Account を生成するファクトリフィクスチャです。."""

    def _factory(
        account_id: int = 1,
        service_name: str = "Example",
        login_id: str = "test_user",
        password_str: str = "password123",  # noqa: S107
        memo: str = "",
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> Account:
        """アカウントを生成します。."""
        return Account.create(
            account_id=account_id,
            service_name=service_name,
            login_id=login_id,
            password_str=password_str,
            memo=memo,
            created_at=created_at,
            updated_at=updated_at,
        )

    return _factory
