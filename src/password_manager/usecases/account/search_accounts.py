"""アカウント検索ユースケース."""

from injector import inject

from password_manager.domain.account import Account, AccountRepository


class SearchAccountsUseCase:
    """アカウントの一覧取得および検索を行うユースケース."""

    @inject
    def __init__(self, account_repo: AccountRepository) -> None:
        """SearchAccountsUseCaseを初期化します."""
        self._account_repo = account_repo

    def execute(self, query: str = "") -> list[Account]:
        """アカウントを検索または全件取得します。.

        Args:
            query: 検索クエリ。空の場合は全件取得します。

        Returns:
            list[Account]: 取得されたアカウントのリスト。
        """
        accounts = self._account_repo.find_all()
        if not query:
            return accounts.to_list()

        return accounts.search(query).to_list()
