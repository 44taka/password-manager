"""PasswordUseCase のユニットテスト."""

from unittest.mock import MagicMock

from password_manager.domain.models import Entry
from password_manager.usecases.password_usecase import PasswordUseCase


def _make_entry(entry_id: int = 1, username: str = "test_user") -> Entry:
    return Entry(
        id=entry_id,
        site_name="Example",
        username=username,
        notes="",
        created_at="2024-01-01",
        updated_at="2024-01-01",
    )


class TestCopyUsername:
    """copy_username() のテスト."""

    def _make_usecase(
        self,
        entry: Entry | None = None,
    ) -> tuple[PasswordUseCase, MagicMock]:
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

    def test_copy_username_success(self) -> None:
        """ユーザー名がクリップボードにコピーされ、Trueが返ること."""
        entry = _make_entry(username="john_doe")
        usecase, clipboard = self._make_usecase(entry=entry)

        result = usecase.copy_username(entry_id=1)

        assert result is True
        clipboard.copy.assert_called_once_with("john_doe", clear_after=0)

    def test_copy_username_entry_not_found(self) -> None:
        """エントリが存在しない場合はFalseが返り、コピーされないこと."""
        usecase, clipboard = self._make_usecase(entry=None)

        result = usecase.copy_username(entry_id=999)

        assert result is False
        clipboard.copy.assert_not_called()

    def test_copy_username_no_auto_clear_by_default(self) -> None:
        """デフォルトでは自動クリアが無効（clear_after=0）であること."""
        entry = _make_entry(username="alice")
        usecase, clipboard = self._make_usecase(entry=entry)

        usecase.copy_username(entry_id=1)

        _, kwargs = clipboard.copy.call_args
        assert kwargs.get("clear_after", 0) == 0
