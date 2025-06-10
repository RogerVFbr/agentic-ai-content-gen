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
                if param.annotation != inspect.Parameter.empty and
                   (param.default == inspect.Parameter.empty or param.annotation in self._services)
            }
            return implementation(**dependencies)
        return implementation
