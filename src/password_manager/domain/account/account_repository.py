"""AccountRepositoryインターフェースの定義."""

from typing import Protocol

from .account import Account
from .account_id import AccountID
from .accounts import Accounts


class AccountRepository(Protocol):
    """Account 集約の永続化を担うインターフェース."""

    def save(self, account: Account) -> None:
        """アカウントを保存（新規作成または更新）する."""
        ...

    def find_by_id(self, account_id: AccountID) -> Account | None:
        """IDでアカウントを取得する."""
        ...

    def find_all(self) -> Accounts:
        """全てのアカウントを取得する."""
        ...

    def delete(self, account_id: AccountID) -> None:
        """アカウントを削除する."""
        ...
