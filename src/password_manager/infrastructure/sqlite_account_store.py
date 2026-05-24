"""SQLiteによるメタデータの永続化を担当するストア."""

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine, select

from password_manager.core.logger import get_logger
from password_manager.infrastructure.exceptions import DatabaseError

from .sqlite_account_model import SqliteAccountModel

logger = get_logger(__name__)


class SqliteAccountStore:
    """SQLiteを用いたアカウントメタデータの管理."""

    def __init__(self, db_path: Path | str) -> None:
        """SqliteAccountStore を初期化します。

        Args:
            db_path: データベースファイルのパス。
        """
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        sqlite_url = f"sqlite:///{self._db_path.absolute()}"
        self._engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        self._create_table()

    def _create_table(self) -> None:
        """テーブルを作成します."""
        SQLModel.metadata.create_all(self._engine)

    def save(self, account_id: str, service_name: str, login_id: str) -> None:
        """メタデータを保存（新規作成または更新）します。

        Args:
            account_id: アカウントID（UUID文字列）。
            service_name: サービス名。
            login_id: ログインID。
        """
        now = datetime.now(UTC).isoformat()

        with Session(self._engine) as session:
            entry = session.get(SqliteAccountModel, account_id)
            if entry is None:
                # 新規作成
                entry = SqliteAccountModel(
                    id=account_id,
                    site_name=service_name,
                    username=login_id,
                    created_at=now,
                    updated_at=now,
                )
                session.add(entry)
            else:
                # 更新
                entry.site_name = service_name
                entry.username = login_id
                entry.updated_at = now
                session.add(entry)
            try:
                session.commit()
            except SQLAlchemyError as e:
                msg = "データベース操作に失敗しました"
                logger.error(
                    msg,
                    exc_info=True,
                    extra={
                        "event": "database_update",
                        "context": {"account_id": account_id},
                    },
                )
                raise DatabaseError(f"{msg} (account_id={account_id}): {e}") from e

    def fetch_by_id(self, account_id: str) -> SqliteAccountModel | None:
        """IDでメタデータを取得します。

        Args:
            account_id: 取得対象のアカウントID（UUID文字列）。

        Returns:
            取得したメタデータ。存在しない場合は None。
        """
        with Session(self._engine) as session:
            entry = session.get(SqliteAccountModel, account_id)
            if entry is None:
                return None
            return entry

    def fetch_all(self) -> list[SqliteAccountModel]:
        """全てのメタデータを取得します。

        Returns:
            全てのメタデータのリスト。
        """
        with Session(self._engine) as session:
            statement = select(SqliteAccountModel).order_by(SqliteAccountModel.site_name)
            entries = session.exec(statement).all()
            return list(entries)

    def delete(self, account_id: str) -> None:
        """メタデータを削除します。

        Args:
            account_id: 削除対象のアカウントID（UUID文字列）。
        """
        with Session(self._engine) as session:
            entry = session.get(SqliteAccountModel, account_id)
            if entry is not None:
                session.delete(entry)
                try:
                    session.commit()
                except SQLAlchemyError as e:
                    msg = "データベース操作に失敗しました"
                    logger.error(
                        msg,
                        exc_info=True,
                        extra={
                            "event": "database_delete",
                            "context": {"account_id": account_id},
                        },
                    )
                    raise DatabaseError(f"{msg} (account_id={account_id}): {e}") from e
