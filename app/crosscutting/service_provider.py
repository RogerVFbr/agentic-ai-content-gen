from typing import Any, Type, Union, Callable

import inspect

class ServiceCollection:
    def __init__(self):
        self._services = {}

    def add_transient(self, service_type: Type[Any], implementation: Union[Type[Any], Callable[..., Any]] = None) -> "ServiceCollection":
        implementation = implementation if implementation is not None else service_type

        self._services[service_type] = {
            "implementation": implementation,
            "lifetime": "transient",
            "is_factory": callable(implementation) and not inspect.isclass(implementation),
        }

        return self

    def add_singleton(self, service_type: Type[Any], implementation: Union[Type[Any], Callable[..., Any]] = None) -> "ServiceCollection":
        implementation = implementation if implementation is not None else service_type

        self._services[service_type] = {
            "implementation": implementation,
            "lifetime": "singleton",
            "is_factory": callable(implementation) and not inspect.isclass(implementation),
        }

        return self

    def merge(self, other_service_collection: "ServiceCollection") -> "ServiceCollection":
        for service_type, service_details in other_service_collection._services.items():
            self._services[service_type] = service_details

        return self

    def build_service_provider(self):
        return ServiceProvider(self._services)


class ServiceProvider:
    def __init__(self, services):
        self._services = services
        self._singletons = {}

    def get_service(self, service_type):
        service = self._services.get(service_type)
        if not service:
            raise Exception(f"Service of type {service_type} not registered.")

        if service["lifetime"] == "singleton":
            if service_type not in self._singletons:
                self._singletons[service_type] = self._resolve_service(service)
            return self._singletons[service_type]

        if service["lifetime"] == "transient":
            return self._resolve_service(service)

        raise Exception(f"Unknown lifetime for service {service_type}.")

    def _resolve_service(self, service):
        if service["is_factory"]:
            return service["implementation"](self)
        return self._create_instance(service["implementation"])

    def _create_instance(self, implementation):
        if inspect.isclass(implementation):
            constructor = inspect.signature(implementation)
            dependencies = {
                param.name: self.get_service(param.annotation)
                for param in constructor.parameters.values()
                if param.annotation != inspect.Parameter.empty
            }
            return implementation(**dependencies)
        return implementation


# Example usage
class Logger:
    def log(self, message):
        print(f"Logger: {message} (Logger Id: {id(self)})")


class Database:
    def save(self):
        print(f"Database: Data saved. (Id: {id(self)})")


class Repository:
    def __init__(self, logger: Logger, database: Database, config: str):
        self.logger = logger
        self.database = database
        self.config = config

    def save(self):
        self.logger.log(f"Repository: Repository called. Config: {self.config}. (Id: {id(self)})")
        self.database.save()


class MyService:
    def __init__(self, logger: Logger, repository: Repository):
        self.logger = logger
        self.repository = repository

    def do_something(self):
        self.logger.log(f"Service: Service called. (Id: {id(self)})")
        self.repository.save()


if __name__ == "__main__":
    # Register services
    services = ServiceCollection()
    services.add_transient(Repository, lambda sp: Repository(sp.get_service(Logger), sp.get_service(Database), "some_config"))
    services.add_singleton(MyService)
    services.add_transient(Logger, Logger)
    services.add_transient(Database, Database)

    # Build service provider
    provider = services.build_service_provider()

    # Resolve services
    my_service = provider.get_service(MyService)
    my_service.do_something()  # Output: Service called. Repository called. Data saved.