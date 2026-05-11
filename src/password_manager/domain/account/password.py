"""Password値オブジェクトの定義."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Password:
    """アカウントのパスワードを表す値オブジェクト."""

    value: str

    def __post_init__(self) -> None:
        """バリデーション（必要に応じて追加可能）."""
        if not self.value:
            raise ValueError("パスワードは空であってはなりません。")

    def __str__(self) -> str:
        """ログ出力時などの誤表示を防ぐためにマスクする."""
        return "********"

    def get_raw_value(self) -> str:
        """生のパスワード文字列を取得する."""
        return self.value
