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
        """イテレータを返します。

        Returns:
            アカウントのイテレータ。
        """
        return iter(self._accounts)

    def __len__(self) -> int:
        """要素数を返します。

        Returns:
            保持しているアカウントの数。
        """
        return len(self._accounts)

    def to_list(self) -> list[Account]:
        """リスト形式でアカウントを返します。

        Returns:
            アカウントのリスト。
        """
        return list(self._accounts)

    def search(self, query: str, threshold: int = 60) -> Accounts:
        """アカウントをあいまい検索でフィルタリングし、スコア降順で返します。

        Args:
            query: 検索クエリ。
            threshold: 類似度の閾値（0-100）。デフォルトは 60。

        Returns:
            検索条件に一致したアカウントのコレクション。
        """
        if not query:
            return self

        scored: list[tuple[int, Account]] = []
        query_lower = query.lower()

        for account in self._accounts:
            service_score = self._calculate_score(query_lower, account.service_name.value.lower())
            login_score = self._calculate_score(query_lower, account.login_id.value.lower())
            best_score = max(service_score, login_score)

            if best_score >= threshold:
                scored.append((best_score, account))

        scored.sort(key=lambda x: x[0], reverse=True)
        return Accounts([account for _, account in scored])

    def _calculate_score(self, query: str, target: str) -> int:
        """2つの文字列間の類似度スコアを計算します。

        Args:
            query: 検索クエリ（小文字化済み）。
            target: 比較対象の文字列（小文字化済み）。

        Returns:
            計算されたスコア（0-100）。
        """
        if not query or not target:
            return 0

        # 1. 完全に部分一致している場合は 100点
        if query in target:
            return 100

        # 2. それ以外の場合は、difflib で類似度 (0.0〜1.0) を計算して 100点満点に変換
        matcher = difflib.SequenceMatcher(None, query, target)
        return int(matcher.ratio() * 100)
