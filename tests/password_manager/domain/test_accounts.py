"""Accountsコレクションのテスト."""

from __future__ import annotations

import pytest

from password_manager.domain.account import Account
from password_manager.domain.account.accounts import Accounts


@pytest.fixture
def sample_accounts() -> list[Account]:
    """テスト用のアカウント一覧を生成します."""
    return [
        Account.create(service_name="GitHub", login_id="tanaka@example.com", password_str="pass1"),  # noqa: S106
        Account.create(service_name="Google", login_id="tanaka@gmail.com", password_str="pass2"),  # noqa: S106
        Account.create(service_name="Amazon", login_id="tanaka@amazon.co.jp", password_str="pass3"),  # noqa: S106
        Account.create(service_name="GitLab", login_id="tanaka@gitlab.com", password_str="pass4"),  # noqa: S106
        Account.create(service_name="Twitter", login_id="tanaka_dev", password_str="pass5"),  # noqa: S106
    ]


class TestAccounts:
    """Accountsコレクションのテスト."""

    def test_initialization_and_iteration(self, sample_accounts: list[Account]) -> None:
        """初期化とイテレーションが正しく行えることを確認する."""
        accounts = Accounts(sample_accounts)

        assert len(accounts) == 5

        # イテレーションの確認
        items = [a for a in accounts]
        assert len(items) == 5
        assert items[0].service_name == "GitHub"

    def test_to_list(self, sample_accounts: list[Account]) -> None:
        """to_listメソッドがリストのコピーを返すことを確認する."""
        accounts = Accounts(sample_accounts)
        lst = accounts.to_list()

        assert isinstance(lst, list)
        assert len(lst) == 5
        assert lst[0] == sample_accounts[0]


class TestAccountsSearch:
    """Accounts.search() のテスト."""

    def test_exact_match(self, sample_accounts: list[Account]) -> None:
        """完全一致するアカウントが正しく検索されることをテストする."""
        accounts = Accounts(sample_accounts)
        results = accounts.search("GitHub").to_list()

        assert len(results) >= 1
        assert results[0].service_name == "GitHub"

    def test_partial_match(self, sample_accounts: list[Account]) -> None:
        """部分一致(in)でスコア100となり、優先的に検索されることをテストする."""
        accounts = Accounts(sample_accounts)
        results = accounts.search("git").to_list()

        service_names = [a.service_name for a in results]
        assert "GitHub" in service_names
        assert "GitLab" in service_names

        # 部分一致のスコアは100となるため、高い順序になるはず
        # （ここでは少なくともヒットしていることを確認）

    def test_typo_fuzzy_match(self, sample_accounts: list[Account]) -> None:
        """タイポがある場合でも、difflibによりあいまい検索されることをテストする."""
        accounts = Accounts(sample_accounts)
        # "GitHbu" というタイポで検索。difflib の ratio が threshold(60) を超えればヒットする
        results = accounts.search("GitHbu", threshold=60).to_list()

        service_names = [a.service_name for a in results]
        assert "GitHub" in service_names

    def test_no_match(self, sample_accounts: list[Account]) -> None:
        """一致するアカウントがない場合に空のコレクションが返ることをテストする."""
        accounts = Accounts(sample_accounts)
        results = accounts.search("zzzzz", threshold=80).to_list()

        assert results == []

    def test_empty_query_returns_self(self, sample_accounts: list[Account]) -> None:
        """空のクエリを指定した場合に自身（すべてのアカウント）が返ることをテストする."""
        accounts = Accounts(sample_accounts)
        results = accounts.search("")

        assert len(results) == len(sample_accounts)
        assert results is accounts  # 同じインスタンスが返るべき

    def test_case_insensitive(self, sample_accounts: list[Account]) -> None:
        """大文字小文字を区別せずに検索できることをテストする."""
        accounts = Accounts(sample_accounts)
        results = accounts.search("github").to_list()

        assert len(results) >= 1
        assert results[0].service_name == "GitHub"
