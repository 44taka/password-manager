"""SQLiteによるメタデータの永続化を担当するストア."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlmodel import Session, SQLModel, create_engine, select

from .sqlite_account_model import SqliteAccountModel


class SqliteAccountStore:
    """SQLiteを用いたアカウントメタデータの管理."""

    def __init__(self, db_path: Path | str) -> None:
        """SqliteAccountStoreを初期化します."""
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        sqlite_url = f"sqlite:///{self._db_path.absolute()}"
        self._engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        self._create_table()

    def _create_table(self) -> None:
        """テーブルを作成します."""
        SQLModel.metadata.create_all(self._engine)

    def save(self, account_id: int, service_name: str, login_id: str, memo: str) -> int:
        """メタデータを保存（新規作成または更新）し、IDを返します."""
        now = datetime.now(UTC).isoformat()

        with Session(self._engine) as session:
            if account_id == 0:
                # 新規作成
                entry = SqliteAccountModel(
                    site_name=service_name,
                    username=login_id,
                    notes=memo,
                    created_at=now,
                    updated_at=now,
                )
                session.add(entry)
                session.commit()
                session.refresh(entry)
                return entry.id  # type: ignore
            else:
                # 更新
                entry = session.get(SqliteAccountModel, account_id)
                if entry is not None:
                    entry.site_name = service_name
                    entry.username = login_id
                    entry.notes = memo
                    entry.updated_at = now
                    session.add(entry)
                    session.commit()
                return account_id

    def fetch_by_id(self, account_id: int) -> dict[str, Any] | None:
        """IDでメタデータを取得します."""
        with Session(self._engine) as session:
            entry = session.get(SqliteAccountModel, account_id)
            if entry is None:
                return None
            return entry.model_dump()

    def fetch_all(self) -> list[dict[str, Any]]:
        """全てのメタデータを取得します."""
        with Session(self._engine) as session:
            statement = select(SqliteAccountModel).order_by(SqliteAccountModel.site_name)
            entries = session.exec(statement).all()
            return [entry.model_dump() for entry in entries]

    def delete(self, account_id: int) -> None:
        """メタデータを削除します."""
        with Session(self._engine) as session:
            entry = session.get(SqliteAccountModel, account_id)
            if entry is not None:
                session.delete(entry)
                session.commit()
