from crosscutting.app_logger import AppLogger
import inspect

class DiContainer:

    CONTAINER = {}

    @classmethod
    @AppLogger.timeit()
    def build_container(cls, pre_instantiated, injections) -> None:
        try:
            injections_dependencies = {}
            for dep in injections:
                argspec = inspect.getfullargspec(dep.__init__)
                injections_dependencies[f"{dep.__module__}.{dep.__name__}"] = {
                    "type": dep,
                    "deps": [f"{argspec.annotations[x].__module__}.{argspec.annotations[x].__name__}" for x in
                             argspec.args
                             if x in argspec.annotations]
                }

            container = {}

            for x in pre_instantiated:
                container[f"{type(x).__module__}.{type(x).__name__}"] = x

            while len(container) < (len(injections_dependencies) + len(pre_instantiated)):
                for item, config in injections_dependencies.items():
                    if item not in container and len(config["deps"]) == 0:
                        container[item] = config["type"]()
                    if item not in container and all(x in container.keys() for x in config["deps"]):
                        args = tuple([container[x] for x in config["deps"]])
                        if len(args) > 1:
                            container[item] = config["type"](*args)
                        else:
                            container[item] = config["type"](args[0])

            cls.CONTAINER = container
        except Exception as e:
            raise Exception(f"Unable to build DI container -> {type(e).__name__}: {e}")

    @classmethod
    def get(cls, obj):
        obj_key = f"{obj.__module__}.{obj.__name__}"
        if obj_key not in cls.CONTAINER:
            raise Exception("Requested class does not exist in DI container.")
        return cls.CONTAINER[obj_key]