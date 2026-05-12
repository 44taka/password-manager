"""ログインIDコピーユースケース."""

from injector import inject

from password_manager.domain.account import AccountID, AccountRepository, ClipboardService


class CopyLoginIDUseCase:
    """ログインIDをクリップボードにコピーするユースケース."""

    @inject
    def __init__(
        self, account_repo: AccountRepository, clipboard_service: ClipboardService
    ) -> None:
        """CopyLoginIDUseCase を初期化します。

        Args:
            account_repo: アカウントリポジトリ。
            clipboard_service: クリップボードサービス。
        """
        self._account_repo = account_repo
        self._clipboard_service = clipboard_service

    def execute(self, account_id: int) -> None:
        """指定されたIDのアカウントのログインIDをコピーします。

        Args:
            account_id: 対象のアカウントID。

        Raises:
            ValueError: アカウントが見つからない場合。
        """
        account = self._account_repo.find_by_id(AccountID(account_id))
        if not account:
            raise ValueError(f"ID {account_id} のアカウントが見つかりません。")

        self._clipboard_service.copy(account.login_id)
