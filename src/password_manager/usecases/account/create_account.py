"""アカウント作成ユースケース."""

from injector import inject

from password_manager.domain.account import Account, AccountRepository


class CreateAccountUseCase:
    """アカウントの新規登録を行うユースケース."""

    @inject
    def __init__(self, account_repo: AccountRepository) -> None:
        """CreateAccountUseCaseを初期化します."""
        self._account_repo = account_repo

    def execute(self, service_name: str, login_id: str, password_str: str, memo: str = "") -> None:
        """新規アカウントを作成し、保存します。.

        Args:
            service_name: サービス名。
            login_id: ログインID。
            password_str: パスワード文字列。
            memo: 備忘録（任意）。
        """
        # ID=0 は新規作成を意味する
        account = Account.create(
            account_id=0,
            service_name=service_name,
            login_id=login_id,
            password_str=password_str,
            memo=memo,
        )
        self._account_repo.save(account)
