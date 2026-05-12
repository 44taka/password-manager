"""Accountエンティティの定義."""

from dataclasses import dataclass

from .account_id import AccountID
from .password import Password


@dataclass
class Account:
    """エンティティ: サービスへのログイン情報を管理する."""

    id: AccountID
    service_name: str
    login_id: str
    password: Password
    memo: str
    created_at: str
    updated_at: str

    @classmethod
    def create(
        cls,
        account_id: int,
        service_name: str,
        login_id: str,
        password_str: str,
        memo: str = "",
        created_at: str = "",
        updated_at: str = "",
    ) -> "Account":
        """新規アカウントを作成するためのファクトリメソッド。

        Args:
            account_id: アカウントID。
            service_name: サービス名。
            login_id: ログインID。
            password_str: パスワード文字列。
            memo: メモ。デフォルトは空文字。
            created_at: 作成日時。デフォルトは空文字。
            updated_at: 更新日時。デフォルトは空文字。

        Returns:
            生成された Account インスタンス。
        """
        return cls(
            id=AccountID(account_id),
            service_name=service_name,
            login_id=login_id,
            password=Password(password_str),
            memo=memo,
            created_at=created_at,
            updated_at=updated_at,
        )
