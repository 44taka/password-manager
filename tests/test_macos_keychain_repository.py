"""KeychainManager のユニットテスト（keyring をモック化）."""

import pytest

from password_manager.infrastructure.macos_keychain_repository import MacosKeychainRepository


class TestKeychainManager:
    """KeychainManager のテスト."""

    def test_save_and_get(self, mocker) -> None:
        mock_set = mocker.patch("password_manager.infrastructure.macos_keychain_repository.keyring.set_password")
        mock_get = mocker.patch(
            "password_manager.infrastructure.macos_keychain_repository.keyring.get_password",
            return_value="secret123",
        )

        km = MacosKeychainRepository(service_name="test-service")
        km.save(1, "secret123")
        result = km.get(1)

        mock_set.assert_called_once_with("test-service", "1", "secret123")
        mock_get.assert_called_once_with("test-service", "1")
        assert result == "secret123"

    def test_get_nonexistent(self, mocker) -> None:
        mocker.patch(
            "password_manager.infrastructure.macos_keychain_repository.keyring.get_password",
            return_value=None,
        )

        km = MacosKeychainRepository(service_name="test-service")
        result = km.get(999)

        assert result is None

    def test_delete(self, mocker) -> None:
        mock_delete = mocker.patch(
            "password_manager.infrastructure.macos_keychain_repository.keyring.delete_password"
        )

        km = MacosKeychainRepository(service_name="test-service")
        km.delete(1)

        mock_delete.assert_called_once_with("test-service", "1")

    def test_delete_nonexistent_does_not_raise(self, mocker) -> None:
        import keyring.errors

        mocker.patch(
            "password_manager.infrastructure.macos_keychain_repository.keyring.delete_password",
            side_effect=keyring.errors.PasswordDeleteError(),
        )

        km = MacosKeychainRepository(service_name="test-service")
        # 例外が出ないことを確認
        km.delete(999)


class TestKeychainManagerServiceName:
    """サービス名の設定テスト."""

    def test_default_service_name(self) -> None:
        km = MacosKeychainRepository()
        assert km._service_name == "password-manager"

    def test_custom_service_name(self) -> None:
        km = MacosKeychainRepository(service_name="custom-service")
        assert km._service_name == "custom-service"
