"""Accountのファーストクラスコレクション."""

from __future__ import annotations

import difflib
from collections.abc import Iterator
from dataclasses import dataclass

from .account import Account


@dataclass(frozen=True)
class Accounts:
    """アカウントのコレクションオブジェクト."""

    _accounts: list[Account]

    def __iter__(self) -> Iterator[Account]:
        """イテレータを返す."""
        return iter(self._accounts)

    def __len__(self) -> int:
        """要素数を返す."""
        return len(self._accounts)

    def to_list(self) -> list[Account]:
        """リストとして返す."""
        return list(self._accounts)

    def search(self, query: str, threshold: int = 60) -> Accounts:
        """アカウントをあいまい検索でフィルタリングし、スコア降順で返す."""
        if not query:
            return self

        scored: list[tuple[int, Account]] = []
        query_lower = query.lower()

        for account in self._accounts:
            service_score = self._calculate_score(query_lower, account.service_name.lower())
            login_score = self._calculate_score(query_lower, account.login_id.lower())
            best_score = max(service_score, login_score)

            if best_score >= threshold:
                scored.append((best_score, account))

        scored.sort(key=lambda x: x[0], reverse=True)
        return Accounts([account for _, account in scored])

    def _calculate_score(self, query: str, target: str) -> int:
        """標準ライブラリのみを使ったスコア計算ロジック."""
        if not query or not target:
            return 0

        # 1. 完全に部分一致している場合は 100点
        if query in target:
            return 100

        # 2. それ以外の場合は、difflib で類似度 (0.0〜1.0) を計算して 100点満点に変換
        matcher = difflib.SequenceMatcher(None, query, target)
        return int(matcher.ratio() * 100)
