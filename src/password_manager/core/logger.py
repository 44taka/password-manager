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


class LayerContextFilter(logging.Filter):
    """ロギングコンテキストにレイヤー情報を付加するフィルタ.

    ロガーの名前（モジュールパス）を解析し、そのログがオニオンアーキテクチャの
    どのレイヤーから出力されたものかを判定して、LogRecord に属性として追加します。
    """

    # サブパッケージ名と表示用のレイヤー名のマッピング
    LAYER_MAPPING = {
        "domain": "Domain",
        "infrastructure": "Infrastructure",
        "usecases": "UseCase",
        "presentation": "Presentation",
        "core": "Core",
        "__main__": "Core",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """ログレコードにレイヤー情報を付与します。

        ロガー名（例: password_manager.infrastructure.sqlite）のドット区切り
        2番目の要素をレイヤーキーとして使用し、対応するレイヤー名を record.layer
        属性にセットします。

        Args:
            record: フィルタリング対象の LogRecord インスタンス。

        Returns:
            常に True。レコードは常に通過させ、属性の付与のみを行います。
        """
        # ロガー名（例: password_manager.infrastructure.sqlite）からレイヤーを抽出
        # password_manager.[layer].module の構成を前提とする
        parts = record.name.split(".")
        layer_key = parts[1] if len(parts) > 1 else ""
        record.layer = self.LAYER_MAPPING.get(layer_key, "Unknown")
        return True


class JsonFormatter(logging.Formatter):
    """ログレコードを構造化された JSON 形式に変換するフォーマッタ.

    ADR 0007 に準拠し、タイムスタンプ、レベル、レイヤー、メッセージ、
    および任意のコンテキスト情報を含む JSON 文字列を生成します。
    """

    def format(self, record: logging.LogRecord) -> str:
        """ログレコードを JSON 文字列にフォーマットします。

        LayerContextFilter によって付与されたレイヤー情報を参照し、
        例外情報がある場合はそれも context に含めて JSON 化します。

        Args:
            record: フォーマット対象の LogRecord インスタンス。

        Returns:
            JSON 形式のログ文字列。
        """
        # LayerContextFilter によって付与されたレイヤー情報を取得
        layer = getattr(record, "layer", "Unknown")

        # 基本情報の構築
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).astimezone().isoformat(),
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
    """アプリケーション全体のロギング基盤を初期化および設定します。

    以下の設定を行います：
    - ログレベルの設定 (デフォルト: INFO)
    - LayerContextFilter の登録
    - TimedRotatingFileHandler によるファイル出力設定
    - StreamHandler による標準出力設定
    - Sentry 統合 (環境変数 SENTRY_DSN が存在する場合)

    ファイルログは ~/Library/Logs/PasswordManager に保存され、
    1日ごとにローテーションされます（最大3世代保持）。
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # ログファイル名 (TimedRotatingFileHandler がローテーション時に日付を自動付与する)
    log_file = LOG_DIR / "app.log"

    # 基本設定
    logger = logging.getLogger("password_manager")
    logger.setLevel(logging.INFO)

    # レイヤー情報付与用のフィルタを追加
    logger.addFilter(LayerContextFilter())

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
    """アプリケーション内で使用する共通のロガーを取得します。

    引数として渡された名前に 'password_manager.' プレフィックスを適切に付与し、
    一貫した階層構造を持つロガーを返します。__name__ を渡すことで、
    自動的にモジュールパスに基づいたロガー名が設定されます。

    Args:
        name: ロガーの識別名。通常は呼び出し元モジュールの __name__ を指定します。

    Returns:
        設定済みの logging.Logger インスタンス。
    """
    prefix = "password_manager"
    # 重複付与を防止
    if name.startswith(f"{prefix}."):
        full_name = name
    elif name == prefix:
        full_name = prefix
    else:
        full_name = f"{prefix}.{name}"

    return logging.getLogger(full_name)
