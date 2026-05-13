"""Domain レイヤーの例外パッケージ."""

from .domain_error import DomainError
from .validation_error import ValidationError

__all__ = ["DomainError", "ValidationError"]
