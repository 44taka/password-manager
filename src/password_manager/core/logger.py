"""ロギングの設定と Sentry 統合."""

import json
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any

import sentry_sdk

LOG_DIR = Path.home() / "Library" / "Logs" / "PasswordManager"


class JsonFormatter(logging.Formatter):
    """ログレコードを JSON 形式に変換するフォーマッタ."""

    # サブパッケージ名と表示用のレイヤー名のマッピング
    # TODO: パッケージ追加時の手動更新を不要にするため、ディレクトリ名からの動的生成や、
    # 各パッケージ内での宣言的なレイヤー定義への移行を検討する。
    LAYER_MAPPING = {
        "domain": "Domain",
        "infrastructure": "Infrastructure",
        "usecases": "UseCase",
        "presentation": "Presentation",
        "core": "Core",
        "__main__": "Core",
    }

    def format(self, record: logging.LogRecord) -> str:
        """ログレコードを JSON 文字列にフォーマットします。"""
        # ロガー名（例: password_manager.infrastructure.sqlite）からレイヤーを抽出
        # password_manager.[layer].module の構成を前提とする
        parts = record.name.split(".")
        layer_key = parts[1] if len(parts) > 1 else ""
        layer = self.LAYER_MAPPING.get(layer_key, "Unknown")

        # 基本情報の構築
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "layer": layer,
            "event": getattr(record, "event", "default"),
            "message": record.getMessage(),
            "context": getattr(record, "context", {}),
        }

        # 例外情報がある場合は context に追加
        if record.exc_info:
            if not isinstance(log_data["context"], dict):
                log_data["context"] = {"original_context": log_data["context"]}
            log_data["context"]["error_detail"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logger() -> None:
    """アプリケーション全体のロガーを初期化します。

    - ログレベル: INFO (デフォルト)
    - 保存先: ~/Library/Logs/PasswordManager/app-YYYY-MM-DD.log
    - 形式: JSON (ADR 0007 に準拠)
    - ローテーション: 1日単位、3世代保持
    - Sentry 統合: 環境変数 SENTRY_DSN が設定されている場合に有効化
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 現在の日付を含むファイル名を生成
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"app-{today}.log"

    # 基本設定
    logger = logging.getLogger("password_manager")
    logger.setLevel(logging.INFO)

    # 重複追加防止
    if logger.handlers:
        return

    # JSON フォーマッタ
    formatter = JsonFormatter()

    # ファイル出力 (TimedRotatingFileHandler)
    file_handler = TimedRotatingFileHandler(
        str(log_file),
        when="D",
        interval=1,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # コンソール出力 (開発用)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Sentry 統合
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            # 生パスワードなどの機密情報が送られないよう、
            # デフォルトで一部のデータ収集を制限する設定（必要に応じて詳細化）
            send_default_pii=False,
            traces_sample_rate=1.0,
        )
        logger.info("Sentry initialized.")


def get_logger(name: str) -> logging.Logger:
    """指定された名前のロガーを取得します。

    Args:
        name: ロガー名。

    Returns:
        logging.Logger インスタンス。
    """
    return logging.getLogger(f"password_manager.{name}")
