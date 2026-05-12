"""アカウント更新ユースケース."""

from injector import inject

from password_manager.domain.account import AccountID, AccountRepository, Password


class UpdateAccountUseCase:
    """アカウント情報の更新を行うユースケース."""

    @inject
    def __init__(self, account_repo: AccountRepository) -> None:
        """UpdateAccountUseCase を初期化します。

        Args:
            account_repo: アカウントリポジトリ。
        """
        self._account_repo = account_repo

    def execute(
        self,
        account_id: int,
        service_name: str | None = None,
        login_id: str | None = None,
        password_str: str | None = None,
        memo: str | None = None,
    ) -> None:
        """既存のアカウント情報を更新します。

        Args:
            account_id: 更新対象のアカウントID。
            service_name: 新しいサービス名（任意）。
            login_id: 新しいログインID（任意）。
            password_str: 新しいパスワード文字列（任意）。
            memo: 新しい備忘録（任意）。

        Raises:
            ValueError: 指定されたIDのアカウントが見つからない場合。
        """
        account = self._account_repo.find_by_id(AccountID(account_id))
        if not account:
            raise ValueError(f"ID {account_id} のアカウントが見つかりません。")

        if service_name is not None:
            account.service_name = service_name
        if login_id is not None:
            account.login_id = login_id
        if password_str is not None:
            account.password = Password(password_str)
        if memo is not None:
            account.memo = memo

        self._account_repo.save(account)
