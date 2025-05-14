import inspect

import asyncio

MEMOIZED_METHODS = {}

def memoize_method():

    def decorator(method):
        source = f"{inspect.getmodule(method).__name__}.{method.__qualname__}"

        if asyncio.iscoroutinefunction(method):
            async def async_method(*args, **kw):
                if source not in MEMOIZED_METHODS:
                    MEMOIZED_METHODS[source] = await method(*args, **kw)
                return MEMOIZED_METHODS[source]
            return async_method
        else:
            def sync_method(*args, **kw):
                if source not in MEMOIZED_METHODS:
                    MEMOIZED_METHODS[source] = method(*args, **kw)
                return MEMOIZED_METHODS[source]
            return sync_method

    return decorator


if __name__ == "__main__":
    # Example usage
    @memoize_method()
    def example_function():
        print("Executed sync.")

    example_function()  # Should compute and cache the result
    example_function()  # Should return the cached result
    example_function()  # Should return the cached result

    @memoize_method()
    async def example_async_function():
        print("Executed async.")

    asyncio.run(example_async_function())  # Should compute and cache the result
    asyncio.run(example_async_function())  # Should return the cached result
    asyncio.run(example_async_function())  # Should return the cached result
