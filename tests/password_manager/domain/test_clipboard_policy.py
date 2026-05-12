"""ClipboardPolicy のテスト."""

from datetime import UTC, datetime, timedelta

from password_manager.domain.account.clipboard_policy import ClipboardPolicy


class TestClipboardPolicy:
    """ClipboardPolicyクラスのテスト."""

    def test_initialization(self) -> None:
        """デフォルトの保持時間で初期化できることを確認します。"""
        policy = ClipboardPolicy()
        assert policy.retention_seconds == 15

        policy_custom = ClipboardPolicy(retention_seconds=30)
        assert policy_custom.retention_seconds == 30

    def test_is_expired(self) -> None:
        """保持期限が切れているか正しく判定できることを確認します。"""
        policy = ClipboardPolicy(retention_seconds=15)
        now = datetime.now(UTC)

        # 期限内 (10秒経過)
        copied_at_1 = now - timedelta(seconds=10)
        assert policy.is_expired(copied_at_1, now) is False

        # 期限ジャスト (15秒経過)
        copied_at_2 = now - timedelta(seconds=15)
        assert policy.is_expired(copied_at_2, now) is True

        # 期限切れ (20秒経過)
        copied_at_3 = now - timedelta(seconds=20)
        assert policy.is_expired(copied_at_3, now) is True
