"""SQLiteメタデータDB - サイト名・ユーザー名の管理."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Entry:
    """パスワードエントリのメタデータ."""

    id: int
    site_name: str
    username: str
    notes: str
    created_at: str
    updated_at: str


# デフォルトのDBパス
DEFAULT_DB_PATH = Path.home() / ".password-manager" / "entries.db"

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_name TEXT NOT NULL,
    username TEXT NOT NULL,
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


class EntryStore:
    """パスワードエントリのメタデータを管理するストア."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_CREATE_TABLE_SQL)
        self._conn.commit()

    def close(self) -> None:
        """DB接続を閉じる."""
        self._conn.close()

    def add(self, site_name: str, username: str, notes: str = "") -> int:
        """エントリを追加し、IDを返す."""
        now = datetime.now(timezone.utc).isoformat()
        cursor = self._conn.execute(
            "INSERT INTO entries (site_name, username, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (site_name, username, notes, now, now),
        )
        self._conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def get(self, entry_id: int) -> Entry | None:
        """IDでエントリを取得する."""
        row = self._conn.execute(
            "SELECT * FROM entries WHERE id = ?", (entry_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_entry(row)

    def list_all(self) -> list[Entry]:
        """全エントリを取得する."""
        rows = self._conn.execute(
            "SELECT * FROM entries ORDER BY site_name"
        ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def update(
        self,
        entry_id: int,
        *,
        site_name: str | None = None,
        username: str | None = None,
        notes: str | None = None,
    ) -> bool:
        """エントリを更新する. 更新があればTrueを返す."""
        entry = self.get(entry_id)
        if entry is None:
            return False

        new_site_name = site_name if site_name is not None else entry.site_name
        new_username = username if username is not None else entry.username
        new_notes = notes if notes is not None else entry.notes
        now = datetime.now(timezone.utc).isoformat()

        self._conn.execute(
            "UPDATE entries SET site_name = ?, username = ?, notes = ?, updated_at = ? "
            "WHERE id = ?",
            (new_site_name, new_username, new_notes, now, entry_id),
        )
        self._conn.commit()
        return True

    def delete(self, entry_id: int) -> bool:
        """エントリを削除する. 削除があればTrueを返す."""
        cursor = self._conn.execute(
            "DELETE FROM entries WHERE id = ?", (entry_id,)
        )
        self._conn.commit()
        return cursor.rowcount > 0

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> Entry:
        """sqlite3.RowをEntryに変換する."""
        return Entry(
            id=row["id"],
            site_name=row["site_name"],
            username=row["username"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
