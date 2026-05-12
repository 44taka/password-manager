"""MacClipboardService のユニットテスト."""

from unittest.mock import MagicMock, patch

from password_manager.infrastructure.mac_clipboard_service import MacClipboardService


class TestMacClipboardService:
    """MacClipboardServiceクラスのテスト."""

    @patch("password_manager.infrastructure.mac_clipboard_service.pyperclip")
    def test_copy_success(self, mock_pyperclip: MagicMock) -> None:
        """クリップボードへのコピーが成功することを確認します。"""
        service = MacClipboardService()
        result = service.copy("test_password")

        assert result is True
        mock_pyperclip.copy.assert_called_once_with("test_password")

    @patch("password_manager.infrastructure.mac_clipboard_service.pyperclip")
    def test_copy_exception(self, mock_pyperclip: MagicMock) -> None:
        """pyperclipで例外が発生した場合にFalseを返すことを確認します。"""
        mock_pyperclip.copy.side_effect = Exception("Clipboard error")
        service = MacClipboardService()
        result = service.copy("test_password")

        assert result is False

    @patch("password_manager.infrastructure.mac_clipboard_service.pyperclip")
    def test_clear_when_match(self, mock_pyperclip: MagicMock) -> None:
        """指定した内容と現在のクリップボードが一致する場合に消去することを確認します。"""
        service = MacClipboardService()
        mock_pyperclip.paste.return_value = "test_password"

        service.clear("test_password")

        mock_pyperclip.paste.assert_called_once()
        mock_pyperclip.copy.assert_called_once_with("")

    @patch("password_manager.infrastructure.mac_clipboard_service.pyperclip")
    def test_clear_when_mismatch(self, mock_pyperclip: MagicMock) -> None:
        """現在のクリップボードの内容が引数と異なる場合は消去しないことを確認します。"""
        service = MacClipboardService()
        mock_pyperclip.paste.return_value = "user_copied_text"

        service.clear("test_password")

        mock_pyperclip.paste.assert_called_once()
        mock_pyperclip.copy.assert_not_called()
