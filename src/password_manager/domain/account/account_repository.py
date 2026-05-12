"""AccountRepositoryインターフェースの定義."""

from typing import Protocol

from .account import Account
from .account_id import AccountID
from .accounts import Accounts


class AccountRepository(Protocol):
    """Account 集約の永続化を担うインターフェース."""

    def save(self, account: Account) -> None:
        """アカウントを保存（新規作成または更新）します。

        Args:
            account: 保存対象のアカウント。
        """
        ...

    def find_by_id(self, account_id: AccountID) -> Account | None:
        """IDでアカウントを取得します。

        Args:
            account_id: 取得対象のアカウントID。

        Returns:
            取得したアカウント。存在しない場合は None。
        """
        ...

    def find_all(self) -> Accounts:
        """全てのアカウントを取得します。

        Returns:
            全てのアカウントを含むコレクション。
        """
        ...

    def delete(self, account_id: AccountID) -> None:
        """アカウントを削除します。

        Args:
            account_id: 削除対象のアカウントID。
        """
        ...
