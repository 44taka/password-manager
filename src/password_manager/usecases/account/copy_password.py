"""パスワードコピーユースケース."""

from injector import inject

from password_manager.domain.account import AccountID, AccountRepository, ClipboardService


class CopyPasswordUseCase:
    """パスワードをクリップボードにコピーするユースケース."""

    @inject
    def __init__(
        self, account_repo: AccountRepository, clipboard_service: ClipboardService
    ) -> None:
        """CopyPasswordUseCase を初期化します。

        Args:
            account_repo: アカウントリポジトリ。
            clipboard_service: クリップボードサービス。
        """
        self._account_repo = account_repo
        self._clipboard_service = clipboard_service

    def execute(self, account_id: int, clear_after: int = 15) -> None:
        """指定されたIDのアカウントのパスワードをコピーします。

        Args:
            account_id: 対象のアカウントID。
            clear_after: クリップボードをクリアするまでの秒数。

        Raises:
            ValueError: アカウントが見つからない場合。
        """
        account = self._account_repo.find_by_id(AccountID(account_id))
        if not account:
            raise ValueError(f"ID {account_id} のアカウントが見つかりません。")

        # 生のパスワードを取得してコピー
        self._clipboard_service.copy(account.password.get_raw_value(), clear_after=clear_after)
