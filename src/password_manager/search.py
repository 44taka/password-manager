"""あいまい検索ロジック."""

from __future__ import annotations

from thefuzz import fuzz

from password_manager.domain.account import Account


def fuzzy_search(
    query: str,
    accounts: list[Account],
    threshold: int = 60,
) -> list[Account]:
    """アカウントをあいまい検索でフィルタリングし、スコア降順で返す.

    サービス名とログインIDの両方をマッチング対象にし、
    高い方のスコアを採用する。

    Args:
        query: 検索クエリ文字列
        accounts: 検索対象のアカウント一覧
        threshold: マッチと判定する最低スコア (0-100)

    Returns:
        スコア降順でソートされた、閾値以上のカウント一覧
    """
    if not query:
        return accounts

    scored: list[tuple[int, Account]] = []
    query_lower = query.lower()

    for account in accounts:
        service_score = fuzz.partial_ratio(query_lower, account.service_name.lower())
        login_score = fuzz.partial_ratio(query_lower, account.login_id.lower())
        best_score = max(service_score, login_score)

        if best_score >= threshold:
            scored.append((best_score, account))

    # スコア降順でソート
    scored.sort(key=lambda x: x[0], reverse=True)
    return [account for _, account in scored]
