"""Domain Models."""

from dataclasses import dataclass

@dataclass
class Entry:
    """パスワードエントリのメタデータ."""

    id: int
    site_name: str
    username: str
    notes: str
    created_at: str
    updated_at: str
