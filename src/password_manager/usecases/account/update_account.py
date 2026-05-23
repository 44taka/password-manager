"""アカウント更新ユースケース."""

import dataclasses

from injector import inject

from password_manager.domain.account import (
    AccountID,
    AccountRepository,
    LoginID,
    Password,
    ServiceName,
)


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
        account_id: str,
        service_name: str | None = None,
        login_id: str | None = None,
        password_str: str | None = None,
    ) -> None:
        """既存のアカウント情報を更新します。

        Args:
            account_id: 更新対象のアカウントID（UUID文字列）。
            service_name: 新しいサービス名（任意）。
            login_id: 新しいログインID（任意）。
            password_str: 新しいパスワード文字列（任意）。

        Raises:
            ValueError: 指定されたIDのアカウントが見つからない場合。
        """
        # TODO: ドメインサービスかな？
        account = self._account_repo.find_by_id(AccountID(account_id))
        if not account:
            raise ValueError(f"ID {account_id} のアカウントが見つかりません。")

        new_values = {}
        if service_name is not None:
            new_values["service_name"] = ServiceName(service_name)
        if login_id is not None:
            new_values["login_id"] = LoginID(login_id)
        if password_str is not None:
            new_values["password"] = Password(password_str)

        # replace を使うことで __post_init__ が実行され、バリデーションが行われる
        account = dataclasses.replace(account, **new_values)

        self._account_repo.save(account)
