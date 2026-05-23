"""SQLiteにおけるアカウントメタデータのORMモデル."""

from sqlmodel import Field, SQLModel


class SqliteAccountModel(SQLModel, table=True):
    """SQLiteの entries テーブルに対応するモデル。

    Attributes:
        id: プライマリキー
        site_name: サービス名
        username: ユーザー名(ログインID)
        created_at: 作成日時(ISO8601形式の文字列)
        updated_at: 更新日時(ISO8601形式の文字列)
    """

    __tablename__ = "entries"  # type: ignore

    id: str = Field(primary_key=True)
    site_name: str
    username: str
    created_at: str
    updated_at: str
