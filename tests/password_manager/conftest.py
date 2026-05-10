"""password_manager パッケージ共通フィクスチャ."""

import pytest

from password_manager.domain.models import Entry


@pytest.fixture
def make_entry() -> any:
    """Entry を生成するファクトリフィクスチャです。.

    Returns:
        any: Entry オブジェクトを生成するファクトリ関数。
    """

    def _factory(
        entry_id: int = 1,
        site_name: str = "Example",
        username: str = "test_user",
        notes: str = "",
        created_at: str = "2024-01-01T00:00:00",
        updated_at: str = "2024-01-01T00:00:00",
    ) -> Entry:
        """エントリを生成します。."""
        return Entry(
            id=entry_id,
            site_name=site_name,
            username=username,
            notes=notes,
            created_at=created_at,
            updated_at=updated_at,
        )

    return _factory
