"""fuzzy_search のユニットテスト."""

import pytest

from password_manager.domain.models import Entry
from password_manager.search import fuzzy_search


@pytest.fixture
def sample_entries(make_entry) -> list[Entry]:
    """テスト用のエントリ一覧."""
    return [
        make_entry(entry_id=1, site_name="GitHub", username="tanaka@example.com"),
        make_entry(entry_id=2, site_name="Google", username="tanaka@gmail.com"),
        make_entry(entry_id=3, site_name="Amazon", username="tanaka@amazon.co.jp"),
        make_entry(entry_id=4, site_name="GitLab", username="tanaka@gitlab.com"),
        make_entry(entry_id=5, site_name="Twitter", username="tanaka_dev"),
    ]


class TestFuzzySearch:
    """fuzzy_search() のテスト."""

    def test_exact_match(self, sample_entries: list[Entry]) -> None:
        results = fuzzy_search("GitHub", sample_entries)
        assert len(results) >= 1
        assert results[0].site_name == "GitHub"

    def test_partial_match(self, sample_entries: list[Entry]) -> None:
        results = fuzzy_search("git", sample_entries)
        site_names = [e.site_name for e in results]
        assert "GitHub" in site_names
        assert "GitLab" in site_names

    def test_no_match(self, sample_entries: list[Entry]) -> None:
        results = fuzzy_search("zzzzz", sample_entries, threshold=80)
        assert results == []

    def test_empty_query_returns_all(self, sample_entries: list[Entry]) -> None:
        results = fuzzy_search("", sample_entries)
        assert len(results) == len(sample_entries)

    def test_case_insensitive(self, sample_entries: list[Entry]) -> None:
        results = fuzzy_search("github", sample_entries)
        assert len(results) >= 1
        assert results[0].site_name == "GitHub"

    def test_username_match(self, sample_entries: list[Entry]) -> None:
        """ユーザー名でもマッチすること."""
        results = fuzzy_search("tanaka_dev", sample_entries)
        assert len(results) >= 1
        site_names = [e.site_name for e in results]
        assert "Twitter" in site_names

    def test_results_sorted_by_score(self, sample_entries: list[Entry]) -> None:
        """完全一致に近いものが先頭に来ること."""
        results = fuzzy_search("GitHub", sample_entries)
        # GitHubがGitLabより先に来るはず
        if len(results) >= 2:
            github_idx = next(
                i for i, e in enumerate(results) if e.site_name == "GitHub"
            )
            gitlab_idx = next(
                (i for i, e in enumerate(results) if e.site_name == "GitLab"),
                None,
            )
            if gitlab_idx is not None:
                assert github_idx < gitlab_idx

    def test_threshold_filtering(self, sample_entries: list[Entry]) -> None:
        """閾値でフィルタリングされること."""
        results_low = fuzzy_search("g", sample_entries, threshold=30)
        results_high = fuzzy_search("g", sample_entries, threshold=90)
        assert len(results_low) >= len(results_high)
