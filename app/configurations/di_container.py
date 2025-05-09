import inspect

class DiContainer:

    CONTAINER = {}

    @classmethod
    def get(cls, obj):
        obj_key = f"{obj.__module__}.{obj.__name__}"
        if obj_key not in cls.CONTAINER:
            raise Exception("Requested class does not exist in DI container.")
        return cls.CONTAINER[obj_key]

    @classmethod
    def build_container(cls, pre_instantiated, injections) -> None:
        try:
            dependencies = cls._inspect_dependencies(injections)
            container = cls._initialize_container(pre_instantiated)
            cls.CONTAINER = cls._resolve_dependencies(container, dependencies, pre_instantiated)
        except Exception as e:
            raise Exception(f"Unable to build DI container -> {type(e).__name__}: {e}")

    @classmethod
    def _inspect_dependencies(cls, injections):
        """Inspect and extract dependencies for each injectable class."""
        dependencies = {}
        for dep in injections:
            original_class = dep

            # Handle CrewAI class decorator
            if getattr(original_class, "is_crew_class", False):
                original_class = original_class.__bases__[0]

            constructor = original_class.__init__
            signature = inspect.signature(constructor)
            dependencies[f"{dep.__module__}.{dep.__name__}"] = {
                "type": dep,
                "deps": [
                    f"{param.annotation.__module__}.{param.annotation.__name__}"
                    for param in signature.parameters.values()
                    if param.name != "self" and param.annotation != param.empty
                ]
            }
        return dependencies

    @classmethod
    def _initialize_container(cls, pre_instantiated):
        """Add pre-instantiated objects to the container."""
        container = {}
        for obj in pre_instantiated:
            container[f"{type(obj).__module__}.{type(obj).__name__}"] = obj
        return container

    @classmethod
    def _resolve_dependencies(cls, container, dependencies, pre_instantiated):
        """Resolve and instantiate dependencies."""
        while len(container) < (len(dependencies) + len(pre_instantiated)):
            for item, config in dependencies.items():
                if item not in container and len(config["deps"]) == 0:
                    container[item] = config["type"]()
                if item not in container and all(x in container.keys() for x in config["deps"]):
                    args = tuple([container[x] for x in config["deps"]])
                    if len(args) > 1:
                        container[item] = config["type"](*args)
                    else:
                        container[item] = config["type"](args[0])

        return container
