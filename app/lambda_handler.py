import asyncio

from configurations.configuration_module import ConfigurationModule
from controllers.langgraph_controller import LangGraphController


def handler(event, context):
    async def execute():
        config = ConfigurationModule.get()
        if config.initialize():
            controller = config.get_instance(LangGraphController)
            await controller.run(event)

    asyncio.run(execute())
