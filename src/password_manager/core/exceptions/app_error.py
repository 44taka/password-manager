"""アプリケーション全体の基底例外クラスの定義."""


class AppError(Exception):
    """アプリケーション内で発生する全ての独自例外の基底クラス."""

    def __init__(self, message: str) -> None:
        """AppError を初期化します。

        Args:
            message: エラーメッセージ。
        """
        super().__init__(message)
        self.message = message
