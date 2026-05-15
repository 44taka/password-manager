"""Core レイヤーの例外パッケージ.

このパッケージは、アプリケーション全体で共有される基底例外を提供します。
"""

from .app_error import AppError

__all__ = ["AppError"]
