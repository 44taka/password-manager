"""infrastructure 層共通フィクスチャ."""

from pathlib import Path

import pytest

from password_manager.infrastructure.sqlite_entry_repository import SqliteEntryRepository


@pytest.fixture
def store(tmp_path: Path) -> SqliteEntryRepository:
    """テスト用の一時DBを使った SqliteEntryRepository."""
    db_path = tmp_path / "test.db"
    return SqliteEntryRepository(db_path)
