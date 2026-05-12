"""パスワードコピーユースケース."""

import threading
import time
from datetime import UTC, datetime

from injector import inject

from password_manager.domain.account import AccountID, AccountRepository, ClipboardPolicy
from password_manager.usecases.interfaces import ClipboardService


class CopyPasswordUseCase:
    """パスワードをクリップボードにコピーするユースケース."""

    @inject
    def __init__(
        self,
        account_repo: AccountRepository,
        clipboard_service: ClipboardService,
        policy: ClipboardPolicy,
    ) -> None:
        """CopyPasswordUseCase を初期化します。

        Args:
            account_repo: アカウントリポジトリ。
            clipboard_service: クリップボードサービス。
            policy: クリップボードポリシー。
        """
        self._account_repo = account_repo
        self._clipboard_service = clipboard_service
        self._policy = policy

    def execute(self, account_id: int) -> None:
        """指定されたアカウントのパスワードをクリップボードにコピーします。

        コピー後、ポリシーに従って一定時間後に自動的にクリップボードを消去します。

        Args:
            account_id: アカウントID。

        Raises:
            ValueError: アカウントが見つからない場合。
        """
        account = self._account_repo.find_by_id(AccountID(account_id))
        if not account:
            raise ValueError(f"ID {account_id} のアカウントが見つかりません。")

        # 生のパスワードを取得してコピー
        password_value = account.password.get_raw_value()
        self._clipboard_service.copy(password_value)
        copied_at = datetime.now(UTC)

        def _clear_clipboard_if_needed() -> None:
            # 保持期限の判定ロジックを ClipboardPolicy (ドメイン層) にカプセル化するため、
            # 直接的な time.sleep() ではなく、ポリシーに従ったポーリングループを採用しています。
            while not self._policy.is_expired(copied_at, datetime.now(UTC)):
                time.sleep(1)
            self._clipboard_service.clear(password_value)

        # バックグラウンドで待機して消去するスレッドを起動
        threading.Thread(target=_clear_clipboard_if_needed, daemon=True).start()
