import asyncio

from configurations.configuration_module import ConfigurationModule
from controllers.app_controller import AppController


def handler(event, context):
    async def execute():
        config = ConfigurationModule.get()
        if config.initialize():
            controller = config.get_instance(AppController)
            await controller.run(event)

    asyncio.run(execute())
