"""infrastructure 層共通フィクスチャ."""

from pathlib import Path

import pytest

from password_manager.infrastructure.sqlite_entry_repository import (
    SqliteEntryRepository,
)


@pytest.fixture
def store(tmp_path: Path) -> SqliteEntryRepository:
    """テスト用の一時 DB を使った SqliteEntryRepository を提供します。.

    Args:
        tmp_path: pytest 提供の一時ディレクトリパス。

    Returns:
        SqliteEntryRepository: 初期化済みのリポジトリ。
    """
    db_path = tmp_path / "test.db"
    return SqliteEntryRepository(db_path)
