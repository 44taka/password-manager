"""SQLiteとKeychainを統合したアカウントリポジトリの実装."""

from password_manager.domain.account import Account, AccountID, AccountRepository, Accounts

from .macos_keychain_store import MacosKeychainStore
from .sqlite_account_store import SqliteAccountStore


class UnifiedAccountRepository(AccountRepository):
    """SQLite(メタデータ)とKeychain(パスワード)を統合したリポジトリ."""

    def __init__(
        self, sqlite_store: SqliteAccountStore, keychain_store: MacosKeychainStore
    ) -> None:
        """UnifiedAccountRepository を初期化します。

        Args:
            sqlite_store: メタデータ保存用の SQLite ストア。
            keychain_store: パスワード保存用の Keychain ストア。
        """
        self._sqlite = sqlite_store
        self._keychain = keychain_store

    def save(self, account: Account) -> None:
        """アカウントを保存します。

        Args:
            account: 保存対象のアカウント。
        """
        account_id = str(account.id)
        self._sqlite.save(
            account_id=account_id,
            service_name=account.service_name,
            login_id=account.login_id,
            memo=account.memo,
        )
        self._keychain.save(account_id, account.password.get_raw_value())

    def find_by_id(self, account_id: AccountID) -> Account | None:
        """IDでアカウントを取得します。

        Args:
            account_id: 取得対象のアカウントID。

        Returns:
            取得したアカウント。存在しない場合は None。
        """
        metadata = self._sqlite.fetch_by_id(str(account_id))
        if metadata is None:
            return None

        password_str = self._keychain.get(str(account_id)) or ""

        return Account.reconstruct(
            account_id=metadata["id"],
            service_name=metadata["site_name"],
            login_id=metadata["username"],
            password_str=password_str,
            memo=metadata["notes"],
            created_at=metadata["created_at"],
            updated_at=metadata["updated_at"],
        )

    def find_all(self) -> Accounts:
        """全てのアカウントを取得します。

        Returns:
            全てのアカウントを含むコレクション。
        """
        metadatas = self._sqlite.fetch_all()
        accounts = []
        for meta in metadatas:
            aid = meta["id"]
            password_str = self._keychain.get(aid) or ""
            accounts.append(
                Account.reconstruct(
                    account_id=aid,
                    service_name=meta["site_name"],
                    login_id=meta["username"],
                    password_str=password_str,
                    memo=meta["notes"],
                    created_at=meta["created_at"],
                    updated_at=meta["updated_at"],
                )
            )
        return Accounts(accounts)

    def delete(self, account_id: AccountID) -> None:
        """アカウントを削除します。

        Args:
            account_id: 削除対象のアカウントID。
        """
        self._sqlite.delete(str(account_id))
        self._keychain.delete(str(account_id))
