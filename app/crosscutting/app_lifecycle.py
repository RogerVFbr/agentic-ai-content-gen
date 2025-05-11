from time import sleep

import asyncio


class AppLifecycle:

    IS_TERMINATION_INFLIGHT = False
    IS_RUNNING=False
    IS_TERMINATED=False

    @classmethod
    def main(cls):
        def decorator(method):
            if asyncio.iscoroutinefunction(method):
                async def async_method(*args, **kw):
                    cls.IS_RUNNING = True

                    result = await method(*args, **kw)

                    while cls.IS_TERMINATION_INFLIGHT:
                        await asyncio.sleep(0.5)

                    cls.IS_RUNNING = False

                    return result

                return async_method
            else:
                def sync_method(*args, **kw):
                    cls.IS_RUNNING = True

                    result = method(*args, **kw)

                    while cls.IS_TERMINATION_INFLIGHT:
                        sleep(0.5)

                    cls.IS_RUNNING = False

                    return result

                return sync_method

        return decorator

    @classmethod
    def terminate(cls):
        def decorator(method):
            if asyncio.iscoroutinefunction(method):
                async def async_method(*args, **kw):
                    if cls.IS_TERMINATION_INFLIGHT or cls.IS_TERMINATED:
                        return None

                    cls.IS_TERMINATION_INFLIGHT = True

                    result = await method(*args, **kw)

                    cls.IS_TERMINATION_INFLIGHT = False
                    cls.IS_TERMINATED = True

                    return result

                return async_method
            else:
                def sync_method(*args, **kw):
                    if cls.IS_TERMINATION_INFLIGHT or cls.IS_TERMINATED:
                        return None

                    cls.IS_TERMINATION_INFLIGHT = True

                    result = method(*args, **kw)

                    cls.IS_TERMINATION_INFLIGHT = False
                    cls.IS_TERMINATED = True

                    return result

                return sync_method

        return decorator