"""clipboard モジュールのユニットテスト."""

import time
from unittest.mock import patch

from password_manager.infrastructure.mac_clipboard_service import MacClipboardService


class TestCopyToClipboard:
    """copy_to_clipboard() のテスト."""

    @patch("password_manager.infrastructure.mac_clipboard_service.pyperclip")
    def test_copy_text(self, mock_pyperclip) -> None:
        """テキストがクリップボードにコピーされること."""
        service = MacClipboardService()
        service.copy("test_password", clear_after=0)
        mock_pyperclip.copy.assert_called_once_with("test_password")

    @patch("password_manager.infrastructure.mac_clipboard_service.pyperclip")
    def test_auto_clear(self, mock_pyperclip) -> None:
        """自動クリアが動作すること."""
        mock_pyperclip.paste.return_value = "test_password"
        service = MacClipboardService()

        service.copy("test_password", clear_after=1)

        # 1秒待ってクリアされることを確認
        time.sleep(1.5)
        # copy が2回呼ばれるはず（初回コピー + クリア）
        assert mock_pyperclip.copy.call_count == 2
        mock_pyperclip.copy.assert_any_call("test_password")
        mock_pyperclip.copy.assert_any_call("")

    @patch("password_manager.infrastructure.mac_clipboard_service.pyperclip")
    def test_no_clear_if_content_changed(self, mock_pyperclip) -> None:
        """クリップボードの内容が変わっていたらクリアしないこと."""
        mock_pyperclip.paste.return_value = "different_content"
        service = MacClipboardService()

        service.copy("test_password", clear_after=1)

        time.sleep(1.5)
        # copy は初回の1回のみ（クリアされない）
        assert mock_pyperclip.copy.call_count == 1

    @patch("password_manager.infrastructure.mac_clipboard_service.pyperclip")
    def test_no_clear_when_disabled(self, mock_pyperclip) -> None:
        """clear_after=0 の場合はクリアしないこと."""
        service = MacClipboardService()
        service.copy("test_password", clear_after=0)

        time.sleep(0.5)
        # copy は初回の1回のみ
        assert mock_pyperclip.copy.call_count == 1
