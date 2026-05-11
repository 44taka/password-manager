"""SQLiteとKeychainを統合したアカウントリポジトリの実装."""

from password_manager.domain.account import Account, AccountID, AccountRepository

from .macos_keychain_store import MacosKeychainStore
from .sqlite_account_store import SqliteAccountStore


class UnifiedAccountRepository(AccountRepository):
    """SQLite(メタデータ)とKeychain(パスワード)を統合したリポジトリ."""

    def __init__(
        self, sqlite_store: SqliteAccountStore, keychain_store: MacosKeychainStore
    ) -> None:
        """UnifiedAccountRepositoryを初期化します."""
        self._sqlite = sqlite_store
        self._keychain = keychain_store

    def save(self, account: Account) -> None:
        """アカウントを保存します。."""
        # 1. メタデータを保存
        new_id = self._sqlite.save(
            account_id=int(account.id),
            service_name=account.service_name,
            login_id=account.login_id,
            memo=account.memo,
        )

        # 2. 生成された（または既存の）IDをセット
        if int(account.id) == 0:
            # 新規作成時はIDを更新（ミュータブルなEntityとしての更新）
            # 本来は新しいIDを持つAccountを再生成して返すのがよりクリーンですが、
            # 現状のインターフェースに合わせてIDをセットします。
            object.__setattr__(account, "id", AccountID(new_id))

        # 3. パスワードをKeychainに保存
        self._keychain.save(int(account.id), account.password.get_raw_value())

    def find_by_id(self, account_id: AccountID) -> Account | None:
        """IDでアカウントを取得します。."""
        metadata = self._sqlite.fetch_by_id(int(account_id))
        if metadata is None:
            return None

        password_str = self._keychain.get(int(account_id))
        if password_str is None:
            # Keychainにパスワードがない場合は空文字とするか、エラーとするか検討が必要ですが
            # 一旦空文字で復元します
            password_str = ""

        return Account.create(
            account_id=metadata["id"],
            service_name=metadata["site_name"],
            login_id=metadata["username"],
            password_str=password_str,
            memo=metadata["notes"],
            created_at=metadata["created_at"],
            updated_at=metadata["updated_at"],
        )

    def find_all(self) -> list[Account]:
        """全てのアカウントを取得します。."""
        metadatas = self._sqlite.fetch_all()
        accounts = []
        for meta in metadatas:
            aid = meta["id"]
            password_str = self._keychain.get(aid) or ""
            accounts.append(
                Account.create(
                    account_id=aid,
                    service_name=meta["site_name"],
                    login_id=meta["username"],
                    password_str=password_str,
                    memo=meta["notes"],
                    created_at=meta["created_at"],
                    updated_at=meta["updated_at"],
                )
            )
        return accounts

    def delete(self, account_id: AccountID) -> None:
        """アカウントを削除します。."""
        # 両方のストアから削除
        self._sqlite.delete(int(account_id))
        self._keychain.delete(int(account_id))
