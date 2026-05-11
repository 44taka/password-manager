"""infrastructure 層共通フィクスチャ."""

from pathlib import Path

import pytest

from password_manager.infrastructure.sqlite_account_store import SqliteAccountStore


@pytest.fixture
def sqlite_store(tmp_path: Path) -> SqliteAccountStore:
    """テスト用の一時 DB を使った SqliteAccountStore を提供します。."""
    db_path = tmp_path / "test.db"
    return SqliteAccountStore(db_path)
