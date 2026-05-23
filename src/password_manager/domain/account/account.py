"""Accountエンティティの定義."""

from dataclasses import dataclass

from .account_id import AccountID
from .login_id import LoginID
from .password import Password
from .service_name import ServiceName


@dataclass
class Account:
    """エンティティ: サービスへのログイン情報を管理する."""

    id: AccountID
    service_name: ServiceName
    login_id: LoginID
    password: Password

    def __post_init__(self) -> None:
        """属性のバリデーションを行います。"""
        pass

    @classmethod
    def create(
        cls,
        service_name: str,
        login_id: str,
        password_str: str,
    ) -> "Account":
        """新規アカウントを作成するためのファクトリメソッド。

        ID はアプリケーション側で UUID を自動発行します。

        Args:
            service_name: サービス名。
            login_id: ログインID。
            password_str: パスワード文字列。

        Returns:
            生成された Account インスタンス。
        """
        return cls(
            id=AccountID.generate(),
            service_name=ServiceName(service_name),
            login_id=LoginID(login_id),
            password=Password(password_str),
        )

    @classmethod
    def reconstruct(
        cls,
        account_id: str,
        service_name: str,
        login_id: str,
        password_str: str,
    ) -> "Account":
        """永続化ストアからアカウントを復元するためのファクトリメソッド。

        既存の ID をそのまま使用します。新規作成には create() を使用してください。

        Args:
            account_id: 既存のアカウントID（UUID文字列）。
            service_name: サービス名。
            login_id: ログインID。
            password_str: パスワード文字列。

        Returns:
            復元された Account インスタンス。
        """
        return cls(
            id=AccountID(account_id),
            service_name=ServiceName(service_name),
            login_id=LoginID(login_id),
            password=Password(password_str),
        )

