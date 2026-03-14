"""あいまい検索ロジック."""

from __future__ import annotations

from thefuzz import fuzz

from password_manager.domain.models import Entry


def fuzzy_search(
    query: str,
    entries: list[Entry],
    threshold: int = 60,
) -> list[Entry]:
    """エントリをあいまい検索でフィルタリングし、スコア降順で返す.

    サイト名とユーザー名の両方をマッチング対象にし、
    高い方のスコアを採用する。

    Args:
        query: 検索クエリ文字列
        entries: 検索対象のエントリ一覧
        threshold: マッチと判定する最低スコア (0-100)

    Returns:
        スコア降順でソートされた、閾値以上のエントリ一覧
    """
    if not query:
        return entries

    scored: list[tuple[int, Entry]] = []
    query_lower = query.lower()

    for entry in entries:
        site_score = fuzz.partial_ratio(query_lower, entry.site_name.lower())
        user_score = fuzz.partial_ratio(query_lower, entry.username.lower())
        best_score = max(site_score, user_score)

        if best_score >= threshold:
            scored.append((best_score, entry))

    # スコア降順でソート
    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored]
