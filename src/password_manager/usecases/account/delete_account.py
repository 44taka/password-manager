"""アカウント削除ユースケース."""

from injector import inject

from password_manager.domain.account import AccountID, AccountRepository


class DeleteAccountUseCase:
    """アカウント情報の削除を行うユースケース."""

    @inject
    def __init__(self, account_repo: AccountRepository) -> None:
        """DeleteAccountUseCase を初期化します。

        Args:
            account_repo: アカウントリポジトリ。
        """
        self._account_repo = account_repo

    def execute(self, account_id: int) -> None:
        """指定されたIDのアカウントを削除します。

        Args:
            account_id: 削除対象のアカウントID。
        """
        self._account_repo.delete(AccountID(account_id))
