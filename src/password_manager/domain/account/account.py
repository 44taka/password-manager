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
        service_name: str,
        login_id: str,
        password_str: str,
        memo: str = "",
        created_at: str = "",
        updated_at: str = "",
    ) -> "Account":
        """新規アカウントを作成するためのファクトリメソッド。

        ID はアプリケーション側で UUID を自動発行します。

        Args:
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
            id=AccountID.generate(),
            service_name=service_name,
            login_id=login_id,
            password=Password(password_str),
            memo=memo,
            created_at=created_at,
            updated_at=updated_at,
        )

    @classmethod
    def reconstruct(
        cls,
        account_id: str,
        service_name: str,
        login_id: str,
        password_str: str,
        memo: str = "",
        created_at: str = "",
        updated_at: str = "",
    ) -> "Account":
        """永続化ストアからアカウントを復元するためのファクトリメソッド。

        既存の ID をそのまま使用します。新規作成には create() を使用してください。

        Args:
            account_id: 既存のアカウントID（UUID文字列）。
            service_name: サービス名。
            login_id: ログインID。
            password_str: パスワード文字列。
            memo: メモ。デフォルトは空文字。
            created_at: 作成日時。デフォルトは空文字。
            updated_at: 更新日時。デフォルトは空文字。

        Returns:
            復元された Account インスタンス。
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
