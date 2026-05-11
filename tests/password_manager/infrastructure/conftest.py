"""infrastructure 層のテスト用共通フィクスチャ."""

from collections.abc import Generator
from pathlib import Path

import keyring
import pytest

from password_manager.infrastructure.sqlite_account_store import SqliteAccountStore

from .keyring_fakes import InMemoryKeyring


@pytest.fixture
def mock_keyring() -> Generator[InMemoryKeyring]:
    """Keyring バックエンドをインメモリに差し替えます."""
    backend = InMemoryKeyring()
    original_backend = keyring.get_keyring()
    keyring.set_keyring(backend)
    yield backend
    keyring.set_keyring(original_backend)


@pytest.fixture
def sqlite_store(tmp_path: Path) -> Generator[SqliteAccountStore]:
    """テスト用の一時 DB を使った SqliteAccountStore を提供します."""
    db_path = tmp_path / "test.db"
    store = SqliteAccountStore(db_path)
    yield store
    store._engine.dispose()
