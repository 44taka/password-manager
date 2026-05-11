"""SQLiteによるメタデータの永続化を担当するストア."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class SqliteAccountStore:
    """SQLiteを用いたアカウントメタデータの管理."""

    def __init__(self, db_path: Path | str) -> None:
        """SqliteAccountStoreを初期化します."""
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        """テーブルを作成します."""
        sql = """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_name TEXT NOT NULL,
            username TEXT NOT NULL,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
        self._conn.execute(sql)
        self._conn.commit()

    def save(self, account_id: int, service_name: str, login_id: str, memo: str) -> int:
        """メタデータを保存（新規作成または更新）し、IDを返します."""
        now = datetime.now(UTC).isoformat()

        if account_id == 0:
            # 新規作成
            cursor = self._conn.execute(
                "INSERT INTO entries (site_name, username, notes, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (service_name, login_id, memo, now, now),
            )
            self._conn.commit()
            return cursor.lastrowid  # type: ignore
        else:
            # 更新
            self._conn.execute(
                "UPDATE entries SET site_name = ?, username = ?, notes = ?, updated_at = ? "
                "WHERE id = ?",
                (service_name, login_id, memo, now, account_id),
            )
            self._conn.commit()
            return account_id

    def fetch_by_id(self, account_id: int) -> dict[str, Any] | None:
        """IDでメタデータを取得します."""
        row = self._conn.execute(
            "SELECT * FROM entries WHERE id = ?", (account_id,)
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def fetch_all(self) -> list[dict[str, Any]]:
        """全てのメタデータを取得します."""
        rows = self._conn.execute("SELECT * FROM entries ORDER BY site_name").fetchall()
        return [dict(row) for row in rows]

    def delete(self, account_id: int) -> None:
        """メタデータを削除します."""
        self._conn.execute("DELETE FROM entries WHERE id = ?", (account_id,))
        self._conn.commit()
