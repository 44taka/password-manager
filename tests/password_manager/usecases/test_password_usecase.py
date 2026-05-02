"""PasswordUseCase のユニットテスト."""

from unittest.mock import MagicMock

from password_manager.domain.models import Entry
from password_manager.usecases.password_usecase import PasswordUseCase


def _make_usecase(entry: Entry | None = None) -> tuple[PasswordUseCase, MagicMock]:
    """UseCase と ClipboardService のモックを生成するヘルパー."""
    entry_repo = MagicMock()
    entry_repo.get.return_value = entry

    password_repo = MagicMock()
    clipboard = MagicMock()

    usecase = PasswordUseCase(
        entry_repo=entry_repo,
        password_repo=password_repo,
        clipboard_service=clipboard,
    )
    return usecase, clipboard


class TestCopyUsername:
    """copy_username() のテスト."""

    def test_copy_username_success(self, make_entry) -> None:
        """ユーザー名がクリップボードにコピーされ、Trueが返ること."""
        entry = make_entry(username="john_doe")
        usecase, clipboard = _make_usecase(entry=entry)

        result = usecase.copy_username(entry_id=1)

        assert result is True
        clipboard.copy.assert_called_once_with("john_doe", clear_after=0)

    def test_copy_username_entry_not_found(self) -> None:
        """エントリが存在しない場合はFalseが返り、コピーされないこと."""
        usecase, clipboard = _make_usecase(entry=None)

        result = usecase.copy_username(entry_id=999)

        assert result is False
        clipboard.copy.assert_not_called()

    def test_copy_username_no_auto_clear_by_default(self, make_entry) -> None:
        """デフォルトでは自動クリアが無効（clear_after=0）であること."""
        entry = make_entry(username="alice")
        usecase, clipboard = _make_usecase(entry=entry)

        usecase.copy_username(entry_id=1)

        _, kwargs = clipboard.copy.call_args
        assert kwargs.get("clear_after", 0) == 0
