"""fuzzy_search のユニットテスト."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from password_manager.domain.account import Account
from password_manager.search import fuzzy_search


@pytest.fixture
def sample_accounts(make_account: Callable[..., Account]) -> list[Account]:
    """テスト用のアカウント一覧を生成します。."""
    return [
        make_account(account_id=1, service_name="GitHub", login_id="tanaka@example.com"),
        make_account(account_id=2, service_name="Google", login_id="tanaka@gmail.com"),
        make_account(account_id=3, service_name="Amazon", login_id="tanaka@amazon.co.jp"),
        make_account(account_id=4, service_name="GitLab", login_id="tanaka@gitlab.com"),
        make_account(account_id=5, service_name="Twitter", login_id="tanaka_dev"),
    ]


class TestFuzzySearch:
    """fuzzy_search() のテスト."""

    def test_exact_match(self, sample_accounts: list[Account]) -> None:
        """完全一致するアカウントが正しく検索されることをテストします。."""
        results = fuzzy_search("GitHub", sample_accounts)
        assert len(results) >= 1
        assert results[0].service_name == "GitHub"

    def test_partial_match(self, sample_accounts: list[Account]) -> None:
        """部分一致するアカウントが正しく検索されることをテストします。."""
        results = fuzzy_search("git", sample_accounts)
        service_names = [a.service_name for a in results]
        assert "GitHub" in service_names
        assert "GitLab" in service_names

    def test_no_match(self, sample_accounts: list[Account]) -> None:
        """一致するアカウントがない場合に空のリストが返ることをテストします。."""
        results = fuzzy_search("zzzzz", sample_accounts, threshold=80)
        assert results == []

    def test_empty_query_returns_all(self, sample_accounts: list[Account]) -> None:
        """空のクエリを指定した場合にすべてのアカウントが返ることをテストします。."""
        results = fuzzy_search("", sample_accounts)
        assert len(results) == len(sample_accounts)

    def test_case_insensitive(self, sample_accounts: list[Account]) -> None:
        """大文字小文字を区別せずに検索できることをテストします。."""
        results = fuzzy_search("github", sample_accounts)
        assert len(results) >= 1
        assert results[0].service_name == "GitHub"
