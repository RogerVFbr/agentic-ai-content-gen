import pytest
from unittest.mock import MagicMock

from crosscutting.service_provider import ServiceCollection, ServiceProvider


class TestServiceCollection:

    @pytest.fixture
    def service_collection(self):
        return ServiceCollection()

    def test_add_transient(self, service_collection):
        # Arrange
        mock_service = MagicMock()

        # Act
        service_collection.add_transient(MagicMock, mock_service)

        # Assert
        assert MagicMock in service_collection._services
        assert service_collection._services[MagicMock]["implementation"] == mock_service
        assert service_collection._services[MagicMock]["lifetime"] == "transient"

    def test_add_singleton(self, service_collection):
        # Arrange
        mock_service = MagicMock()

        # Act
        service_collection.add_singleton(MagicMock, mock_service)

        # Assert
        assert MagicMock in service_collection._services
        assert service_collection._services[MagicMock]["implementation"] == mock_service
        assert service_collection._services[MagicMock]["lifetime"] == "singleton"

    def test_merge(self, service_collection):
        # Arrange
        other_collection = ServiceCollection()
        mock_service = MagicMock()
        other_collection.add_singleton(MagicMock, mock_service)

        # Act
        service_collection.merge(other_collection)

        # Assert
        assert MagicMock in service_collection._services
        assert service_collection._services[MagicMock]["implementation"] == mock_service

    def test_build_service_provider(self, service_collection):
        # Act
        provider = service_collection.build_service_provider()

        # Assert
        assert isinstance(provider, ServiceProvider)

    def test_transient_service_resolution(self, service_collection):
        # Arrange
        service_collection.add_transient(MagicMock, MagicMock)

        # Act
        provider = service_collection.build_service_provider()
        service_instance_1 = provider.get_service(MagicMock)
        service_instance_2 = provider.get_service(MagicMock)

        # Assert
        assert service_instance_1 != service_instance_2  # Transient services should create new instances

    def test_singleton_service_resolution(self, service_collection):
        # Arrange
        service_collection.add_singleton(MagicMock, MagicMock)

        # Act
        provider = service_collection.build_service_provider()
        service_instance_1 = provider.get_service(MagicMock)
        service_instance_2 = provider.get_service(MagicMock)

        # Assert
        assert service_instance_1 == service_instance_2  # Singleton services should return the same instance