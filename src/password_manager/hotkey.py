"""グローバルショートカット - Cmd+Shift+P での検索ウィンドウ呼び出し."""

from __future__ import annotations

from collections.abc import Callable
from threading import Thread

from pynput import keyboard


class HotkeyManager:
    """グローバルホットキーの管理.

    macOS ではアクセシビリティ権限が必要:
    「システム設定 > プライバシーとセキュリティ > アクセシビリティ」で
    ターミナルまたはアプリに権限を付与すること。
    """

    # Cmd+Shift+P のキーコンビネーション
    HOTKEY = "<cmd>+<shift>+p"

    def __init__(self) -> None:
        self._listener: keyboard.GlobalHotKeys | None = None
        self._thread: Thread | None = None
        self._callback: Callable[[], None] | None = None

    def register(self, callback: Callable[[], None]) -> None:
        """ホットキーが押されたときのコールバックを登録する."""
        self._callback = callback

    def start(self) -> None:
        """ホットキーリスナーをバックグラウンドスレッドで開始する."""
        if self._callback is None:
            msg = "コールバックが登録されていません。register() を先に呼んでください。"
            raise RuntimeError(msg)

        self._listener = keyboard.GlobalHotKeys({
            self.HOTKEY: self._callback,
        })
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        """ホットキーリスナーを停止する."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
