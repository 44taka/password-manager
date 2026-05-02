"""password_manager パッケージ共通フィクスチャ."""

import pytest

from password_manager.domain.models import Entry


@pytest.fixture
def make_entry():
    """Entry を生成するファクトリフィクスチャ.

    使用例:
        def test_something(make_entry):
            entry = make_entry(entry_id=1, site_name="GitHub", username="user@example.com")
    """

    def _factory(
        entry_id: int = 1,
        site_name: str = "Example",
        username: str = "test_user",
        notes: str = "",
        created_at: str = "2024-01-01T00:00:00",
        updated_at: str = "2024-01-01T00:00:00",
    ) -> Entry:
        return Entry(
            id=entry_id,
            site_name=site_name,
            username=username,
            notes=notes,
            created_at=created_at,
            updated_at=updated_at,
        )

    return _factory
