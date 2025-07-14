import pytest
from unittest.mock import MagicMock

from crosscutting.service_provider import ServiceCollection


class TestServiceProvider:

    @pytest.fixture
    def service_collection(self):
        return ServiceCollection()

    def test_missing_dependency(self, service_collection):
        # Arrange: Define a class `A` that depends on a class `B`, but do not register `B` in the service collection.
        class A:
            def __init__(self, b: "B"):
                self.b = b

        service_collection.add_transient(A)
        provider = service_collection.build_service_provider()

        # Act & Assert: Attempt to resolve `A` and verify that an exception is raised due to the missing dependency `B`.
        with pytest.raises(Exception, match="Service of type .* not registered."):
            provider.get_service(A)

    def test_unknown_lifetime(self, service_collection):
        # Arrange: Manually add a service with an invalid lifetime to the service collection.
        service_collection._services["UnknownService"] = {
            "implementation": MagicMock(),
            "lifetime": "unknown",
            "is_factory": False,
        }
        provider = service_collection.build_service_provider()

        # Act & Assert: Attempt to resolve the service and verify that an exception is raised for the unknown lifetime.
        with pytest.raises(Exception, match="Unknown lifetime for service .*"):
            provider.get_service("UnknownService")

    def test_recursive_factory_resolution(self, service_collection):
        # Arrange: Define a class `A` that depends on an integer value. Register `A` as transient and the integer as a singleton.
        class A:
            def __init__(self, value: int):
                self.value = value

        service_collection.add_transient(A, lambda sp: A(sp.get_service(int)))
        service_collection.add_singleton(int, lambda sp: 42)

        provider = service_collection.build_service_provider()

        # Act: Resolve an instance of `A` using the service provider.
        a_instance = provider.get_service(A)

        # Assert: Verify that the resolved instance of `A` has the correct integer value injected.
        assert a_instance.value == 42

    def test_recursive_factory_with_multiple_dependencies(self, service_collection):
        # Arrange
        class A:
            def __init__(self, value: int):
                self.value = value

        class B:
            def __init__(self, a: A, text: str):
                self.a = a
                self.text = text

        service_collection.add_transient(A, lambda sp: A(sp.get_service(int)))
        service_collection.add_transient(B, lambda sp: B(sp.get_service(A), sp.get_service(str)))
        service_collection.add_singleton(int, lambda sp: 42)
        service_collection.add_singleton(str, lambda sp: "Hello")

        provider = service_collection.build_service_provider()

        # Act
        b_instance = provider.get_service(B)

        # Assert
        assert b_instance.a.value == 42
        assert b_instance.text == "Hello"

    def test_recursive_nested_factory_dependencies(self, service_collection):
        # Arrange
        class A:
            def __init__(self, value: int):
                self.value = value

        class B:
            def __init__(self, a: A):
                self.a = a

        class C:
            def __init__(self, b: B):
                self.b = b

        service_collection.add_transient(A, lambda sp: A(sp.get_service(int)))
        service_collection.add_transient(B, lambda sp: B(sp.get_service(A)))
        service_collection.add_transient(C, lambda sp: C(sp.get_service(B)))
        service_collection.add_singleton(int, lambda sp: 99)

        provider = service_collection.build_service_provider()

        # Act
        c_instance = provider.get_service(C)

        # Assert
        assert c_instance.b.a.value == 99

    def test_recursive_factory_with_optional_dependency(self, service_collection):
        # Arrange
        class A:
            def __init__(self, value: int = None):
                self.value = value

        service_collection.add_transient(A, lambda sp: A(sp.get_service(int) if int in sp._services else None))
        provider = service_collection.build_service_provider()

        # Act
        a_instance = provider.get_service(A)

        # Assert
        assert a_instance.value is None  # Optional dependency not registered

    def test_invalid_service_type(self, service_collection):
        # Arrange: Build a service provider without registering any services.
        provider = service_collection.build_service_provider()

        # Act & Assert: Attempt to resolve a non-existent service and verify that an exception is raised.
        with pytest.raises(Exception, match="Service of type .* not registered."):
            provider.get_service("NonExistentService")

    def test_singleton_service_resolution(self, service_collection):
        # Arrange
        class SingletonService:
            pass

        service_collection.add_singleton(SingletonService)
        provider = service_collection.build_service_provider()

        # Act
        instance1 = provider.get_service(SingletonService)
        instance2 = provider.get_service(SingletonService)

        # Assert
        assert instance1 is instance2  # Singleton should return the same instance

    def test_transient_service_resolution(self, service_collection):
        # Arrange
        class TransientService:
            pass

        service_collection.add_transient(TransientService)
        provider = service_collection.build_service_provider()

        # Act
        instance1 = provider.get_service(TransientService)
        instance2 = provider.get_service(TransientService)

        # Assert
        assert instance1 is not instance2  # Transient should return new instances

    def test_factory_service_resolution_for_transient(self, service_collection):
        # Arrange
        class FactoryService:
            def __init__(self, value):
                self.value = value

        service_collection.add_transient(FactoryService, lambda sp: FactoryService(42))
        provider = service_collection.build_service_provider()

        # Act
        instance1 = provider.get_service(FactoryService)
        instance2 = provider.get_service(FactoryService)

        # Assert
        assert instance1 is not instance2  # Factory should return new instances
        assert instance1.value == 42
        assert instance2.value == 42

    def test_factory_service_resolution_for_singleton(self, service_collection):
        # Arrange
        class FactoryService:
            def __init__(self, value):
                self.value = value

        service_collection.add_singleton(FactoryService, lambda sp: FactoryService(42))
        provider = service_collection.build_service_provider()

        # Act
        instance1 = provider.get_service(FactoryService)
        instance2 = provider.get_service(FactoryService)

        # Assert
        assert instance1 is instance2

    def test_dependency_injection_for_transient(self, service_collection):
        # Arrange
        class Logger:
            pass

        class Repository:
            def __init__(self, logger: Logger):
                self.logger = logger

        service_collection.add_transient(Logger)
        service_collection.add_transient(Repository)
        provider = service_collection.build_service_provider()

        # Act
        repository = provider.get_service(Repository)

        # Assert
        assert isinstance(repository, Repository)
        assert isinstance(repository.logger, Logger)

    def test_dependency_injection_for_singleton(self, service_collection):
        # Arrange
        class Logger:
            pass

        class Repository:
            def __init__(self, logger: Logger):
                self.logger = logger

        service_collection.add_singleton(Logger)
        service_collection.add_singleton(Repository)
        provider = service_collection.build_service_provider()

        # Act
        repository = provider.get_service(Repository)

        # Assert
        assert isinstance(repository, Repository)
        assert isinstance(repository.logger, Logger)

    def test_multiple_dependencies_for_transient(self, service_collection):
        # Arrange: Define classes with multiple dependencies
        class Logger:
            pass

        class Config:
            pass

        class Service:
            def __init__(self, logger: Logger, config: Config):
                self.logger = logger
                self.config = config

        service_collection.add_transient(Logger)
        service_collection.add_transient(Config)
        service_collection.add_transient(Service)
        provider = service_collection.build_service_provider()

        # Act: Resolve the service
        service = provider.get_service(Service)

        # Assert: Verify that all dependencies are injected correctly
        assert isinstance(service, Service)
        assert isinstance(service.logger, Logger)
        assert isinstance(service.config, Config)

    def test_multiple_dependencies_for_singleton(self, service_collection):
        # Arrange: Define classes with multiple dependencies
        class Logger:
            pass

        class Config:
            pass

        class Service:
            def __init__(self, logger: Logger, config: Config):
                self.logger = logger
                self.config = config

        service_collection.add_singleton(Logger)
        service_collection.add_singleton(Config)
        service_collection.add_singleton(Service)
        provider = service_collection.build_service_provider()

        # Act: Resolve the service
        service = provider.get_service(Service)

        # Assert: Verify that all dependencies are injected correctly
        assert isinstance(service, Service)
        assert isinstance(service.logger, Logger)
        assert isinstance(service.config, Config)

    def test_nested_dependencies_for_transient(self, service_collection):
        # Arrange: Define classes with nested dependencies
        class Logger:
            pass

        class Repository:
            def __init__(self, logger: Logger):
                self.logger = logger

        class Service:
            def __init__(self, repository: Repository):
                self.repository = repository

        service_collection.add_transient(Logger)
        service_collection.add_transient(Repository)
        service_collection.add_transient(Service)
        provider = service_collection.build_service_provider()

        # Act: Resolve the service
        service = provider.get_service(Service)

        # Assert: Verify that nested dependencies are injected correctly
        assert isinstance(service, Service)
        assert isinstance(service.repository, Repository)
        assert isinstance(service.repository.logger, Logger)

    def test_nested_dependencies_for_singleton(self, service_collection):
        # Arrange: Define classes with nested dependencies
        class Logger:
            pass

        class Repository:
            def __init__(self, logger: Logger):
                self.logger = logger

        class Service:
            def __init__(self, repository: Repository):
                self.repository = repository

        service_collection.add_singleton(Logger)
        service_collection.add_singleton(Repository)
        service_collection.add_singleton(Service)
        provider = service_collection.build_service_provider()

        # Act: Resolve the service
        service = provider.get_service(Service)

        # Assert: Verify that nested dependencies are injected correctly
        assert isinstance(service, Service)
        assert isinstance(service.repository, Repository)
        assert isinstance(service.repository.logger, Logger)

    def test_dependency_with_factory_for_transient(self, service_collection):
        # Arrange: Define a class with a dependency provided by a factory
        class Config:
            def __init__(self, value):
                self.value = value

        class Service:
            def __init__(self, config: Config):
                self.config = config

        service_collection.add_transient(Config, lambda sp: Config(42))
        service_collection.add_transient(Service)
        provider = service_collection.build_service_provider()

        # Act: Resolve the service
        service = provider.get_service(Service)

        # Assert: Verify that the factory-provided dependency is injected correctly
        assert isinstance(service, Service)
        assert service.config.value == 42

    def test_dependency_with_factory_for_singleton(self, service_collection):
        # Arrange: Define a class with a dependency provided by a factory
        class Config:
            def __init__(self, value):
                self.value = value

        class Service:
            def __init__(self, config: Config):
                self.config = config

        service_collection.add_singleton(Config, lambda sp: Config(42))
        service_collection.add_singleton(Service)
        provider = service_collection.build_service_provider()

        # Act: Resolve the service
        service = provider.get_service(Service)

        # Assert: Verify that the factory-provided dependency is injected correctly
        assert isinstance(service, Service)
        assert service.config.value == 42

    def test_optional_dependency_for_transient(self, service_collection):
        # Arrange: Define a class with an optional dependency
        class Logger:
            pass

        class Service:
            def __init__(self, logger: Logger = None):
                self.logger = logger

        service_collection.add_transient(Service)
        provider = service_collection.build_service_provider()

        # Act: Resolve the service
        service = provider.get_service(Service)

        # Assert: Verify that the optional dependency is handled correctly
        assert isinstance(service, Service)
        assert service.logger is None

    def test_optional_dependency_for_singleton(self, service_collection):
        # Arrange: Define a class with an optional dependency
        class Logger:
            pass

        class Service:
            def __init__(self, logger: Logger = None):
                self.logger = logger

        service_collection.add_singleton(Service)
        provider = service_collection.build_service_provider()

        # Act: Resolve the service
        service = provider.get_service(Service)

        # Assert: Verify that the optional dependency is handled correctly
        assert isinstance(service, Service)
        assert service.logger is None

    def test_complex_dependency_graph(self, service_collection):
        # Arrange: Define classes with multiple and varied dependencies
        class Logger:
            pass

        class Config:
            pass

        class Repository:
            def __init__(self, logger: Logger, config: Config):
                self.logger = logger
                self.config = config

        class ServiceA:
            def __init__(self, repository: Repository):
                self.repository = repository

        class ServiceB:
            def __init__(self, service_a: ServiceA, logger: Logger):
                self.service_a = service_a
                self.logger = logger

        class ServiceC:
            def __init__(self, service_b: ServiceB, config: Config):
                self.service_b = service_b
                self.config = config

        service_collection.add_singleton(Logger)
        service_collection.add_singleton(Config)
        service_collection.add_transient(Repository)
        service_collection.add_transient(ServiceA)
        service_collection.add_transient(ServiceB)
        service_collection.add_transient(ServiceC)
        provider = service_collection.build_service_provider()

        # Act: Resolve the top-level service
        service_c = provider.get_service(ServiceC)

        # Assert: Verify that all dependencies are injected correctly
        assert isinstance(service_c, ServiceC)
        assert isinstance(service_c.service_b, ServiceB)
        assert isinstance(service_c.service_b.service_a, ServiceA)
        assert isinstance(service_c.service_b.service_a.repository, Repository)
        assert isinstance(service_c.service_b.service_a.repository.logger, Logger)
        assert isinstance(service_c.service_b.service_a.repository.config, Config)
        assert isinstance(service_c.service_b.logger, Logger)
        assert isinstance(service_c.config, Config)

    def test_shared_dependencies(self, service_collection):
        # Arrange: Define classes with shared dependencies
        class Logger:
            pass

        class Config:
            pass

        class ServiceA:
            def __init__(self, logger: Logger):
                self.logger = logger

        class ServiceB:
            def __init__(self, logger: Logger, config: Config):
                self.logger = logger
                self.config = config

        class ServiceC:
            def __init__(self, service_a: ServiceA, service_b: ServiceB):
                self.service_a = service_a
                self.service_b = service_b

        service_collection.add_singleton(Logger)
        service_collection.add_singleton(Config)
        service_collection.add_transient(ServiceA)
        service_collection.add_transient(ServiceB)
        service_collection.add_transient(ServiceC)
        provider = service_collection.build_service_provider()

        # Act: Resolve the top-level service
        service_c = provider.get_service(ServiceC)

        # Assert: Verify that shared dependencies are injected correctly
        assert isinstance(service_c, ServiceC)
        assert isinstance(service_c.service_a, ServiceA)
        assert isinstance(service_c.service_b, ServiceB)
        assert service_c.service_a.logger is service_c.service_b.logger  # Shared singleton
        assert isinstance(service_c.service_b.config, Config)

    def test_nested_and_optional_dependencies(self, service_collection):
        # Arrange: Define classes with nested and optional dependencies
        class Logger:
            pass

        class Config:
            pass

        class ServiceA:
            def __init__(self, logger: Logger = None):
                self.logger = logger

        class ServiceB:
            def __init__(self, service_a: ServiceA, config: Config):
                self.service_a = service_a
                self.config = config

        class ServiceC:
            def __init__(self, service_b: ServiceB):
                self.service_b = service_b

        service_collection.add_singleton(Config)
        service_collection.add_transient(ServiceA)
        service_collection.add_transient(ServiceB)
        service_collection.add_transient(ServiceC)
        provider = service_collection.build_service_provider()

        # Act: Resolve the top-level service
        service_c = provider.get_service(ServiceC)

        # Assert: Verify that nested and optional dependencies are handled correctly
        assert isinstance(service_c, ServiceC)
        assert isinstance(service_c.service_b, ServiceB)
        assert isinstance(service_c.service_b.service_a, ServiceA)
        assert service_c.service_b.service_a.logger is None  # Optional dependency
        assert isinstance(service_c.service_b.config, Config)

    def test_mixed_lifetimes(self, service_collection):
        # Arrange: Define classes with mixed lifetimes
        class Logger:
            pass

        class Config:
            pass

        class ServiceA:
            def __init__(self, logger: Logger):
                self.logger = logger

        class ServiceB:
            def __init__(self, service_a: ServiceA, config: Config):
                self.service_a = service_a
                self.config = config

        service_collection.add_singleton(Logger)
        service_collection.add_singleton(Config)
        service_collection.add_transient(ServiceA)
        service_collection.add_transient(ServiceB)
        provider = service_collection.build_service_provider()

        # Act: Resolve services
        service_b1 = provider.get_service(ServiceB)
        service_b2 = provider.get_service(ServiceB)

        # Assert: Verify mixed lifetimes
        assert service_b1 is not service_b2  # Transient
        assert service_b1.service_a.logger is service_b2.service_a.logger  # Shared singleton
        assert service_b1.config is service_b2.config  # Shared singleton